"""Apercu du plugin (avant code) : fond + lumieres + inverseur + repere du potard + serigraphie vectorielle + barre de presets.
Usage : python3 tools/preview.py sortie.png [on|off] [rate 0..1] [haut|bas] [texte_pastille]"""
import os, sys, json, math, subprocess, io
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
LAY = json.load(open(os.path.join(HERE, 'layout.json')))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'design', 'preview.png')
ON = (sys.argv[2] if len(sys.argv) > 2 else 'on') == 'on'
RATE = float(sys.argv[3]) if len(sys.argv) > 3 else 0.389
DEEP = (sys.argv[4] if len(sys.argv) > 4 else 'bas') == 'bas'
PILL = sys.argv[5] if len(sys.argv) > 5 else 'Grunge Water'
GLOW = float(os.environ.get('GLOW', '1.0'))           # reglage Glow du clic droit (1.0 = 100 %)
K = 2.0                                                     # px par unite du plugin (image 1235 x 1800)
FONTS = {0: 'Poppins-Medium.ttf', 1: 'Poppins-Bold.ttf', 2: 'Poppins-Light.ttf'}

bg = Image.open(os.path.join(ROOT, 'background.png')).convert('RGBA')
canvas = Image.new('RGBA', bg.size, (14, 14, 15, 255)); canvas.alpha_composite(bg)

def paste(fn, rect, op=1.0):
    im = Image.open(os.path.join(ROOT, fn)).convert('RGBA')
    w, h = int(round(rect[2] * K)), int(round(rect[3] * K))
    im = im.resize((w, h), Image.LANCZOS)
    if op < 1: im.putalpha(im.getchannel('A').point(lambda v: int(v * op)))
    canvas.alpha_composite(im, (int(round(rect[0] * K)), int(round(rect[1] * K))))

if ON:
    paste('glow_ring.png', LAY['glowRing'], min(1.0, GLOW)); (paste('glow_ring.png', LAY['glowRing'], GLOW - 1.0) if GLOW > 1.0 else None); paste('ring_core.png', LAY['glowRing']); paste('glow_led.png', LAY['glowLed'])
    l = LAY['led']; paste('led_on.png', (l[0] - l[2] / 2, l[1] - l[2] / 2, l[2], l[2]))
    f_ = LAY['fs']; paste('fs_refl.png', (f_[0] - f_[3] / 2, f_[1] - f_[3] / 2, f_[3], f_[3]), 0.35)
# inverseur
strip = Image.open(os.path.join(ROOT, 'toggle_strip.png')).convert('RGBA')
n = strip.width; fr = strip.crop((0, (2 if DEEP else 0) * n, n, (3 if DEEP else 1) * n))
t = LAY['toggle']; s = int(round(t[2] * K)); fr = fr.resize((s, s), Image.LANCZOS)
canvas.alpha_composite(fr, (int(round(t[0] * K - s / 2)), int(round(t[1] * K - s / 2))))

