# YYZ Caregivers — UI/UX Specification

Status: Design revised for the eight-page non-sending pilot

> Change-control note — September 10, 2026: This revision adds a browser-only Support Needs Assessment. It uses broad daily-living topics and creates only a temporary on-screen summary. It is not a patient intake, clinical assessment, diagnosis tool, triage flow, eligibility decision, price calculator, care-plan generator, booking, or submission. It must not transmit, persist, download, print by default, or attach answers to contact links.

## 1. Design Summary

- **Project:** YYZ Caregivers
- **Design objective:** Create a calm, respectful, highly legible website that helps Greater Toronto Area families understand a proposed private-home support service and find a safe next step.
- **Primary audience:** Older adults, adults who may need daily-living support, and family members researching support on their behalf.
- **Primary conversion:** Contact YYZ Caregivers or organize broad topics through the non-sending Support Needs Assessment before making contact separately.
- **Design direction:** Warm, reassuring, uncluttered, and practical. The interface uses generous spacing, plain language, large readable type, strong focus treatment, soft rectangular surfaces, and restrained navy/teal accents.
- **Experience principle:** Dignity before persuasion. The site must feel helpful without using fear, urgency, fabricated authority, or pressure.
- **Pilot boundary:** Every page distinguishes confirmed contact details from unverified business claims and clearly labels both forms as local, non-sending demonstrations.

## 2. Design Assumptions

- Candidate logo and photographs have been supplied, but ownership, model releases, accessibility treatment, source quality, and public-use rights are not yet confirmed. All visual tokens below remain reversible pilot choices.
- A text wordmark reading “YYZ Caregivers” replaces a logo. It must not include a certification seal, medical cross, shield, award, or other implied credential.
- No genuine staff, client, home, or service photography is available. The pilot uses subtle abstract shapes and simple line motifs rather than fabricated people.
- Confirmed defaults are phone 416-731-5383, public/privacy email frontline.mlvn@gmail.com, email preferred, Monday-Friday 9:00 a.m.-6:00 p.m. Eastern Time, response within 12 business hours, “Now accepting new client inquiries,” and no public address.
- The service catalogue, exact municipalities, credentials, screening practices, insurance, pricing, actual capacity, domain control, and image rights remain unverified.
- The site is English-only for the pilot. The layout must tolerate text expansion so later translation remains possible.
- The Contact form and Support Needs Assessment are browser-only demonstrations. They never submit, store, email, schedule, score, recommend, or create a care relationship.
- No analytics, cookie banner, chat, map, booking widget, testimonials, ratings, or partner logos appear.
- The design targets WCAG 2.2 AA, subject to implementation testing and specialist review.

## 3. Information Hierarchy

### Global priority

1. What YYZ Caregivers proposes to help with
2. Who the service is intended for
3. What is confirmed versus still awaiting owner verification
4. How a consultation may work
5. How to organize broad support topics safely
6. How to reach the Contact page safely
7. Policy and pilot limitations

The “Request a consultation” action is consistently visible but never styled as urgent. Visitors can always explore Services and FAQ before choosing contact.

### Page priorities

- **Home:** Plain-language value → proposed support categories → process → service-area assumption → common questions → consultation CTA.
- **About:** Intended values and approach → what still requires verification → Services CTA.
- **Services:** Proposed categories and boundaries → how consultation may work → service-area note → Contact CTA.
- **Contact:** Privacy and non-emergency boundary → demonstration form → no-send confirmation → verified contact details and response expectations.
- **Support Needs Assessment:** Safety boundary → broad non-clinical choices → required acknowledgements → temporary review summary → separate contact actions.
- **FAQ:** Scope and fit → consultation → area, pricing, credentials, privacy, and emergency questions → Contact CTA.
- **Privacy:** Pilot data behaviour → information not collected → production requirements → verified privacy contact.
- **Terms:** Pilot and informational-use boundaries → accuracy/availability limits → production review requirement.

## 4. Page Layout Specifications

### Global page frame

All pages use this order:

1. Skip link
2. Pilot-status bar
3. Site header and navigation
4. Main content with one `h1`
5. Optional closing CTA band
6. Site footer

The default content container is `min(100% - 32px, 1180px)` on mobile and grows to 48px horizontal gutters on wide screens. Reading copy is capped near 66 characters per line. Page sections use 64px vertical spacing on mobile and 96px on desktop, reduced for tightly related content.

### Home — `index.html`

**Purpose:** Give a clear first impression and route visitors toward Services or Contact.

**Section order:**

