#!/usr/bin/env python3
import json, subprocess, sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE)); import taxlib as T
EDGES=[0,1,18200,18201,28011,28012,35012,35013,45000,45001,67000,67001,69528,69529,125000,125001,129717,129718,135000,135001,190000,190001,10_000_000]
FIELDS=["annualEx","annualIncl","annualGst","taxable","tax","medicare","helpRepayment","totalTax","takeHome","weeklyTakeHome","effectiveRate","superSetAside","employerSuper","takeHomeAfterSuper"]

def cases():
  out=[]
  for fy in T.CONFIG["years"]:
    for days in (1,220,365):
      for rate in T.PRESET_DAY_RATES:
        for inc in (False,True): out.append({"mode":"day","amount":rate,"days":days,"gstInclusive":inc,"fy":fy})
    for amount in T.PRESET_SALARIES+EDGES:
      for mode in ("annual","employee"):
        for help_value in (False,True): out.append({"mode":mode,"amount":amount,"days":220,"gstInclusive":False,"hasHelp":help_value,"fy":fy})
    for rate in T.PRESET_HOURLY_RATES: out.append({"mode":"hourly","amount":rate,"days":220,"hoursPerDay":8,"gstInclusive":False,"fy":fy})
    for target in (500,1000,1500,2424,3000,5000): out.append({"mode":"solve","amount":target,"days":220,"deductions":15000,"hasHelp":True,"fy":fy})
  return out

def main():
  cs=cases(); proc=subprocess.run(["node",str(HERE/"calc_runner.js")],input=json.dumps(cs),capture_output=True,text=True)
  if proc.returncode: print(proc.stderr); return 1
  js=json.loads(proc.stdout); bad=0
  for c,j in zip(cs,js):
    if c["mode"]=="solve":
      p=T.solve_day_rate_for_weekly_take_home(c["amount"],c["days"],c.get("deductions",0),c["fy"],c.get("hasHelp",False))
      if abs(j["solved"]-p)>.01: bad+=1; print("MISMATCH",c,"solved",j["solved"],p)
      continue
    p=T.calculate(c["mode"],c["amount"],c.get("days"),c.get("gstInclusive",False),c.get("deductions",0),c["fy"],c.get("hasHelp",False),c.get("hoursPerDay"))
    for f in FIELDS:
      if abs(j[f]-p[f])>.01: bad+=1; print("MISMATCH",c,f,j[f],p[f])
  print(f"parity: {len(cs)} cases x {len(FIELDS)} fields, {bad} mismatches")
  return bool(bad)
if __name__=="__main__": sys.exit(main())
