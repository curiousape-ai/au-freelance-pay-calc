import json
from pathlib import Path

# Single source of truth: scripts/cfg.json (same values served as config.js).
CONFIG = json.loads((Path(__file__).resolve().parent / "cfg.json").read_text())

# Preset page families (used by make_specs, write_meta, write_page).
PRESET_DAY_RATES = list(range(400, 1550, 50))
PRESET_SALARIES = [60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 150000, 180000, 200000]

def income_tax(taxable):
    taxable = float(taxable)
    if taxable <= 0:
        return 0.0
    prev = 0.0
    for b in CONFIG["brackets"]:
        up_to = b["up_to"]
        if up_to is None or taxable <= up_to:
            return b["base"] + (taxable - prev) * b["rate"]
        prev = float(up_to)
    return 0.0  # unreachable while a null (top) bracket exists

def medicare_levy(taxable):
    taxable = float(taxable)
    lower = CONFIG["medicare_lower"]
    upper = CONFIG["medicare_upper"]
    rate = CONFIG["medicare_levy"]
    if taxable <= lower:
        return 0.0
    if taxable < upper:
        return min((taxable - lower) * 0.10, taxable * rate)
    return taxable * rate

def calculate(mode, amount, days=None, gst_inclusive=False, deductions=0):
    days = days or CONFIG["default_days"]
    amount = float(amount) or 0.0
    deductions = max(0.0, float(deductions or 0.0))
    r = CONFIG["gst_rate"]
    if gst_inclusive:
        ex = amount / (1 + r)
        inc = amount
        gst = amount - ex
    else:
        ex = amount
        inc = amount * (1 + r)
        gst = amount * r
    if mode == "day":
        annual_ex, annual_inc, annual_gst = ex * days, inc * days, gst * days
        day_ex, day_inc, day_gst = ex, inc, gst
    else:
        annual_ex, annual_inc, annual_gst = ex, inc, gst
        day_ex = annual_ex / days if days else 0.0
        day_inc = annual_inc / days if days else 0.0
        day_gst = annual_gst / days if days else 0.0
    taxable = max(0.0, annual_ex - deductions)
    tax = income_tax(taxable)
    med = medicare_levy(taxable)
    take = max(0.0, taxable - tax - med)
    total = tax + med
    sg = annual_ex * CONFIG["sg_rate"]
    return {
        "days": days,
        "dayEx": day_ex,
        "dayIncl": day_inc,
        "dayGst": day_gst,
        "annualEx": annual_ex,
        "annualIncl": annual_inc,
        "annualGst": annual_gst,
        "deductions": deductions,
        "taxable": taxable,
        "tax": tax,
        "medicare": med,
        "totalTax": total,
        "takeHome": take,
        "weeklyTakeHome": take / 52.0,
        "weeklyGrossEx": annual_ex / 52.0,
        "effectiveRate": (total / taxable) if taxable else 0.0,
        "superSetAside": sg,
        "takeHomeAfterSuper": max(0.0, take - sg),
        "gstInclusive": gst_inclusive,
    }

def solve_day_rate_for_weekly_take_home(target_weekly, days=None, deductions=0):
    """Reverse: weekly take-home target -> GST-exclusive day rate (bisection)."""
    target_weekly = float(target_weekly) or 0.0
    if target_weekly <= 0:
        return 0.0
    lo, hi = 0.0, 20000.0
    for _ in range(80):
        mid = (lo + hi) / 2
        w = calculate("day", mid, days, False, deductions)["weeklyTakeHome"]
        if w < target_weekly:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def money(n):
    return f"${n:,.0f}"

def fmt_aud(n):
    return f"${n:,.0f}"

def fmt_aud2(n):
    return f"${n:,.2f}"

def fmt_pct(n):
    return f"{n * 100:.1f}%"
