#!/usr/bin/env python3
"""Render the static og:image (1200x630 PNG) into scripts/embedded/og.png."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "embedded" / "og.png"
W, H = 1200, 630
BG = (11, 18, 32)       # --bg
ACCENT = (61, 214, 198)  # --accent
TEXT = (232, 238, 249)   # --text
MUTED = (154, 171, 196)  # --muted
BLUE = (91, 140, 255)    # --accent2

FONT = "/System/Library/Fonts/Helvetica.ttc"

def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=1 if bold else 0)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# subtle accent bar
d.rectangle([0, H - 12, W, H], fill=ACCENT)

d.text((80, 90), "AU FREELANCER CALC", font=font(40, bold=True), fill=ACCENT)
d.text((80, 200), "Day rate to annual to take-home", font=font(64, bold=True), fill=TEXT)
d.text((80, 320), "$800/day ≈ $126,022 take-home (FY2025-26)", font=font(44), fill=BLUE)
d.text((80, 430), "ATO brackets + Medicare · GST in/ex · estimate only", font=font(34), fill=MUTED)

img.save(OUT)
print("wrote", OUT)
