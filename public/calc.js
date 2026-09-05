
(function (global) {
  const CFG = global.AU_CALC_CONFIG;

  function incomeTax(taxable) {
    if (taxable <= 0) return 0;
    // Progressive calc driven entirely by CFG.brackets:
    // each bracket carries the cumulative ATO base tax at its lower edge.
    let prev = 0;
    for (const b of CFG.brackets) {
      if (b.up_to === null || taxable <= b.up_to) {
        return b.base + (taxable - prev) * b.rate;
      }
      prev = b.up_to;
    }
    return 0; // unreachable while a null (top) bracket exists
  }

  function medicareLevy(taxable) {
    const lower = CFG.medicare_lower;
    const upper = CFG.medicare_upper;
    const rate = CFG.medicare_levy;
    if (taxable <= lower) return 0;
    if (taxable < upper) {
      // Shade-out: levy = rate * (income - lower) / (upper - lower) * income? 
      // ATO formula: reduced levy = (taxable - lower) * 0.10 (approx shade rate historically)
      // Accurate-enough: linear shade from 0 at lower to full rate*upper at upper.
      // Official reduction: Medicare levy = (taxable income − lower threshold) × 10%
      // until it reaches 2% of taxable income.
      const reduced = (taxable - lower) * 0.10;
      const full = taxable * rate;
      return Math.min(reduced, full);
    }
    return taxable * rate;
  }

  function gstSplit(amount, inclusive) {
    const r = CFG.gst_rate;
    if (inclusive) {
      const ex = amount / (1 + r);
      return { exclusive: ex, inclusive: amount, gst: amount - ex };
    }
    return { exclusive: amount, inclusive: amount * (1 + r), gst: amount * r };
  }

  /**
   * mode: 'day' | 'annual'
   * amount: day rate or annual (depending on gstInclusive interpretation for day rate)
   * days: billable days/year
   * gstInclusive: whether amount includes GST
   * deductions: annual tax deductions (reduce taxable income)
   * For take-home we tax on GST-exclusive income (contractors remit GST; taxable income ≈ excl GST).
   */
  function calculate({ mode, amount, days, gstInclusive, deductions }) {
    days = days || CFG.default_days;
    amount = Number(amount) || 0;
    deductions = Math.max(0, Number(deductions) || 0);
    let dayRateInput = 0;
    let annualGrossInclOrAsEntered = 0;
    let dayEx, dayIncl, dayGst, annualEx, annualIncl, annualGst;

    if (mode === 'day') {
      const split = gstSplit(amount, gstInclusive);
      dayEx = split.exclusive;
      dayIncl = split.inclusive;
      dayGst = split.gst;
      annualEx = dayEx * days;
      annualIncl = dayIncl * days;
      annualGst = dayGst * days;
      dayRateInput = amount;
    } else {
      const split = gstSplit(amount, gstInclusive);
      annualEx = split.exclusive;
      annualIncl = split.inclusive;
      annualGst = split.gst;
      dayEx = days ? annualEx / days : 0;
      dayIncl = days ? annualIncl / days : 0;
      dayGst = days ? annualGst / days : 0;
    }

    const taxable = Math.max(0, annualEx - deductions); // estimate: GST-exclusive revenue minus deductions (contractors remit GST)
    const tax = incomeTax(taxable);
    const medicare = medicareLevy(taxable);
    const totalTax = tax + medicare;
    const takeHome = Math.max(0, taxable - totalTax);
    const weeklyTakeHome = takeHome / 52;
    const weeklyGrossEx = annualEx / 52;
    const effectiveRate = taxable > 0 ? totalTax / taxable : 0;
    const superSetAside = annualEx * CFG.sg_rate;
    const takeHomeAfterSuper = Math.max(0, takeHome - superSetAside);

    return {
      days,
      dayEx, dayIncl, dayGst,
      annualEx, annualIncl, annualGst,
      deductions,
      taxable, tax, medicare, totalTax, takeHome,
      weeklyTakeHome, weeklyGrossEx, effectiveRate,
      superSetAside, takeHomeAfterSuper,
      gstInclusive
    };
  }

  function fmtAUD(n) {
    return new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD', maximumFractionDigits: 0 }).format(n || 0);
  }
  function fmtAUD2(n) {
    return new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD', minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n || 0);
  }
  function fmtPct(n) {
    return (n * 100).toFixed(1) + '%';
  }

  global.AUCalc = { calculate, incomeTax, medicareLevy, gstSplit, fmtAUD, fmtAUD2, fmtPct };
})(window);
