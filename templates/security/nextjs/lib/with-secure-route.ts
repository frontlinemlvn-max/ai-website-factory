import { NextResponse } from "next/server";
import { applySecurityHeaders, PayloadValidationError, readJsonBody, type PayloadLimits } from "./security";
import { enforceRateLimit, rateLimitHeaders, type RateLimitBucket } from "./rate-limit";

type SecureHandler = (request: Request, payload: unknown) => Promise<Response> | Response;

type SecureRouteOptions = {
  bucket?: RateLimitBucket;
  limits?: Partial<PayloadLimits>;
  methods?: string[];
};

function jsonError(message: string, status: number, extra: Record<string, string> = {}): Response {
  const response = NextResponse.json({ error: message }, { status });
  applySecurityHeaders(response.headers);
  for (const [name, value] of Object.entries(extra)) {
    response.headers.set(name, value);
  }
  return response;
}

export function withSecureRoute(handler: SecureHandler, options: SecureRouteOptions = {}) {
  const methods = options.methods ?? ["POST"];
  const bucket = options.bucket ?? "api";

  return async function secureRoute(request: Request): Promise<Response> {
    if (!methods.includes(request.method)) {
      return jsonError("Method not allowed.", 405);
    }

    const limited = await enforceRateLimit(request, bucket);
    const limitHeaders = rateLimitHeaders(limited);
    if (!limited.success) {
      return jsonError("Rate limit exceeded.", 429, limitHeaders);
    }

    try {
      const payload = ["POST", "PUT", "PATCH"].includes(request.method)
        ? await readJsonBody(request, options.limits)
        : null;
      const response = await handler(request, payload);
      applySecurityHeaders(response.headers);
      for (const [name, value] of Object.entries(limitHeaders)) {
        response.headers.set(name, value);
      }
      return response;
    } catch (error) {
      if (error instanceof PayloadValidationError) {
        return jsonError(error.message, error.status, limitHeaders);
      }
      return jsonError("Request could not be processed.", 500, limitHeaders);
    }
  };
}
