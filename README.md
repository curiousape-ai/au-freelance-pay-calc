# AU Freelancer Money Calculator

Weekend wedge: day-rate ↔ annual ↔ estimated AU contractor take-home (FY2025–26).

## Live URL

**https://au-freelance-pay-calc.netlify.app/**

- Netlify: robots.txt `Allow: /` (SEO unblocked), Netlify Forms capturing the lead form.
- Legacy Surge mirror: https://au-freelancer-calc-e23a.surge.sh/ (robots locked to Disallow on `*.surge.sh` — do not use for SEO/GSC).

## What’s included

- Single-page calculator (vanilla HTML/CSS/JS)
  - Modes: day rate, annual revenue, **target take-home** (reverse-solves the day rate)
  - GST inclusive / exclusive toggle (10%), billable days (default **220**)
  - Optional **deductions** input (reduces taxable income)
  - **Super set-aside** cards (12% SG-equivalent, informational — not deducted)
  - Outputs: annual/weekly/day equivalents, GST component, income tax, Medicare levy, take-home, take-home after super
  - **Shareable URL state** (`?mode=&amount=&days=&gst=&ded=`) + home-page session restore (localStorage)
  - Print / save-PDF cheat-sheet view
- **34 SEO variant pages** + home = **35 URLs** in `sitemap.xml`, each with baked neighbour comparison tables
- `robots.txt`, `sitemap.xml`, `llms.txt`, og:image, favicon, FAQ/Breadcrumb/WebApplication JSON-LD
- Email capture form — **live via Netlify Forms** (form name `lead`; dashboard → Forms)

## Formula sources / disclaimer

Rates live in `scripts/cfg.json` (single source of truth — drives `config.js`, `calc.js` and `taxlib.py`). **Last checked: 2026-08-22.**

| Item | Value | Source |
|------|-------|--------|
| Resident tax brackets FY2025–26 | 0 / 16% / 30% / 37% / 45% with ATO cumulative bases | [ATO resident tax rates](https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/) |
| Medicare levy | 2%, single low-income shade $28,011 / $35,013 | [ATO Medicare levy reduction](https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners) |
| GST | 10% | [ATO GST](https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst) |
| Super set-aside (informational) | 12% SG-equivalent | — |

**Assumptions (estimate only, not advice):** taxable income ≈ GST-exclusive revenue minus deductions; no HELP/HECS, MLS, offsets, family/SAPTO Medicare thresholds, or company/PSI structures; super shown separately, not deducted.

## Regenerate + deploy

```bash
python3 scripts/generate_site.py          # parity pre-flight, then bakes public/
netlify deploy --prod --dir=public        # repo is linked to the au-freelance-pay-calc site
```

- `generate_site.py --base-url https://…` overrides canonical/sitemap origin; the build **fails** if `SITE_URL_PLACEHOLDER` survives into `public/`.
- `scripts/check_parity.py` (auto-run pre-flight): JS engine vs Python engine over 208 cases — brackets, Medicare shade edges, GST modes, deductions, reverse-solver targets.
- Keep the form `action="/"` (same-origin) — an external `action` silently defeats Netlify form detection. JS reroutes to Formspree if a real ID is ever set in `cfg.json`.

## GSC next steps for Ian

1. [Google Search Console](https://search.google.com/search-console) → add property `https://au-freelance-pay-calc.netlify.app/`, verify.
2. Sitemaps → submit `/sitemap.xml` (35 URLs).
3. Spot-check `/800-day-rate/` and `/80000-salary-after-tax/` with URL Inspection.
4. Optional: custom domain later; update `cfg.json base_url` + regen + redeploy.

## Paths

```
scripts/
  cfg.json           # rates + site config (single source of truth)
  generate_site.py   # orchestrator: parity pre-flight → bake → placeholder guard
  make_specs.py / write_page.py / write_meta.py
  taxlib.py          # Python engine (+ preset lists)
  embedded/          # calc.js, app.js, styles.css, favicon.svg, og.png, _headers
  check_parity.py + calc_runner.js
  make_og_image.py   # regenerate og.png (PIL)
public/              # deploy root (generated)
```
