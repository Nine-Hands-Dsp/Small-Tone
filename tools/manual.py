# SMALL TONE (NINE HANDS | DSP) - notice PDF en francais, illustree avec le rendu reel du plugin (tools/render).
# Usage : python3 tools/manual.py [<dossier des captures (tools/render)>] <fichier PDF de sortie>
#   avec captures : recompose les images et les copie dans tools/manual_assets/ ;
#   sans captures : reprend les images composees de tools/manual_assets/.
# Version lue dans CMakeLists.txt. Couverture « minimale » (gabarit fixe commun a toutes les notices NINE HANDS | DSP).
import os, re, sys, json, shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (BaseDocTemplate, PageTemplate, NextPageTemplate, Frame, Paragraph, Spacer, Image as RLImage,
                                Table, TableStyle, PageBreak, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = re.search(r"project\s*\(\s*\w+\s+VERSION\s+([0-9.]+)", open(os.path.join(ROOT, "CMakeLists.txt")).read()).group(1)
SHOTS = sys.argv[1] if len(sys.argv) > 2 else None
OUT = sys.argv[-1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "SmallTone_Notice_FR_v" + VERSION + ".pdf")
TMP = os.path.dirname(os.path.abspath(OUT))
FONTS = os.path.join(ROOT, "assets", "fonts")
ASSETS = os.path.join(ROOT, "tools", "manual_assets")
LOGO_PNG = os.path.join(ROOT, "assets", "nine_hands_logo_blanc.png")      # rendu du SVG officiel (NineHandsLogo.svg)

for n, f in (("Pop", "Poppins-Regular"), ("PopL", "Poppins-Light"), ("PopM", "Poppins-Medium"), ("PopB", "Poppins-Bold"),
             ("Title", "BarlowCondensed-ExtraBold")):
    pdfmetrics.registerFont(TTFont(n, os.path.join(FONTS, f + ".ttf")))

ACC = colors.HexColor("#7A5CBE"); ACC_L = colors.HexColor("#B9A2FF")      # violet de la pedale / anneaux allumes
DARK = colors.HexColor("#1B1824"); GREY = colors.HexColor("#625E6E"); LIGHT = colors.HexColor("#F0ECF8")
LAY = json.load(open(os.path.join(ROOT, "tools", "layout.json")))

NAMES = ["st_annotated.png", "st_onoff.png", "st_switch.png", "st_bar.png", "st_glow.png", "st_menus.png", "st_cover.png"]
if SHOTS:
    def shot(name): return Image.open(os.path.join(SHOTS, name)).convert("RGB")
    src = shot("st_exact_on.png")
    k = src.height / 900.0                          # repere du plugin : 617,5 x 900 unites (fond 1235 x 1800 / 2)
    TX = {t[0]: t for t in LAY["texts"]}
    kx, ky, kr = LAY["knob"]; tx, ty = LAY["toggle"][:2]; lx, ly = LAY["led"][:2]; fx, fy = LAY["fs"][:2]
    px, py, pw, ph = LAY["preset"]; jo, ji = LAY["jacks"]

    # ---------- capture annotee ----------
    marks = [(1, kx + kr + 30, ky - kr + 4), (2, tx + 52, ty - 34), (3, lx - 4, ly - 40), (4, fx + 84, fy - 30),
             (5, px - 2, py - 16), (6, jo - 48, 36), (7, ji + 48, 36)]
    ann = src.copy(); dr = ImageDraw.Draw(ann)
    fnt = ImageFont.truetype(os.path.join(FONTS, "Poppins-Bold.ttf"), 36)
    for n, x, y in marks:
        cx, cy, r = x * k, y * k, 29
        dr.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(122, 92, 190), width=5)
        dr.text((cx, cy + 1), str(n), font=fnt, fill=(27, 24, 36), anchor="mm")
    ann.save(os.path.join(TMP, NAMES[0]))

    def crop_u(im, box): return im.crop(tuple(int(round(v * k)) for v in box))
    gap = 18
    def strip(parts, path, bg=(255, 255, 255)):
        s = Image.new("RGB", (sum(p.width for p in parts) + gap * (len(parts) - 1), max(p.height for p in parts)), bg)
        x = 0
        for p in parts: s.paste(p, (x, 0)); x += p.width + gap
        s.save(path); return path

    byp = shot("st_exact_bypass.png")
    # bypass (DIN.) puis effet actif (DEPTH) : pedale entiere
    strip([byp.resize((618, 900), Image.LANCZOS), src.resize((618, 900), Image.LANCZOS)], os.path.join(TMP, NAMES[1]))
    # inverseur DIN. / DEPTH : en haut (DIN.) puis en bas (DEPTH)
    box_sw = (tx - 62, TX["DIN."][5] - 20, tx + 62, TX["DEPTH"][5] + 20)
    strip([crop_u(byp, box_sw), crop_u(src, box_sw)], os.path.join(TMP, NAMES[2]))
    # pastille : barre de presets, ligne d'etat (RATE), synchro tempo
    box_bar = (px - 8, py - 8, px + pw + 8, py + ph + 8)
    bars = [crop_u(shot(n), box_bar) for n in ("st_exact_on.png", "st_exact_status.png", "st_exact_sync.png")]
    bw, bh = bars[0].size
    col = Image.new("RGB", (bw, bh * 3 + gap * 2), (255, 255, 255))
    for i, b in enumerate(bars): col.paste(b, (0, i * (bh + gap)))
    col.save(os.path.join(TMP, NAMES[3]))
    # reglage Glow : 25 / 50 / 75 / 100 % (zone du potard et de la LED)
    box_gl = (kx - 150, ky - 150, kx + 150, ky + 150)
    strip([crop_u(shot(n), box_gl) for n in ("st_glow_25.png", "st_glow_50.png", "st_glow_75.png", "st_exact_on.png")], os.path.join(TMP, NAMES[4]))
    # menus clic droit : menu principal et sous-menu Glow
    m1, m2 = Image.open(os.path.join(SHOTS, "st_menu.png")).convert("RGBA"), Image.open(os.path.join(SHOTS, "st_menu_glow.png")).convert("RGBA")
    mm_ = Image.new("RGBA", (m1.width + m2.width + gap * 2, max(m1.height, m2.height)), (255, 255, 255, 255))
    mm_.alpha_composite(m1, (0, 0)); mm_.alpha_composite(m2, (m1.width + gap * 2, 60))
    mm_.convert("RGB").save(os.path.join(TMP, NAMES[5]))

    # ---------- couverture : pedale detouree (canal alpha du fond), reflet au sol, halo violet tres doux ----------
    bg_a = Image.open(os.path.join(ROOT, "background.png")).split()[3].resize(src.size, Image.LANCZOS)
    cut = Image.new("RGBA", src.size, (0, 0, 0, 0)); cut.paste(src, (0, 0), bg_a)
    cut = cut.crop(cut.getbbox())
    cw, ch = cut.size
    pad = int(cw * 0.16)
    canvas = Image.new("RGBA", (cw + 2 * pad, int(ch * 1.30) + pad), (0, 0, 0, 255))
    yy, xx = np.mgrid[0:canvas.height, 0:canvas.width].astype(np.float64)
    gcx, gcy = canvas.width / 2, pad + ch * 0.45
    glow = np.exp(-(((xx - gcx) / (cw * 0.62)) ** 2 + ((yy - gcy) / (ch * 0.48)) ** 2)) * 30
    edge = np.clip(np.minimum.reduce([xx, canvas.width - 1 - xx, yy, canvas.height - 1 - yy]) / (pad * 0.9), 0, 1)
    glow *= edge ** 2
    halo = np.dstack([glow * 0.62, glow * 0.40, glow * 1.0, np.full_like(glow, 255)]).astype(np.uint8)
    canvas = Image.alpha_composite(canvas, Image.fromarray(halo, "RGBA"))
    refl = cut.transpose(Image.FLIP_TOP_BOTTOM)
    ra = np.array(refl).astype(np.float64)
    fade = np.clip(1 - np.arange(refl.height) / (refl.height * 0.22), 0, 1) ** 1.6 * 0.22
    ra[..., 3] *= fade[:, None]
    canvas.alpha_composite(Image.fromarray(ra.astype(np.uint8), "RGBA"), (pad, pad + ch + 6))
    canvas.alpha_composite(cut, (pad, pad))
    canvas = canvas.crop((0, 0, canvas.width, pad + int(ch * 1.20)))
    canvas.convert("RGB").save(os.path.join(TMP, NAMES[6]))
    os.makedirs(ASSETS, exist_ok=True)
    for n in NAMES: shutil.copy(os.path.join(TMP, n), os.path.join(ASSETS, n))
