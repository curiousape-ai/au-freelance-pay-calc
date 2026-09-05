#!/usr/bin/env python3
"""Parity check: embedded calc.js (via node) vs taxlib.py.

Covers every preset page input plus bracket edges, Medicare shade
boundaries, and degenerate inputs. Exits non-zero on any divergence,
so it can run as a generator pre-flight.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import taxlib as T

DAY_RATES = list(range(400, 1550, 50))
SALARIES = [60000, 70000, 80000, 90000, 100000, 110000, 120000, 130000, 150000, 180000, 200000]
# Bracket edges +-1 and Medicare shade boundaries +-1, exercised as annual income.
EDGES = [0, 1, 18200, 18201, 28011, 28012, 35012, 35013, 45000, 45001, 135000, 135001, 190000, 190001, 10_000_000]
DAY_COUNTS = [1, 220, 365]

FIELDS = ["annualEx", "annualIncl", "annualGst", "deductions", "taxable", "tax", "medicare", "totalTax",
          "takeHome", "weeklyTakeHome", "effectiveRate", "superSetAside", "takeHomeAfterSuper"]


def cases():
    out = []
    for days in DAY_COUNTS:
        for r in DAY_RATES:
            for inc in (False, True):
                out.append({"mode": "day", "amount": r, "days": days, "gstInclusive": inc})
    for s in SALARIES + EDGES:
        for inc in (False, True):
            out.append({"mode": "annual", "amount": s, "days": 220, "gstInclusive": inc})
    # Deductions: typical, and deliberately exceeding income (taxable floors at 0).
    for ded in (5000, 20000, 999999):
        out.append({"mode": "day", "amount": 800, "days": 220, "gstInclusive": False, "deductions": ded})
        out.append({"mode": "annual", "amount": 80000, "days": 220, "gstInclusive": False, "deductions": ded})
    return out


def main():
    cs = cases()
    proc = subprocess.run(
        ["node", str(HERE / "calc_runner.js")],
        input=json.dumps(cs), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        print("node runner failed:\n" + proc.stderr)
        return 1
    js = proc.stdout and json.loads(proc.stdout)

    bad = 0
    for c, j in zip(cs, js):
        p = T.calculate(c["mode"], c["amount"], c["days"], c["gstInclusive"], c.get("deductions", 0))
        for f in FIELDS:
            if abs(j[f] - p[f]) > 0.01:
                bad += 1
                print(f"MISMATCH {c} field={f}: js={j[f]} py={p[f]}")
    print(f"parity: {len(cs)} cases x {len(FIELDS)} fields, {bad} mismatches")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
