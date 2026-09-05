CONFIG = {
    "fy": "2025-26",
    "last_checked": "2026-08-22",
    "gst_rate": 0.10,
    "medicare_levy": 0.02,
    "medicare_lower": 28011,
    "medicare_upper": 35013,
    "default_days": 220,
}

def income_tax(taxable):
    taxable = float(taxable)
    if taxable <= 0:
        return 0.0
    if taxable <= 18200:
        return 0.0
    if taxable <= 45000:
        return (taxable - 18200) * 0.16
    if taxable <= 135000:
        return 4288 + (taxable - 45000) * 0.30
    if taxable <= 190000:
        return 31288 + (taxable - 135000) * 0.37
    return 51638 + (taxable - 190000) * 0.45

def medicare_levy(taxable):
    taxable = float(taxable)
    lower, upper, rate = 28011, 35013, 0.02
    if taxable <= lower:
        return 0.0
    if taxable < upper:
        return min((taxable - lower) * 0.10, taxable * rate)
    return taxable * rate

def calculate(mode, amount, days=220, gst_inclusive=False):
    amount = float(amount) or 0.0
    r = 0.10
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
