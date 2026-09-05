# AU Freelancer Calc — implementation plan
**Date:** 2026-09-05 · **Source review:** `2026-09-05-codex-sol-review.md` plus the Fable review of the same day · **Live:** https://au-freelance-pay-calc.netlify.app/ · **Repo:** curiousape-ai/au-freelance-pay-calc

## Verdict from the review

Engine correct (parity 208 cases, 0 mismatches). Site live, crawl unblocked, Netlify Forms capturing (1 submission, looks like a test). The three risks worth fixing before any traffic arrives are: the rates are a financial year stale, the headline number is buried on mobile, and the lead form promises a cheat-sheet that is never sent.

## Working rules for every phase

- Branch per phase (`feat/`, `fix/`, `chore/`), PR, Netlify Deploy Preview, Ian merges. Never push to main.
- Every change to `scripts/cfg.json`, `scripts/embedded/calc.js`, or `scripts/taxlib.py` must keep `python3 scripts/check_parity.py` at 0 mismatches. Extend the parity cases whenever a new tax input is added.
- Regenerate with `python3 scripts/generate_site.py` before every deploy. Never hand-edit `public/`.
- Done means: parity green, generator green, preview checked on a phone, live URL spot-checked after merge.

---

## Phase 0 — Wrong-number and broken-promise fixes (do first, ~1 day)

### 0.1 Bring rates to FY2026-27 and keep FY2025-26 selectable
**Why:** FY2026-27 began 1 July 2026. The 16% bracket was legislated to fall to 15% from 1 July 2026. Every figure on the site is for the previous year.

Tasks
1. Restructure `scripts/cfg.json` from a flat rate set to `{"default_fy": "2026-27", "years": {"2025-26": {...}, "2026-27": {...}}}`. Keep `gst_rate`, `sg_rate`, `default_days`, `sources`, site fields at top level.
2. Enter the 2026-27 set. Expected values to **verify against the ATO resident rates page before committing**:

   | Bracket | Rate | Base at lower edge |
   |---|---|---|
   | 0 to 18,200 | 0% | 0 |
   | 18,201 to 45,000 | 15% | 0 |
   | 45,001 to 135,000 | 30% | 4,020 |
   | 135,001 to 190,000 | 37% | 31,020 |
   | 190,001 and over | 45% | 51,370 |

   Medicare low-income thresholds index each year. Look up the 2026-27 single thresholds; if the ATO has not published them, keep the 2025-26 pair and say so in the sources line.
3. `taxlib.py` and `calc.js`: read the bracket set for the selected year. Add a `fy` argument to `calculate` in both engines. Default to `cfg.default_fy`.
4. `check_parity.py` and `calc_runner.js`: run the whole case matrix for both years.
5. UI: add a two-button segment "FY2026-27 / FY2025-26" next to the GST segment. Persist in URL state (`&fy=`) and localStorage. Baked pages default to the current year.
6. Generator: bake all titles, badges, answers, FAQ and JSON-LD with the default year. Add a `last_checked` date per year.
7. Generator guard: fail the build if today is after 1 July of the year following `default_fy` (so 2026-27 fails after 1 July 2027). Print the ATO source URL in the error.
8. Update `README.md` formula table and the `llms.txt` disclaimer line.

Acceptance
- `/800-day-rate/` shows FY2026-27 and the take-home changes from $126,022 to the recomputed figure. Toggle to 2025-26 restores $126,022.
- Parity passes for both years.
- Generator fails with a clear message if `default_fy` is set to `2024-25`.

### 0.2 Move the headline number to the top of results
**Why:** take-home is the thirteenth card. On a phone the reader scrolls past twelve stats first.

Tasks
1. In `scripts/page_template.html` and the home template path, reorder the results grid: solved-day-rate card (target mode only), then take-home per year with weekly, then day rate ex and inc, then annual ex and inc, then income tax, Medicare, effective rate, GST per year, weekly gross, super set-aside, take-home after super.
2. Add a "What goes into this" collapsed `<details>` under the take-home card holding the exclusions hint text, so the number itself is not surrounded by caveats.
3. Add `aria-live="polite"` on the results grid container.

Acceptance
- On a 390px viewport the take-home figure is visible without scrolling past the inputs card.

### 0.3 Make the lead form keep its promise
**Why:** "Send me the cheat-sheet" captures an email and sends nothing.

Decision needed from Ian: (a) deliver a real cheat-sheet, or (b) relabel as a tips list.

