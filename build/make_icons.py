# -*- coding: utf-8 -*-
"""Tao bo icon cho app: nen xanh chalkboard, chu 3K."""
import os
from PIL import Image, ImageDraw, ImageFont
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'icons'); os.makedirs(OUT, exist_ok=True)
BG, FG = (31, 111, 92), (255, 255, 255)

def font(size):
    for p in [r'C:\Windows\Fonts\segoeuib.ttf', r'C:\Windows\Fonts\arialbd.ttf',
              r'C:\Windows\Fonts\calibrib.ttf']:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def icon(size, maskable=False):
    im = Image.new('RGB', (size, size), BG)
    d = ImageDraw.Draw(im)
    if not maskable:                      # bo goc tron cho icon thuong
        r = int(size * 0.22)
        mask = Image.new('L', (size, size), 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, size-1, size-1], r, fill=255)
        bg = Image.new('RGB', (size, size), (0, 0, 0))
        im = Image.composite(im, bg, mask)
        d = ImageDraw.Draw(im)
    scale = 0.34 if maskable else 0.44    # maskable phai chua chu trong vung an toan
    f = font(int(size * scale))
    t = '3K'
    box = d.textbbox((0, 0), t, font=f)
    d.text(((size - (box[2]-box[0])) / 2 - box[0],
            (size - (box[3]-box[1])) / 2 - box[1]), t, font=f, fill=FG)
    return im

made = []
for s in (192, 512):
    p = os.path.join(OUT, 'icon-%d.png' % s); icon(s).save(p); made.append(p)
    p = os.path.join(OUT, 'maskable-%d.png' % s); icon(s, True).save(p); made.append(p)
p = os.path.join(OUT, 'apple-touch-icon.png'); icon(180, True).save(p); made.append(p)
for p in made: print('  %-34s %6.1f KB' % (os.path.basename(p), os.path.getsize(p)/1024))
