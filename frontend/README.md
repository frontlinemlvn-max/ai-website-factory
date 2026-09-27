# Customer Frontend

This directory contains the customer-facing prototype exported from Claude Design.
It is intentionally isolated from the factory CLI and from generated client projects.

## Technology

This is a static Claude Design Component export, not a Vite, Next.js, or conventional
React source project. The pages contain Claude's `x-dc`, `sc-if`, and `sc-for`
markup plus embedded component state. `support.js` loads React 18.3.1 (and Babel
when required) from unpkg and renders that markup in the browser.

There is no package installation or build step.

## Files

- `index.html` - the full interactive Website Factory application prototype
- `landing.html` - the separate marketing/landing-page prototype
- `support.js` - generated Claude Design runtime; keep it unedited
- `_ds/` - the Nocturne design-system JavaScript and CSS
- `assets/` - the image used by the application header

The original export filenames were `Website Factory App.dc.html` and
`AI Website Factory.dc.html`. They were renamed so a normal static server can open
the application at `/` and the landing page at `/landing.html`.

## Run locally

**Option A — static only**, no project creation, everything simulated:

```bash
cd /Users/brandingbadge/Documents/ai-website-factory/frontend
python3 -m http.server 5173 --bind 127.0.0.1
```

**Option B — with the local backend**, from the factory root:

```bash
./factory frontend
```

Both open:

- Application: http://127.0.0.1:5173/
- Landing page: http://127.0.0.1:5173/landing.html

Press `Control-C` in the terminal to stop either server.

The preview needs an internet connection because React, Phosphor icons, and Google
Fonts are loaded from their CDNs. Both servers bind only to the local computer.

## Prototype boundaries

- Claude-powered copy generation prefers `window.claude.complete` (available inside
  the Claude Design host), then falls back to the local backend's real
  `/api/generate` (see below) when run via `./factory frontend`, then finally to a
  deterministic draft generated from the entered brief if neither is available or
  configured. Which of these three actually ran is not shown in the UI — the visible
  result looks the same either way, by design.
- Domain **availability and pricing** becomes real when `VERCEL_TOKEN` is configured
  (see below), falling back to the existing simulated results otherwise. Domain
  **registration** (actually buying it) remains fully simulated in every run option —
  it is never reachable from the browser at all, by design (see "Domain registration"
  below for why).
- The one-time **export purchase** ($39 CAD) becomes a real Square Checkout when
  `SQUARE_ACCESS_TOKEN` and `SQUARE_LOCATION_ID` are configured (see below), falling
  back to the existing simulated instant-unlock otherwise. The recurring "Studio"
  subscription plan stays fully simulated in every run option, since a real recurring
  charge needs a user-account system this prototype doesn't have — source-download
  itself also remains simulated (there is no real generated site bundle to download).
- Clicking **Publish** checks the project's REAL stage (via the existing
  `/api/projects/<slug>/status`) when a real backend project exists, and reports it
  honestly — a freshly-generated draft will say so and name the real stage, rather
  than pretending to go live. It only shows as genuinely "Live" when the project has
  actually reached the `Deployed` stage, which only happens if the owner ran
  `./factory deploy` themselves, directly — never reachable from the browser, for the
  same no-authentication reason domain registration isn't. Falls back to the prior
  simulated toggle when there's no real backend project to check.
- No credentials belong in this directory. The Anthropic API key used by
  `/api/generate`, the Vercel token used by domain checks, and the Square access
  token used by checkout all live server-side only (environment variable or `.env`
  at the factory root) — the browser never sees them.

## Local backend vertical slice

Run with `./factory frontend` (see `tools/local_backend.py`) and these become real:

- `GET /api/health`
- `POST /api/projects` — validates the submitted name, derives a slug, and calls the
  existing `tools/init-project.sh` to create the project (no scaffolding logic is
  duplicated in the browser or the backend). The submitted business name, brief,
  audience, action, and extras are appended to the new project's `PROJECT-BRIEF.md`
  as an explicitly unverified customer-submitted summary — never treated as a
  validated answer.
- `GET /api/projects/<slug>/status` — reads the project's `PROJECT-STATUS.md` and
  returns its stage, owner, active work, blockers, known issues, human decisions,
  and next action.
- `POST /api/generate` — calls the real Anthropic API server-side (`claude-haiku-4-5`)
  with the submitted brief, using the same prompt/response shape `window.claude.complete`
  already expects. Requires `ANTHROPIC_API_KEY` in the environment or in a `.env` file
  at the factory root (see `.env.example`); **fails closed with a clear 503** rather
  than fabricating output when the key is missing. Limited to 5 requests/minute per
  IP — tighter than the other routes' 180/minute, since each call costs real money.
