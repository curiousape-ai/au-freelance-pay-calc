#!/usr/bin/env python3
import html as H,json,os,sys
from datetime import date
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import taxlib as T
HERE=Path(__file__).resolve().parent;CFG=T.CONFIG;TPL=(HERE/"page_template.html").read_text();PRESETS=(HERE/"presets.html").read_text();FY=CFG["default_fy"];YC=CFG["years"][FY];DAYS=CFG["default_days"];BASE=os.environ.get("SITE_BASE_URL",CFG["base_url"]).rstrip("/")
SOURCES="\n".join(f'<li><a href="{H.escape(s["url"])}" rel="noopener" target="_blank">{H.escape(s["label"])}</a></li>' for s in CFG["sources"])

def answer(mode,amount,r):
  if mode=="employee":
    eq=T.solve_contractor_day_rate_for_employee_salary(amount,DAYS,0,FY)
    return f"A {T.money(amount)} employee salary leaves an estimated {T.fmt_aud(r['takeHome'])} after resident income tax and Medicare in FY{FY}. Employer super is {T.fmt_aud(r['employerSuper'])} on top. A contractor would need about {T.fmt_aud(eq)}/day ex GST over {DAYS} days for the same take-home."
  unit="hour" if mode=="hourly" else "day" if mode=="day" else "year"
  return f"At {T.money(amount)} per {unit}, estimated GST-exclusive revenue is {T.fmt_aud(r['annualEx'])}. Resident income tax is {T.fmt_aud(r['tax'])}, Medicare is {T.fmt_aud(r['medicare'])}, and take-home is about {T.fmt_aud(r['takeHome'])} ({T.fmt_aud(r['weeklyTakeHome'])}/week) in FY{FY}."

def faqs(mode,amount,r):
  return [("Which financial year does this use?",f"Baked figures use FY{FY}. Use the financial-year switch to compare FY2025-26."),("How is take-home calculated?",f"GST-exclusive revenue minus deductions, resident income tax, Medicare and an optional HELP repayment. The default is {DAYS} billable days."),("Does this include super?","For contractors, 12% is shown as a voluntary set-aside. For employees, 12% employer super is shown on top of salary."),("Is this tax advice?","No. It is an estimate for planning. Confirm your circumstances with the ATO or a registered tax agent.")]

def neighbours(mode,amount):
  if mode=="day": items,path,label=T.PRESET_DAY_RATES,"/{v}-day-rate/",lambda v:f"{T.money(v)}/day"
  elif mode=="employee": items,path,label=T.PRESET_SALARIES,"/{v}-salary-after-tax/",lambda v:f"{T.money(v)} salary"
  elif mode=="hourly": items,path,label=T.PRESET_HOURLY_RATES,"/{v}-hourly-rate/",lambda v:f"{T.money(v)}/hour"
  else:return""
  if amount not in items:return""
  i=items.index(amount);rows=[]
  for v in items[max(0,i-2):i+3]:
    rr=T.calculate(mode,v,DAYS,False,0,FY);name=H.escape(label(v)) if v==amount else f'<a href="{path.format(v=v)}">{H.escape(label(v))}</a>';rows.append(f'<tr><td>{name}</td><td>{T.fmt_aud(rr["annualEx"])}</td><td>{T.fmt_aud(rr["takeHome"])}</td></tr>')
  return f'<table class="baked neighbours"><caption>Nearby FY{FY} presets</caption><thead><tr><th>Preset</th><th>Annual</th><th>Take-home</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'

