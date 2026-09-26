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
- Domain availability, registration, payment, publishing, and source-download actions
  remain simulated interface states in every run option. They do not contact a
  registrar, payment provider, or deployment service.
- No credentials belong in this directory. The Anthropic API key used by
  `/api/generate` lives server-side only (environment variable or `.env` at the
  factory root) — the browser never sees it.

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

`index.html` calls `/api/projects` once the onboarding wizard finishes and shows the
result in a small "Factory record" line — but only when a response actually comes
back; any failure (backend not running, network error, generation not configured) is
caught silently and the fully simulated/local-draft experience continues exactly as
before. Payments, domain purchase, publishing, deployment, and downloads are
unaffected either way — they stay simulated regardless of which run option is used.

## Further integration boundary

Keep this prototype as the presentation layer. Real AI copy generation now runs
server-side (see above) using this same pattern; if payments or deployment are added
later, extend it the same way — a server-side API between the browser and any
provider credentials, never provider keys or factory logic moved into browser code.