- `POST /api/checkout` — creates a real Square hosted Checkout Payment Link for the
  one-time $39 CAD export (`plan: "once"` only; the recurring "Studio" plan is
  rejected with a 400, since it needs a real user-account system). Requires
  `SQUARE_ACCESS_TOKEN` and `SQUARE_LOCATION_ID` in the environment or `.env`;
  **fails closed with a clear 503** when missing. `SQUARE_ENVIRONMENT` defaults to
  `sandbox`. Limited to 10 requests/minute per IP.
- `GET /api/checkout/verify?orderId=<id>` — after the browser is redirected back from
  Square's hosted checkout, this cross-checks the order against Square's Orders API
  (exact state, amount, and location) before the frontend unlocks anything. The
  browser's own return-URL parameters are never trusted by themselves.

`index.html` resolves copy first (`window.claude.complete`, then `/api/generate`, then
a local deterministic draft), then calls `POST /api/projects` with that copy attached.
When real copy was obtained, the backend also renders it into an actual
`src/index.html` for the new project — a single-page static draft (see
`templates/site-draft/index.html.tmpl`), using the AI's suggested palette (with a
verified-accessible fallback if it's missing or invalid) and every field
HTML-escaped, since this is untrusted AI-generated content being written into a real
file that gets served in a browser. The generated page carries a visible "AI-drafted
pilot, unverified" banner and lists its `nav` suggestions as "planned pages, not yet
built" rather than fabricating links to pages that don't exist — the project's
`PROJECT-BRIEF.md` gets a matching note that it still needs the full factory pipeline
(Architecture, Design, Development, QA, every specialist review) before any of it is
trustworthy. If copy generation fails, the project is still created — just without an
auto-generated site — rather than ever writing fabricated content to disk. The
"Factory record" line shows whether a draft site was generated. Any failure anywhere
in this chain (backend not running, network error, generation not configured) is
caught silently and the fully simulated/local-draft experience continues exactly as
before. Domain purchase, publishing, deployment, and downloads are unaffected either
way — they stay simulated regardless of which run option is used.

## Payments: real one-time export, simulated subscription

Clicking "Pay" for the one-time $39 CAD export calls `POST /api/checkout`, which
creates a real Square hosted Checkout Payment Link, and redirects the browser to it —
this app never collects or sees card details itself. Before redirecting, the pending
order ID and the wizard's in-progress state are saved to `localStorage` (the only
state this frontend persists beyond `theme`), since Square's hosted checkout is a full
page navigation away and back, not an embedded flow. On return, `GET
/api/checkout/verify` confirms with Square's own Orders API that the order is
`COMPLETED`, for the correct location, and for the exact expected amount, before the
export is unlocked and the saved wizard state is restored — a successful-looking
redirect URL by itself proves nothing and is never trusted alone. If checkout isn't
configured (`SQUARE_ACCESS_TOKEN`/`SQUARE_LOCATION_ID` unset) or the request fails for
any reason, the button falls back to the prior simulated instant-unlock — no
functionality is lost. The recurring "Studio" subscription plan always uses the
simulated unlock, in every run option: a real recurring charge needs a way to
associate a paying customer with future access, which requires a user-account system
this prototype does not have. Source-download after unlock also stays simulated
either way, since there is no real generated site bundle to serve yet.

## Domain registration is intentionally CLI-only

`GET /api/domains/check?name=<domain>` (real, via Vercel's Domains Registrar API,
fails closed with a 503 if `VERCEL_TOKEN` isn't set) is the only domain-related
backend route. There is no `/api/domains/buy` or equivalent, and there never should
be one reachable from the browser: this server has no user-authentication system, so
any endpoint that could spend real, non-refundable money would be triggerable by
anyone who can reach the URL, not just the account owner. Registering a domain is a
separate CLI command, `./factory buy-domain` (see the root `README.md` and
`tools/domain-adapter.py`), run directly by whoever controls the Vercel account and
its billing.

## Further integration boundary

Keep this prototype as the presentation layer. Real AI copy generation, a real
single-page draft site, real domain availability/pricing, and a real one-time export
payment now run server-side (see above) using this same pattern; if a Studio
subscription, multi-page generation, or deployment are added later, extend it the
same way — a server-side API between the browser and any provider credentials, never
provider keys or factory logic moved into browser code. A generated draft is
intentionally not a finished, launchable site: it still needs to go through the same
Architecture → Design → Development → QA → specialist-review pipeline as any other
factory project (see `yyz-caregivers` for what that looks like end to end) before any
of its claims can be trusted or it can be approved for launch.
