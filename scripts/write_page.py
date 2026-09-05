#!/usr/bin/env python3
import json, html as H, os, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import taxlib as T

HERE = Path(__file__).resolve().parent
CFG = json.loads((HERE / "cfg.json").read_text())
TPL = (HERE / "page_template.html").read_text()
PRESETS = (HERE / "presets.html").read_text()
SOURCES = "\n".join(
    f'<li><a href="{H.escape(s["url"])}" rel="noopener" target="_blank">{H.escape(s["label"])}</a></li>'
    for s in CFG["sources"]
)
FY, DAYS = CFG["fy"], CFG["default_days"]
BASE = os.environ.get("SITE_BASE_URL", CFG["base_url"]).rstrip("/")


def faqs(mode, amount, r, example):
    m, a, a2, p = T.money, T.fmt_aud, T.fmt_aud2, T.fmt_pct
    lo, hi = CFG["medicare_lower"], CFG["medicare_upper"]
    if example:
        return [
            ("How do I convert an AU contractor day rate to annual income?",
             f"Multiply your GST-exclusive day rate by billable days. Default is {DAYS} days. Example: {m(amount)} x {DAYS} = {a(r['annualEx'])} a year before tax."),
            ("Which tax year and brackets does AU Freelancer Calc use?",
             f"ATO resident rates for FY{FY}: 0% to $18,200, 16% to $45,000, 30% to $135,000, 37% to $190,000, then 45%. Medicare 2% with shade ${lo:,} to ${hi:,}. Last checked {CFG['last_checked']}."),
            ("Does estimated take-home include GST, super, or HELP?",
             "No. Taxable income is GST-exclusive revenue. Super, HELP/HECS, MLS, offsets and deductions are not modelled. Estimate only."),
            (f"Example: what does a {m(amount)} day rate come to after tax?",
             f"Labelled example {m(amount)}/day GST exclusive over {DAYS} days: annual {a(r['annualEx'])} (ex GST), income tax {a(r['tax'])}, Medicare {a(r['medicare'])}, take-home {a(r['takeHome'])}."),
            ("Is this official ATO tax advice?",
             "No. Free estimate for AU freelancers, not tax advice. Confirm with the ATO or a registered tax agent."),
        ]
    if mode == "day":
        return [
            (f"How much is a {m(amount)} day rate annually in Australia?",
             f"At {DAYS} billable days, {m(amount)} GST exclusive is {a(r['annualEx'])} a year before tax, or {a(r['annualIncl'])} including 10% GST ({a(r['annualGst'])} GST)."),
            (f"What income tax applies to a {m(amount)}/day contractor rate (FY{FY})?",
             f"Treating {a(r['annualEx'])} GST-exclusive revenue as taxable income with no deductions, resident income tax is about {a(r['tax'])} using ATO FY{FY} brackets."),
            (f"What is estimated take-home on {m(amount)} per day?",
             f"After {a(r['tax'])} income tax and {a(r['medicare'])} Medicare levy, take-home is {a(r['takeHome'])}/year (about {a(r['weeklyTakeHome'])}/week). Effective rate {p(r['effectiveRate'])}."),
            (f"Is the {m(amount)} day rate GST inclusive or exclusive on this page?",
             f"This preset is GST exclusive. Toggle inclusive to model {m(amount)} inc-GST (ex-GST then about {a2(amount/1.10)}/day)."),
            (f"How many billable days does this {m(amount)} calculator assume?",
             f"Default is {DAYS} billable days per year. Change the days field to remodel annual, tax, and take-home."),
        ]
    return [
        (f"How much tax does a freelancer pay on {m(amount)} a year in Australia (FY{FY})?",
         f"For {m(amount)} taxable income with no deductions, income tax is {a(r['tax'])} plus Medicare {a(r['medicare'])} (combined {a(r['totalTax'])}, effective {p(r['effectiveRate'])})."),
        (f"What is take-home on {m(amount)} after tax and Medicare?",
         f"Estimated take-home is {a(r['takeHome'])} a year, or about {a(r['weeklyTakeHome'])} per week. Super, HELP/HECS, MLS and deductions are not modelled."),
        (f"What contractor day rate equals {m(amount)} at {DAYS} days?",
         f"At {DAYS} days, {m(amount)} GST exclusive is about {a2(r['dayEx'])}/day ex GST, or {a2(r['dayIncl'])} including GST."),
        (f"Does this {m(amount)} figure include GST?",
         f"This preset treats {m(amount)} as GST-exclusive annual contractor revenue. GST on the inc-GST equivalent would be {a(r['annualGst'])}. Employee salaries never include GST — leave the toggle on exclusive for a salary-like comparison."),
        (f"Is the Medicare levy charged on {m(amount)}?",
         f"Yes in this estimate: above the FY{FY} shade-out of ${hi:,}, so Medicare is 2% = {a(r['medicare'])}."),
    ]


