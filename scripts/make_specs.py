import json
from pathlib import Path
PUB = Path("/workspace/au-freelancer-calc/public")
OUT = Path("/tmp/pages")
OUT.mkdir(exist_ok=True)
rates = list(range(400, 1550, 50))
sals = [60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 150000, 180000, 200000]

def money(n):
    return f"${n:,.0f}"

specs = []
specs.append({
    "mode": "day", "amount": 800, "path": "/", "example": True,
    "outfile": str(PUB / "index.html"),
    "title": "AU Freelancer Calculator — Day Rate to Take-Home (FY2025-26)",
    "h1": "AU freelancer money calculator",
    "desc": "Convert AU contractor day rate to annual income with GST in/ex and estimated take-home using ATO FY2025-26 tax brackets and Medicare levy.",
    "intro": "Free Australian freelancer calculator: convert day rate to annual, GST in/ex, and estimate contractor take-home using FY2025-26 ATO resident brackets + Medicare levy.",
})
for r in rates:
    specs.append({
        "mode": "day", "amount": r, "path": f"/{r}-day-rate/", "example": False,
        "outfile": str(PUB / f"{r}-day-rate" / "index.html"),
        "title": f"{money(r)} Day Rate Calculator (AU) — Annual and Take-Home FY2025-26",
        "h1": f"{money(r)}/day contractor calculator (Australia)",
        "desc": f"What does a {money(r)} day rate mean annually for an AU freelancer? GST in/ex, 220 days/year default, and estimated after-tax take-home for FY2025-26.",
        "intro": f"Preset: {money(r)} day rate (GST exclusive). Adjust days/year and GST toggle — results update instantly.",
    })
for s in sals:
    specs.append({
        "mode": "annual", "amount": s, "path": f"/{s}-salary-after-tax/", "example": False,
        "outfile": str(PUB / f"{s}-salary-after-tax" / "index.html"),
        "title": f"{money(s)} Salary After Tax (AU) — Freelancer Equivalent FY2025-26",
        "h1": f"{money(s)} after-tax / annual calculator (AU)",
        "desc": f"Estimate take-home on {money(s)} annual income for an Australian resident, plus day-rate equivalent at 220 billable days. FY2025-26 ATO brackets + Medicare.",
        "intro": f"Preset: {money(s)} annual income (GST exclusive). Switch to day-rate mode to reverse-engineer your rate.",
    })
for i, spec in enumerate(specs):
    p = OUT / f"{i:03d}.json"
    p.write_text(json.dumps(spec), encoding="utf-8")
print(f"wrote {len(specs)} specs")