def main():
  meta=json.loads(Path(sys.argv[1]).read_text());mode=meta["mode"];amount=int(meta["amount"]);r=T.calculate(mode,amount,DAYS,False,0,FY);faq=faqs(mode,amount,r);page_url=BASE+meta["path"]
  person={"@type":"Person","@id":BASE+"/#author","name":CFG["author"]["name"],"url":CFG["author"]["url"],"sameAs":CFG["author"]["same_as"]};org={"@type":"Organization","@id":BASE+"/#publisher","name":CFG["publisher"]["name"],"url":CFG["publisher"]["url"],"sameAs":CFG["publisher"]["same_as"]}
  app={"@type":"WebApplication","@id":BASE+"/#calculator","name":CFG["site_name"],"url":page_url,"applicationCategory":"FinanceApplication","operatingSystem":"Any","dateModified":date.today().isoformat(),"author":{"@id":person["@id"]},"publisher":{"@id":org["@id"]},"offers":{"@type":"Offer","price":"0","priceCurrency":"AUD"}}
  faq_schema={"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}}for q,a in faq]};ld={"@context":"https://schema.org","@graph":[person,org,app,faq_schema]}
  cap=f"Preset snapshot, FY{FY}. Interactive results update when inputs change.";a=answer(mode,amount,r)
  home=meta["path"]=="/"
  hero='<a class="primary no-print" href="#amount" id="hero-cta">Enter your rate</a>' if home else '<a class="ghost" href="/">Full calculator</a>'
  nxt='' if not home else '<section class="card next-step no-print" id="next-step"><h2>Next step</h2><p>Print this estimate, compare baked presets, or join the contractor tips list.</p><p class="cta-row"><button type="button" class="primary" id="next-print">Print / save PDF</button> <a class="ghost" href="/presets/">Browse presets</a> <a class="ghost" href="#lead-form">Get tips</a></p></section>'
  repl={"__HERO_CTA__":hero,"__NEXT_STEP__":nxt,"__OG_TITLE__":H.escape(meta["title"]),"__OG_DESC__":H.escape(meta["desc"]),"__CANONICAL__":H.escape(page_url),"__OG_IMAGE__":H.escape(BASE+"/og.png"),"__FAQ_JSON_LD__":json.dumps(ld,ensure_ascii=False),"__ANALYTICS_DOMAIN__":H.escape(CFG["analytics_domain"]),"__PRESET_MODE__":mode,"__PRESET_AMOUNT__":str(amount),"__FY__":FY,"__H1__":H.escape(meta["h1"]),"__INTRO__":H.escape(meta["intro"]),"__ANSWER_HEADING__":"Quick answer (example)" if meta.get("example") else "Quick answer","__ANSWER__":H.escape(a),"__AMOUNT_LABEL__":"Employee salary (AUD)" if mode=="employee" else "Hourly rate (AUD)" if mode=="hourly" else "Day rate (AUD)","__GST_HINT__":"Employee salaries do not include GST." if mode=="employee" else "Choose whether the entered amount includes GST.","__DAYS__":str(DAYS),"__V_ANNUAL_EX__":T.fmt_aud(r["annualEx"]),"__V_ANNUAL_INC__":T.fmt_aud(r["annualIncl"]),"__V_GST__":T.fmt_aud(r["annualGst"]),"__V_DAY_EX__":T.fmt_aud2(r["dayEx"]),"__V_DAY_INC__":T.fmt_aud2(r["dayIncl"]),"__V_WEEKLY__":T.fmt_aud(r["weeklyGrossEx"]),"__V_TAX__":T.fmt_aud(r["tax"]),"__V_MEDICARE__":T.fmt_aud(r["medicare"]),"__V_EFF__":T.fmt_pct(r["effectiveRate"]),"__V_TAKE__":T.fmt_aud(r["takeHome"]),"__V_TAKE_WEEK__":T.fmt_aud(r["weeklyTakeHome"]),"__V_SUPER__":T.fmt_aud(r["employerSuper"] if mode=="employee" else r["superSetAside"]),"__V_TAKE_SUPER__":T.fmt_aud(r["takeHomeAfterSuper"]),"__SG_PCT__":str(int(CFG["sg_rate"]*100)),"__CAPTION__":cap,"__NEIGHBOURS__":neighbours(mode,amount),"__PRESETS__":PRESETS,"__FAQ_ITEMS__":"".join(f'<li><h3>{H.escape(q)}</h3><p>{H.escape(x)}</p></li>'for q,x in faq),"__SOURCES__":SOURCES,"__LAST_CHECKED__":YC["last_checked"],"__DATE_MODIFIED__":date.today().isoformat(),"__MEDICARE_NOTE__":H.escape(YC["medicare_note"])}
  out=TPL
  for k,v in repl.items():out=out.replace(k,v)
  dest=Path(meta["outfile"]);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(out);print("wrote",dest)
if __name__=="__main__":main()
