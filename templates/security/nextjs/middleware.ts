import { NextResponse, type NextRequest } from "next/server";
import { XSS_PROTECTION_HEADERS } from "./lib/security";
import { clientKey, enforceRateLimit, rateLimitHeaders } from "./lib/rate-limit";

const MAX_API_BODY_BYTES = 32 * 1024;
const MAX_GENERATE_BODY_BYTES = 16 * 1024;
const GENERATE_PREFIXES = ["/api/generate", "/api/ai", "/api/completion"];

function isApiPath(pathname: string): boolean {
  return pathname === "/api" || pathname.startsWith("/api/");
}

function isGeneratePath(pathname: string): boolean {
  return GENERATE_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`));
}

function withSecurityHeaders(response: NextResponse): NextResponse {
  for (const [name, value] of Object.entries(XSS_PROTECTION_HEADERS)) {
    response.headers.set(name, value);
  }
  return response;
}

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (isApiPath(pathname)) {
    const declaredLength = Number(request.headers.get("content-length") || "0");
    const maxBytes = isGeneratePath(pathname) ? MAX_GENERATE_BODY_BYTES : MAX_API_BODY_BYTES;
    if (Number.isFinite(declaredLength) && declaredLength > maxBytes) {
      return withSecurityHeaders(
        NextResponse.json({ error: "Payload is too large." }, { status: 413 }),
      );
    }

    const bucket = isGeneratePath(pathname) ? "generate" : "api";
    const limited = await enforceRateLimit(request, bucket, `${bucket}:${clientKey(request)}`);
    if (!limited.success) {
      const response = NextResponse.json({ error: "Rate limit exceeded." }, { status: 429 });
      for (const [name, value] of Object.entries(rateLimitHeaders(limited))) {
        response.headers.set(name, value);
      }
      return withSecurityHeaders(response);
    }
  }

  return withSecurityHeaders(NextResponse.next());
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