def answer(mode, amount, r, example):
    m, a, a2 = T.money, T.fmt_aud, T.fmt_aud2
    if example:
        return (f"Example (not a quote): a {m(amount)} GST-exclusive day rate over {DAYS} billable days is {a(r['annualEx'])} a year before tax. For an Australian resident in FY{FY}, estimated income tax is {a(r['tax'])} and the Medicare levy is {a(r['medicare'])} (2% after the low-income shade). That leaves take-home of about {a(r['takeHome'])}, or {a(r['weeklyTakeHome'])} per week. Change the inputs for your own rate. Super, HELP/HECS, MLS and deductions are not modelled. This is an estimate only — confirm with the ATO or a registered tax agent.")
    if mode == "day":
        return (f"A {m(amount)} GST-exclusive contractor day rate over {DAYS} billable days is {a(r['annualEx'])} a year before tax (about {a(r['annualIncl'])} including 10% GST). For an Australian resident in FY{FY}, estimated income tax is {a(r['tax'])} and the Medicare levy is {a(r['medicare'])} (2% above the shade-out). That leaves take-home of about {a(r['takeHome'])}, or {a(r['weeklyTakeHome'])} per week. Super, HELP/HECS, MLS and deductions are not modelled. Confirm with the ATO or a registered tax agent — this is an estimate only, not advice.")
    return (f"For a freelancer invoicing {m(amount)} a year (GST exclusive), estimated FY{FY} income tax for an Australian resident is {a(r['tax'])}, plus a Medicare levy of {a(r['medicare'])}. Estimated take-home is {a(r['takeHome'])} a year ({a(r['weeklyTakeHome'])} per week). At {DAYS} billable days that is about {a2(r['dayEx'])} per day exclusive of GST ({a2(r['dayIncl'])} including GST). This models contractor revenue, not a PAYG salary: employees also have tax withheld by their employer and super on top. No deductions, HELP, MLS or super are modelled. Estimate only — confirm with the ATO or a registered tax agent before you quote or budget.")


def main():
    meta = json.loads(Path(sys.argv[1]).read_text())
    mode, amount = meta["mode"], float(meta["amount"])
    example = bool(meta.get("example"))
    r = T.calculate(mode, amount, DAYS, False)
    faq = faqs(mode, amount, r, example)
    ld = {"@context": "https://schema.org", "@type": "FAQPage",
          "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}
    faq_html = "\n".join(f"<li><h3>{H.escape(q)}</h3><p>{H.escape(a)}</p></li>" for q, a in faq)
    if example:
        cap, head = f"Example snapshot — {T.money(amount)}/day GST exclusive, {DAYS} days (FY{FY} estimate). Cards above update if you change inputs.", "Quick answer (example)"
    elif mode == "day":
        cap, head = f"Preset snapshot — {T.money(amount)}/day GST exclusive, {DAYS} days (FY{FY} estimate). Cards above update if you change inputs.", "Quick answer"
    else:
        cap, head = f"Preset snapshot — {T.money(amount)} annual GST exclusive, {DAYS} days (FY{FY} estimate). Cards above update if you change inputs.", "Quick answer"
    repl = {
        "__OG_TITLE__": H.escape(meta["title"]), "__OG_DESC__": H.escape(meta["desc"]),
        "__CANONICAL__": H.escape(f"{BASE.rstrip('/')}{meta['path']}"),
        "__CONFIG_JSON__": json.dumps(CFG), "__FAQ_JSON_LD__": json.dumps(ld, ensure_ascii=False, indent=2),
        "__PRESET_MODE__": mode, "__PRESET_AMOUNT__": str(int(amount)), "__PRESET_GST__": "ex",
        "__FY__": FY, "__H1__": H.escape(meta["h1"]), "__INTRO__": H.escape(meta["intro"]),
        "__ANSWER_HEADING__": head, "__ANSWER__": H.escape(answer(mode, amount, r, example)),
        "__AMOUNT_LABEL__": "Day rate (AUD)" if mode == "day" else "Annual contractor revenue (AUD)",
        "__GST_HINT__": ("Is your quoted day rate before GST (exclusive) or including GST?" if mode == "day"
                         else "Enter revenue before GST. Employee salaries have no GST — leave this on exclusive for a salary comparison."),
        "__DAY_BTN__": "active" if mode == "day" else "", "__ANN_BTN__": "active" if mode == "annual" else "",
        "__EX_BTN__": "active", "__INC_BTN__": "", "__DAYS__": str(DAYS),
        "__V_ANNUAL_EX__": T.fmt_aud(r["annualEx"]), "__V_ANNUAL_INC__": T.fmt_aud(r["annualIncl"]),
        "__V_GST__": T.fmt_aud(r["annualGst"]), "__V_DAY_EX__": T.fmt_aud2(r["dayEx"]),
        "__V_DAY_INC__": T.fmt_aud2(r["dayIncl"]), "__V_WEEKLY__": T.fmt_aud(r["weeklyGrossEx"]),
        "__V_TAX__": T.fmt_aud(r["tax"]), "__V_MEDICARE__": T.fmt_aud(r["medicare"]),
        "__V_EFF__": T.fmt_pct(r["effectiveRate"]), "__V_TAKE__": T.fmt_aud(r["takeHome"]),
        "__V_TAKE_WEEK__": T.fmt_aud(r["weeklyTakeHome"]), "__CAPTION__": H.escape(cap),
        "__FORMSPREE__": H.escape(CFG["formspree_endpoint"]), "__PRESETS__": PRESETS,
        "__FAQ_ITEMS__": faq_html, "__SOURCES__": SOURCES, "__LAST_CHECKED__": CFG["last_checked"],
    }
    out = TPL
    for k, v in repl.items():
        out = out.replace(k, v)
    dest = Path(meta["outfile"])
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    print("wrote", dest)

if __name__ == "__main__":
    main()