Option (a) tasks
1. Build a one-page PDF cheat-sheet from the generator (reuse the print CSS via a headless Chromium step, or a Pillow render like `make_og_image.py`). Contents: FY brackets, Medicare, GST rule of thumb, 220-day arithmetic, day-rate to annual table for $400 to $1,500.
2. Host it at `/cheat-sheet.pdf` and add a Netlify Forms email notification that includes the link. Netlify notifications are dashboard config, not code. Record the setting in README.
3. Show the download link in the success message too, so delivery does not depend on email.

Option (b) tasks
1. Relabel button to "Send me occasional AU contractor tips" and the heading to match.
2. Point people at the existing "Print / save PDF" button for the cheat-sheet.

Either option
- Replace the failure copy that mentions Formspree with "Could not submit. Please try again in a minute."
- Remove the Formspree branch from `app.js` and the `formspree_endpoint` and `_subject` fields unless Formspree is actually going to be used. One path is easier to trust.

### 0.4 Disable the GST toggle in target mode
Target mode always solves ex-GST. Grey out the GST segment with `aria-disabled` when mode is `target`, and say "solved ex GST" in the solved card. One small change in `app.js`.

---

## Phase 1 — Hardening and deploy hygiene (~half a day)

### 1.1 Reproducible deploys from GitHub
1. Link the GitHub repo to the Netlify site. Build command `python3 scripts/generate_site.py`, publish `public`. Netlify build images ship Python 3 and Node, both of which the parity gate needs; pin with `PYTHON_VERSION` in `netlify.toml` if needed.
2. Move `netlify.toml` to the repo root (Netlify reads it from the base directory, not the publish directory). Keep headers in one place: root `netlify.toml`. Delete `public/_headers` and `scripts/embedded/_headers`.
3. Enable Deploy Previews for PRs. Add a `DEPLOYING.md` section to README replacing the manual `netlify deploy --prod` instruction.
4. Delete `public/CNAME` (Surge leftover, served publicly). Remove the Surge mirror from README or mark it deprecated.

### 1.2 Content-Security-Policy
Prerequisites: no inline script, no inline styles.
1. Generator emits config into `public/config.js` (file already exists but is unused) and the template loads `<script src="/config.js">` before `calc.js`. Drop the inline `window.AU_CALC_CONFIG` block.
2. Move the fourteen inline `style=""` attributes in the templates to classes in `styles.css`. Print CSS already exists for the rest.
3. Add headers in `netlify.toml`:
   ```
   Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'
   Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
   ```
   Keep `X-Frame-Options: DENY` unless Phase 3 embeds the calculator elsewhere.
4. Test on the Deploy Preview: open DevTools console, confirm no CSP violations across home, a day-rate page, a salary page, print view, and a form submit.

### 1.3 Custom 404
Add `public/404.html` from a small template: "That rate isn't a preset yet", the full calculator link, and the preset index from 2.4. Netlify serves it automatically.

### 1.4 Accessibility fixes
1. Segmented buttons: add `aria-pressed="true|false"` toggled in `setMode` and `setGst`.
2. The bare `<label>Super set-aside</label>` becomes a `<p class="label">`.
3. Confirm focus ring is visible on the dark background for buttons as well as inputs.

### 1.5 Stale baked prose on home
When restored or query inputs differ from the baked preset on the home page, hide `table.baked` and swap the "Quick answer" heading to "Your estimate", regenerating the sentence from `calculate()` client-side. Small `app.js` addition, no generator change.

---

## Phase 2 — SEO and GEO (~1 day, after Phase 0 so the year is right)

### 2.1 Titles, H1s, and year
1. Home H1: "Contractor day rate calculator (Australia, FY2026-27)". Title: "Day Rate Calculator Australia — Contractor Take-Home FY2026-27".
2. Variant titles keep the amount first and add the year: "$800/day contractor calculator — take-home FY2026-27 (Australia)".
3. Salary pages: rename to intent-honest titles until PAYG mode ships (Phase 3), e.g. "$80,000 contractor revenue after tax (Australia, FY2026-27)". Keep slugs so nothing 404s.

