
(function () {
  const $ = (sel) => document.querySelector(sel);
  const modeBtns = document.querySelectorAll('[data-mode]');
  const gstBtns = document.querySelectorAll('[data-gst]');
  const amountEl = $('#amount');
  const daysEl = $('#days');
  const dedEl = $('#deductions');
  const amountLabel = $('#amount-label');
  const CFG = window.AU_CALC_CONFIG;

  // --- State resolution: query > (home only) saved > preset -------------
  // Variant pages keep their preset as the URL's promise; saved inputs are
  // restored only on the home page.
  const params = new URLSearchParams(location.search);
  const isHome = /^\/(index\.html)?$/.test(location.pathname);
  let saved = null;
  try { saved = isHome ? JSON.parse(localStorage.getItem('aucalc') || 'null') : null; } catch (e) { /* ignore */ }
  const presetMode = document.body.dataset.presetMode || 'day';
  const presetGst = document.body.dataset.presetGst || 'ex';

  let mode = params.get('mode') || (saved && saved.mode) || presetMode;
  let gstInclusive = (params.get('gst') || (saved && saved.gst) || presetGst) === 'inc';

  function setMode(m) {
    mode = ['day', 'annual', 'target'].includes(m) ? m : 'day';
    modeBtns.forEach(b => b.classList.toggle('active', b.dataset.mode === mode));
    amountLabel.textContent = mode === 'day' ? 'Day rate (AUD)'
      : mode === 'annual' ? 'Annual contractor revenue (AUD)'
      : 'Target weekly take-home (AUD)';
    if (!amountEl.value) {
      amountEl.value = mode === 'day' ? '800' : mode === 'annual' ? '120000' : '2000';
    }
    recalc();
  }
  function setGst(inc) {
    gstInclusive = !!inc;
    gstBtns.forEach(b => b.classList.toggle('active', (b.dataset.gst === 'inc') === gstInclusive));
    recalc();
  }

  // Keep the URL shareable and persist the session (home restore).
  function sync() {
    const state = {
      mode, gst: gstInclusive ? 'inc' : 'ex',
      amount: amountEl.value, days: daysEl.value, ded: dedEl.value,
    };
    const qs = new URLSearchParams(state).toString();
    try {
      history.replaceState(null, '', location.pathname + '?' + qs);
      localStorage.setItem('aucalc', JSON.stringify(state));
    } catch (e) { /* file:// or privacy mode — non-fatal */ }
  }

  function recalc() {
    const amount = parseFloat(amountEl.value) || 0;
    const days = parseFloat(daysEl.value) || CFG.default_days;
    const deductions = parseFloat(dedEl.value) || 0;
    const solvedCard = $('#solved-card');
    let r;
    if (mode === 'target') {
      // Solve on a GST-exclusive basis, then render the solved day rate.
      const dayRate = window.AUCalc.solveDayRateForWeeklyTakeHome(amount, days, deductions);
      r = window.AUCalc.calculate({ mode: 'day', amount: dayRate, days, gstInclusive: false, deductions });
      solvedCard.style.display = '';
      $('#out-solved').textContent = window.AUCalc.fmtAUD(dayRate) + ' /day';
      $('#out-solved-inc').textContent = window.AUCalc.fmtAUD(dayRate * (1 + CFG.gst_rate));
    } else {
      r = window.AUCalc.calculate({ mode, amount, days, gstInclusive, deductions });
      solvedCard.style.display = 'none';
    }
    const F = window.AUCalc;
    $('#out-annual-ex').textContent = F.fmtAUD(r.annualEx);
    $('#out-annual-inc').textContent = F.fmtAUD(r.annualIncl);
    $('#out-day-ex').textContent = F.fmtAUD2(r.dayEx);
    $('#out-day-inc').textContent = F.fmtAUD2(r.dayIncl);
    $('#out-gst-annual').textContent = F.fmtAUD(r.annualGst);
    $('#out-weekly').textContent = F.fmtAUD(r.weeklyGrossEx);
    $('#out-tax').textContent = F.fmtAUD(r.tax);
    $('#out-medicare').textContent = F.fmtAUD(r.medicare);
    $('#out-takehome').textContent = F.fmtAUD(r.takeHome);
    $('#out-takehome-week').textContent = F.fmtAUD(r.weeklyTakeHome);
    $('#out-eff').textContent = F.fmtPct(r.effectiveRate);
    $('#out-days').textContent = String(r.days);
    $('#out-super').textContent = F.fmtAUD(r.superSetAside);
    $('#out-takehome-super').textContent = F.fmtAUD(r.takeHomeAfterSuper);
    sync();
  }

  modeBtns.forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  gstBtns.forEach(b => b.addEventListener('click', () => setGst(b.dataset.gst === 'inc')));
  amountEl.addEventListener('input', recalc);
  daysEl.addEventListener('input', recalc);
  dedEl.addEventListener('input', recalc);

  // Initial inputs: query > saved (home) > preset baked into the page.
  amountEl.value = params.get('amount')
    || (saved && saved.amount)
    || document.body.dataset.presetAmount
    || '';
  daysEl.value = params.get('days')
    || (saved && saved.days)
    || String(CFG.default_days);
  dedEl.value = params.get('ded')
    || (saved && saved.ded)
    || '0';
  setMode(mode);
  setGst(gstInclusive);


  // Email form — Formspree if configured; else Netlify Forms POST to current path
  const form = $('#lead-form');
  const msg = $('#form-msg');
  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      msg.textContent = '';
      msg.className = 'form-msg';
      const endpoint = CFG.formspree_endpoint;
      const fd = new FormData(form);
      const useFormspree = endpoint && !endpoint.includes('YOUR_FORM_ID');
      try {
        let res;
        if (useFormspree) {
          res = await fetch(endpoint, { method: 'POST', body: fd, headers: { 'Accept': 'application/json' } });
        } else {
          // Netlify Forms: encode as application/x-www-form-urlencoded
          if (!fd.get('form-name')) fd.set('form-name', 'lead');
          const body = new URLSearchParams(fd).toString();
          res = await fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body
          });
        }
        if (res.ok) {
          msg.classList.add('ok');
          msg.textContent = 'Thanks — we will be in touch.';
          form.reset();
        } else {
          msg.classList.add('err');
          msg.textContent = useFormspree
            ? 'Could not submit. Please try again later.'
            : 'Form endpoint not fully configured (Formspree ID still placeholder). On Netlify, check Forms dashboard after claiming the site. Submissions may still be captured if Netlify Forms is active.';
        }
      } catch (err) {
        msg.classList.add('err');
        msg.textContent = 'Network error. Please try again.';
      }
    });
  }

})();