annotated, onoff, sw_img, bar_img, glow_img, menus_img, cover = [os.path.join(ASSETS, n) for n in NAMES]

def img(path, width):
    im = Image.open(path); h = width * im.height / im.width
    return RLImage(path, width=width, height=h)

# ---------- styles ----------
st = {
    "h1": ParagraphStyle("h1", fontName="PopB", fontSize=20, leading=24, textColor=ACC, spaceAfter=8, spaceBefore=4, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="PopM", fontSize=13, leading=17, textColor=DARK, spaceAfter=4, spaceBefore=10, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Pop", fontSize=9.6, leading=14, textColor=DARK, spaceAfter=5),
    "tip": ParagraphStyle("tip", fontName="Pop", fontSize=9.2, leading=13, textColor=DARK, spaceAfter=4),
    "small": ParagraphStyle("small", fontName="Pop", fontSize=8.2, leading=11.5, textColor=GREY, spaceAfter=4),
    "cell": ParagraphStyle("cell", fontName="Pop", fontSize=8.6, leading=11.4, textColor=DARK),
    "cellb": ParagraphStyle("cellb", fontName="PopM", fontSize=8.6, leading=11.4, textColor=DARK),
}
def P(t, s="p"): return Paragraph(t, st[s])
def bullets(items, s="p"): return [P("&bull;&nbsp;&nbsp;" + i, s) for i in items]
def table(rows, widths, header=True):
    data = [[P(c, "cellb" if (header and r == 0) else "cell") for c in row] for r, row in enumerate(rows)]
    t = Table(data, colWidths=widths, repeatRows=1 if header else 0)
    style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#DCD5EA")),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header: style += [("BACKGROUND", (0, 0), (-1, 0), LIGHT), ("LINEBELOW", (0, 0), (-1, 0), 0.8, ACC)]
    t.setStyle(TableStyle(style)); return t
def side(left, right, wl):
    t = Table([[left, right]], colWidths=[wl, W - wl])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (-1, 0), (-1, 0), 0)]))
    return t