### 2.2 Authorship and entity schema
1. Add an "About this calculator" section: who built it, where, why, and the maintenance promise ("rates re-checked every July and after each budget"). One paragraph.
2. JSON-LD: add `Person` (Ian) and `Organization` (Curious Ape or Ape Labs, Ian's call) with `sameAs` to the public profiles, and set `author` and `publisher` on the `WebApplication` node. Add `dateModified` from the generator run date.
3. Add `Last updated` visibly next to "Rates last checked".

### 2.3 Sitemap and llms.txt
1. Emit `<lastmod>` per URL in `sitemap.xml` using the generator run date.
2. Add a `## Methodology` block to `llms.txt` with the formula in words and the current FY.

### 2.4 Preset index page
Create `/presets/` listing every day-rate and salary page as a two-column HTML table with the baked take-home next to each link. Replace the homepage "Full sitemap" link with this page. Add it to the sitemap.

### 2.5 Methodology page
Create `/how-it-works/`: the 220-day arithmetic (260 weekdays minus leave, public holidays, sick days), why taxable income is ex-GST revenue, what is excluded and why, how the reverse solver works. Written as short declarative paragraphs with the numbers stated, which is what AI engines lift. Link from every page footer.

### 2.6 Domain decision (Ian)
Before Search Console: keep the Netlify subdomain, buy a dedicated .com.au, or proxy under an existing property via Netlify redirects. Recommendation: dedicated domain only if this becomes a product; otherwise a subfolder of the strongest existing domain. Once decided, update `base_url` in cfg, regenerate, redeploy, then submit the sitemap.

---

## Phase 3 — Product depth (~2 days, sequenced by demand)

### 3.1 PAYG employee mode
1. Add mode `employee` to both engines: taxable = salary minus deductions, no GST split, super shown as employer SG on top at 12%, not a set-aside.
2. UI: mode segment gains "Employee salary". GST segment disabled in this mode.
3. Salary pages switch preset to employee mode and gain a comparison table: "$80,000 salary is equivalent to a $X/day contractor rate at 220 days" solving for the day rate that yields the same take-home. This is the differentiated page nobody ranks for.
4. Retitle salary pages to "$80,000 a year after tax (Australia, FY2026-27) and the contractor day-rate equivalent".
5. Parity cases for employee mode across bracket edges.

### 3.2 HELP/HECS repayment toggle
1. Add per-year HELP config: threshold and marginal rates. For 2025-26 the legislated marginal system is expected to be a $67,000 threshold, 15% on income between $67,000 and $125,000, then 17% above $125,000. **Verify on the ATO study loan repayment page before entering; confirm the 2026-27 indexation.**
2. Checkbox "I have a HELP/HECS debt". Repayment shown as its own card and subtracted from take-home.
3. Remove "HELP not modelled" from all baked copy via the generator once live. Parity cases at each HELP threshold.

### 3.3 GST registration hint
When annual ex-GST revenue is under $75,000, show under the GST segment: "Under $75k turnover, GST registration is optional. If you are not registered, use GST exclusive and ignore the GST cards." No engine change.

### 3.4 Hourly rate mode and pages
Mode `hourly` with an hours-per-day input defaulting to 8. Generate `/{rate}-hourly-rate/` for $50 to $200 in $10 steps. Add to sitemap, presets index, llms.txt.

---

## Phase 4 — Measurement (before Phase 2 goes live)

- Add Plausible (workspace default) to the template before submitting to Search Console. Custom events: `calc_change`, `mode_change`, `print`, `lead_submit`. Confirm a real event fires on the Deploy Preview before merge.
- Watch Netlify Forms submission count monthly against the free-tier cap; enable reCAPTCHA only if spam appears.

---

## Sequence and estimates

| Order | Phase | Effort | Blocks |
|---|---|---|---|
| 1 | 0.1 rates FY2026-27 | 3 h | everything else that bakes copy |
| 2 | 0.2, 0.4 results order, target-mode toggle | 1 h | |
| 3 | 0.3 lead form promise | 1 to 3 h | Ian picks option (a) or (b) |
| 4 | 1.1 GitHub-linked deploys | 1 h | all later PRs use previews |
| 5 | 1.2 CSP | 2 h | |
| 6 | 1.3 to 1.5 404, a11y, stale prose | 1.5 h | |
| 7 | 4 analytics | 0.5 h | must precede Search Console |
| 8 | 2.1 to 2.5 SEO/GEO | 5 h | 0.1 done |
| 9 | 2.6 domain | Ian decision | Search Console submission |
| 10 | 3.1 PAYG mode | 5 h | salary page retitle |
| 11 | 3.2 HELP | 3 h | ATO figures verified |
| 12 | 3.3, 3.4 GST hint, hourly | 3 h | |

## Decisions needed from Ian

1. Lead form: real cheat-sheet PDF (a) or tips-list relabel (b).
2. Entity for authorship schema: Curious Ape or Ape Labs.
3. Domain: Netlify subdomain, dedicated .com.au, or subfolder of an existing property.

## Out of scope for now

Company and PSI structures, Medicare levy surcharge, family and SAPTO Medicare thresholds, tax offsets, non-resident rates. Each is a documented exclusion in the copy and stays that way until a reader asks for it.
