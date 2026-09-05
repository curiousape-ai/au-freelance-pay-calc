(function(global){
  const CFG=global.AU_CALC_CONFIG, yc=(fy)=>CFG.years[fy||CFG.default_fy];
  function incomeTax(x,fy){x=Math.max(0,Number(x)||0);let prev=0;for(const b of yc(fy).brackets){if(b.up_to===null||x<=b.up_to)return b.base+(x-prev)*b.rate;prev=b.up_to}return 0}
  function medicareLevy(x,fy){x=Math.max(0,Number(x)||0);const y=yc(fy);if(x<=y.medicare_lower)return 0;if(x<y.medicare_upper)return Math.min((x-y.medicare_lower)*.1,x*y.medicare_levy);return x*y.medicare_levy}
  function helpRepayment(x,fy){x=Math.max(0,Number(x)||0);const h=yc(fy).help;if(x<=h.threshold)return 0;let m=(x-h.threshold)*h.lower_rate;if(x>h.upper_threshold)m+=(x-h.upper_threshold)*h.upper_rate;return Math.min(m,x*h.cap_rate)}
  function split(x,inc){if(inc){const ex=x/(1+CFG.gst_rate);return{ex,inc:x,gst:x-ex}}return{ex:x,inc:x*(1+CFG.gst_rate),gst:x*CFG.gst_rate}}
  function calculate({mode,amount,days,gstInclusive,deductions,fy,hasHelp,hoursPerDay}){
    fy=fy||CFG.default_fy;days=Number(days)||CFG.default_days;hoursPerDay=Number(hoursPerDay)||CFG.default_hours_per_day;amount=Math.max(0,Number(amount)||0);deductions=Math.max(0,Number(deductions)||0);
    const employee=mode==='employee';let dayEx,dayIncl,dayGst,annualEx,annualIncl,annualGst;
    if(employee){annualEx=annualIncl=amount;annualGst=0;dayEx=dayIncl=days?amount/days:0;dayGst=0}
    else{const entered=mode==='hourly'?amount*hoursPerDay:amount,s=split(entered,!!gstInclusive);if(mode==='day'||mode==='hourly'){dayEx=s.ex;dayIncl=s.inc;dayGst=s.gst;annualEx=dayEx*days;annualIncl=dayIncl*days;annualGst=dayGst*days}else{annualEx=s.ex;annualIncl=s.inc;annualGst=s.gst;dayEx=days?annualEx/days:0;dayIncl=days?annualIncl/days:0;dayGst=days?annualGst/days:0}}
    const taxable=Math.max(0,annualEx-deductions),tax=incomeTax(taxable,fy),medicare=medicareLevy(taxable,fy),help=hasHelp?helpRepayment(taxable,fy):0,totalTax=tax+medicare+help,takeHome=Math.max(0,taxable-totalTax),employerSuper=employee?annualEx*CFG.sg_rate:0,superSetAside=employee?0:annualEx*CFG.sg_rate;
    return{fy,days,hoursPerDay,dayEx,dayIncl,dayGst,hourlyEx:hoursPerDay?dayEx/hoursPerDay:0,annualEx,annualIncl,annualGst,deductions,taxable,tax,medicare,helpRepayment:help,totalTax,takeHome,weeklyTakeHome:takeHome/52,weeklyGrossEx:annualEx/52,effectiveRate:taxable?totalTax/taxable:0,superSetAside,employerSuper,takeHomeAfterSuper:Math.max(0,takeHome-superSetAside),gstInclusive:!!gstInclusive&&!employee,hasHelp:!!hasHelp}
  }
  function solveDayRateForWeeklyTakeHome(target,days,deductions,fy,hasHelp){target=Math.max(0,Number(target)||0);if(!target)return 0;let lo=0,hi=20000;for(let i=0;i<80;i++){const mid=(lo+hi)/2,v=calculate({mode:'day',amount:mid,days,gstInclusive:false,deductions,fy,hasHelp}).weeklyTakeHome;if(v<target)lo=mid;else hi=mid}return(lo+hi)/2}
  function solveContractorDayRateForEmployeeSalary(salary,days,deductions,fy,hasHelp){const take=calculate({mode:'employee',amount:salary,days,deductions,fy,hasHelp}).takeHome;return solveDayRateForWeeklyTakeHome(take/52,days,0,fy,hasHelp)}
  const fmtAUD=n=>new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',maximumFractionDigits:0}).format(n||0),fmtAUD2=n=>new Intl.NumberFormat('en-AU',{style:'currency',currency:'AUD',minimumFractionDigits:2,maximumFractionDigits:2}).format(n||0),fmtPct=n=>(n*100).toFixed(1)+'%';
  global.AUCalc={calculate,solveDayRateForWeeklyTakeHome,solveContractorDayRateForEmployeeSalary,incomeTax,medicareLevy,helpRepayment,fmtAUD,fmtAUD2,fmtPct};
})(window);
