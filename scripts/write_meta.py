from datetime import date
from pathlib import Path
import html,json,os,sys
sys.path.insert(0,str(Path(__file__).resolve().parent));import taxlib as T
ROOT=Path(__file__).resolve().parent.parent;PUB=ROOT/"public";cfg=T.CONFIG;fy=cfg["default_fy"];yc=cfg["years"][fy];host=os.environ.get("SITE_BASE_URL",cfg["base_url"]).rstrip("/");today=date.today().isoformat()
urls=["/","/presets/","/how-it-works/"]+[f"/{r}-day-rate/" for r in T.PRESET_DAY_RATES]+[f"/{s}-salary-after-tax/" for s in T.PRESET_SALARIES]+[f"/{h}-hourly-rate/" for h in T.PRESET_HOURLY_RATES]
PUB.joinpath("robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {host}/sitemap.xml\n")
entries="\n".join(f"  <url><loc>{host}{u}</loc><lastmod>{today}</lastmod><changefreq>monthly</changefreq><priority>{'1.0' if u=='/' else '0.8'}</priority></url>" for u in urls)
PUB.joinpath("sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries}\n</urlset>\n')
day_lines="\n".join(f"- [${r:,}/day]({host}/{r}-day-rate/)" for r in T.PRESET_DAY_RATES);sal_lines="\n".join(f"- [${s:,} salary]({host}/{s}-salary-after-tax/)" for s in T.PRESET_SALARIES);hour_lines="\n".join(f"- [${h:,}/hour]({host}/{h}-hourly-rate/)" for h in T.PRESET_HOURLY_RATES)
PUB.joinpath("llms.txt").write_text(f"""# AU Freelancer Calc
> Australian contractor and employee take-home calculator for FY{fy}.

Disclaimer: Estimate only, not tax, financial or legal advice. Uses Australian resident FY{fy} brackets, 10% GST, 2% Medicare with single low-income thresholds, optional HELP repayments and 220 billable days by default.

## Methodology
Contractor taxable income is GST-exclusive revenue minus entered deductions. Income tax is calculated progressively, then Medicare and any selected HELP repayment are subtracted. Day-rate annual revenue is the rate multiplied by billable days. Hourly revenue also multiplies by hours per day. Employee salary excludes GST and employer super is shown on top. The reverse solver uses bisection to find the ex-GST day rate that reaches a target weekly take-home.

## Start here
- [Calculator]({host}/)
- [How it works]({host}/how-it-works/)
- [All presets]({host}/presets/)

## Day rates
{day_lines}

## Employee salaries
{sal_lines}

## Hourly rates
{hour_lines}
""")

def shell(title,h1,body,desc,path,robots=None):
  url=html.escape(host+path); meta_desc=html.escape(desc)
  robot_tag=f'<meta name="robots" content="{html.escape(robots)}">' if robots else ""
  canon="" if robots and "noindex" in robots else f'<link rel="canonical" href="{url}">'
  return f'''<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><meta name="description" content="{meta_desc}">{robot_tag}{canon}<link rel="stylesheet" href="/styles.css"><link rel="icon" href="/favicon.svg"></head><body><main class="wrap content-page"><header class="hero"><div><div class="badge">FY{fy} · Estimate only</div><h1>{html.escape(h1)}</h1></div><a class="ghost" href="/">Calculator</a></header>{body}<footer><a href="/">Calculator</a> · <a href="/presets/">All presets</a> · <a href="/how-it-works/">How it works</a></footer></main></body></html>'''

def preset_rows(items,mode,path,label):
  return "".join(f'<tr><td><a href="{path.format(v=v)}">{label(v)}</a></td><td>{T.fmt_aud(T.calculate(mode,v,fy=fy)["takeHome"])}</td></tr>' for v in items)
rows=preset_rows(T.PRESET_DAY_RATES,"day","/{v}-day-rate/",lambda v:f"${v:,}/day")+preset_rows(T.PRESET_SALARIES,"employee","/{v}-salary-after-tax/",lambda v:f"${v:,} salary")+preset_rows(T.PRESET_HOURLY_RATES,"hourly","/{v}-hourly-rate/",lambda v:f"${v:,}/hour")
(PUB/"presets").mkdir(exist_ok=True);(PUB/"presets"/"index.html").write_text(shell(f"All AU contractor rate presets — take-home FY{fy} (Australia)","All calculator presets",f'<section class="card"><table class="baked"><thead><tr><th>Preset</th><th>Estimated take-home</th></tr></thead><tbody>{rows}</tbody></table></section>',f"Browse every baked Australian contractor day-rate, hourly-rate and employee-salary preset with FY{fy} take-home estimates.","/presets/"))
method=f'''<section class="card"><h2>Billable-day arithmetic</h2><p>The default is 220 billable days: roughly 260 weekdays minus annual leave, public holidays, sick days and non-billable time. Change it to match your workload.</p><h2>Taxable income and GST</h2><p>For contractors, taxable income is GST-exclusive revenue minus entered deductions. GST collected is not treated as income because it is remitted through BAS.</p><h2>Tax, Medicare and HELP</h2><p>Resident income tax uses FY{fy} progressive brackets. Medicare uses the 2% single-person calculation and low-income shade. HELP is optional and uses the FY{fy} marginal repayment thresholds.</p><h2>Reverse solver</h2><p>The target mode repeatedly tests an ex-GST day rate until its estimated weekly take-home matches the target. It uses the same tax calculation as the forward modes.</p><h2>Exclusions</h2><p>Medicare levy surcharge, tax offsets, family and SAPTO thresholds, company and PSI structures are excluded. This is an estimate, not advice.</p></section>'''
(PUB/"how-it-works").mkdir(exist_ok=True);(PUB/"how-it-works"/"index.html").write_text(shell(f"How AU Freelancer Calc estimates take-home — FY{fy} (Australia)","How this calculator works",method,f"How AU Freelancer Calc turns a day rate into GST, resident tax, Medicare and estimated FY{fy} take-home. Estimate only, not advice.","/how-it-works/"))
PUB.joinpath("404.html").write_text(shell("Page not found — AU Freelancer Calc (Australia)","That rate isn't a preset yet",'<section class="card"><p>Try the <a href="/">full calculator</a> for any rate, or browse the <a href="/presets/">preset index</a>.</p></section>',"That rate is not a baked preset. Use the full Australian contractor calculator or browse take-home presets.","/404.html","noindex, nofollow"))
ROOT.joinpath("variant-count.json").write_text(json.dumps({"day_rates":T.PRESET_DAY_RATES,"salaries":T.PRESET_SALARIES,"hourly_rates":T.PRESET_HOURLY_RATES,"variant_pages":len(urls)-3,"total_urls_in_sitemap":len(urls)},indent=2))
print("meta written",len(urls),"urls")
