"""
SMALL TONE (NINE HANDS | DSP) - visuel du plugin, entierement synthetise : pedale simple (refonte nov. 2026).

Design de l'utilisateur (Small Tone Full-Chorus : cadre violet anodise, trois plaques noires, potard RATE noir brosse
entoure d'un anneau lumineux, LED STATUS, inverseur DIN. / DEPTH, footswitch entoure d'un anneau lumineux),
refait selon les regles NINE HANDS | DSP :
  - image du plugin 1235 x 1800 px, pedale plein cadre, fond transparent seulement autour des jacks ;
  - pieces photo du kit (potard, LED, footswitch, inverseur, embases jack) + vis fournie par l'utilisateur ;
  - textes, graduations et logo dessines en vectoriel par le plugin (Poppins, NineHandsLogo.svg) ;
  - une seule lumiere, en haut a gauche (ombres portees vers le bas a droite).
Travail dans un repere 760 x 958 unites (2 px par unite), puis recadrage boitier + jacks -> 1235 x 1800.
Sorties : background.png, glow_led.png, glow_ring.png (anneau du RATE),
led_on.png, fs_refl.png, toggle_strip.png, Layout.h, tools/layout.json, design/preview_art.png
Usage : python3 tools/make_art.py
"""
import os, sys, math, json
import numpy as np, cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import photo_controls as PC
import toggle_photo as TP

AS = 2
UW, UH = 760, 958
W, H = UW * AS, UH * AS
L = np.array([-0.46, -0.62, 0.64]); L /= np.linalg.norm(L)
V = np.array([0.0, 0.0, 1.0]); HV = (L + V) / np.linalg.norm(L + V)

# ------------------------------------------------------------------ geometrie (unites de travail)
OUT_W, OUT_H = 1235, 1800
JACK_LEN = 104.0
JACK_PROT = PC.jack_sprite(JACK_LEN, AS, 1)[1] - 1.5 / AS       # saillie de l'embase hors du boitier
FH = 890.0                                        # hauteur du cadre final : jacks (au-dessus) + boitier
PY0, PR = 34.0 + JACK_PROT, 30.0
PH = FH - JACK_PROT
PW = OUT_W / OUT_H * FH                           # jacks sur le dessus (choix de l'utilisateur) : le boitier touche les bords gauche / droit
PX0 = (UW - PW) / 2
CX = PX0 + PW / 2
CROP_X0, CROP_W = PX0, PW
CROP_Y0 = PY0 - JACK_PROT
SC = (OUT_H / 2.0) / FH
KX = PW / 576.0
def P(y): return PY0 + y

FR = 15.0                                         # largeur du cadre violet visible entre les plaques
PANELS = [(PX0 + FR, P(FR), PW - 2 * FR, 290.0 - FR, 20.0),          # plaque du haut
          (PX0 + FR, P(306.0), PW - 2 * FR, 434.0, 20.0),           # plaque du milieu (nom + footswitch)
          (PX0 + FR, P(755.0), PW - 2 * FR, PH - 755.0 - FR, 20.0)] # plaque du bas (barre de presets + logo)

KNOB = (CX, P(152.0)); KNOB_R = 72.0
RING_R0, RING_R1 = KNOB_R + 5.0, KNOB_R + 11.0     # anneau lumineux autour du potard
TICK_R0, TICK_R1, TICK_R1L = KNOB_R + 21.0, KNOB_R + 31.0, KNOB_R + 35.0
TOG = (CX - 196.0 * KX, P(158.0)); TOG_WR = 25.0
LED = (CX + 186.0 * KX, P(158.0)); LED_LENS = 10.5
FS = (CX, P(648.0) + 8.0 / SC); FS_FLATS = 98.0   # centre entre le pied de FULL-CHORUS et le rebord violet du bas (73 px de chaque cote, image 1800 px)
FS_GROOVE_R, FS_GROOVE_W = 40.0, 2.5             # anneau lumineux dans la gorge du footswitch (comme Octopus)
PRESET = (CX - 198.0, P(770.0), 396.0, 37.6)      # 400 x 38 unites du plugin (regle Strong Pickle)
LOGO_C = (CX, P(834.0)); LOGO_W = 190.0
JACK_X = (CX - 196.0 * KX, CX + 190.0 * KX)       # jacks sur le dessus : OUTPUT a gauche, INPUT a droite (au-dessus des inscriptions)
SCREWS = [(TOG[0], P(72.0)), (TOG[0], P(256.0)), (LED[0] + 4.0, P(72.0)), (LED[0] + 4.0, P(256.0)),
          (PX0 + 50.0, P(706.0)), (PX0 + PW - 50.0, P(706.0))]
