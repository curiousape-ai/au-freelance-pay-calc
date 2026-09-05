import json
from pathlib import Path
from taxlib import PRESET_DAY_RATES,PRESET_SALARIES,PRESET_HOURLY_RATES,CONFIG
PUB=Path(__file__).resolve().parent.parent/"public"; OUT=Path("/tmp/pages"); OUT.mkdir(exist_ok=True)
fy=CONFIG["default_fy"]
money=lambda n:f"${n:,.0f}"
specs=[{"mode":"day","amount":800,"path":"/","example":True,"outfile":str(PUB/"index.html"),"title":f"Day Rate Calculator Australia — Contractor Take-Home FY{fy}","h1":f"Contractor day rate calculator (Australia, FY{fy})","desc":f"Convert an Australian contractor day rate to annual revenue, GST and estimated FY{fy} take-home.","intro":"Compare contractor day rates, annual revenue, employee salary and target take-home with current Australian resident tax settings."}]
for r in PRESET_DAY_RATES: specs.append({"mode":"day","amount":r,"path":f"/{r}-day-rate/","outfile":str(PUB/f"{r}-day-rate"/"index.html"),"title":f"{money(r)}/day contractor calculator — take-home FY{fy} (Australia)","h1":f"{money(r)}/day contractor calculator (Australia, FY{fy})","desc":f"See annual revenue, tax, Medicare and take-home for a {money(r)} Australian contractor day rate in FY{fy}.","intro":f"Preset: {money(r)} per day, GST exclusive, over 220 billable days."})
for s in PRESET_SALARIES: specs.append({"mode":"employee","amount":s,"path":f"/{s}-salary-after-tax/","outfile":str(PUB/f"{s}-salary-after-tax"/"index.html"),"title":f"{money(s)} a year after tax (Australia, FY{fy}) and contractor equivalent","h1":f"{money(s)} salary after tax and contractor day-rate equivalent","desc":f"Estimate FY{fy} take-home on a {money(s)} Australian employee salary and the contractor day rate with the same take-home.","intro":f"Preset: {money(s)} employee salary with 12% employer super shown on top."})
for h in PRESET_HOURLY_RATES: specs.append({"mode":"hourly","amount":h,"path":f"/{h}-hourly-rate/","outfile":str(PUB/f"{h}-hourly-rate"/"index.html"),"title":f"{money(h)}/hour contractor calculator — FY{fy} (Australia)","h1":f"{money(h)}/hour contractor calculator (Australia, FY{fy})","desc":f"Convert a {money(h)} Australian contractor hourly rate into day, annual and after-tax take-home estimates for FY{fy}.","intro":f"Preset: {money(h)} per hour, GST exclusive, at 8 hours per day and 220 days."})
for i,s in enumerate(specs):(OUT/f"{i:03d}.json").write_text(json.dumps(s))
print(f"wrote {len(specs)} specs")
