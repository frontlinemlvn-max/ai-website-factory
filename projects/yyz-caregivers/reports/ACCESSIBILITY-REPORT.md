# YYZ Caregivers — Accessibility Report

- **Review date:** September 9, 2026
- **Target:** WCAG 2.2 AA where applicable
- **Overall status:** **READY FOR FINAL REVIEW WITH DOCUMENTED MANUAL-TEST LIMITATIONS**

## Accessibility Summary

The seven-page static pilot has strong accessibility foundations. Source inspection, the browser accessibility tree, responsive review, contrast calculations, maintained smoke checks, and interaction testing found no reproducible Critical, High, Medium, or Low accessibility defect.

Finding count: Critical 0, High 0, Medium 0, Low 0, Informational limitations 3. The highest remaining concern is incomplete physical screen-reader and full native keyboard traversal testing; this is a production-verification requirement, not a confirmed defect.

## Findings

### A11Y-001 — Physical screen-reader testing remains outstanding

- **Severity:** Informational / production verification
- **Evidence:** The browser accessibility tree exposes named landmarks, headings, controls, labels, group names, current-page states, form guidance, and status content. No VoiceOver, NVDA, JAWS, or TalkBack session was performed.
- **User impact:** An assistive-technology-specific announcement or navigation issue could remain undetected.
- **Retest:** Test the primary journeys and Contact validation with VoiceOver on Safari and at least one additional representative screen-reader/browser combination.

### A11Y-002 — Full native keyboard traversal requires physical verification

- **Severity:** Informational / production verification
- **Evidence:** Menu activation with Enter, Escape close behavior, focus return, native FAQ disclosure, button/link semantics, source focus order, and visible focus CSS were reviewed. The automation surface did not reliably dispatch repeated native Tab traversal, so no claim of a complete physical keyboard session is made.
- **Retest:** Traverse every page using Tab and Shift+Tab; operate links, menu, radios, checkbox, select, FAQ disclosures, form submit, summary links, and restart control using native keys; verify no trap and a consistently visible indicator.

### A11Y-003 — Operating-system modes and zoom need final manual coverage

- **Severity:** Informational / production verification
- **Evidence:** Dedicated `prefers-reduced-motion` and `forced-colors` rules exist. Responsive testing found no horizontal overflow at 320, 390, 768, 1024, and 1440 CSS pixels. Live forced-colour, reduced-motion, browser zoom, and physical-touch sessions were not performed.
- **Retest:** Verify 200% and 400% zoom/reflow, Windows High Contrast, reduced motion, and representative touch operation before production approval.

## Keyboard Review

- The skip link is first in source order and targets `#main-content`.
- Navigation uses native links and a native menu button with `aria-expanded` and `aria-controls`.
- Enter opens the mobile menu; Escape closes it and returns focus to the trigger.
- FAQ items use native `details` and `summary` controls.
- No modal, tab widget, carousel, hover-only control, precision gesture, or keyboard trap exists.
- Global `:focus-visible` styling uses a 2px blue outline with a 3px offset; the skip link becomes visible on focus.
- DOM and form order are logical: name, email, phone, preferred contact method, category, municipality, message, acknowledgement, submit.

## Forms and Interaction Review

All Contact controls have visible, programmatically associated labels. Required controls use native `required`; the radio set uses `fieldset` and `legend`; guidance and errors use `aria-describedby`. Empty submission focuses a linked error summary. Field errors are specific, set `aria-invalid`, and are not communicated by colour alone. Email and phone requirements update according to the chosen method. A message over 500 characters is blocked with an associated error; exactly 500 succeeds. The success panel has `role="status"`, receives focus, clearly states nothing was sent, and the restart button restores the form and focuses Preferred name.

The form remains disabled with an explanatory message when JavaScript is unavailable. It does not transmit or store personal information.

## Semantic and Screen Reader Review