# ---------- donnees (identiques au code livre : PluginProcessor.cpp) ----------
FACTORY = [("Classic Deep", "DEPTH", "1,21 Hz", "Le son Small Clone de référence (preset par défaut)."),
           ("Grunge Water", "DEPTH", "1,45 Hz", "Le son aquatique de Kurt Cobain sur « Come As You Are » (Nirvana, <i>Nevermind</i>) : DEPTH, RATE vers 11 h."),
           ("Slow Ocean", "DEPTH", "0,45 Hz", "Houle lente et ample."),
           ("Seasick", "DEPTH", "3,50 Hz", "Prononcé, tanguant, presque « mal de mer »."),
           ("Rotary Fast", "DEPTH", "7,03 Hz", "Scintillement de haut-parleur tournant."),
           ("Subtle Thickener", "DIN.", "0,60 Hz", "Doublage discret pour épaissir une rythmique."),
           ("Shimmer Clean", "DIN.", "2,49 Hz", "Arpèges clairs scintillants."),
           ("Warble", "DIN.", "6,05 Hz", "Presque un vibrato."),
           ("Bass Chorus", "DIN.", "1,00 Hz", "Léger, garde le grave ferme (basse, guitare accordée bas).")]

W = A4[0] - 36 * mm
f = [NextPageTemplate("p"), Spacer(1, 1), PageBreak()]     # page 1 = couverture dessinee a positions fixes (cover_bg)

