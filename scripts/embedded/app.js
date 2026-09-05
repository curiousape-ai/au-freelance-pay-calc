
(function () {
  const $ = (sel) => document.querySelector(sel);
  const modeBtns = document.querySelectorAll('[data-mode]');
  const gstBtns = document.querySelectorAll('[data-gst]');
  const amountEl = $('#amount');
  const daysEl = $('#days');
  const amountLabel = $('#amount-label');
  let mode = document.body.dataset.presetMode || 'day';
  let gstInclusive = (document.body.dataset.presetGst || 'ex') === 'inc';

  function setMode(m) {
    mode = m;
    modeBtns.forEach(b => b.classList.toggle('active', b.dataset.mode === m));
    amountLabel.textContent = m === 'day' ? 'Day rate (AUD)' : 'Annual contractor revenue (AUD)';
    if (!amountEl.value) {
      amountEl.value = m === 'day' ? '800' : '120000';
    }
    recalc();
  }
  function setGst(inc) {
    gstInclusive = inc;
    gstBtns.forEach(b => b.classList.toggle('active', (b.dataset.gst === 'inc') === inc));
    recalc();
  }

  function recalc() {
    const amount = parseFloat(amountEl.value) || 0;
    const days = parseFloat(daysEl.value) || window.AU_CALC_CONFIG.default_days;
    const r = window.AUCalc.calculate({ mode, amount, days, gstInclusive });
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
  }

  modeBtns.forEach(b => b.addEventListener('click', () => setMode(b.dataset.mode)));
  gstBtns.forEach(b => b.addEventListener('click', () => setGst(b.dataset.gst === 'inc')));
  amountEl.addEventListener('input', recalc);
  daysEl.addEventListener('input', recalc);

  // Apply preset from body dataset
  if (document.body.dataset.presetAmount) {
    amountEl.value = document.body.dataset.presetAmount;
  }
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
      const endpoint = window.AU_CALC_CONFIG.formspree_endpoint;
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
