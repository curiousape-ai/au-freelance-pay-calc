// Reads calc cases as JSON on stdin, prints AUCalc.calculate results as JSON.
// Used by check_parity.py to compare the browser engine against taxlib.py.
const fs = require("fs");
const path = require("path");
const HERE = __dirname;
const window = {
  AU_CALC_CONFIG: JSON.parse(fs.readFileSync(path.join(HERE, "cfg.json"), "utf8")),
};
eval(fs.readFileSync(path.join(HERE, "embedded", "calc.js"), "utf8"));
const cases = JSON.parse(fs.readFileSync(0, "utf8"));
const out = cases.map((c) =>
  c.mode === "solve"
    ? { solved: window.AUCalc.solveDayRateForWeeklyTakeHome(c.amount, c.days, c.deductions) }
    : window.AUCalc.calculate(c)
);
process.stdout.write(JSON.stringify(out));
