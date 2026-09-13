# YYZ Caregivers — Performance Report

- **Project:** `yyz-caregivers`
- **Review date:** September 11, 2026
- **Environment:** Local Python preview on loopback; static source inventory; automated regression checks
- **Scope:** Revised eight-page pilot, including the Support Needs Assessment
- **Overall status:** **PASSED FOR THE LOCAL PILOT; PRODUCTION CORE WEB VITALS REMAIN UNVERIFIED**

## 1. Performance Summary

YYZ Caregivers remains a very small, dependency-free static site. The complete served source is **129,648 bytes uncompressed** across eight HTML pages, one stylesheet, two JavaScript files, two SVGs, `robots.txt`, and `sitemap.xml`. Combined CSS and JavaScript is **40,959 bytes**, safely below the maintained 100 KB budget.

The Home page needs five initial local requests: HTML, favicon, stylesheet, deferred navigation/form script, and a 892-byte SVG. The Support Needs page also needs five: HTML, favicon, stylesheet, the deferred shared script, and the deferred 8,982-byte assessment script. Other pages need four. There are no remote fonts, third-party scripts, trackers, frameworks, APIs, packages, images from external hosts, or backend rendering waits.

No source optimization was applied. The measured build revealed no meaningful bottleneck, and minifying, bundling, splitting, or introducing a build tool would provide little value at this size while adding maintenance and regression risk. Baseline and post-review source measurements are therefore identical by design.

Production Core Web Vitals are not claimed. A localhost server cannot represent public TLS, CDN, compression, caching, cellular latency, mobile CPU, or field traffic. A Lighthouse run was attempted, but the audit process could not attach to Chrome in the sandbox and produced no report; no score or partial result is presented.

## 2. Baseline Source Measurements

| Resource group | Files | Uncompressed bytes |
|---|---:|---:|
| HTML | 8 | 87,171 |
| CSS | 1 | 24,292 |
| JavaScript | 2 | 16,667 |
| SVG | 2 | 1,208 |
| Robots and sitemap | 2 | 310 |
| **Complete served source** | **15** | **129,648** |

Compressing each text asset independently with local gzip produced a combined **36,260-byte estimate**. This is not a production transfer measurement: actual results depend on the selected host, compression level, response headers, and per-route cache state.

### HTML route sizes

| Route | HTML bytes |
|---|---:|
| Home | 11,528 |
| About | 7,478 |
| Services | 9,095 |
| Contact | 12,058 |
| Support Needs | 21,775 |
| FAQ | 9,773 |
| Privacy | 7,770 |
| Terms | 7,694 |

Support Needs is the largest HTML page because its accessible native controls and guidance are server-delivered rather than constructed by a framework. At 21,775 bytes, it does not justify client-side rendering or code generation.

## 3. Local Response Baseline

The following results are **20-sample loopback diagnostics**, not public speed claims:

| Route | Median local TTFB | Average local TTFB | Local TTFB p95 | Average local total |
|---|---:|---:|---:|---:|
| Home | 3.111 ms | 5.131 ms | 16.973 ms | 6.000 ms |
| Support Needs | 2.627 ms | 3.725 ms | 9.578 ms | 3.916 ms |

Every request returned successfully from the temporary local server. The timing spread reflects development-machine and sandbox scheduling. It does not predict production hosting performance.

## 4. Request and Rendering Architecture

- All nine script elements across eight pages use `defer`.
- Each route uses one shared render-blocking stylesheet.
- No inline event handler, framework hydration, remote module, dynamic import, polling loop, network request, or browser-storage operation exists.
- Home loads four local assets in addition to its document.
- Support Needs loads four local assets in addition to its document.
- No preconnect, DNS-prefetch, or speculative preload is justified because there is no third-party origin or large critical asset.
- All 215 local references resolve.

The assessment script performs small bounded validation and DOM updates only after user interaction. It builds the review with text nodes rather than HTML. There is no evidence of a long-running task or repeated render loop in the source, but INP was not measured on representative field hardware.

## 5. Core Web Vitals Assessment