1. **Pilot-status bar:** “Local pilot — forms do not send or store information, and service details still require confirmation.” Link to the explanatory note lower on the page.
2. **Header:** Text wordmark, primary routes, and consultation button.
3. **Hero:** Eyebrow “Private-home support · GTA pilot”; `h1` “Support at home, with clarity and respect”; short supporting paragraph; primary “Request a consultation”; secondary “Explore services”; abstract home-and-connection visual.
4. **Audience reassurance:** Three concise statements: clear information, respectful choices, and a straightforward next step. These are experience principles, not business-performance claims.
5. **Proposed services:** Four cards for personal routines, companionship, meal and household support, and mobility-related assistance. Each card carries “Service details to be confirmed.”
6. **How a consultation may work:** Three numbered steps—share a general question, discuss possible fit, confirm next steps—with a note that the process is provisional.
7. **Dignity and clarity panel:** Short copy about respectful language, visitor choice, and no pressure.
8. **Service-area panel:** GTA illustration or text treatment with “Exact municipalities require confirmation”; no map boundaries.
9. **FAQ preview:** Four high-priority questions with links to the full FAQ.
10. **Pilot verification notice:** Lists the business details that must be confirmed before public launch.
11. **Closing CTA:** “Have a general question?” with Contact and Services actions.

**Desktop:** Hero uses a 7/5 text-to-visual grid. Service cards use a four-column grid only when each card remains at least 240px wide. Process steps use three columns.

**Mobile:** Everything stacks in source order. Hero actions become full-width below 420px. Cards use one column. The abstract visual moves below the actions and remains decorative.

### About — `about.html`

**Purpose:** Explain the intended approach without inventing an operating history.

**Section order:** Page header; intended mission; four-value grid; “What respectful support means in this pilot” content split; owner-verification notice; Services CTA.

**Header behavior:** Standard global header with About marked `aria-current="page"`.

**CTA placement:** “Explore proposed services” follows the approach content; “Request a consultation” appears in the closing band.

**Desktop:** Mission text and a quiet abstract visual use a 6/6 split. Values use two columns rather than four to preserve readable descriptions.

**Mobile:** Visual follows mission copy. Values stack. The verification notice remains full width and is not hidden in an accordion.

### Services — `services.html`

**Purpose:** Present the proposed service model and boundaries in a scannable format.

**Section order:** Page header; in-page service links; four detailed service cards; service-boundary notice; consultation process; provisional service-area panel; FAQ cross-link; CTA.

Each service card contains a title, one-sentence description, a short “may include” list, and a persistent “Confirm with YYZ Caregivers” label. Avoid “we provide” until the owner verifies the scope.

**CTA placement:** One contextual “Ask about support needs” action after the service cards and one closing Contact action.

**Desktop:** In-page links appear as a wrapping row. Detailed cards use two columns. Process steps use three columns.

**Mobile:** In-page links become a vertical list of large targets. Cards and process steps stack. Long lists remain visible rather than collapsed.

### Contact — `contact.html`

**Purpose:** Demonstrate a safe consultation-request experience without implying a live communication channel.

**Section order:** Page header; prominent non-emergency and privacy notice; two-column contact area; demonstration form; “what happens in this pilot” explanation; verified phone/email card; response-expectation note; related FAQ and Support Needs Assessment links.

**Desktop:** The form occupies roughly two-thirds of the content width. A one-third side panel repeats privacy boundaries, pilot status, and future verified contact methods. The side panel is not sticky.

**Mobile:** Notices appear before the form. All fields and actions are one column. The side panel becomes an ordinary section after the form.

**CTA behavior:** Submit label is “Preview consultation request,” never “Send” or “Book.” The result must say clearly that no information was sent or stored.

### Support Needs Assessment — `intake.html`

**Purpose:** Help a prospective client, family member, friend, or authorized representative organize broad support topics for a future conversation without disclosing diagnoses or creating a record.

**Page header:** Eyebrow “Non-sending support tool”; `h1` “Organize topics for a support conversation”; short introduction explaining that answers stay only on the current page and the result is not a care plan or recommendation.

**Section order:**

1. Pilot-status bar with direct no-send language.
2. Standard header with Support Needs Assessment marked current when it is visible in navigation.
3. Page header and a short three-point “Before you begin” list: general topics only; nothing is sent or stored; emergencies require appropriate local emergency assistance.
4. Side-by-side non-emergency and privacy notices, stacked on mobile.
5. Assessment shell with a visible introduction and field groups.
6. Review state titled “Topics you may want to discuss.”
7. Separate contact card with verified email/phone, contact hours, expected response, and an explicit statement that YYZ Caregivers has not received the summary.
8. Privacy and FAQ cross-links.
9. Standard footer.

**Form presentation:** Use one continuous page with five numbered field groups, not a wizard. All sections remain visible so users can understand the scope, move backward freely, use browser Find, and avoid losing context. A quiet vertical progress rail may show section numbers on desktop, but it must not imply completion scoring and disappears on narrow screens.

**Field groups:**

1. **About this conversation** — who is completing the form; optional preferred name; preferred follow-up method.
2. **Where and when support may help** — optional city/municipality; time-of-day preferences; frequency to discuss.
3. **Topics to discuss** — large checkbox cards for personal routines, mobility/getting around, meal preparation, light household routines, companionship/social connection, caregiver respite, accompaniment to appointments or errands, reminders/routine organization, another general need, and unsure.
4. **Communication and accessibility preferences** — large print/written follow-up, slower-paced conversation, language preference, mobility-access consideration for a future visit, another preference, none/unsure.
5. **Review understanding** — optional general note with sensitive-information warning, followed by the two required acknowledgements specified by Architecture.

