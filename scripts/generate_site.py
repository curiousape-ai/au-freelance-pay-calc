#!/usr/bin/env python3
"""Generate AU Freelancer Calc static site with GEO-baked numbers."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

TITLE_RE = re.compile(r"<title>(.*?)</title>", re.I | re.S)


def unique_title_errors(public: Path) -> list[str]:
    seen: dict[str, Path] = {}
    errors: list[str] = []
    for path in sorted(p for p in public.rglob("*.html") if p.is_file()):
        text = path.read_text(encoding="utf-8", errors="ignore")
        match = TITLE_RE.search(text)
        rel = path.relative_to(public)
        if not match:
            errors.append(f"missing <title> in {rel}")
            continue
        title = " ".join(match.group(1).split())
        if not title:
            errors.append(f"empty <title> in {rel}")
            continue
        prior = seen.get(title.lower())
        if prior:
            errors.append(f"duplicate title {title!r} in {rel} and {prior.relative_to(public)}")
            continue
        seen[title.lower()] = path
    return errors

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PUBLIC = ROOT / "public"
EMBED = HERE / "embedded"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--base-url",
        help="Canonical site origin (e.g. https://example.com). "
        "Overrides cfg.json base_url for canonicals/robots/sitemap.",
    )
    args = ap.parse_args()

    env = dict(os.environ)
    if args.base_url:
        env["SITE_BASE_URL"] = args.base_url.rstrip("/")

    cfg = json.loads((HERE / "cfg.json").read_text(encoding="utf-8"))
    end_year = 2000 + int(cfg["default_fy"].split("-")[1])
    stale_after = date(end_year, 7, 1)
    if date.today() > stale_after:
        source = cfg["sources"][0]["url"]
        print(f"ERROR: default_fy {cfg['default_fy']} is stale after {stale_after}. Verify and update rates: {source}")
        return 1

    # Pre-flight: the two tax engines must agree before we bake pages.
    subprocess.check_call([sys.executable, str(HERE / "check_parity.py")], env=env)

    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in ("styles.css", "calc.js", "app.js", "favicon.svg", "og.png"):
        shutil.copy2(EMBED / name, PUBLIC / name)
    (PUBLIC / "config.js").write_text(
        "window.AU_CALC_CONFIG = " + json.dumps(cfg, indent=2) + ";\n",
        encoding="utf-8",
    )
    subprocess.check_call([sys.executable, str(HERE / "make_specs.py")], env=env)
    specs = sorted(Path("/tmp/pages").glob("*.json"))
    for spec in specs:
        subprocess.check_call([sys.executable, str(HERE / "write_page.py"), str(spec)], env=env)
    subprocess.check_call([sys.executable, str(HERE / "write_meta.py")], env=env)

    title_errors = unique_title_errors(PUBLIC)
    if title_errors:
        print("ERROR: page titles must be unique and present:")
        print("\n".join(f"  {err}" for err in title_errors))
        return 1

    # Guard: no template placeholder may survive into the deploy root.
    leftovers = [
        str(p.relative_to(PUBLIC))
        for p in PUBLIC.rglob("*")
        if p.is_file() and "SITE_URL_PLACEHOLDER" in p.read_text(encoding="utf-8", errors="ignore")
    ]
    if leftovers:
        print("ERROR: SITE_URL_PLACEHOLDER survived in:", *leftovers, sep="\n  ")
        sys.exit(1)

    print(f"Generated {len(specs)} calculator pages + 404/presets/methodology + robots/llms/sitemap")
    print(f"Public dir: {PUBLIC}")


if __name__ == "__main__":
    raise SystemExit(main() or 0)