f += [P("1. Présentation", "h1"),
      P("<b>SMALL TONE</b> est un chorus VST3 NINE HANDS | DSP au format pédale, modélisé composant par composant sur "
        "l'<b>Electro-Harmonix Small Clone</b> (EH-4600), le chorus analogique entendu sur d'innombrables disques des années 80 et 90, "
        "célèbre pour son tourbillon profond et « liquide ». Comme l'original, il n'a que deux réglages : le potard <b>RATE</b> et "
        "l'inverseur <b>DIN. / DEPTH</b>. Son direct et son retardé sont mélangés à parts égales : pas de réglage de mix, c'est toujours un chorus franc."),
      P("À l'intérieur, le plugin reproduit le vrai circuit : le LFO triangle à LM358, le réseau qui le conduit à l'horloge CD4047 et la "
        "ligne à retard « bucket brigade » MN3207 (1024 étages) avec ses filtres, sa saturation douce et son léger souffle. C'est pour cela "
        "que les réglages se comportent comme sur la pédale et non comme un chorus générique (section 4)."),
      P("La version 2 redessine entièrement la pédale : boîtier violet anodisé, plaques noires biseautées, potard, inverseur, LED, "
        "footswitch et jacks photographiés, sérigraphie vectorielle nette à toutes les tailles, jacks sur le dessus, halos lumineux réglables "
        "(<b>Glow</b>) et menus du clic droit au style NINE HANDS | DSP."),
      Spacer(1, 2 * mm), img(os.path.join(ASSETS, "diagram_fr.png"), W), P("Synoptique du circuit modélisé.", "small"),
      P("2. Installation", "h1")]
f += bullets(["<b>Windows</b> : téléchargez <b>SmallTone-VST3-Windows.zip</b> (page Releases du dépôt GitHub Nine-Hands-Dsp/Small-Tone), "
              "décompressez-le et copiez <b>Small Tone.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>.",
              "<b>macOS</b> (universel, Apple Silicon et Intel) : téléchargez <b>SmallTone-VST3-macOS.zip</b>, copiez <b>Small Tone.vst3</b> dans "
              "<b>~/Library/Audio/Plug-Ins/VST3/</b>, puis lancez une fois dans le Terminal : "
              "<i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/\"Small Tone.vst3\"</i> (retire la quarantaine du téléchargement).",
              "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. Le plugin apparaît sous le nom "
              "<b>Small Tone (NINE HANDS | DSP)</b>, catégorie Fx | Modulation. Pour le piloter en MIDI, la piste doit recevoir le MIDI du contrôleur "
              "(armement ou monitoring d'entrée, entrée MIDI réglée sur votre appareil)."])
f.append(PageBreak())

ov = [["N°", "Commande", "Rôle"],
      ["1", "RATE", "Vitesse de modulation. L'anneau lumineux autour du potard pulse au rythme du LFO. Glisser, molette, double-clic = milieu, clic droit = MIDI Learn."],
      ["2", "Inverseur DIN. / DEPTH", "En haut = DIN. (léger), en bas = DEPTH (profond). Clic sur le levier ou sur l'inscription."],
      ["3", "LED STATUS / SYNC", "Bleue = effet actif. Clic sur la LED ou le mot SYNC : synchro tempo du RATE (la LED clignote en mesure, SYNC s'illumine)."],
      ["4", "Footswitch", "Effet / bypass. L'anneau de sa gorge s'allume en violet avec l'effet."],
      ["5", "Barre de presets / ligne d'état", "Au repos : flèches = preset précédent / suivant, clic sur le nom = menu des presets. Pendant un réglage : la valeur en direct."],
      ["6", "OUTPUT", "Jack de sortie, sur le dessus (décoratif)."],
      ["7", "INPUT", "Jack d'entrée, sur le dessus (décoratif). Entrée mono ou stéréo."]]
f += [P("3. Vue d'ensemble de l'interface", "h1"),
      side([img(annotated, 84 * mm)], table(ov, [8 * mm, 27 * mm, W - 88 * mm - 35 * mm]), 88 * mm),
      Spacer(1, 4 * mm), KeepTogether([img(onoff, 104 * mm), P("À gauche : bypass (DIN., lumières éteintes) · À droite : effet actif (DEPTH, LED, anneaux et halos allumés).", "small")]),
      PageBreak()]

f += [P("4. Les commandes en détail", "h1"), P("Potard RATE", "h2")]
f += bullets(["Plage : environ 0,42 Hz (tout à gauche) à 9,4 Hz (tout à droite), milieu environ 2,06 Hz. La ligne d'état affiche la vitesse en Hz.",
              "Courbe du potard d'origine, un 1 M « ccw log » en série avec 47 k : la première moitié de la course couvre les vitesses de chorus "
              "classiques (0,4 à 2 Hz), la seconde monte vite vers les vitesses rotary / vibrato.",
              "Souris : tirer vers le haut ou la droite pour augmenter (toute la course demande le même déplacement quelle que soit la taille de la fenêtre), "
              "molette pour les petits pas, <b>Maj</b> = 4x plus fin, <b>double-clic</b> = milieu. Le repère tourne sur ±135°, comme la graduation ; "
              "les changements de vitesse glissent sur 30 ms environ, comme un vrai potard (aucun clic).",
              "Avec la synchro tempo, le potard choisit une valeur de note : 2 mesures, 1 mesure, 1/2, 1/4., 1/4, 1/4T, 1/8, 1/8T, 1/16."])