Google’s current Core Web Vitals are LCP, INP, and CLS, assessed at the 75th percentile of visits; the “good” thresholds remain LCP at or below 2.5 seconds, INP at or below 200 milliseconds, and CLS at or below 0.1 ([web.dev Web Vitals guidance](https://web.dev/articles/vitals?hl=en), [threshold methodology](https://web.dev/articles/defining-core-web-vitals-thresholds)).

### Largest Contentful Paint

Favourable implementation factors:

- Direct static HTML with no client-rendering delay.
- One small local stylesheet.
- Deferred scripts.
- System fonts with no font download or swap.
- A 892-byte Home hero SVG that is not lazy-loaded.
- No API, tracker, widget, consent platform, or third-party execution.

**Status:** Not measured under representative production conditions. No claim is made that the LCP threshold is met.

### Interaction to Next Paint

Favourable implementation factors:

- 16,667 bytes of plain JavaScript across two route-scoped files.
- Bounded event handlers and no framework rerenders.
- No polling, network callback, third-party execution, or expensive computation.
- The larger assessment script loads only on the Support Needs route.

**Status:** Not measured on representative devices or field traffic. No claim is made that the INP threshold is met.

### Cumulative Layout Shift

Both HTML image elements declare explicit width and height. The site uses system fonts and has no advertisement, embed, remote banner, asynchronous content feed, or injected third-party UI. Form and assessment panels change only after deliberate interaction.

Explicit image dimensions allow browsers to reserve aspect-ratio space and reduce layout shifts ([web.dev CLS guidance](https://web.dev/articles/optimize-cls?hl=en)).

**Status:** Low obvious source-level risk, but not measured with production lab or field tooling. No claim is made that the CLS threshold is met.

## 6. Images and Media

The complete image payload is **1,208 bytes**:

- Home illustration SVG: 892 bytes.
- Favicon SVG: 316 bytes.

SVG remains the appropriate format for both vector assets. Converting them to raster AVIF or WebP would add complexity without a demonstrated saving. Both content-image occurrences have explicit dimensions.

If approved photography is added later:

- Confirm rights and model releases before performance work.
- Generate appropriately sized AVIF/WebP variants.
- Use `srcset` and `sizes` for responsive delivery.
- Include explicit width and height.
- Do not lazy-load the actual LCP image.
- Rebaseline transfer size and LCP before acceptance.

## 7. CSS, JavaScript, Fonts, and Accessibility

The 24,292-byte stylesheet includes shared layout, responsive breakpoints, visible focus, forced-colour support, print behavior, and reduced-motion handling. Removing these accessibility rules for a smaller score is prohibited.

The shared 7,685-byte script handles navigation and the Contact preview. The 8,982-byte assessment script is loaded only by Support Needs. Splitting either file further would increase requests and maintenance overhead without a measured benefit.

There are no `@font-face` rules or icon fonts. The system font stack eliminates font transfer and swap delay.

Source minification was not added. Production hosting can compress text responses while the repository preserves readable, auditable source. Any future build/minification step must justify its maintenance, caching, and source-map consequences with measurements.

## 8. Hosting, Compression, and Caching

The Python preview is a development server and does not represent production compression, CDN, TLS, or cache policy.

For the approved release candidate:

- Enable Brotli or gzip for HTML, CSS, JavaScript, SVG, XML, and text.
- Keep HTML fresh enough for prompt content and policy corrections.
- Use long-lived immutable caching only for fingerprinted assets with a defined invalidation strategy.
- Coordinate cache behavior with the response security headers required by the Security report.
- Verify cold and warm loads from the target service region on a representative mobile profile.
- Avoid third-party origins and resource hints unless measured user value justifies them.

Browser caching avoids unnecessary network requests, but cache lifetime and invalidation should be chosen according to how each resource changes ([web.dev HTTP cache guidance](https://web.dev/articles/http-cache?hl=en)).

## 9. Performance Budget

| Metric | Budget | Current result |
|---|---:|---:|
| CSS + JavaScript | ≤100 KB uncompressed | 40,959 bytes — pass |
| Complete source before production photos | ≤150 KB uncompressed | 129,648 bytes — pass |
| Support Needs HTML | ≤30 KB uncompressed | 21,775 bytes — pass |
| Runtime dependencies | 0 unless approved | 0 — pass |
| Remote fonts | 0 unless approved | 0 — pass |
| Third-party runtime scripts | 0 unless justified | 0 — pass |
| Home hero image | ≤100 KB | 892 bytes — pass |
| Explicit content-image dimensions | 100% | 100% — pass |
| Broken local references | 0 | 0 — pass |

Rebaseline immediately after adding photography, analytics, a real form provider, maps, chat, scheduling, consent tooling, a CMS, or any other dependency or third party.

## 10. Optimizations Performed

No source change was justified by the baseline.

| Measurement | Baseline | Post-review | Change |
|---|---:|---:|---:|
| Complete source | 129,648 bytes | 129,648 bytes | 0 |
| CSS + JavaScript | 40,959 bytes | 40,959 bytes | 0 |
| Runtime dependencies | 0 | 0 | 0 |
| Remote fonts | 0 | 0 | 0 |
| Third-party runtimes | 0 | 0 | 0 |
| Performance source edits | 0 | 0 | 0 |

Preserving the implementation avoids unnecessary risk to navigation, accessibility, form validation, privacy boundaries, SEO metadata, security, and maintainability.

## 11. Findings

### PERF-001 — Production Core Web Vitals are unverified

- **Severity:** Production blocker; expected local-pilot limitation
- **Status:** Open until an approved hosted release candidate exists
- **Recommendation:** Run recorded mobile Lighthouse tests against multiple representative routes, exercise the Contact and Support Needs interactions, and evaluate field data at the 75th percentile when sufficient privacy-approved traffic exists. Google recommends combining field and lab tools because each reveals different aspects of LCP, INP, and CLS ([web.dev measurement workflow](https://web.dev/articles/vitals-tools)).

### PERF-002 — Production compression and caching are undefined

- **Severity:** Production hardening
- **Status:** Awaiting approved host and final asset URLs
- **Recommendation:** Verify compression, HTML freshness, fingerprinted-asset caching, HTTPS/CDN behavior, and security headers on actual responses. Compare cold and warm loads.

### PERF-003 — Future media and integrations can invalidate the budget

- **Severity:** Change-triggered risk
- **Status:** No current overage
- **Recommendation:** Measure every approved photograph, dependency, font, analytics tool, form provider, map, chat, scheduler, or consent layer before acceptance. Remove costs whose user value does not justify their transfer, privacy, and main-thread impact.

No current performance defect requires a source-code or debugging handoff.

## 12. Test Coverage and Limitations

Completed:

- Exact source and per-route byte inventory.
- Independent gzip-size estimate for every text asset.
- Twenty-sample local Home and Support Needs response baselines.
- Initial request-architecture review.
- Image dimension, deferred-script, font, remote-resource, and reduced-motion audits.
- Factory project check and all 215 local references.
- YYZ Caregivers frontend smoke suite.
- Both JavaScript syntax checks.
- All 50 factory regression tests; real projects unchanged and no production deployment.

Not measured:

- Production Lighthouse score.
- Throttled lab LCP, INP, or CLS.
- Chrome User Experience Report or other field data.
- Production TTFB, TLS, CDN behavior, compressed transfer, cache hit rate, or regional latency.
- Real low-end mobile CPU, memory, energy, or data use.

The Lighthouse attempt failed before measurement because the sandboxed audit process could not attach to Chrome. It produced no usable report, and no score has been inferred or fabricated.

## 13. QA Handoff and Readiness

**Performance stage passed for the local pilot.** The project may proceed to Accessibility after the workflow is explicitly advanced. No performance source change requires an additional QA defect cycle.

Final review should preserve navigation, form validation, focus management, responsive behavior, metadata, security boundaries, no-send/no-store behavior, and the documented budgets. A production candidate must additionally verify Core Web Vitals, compression, caching, CDN behavior, and third-party impact under recorded conditions.

No functionality, accessibility feature, SEO control, security safeguard, deployment setting, or website source file was changed. No commit, push, approval, deployment, or workflow advancement occurred.