**Choice-card design:** Checkbox and radio inputs remain native and visible. Each choice is a minimum 52px high bordered surface with the control first, concise label second, and optional one-line description. The complete card may activate the input through its label. Selected state uses border, inset indicator, and text—not colour alone. Never preselect support topics or representative status.

**Review action:** Primary button label is “Review my topics.” It validates required groups locally, then replaces or moves below the form with a review panel. It must never say Submit, Send, Get results, Get matched, View care plan, or See recommendations.

**Review panel:** Begin with a persistent notice: “Nothing was sent or stored. This is not a care plan or recommendation.” List only non-empty broad selections under neutral headings. Omit empty optional sections rather than showing “None.” Provide “Edit my answers” and “Start over” as buttons. Provide email and phone as separate links outside the summary; neither link contains assessment answers.

**Focus behaviour:** After invalid review, focus the linked error summary. After a valid review, focus the review heading (`tabindex="-1"`). “Edit my answers” reveals the form and focuses its legend/heading. “Start over” uses a lightweight inline confirmation because it discards local entries; after confirmation, clear everything and focus the page's assessment heading. Do not use a modal.

**Desktop:** Use a maximum 920px assessment shell. Field-group content is single-column; choice cards may use two columns when every label remains readable. Notices may use two equal columns. The review summary stays within 760px for scanning.

**Mobile:** Use one column and full-width actions below 420px. Choice cards remain at least 48px tall with comfortable gaps. Keep labels above controls, never place two text inputs side by side, and preserve source order. At 320 CSS pixels and 400% reflow, no horizontal scrolling or sticky element may obscure content.

**No-JavaScript state:** The assessment form remains visible for review but its action is disabled with adjacent text: “JavaScript is required to create a local summary. Nothing can be submitted from this page.” Email and phone links remain available.

### FAQ — `faq.html`

**Purpose:** Answer common questions while identifying unconfirmed operational details.

**Section order:** Page header; short scope note; grouped FAQ sections for Services, Consultation, Service Area, Pricing and Scheduling, Privacy, and Emergencies; owner-verification panel; Contact CTA.

Use native `details`/`summary` elements. Keep the first item closed by default so no answer receives implied priority. Do not add “expand all” in the pilot.

**Desktop:** FAQ content is capped near 820px with a quiet category navigation column only if it remains useful after content is written.

**Mobile:** Single column. Summary rows have at least 48px height, clear plus/minus treatment, and generous separation.

### Privacy Policy — `privacy.html`

**Purpose:** Explain actual pilot data behavior and mark production policy needs.

**Section order:** Page header; pilot-policy warning; table of contents; information not collected; demonstration form behaviour; cookies and analytics; third-party services; production review requirements; verified privacy contact; last-reviewed label.

**Layout:** Policy copy uses a maximum 72-character line length. A table of contents becomes a simple vertical list. Notices remain in normal document flow.

**Mobile:** No side navigation or sticky table of contents. Headings and anchor targets include enough scroll margin below the header.

### Terms — `terms.html`

**Purpose:** State informational and pilot boundaries without presenting draft architecture as approved legal terms.

**Section order:** Page header; unapproved-draft warning; table of contents; pilot-only use; no service or care relationship; non-emergency use; accuracy and availability; intellectual-property placeholder; external links; owner/professional review; last-reviewed label.

**Layout and mobile behavior:** Match Privacy to reduce cognitive load and development variance.

### Footer behavior on every page

Footer columns contain the text wordmark and pilot summary, Explore links, Policy links, and verified public email/phone with “Email preferred.” At mobile widths, columns stack with visible headings. Privacy and Terms are never hidden behind a menu. The business address is not displayed. The final line identifies the page as a local pilot and contains no copyright year until ownership wording is confirmed.

## 5. Component System

### Pilot-status bar

- **Purpose:** Prevent the local pilot from being mistaken for a live service.
- **Variant:** One neutral-warning treatment only.
- **States:** Default and focused link.
- **Responsive behavior:** Wraps naturally; never truncates.
- **Accessibility:** Text states the meaning without relying on colour or an icon.

### Site header and navigation

- **Purpose:** Provide predictable access to Home, About, Services, FAQ, and Contact.
- **Variants:** Desktop inline navigation and mobile disclosure navigation.
- **States:** Default, hover, focus-visible, active/current page, menu open, menu closed.
- **Responsive behavior:** Inline at 960px and above; enhanced disclosure below 960px.
- **Accessibility:** Real links, button-based menu trigger, accurate `aria-expanded`, visible current page, and usable fallback when JavaScript is unavailable.

### Buttons and text links

- **Primary button:** Solid dark teal, white text. Reserved for consultation actions.
- **Secondary button:** Transparent or warm-white surface with navy border and text.
- **Text link:** Underlined by default in paragraphs; navigation links use another visible active/focus cue.
- **States:** Default, hover, focus-visible, active, disabled, loading, success where applicable.
- **Accessibility:** Minimum 44×44px target where practical, clear labels, no colour-only state, and 2px focus outline with offset.

### Hero