f += [P("Inverseur DIN. / DEPTH", "h2"),
      side(bullets(["<b>DIN.</b> (levier en haut) : une résistance à la masse divise la modulation par 2 environ et raccourcit le délai moyen "
                    "(environ 2,6 à 3,5 ms). Doublage, épaississement léger, idéal pour les rythmiques en son clair.",
                    "<b>DEPTH</b> (levier en bas) : modulation complète (environ 3,0 à 6,3 ms aux vitesses lentes). Le son Small Clone profond, presque « mal de mer ».",
                    "Cliquez sur le levier pour basculer, ou directement sur l'inscription « DIN. » ou « DEPTH » ; la molette sur le levier marche aussi. "
                    "Le levier passe par sa position intermédiaire, comme un vrai inverseur."]),
           [img(sw_img, 44 * mm), P("À gauche : DIN. · À droite : DEPTH", "small")], W - 50 * mm),
      P("Interactions entre les réglages", "h2")]
f += bullets(["En DEPTH, le condensateur de 10 µF entre le LFO et l'horloge arrondit le triangle : plus le RATE est rapide, plus le balayage se resserre "
              "et s'adoucit (environ 3,5 à 4,8 ms à 6 Hz). Les vitesses rapides restent musicales : un scintillement de haut-parleur tournant plutôt qu'un son faux.",
              "En DIN., ce filtrage est environ deux fois plus rapide : le balayage léger reste presque triangulaire à toutes les vitesses.",
              "Basculer l'inverseur fait glisser le délai pendant environ une demi-seconde, le temps que le 10 µF se recharge, comme sur la pédale."])
gr = Table([[img(os.path.join(ASSETS, "graph_rate.png"), W / 2 - 3 * mm), img(os.path.join(ASSETS, "graph_delay.png"), W / 2 - 3 * mm)]], colWidths=[W / 2, W / 2])
gr.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
f += [KeepTogether([Spacer(1, 2 * mm), gr, P("À gauche : vitesse du LFO selon la position du RATE · À droite : délai du BBD sur 2 secondes pour trois réglages.", "small")])]

f += [P("5. Footswitch, LED, Glow et synchro tempo", "h1")]
f += bullets(["<b>Footswitch</b> : effet / bypass dès l'appui ; le bouton s'assombrit tant qu'on appuie. Le bypass est totalement transparent "
              "(le signal direct passe intact) et le passage se fait en fondu de 10 ms : aucun clic.",
              "<b>Lumières</b> : avec l'effet, la LED STATUS s'allume en bleu, l'anneau de la gorge du footswitch et l'anneau du potard s'allument en violet. "
              "L'anneau du RATE pulse au rythme du LFO (entre 55 et 100 % de sa luminosité) ; il peut rester fixe : clic droit &gt; Settings &gt; "
              "<i>Rate ring pulses with the LFO</i>.",
              "<b>Glow</b> (clic droit &gt; <i>Glow (halo of the lights)</i>) : règle le halo autour des lumières, <b>25 %</b>, <b>50 %</b>, <b>75 %</b> "
              "ou <b>100 %</b> (par défaut). Seul le halo change ; la source lumineuse elle-même garde son éclat. Réglage commun à toutes les instances, "
              "enregistré sur l'ordinateur."])
f += [KeepTogether([Spacer(1, 1 * mm), img(glow_img, W * 0.86), P("Glow 25 %, 50 %, 75 % et 100 %.", "small")]),
      P("Synchro tempo", "h2"),
      side([P("Cliquez sur la LED STATUS ou sur le mot <b>SYNC</b> à côté (ou clic droit &gt; Settings &gt; <i>Rate synced to host tempo</i>). "
              "Le LFO suit alors le tempo du DAW et le potard RATE choisit la valeur de note. La ligne d'état affiche brièvement la valeur et le tempo "
              "(<i>Tempo sync 1/4 @ 120 BPM</i>), la LED STATUS clignote à chaque cycle du LFO, en mesure avec le DAW, et SYNC s'illumine en bleu. "
              "Recliquez pour revenir à la vitesse libre. Le réglage est enregistré avec le projet, automatisable, et se pilote en MIDI (section 6).")],
           [img(bar_img, 62 * mm), P("La pastille : barre de presets au repos, ligne d'état pendant un réglage du RATE, puis en synchro tempo.", "small")], W - 66 * mm)]

