import json
from pathlib import Path

# Single source of truth: scripts/cfg.json (same values served as config.js).
CONFIG = json.loads((Path(__file__).resolve().parent / "cfg.json").read_text())

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

def calculate(mode, amount, days=None, gst_inclusive=False):
    days = days or CONFIG["default_days"]
    amount = float(amount) or 0.0
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
    tax = income_tax(annual_ex)
    med = medicare_levy(annual_ex)
    take = max(0.0, annual_ex - tax - med)
    total = tax + med
    return {
        "days": days,
        "dayEx": day_ex,
        "dayIncl": day_inc,
        "dayGst": day_gst,
        "annualEx": annual_ex,
        "annualIncl": annual_inc,
        "annualGst": annual_gst,
        "taxable": annual_ex,
        "tax": tax,
        "medicare": med,
        "totalTax": total,
        "takeHome": take,
        "weeklyTakeHome": take / 52.0,
        "weeklyGrossEx": annual_ex / 52.0,
        "effectiveRate": (total / annual_ex) if annual_ex else 0.0,
        "gstInclusive": gst_inclusive,
    }

def money(n):
    return f"${n:,.0f}"

def fmt_aud(n):
    return f"${n:,.0f}"

def fmt_aud2(n):
    return f"${n:,.2f}"

def fmt_pct(n):
    return f"{n * 100:.1f}%"