- **Purpose:** Communicate audience, value, next step, and pilot status within the first viewport without crowding.
- **Variants:** Home hero with abstract visual; inner-page header without decorative art.
- **Responsive behavior:** Two columns on wide screens; stacked on mobile.
- **Accessibility:** Decorative shapes are ignored by assistive technology. Heading and actions precede visuals in source order.

### Content cards

- **Variants:** Service, value, process, and FAQ-preview cards.
- **States:** Default; optional hover lift only when the entire card is a link; focus state belongs to the actual link.
- **Responsive behavior:** One to four columns based on content width, never merely viewport width.
- **Accessibility:** Card headings use the correct document level; avoid nested interactive controls; labels state provisional content directly.

### Notice panel

- **Variants:** Pilot information, privacy caution, non-emergency caution, owner verification, success, and error.
- **States:** Static except live form feedback.
- **Responsive behavior:** Full width with 16–24px padding.
- **Accessibility:** Each variant includes a short heading; status meaning appears in text; dynamic messages use the appropriate live-region behavior without stealing focus.

### Consultation process steps

- **Purpose:** Explain a simple provisional path without promising response times or outcomes.
- **Variants:** Three numbered steps.
- **Responsive behavior:** Horizontal at desktop, stacked on mobile.
- **Accessibility:** Implement as an ordered list so sequence is available without visual styling.

### FAQ disclosure

- **Purpose:** Keep long answers manageable while using native browser interaction.
- **States:** Closed, open, hover, focus-visible.
- **Responsive behavior:** Full width at all sizes.
- **Accessibility:** Native `details` and `summary`; visible open indicator; no custom keyboard model.

### Consultation form

- **Purpose:** Demonstrate the future general-inquiry flow with data minimization.
- **Variants:** Default, validation error, submitting/loading placeholder for future production, and local success.
- **Responsive behavior:** One column; related short fields may use two columns only above 768px.
- **Accessibility:** Persistent labels and hints, programmatic required state, grouped controls, error summary, field associations, focus management, and explicit no-send language.

### Support Needs Assessment form

- **Purpose:** Organize broad topics without collecting or transmitting information.
- **Variants:** Editable form, validation error, local review summary, and reset-confirmation state. There is no loading or submitted state.
- **Structure:** Semantic form; numbered `section` elements or grouped containers; `fieldset`/`legend` for radio and checkbox groups; visible labels and hints for text/select controls; error summary before field groups; action row at the end.
- **Responsive behavior:** Single-column field groups at every width; choice cards may form two columns from 768px when content fits; review actions wrap without reordering.
- **Accessibility:** Native controls, no custom checkbox keyboard model, no required field conveyed by colour alone, linked errors, focus-managed review state, and reset confirmation in normal flow.

### Assessment review summary

- **Purpose:** Restate the visitor's broad selections for their own use.
- **States:** Hidden before valid review; visible review; edit transition; reset confirmation.
- **Presentation:** White raised surface with Navy heading, neutral definition lists or heading/list groups, and a prominent pilot notice. Avoid success-green because review is not a completed service or favourable result.
- **Accessibility:** `aria-live` is unnecessary when focus moves to the review heading. Do not place the whole summary in a live region. Use semantic headings and lists; keep Edit and Start over as buttons.

### CTA band

- **Purpose:** Provide a calm next step at the end of content.
- **Variants:** Teal-tinted light surface and dark navy surface.
- **Responsive behavior:** Text/actions inline on wide screens and stacked on mobile.
- **Accessibility:** One primary action; sufficient contrast; no background text over photography.

## 6. Navigation Design

### Desktop navigation

At 960px and above, show the wordmark on the left and Home/About/Services/Support Needs/FAQ/Contact links in the centre-right when they fit without crowding. Use the shorter visible label “Support Needs” for `intake.html`. The primary consultation button remains at the far right. Privacy and Terms stay in the footer. Use `aria-current="page"` and a visible underline or bottom border for the current route.

The header is static rather than sticky. This preserves vertical space for zoomed text and smaller laptops. Consultation actions repeat in page content, so no essential action depends on a persistent header.

### Mobile navigation

Below 960px, show the wordmark and a labeled “Menu” button. With JavaScript enhancement active, the button expands a full-width panel directly below the header. Links remain vertically stacked with at least 48px row height. The button changes to “Close menu” or otherwise exposes an equivalent accessible state.

- Escape closes the enhanced menu and returns focus to the trigger.
- Activating a navigation link closes the menu naturally through page navigation.
- Clicking outside may close it but must not be the only closing method.
- Without JavaScript, navigation links remain visible in a wrapped or stacked layout.
- Opening the menu does not trap focus because it is an inline disclosure, not a modal.

### Breadcrumbs

Breadcrumbs are optional for this shallow eight-page site. Use them only on Privacy and Terms if user testing shows that they improve orientation. They must not replace the page title or global navigation.

## 7. Responsive Design

### Mobile: 320–767px

