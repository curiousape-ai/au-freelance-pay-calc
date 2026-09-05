import json
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parent / "cfg.json").read_text())
PRESET_DAY_RATES = list(range(400, 1550, 50))
PRESET_SALARIES = [60000,70000,80000,90000,100000,110000,120000,130000,150000,180000,200000]
PRESET_HOURLY_RATES = list(range(50, 210, 10))

def year_config(fy=None): return CONFIG["years"][fy or CONFIG["default_fy"]]

def income_tax(taxable, fy=None):
    taxable, prev = max(0.0, float(taxable)), 0.0
    for b in year_config(fy)["brackets"]:
        if b["up_to"] is None or taxable <= b["up_to"]:
            return b["base"] + (taxable - prev) * b["rate"]
        prev = float(b["up_to"])
    return 0.0

def medicare_levy(taxable, fy=None):
    taxable, yc = max(0.0, float(taxable)), year_config(fy)
    if taxable <= yc["medicare_lower"]: return 0.0
    if taxable < yc["medicare_upper"]: return min((taxable-yc["medicare_lower"])*0.10, taxable*yc["medicare_levy"])
    return taxable * yc["medicare_levy"]

def help_repayment(income, fy=None):
    income, hc = max(0.0, float(income)), year_config(fy)["help"]
    if income <= hc["threshold"]: return 0.0
    marginal = (income-hc["threshold"]) * hc["lower_rate"]
    if income > hc["upper_threshold"]: marginal += (income-hc["upper_threshold"]) * hc["upper_rate"]
    return min(marginal, income*hc["cap_rate"])

def calculate(mode, amount, days=None, gst_inclusive=False, deductions=0, fy=None, has_help=False, hours_per_day=None):
    fy, days = fy or CONFIG["default_fy"], float(days or CONFIG["default_days"])
    hours_per_day = float(hours_per_day or CONFIG["default_hours_per_day"])
    amount, deductions = max(0.0,float(amount or 0)), max(0.0,float(deductions or 0))
    employee = mode == "employee"
    if employee:
        annual_ex = annual_inc = amount; annual_gst = 0.0
        day_ex = day_inc = amount/days if days else 0.0; day_gst = 0.0
    else:
        entered = amount*hours_per_day if mode == "hourly" else amount
        if gst_inclusive: ex, inc = entered/(1+CONFIG["gst_rate"]), entered
        else: ex, inc = entered, entered*(1+CONFIG["gst_rate"])
        gst = inc-ex
        if mode in ("day","hourly"):
            day_ex,day_inc,day_gst = ex,inc,gst
            annual_ex,annual_inc,annual_gst = ex*days,inc*days,gst*days
        else:
            annual_ex,annual_inc,annual_gst = ex,inc,gst
            day_ex = annual_ex/days if days else 0.0; day_inc = annual_inc/days if days else 0.0; day_gst = annual_gst/days if days else 0.0
    taxable = max(0.0,annual_ex-deductions)
    tax, med = income_tax(taxable,fy), medicare_levy(taxable,fy)
    help_amount = help_repayment(taxable,fy) if has_help else 0.0
    total = tax+med+help_amount; take = max(0.0,taxable-total)
    employer_super = annual_ex*CONFIG["sg_rate"] if employee else 0.0
    super_set_aside = 0.0 if employee else annual_ex*CONFIG["sg_rate"]
    return {"fy":fy,"days":days,"hoursPerDay":hours_per_day,"dayEx":day_ex,"dayIncl":day_inc,"dayGst":day_gst,
      "hourlyEx":day_ex/hours_per_day if hours_per_day else 0.0,"annualEx":annual_ex,"annualIncl":annual_inc,"annualGst":annual_gst,
      "deductions":deductions,"taxable":taxable,"tax":tax,"medicare":med,"helpRepayment":help_amount,"totalTax":total,
      "takeHome":take,"weeklyTakeHome":take/52.0,"weeklyGrossEx":annual_ex/52.0,"effectiveRate":total/taxable if taxable else 0.0,
      "superSetAside":super_set_aside,"employerSuper":employer_super,"takeHomeAfterSuper":max(0.0,take-super_set_aside),
      "gstInclusive":bool(gst_inclusive and not employee),"hasHelp":bool(has_help)}

def solve_day_rate_for_weekly_take_home(target_weekly, days=None, deductions=0, fy=None, has_help=False):
    target_weekly=max(0.0,float(target_weekly or 0))
    if not target_weekly: return 0.0
    lo,hi=0.0,20000.0
    for _ in range(80):
        mid=(lo+hi)/2
        if calculate("day",mid,days,False,deductions,fy,has_help)["weeklyTakeHome"] < target_weekly: lo=mid
        else: hi=mid
    return (lo+hi)/2

def solve_contractor_day_rate_for_employee_salary(salary, days=None, deductions=0, fy=None, has_help=False):
    take=calculate("employee",salary,days,False,deductions,fy,has_help)["takeHome"]
    return solve_day_rate_for_weekly_take_home(take/52,days,0,fy,has_help)

def money(n): return f"${n:,.0f}"
def fmt_aud(n): return f"${n:,.0f}"
def fmt_aud2(n): return f"${n:,.2f}"
def fmt_pct(n): return f"{n*100:.1f}%"
