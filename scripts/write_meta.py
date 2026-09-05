from pathlib import Path
import json, os
ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "public"
cfg = json.loads((ROOT / "scripts" / "cfg.json").read_text())
host = os.environ.get("SITE_BASE_URL", cfg["base_url"]).rstrip("/")
days = list(range(400, 1550, 50))
sals = [60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 150000, 180000, 200000]
urls = ["/"] + [f"/{r}-day-rate/" for r in days] + [f"/{s}-salary-after-tax/" for s in sals]

PUB.joinpath("robots.txt").write_text(
    f"""User-agent: *
Allow: /

# AI crawlers welcome (explicit allow; no Disallow)
# User-agent: GPTBot
# Allow: /
# User-agent: ClaudeBot
# Allow: /
# User-agent: Google-Extended
# Allow: /

Sitemap: {host}/sitemap.xml
""",
    encoding="utf-8",
)

def money(n):
    return f"${n:,.0f}"

llms_day = [400, 500, 600, 700, 750, 800, 850, 900, 1000, 1100, 1200, 1300, 1400, 1500]
llms_sal = sals
day_lines = "\n".join(f"- [{money(r)}/day]({host}/{r}-day-rate/)" for r in llms_day)
sal_lines = "\n".join(f"- [{money(s)} after tax]({host}/{s}-salary-after-tax/)" for s in llms_sal)
PUB.joinpath("llms.txt").write_text(
    f"""# AU Freelancer Calc
> Day rate to annual to take-home for Australian contractors (FY2025-26 estimate).

**Disclaimer:** Estimate only — not tax, financial, or legal advice. Uses ATO resident brackets for FY2025-26 (last checked 2026-08-22), GST 10%, Medicare levy 2% with single low-income shade $28,011-$35,013. Default 220 billable days. Taxable income is GST-exclusive revenue; no deductions, HELP/HECS, MLS, offsets, or super.

## Start here
- [Calculator home]({host}/)

## Popular day rates
{day_lines}

## Salary after tax (freelancer equivalent)
{sal_lines}

## Sources
- [ATO resident tax rates 2025-26](https://www.ato.gov.au/tax-rates-and-codes/tax-rates-australian-residents/)
- [ATO Medicare levy reduction](https://www.ato.gov.au/individuals-and-families/medicare-and-private-health-insurance/medicare-levy/medicare-levy-reduction/medicare-levy-reduction-for-low-income-earners)
- [ATO GST overview](https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst)
""",
    encoding="utf-8",
)

entries = []
for u in urls:
    prio = "1.0" if u == "/" else "0.8"
    loc = f"{host}{u}"
    entries.append(f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>{prio}</priority>\n  </url>")
PUB.joinpath("sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "\n".join(entries)
    + "\n</urlset>\n",
    encoding="utf-8",
)
ROOT.joinpath("variant-count.json").write_text(
    json.dumps({"day_rates": days, "salaries": sals, "variant_pages": len(days)+len(sals), "total_urls_in_sitemap": len(urls)}, indent=2),
    encoding="utf-8",
)
print("meta written", len(urls), "urls")