- One-column page flow and 16px horizontal gutters.
- Body text begins at 18px with generous line height.
- Hero, cards, notices, form, CTAs, and footer columns stack in source order.
- Assessment choice cards, field groups, review sections, and actions use one column; there is no sticky progress control.
- Primary and secondary hero buttons become full width below 420px.
- No horizontal scrolling at 320 CSS pixels at 400% zoom/reflow testing conditions.
- Decorative art is reduced or removed when it competes with content.
- Touch targets are at least 44px in both dimensions where practical, with adequate spacing between controls.

### Tablet: 768–959px

- 24px horizontal gutters.
- Two-column service/value grids where content remains balanced.
- Form may pair short fields while labels and errors remain independent.
- Assessment choice cards may use two equal columns, but field groups remain in one logical reading sequence.
- Mobile disclosure navigation remains in use to avoid crowded labels.

### Desktop: 960–1279px

- Inline navigation and 32px horizontal gutters.
- Hero uses a 7/5 grid; service and process content uses two or three columns.
- Main content maximum width is 1180px; long-form content remains much narrower.

### Wide desktop: 1280px and above

- Maximum container remains 1180px; extra viewport width becomes outer whitespace.
- Section gaps may increase, but text and controls do not scale indefinitely.

Images use `max-width: 100%`, explicit intrinsic dimensions, and responsive sources when photographs are eventually approved. Crops must preserve faces and meaningful context at every breakpoint. No text is embedded in images.

## 8. Typography System

Use a local system stack to avoid remote requests and unpredictable rendering:

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont,
  "Segoe UI", sans-serif;
```

`Inter` is listed only as a locally available preference; do not download it. System fonts are the expected result.

- **Display / `h1`:** `clamp(2.25rem, 5vw, 4.5rem)`, weight 700, line-height 1.05–1.12, letter spacing `-0.025em`, maximum 15 words.
- **`h2`:** `clamp(1.75rem, 3vw, 2.75rem)`, weight 700, line-height 1.15, maximum two short lines.
- **`h3`:** `clamp(1.25rem, 2vw, 1.5rem)`, weight 650–700, line-height 1.25.
- **Body large:** 1.25rem, line-height 1.6, used for hero and page introductions.
- **Body:** 1.125rem mobile and up to 1.25rem for long reading areas, line-height 1.6–1.7.
- **Small/supporting text:** Never below 0.9375rem; line-height at least 1.5.
- **Labels:** 1rem, weight 650, line-height 1.4.
- **Buttons/navigation:** 1rem, weight 650, sentence or title case; never all caps.
- **Eyebrows:** 0.875–0.9375rem, weight 700, moderate letter spacing; concise and not used as the only heading.

Keep paragraphs near 60–66 characters per line and left aligned. Do not justify text. Allow user font-size overrides without clipping.

## 9. Spacing System

Use the following base scale only:

- `space-1`: 4px
- `space-2`: 8px
- `space-3`: 12px
- `space-4`: 16px
- `space-5`: 24px
- `space-6`: 32px
- `space-7`: 48px
- `space-8`: 64px
- `space-9`: 96px

Apply 8–12px between labels and controls, 16px between related content, 24–32px inside cards/notices, 48px between subsections, and 64–96px between major sections. Use logical properties so spacing remains adaptable to future language direction.

## 10. Color System

These are pilot tokens and require contrast verification in implementation:

- **Navy 900 / primary text:** `#123047`
- **Navy 800 / dark surface:** `#173F5B`
- **Teal 700 / primary action:** `#0B675F`
- **Teal 100 / accent surface:** `#DDF2EE`
- **Warm white / page:** `#FFFCF7`
- **Pure white / raised surface:** `#FFFFFF`
- **Soft grey-green / alternate surface:** `#F1F5F3`
- **Body text:** `#18252D`
- **Muted text:** `#46565E`
- **Border:** `#C5D2CE`
- **Focus:** `#005FCC`
- **Success:** `#17643A` on `#E8F6ED`
- **Warning:** `#694100` on `#FFF2C7`
- **Error:** `#A51D22` on `#FDEBED`
- **Disabled text:** `#5F6B71` on `#EEF1F0`

Primary buttons use white text on Teal 700. Dark CTA bands use warm-white text on Navy 900. Body copy uses Body Text on Warm White or White. Muted text is reserved for secondary information, never essential instructions. Every status pairs colour with a heading, icon only when useful, and explicit text.

## 11. Form UX

### Contact form field order

1. Preferred name — required, text, maximum 80 characters
2. Email address — conditionally required when email is preferred
3. Phone number — conditionally required when phone is preferred
4. Preferred contact method — required radio group: Email or Phone
5. General inquiry category — required select: Service information, Service area, Consultation process, or Other general question
6. City or municipality — optional; do not request a street address
7. General message — optional, maximum 500 characters
8. Acknowledgement — required checkbox confirming the visitor understands this is a non-sending pilot and will not enter sensitive or emergency information

### Support Needs Assessment field order