midi = [["Commande", "Type"],
        ["Footswitch", "À accrochage (défaut) : 64-127 = effet, 0-63 = bypass. Momentané : chaque appui bascule."],
        ["Rate", "Continu : 0-127 = toute la course du potard (valeur de note en synchro). À apprendre sur la pédale d'expression."],
        ["Depth switch", "Bascule : 0-63 = DIN., 64-127 = DEPTH."],
        ["Sync (LED STATUS)", "Bascule : 64-127 = synchro tempo, 0-63 = RATE libre."],
        ["Program Change", "Non apprenable : le programme n charge le preset usine n+1 (programme 0 = Classic Deep)."]]
f += [P("6. MIDI", "h1"),
      P("Chaque commande peut être pilotée par un footswitch, une pédale d'expression ou un contrôleur MIDI. <b>Aucun CC n'est assigné par défaut</b> : "
        "tout passe par le <b>MIDI Learn</b>, le plugin ne réagit donc jamais à un contrôleur que vous n'avez pas assigné vous-même.")]
f += bullets(["<b>Clic droit sur une commande</b> (potard RATE, inverseur DIN. / DEPTH, footswitch, LED STATUS ou mot SYNC) : le menu s'ouvre sur cette commande "
              "(son CC actuel ou <i>not assigned</i>), avec <b>MIDI Learn: &lt;commande&gt;</b> et <b>Clear MIDI: &lt;commande&gt;</b>.",
              "La ligne d'état affiche <b>MIDI LEARN</b> et le nom de la commande tant qu'elle attend. Bougez une pédale ou appuyez sur un bouton : le premier CC "
              "reçu est assigné et la ligne d'état le confirme (<i>Rate = CC 11</i>). Un CC déjà utilisé par une autre commande lui est retiré ; "
              "<b>Cancel MIDI learn</b> arrête l'attente.",
              "<b>Clic droit ailleurs &gt; MIDI</b> : <b>MIDI channel</b> (omni par défaut ou 1 à 16), <b>Learn</b> de chaque commande avec son CC actuel, "
              "<b>Clear all MIDI assignments</b>, footswitch MIDI à accrochage ou momentané.",
              "Les assignations sont enregistrées avec le projet ; tous les paramètres sont aussi automatisables depuis le DAW. Un ancien projet resté sur "
              "les anciennes assignations d'usine, jamais modifiées, s'ouvre sans assignation."])
f += [KeepTogether([Spacer(1, 1 * mm), table(midi, [38 * mm, W - 38 * mm])])]

f += [P("7. Fenêtre et menus", "h1")]
f += bullets(["La fenêtre s'ouvre à la taille par défaut, <b>60 %</b> tant que vous n'en choisissez pas une autre, et ne peut jamais être plus petite que 60 %.",
              "Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> pour cette fenêtre (la taille actuelle est cochée, "
              "« (default) » marque la taille par défaut). On peut aussi agrandir la fenêtre par son coin, jusqu'à 150 % (proportions conservées).",
              "<b>Plugin size &gt; Default size (new windows)</b> : choisit la taille d'ouverture de toutes les nouvelles fenêtres de Small Tone (réglage commun à "
              "toutes les instances, enregistré sur l'ordinateur) ; la fenêtre ouverte prend aussitôt cette taille.",
              "Une instance dont la fenêtre a été redimensionnée garde sa taille dans le projet ; une instance jamais redimensionnée s'ouvre à la taille par défaut.",
              "La <b>barre de presets</b> et la <b>ligne d'état</b> partagent la même pastille, sous le footswitch. Au repos, elle affiche le preset en cours "
              "(ou <i>Edited</i>). Dès qu'un réglage bouge (souris, molette, automation, MIDI), la ligne d'état prend sa place en fondu et affiche la valeur "
              "(<i>Rate 1.5 Hz</i>, <i>Depth (deep)</i>, <i>Bypass</i>…), puis s'efface ; un clic sur la pastille fait revenir la barre de presets tout de suite. "
              "Le changement de preset, lui, ne fait pas apparaître la ligne d'état."])
