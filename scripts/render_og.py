#!/usr/bin/env python3
"""Dark-studio OG cards. Typography only. No client names."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "og"
OUT.mkdir(parents=True, exist_ok=True)

BG = (10, 10, 10)
INK = (243, 242, 238)
MUTED = (138, 138, 134)
LINE = (44, 44, 44)

FONT_DIR = Path("/usr/share/fonts/truetype/macos")
FONT_MED = FONT_DIR / "Inter-Medium.ttf"
FONT_SEMI = FONT_DIR / "Inter-SemiBold.ttf"


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def draw_tracked(draw: ImageDraw.ImageDraw, text: str, y: int, face, fill, tracking: int, width: int):
    glyphs = list(text)
    widths = [draw.textlength(g, font=face) for g in glyphs]
    total = sum(widths) + tracking * max(0, len(glyphs) - 1)
    x = (width - total) / 2
    for g, w in zip(glyphs, widths):
        draw.text((x, y), g, font=face, fill=fill)
        x += w + tracking


def card(path: Path, title: str, kicker: str | None = None, size=(1600, 900), title_size=72, tracking=10):
    w, h = size
    im = Image.new("RGB", size, BG)
    draw = ImageDraw.Draw(im)
    title_face = font(FONT_SEMI, title_size)
    kicker_face = font(FONT_MED, 22)

    # Measure title to place the stack.
    tmp = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    glyphs = list(title)
    tw = sum(tmp.textlength(g, font=title_face) for g in glyphs) + tracking * max(0, len(glyphs) - 1)
    th = title_face.getbbox("Hg")[3]

    stack_h = th
    if kicker:
        stack_h += 28 + 36
    y = (h - stack_h) / 2 - 8

    if kicker:
        draw_tracked(draw, kicker.upper(), y, kicker_face, MUTED, 6, w)
        y += 36
        line_w = min(120, tw * 0.22)
        draw.rectangle(((w - line_w) / 2, y, (w + line_w) / 2, y + 1), fill=LINE)
        y += 28

    draw_tracked(draw, title, y, title_face, INK, tracking, w)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True)
    print(f"wrote {path.relative_to(ROOT)} {size}")


def header(path: Path):
    """Slim README banner — name, hairline, one English line."""
    w, h = 1600, 420
    im = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(im)
    name = font(FONT_SEMI, 54)
    sub = font(FONT_MED, 18)
    draw_tracked(draw, "PARSA FORUGHI", 156, name, INK, 14, w)
    draw.rectangle((700, 232, 900, 233), fill=LINE)
    draw_tracked(draw, "PRODUCTS", 258, sub, MUTED, 8, w)
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, "PNG", optimize=True)
    print(f"wrote {path.relative_to(ROOT)} {(w, h)}")


def main():
    header(OUT / "header.png")

    card(ROOT / "docs" / "og.png", "PARSA FORUGHI", "Products", title_size=64, tracking=14)
    card(OUT / "profile.png", "PARSA FORUGHI", "Products", title_size=64, tracking=14)

    products = [
        ("reeldrive.png", "REELDRIVE"),
        ("bstory.png", "BSTORY"),
        ("vip.png", "VIP PASSPORT"),
        ("shelftalker.png", "SHELFTALKER"),
        ("pixxel.png", "PIXXEL UV"),
        ("viral.png", "VIRAL"),
        ("affiliate.png", "AFFILIATE"),
        ("resume.png", "RESUME"),
        ("mastermindos.png", "MASTERMIND OS"),
    ]
    for fname, title in products:
        tracking = 8 if len(title) > 10 else 14
        size = 58 if len(title) > 12 else 72
        card(OUT / fname, title, tracking=tracking, title_size=size)


if __name__ == "__main__":
    main()
