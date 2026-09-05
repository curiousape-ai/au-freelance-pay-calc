#!/usr/bin/env python3
"""Generate AU Freelancer Calc static site with GEO-baked numbers."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC = ROOT / "public"
EMBED = HERE / "embedded"


def main():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in ("styles.css", "calc.js", "app.js"):
        shutil.copy2(EMBED / name, PUBLIC / name)
    cfg = json.loads((HERE / "cfg.json").read_text(encoding="utf-8"))
    (PUBLIC / "config.js").write_text(
        "window.AU_CALC_CONFIG = " + json.dumps(cfg, indent=2) + ";\n",
        encoding="utf-8",
    )
    subprocess.check_call([sys.executable, str(HERE / "make_specs.py")])
    specs = sorted(Path("/tmp/pages").glob("*.json"))
    for spec in specs:
        subprocess.check_call([sys.executable, str(HERE / "write_page.py"), str(spec)])
    subprocess.check_call([sys.executable, str(HERE / "write_meta.py")])
    print(f"Generated {len(specs)} HTML pages + robots/llms/sitemap")
    print(f"Public dir: {PUBLIC}")


if __name__ == "__main__":
    main()