SS = 3                                                      # sur-echantillonnage du dessin vectoriel
big = Image.new('RGBA', (canvas.width * SS, canvas.height * SS), (0, 0, 0, 0))
d = ImageDraw.Draw(big)
INK = (238, 236, 242, 255)
def spaced(txt, font, em, track, x, y, rot, align, fill=INK, stroke=0, stroke_fill=None):
    f = ImageFont.truetype(os.path.join(ROOT, FONTS[font]), int(em * K * SS))
    ws = [f.getlength(c) for c in txt]; tot = sum(ws) + track * K * SS * (len(txt) - 1)
    if rot:
        lay = Image.new('RGBA', (int(tot) + 20, int(em * K * SS * 1.8)), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        cx = 10
        for c, w in zip(txt, ws): ld.text((cx, lay.height / 2), c, font=f, fill=fill, anchor='lm'); cx += w + track * K * SS
        lay = lay.rotate(rot, expand=True)
        big.alpha_composite(lay, (int(x * K * SS - lay.width / 2), int(y * K * SS - lay.height / 2))); return
    cx = x * K * SS - (tot / 2 if align == 0 else 0)
    for c, w in zip(txt, ws):
        d.text((cx, y * K * SS), c, font=f, fill=fill, anchor='lm', stroke_width=stroke, stroke_fill=stroke_fill); cx += w + track * K * SS
for tx in LAY['texts']:
    s_, font, em, track, x, y, rot, align = tx
    if s_ in ('SMALL', 'TONE'):
        spaced(s_, font, em, track, x, y, rot, align, fill=(244, 242, 250, 255), stroke=int(1.6 * K * SS), stroke_fill=(122, 92, 190, 255))
    elif s_ == 'SYNC':
        spaced(s_, font, em, track, x, y, rot, align, fill=INK if not ON else (232, 238, 255, 255))
    else:
        spaced(s_, font, em, track, x, y, rot, align)
for (x0, y0, x1, y1, w) in LAY['ticks']:
    d.line([(x0 * K * SS, y0 * K * SS), (x1 * K * SS, y1 * K * SS)], fill=(228, 228, 234, 235), width=max(1, int(w * K * SS)))
# repere du potard (trait blanc arrondi)
kx, ky, kr = LAY['knob']; r0, r1, iw = LAY['indexR']
a = math.radians(-135 + 270 * RATE)
p0 = ((kx + r0 * math.sin(a)) * K * SS, (ky - r0 * math.cos(a)) * K * SS); p1 = ((kx + r1 * math.sin(a)) * K * SS, (ky - r1 * math.cos(a)) * K * SS)
d.line([p0, p1], fill=(246, 246, 248, 255), width=int(iw * K * SS))
for p in (p0, p1): d.ellipse((p[0] - iw * K * SS / 2, p[1] - iw * K * SS / 2, p[0] + iw * K * SS / 2, p[1] + iw * K * SS / 2), fill=(246, 246, 248, 255))
# pastille de presets (400 x 38) : face noire, liseré, nom du preset en Poppins Medium 23
px, py, pw, ph = LAY['preset']
d.rounded_rectangle((px * K * SS, py * K * SS, (px + pw) * K * SS, (py + ph) * K * SS), radius=ph / 2 * K * SS, fill=(8, 8, 10, 255), outline=(58, 56, 66, 255), width=int(1.0 * K * SS))
fm = ImageFont.truetype(os.path.join(ROOT, 'Poppins-Medium.ttf'), int(23 * K * SS))
d.text(((px + pw / 2) * K * SS, (py + ph / 2 + 1) * K * SS), PILL, font=fm, fill=(232, 232, 236, 255), anchor='mm')
for sgn in (-1, 1):
    cx = (px + pw / 2 + sgn * (pw / 2 - 17)) * K * SS; cy = (py + ph / 2) * K * SS; r = 5.5 * K * SS
    d.polygon([(cx + sgn * r, cy), (cx - sgn * r * 0.6, cy - r), (cx - sgn * r * 0.6, cy + r)], fill=(150, 150, 156, 255))
if ON:
    fx, fy = LAY['fs'][0], LAY['fs'][1]; rr, rw = LAY['fsRing']
    ov = Image.new('RGBA', big.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    col = (150, 108, 255)
    def ring(width, rgba):
        lay = Image.new('RGBA', big.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        w_ = max(1, int(width * K * SS)); R_ = rr * K * SS
        ld.ellipse((fx * K * SS - R_ - w_ / 2, fy * K * SS - R_ - w_ / 2, fx * K * SS + R_ + w_ / 2, fy * K * SS + R_ + w_ / 2), outline=rgba, width=w_)
        ov.alpha_composite(lay)
    k_ = rr / 33.2
    hw = 20.0                                   # halo du footswitch (encore un peu plus fort, nov. 2026), dose par Glow
    while hw > 3.0:
        ring(hw * k_, col + (int(255 * min(1.0, 0.075 * GLOW)),)); hw -= 1.5
    ring(rw, col + (int(255 * 0.85),))
    ring(rw * 0.42, (214, 198, 255, int(255 * 0.9)))
    big.alpha_composite(ov)
small = big.resize(canvas.size, Image.LANCZOS)
canvas.alpha_composite(small)
# logo NINE HANDS | DSP (SVG officiel)
lx, ly, lw = LAY['logo']
logo = Image.open(os.path.join(ROOT, 'assets', 'nine_hands_logo_blanc.png')).convert('RGBA')
logo = logo.resize((int(lw * K), int(round(logo.height * lw * K / logo.width))), Image.LANCZOS)
canvas.alpha_composite(logo, (int(lx * K - logo.width / 2), int(ly * K - logo.height / 2)))
canvas.save(out)
print(out)