SCREW_R = 9.5

# ------------------------------------------------------------------ outils
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
UX, UY = (XX + 0.5) / AS, (YY + 0.5) / AS

def rrect_sd(x, y, x0, y0, w, h, r):
    cx, cy = x0 + w / 2, y0 + h / 2
    qx = np.abs(x - cx) - (w / 2 - r); qy = np.abs(y - cy) - (h / 2 - r)
    return np.hypot(np.maximum(qx, 0), np.maximum(qy, 0)) + np.minimum(np.maximum(qx, qy), 0) - r

def fbm(shape, scales, amps, seed=0):
    r = np.random.default_rng(seed); out = np.zeros(shape, np.float32)
    for s, a in zip(scales, amps):
        n = r.standard_normal((max(2, shape[0] // s + 2), max(2, shape[1] // s + 2))).astype(np.float32)
        out += a * cv2.resize(n, (shape[1], shape[0]), interpolation=cv2.INTER_CUBIC)
    return out

def over(dst, rgba, x0, y0):
    h, w = rgba.shape[:2]
    X0, Y0 = int(round(x0)), int(round(y0))
    sx0, sy0 = max(0, -X0), max(0, -Y0)
    ex, ey = min(w, dst.shape[1] - X0), min(h, dst.shape[0] - Y0)
    a = rgba[sy0:ey, sx0:ex, 3:4] / 255.0
    reg = dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex]
    dst[Y0 + sy0:Y0 + ey, X0 + sx0:X0 + ex] = reg * (1 - a) + rgba[sy0:ey, sx0:ex, :3] * a

def ring_mask(c, r0, r1):
    d = np.hypot(UX - c[0], UY - c[1])
    return np.clip((d - r0) * AS + 0.5, 0, 1) * np.clip((r1 - d) * AS + 0.5, 0, 1)

def disc(c, r):
    return np.clip((r - np.hypot(UX - c[0], UY - c[1])) * AS + 0.5, 0, 1)

# ------------------------------------------------------------------ 1. boitier : aluminium anodise violet, arete arrondie
print('boitier...')
sd = rrect_sd(UX, UY, PX0, PY0, PW, PH, PR)
body = np.clip(0.5 - sd * AS, 0, 1)
EDGE = 9.0
d_in = np.clip(-sd, 0, None)
hgt = np.where(d_in < EDGE, np.sqrt(np.clip(EDGE ** 2 - (EDGE - d_in) ** 2, 0, None)), EDGE)
gy, gx = np.gradient(cv2.GaussianBlur(hgt, (0, 0), 1.0), 1.0 / AS)
nrm = np.dstack([-gx, -gy, np.ones_like(hgt)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
ndl = np.clip(nrm @ L, 0, 1); ndh = np.clip(nrm @ HV, 0, 1)
anod = np.array([96.0, 64.0, 146.0])                       # violet anodise (mesure sur le visuel de l'utilisateur)
img = anod * (0.46 + 0.80 * ndl)[..., None] + (64 * ndh ** 36 + 16 * ndh ** 6)[..., None] * np.array([0.92, 0.86, 1.0])
# anodisation satinee + grain fin (demande de l'utilisateur, nov. 2026 : version lisse avec un peu de grain) :
# grain au pixel et a 2 px, un peu plus visible dans la lumiere et sur l'arete, + legere marbrure tres basse frequence
sheen = np.exp(-(((UX - 260) / 320) ** 2 + ((UY - 220) / 380) ** 2))
fine = fbm((H, W), [1, 2], [3.2, 1.7], 3)
img += (fine * (0.75 + 0.5 * sheen + 0.6 * ndh ** 8))[..., None] * np.array([0.85, 0.7, 1.0])
img += (0.8 * fbm((H, W), [60, 220], [0.8, 1.0], 4))[..., None] * np.array([0.8, 0.6, 1.0])
img += (20.0 * sheen)[..., None] * np.array([0.75, 0.6, 1.0])
img *= (1.0 - 0.10 * np.clip((UY - PY0) / PH, 0, 1))[..., None]          # un peu plus sombre vers le bas
img *= body[..., None]

# ------------------------------------------------------------------ 2. plaques noires (encastrees, coins arrondis)
print('plaques...')
for (x0, y0, w, h, r) in PANELS:
    psd = rrect_sd(UX, UY, x0, y0, w, h, r)
    pm = np.clip(0.5 - psd * AS, 0, 1)
    # ombre interne de l'encastrement (bord haut / gauche) et liseré clair (bord bas / droit)
    inner = np.clip(-psd, 0, None)
    sh_in = np.exp(-inner / 2.2) * np.clip(-(UX - (x0 + w / 2)) / w - (UY - (y0 + h / 2)) / h + 0.6, 0, 1.2)
    hl_in = np.exp(-inner / 1.1) * np.clip((UX - (x0 + w / 2)) / w + (UY - (y0 + h / 2)) / h + 0.2, 0, 1)
    tex = 15.0 + fbm((H, W), [1, 3], [1.4, 0.8], 7) + 2.5 * fbm((H, W), [80, 240], [0.6, 0.8], 8)
    lit = 1.0 + 0.22 * np.exp(-(((UX - 250) / 300) ** 2 + ((UY - 180) / 360) ** 2))
    pcol = (tex * lit)[..., None] * np.array([0.98, 0.98, 1.04])
    pcol *= (1 - 0.55 * np.clip(sh_in, 0, 1))[..., None]
    pcol += (34.0 * np.clip(hl_in, 0, 1))[..., None] * np.array([0.85, 0.75, 1.0])
    # fin chanfrein du cadre violet autour de la plaque : la lumiere accroche le bord bas / droit de l'ouverture
    rim = np.clip(1 - np.abs(psd + 0.2) / 1.2, 0, 1)
    img = img * (1 - pm[..., None]) + pcol * pm[..., None]
    img += (rim * np.clip((UX - (x0 + w / 2)) / w + (UY - (y0 + h / 2)) / h + 0.4, 0, 1) * 30.0)[..., None] * np.array([0.8, 0.7, 1.0])
img *= body[..., None]

# ------------------------------------------------------------------ 3. anneaux lumineux (acrylique fume, eteints)
def smoky_ring(c, r0, r1):
    m = ring_mask(c, r0, r1)
    d = np.hypot(UX - c[0], UY - c[1])
    t = np.clip((d - r0) / (r1 - r0), 0, 1)
    ang = np.arctan2(UY - c[1], UX - c[0])
    toward = np.cos(ang - math.atan2(L[1], L[0]))               # face tournee vers la lumiere
    col = 20.0 + 10.0 * np.sin(t * math.pi) + 8.0 * np.clip(toward, 0, 1) * (1 - t)
    rc = col[..., None] * np.array([0.92, 0.88, 1.08])
    # fine arete brillante sur le bord interieur cote lumiere, sombre cote ombre
    edge = np.exp(-np.abs(d - r0 - 0.6) / 0.5)
    rc += (edge * np.clip(toward, 0, 1) * 55.0)[..., None] * np.array([0.9, 0.85, 1.0])
    global img
    img = img * (1 - m[..., None]) + rc * m[..., None]
    return m
RING_M = smoky_ring(KNOB, RING_R0, RING_R1)

# ------------------------------------------------------------------ 4. occlusion + pieces photo
print('pieces photo...')
def occlusion(mask, strength=1.0, wide=14.0):
    contact = cv2.GaussianBlur(mask, (0, 0), 3.0 * AS)
    soft = cv2.GaussianBlur(mask, (0, 0), wide * AS)
    o = np.clip(contact * 0.55 + soft * 0.9, 0, 0.5) * strength * (1.0 - mask)
    img[...] = img * (1.0 - o * body)[..., None]
_m = disc(KNOB, KNOB_R)
_m = np.maximum(_m, disc(LED, LED_LENS * 1.07) * 0.6)
_m = np.maximum(_m, disc(TOG, TOG_WR) * 0.8)
_fs_tmp = PC.footswitch_sprite(FS_FLATS, AS)[0]
_fa = np.zeros((H, W), np.float32); _n = _fs_tmp.shape[0]
_x0 = int(round((FS[0] - _n / AS / 2) * AS)); _y0 = int(round((FS[1] - _n / AS / 2) * AS))
_fa[_y0:_y0 + _n, _x0:_x0 + _n] = np.clip((_fs_tmp[..., 3] / 255.0 - 0.86) / 0.14, 0, 1)
_m = np.maximum(_m, _fa)
for s in SCREWS: _m = np.maximum(_m, disc(s, SCREW_R) * 0.5)
occlusion(_m)

KN, KS = PC.knob_sprite(KNOB_R, AS)
over(img, KN, (KNOB[0] - KS / 2) * AS, (KNOB[1] - KS / 2) * AS)

LD, LDON, LS = PC.led_sprites(LED_LENS, AS, colour='blue')
over(img, LD, (LED[0] - LS / 2) * AS, (LED[1] - LS / 2) * AS)
Image.fromarray(np.clip(LDON, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'led_on.png'))

FSPR, FSREFL, FS_W, FS_BTN = PC.footswitch_sprite(FS_FLATS, AS, refl_colour=(170.0, 120.0, 255.0))
over(img, FSPR, (FS[0] - FS_W / 2) * AS, (FS[1] - FS_W / 2) * AS)
Image.fromarray(FSREFL, 'RGBA').save(os.path.join(ROOT, 'fs_refl.png'))

# vis (photo fournie par l'utilisateur : tete noire a six pans creux) : detouree sur son cercle, ombre portee
def screw_sprite(R_units):
    src = np.asarray(Image.open(os.path.join(ROOT, 'assets', 'kit', 'screw_photo.png')).convert('RGB')).astype(np.float32)
    g = src.mean(2)
    m = (g < 120).astype(np.uint8)
    cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    (cx, cy), r = cv2.minEnclosingCircle(max(cnts, key=cv2.contourArea))
    r -= 1.5
    n = int(round(R_units * 2 * 1.6 * AS)); k = R_units * AS / r
    M = np.float32([[k, 0, n / 2 - k * cx], [0, k, n / 2 - k * cy]])
    rgb = cv2.warpAffine(src, M, (n, n), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_REPLICATE)
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    a = np.clip((R_units * AS - np.hypot(xx - n / 2 + 0.5, yy - n / 2 + 0.5)) + 0.5, 0, 1)
    rgb = rgb * 0.95 + 4.0                           # accordee au noir des plaques
    sh = cv2.GaussianBlur(np.roll(np.roll(a, int(0.22 * R_units * AS), 0), int(0.15 * R_units * AS), 1), (0, 0), 0.25 * R_units * AS)
    return rgb, a, sh, n
SRGB, SA, SSH, SN = screw_sprite(SCREW_R)
for (sx, sy) in SCREWS:
    x0, y0 = int(round(sx * AS - SN / 2)), int(round(sy * AS - SN / 2))
    reg = img[y0:y0 + SN, x0:x0 + SN]
    reg *= (1 - 0.6 * SSH * (1 - SA))[..., None]
    img[y0:y0 + SN, x0:x0 + SN] = reg * (1 - SA[..., None]) + SRGB * SA[..., None]

# inverseur : trois images superposees (haut / milieu / bas), dessinees par le plugin
TOG_S = TOG_WR * 3.6
AS_T = 4
tf = TP.aligned_frames(TOG_WR, TOG_S, AS_T)
Image.fromarray(np.concatenate(tf, 0), 'RGBA').save(os.path.join(ROOT, 'toggle_strip.png'), optimize=True)

# ------------------------------------------------------------------ 5. embases jack (photo du kit) sur le DESSUS : OUTPUT a gauche, INPUT a droite
#     la photo a deja la rondelle vers l'exterieur (en haut) et la face coupee contre le boitier (en bas) : aucune rotation
alpha = body.copy()
def top_jack(length_units):
    im = PC._load('jack_photo.png'); x0, x1, y0, y1 = PC.JACK_BOX
    crop = im[y0:y1, x0:x1].copy()
    k = length_units * AS / crop.shape[1]
    n_w, n_h = int(round(crop.shape[1] * k)), int(round(crop.shape[0] * k))
    pm = crop.copy(); pm[..., :3] *= pm[..., 3:4] / 255.0
    sm = cv2.resize(pm, (n_w, n_h), interpolation=cv2.INTER_AREA)
    a = np.clip(sm[..., 3] / 255.0, 0, 1)
    rgb = np.where(a[..., None] > 1e-4, sm[..., :3] / np.maximum(a, 1e-4)[..., None], 0)
    rgb = np.clip(rgb * np.linspace(1.06, 0.90, n_w)[None, :, None], 0, 255)      # lumiere en haut a gauche
    return np.dstack([rgb, a * 255]).astype(np.float32)
J = top_jack(JACK_LEN)
jh, jw = J.shape[:2]
for jx in JACK_X:
    x0 = int(round(jx * AS - jw / 2)); y0 = int(round(PY0 * AS + 1.5 - jh))
    over(img, J, x0, y0)
    ja = np.zeros((H, W), np.float32); ja[y0:y0 + jh, x0:x0 + jw] = J[..., 3] / 255.0
    alpha = np.maximum(alpha, ja)

# ------------------------------------------------------------------ 6. sauvegarde du fond 1235 x 1800
def to_out(a):
    x0, x1 = CROP_X0 * AS, (CROP_X0 + CROP_W) * AS
    y0, y1 = CROP_Y0 * AS, (PY0 + PH) * AS
    M = np.float32([[OUT_W / (x1 - x0), 0, -x0 * OUT_W / (x1 - x0)], [0, OUT_H / (y1 - y0), -y0 * OUT_H / (y1 - y0)]])
    return cv2.warpAffine(a, M, (OUT_W, OUT_H), flags=cv2.INTER_AREA if OUT_H < (y1 - y0) else cv2.INTER_CUBIC)
out_rgb = np.clip(to_out(img), 0, 255); out_a = np.clip(to_out(alpha), 0, 1)
Image.fromarray(np.dstack([out_rgb, out_a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'background.png'), optimize=True)

# ------------------------------------------------------------------ 7. calques de lumiere (alpha = seule la lumiere ajoutee)
def light_layer(src_mask, col, emit_col, gr, c, fn, fn_core, k1=1.0, k2=0.18, s1=4.0, s2=22.0, strength=1.0):
    """facade eclairee par une source etendue (src_mask) : tache serree + diffusion large.
    Deux calques alpha (seule la lumiere ajoutee) : fn = halo sur la facade (dose par le reglage Glow du clic droit),
    fn_core = la source elle-meme (anneau allume : coeur presque blanc, bords colores), jamais dosee."""
    x0p, y0p = int(round((c[0] - gr) * AS)), int(round((c[1] - gr) * AS)); size = int(round(2 * gr * AS))
    reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    sm = src_mask[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
    E = k1 * cv2.GaussianBlur(sm, (0, 0), s1 * AS) * 6.0 + k2 * cv2.GaussianBlur(sm, (0, 0), s2 * AS) * 6.0
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    d = np.hypot((xx + 0.5) / AS - gr, (yy + 0.5) / AS - gr)
    E *= np.clip((gr - d) / 24.0, 0, 1) * strength
    lum = reg.mean(2, keepdims=True)
    core = np.clip(sm * 1.4, 0, 1)[..., None]
    lit = reg + (reg * 2.2 + 12.0 * np.clip(lum / 40.0, 0.3, 1.6)) * E[..., None] * np.array(col)
    def save(add, f):
        a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
        rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
        Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, f))
    save((lit - reg) * (1 - core), fn)                       # halo seul (hors de l'anneau)
    hot = np.clip((sm - 0.55) / 0.45, 0, 1)[..., None] ** 1.5
    emit = np.array(col) * 255.0 * 0.92 * (1 - hot) + np.array(emit_col) * hot
    cr = np.dstack([emit, np.clip(sm * 1.4, 0, 1) * 255])     # anneau allume seul
    cr = np.where(cr[..., 3:4] > 0, cr, 0)
    Image.fromarray(np.clip(cr, 0, 255).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, fn_core))
    return (x0p / AS, y0p / AS, size / AS, size / AS)

def ring_emitter(c, r0, r1):
    d = np.hypot(UX - c[0], UY - c[1]); t = np.clip((d - r0) / (r1 - r0), 0, 1)
    return ring_mask(c, r0, r1) * (0.35 + 0.65 * np.clip(np.sin(t * math.pi), 0, 1) ** 1.5)
print('lumieres...')
VIOLET = [0.62, 0.42, 1.0]
RING_EM = ring_emitter(KNOB, RING_R0, RING_R1)
GL_RING = light_layer(RING_EM, VIOLET, [246, 240, 255], KNOB_R + 86, KNOB, 'glow_ring.png', 'ring_core.png', k1=1.5, k2=0.45)   # halo un peu plus fort (nov. 2026)
# LED bleue : petite source au-dessus de la facade (loi cos / d^2)
GR = 90.0
x0p, y0p = int(round((LED[0] - GR) * AS)), int(round((LED[1] - GR) * AS)); size = int(round(2 * GR * AS))
reg = img[y0p:y0p + size, x0p:x0p + size].astype(np.float64)
yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
d = np.hypot((xx + 0.5) / AS - GR, (yy + 0.5) / AS - GR)
h1, h2 = 7.0, 26.0
E = 1.1 * h1 ** 3 / (d ** 2 + h1 ** 2) ** 1.5 + 0.176 * h2 ** 3 / (d ** 2 + h2 ** 2) ** 1.5
E *= np.clip((GR - d) / 26.0, 0, 1); E[d < LED_LENS * 1.07] = 0
lum = reg.mean(2, keepdims=True)
lit = reg + (reg * 2.2 + 12.0 * np.clip(lum / 40.0, 0.3, 1.6)) * E[..., None] * np.array([0.25, 0.45, 1.0])
add = lit - reg; a = np.clip(np.abs(add).max(-1) / 12.0, 0, 1)
rgb = np.where(a[..., None] > 1e-3, reg + add / np.maximum(a, 1e-3)[..., None], reg)
Image.fromarray(np.dstack([np.clip(rgb, 0, 255), a * 255]).astype(np.uint8), 'RGBA').save(os.path.join(ROOT, 'glow_led.png'))
GL_LED = (x0p / AS, y0p / AS, size / AS, size / AS)

# ------------------------------------------------------------------ 8. Layout.h (repere du plugin 617,5 x 900)
def f(v): return f"{v:.2f}f"
def X(v): return (v - CROP_X0) * SC
def Y(v): return (v - CROP_Y0) * SC
def PT(p): return "{ %s, %s }" % (f(X(p[0])), f(Y(p[1])))
def RC(r): return "{ %s, %s, %s, %s }" % (f(X(r[0])), f(Y(r[1])), f(r[2] * SC), f(r[3] * SC))

# serigraphie vectorielle (dessinee par le plugin) : texte, police (0 medium, 1 bold, 2 light, 3 semibold-like bold), taille, espacement, centre, rotation
TX = []
def T(s, font, em, track, x, y, rot=0.0, align=0): TX.append((s, font, em, track, x, y, rot, align))
T('DIN.', 1, 15.0, 1.6, TOG[0], P(104.0))
T('DEPTH', 1, 17.0, 1.8, TOG[0], P(220.0))
T('RATE', 1, 19.0, 2.4, KNOB[0], P(272.0))
T('STATUS', 1, 17.0, 1.8, LED[0] + 4.0, P(214.0))
T('SYNC', 1, 13.5, 1.6, LED[0] + LED_LENS + 9.0, LED[1], 0.0, 1)       # aligne a gauche, a droite de la LED
T('SMALL', 1, 92.0, 2.0, CX, P(418.0))
T('TONE', 1, 92.0, 2.0, CX, P(505.0))
T('FULL-CHORUS', 2, 26.0, 2.6, CX, P(562.0))
T('OUTPUT', 1, 17.0, 1.8, JACK_X[0], P(40.0))
T('INPUT', 1, 17.0, 1.8, JACK_X[1], P(40.0))
TICKS = []
for i in range(31):
    a = math.radians(-135 + 9 * i)
    major = (i % 5 == 0)
    r1 = TICK_R1L if major else TICK_R1
    TICKS.append((KNOB[0] + TICK_R0 * math.sin(a), KNOB[1] - TICK_R0 * math.cos(a), KNOB[0] + r1 * math.sin(a), KNOB[1] - r1 * math.cos(a), 3.4 if major else 2.4))

LAY = {"frame": [OUT_W / 2, OUT_H / 2], "knob": [X(KNOB[0]), Y(KNOB[1]), KNOB_R * SC], "led": [X(LED[0]), Y(LED[1]), LS * SC],
       "fs": [X(FS[0]), Y(FS[1]), FS_BTN * SC, FS_W * SC], "toggle": [X(TOG[0]), Y(TOG[1]), TOG_S * SC],
       "preset": [X(PRESET[0]), Y(PRESET[1]), PRESET[2] * SC, PRESET[3] * SC], "logo": [X(LOGO_C[0]), Y(LOGO_C[1]), LOGO_W * SC],
       "glowRing": [X(GL_RING[0]), Y(GL_RING[1]), GL_RING[2] * SC, GL_RING[3] * SC],
       "fsRing": [FS_GROOVE_R * SC, FS_GROOVE_W * SC],
       "glowLed": [X(GL_LED[0]), Y(GL_LED[1]), GL_LED[2] * SC, GL_LED[3] * SC],
       "box": [X(PX0), Y(PY0), PW * SC, PH * SC], "jacks": [X(JACK_X[0]), X(JACK_X[1])],
       "texts": [[t[0], t[1], t[2] * SC, t[3] * SC, X(t[4]), Y(t[5]), t[6], t[7]] for t in TX],
       "ticks": [[X(t[0]), Y(t[1]), X(t[2]), Y(t[3]), t[4] * SC] for t in TICKS],
       "indexR": [0.30 * KNOB_R * SC, 0.92 * KNOB_R * SC, 0.075 * KNOB_R * SC]}
json.dump(LAY, open(os.path.join(ROOT, 'tools', 'layout.json'), 'w'), indent=1)
with open(os.path.join(ROOT, 'Layout.h'), 'w') as fo:
    fo.write(f"// genere par tools/make_art.py - ne pas modifier a la main (repere {OUT_W / 2} x {OUT_H / 2} = fond {OUT_W} x {OUT_H} px / 2)\n")
    fo.write("#pragma once\n#include <juce_graphics/juce_graphics.h>\nnamespace layout\n{\n")
    fo.write(f"    constexpr float frameW = {f(OUT_W / 2)}, frameH = {f(OUT_H / 2)};\n")
    fo.write(f"    const juce::Point<float> knobPos {PT(KNOB)}; const float knobR = {f(KNOB_R * SC)};\n")
    fo.write(f"    const float indexR0 = {f(LAY['indexR'][0])}, indexR1 = {f(LAY['indexR'][1])}, indexW = {f(LAY['indexR'][2])};   // repere blanc du potard\n")
    fo.write(f"    const juce::Point<float> ledPos {PT(LED)}; const float ledS = {f(LS * SC)};\n")
    fo.write(f"    const juce::Point<float> fsPos {PT(FS)}; const float footR = {f(FS_BTN * SC)}, fsS = {f(FS_W * SC)};\n")
    fo.write(f"    const juce::Point<float> togglePos {PT(TOG)}; const float toggleS = {f(TOG_S * SC)};\n")
    fo.write(f"    const juce::Rectangle<float> glowRing {RC(GL_RING)}, glowLed {RC(GL_LED)};\n")
    fo.write(f"    const float fsRingR = {f(FS_GROOVE_R * SC)}, fsRingW = {f(FS_GROOVE_W * SC)};   // anneau lumineux dans la gorge du footswitch (dessin d'Octopus)\n")
    fo.write(f"    const juce::Rectangle<float> presetRect {RC(PRESET)};   // pastille unique : barre de presets / ligne d'etat\n")
    fo.write(f"    const float presetFont = 23.0f;\n")
    fo.write(f"    const juce::Rectangle<float> boxRect {RC((PX0, PY0, PW, PH))};\n")
    fo.write("    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, x, y, rotation, alignement (0 centre, 1 gauche)\n")
    fo.write("    struct Txt { const char* s; int font; float em, track, x, y, rot; int align; };\n")
    fo.write("    const Txt texts[] = {\n" + ",\n".join(f'        {{ "{t[0]}", {t[1]}, {f(t[2] * SC)}, {f(t[3] * SC)}, {f(X(t[4]))}, {f(Y(t[5]))}, {f(t[6])}, {t[7]} }}' for t in TX) + "\n    };\n")
    fo.write("    struct Tick { float x0, y0, x1, y1, w; };\n")
    fo.write("    const Tick ticks[] = { " + ", ".join(f"{{ {f(X(t[0]))}, {f(Y(t[1]))}, {f(X(t[2]))}, {f(Y(t[3]))}, {f(t[4] * SC)} }}" for t in TICKS) + " };\n")
    fo.write(f"    const juce::Point<float> logoPos {PT(LOGO_C)}; const float logoW = {f(LOGO_W * SC)};\n")
    fo.write("}\n")
print('ok')
