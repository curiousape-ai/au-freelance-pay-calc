# AU Freelancer Money Calculator

Weekend wedge: day-rate ↔ annual ↔ estimated AU contractor take-home (FY2025–26).

## Live URL

**https://au-freelancer-calc-e23a.surge.sh/**

- Works in any browser, no login.
- HTTPS via Surge.
- **SEO caveat:** `*.surge.sh` subdomains force `robots.txt` → `Disallow: /`, so Google will not index this host. Sitemap + unique titles/H1s are ready; Ian must point a **custom domain** at Surge (or redeploy to Netlify/Cloudflare Pages) for GSC indexing.

Backup/local build: `/workspace/au-freelancer-calc/public/`

## What’s included

- Single-page calculator (vanilla HTML/CSS/JS)
  - Modes: day rate or annual income
  - GST inclusive / exclusive toggle (10%)
  - Billable days/year (default **220**)
  - Outputs: annual/weekly/day equivalents, GST component, income tax, Medicare levy, estimated take-home
  - Super note (not deducted from take-home)
- **34 SEO variant pages** + home = **35 URLs** in `sitemap.xml`
  - Day rates **$400–$1500** step **$50** (23 pages), e.g. `/800-day-rate/`
  - Salary presets (11): `/60000-salary-after-tax/` … `/200000-salary-after-tax/`
- `robots.txt`, `sitemap.xml`, Open Graph + canonical tags on every page
- Email capture form (Formspree placeholder + Netlify Forms attributes ready)

## Formula sources / disclaimer

Hardcoded in `public/config.js` (also embedded in each HTML page). **Last checked: 2026-08-22.**

| Item | Value | Source |
|------|-------|--------|
| Resident tax brackets FY2025–26 | 0 / 16% / 30% / 37% / 45% with ATO cumulative bases | [ATO resident tax rates](https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/) |
| Medicare levy | 2%, with single low-income shade (lower $28,011 / upper $35,013) | [ATO Medicare levy reduction](https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners) |
| GST | 10% | [ATO GST](https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst) |

**Assumptions (estimate only, not advice):** taxable income ≈ GST-exclusive revenue; no deductions, HELP/HECS, MLS, offsets, or private health surcharge; super not deducted.

## Email capture status

- Form is on every page (name optional, email required).
- Wired for **Formspree**: `https://formspree.io/f/YOUR_FORM_ID` — placeholder until Ian swaps the ID in `public/config.js` (and regenerates, or search-replace `YOUR_FORM_ID` across `public/`).
- Also has `data-netlify="true"` for **Netlify Forms** if redeployed to Netlify.
- Could not complete Formspree/Web3Forms/Basin signup without Ian’s email inbox for verification.
- On Surge, submissions will show an in-UI message until Formspree ID is set.

### Swap Formspree (2 minutes)

1. Create a form at https://formspree.io (free).
2. Copy the form ID (e.g. `xpwabcdz`).
3. Replace `YOUR_FORM_ID` in `public/config.js` and all HTML `action=` / embedded config (or edit `scripts/generate_site.py` → `formspree_endpoint` and re-run generator).
4. Redeploy: `npx surge /workspace/au-freelancer-calc/public au-freelancer-calc-e23a.surge.sh --token <token>` (token in `.surge-credentials.json` on the box).

## Regenerate site

```bash
python3 /workspace/au-freelancer-calc/scripts/generate_site.py
# then patch live base URL + redeploy
```

## Deploy notes

| Host | Status |
|------|--------|
| Surge `au-freelancer-calc-e23a.surge.sh` | **LIVE** (permanent free subdomain). Robots locked to Disallow on `*.surge.sh`. |
| Netlify `--allow-anonymous` | Blocked: daily anonymous deploy limit on this environment. |
| Tiiny Host | Needs verified email / API key (Solo+ for API). |

Credentials for Surge redeploy (box only): `/workspace/au-freelancer-calc/.surge-credentials.json`

## GSC next steps for Ian (minimal)

1. Prefer a custom domain (or Netlify/Cloudflare Pages) so `robots.txt` allows indexing.
2. [Google Search Console](https://search.google.com/search-console) → **Add property** → URL prefix = live site root.
3. Verify (DNS TXT, HTML file, or meta tag — GSC shows options).
4. **Sitemaps** → submit `https://YOUR-DOMAIN/sitemap.xml`.
5. Spot-check a few variant URLs (e.g. `/800-day-rate/`, `/80000-salary-after-tax/`) with URL Inspection.

Do **not** use the Surge `*.surge.sh` URL for GSC — crawlers are blocked by Surge’s forced robots.txt.

## Paths on box

```
/workspace/au-freelancer-calc/
  README.md
  scripts/generate_site.py
  public/                 # deploy root
    index.html
    calc.js app.js styles.css config.js
    robots.txt sitemap.xml
    netlify.toml
    400-day-rate/ … 1500-day-rate/
    60000-salary-after-tax/ … 200000-salary-after-tax/
  variant-count.json
  .surge-credentials.json
```
