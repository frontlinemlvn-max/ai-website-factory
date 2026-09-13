/**
 * Upstash Redis rate limiter for API and AI generation routes.
 *
 * Credentials must come from the environment. This module fails closed in
 * production when Redis is not configured.
 */

import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

export type RateLimitResult = {
  success: boolean;
  limit: number;
  remaining: number;
  reset: number;
};

type LimitRule = {
  limit: number;
  window: `${number} ms` | `${number} s` | `${number} m` | `${number} h` | `${number} d`;
};

export const RATE_LIMIT_RULES = {
  api: { limit: 60, window: "1 m" },
  generate: { limit: 8, window: "1 m" },
  auth: { limit: 10, window: "10 m" },
} as const satisfies Record<string, LimitRule>;

export type RateLimitBucket = keyof typeof RATE_LIMIT_RULES;

const limiterCache = new Map<string, Ratelimit>();

function redisFromEnv(): Redis | null {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) {
    return null;
  }
  return new Redis({ url, token });
}

function limiterFor(bucket: RateLimitBucket): Ratelimit | null {
  const redis = redisFromEnv();
  if (!redis) {
    return null;
  }
  const cached = limiterCache.get(bucket);
  if (cached) {
    return cached;
  }
  const rule = RATE_LIMIT_RULES[bucket];
  const limiter = new Ratelimit({
    redis,
    limiter: Ratelimit.slidingWindow(rule.limit, rule.window),
    prefix: `factory:${bucket}`,
    analytics: false,
  });
  limiterCache.set(bucket, limiter);
  return limiter;
}

export function clientKey(request: Request): string {
  const forwarded = request.headers.get("x-forwarded-for");
  const ip = forwarded?.split(",")[0]?.trim() || request.headers.get("x-real-ip") || "unknown";
  return ip;
}

export async function enforceRateLimit(
  request: Request,
  bucket: RateLimitBucket = "api",
  identity = clientKey(request),
): Promise<RateLimitResult> {
  const limiter = limiterFor(bucket);
  const rule = RATE_LIMIT_RULES[bucket];

  if (!limiter) {
    if (process.env.NODE_ENV === "production") {
      return { success: false, limit: rule.limit, remaining: 0, reset: Date.now() + 60_000 };
    }
    return { success: true, limit: rule.limit, remaining: rule.limit, reset: Date.now() + 60_000 };
  }

  const result = await limiter.limit(identity);
  return {
    success: result.success,
    limit: result.limit,
    remaining: result.remaining,
    reset: result.reset,
  };
}

export function rateLimitHeaders(result: RateLimitResult): Record<string, string> {
  return {
    "X-RateLimit-Limit": String(result.limit),
    "X-RateLimit-Remaining": String(Math.max(0, result.remaining)),
    "X-RateLimit-Reset": String(result.reset),
    "Retry-After": result.success ? "0" : "60",
  };
}
