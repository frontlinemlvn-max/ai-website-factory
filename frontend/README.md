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

From a VS Code terminal:

```bash
cd /Users/brandingbadge/Documents/ai-website-factory/frontend
python3 -m http.server 5173 --bind 127.0.0.1
```

Open:

- Application: http://127.0.0.1:5173/
- Landing page: http://127.0.0.1:5173/landing.html

Press `Control-C` in the terminal to stop the preview server.

The preview needs an internet connection because React, Phosphor icons, and Google
Fonts are loaded from their CDNs. The server binds only to the local computer.

## Prototype boundaries

The exported interaction model is suitable for visual and local workflow testing,
but it is not connected to the repository's factory CLI:

- Claude-powered copy generation uses `window.claude.complete`, which exists in the
  Claude Design host but not in a normal local browser. The page catches that error
  and shows a deterministic draft generated from the entered brief.
- Domain availability, registration, payment, publishing, and source-download actions
  are simulated interface states. They do not contact a registrar, payment provider,
  deployment service, or the local factory.
- No credentials belong in this directory. A later backend/API service should own AI
  keys and invoke the factory; the browser should send only validated customer input.

## Safe next integration boundary

Keep this prototype as the presentation layer. When real generation is added, place a
server-side API between it and the existing factory. A minimal boundary would expose
operations such as creating a generation job, reading its status, and opening its
preview. That API can translate validated form data into the factory's existing
project brief/workflow without moving factory logic into browser code.