1. Who is completing this? — required radio group: Self; Family member or friend; Substitute decision-maker or authorized representative; Other or prefer not to say
2. Preferred name — optional, maximum 80 characters
3. Preferred follow-up method — optional radio group: Email; Phone; Undecided
4. City or municipality — optional, maximum 80 characters; no street address
5. When support may be useful — optional checkbox group: Mornings; Afternoons; Evenings; Overnight; Weekdays; Weekends; Flexible or unsure
6. Frequency to discuss — optional radio group: One-time or short-term; A few times per week; Daily; Respite or occasional; Flexible or unsure
7. Topics to discuss — required checkbox group; use only the ten broad topics approved in Architecture and require at least one selection
8. Communication and accessibility preferences — optional checkbox group plus an optional language field capped at 60 characters
9. General note — optional, maximum 300 characters, with persistent sensitive-information warning and character count
10. Non-sending acknowledgement — required checkbox
11. Non-clinical/non-emergency acknowledgement — required checkbox

Required controls are limited to who is completing, at least one broad topic, and the two acknowledgements. Name, contact preference, location, timing, frequency, accessibility preferences, language, and note remain optional to minimize disclosure.

### Labels and guidance

- Labels stay above fields; placeholders may show formatting examples but never carry required meaning.
- Required status is stated in text near the form heading and programmatically on each required control.
- A privacy notice appears before the first field: “Do not include health, medication, identification, financial, or emergency information.”
- The message field includes a visible character count and repeats “General questions only.”
- Assessment legends are phrased as questions or plain tasks. Group-level hints come immediately after legends and are referenced programmatically by every control when needed.
- Support-topic cards say “Topics to discuss” and never “conditions,” “symptoms,” “needs detected,” or “recommended services.”
- The general-note warning appears before the textarea, not only after it, and repeats the prohibited examples from Architecture.

### Validation

- Validate on attempted submission, then validate a field again when the visitor corrects it. Do not show errors before interaction.
- Place a short error directly below each invalid field and connect it with `aria-describedby`.
- Show an error summary above the form with links to each invalid field. Move focus to the summary only after a failed submission.
- Use specific messages: “Enter your preferred name,” “Enter an email address in the format name@example.com,” or “Choose a preferred contact method.”
- Do not erase valid values after an error.
- Assessment errors use direct text: “Choose who is completing this assessment,” “Choose at least one topic to discuss,” and “Confirm both statements before reviewing your topics.”
- If multiple acknowledgement boxes are missing, the summary links to the first and each checkbox has its own associated message.
- Optional text fields still enforce their length limits. A pasted over-limit value must produce a field error rather than silently entering the review state.

### Success and data clearing

After valid demonstration submission, clear the field values and show a focused or announced success panel:

“Preview complete. This local pilot did not send or store your information. No consultation has been requested.”

Offer “Return to Services” and “Preview another request” actions. Do not imply a response time, confirmation number, booking, or follow-up.

For the assessment, valid review does not use success styling or a success announcement. Hide the editable form, focus “Topics you may want to discuss,” and show only non-empty broad selections. Precede them with: “Nothing was sent or stored. This is not a care plan or recommendation.” “Edit my answers” restores the existing values. “Start over” requests inline confirmation, clears every value after confirmation, removes the summary, and restores focus to the assessment heading.

### Loading and disabled states

Both local pilot actions are immediate and must not simulate network delay. The assessment has no loading, submitting, or completion spinner because no work leaves the page. The Contact architecture reserves a loading state for a separately approved future production version: disable only the submit button, retain its label with a concise “Submitting…” status, and never disable the full form without explanation.

## 12. Interaction States

- **Default:** Clear affordance, visible border, and sufficient contrast.
- **Hover:** Modest colour or border change; no essential information appears only on hover.
- **Focus-visible:** 2px Focus token outline plus 3px offset. Never remove native focus without a stronger replacement.
- **Active/pressed:** Slightly darker fill or minimal 1px translation that does not cause layout movement.
- **Current navigation:** Underline/border plus `aria-current`, not colour alone.
- **Disabled:** Reduced emphasis with persistent readable label and explanatory text when the reason is not obvious. Disabled links are avoided.
- **Loading:** Text status and optional low-motion spinner; control dimensions do not change.
- **Success:** Success heading and explicit outcome, announced politely.
- **Error:** Error heading, specific correction, and programmatic association; never rely on red alone.
- **Empty:** Plain explanation and next action. Optional assessment groups are omitted from review when empty; do not invent “none” answers.
- **Assessment review:** Neutral review surface, focus on its heading, no success icon, score, match percentage, celebration, or implied approval.
- **Assessment edit:** Restore the form with values intact and focus its heading; do not erase selections.
- **Assessment reset:** Inline warning names what will be cleared and offers “Clear my answers” and “Keep my answers.”
- **Menu open:** Trigger state updates; panel is visible in normal flow; background page remains usable.
- **FAQ open:** Indicator rotates or swaps with a brief transition; content appears without large motion.

## 13. Accessibility Requirements

