#!/usr/bin/env python3
"""Erzeugt Titelbilder für Blogartikel: große Nummer, Kicker, Wortmarke.

    python3 cover.py --nummer 06 --farbe "#8a2f52" --kicker "MEIN WEG · TEIL 6" \
                     --out bilder/06-cover.jpg

Warum das Skript und nicht Photoshop: Die Cover sollen alle gleich aussehen.
Zwölf von Hand gebaute Bilder driften auseinander, ein Skript nicht.
"""
import argparse
from PIL import Image, ImageDraw, ImageFont

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"

W, H = 1200, 630


def raster(draw, schritt=40, alpha=24):
    """Punktraster wie auf der Website."""
    for x in range(0, W, schritt):
        draw.line([(x, 0), (x, H)], fill=(255, 255, 255, alpha))
    for y in range(0, H, schritt):
        draw.line([(0, y), (W, y)], fill=(255, 255, 255, alpha))


def baue(nummer, farbe, kicker, wortmarke, out):
    img = Image.new("RGB", (W, H), farbe)
    gitter = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    raster(ImageDraw.Draw(gitter))
    img = Image.alpha_composite(img.convert("RGBA"), gitter).convert("RGB")

    d = ImageDraw.Draw(img)
    d.text((72, 66), kicker.upper(), font=ImageFont.truetype(MONO, 20), fill=(255, 255, 255, 205))
    d.text((66, 150), nummer, font=ImageFont.truetype(SERIF, 180), fill=(255, 255, 255, 235))
    d.rectangle([72, 470, 196, 475], fill="#ffffff")
    d.text((72, 506), wortmarke, font=ImageFont.truetype(MONO, 19), fill=(255, 255, 255, 175))

    img.save(out, quality=95)
    return out


def main():
    p = argparse.ArgumentParser(description="Blog-Cover erzeugen")
    p.add_argument("--nummer", required=True, help="große Zahl im Bild, z. B. 06")
    p.add_argument("--farbe", default="#5b46e0", help="Hintergrundfarbe als Hex")
    p.add_argument("--kicker", default="KISIUM · MEIN WEG", help="kleine Zeile oben")
    p.add_argument("--wortmarke", default="kisium.de")
    p.add_argument("--out", default="cover.jpg")
    a = p.parse_args()
    print(baue(a.nummer, a.farbe, a.kicker, a.wortmarke, a.out))


if __name__ == "__main__":
    main()
