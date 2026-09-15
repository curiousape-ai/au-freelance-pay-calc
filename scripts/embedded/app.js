(function(){
  const $=s=>document.querySelector(s), $$=s=>document.querySelectorAll(s), CFG=window.AU_CALC_CONFIG, F=window.AUCalc;
  window.plausible=window.plausible||function(){(window.plausible.q=window.plausible.q||[]).push(arguments)};
  const params=new URLSearchParams(location.search), isHome=/^\/(index\.html)?$/.test(location.pathname);
  let saved=null;try{saved=isHome?JSON.parse(localStorage.getItem('aucalc')||'null'):null}catch(e){}
  const preset={mode:document.body.dataset.presetMode||'day',amount:document.body.dataset.presetAmount||'800',gst:document.body.dataset.presetGst||'ex',fy:document.body.dataset.presetFy||CFG.default_fy};
  let mode=params.get('mode')||(saved&&saved.mode)||preset.mode;
  let gstInclusive=(params.get('gst')||(saved&&saved.gst)||preset.gst)==='inc';
  let fy=params.get('fy')||(saved&&saved.fy)||preset.fy;
  if(!CFG.years[fy])fy=CFG.default_fy;
  const amount=$('#amount'),days=$('#days'),ded=$('#deductions'),hours=$('#hours'),help=$('#has-help'),amountLabel=$('#amount-label');
  let calcTimer;
  function track(name,props){window.plausible(name,{props:props||{}})}
  function setPressed(nodes,predicate){nodes.forEach(b=>{const on=predicate(b);b.classList.toggle('active',on);b.setAttribute('aria-pressed',String(on))})}
  function updateControls(){
    setPressed($$('[data-mode]'),b=>b.dataset.mode===mode);setPressed($$('[data-gst]'),b=>(b.dataset.gst==='inc')===gstInclusive);setPressed($$('[data-fy]'),b=>b.dataset.fy===fy);
    const disabled=mode==='target'||mode==='employee',gstSeg=$('#gst-seg');gstSeg.setAttribute('aria-disabled',String(disabled));$$('[data-gst]').forEach(b=>b.disabled=disabled);
    $('#hours-field').hidden=mode!=='hourly';
    amountLabel.textContent=mode==='day'?'Day rate (AUD)':mode==='annual'?'Annual contractor revenue (AUD)':mode==='target'?'Target weekly take-home (AUD)':mode==='employee'?'Employee salary (AUD)':'Hourly rate (AUD)';
    $('#gst-hint').textContent=mode==='target'?'Target mode is solved ex GST.':mode==='employee'?'Employee salaries do not include GST.':'Choose whether the entered amount includes GST.';
    $('#badge-fy').textContent=fy;$$('.current-fy').forEach(el=>el.textContent=fy);
  }
  function sync(){const state={mode,gst:gstInclusive?'inc':'ex',fy,amount:amount.value,days:days.value,ded:ded.value,hours:hours.value,help:help.checked?'1':'0'};try{history.replaceState(null,'',location.pathname+'?'+new URLSearchParams(state));localStorage.setItem('aucalc',JSON.stringify(state))}catch(e){}}
  function changedFromBake(){return mode!==preset.mode||String(amount.value)!==String(preset.amount)||gstInclusive||(Number(days.value)||CFG.default_days)!==CFG.default_days||(Number(ded.value)||0)!==0||fy!==preset.fy||help.checked||mode==='hourly'}
  function updateBaked(r){const changed=changedFromBake();$$('table.baked').forEach(t=>t.hidden=changed);if(changed){$('#answer-heading').textContent='Your estimate';$('#quick-answer').textContent=`Estimated FY${fy} take-home is ${F.fmtAUD(r.takeHome)} a year (${F.fmtAUD(r.weeklyTakeHome)} a week) from ${F.fmtAUD(r.annualEx)} taxable revenue before deductions. This is an estimate, not advice.`}}
  function recalc(trackChange){
    const n=Number(amount.value)||0,d=Number(days.value)||CFG.default_days,dx=Number(ded.value)||0,h=Number(hours.value)||CFG.default_hours_per_day;
    let r,solved=null;if(mode==='target'){solved=F.solveDayRateForWeeklyTakeHome(n,d,dx,fy,help.checked);r=F.calculate({mode:'day',amount:solved,days:d,deductions:dx,fy,hasHelp:help.checked,gstInclusive:false})}else r=F.calculate({mode,amount:n,days:d,deductions:dx,fy,hasHelp:help.checked,gstInclusive,hoursPerDay:h});
    $('#solved-card').hidden=mode!=='target';if(solved!==null){$('#out-solved').textContent=F.fmtAUD(solved)+' /day';$('#out-solved-inc').textContent=F.fmtAUD(solved*(1+CFG.gst_rate))}
    $('#equivalent-card').hidden=mode!=='employee';if(mode==='employee')$('#out-equivalent').textContent=F.fmtAUD(F.solveContractorDayRateForEmployeeSalary(n,d,dx,fy,help.checked))+' /day ex GST';
    const pairs={"#out-annual-ex":F.fmtAUD(r.annualEx),"#out-annual-inc":F.fmtAUD(r.annualIncl),"#out-day-ex":F.fmtAUD2(r.dayEx),"#out-day-inc":F.fmtAUD2(r.dayIncl),"#out-gst-annual":F.fmtAUD(r.annualGst),"#out-weekly":F.fmtAUD(r.weeklyGrossEx),"#out-tax":F.fmtAUD(r.tax),"#out-medicare":F.fmtAUD(r.medicare),"#out-help":F.fmtAUD(r.helpRepayment),"#out-takehome":F.fmtAUD(r.takeHome),"#out-takehome-week":F.fmtAUD(r.weeklyTakeHome),"#out-eff":F.fmtPct(r.effectiveRate),"#out-super":F.fmtAUD(mode==='employee'?r.employerSuper:r.superSetAside),"#out-takehome-super":F.fmtAUD(r.takeHomeAfterSuper),"#out-days":String(r.days)};Object.entries(pairs).forEach(([s,v])=>$(s).textContent=v);
    $('#super-label').textContent=mode==='employee'?`Employer super on top (${CFG.sg_rate*100}%)`:`Super set-aside (${CFG.sg_rate*100}%)`;$('#help-card').hidden=!help.checked;$('#gst-threshold-hint').hidden=mode==='employee'||r.annualEx>=CFG.gst_registration_threshold;
    updateBaked(r);sync();if(trackChange){clearTimeout(calcTimer);calcTimer=setTimeout(()=>track('calc_change',{mode,fy}),600)}
  }
  function setMode(value,user){mode=['day','annual','target','employee','hourly'].includes(value)?value:'day';if(mode==='target'||mode==='employee')gstInclusive=false;updateControls();recalc(user);if(user)track('mode_change',{mode})}
  function setGst(value){if(mode==='target'||mode==='employee')return;gstInclusive=value;updateControls();recalc(true)}
  function setFy(value){if(CFG.years[value])fy=value;updateControls();recalc(true)}
  amount.value=params.get('amount')||(saved&&saved.amount)||preset.amount;days.value=params.get('days')||(saved&&saved.days)||CFG.default_days;ded.value=params.get('ded')||(saved&&saved.ded)||'0';hours.value=params.get('hours')||(saved&&saved.hours)||CFG.default_hours_per_day;help.checked=(params.get('help')||(saved&&saved.help)||'0')==='1';
  $$('[data-mode]').forEach(b=>b.addEventListener('click',()=>setMode(b.dataset.mode,true)));$$('[data-gst]').forEach(b=>b.addEventListener('click',()=>setGst(b.dataset.gst==='inc')));$$('[data-fy]').forEach(b=>b.addEventListener('click',()=>setFy(b.dataset.fy)));[amount,days,ded,hours,help].forEach(el=>el.addEventListener('input',()=>recalc(true)));setMode(mode,false);
  $('#print-btn')?.addEventListener('click',()=>{track('print',{mode,fy});window.print()});
  $('#hero-cta')?.addEventListener('click',e=>{e.preventDefault();amount.focus();amount.select();amount.scrollIntoView({block:'center'})});
  $('#next-print')?.addEventListener('click',()=>$('#print-btn')?.click());
  const form=$('#lead-form'),msg=$('#form-msg');form?.addEventListener('submit',async e=>{e.preventDefault();msg.textContent='';msg.className='form-msg';const fd=new FormData(form);if(!fd.get('form-name'))fd.set('form-name','lead');try{const res=await fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(fd)});if(!res.ok)throw new Error();msg.classList.add('ok');msg.textContent='Thanks — you are on the tips list.';form.reset();track('lead_submit')}catch(err){msg.classList.add('err');msg.textContent='Could not submit. Please try again in a minute.'}});
})();
