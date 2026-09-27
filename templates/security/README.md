# Security layers for factory websites

This factory currently ships static HTML projects and a Python CLI. The Next.js files below are the approved API/AI hardening kit. Copy them only when a project actually adds a Node/Next.js backend.

## Current Python factory (already wired)

- `./factory preview` serves `src/` through `tools/preview-server.py` with XSS/CSP headers, path checks, disabled directory listing, and a loopback-only bind.
- `./factory scan-secrets [project-name]` scans for committed `.env` files and high-confidence keys without printing values.
- Root `.env.example` lists required variable names. Real values belong in a gitignored `.env`.

## Next.js / Node API projects

1. Install dependencies:

```bash
npm install @upstash/ratelimit @upstash/redis
```

2. Copy these files into the Next.js app root:

- `templates/security/nextjs/middleware.ts` → `middleware.ts`
- `templates/security/nextjs/lib/security.ts` → `lib/security.ts`
- `templates/security/nextjs/lib/rate-limit.ts` → `lib/rate-limit.ts`
- `templates/security/nextjs/lib/with-secure-route.ts` → `lib/with-secure-route.ts`

3. Put Upstash REST credentials in `.env` (never in git):

```bash
UPSTASH_REDIS_REST_URL=https://example.upstash.io
UPSTASH_REDIS_REST_TOKEN=replace-with-upstash-token
```

4. Wrap generation and other mutating routes:

```ts
import { NextResponse } from "next/server";
import { withSecureRoute } from "@/lib/with-secure-route";

export const POST = withSecureRoute(
  async (_request, payload) => NextResponse.json({ ok: true, payload }),
  { bucket: "generate", limits: { maxBytes: 16 * 1024, maxStringLength: 2000 } },
);
```

Production requests fail closed if Upstash is missing. Local `NODE_ENV !== production` allows development without Redis.

## Static hosting headers

Copy `templates/security/vercel.json` into the deployment root of a project that deploys on Vercel without Next.js middleware — for factory projects that is `src/`, where the `.vercel` link lives. Vercel ignores a `vercel.json` outside the directory it deploys from, so a copy at the project root silently sends no headers. Tighten `style-src` / `font-src` if the site does not load Google Fonts.
