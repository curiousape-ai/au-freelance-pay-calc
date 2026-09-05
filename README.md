# AU Freelancer Money Calculator

Day-rate, hourly-rate, employee salary and target take-home calculator for Australia. The default is FY2026–27, with FY2025–26 selectable.

Live: **https://au-freelance-pay-calc.netlify.app/**

## Included

- Day rate, annual contractor revenue, target weekly take-home, employee salary and hourly modes.
- FY2026–27 / FY2025–26 URL and local-storage state.
- GST inclusive/exclusive calculations, 220 default billable days and configurable hours per day.
- Deductions, Medicare, optional HELP/HECS, contractor super set-aside and employee super on top.
- 23 day-rate, 11 employee-salary and 16 hourly-rate preset pages, plus preset index, methodology and custom 404.
- Netlify Forms tips-list capture and Plausible events: `calc_change`, `mode_change`, `print`, `lead_submit`.

## Formula sources and disclaimer

Rates live in `scripts/cfg.json`, the single source used by the Python and JavaScript engines. Last checked: 2026-09-05.

| Item | FY2025–26 | FY2026–27 | Source |
|---|---|---|---|
| Resident brackets | 0 / 16% / 30% / 37% / 45% | 0 / 15% / 30% / 37% / 45% | [ATO resident rates](https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/individual-income-tax-rates) |
| Medicare levy | 2%; single shade $28,011–$35,013 | Same pair retained because a separate 2026–27 pair is not yet published | [ATO Medicare reduction](https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners) |
| HELP marginal thresholds | $67,000 / $125,000 | $69,528 / $129,717 | [ATO study-loan rates](https://www.ato.gov.au/tax-rates-and-codes/study-and-training-support-loans-rates-and-repayment-thresholds) |
| GST | 10% | 10% | [ATO GST](https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst) |
| Super | 12% | 12% | SG-equivalent planning amount |

Estimate only, not tax, financial or legal advice. MLS, tax offsets, family/SAPTO thresholds and company/PSI structures are excluded.

## Development

```bash
python3 scripts/check_parity.py
python3 scripts/generate_site.py
```

Never edit `public/` by hand; it is generated. The generator runs the parity gate and fails when `default_fy` is stale after the following 1 July.

## Deploying

Netlify reads the root `netlify.toml`:

- build command: `python3 scripts/generate_site.py`
- publish directory: `public`
- deploy previews: enable for pull requests in Netlify
- production: merge an approved preview PR to `main`; Netlify then auto-deploys

The site is linked locally as Netlify site `92289150-c169-4786-b2a4-1fbff973a560`. Confirm the GitHub repository link and Deploy Preview setting in the Netlify dashboard. Do not use manual `netlify deploy --prod` as the normal release path.

Before go-live or domain cutover, verify Plausible receives a real event from the deploy preview and production. Submit the regenerated sitemap to Search Console only after that check.