menu = [["Entrée", "Contenu"],
        ["MIDI Learn (sur une commande)", "MIDI Learn / Clear MIDI / Cancel MIDI learn"],
        ["Plugin size", "60 % · 75 % · 100 % · Default size (new windows)"],
        ["Glow (halo of the lights)", "Glow 25 % · 50 % · 75 % · 100 % (default)"],
        ["Factory presets", "les 9 presets usine (section 8)"],
        ["Load / Save user preset", "User 1 … 9"],
        ["Settings", "Rate synced to host tempo · Stereo spread (LFO inversé à droite) · BBD hiss (souffle analogique) · Rate ring pulses with the LFO"],
        ["MIDI", "MIDI channel · Learn x4 · Cancel / Clear all MIDI assignments · footswitch à accrochage / momentané · Program Change"]]
f += [Spacer(1, 1 * mm),
      side([table(menu, [40 * mm, W - 40 * mm - 70 * mm])], [img(menus_img, 66 * mm), P("Menu du clic droit et sous-menu Glow : il s'ouvre là où vous cliquez.", "small")], W - 70 * mm)]

pre = [["PC", "Preset", "Inverseur", "RATE", "Caractère"]] + [[str(i), "<b>" + n + "</b>", s, r, d] for i, (n, s, r, d) in enumerate(FACTORY)]
f += [P("8. Presets", "h1"),
      P("Les 9 presets usine sont des programmes VST3 : ils apparaissent dans le menu des presets du DAW (Reaper : champ preset de la fenêtre FX), "
        "sous les flèches et le nom de la barre de presets, et sous clic droit &gt; Factory presets. Clic droit &gt; <b>Save user preset</b> enregistre "
        "jusqu'à 9 presets personnels, communs à toutes les instances (%APPDATA%\\NINE HANDS | DSP\\Small Tone\\ ou ~/Library/NINE HANDS | DSP/Small Tone/)."),
      KeepTogether([table(pre, [9 * mm, 30 * mm, 21 * mm, 17 * mm, W - 77 * mm])])]

f += [P("9. Conseils d'utilisation", "h1")]
f += bullets(["<b>Chaîne Reaper</b> : placez Small Tone avant la simulation d'ampli (Ampire, Impulse…), comme une pédale devant un ampli, avec vos autres "
              "pédales NINE HANDS | DSP. Pour un chorus plus propre, plus « studio », essayez-le après la simulation (façon boucle d'effets).",
              "<b>7 cordes / accordages graves</b> : le signal retardé est filtré sous 70 Hz environ, un Sol grave garde une fondamentale ferme, sans chorus. "
              "Pour les riffs graves, préférez DIN. ou le preset Bass Chorus ; gardez DEPTH pour les accords et les sons clairs.",
              "<b>Stéréo</b> : la pédale d'origine est mono. Clic droit &gt; Settings &gt; Stereo spread inverse le LFO du canal droit pour une image large.",
              "<b>Pédale d'expression</b> : apprenez Rate sur votre pédale d'expression pour passer en direct du chorus lent au rotary rapide ; "
              "apprenez Sync sur un footswitch MIDI pour basculer la synchro tempo en live.",
              "Coupez le souffle du BBD (<b>BBD hiss</b>, Settings) pour un fond parfaitement silencieux quand vous empilez beaucoup de pistes."], "tip")

