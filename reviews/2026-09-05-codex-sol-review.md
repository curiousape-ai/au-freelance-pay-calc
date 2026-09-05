# AU Freelancer Calc — Codex Sol–bar review
**Live:** https://au-freelancer-calc-e23a.surge.sh/  
**Source:** `/workspace/au-freelancer-calc/` (live `calc.js` == local)  
**Reviewer:** Code Review (Codex Sol–equivalent pass) · 2026-09-05 · no code changes

## Verdict
**No correctness ship-blocker on tax/GST math.** Resident FY2025–26 brackets + single Medicare shade match ATO. Variant SEO pages match `calc.js`/`taxlib.py` (34/34).

**Experiment / growth ship-blockers remain:** Surge-forced `robots.txt` Disallow, Formspree still `YOUR_FORM_ID`. Calculator can stay live as an estimate wedge; do not treat Surge URL as an SEO bet until custom domain / non-Surge host.

---

## Ship-blockers

1. **SEO dead on current host** — Live `robots.txt` is `User-agent: *` / `Disallow: /` (Surge `*.surge.sh` override). Local `public/robots.txt` says `Allow: /` but is irrelevant on this host. Sitemap + variants are wasted for Google until custom domain or Netlify/CF Pages.

2. **Lead form non-functional on Surge** — `formspree_endpoint` / form `action` still `https://formspree.io/f/YOUR_FORM_ID`. `app.js` detects placeholder and POSTs to `/` (Netlify Forms path); on Surge that fails. Growth loop broken until Formspree ID or host with working forms.

*(Neither is a tax-math defect. Both block the experiment’s acquisition goals.)*

---

## Spot-checks (GST exclusive, 220 days unless noted)

Verified vs ATO resident rates 2025–26 + single Medicare thresholds $28,011 / $35,013; shade `(taxable − lower) × 10%` capped at 2%.

| Case | Taxable | Income tax | Medicare | Take-home |
|------|---------|------------|----------|-----------|
| $800/day ex | $176,000 | $46,458 | $3,520 | $126,022 |
| $1,200/day ex | $264,000 | $84,938 | $5,280 | $173,782 |
| $800/day **inc** GST | $160,000 | $40,538 | $3,200 | $116,262 |
| $80k annual ex | $80,000 | $14,788 | $1,600 | $63,612 |
| $150k annual ex | $150,000 | $36,838 | $3,000 | $110,162 |

Bracket bases: $4,288 / $31,288 / $51,638 — match ATO table.  
ATO shade example (Angie $29k → $98.90): `(29000−28011)×0.10 = 98.90` — match.

GST split: inclusive → `amount/1.1`; exclusive → `×1.1`. Taxable = GST-exclusive annual — correct contractor remit assumption.

---

## Risks (not immediate ship-stop for a labelled estimate)

1. **Model scope vs “salary after tax” URLs** — Pages like `/80000-salary-after-tax/` still run the contractor model (GST toggle, taxable ≈ GST-ex revenue, no PAYG withholding nuances). Easy to read as employee take-home. Disclaimer helps; slug/title still over-promise vs engine.

2. **`incomeTax()` ignores `CFG.brackets`** — Rates hardcoded in `calc.js` / `taxlib.py` while `config.js` also carries brackets. Currently consistent; future FY update can desync if only one side changes.

3. **Intentionally omitted (documented):** deductions, HELP/HECS, MLS, offsets, family Medicare thresholds, SAPTO, company/PSI structures. Fine for estimate; misleading if marketed as “your real take-home.”

4. **Ops secret hygiene (not public leak):** `.surge-credentials.json` sits next to the project on the box (email/password/token). **Not** under `public/` — good. Keep it out of any future git remote / zip share. No API secrets in public HTML.

5. **Regen drift:** local generated HTML still had `SITE_URL_PLACEHOLDER` in older tree; live pages are patched. Blind re-run of generator without URL patch can regress canonicals/sitemap.

---

## Disclaimer / advice risk
**OK.** Visible “Estimate only”, badge, take-home hint lists exclusions, footer disclaimer: not tax/financial/legal advice; confirm with ATO/agent. Does not claim official ATO calculator status. No overclaim found that would be a legal ship-blocker for a free estimate tool.

---

## Variant integrity
All 34 preset pages: `data-preset-*` + embedded FAQ/prose figures match `taxlib.calculate` (tax, Medicare, annual ex, take-home). Live `/800-day-rate/` and salary presets serve; placeholders cleared on live.

---

## Optional fixes (nits / next Zeus pass — do not block leave-up)
- Swap Formspree ID; or hide form until wired.
- Point custom domain (or redeploy host that allows crawl) before GSC.
- Drive `incomeTax` from `CFG.brackets` only.
- Rename salary presets to “annual income” / “contractor revenue” language.
- Add one-line note: family/SAPTO Medicare thresholds not modelled.
- Keep surge creds out of deploy root and any shared archive.

---

## Bottom line for Chief / Ian
**Math: ship.** **SEO + email capture on Surge: blocked for the experiment.** Leave calculator live; next build priority (#1 Modern award rates) is separate. No merge/redeploy from this review.