- Target WCAG 2.2 AA and verify rather than assume compliance.
- Preserve semantic page regions and a logical heading outline on all eight pages.
- Make the skip link visible on focus and target the main content correctly.
- Support keyboard-only use for navigation, menu, FAQ, form, links, and all actions.
- Use strong focus treatment that is not clipped by overflow containers.
- Verify text, link, control, icon, focus, success, warning, and error contrast in implementation.
- Support browser zoom to 200% and content reflow at 320 CSS pixels without two-dimensional scrolling, except a genuinely necessary data table (none is planned).
- Keep target sizes at least 44×44px where practical and avoid tightly packed inline actions.
- Use visible labels, fieldsets/legends for grouped controls, helpful autocomplete attributes, and accessible error summaries.
- Keep native checkbox and radio inputs visible inside assessment choice cards; selected styling supplements rather than replaces checked state.
- Do not use ARIA tabs, custom listboxes, drag controls, auto-advancing steps, or `role="application"` for the assessment.
- When the assessment switches between edit and review, manage focus deliberately and keep hidden content out of the accessibility tree.
- Announce menu expanded state and form results accurately; avoid excessive live regions.
- Write meaningful alternative text for approved informational images; decorative abstract artwork uses empty alternative text or CSS.
- Do not autoplay media, flash content, or require motion. Respect reduced-motion preferences.
- Keep language respectful, direct, and free of stereotypes about age, disability, dependence, family roles, or cognition.
- Test with keyboard, screen reader, text resize, zoom/reflow, forced-colour/high-contrast modes, reduced motion, and touch before approval.

## 14. Content Design

### Voice

Use calm, respectful, plain Canadian English. Speak to the person receiving support as an autonomous adult, not only to family members. Prefer “support,” “choices,” and “daily routines” over fear-based language.

### Proposed key copy

- **Home `h1`:** “Support at home, with clarity and respect”
- **Primary CTA:** “Request a consultation”
- **Secondary CTA:** “Explore services”
- **Services CTA:** “Ask about support needs”
- **FAQ CTA:** “Ask another question”
- **Form submit:** “Preview consultation request”
- **Assessment navigation:** “Support Needs”
- **Assessment `h1`:** “Organize topics for a support conversation”
- **Assessment action:** “Review my topics”
- **Assessment review heading:** “Topics you may want to discuss”
- **Assessment boundary:** “Nothing was sent or stored. This is not a care plan or recommendation.”
- **Assessment edit:** “Edit my answers”
- **Assessment reset:** “Start over”
- **Availability:** “Now accepting new client inquiries”
- **Response:** “Email is preferred. We aim to respond within 12 business hours, Monday-Friday, 9:00 a.m.-6:00 p.m. Eastern Time.”
- **Pilot label:** “Local pilot — forms do not send or store information”

### Writing rules

- Keep `h1` headings under approximately 12–15 words and button labels under five words where clarity permits.
- Start section headings with the visitor's need, not internal business terminology.
- Keep paragraphs to roughly three sentences and use bullets for genuine sets, not decorative fragments.
- Never publish “trusted,” “certified,” “licensed,” “insured,” “screened,” “available 24/7,” “affordable,” “best,” “experienced,” or similar claims without owner-supplied evidence and approved context.
- Do not imply medical advice, nursing, emergency monitoring, guaranteed continuity, guaranteed outcomes, or immediate response.
- Replace every pilot label only through an explicit content-verification review.

### Form and system messages

- **Privacy guidance:** “Share a general question only. Do not include health, medication, identification, financial, or emergency information.”
- **Error summary heading:** “Check the highlighted information.”
- **Local success:** “Preview complete. This local pilot did not send or store your information. No consultation has been requested.”
- **Contact detail note:** “Email is the preferred contact method.”
- **Non-emergency notice:** “This website is not monitored for emergencies. Seek appropriate local emergency assistance when immediate help is needed.”
- **Assessment privacy guidance:** “Keep your answers general. Do not include diagnoses, medication details, health-card numbers, financial information, a street address, or emergency information.”
- **Assessment no-JavaScript message:** “JavaScript is required to create a local summary. Nothing can be submitted from this page.”
- **Reset question:** “Clear your answers and start over?”

## 15. Visual Assets

### Pilot assets

- Text-only YYZ Caregivers wordmark.
- Small set of simple local SVG line motifs: home outline, open doorway, gentle connection arc, and neutral check/list shapes.
- Soft CSS background shapes or gradients using the approved pilot tokens.
- No photography is required to complete the pilot.
- The supplied logo and photographs remain candidate assets only. Do not place them in the design or source until ownership, model releases, intended representation, crop, quality, and alternative-text decisions are documented.

### Future photography direction

If genuine, properly licensed imagery is approved later, favour natural home settings, varied ages and abilities, mutual interaction, eye-level framing, and everyday dignity. Avoid hospital-like staging, pity, isolated hands, infantilizing scenes, exaggerated vulnerability, uniforms that imply unverified credentials, or images presented as actual staff/clients when they are not.

Every image requires documented source/rights, content-owner approval, appropriate crop guidance, dimensions, and alternative-text decision. Do not add fake portraits, testimonial headshots, accreditation seals, partner logos, star ratings, awards, or stock trust badges.

## 16. Design Tokens