Every page declares `lang="en-CA"`, contains one `main` and one meaningful `h1`, and uses native `header`, `nav`, `section`, `article`, `aside`, and `footer` elements appropriately. Navigation regions have distinct accessible names. Current pages use `aria-current="page"`. Section labels resolve to existing headings. Buttons perform actions and links navigate.

The repeated abstract image is decorative in context and uses empty alternative text; its wrapper is hidden from assistive technology. Inline wordmark icons are also hidden while readable brand text remains. No audio, video, data table, dialog, canvas, or meaningful image requiring additional alternatives exists.

Accessibility-tree inspection confirmed meaningful names for text fields, radio buttons, checkbox, select, menu button, links, form regions, complementary content, and dynamic result content. This inspection does not replace a real screen-reader session.

## Visual and Responsive Review

Automated contrast checks passed AA text thresholds: white/teal 6.73:1, navy/warm-white 13.33:1, body/warm-white 15.30:1, muted/warm-white 7.45:1, success 6.45:1, warning 7.97:1, error 6.53:1, and disabled text 4.83:1. Form-control borders pass the 3:1 non-text threshold at 3.52:1.

Base body text is 18px with 1.65 line height. Controls and navigation targets generally provide at least 44–48px clickable rows; radio and checkbox inputs sit inside larger labelled targets. Status, required, current, error, and success meanings use text or programmatic state rather than colour alone. Browser zoom is not disabled.

## Test Methods and Limitations

Performed: semantic/source audit, heading and landmark review, accessibility-tree inspection, menu keyboard operation, FAQ native-control review, form error/success review, contrast calculation, responsive overflow review, link/asset validation, and maintained smoke tests.

Not performed: physical screen-reader testing, complete native Tab traversal, live forced-colour/reduced-motion modes, physical touch-device testing, and manual 200%/400% browser zoom. Automated and source checks cannot prove full WCAG conformance, so this report does not claim certification.

## Accessibility Readiness and Handoff

**Ready for Final Review.** No verified accessibility defect requires remediation in the current local pilot. Final Review must retain A11Y-001 through A11Y-003 as production verification items and preserve semantics, labels, error behavior, focus styles, reduced-motion rules, contrast, responsive layout, and the no-send privacy boundary.

Return to Accessibility review if production adds photography, a live form, third-party widgets, scheduling, maps, media, a CMS, or materially different content. No source file, deployment setting, Git history, or external system was changed during this review.

## Addendum — September 12, 2026 (Support Needs Assessment retest)

This report's original scope (September 9, 2026) predates `intake.html`, the eighth route added September 10, 2026. A follow-up review of the Support Needs Assessment's "Which general topics would you like to discuss?" group found and corrected one defect.

### A11Y-004 — Fixed: `required` misapplied to a single checkbox in an at-least-one group

- **Severity:** Medium (now fixed)
- **Evidence:** In `src/intake.html`, the topics `fieldset` legend states "Choose at least one," but only the first checkbox (`topic-routines`, "Personal routines") of the ten-item group carried the HTML `required` attribute. Unlike same-named radio buttons, `required` on a checkbox is not a group construct — it marks that one specific control as individually mandatory. This mismatched the group's actual "select at least one" requirement exposed to assistive technology: a screen reader announced "Personal routines... required" without indicating the same for its siblings, implying that item specifically must be checked.
- **User impact:** A screen-reader or other AT user could be misled into believing "Personal routines" must always be selected, rather than any one topic satisfying the requirement.
- **Fix:** Removed the `required` attribute from the `topic-routines` checkbox. Group-level "at least one selected" enforcement already existed independently in `assets/js/assessment.js` (validated against `groups.topics`) and is surfaced via the fieldset's visible "(required)" legend text and the associated `topics-error` element — so no functional validation changed, only the misleading per-control semantic was removed.
- **Verified unaffected:** The two `acknowledgements` checkboxes each keep `required`, which is correct there because the legend requires confirming *both* statements individually, not "at least one of many."
- **Retest performed:** Reran the full frontend smoke suite (`tests/frontend_smoke.py`), including "support topics use an accessible required group" — all checks passed.
