/**
 * Input sanitization and strict JSON payload validation for Node/Next.js routes.
 * Use from Route Handlers / API routes. Middleware cannot safely consume the body.
 */

const DANGEROUS_KEYS = new Set(["__proto__", "prototype", "constructor"]);
const CONTROL_CHAR = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/;
const CONTROL_CHARS_GLOBAL = /[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g;
const HTML_MARKUP = /[<>]/g;

export const DEFAULT_PAYLOAD_LIMITS = {
  maxBytes: 32 * 1024,
  maxDepth: 6,
  maxKeys: 80,
  maxStringLength: 4000,
  maxArrayLength: 50,
};

export type PayloadLimits = typeof DEFAULT_PAYLOAD_LIMITS;

export class PayloadValidationError extends Error {
  status: number;

  constructor(message: string, status = 400) {
    super(message);
    this.name = "PayloadValidationError";
    this.status = status;
  }
}

export function sanitizeString(value: string, maxLength = DEFAULT_PAYLOAD_LIMITS.maxStringLength): string {
  return value
    .replace(CONTROL_CHARS_GLOBAL, "")
    .replace(HTML_MARKUP, "")
    .normalize("NFC")
    .trim()
    .slice(0, maxLength);
}

function assertPlainObject(value: unknown): value is Record<string, unknown> {
  return Boolean(value) && typeof value === "object" && Object.getPrototypeOf(value) === Object.prototype;
}

function walk(value: unknown, limits: PayloadLimits, depth: number, keyCount: { count: number }): unknown {
  if (depth > limits.maxDepth) {
    throw new PayloadValidationError("Payload exceeds maximum object depth.");
  }

  if (typeof value === "string") {
    if (value.length > limits.maxStringLength) {
      throw new PayloadValidationError("A string field exceeds the allowed length.");
    }
    return sanitizeString(value, limits.maxStringLength);
  }

  if (typeof value === "number") {
    if (!Number.isFinite(value)) {
      throw new PayloadValidationError("Non-finite numbers are not allowed.");
    }
    return value;
  }

  if (typeof value === "boolean" || value === null) {
    return value;
  }

  if (Array.isArray(value)) {
    if (value.length > limits.maxArrayLength) {
      throw new PayloadValidationError("An array field exceeds the allowed length.");
    }
    return value.map((entry) => walk(entry, limits, depth + 1, keyCount));
  }

  if (!assertPlainObject(value)) {
    throw new PayloadValidationError("Payload must be JSON objects, arrays, or primitive values.");
  }

  const result: Record<string, unknown> = Object.create(null);
  const keys = Object.keys(value);
  keyCount.count += keys.length;
  if (keyCount.count > limits.maxKeys) {
    throw new PayloadValidationError("Payload contains too many keys.");
  }

  for (const key of keys) {
    if (DANGEROUS_KEYS.has(key) || CONTROL_CHAR.test(key)) {
      throw new PayloadValidationError("Payload contains a disallowed key.");
    }
    result[sanitizeString(key, 80)] = walk(value[key], limits, depth + 1, keyCount);
  }
  return result;
}

export function validateJsonPayload(value: unknown, limits: Partial<PayloadLimits> = {}): unknown {
  const merged = { ...DEFAULT_PAYLOAD_LIMITS, ...limits };
  return walk(value, merged, 0, { count: 0 });
}

export async function readJsonBody(
  request: Request,
  limits: Partial<PayloadLimits> = {},
): Promise<unknown> {
  const merged = { ...DEFAULT_PAYLOAD_LIMITS, ...limits };
  const contentType = request.headers.get("content-type") || "";
  if (!contentType.toLowerCase().includes("application/json")) {
    throw new PayloadValidationError("Content-Type must be application/json.");
  }

  const declaredLength = Number(request.headers.get("content-length") || "0");
  if (Number.isFinite(declaredLength) && declaredLength > merged.maxBytes) {
    throw new PayloadValidationError("Payload is too large.", 413);
  }

  const raw = await request.text();
  if (raw.length > merged.maxBytes) {
    throw new PayloadValidationError("Payload is too large.", 413);
  }
  if (!raw) {
    throw new PayloadValidationError("JSON body is required.");
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new PayloadValidationError("Body is not valid JSON.");
  }
  return validateJsonPayload(parsed, merged);
}

export const XSS_PROTECTION_HEADERS: Record<string, string> = {
  "Content-Security-Policy":
    "default-src 'self'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'; object-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; worker-src 'self'",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "DENY",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=()",
  "Cross-Origin-Opener-Policy": "same-origin",
  "Cross-Origin-Resource-Policy": "same-origin",
  "X-XSS-Protection": "0",
};

export function applySecurityHeaders(headers: Headers): void {
  for (const [name, value] of Object.entries(XSS_PROTECTION_HEADERS)) {
    headers.set(name, value);
  }
}
