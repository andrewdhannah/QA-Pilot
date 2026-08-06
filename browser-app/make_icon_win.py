#!/usr/bin/env python3
"""
make_icon_win.py — generates qa_pilot.ico for the Windows shortcut
───────────────────────────────────────────────────────────────────
Called by setup_launcher.ps1. Can also be run standalone:
    python make_icon_win.py

Requires: Pillow  (pip install pillow)

Pillow can write multi-resolution .ico files directly — no extra
tools needed on Windows (unlike macOS which needs iconutil).
"""

import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("❌  Pillow not found. Install it with:  pip install pillow")
    sys.exit(1)

# ── Paths ────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ICO_OUT    = os.path.join(SCRIPT_DIR, "qa_pilot.ico")

# ── Design constants (same palette as Mac icon + CSS theme) ──
BG_COLOR     = (15,  30,  60)   # deep navy
ACCENT_COLOR = (0,  136, 255)   # bright blue  (--primary)
TEXT_COLOR   = (255, 255, 255)  # white

# Windows .ico requires these specific sizes
ICO_SIZES = [16, 32, 48, 64, 128, 256]


def draw_icon(size: int) -> Image.Image:
    """Draw the QA Pilot icon at 'size' × 'size' pixels."""
    img  = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    pad  = max(size // 10, 1)

    # ── Background: rounded rectangle ───────────────────────
    radius = max(size // 5, 2)
    draw.rounded_rectangle(
        [(pad, pad), (size - pad, size - pad)],
        radius=radius,
        fill=BG_COLOR,
    )

    # ── Airplane silhouette (scaled from 100×100 grid) ───────
    def pt(x, y):
        usable = size - 2 * pad
        return (pad + x / 100 * usable, pad + y / 100 * usable)

    fuselage = [
        pt(20, 78), pt(48, 50), pt(58, 40), pt(72, 28),
        pt(78, 22), pt(82, 20),
        pt(80, 26), pt(68, 34), pt(56, 46), pt(52, 52),
        pt(24, 80),
    ]
    wing = [
        pt(52, 52), pt(56, 46), pt(38, 62), pt(14, 74),
        pt(12, 80), pt(38, 70),
    ]
    tail = [
        pt(24, 80), pt(28, 68), pt(36, 72), pt(34, 82),
    ]

    draw.polygon(fuselage, fill=ACCENT_COLOR)
    draw.polygon(wing,     fill=ACCENT_COLOR)
    draw.polygon(tail,     fill=TEXT_COLOR)

    # ── "QA" text badge (skip at very small sizes — too cramped) ──
    if size >= 48:
        font_size = max(size // 6, 8)
        font = None
        # Try common Windows system fonts
        for font_path in [
            r"C:\Windows\Fonts\arial.ttf",
            r"C:\Windows\Fonts\segoeui.ttf",
            r"C:\Windows\Fonts\verdana.ttf",
        ]:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except Exception:
                    continue

        if font is None:
            font = ImageFont.load_default()

        label = "QA"
        bbox  = draw.textbbox((0, 0), label, font=font)
        tw    = bbox[2] - bbox[0]
        th    = bbox[3] - bbox[1]
        tx    = size - pad - tw - max(size // 14, 1)
        ty    = size - pad - th - max(size // 14, 1)
        draw.text((tx, ty), label, fill=TEXT_COLOR, font=font)

    return img


# ── Generate all sizes ───────────────────────────────────────
print("🎨  Drawing icon frames...")
frames = []
for px in ICO_SIZES:
    img = draw_icon(px)
    frames.append(img)
    print(f"    ✓  {px}×{px}px")

# ── Save as multi-resolution .ico ───────────────────────────
# Pillow saves all frames into a single .ico with a directory
# entry per size — exactly what Windows Explorer expects.
print(f"\n💾  Saving {ICO_OUT}...")
frames[0].save(
    ICO_OUT,
    format="ICO",
    sizes=[(f.width, f.height) for f in frames],
    append_images=frames[1:],
)

print(f"\n✅  Done!  {ICO_OUT}")