tech = [["Format", "VST3 - Windows 64 bits, macOS universel (Apple Silicon + Intel) - NINE HANDS | DSP, Fx | Modulation"],
        ["Pédale d'origine", "Electro-Harmonix Small Clone (EH-4600)"],
        ["Canaux", "mono vers stéréo, stéréo vers stéréo"],
        ["LFO", "intégrateur LM358 (2,2 µF) + comparateur à hystérésis (120k / 470k), triangle 0,86 - 2,79 V, 0,42 - 9,4 Hz"],
        ["Retard", "BBD MN3207, 1024 étages, horloge environ 75 - 200 kHz, délai 1024 / (2 f) environ 2,6 - 6,5 ms"],
        ["Filtres", "anti-repliement 4e ordre ~6,2 kHz, reconstruction ~5,6 kHz, passe-haut 70 Hz sur le signal traité"],
        ["Mix", "direct + retardé 50 / 50, niveau compensé ; fondu de bypass 10 ms ; latence 0"],
        ["Fréquences", "44,1 - 192 kHz (LFO indépendant de la fréquence d'échantillonnage)"],
        ["Presets", "9 usine (programmes VST3) + 9 utilisateur communs à toutes les instances"],
        ["MIDI", "MIDI Learn sur Footswitch, Rate, Depth switch et Sync, aucun CC assigné par défaut, canal omni / 1-16, footswitch à accrochage ou momentané, Program Change"],
        ["Fenêtre", "Plugin size 60 % / 75 % / 100 %, taille par défaut au choix (60 % au départ), jamais moins de 60 %, jusqu'à 150 % par le coin ; Glow 25 - 100 %"],
        ["Stabilité Windows", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement piloté par un timer avec chien de garde"]]
f += [KeepTogether([P("10. Caractéristiques techniques", "h1"), table(tech, [30 * mm, W - 30 * mm], header=False)])]

def deco(c, doc):
    c.saveState()
    c.setFillColor(DARK); c.rect(0, A4[1] - 6 * mm, A4[0], 6 * mm, stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, A4[1] - 6.8 * mm, A4[0], 0.8 * mm, stroke=0, fill=1)
    c.setFont("Pop", 7.5); c.setFillColor(GREY)
    c.drawString(18 * mm, 10 * mm, "Small Tone (NINE HANDS | DSP) · v" + VERSION)
    c.drawRightString(A4[0] - 18 * mm, 10 * mm, str(doc.page))
    c.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
                      title="SMALL TONE - Notice v" + VERSION, author="NINE HANDS | DSP")
# ---- Couverture « minimale » (modele 6) : gabarit fixe commun a toutes les notices (mm depuis le HAUT, logo et bandeau depuis le bas) ----
COVER_NAME, COVER_SUB, COVER_LANG = "SMALL TONE", "Chorus analogique", "FRANÇAIS"
PEDAL_H, PEDAL_MAXW, PEDAL_TOP = 82 * mm, 115 * mm, 84 * mm
LANG_TOP = 18 * mm
NAME_TOP, NAME_PT = 194 * mm, 30
SUB_TOP, SUB_PT = 208 * mm, 10
LOGO_W, LOGO_BOTTOM = 38 * mm, 22 * mm
BAND_H = 3 * mm
def cover_bg(c, doc):
    c.saveState(); c.setFillColor(colors.black); c.rect(0, 0, A4[0], A4[1], stroke=0, fill=1)
    c.setFillColor(ACC); c.rect(0, 0, A4[0], BAND_H, stroke=0, fill=1)
    def line(text, top, font, size, cs, col):
        w = pdfmetrics.stringWidth(text, font, size) + cs * (len(text) - 1)
        t = c.beginText((A4[0] - w) / 2, A4[1] - top - size * 0.8); t.setFont(font, size); t.setCharSpace(cs)
        t.setFillColor(col); t.textOut(text); c.drawText(t)
    line(COVER_LANG, LANG_TOP, "PopM", 8.5, 0, ACC_L)
    ci = Image.open(cover); iw, ih = ci.size
    cw = iw / 1.32; pad = int(cw * 0.16); ch = (ih - pad) / 1.2            # geometrie de st_cover.png
    k = min(PEDAL_H / ch, PEDAL_MAXW / cw)
    dw, dh = iw * k, ih * k
    y0 = A4[1] - (PEDAL_TOP + (PEDAL_H - ch * k) / 2) + pad * k
    c.drawImage(cover, (A4[0] - dw) / 2, y0 - dh, dw, dh)
    line(COVER_NAME, NAME_TOP - NAME_PT * 0.02, "Title", NAME_PT, NAME_PT * 0.5, colors.white)
    line(COVER_SUB, SUB_TOP, "Pop", SUB_PT, 1.5, colors.HexColor("#BDC4B8"))
    lw, lh = Image.open(LOGO_PNG).size
    c.drawImage(LOGO_PNG, (A4[0] - LOGO_W) / 2, LOGO_BOTTOM, LOGO_W, LOGO_W * lh / lw, mask="auto")
    c.restoreState()
doc.addPageTemplates([PageTemplate(id="cover", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="fc")], onPage=cover_bg),
                      PageTemplate(id="p", frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="f")], onPage=deco)])
doc.build(f)
print(OUT)