```text
container-max:       1180px
measure-copy:        66ch
measure-policy:      72ch

breakpoint-tablet:   768px
breakpoint-nav:      960px
breakpoint-wide:     1280px

radius-small:        8px
radius-medium:       16px
radius-large:        28px
radius-pill:         999px (labels only, never long paragraphs)

border-default:      1px solid #C5D2CE
shadow-small:        0 2px 10px rgb(18 48 71 / 8%)
shadow-medium:       0 12px 30px rgb(18 48 71 / 12%)

focus-outline:       2px solid #005FCC
focus-offset:        3px

motion-fast:         120ms
motion-standard:     180ms
motion-ease:         cubic-bezier(.2, .8, .2, 1)
```

Colour, type, and spacing tokens are defined in Sections 8–10. Components must consume tokens rather than introducing one-off values. Shadows are optional hierarchy aids, not the only component boundary.

## 17. Motion and Animation

- Use 120–180ms transitions for button colour, link underline, menu disclosure, and FAQ indicator only.
- Do not animate page entry, scroll position, counters, card reveals, hero copy, or decorative parallax.
- The mobile menu opens in document flow with a short opacity/height transition only if it does not delay access or disrupt focus.
- The FAQ indicator may rotate, but answer content must remain understandable without animation.
- Loading feedback is reserved for a future real submission and must include text.
- Under `prefers-reduced-motion: reduce`, remove non-essential transitions and disable smooth scrolling.

## 18. Acceptance Criteria

Design is ready for Frontend Development when:

- All eight page layouts, section orders, calls to action, and mobile behaviours are documented.
- Navigation works conceptually with keyboard, touch, screen reader, JavaScript, and no JavaScript.
- Every reusable component has a purpose, responsive behavior, states, and accessibility expectations.
- Typography, spacing, colour, radius, shadow, breakpoint, focus, and motion tokens are implementation-ready.
- Both forms define field order, minimization, labels, required logic, errors, review/success states, clearing, and no-send messaging.
- The assessment specifies broad topic choices, a neutral temporary summary, edit/reset behaviour, no-JavaScript handling, and separate contact links that contain no answers.
- Privacy, non-emergency, pilot, success, warning, error, and empty states are distinct in text as well as colour.
- No layout depends on unapproved photography, logo, testimonial, credential, price, or service claim; verified contact details may be shown.
- Every page remains usable at 320 CSS pixels and with enlarged text.
- The approved Architecture sitemap and pilot boundaries remain unchanged.

The implemented pilot is ready for QA only when:

- Visual tokens are applied consistently with verified contrast.
- Header, navigation, footer, current-page states, page titles, and CTA wording are consistent across all routes.
- Keyboard focus order matches reading order and focus is always visible.
- Mobile menu, native FAQ controls, Contact demonstration form, and Support Needs Assessment behave as specified.
- Neither form sends a request or stores values. Contact clears data after local success; the assessment clears on confirmed reset, refresh, or navigation.
- The assessment produces no diagnosis, score, match, price, schedule, eligibility result, care recommendation, download, or implied submission.
- There are no broken links, horizontal overflow, fake contact actions, remote trackers/fonts, or fabricated trust signals.
- Reduced-motion and no-JavaScript fallbacks are confirmed.
- Placeholder/pilot notices remain visible until owner verification is complete.

## 19. Handoff to the Frontend Developer

Build eight static pages—Home, About, Services, Contact, Support Needs Assessment, FAQ, Privacy, and Terms—using semantic HTML, shared local CSS, and minimal progressive JavaScript. Implement the token system in CSS custom properties and reuse the documented header, navigation, hero/page-header, cards, process steps, notices, FAQ, forms, review summary, CTA band, and footer.

Development priorities:

1. Preserve content and focus order from mobile through desktop.
2. Keep navigation available without JavaScript; enhance it into the labeled mobile disclosure when JavaScript runs.
3. Implement the Contact form as a non-sending local demonstration with accessible validation, error summary, field messages, value clearing, and explicit success wording.
4. Implement `intake.html` as one continuous, non-sending Support Needs Assessment with the approved field groups, native inputs, accessible validation, temporary review summary, edit and inline-reset states, and contact links that never contain answers.
5. Add no network/storage API, diagnosis field, clinical score, care recommendation, eligibility or pricing logic, download, print-by-default, or third-party dependency.
6. Use local abstract assets only until the candidate logo/photo rights are confirmed. Do not create badges, testimonials, unsupported service claims, prices, or credentials.
7. Include visible pilot, privacy, non-emergency, non-clinical, and owner-verification notices where specified.
8. Use native `details`/`summary` for FAQ and avoid unnecessary custom widgets.
9. Verify contrast, keyboard behaviour, focus transitions, reflow, reduced motion, reset/data clearing, link integrity, and no external runtime requests before handoff.

Unconfirmed decisions that must remain visible: exact services and municipalities, organization story, logo/photo rights, qualifications/screening/insurance, pricing, actual capacity, production form handling, policies, domain control, and launch date. Confirmed defaults are the public phone/email, email preference, public/privacy contact, Eastern Time hours, 12-business-hour response expectation, private address, and “Now accepting new client inquiries.” The next required output is the implementation in `src/` with supporting instructions in `documentation/DEVELOPMENT.md`.
