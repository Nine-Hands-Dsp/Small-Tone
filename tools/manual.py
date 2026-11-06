# SMALL TONE (NINE HANDS | DSP) - notice PDF bilingue (anglais puis francais).
# Usage : python3 tools/manual.py [fichier PDF de sortie]   (defaut : docs/SmallTone_Manual_EN-FR_v<version>.pdf)
# Version lue dans CMakeLists.txt. Illustrations : tools/manual_assets/ (captures et graphiques repris de la notice v1.2.0,
# toujours justes ; diagram_en/fr = synoptique du circuit). Moteur de mise en page : tools/manual_lib.py.
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import manual_lib as L

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = re.search(r"project\s*\(\s*\w+\s+VERSION\s+([0-9.]+)", open(os.path.join(ROOT, "CMakeLists.txt")).read()).group(1)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "docs", "SmallTone_Manual_EN-FR_v" + VERSION + ".pdf")

TEXTS = {"en": dict(lang="ENGLISH", sub=["Analog chorus modelled on the EHX Small Clone - VST3"], ver="User manual \u00b7 version " + VERSION),
         "fr": dict(lang="FRANÇAIS", sub=["Chorus analogique modélisé sur l'EHX Small Clone - VST3"], ver="Notice d'utilisation \u00b7 version " + VERSION)}

# presets usine (PluginProcessor.cpp) : nom, frequence affichee, DEPTH
FACTORY = [("Classic Deep", "1.21 Hz", 1), ("Grunge Water", "1.45 Hz", 1), ("Slow Ocean", "0.45 Hz", 1), ("Seasick", "3.50 Hz", 1),
           ("Rotary Fast", "7.03 Hz", 1), ("Subtle Thickener", "0.60 Hz", 0), ("Shimmer Clean", "2.49 Hz", 0), ("Warble", "6.05 Hz", 0),
           ("Bass Chorus", "1.00 Hz", 0)]
DESC = {"en": ["The reference Small Clone sound (default).", "Kurt Cobain's watery tone on Nirvana's “Come As You Are”: RATE around 11 o'clock.",
               "Slow, wide swell.", "Pronounced, wobbly.", "Rotating-speaker shimmer.", "Discreet doubling.", "Sparkly clean arpeggios.",
               "Almost vibrato.", "Light, keeps the low end firm."],
        "fr": ["Le son Small Clone de référence (par défaut).", "Le son aquatique de Kurt Cobain sur « Come As You Are » de Nirvana : RATE vers 11 h.",
               "Houle lente et ample.", "Prononcé, tanguant.", "Scintillement de haut-parleur tournant.", "Doublage discret.", "Arpèges clairs scintillants.",
               "Presque un vibrato.", "Léger, garde le grave ferme."]}


def content(lang):
    en = lang == "en"
    def t(a, b): return a if en else b
    b = []
    b += [("h1", t("1. Introduction", "1. Présentation")),
          ("p", t("Small Tone is a VST3 chorus in the shape of a guitar pedal, modelled component by component on the <b>Electro-Harmonix Small Clone</b> (EH-4600), the analog chorus heard on countless 80s and 90s records, famous for its deep, “liquid” swirl. Like the original it has only two controls: a <b>RATE</b> knob and a <b>DIN. / DEPTH</b> switch. Dry and delayed signals are blended in equal parts, so there is no mix knob: the sound is always a full chorus.",
                  "Small Tone est un chorus VST3 au format pédale, modélisé composant par composant sur l'<b>Electro-Harmonix Small Clone</b> (EH-4600), le chorus analogique entendu sur d'innombrables disques des années 80 et 90, célèbre pour son tourbillon profond et « liquide ». Comme l'original, il n'a que deux réglages : le potard <b>RATE</b> et le switch <b>DIN. / DEPTH</b>. Son direct et son retardé sont mélangés à parts égales : pas de réglage de mix, c'est toujours un chorus franc.")),
          ("p", t("Inside, the plug-in reproduces the real circuit: the LM358 triangle LFO, the network that feeds it to the CD4047 clock, and the MN3207 bucket-brigade delay line (1024 stages) with its filters, soft saturation and light hiss. This is why the controls behave like the pedal and not like a generic chorus (section 4).",
                  "À l'intérieur, le plugin reproduit le vrai circuit : le LFO triangle à LM358, le réseau qui le conduit à l'horloge CD4047, et la ligne à retard « bucket brigade » MN3207 (1024 étages) avec ses filtres, sa saturation douce et son léger souffle. C'est pour cela que les réglages se comportent comme sur la pédale et non comme un chorus générique (section 4).")),
          ("img", "diagram_" + lang + ".png", 172, None),
          ("h1", "2. Installation"),
          ("bullets", [t("<b>Windows</b>: copy <b>Small Tone.vst3</b> into <b>C:\\Program Files\\Common Files\\VST3\\</b>.", "<b>Windows</b> : copiez <b>Small Tone.vst3</b> dans <b>C:\\Program Files\\Common Files\\VST3\\</b>."),
                       t("<b>macOS</b> (universal, Apple Silicon and Intel): copy <b>Small Tone.vst3</b> into <b>~/Library/Audio/Plug-Ins/VST3/</b>, then run once in Terminal: <i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/\"Small Tone.vst3\"</i> (removes the download quarantine).",
                         "<b>macOS</b> (universel, Apple Silicon et Intel) : copiez <b>Small Tone.vst3</b> dans <b>~/Library/Audio/Plug-Ins/VST3/</b>, puis lancez une fois dans le Terminal : <i>xattr -cr ~/Library/Audio/Plug-Ins/VST3/\"Small Tone.vst3\"</i> (retire la quarantaine du téléchargement)."),
                       t("<b>Reaper</b>: Options &gt; Preferences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. The plug-in appears as <b>Small Tone (NINE HANDS | DSP)</b>, category Fx | Modulation.",
                         "<b>Reaper</b> : Options &gt; Préférences &gt; Plug-ins &gt; VST &gt; <i>Re-scan</i>. Le plugin apparaît sous le nom <b>Small Tone (NINE HANDS | DSP)</b>, catégorie Fx | Modulation.")]),
          ("pb",)]
    rows = [[t("No.", "N°"), t("Element", "Élément"), t("Function", "Fonction")],
            ["1", "RATE", t("Modulation speed. The light ring around the knob pulses with the LFO.", "Vitesse de modulation. L'anneau lumineux autour du potard pulse au rythme du LFO.")],
            ["2", "DIN. / DEPTH", t("Depth switch: up = DIN. (light), down = DEPTH (deep).", "Switch de profondeur : en haut = DIN. (léger), en bas = DEPTH (profond).")],
            ["3", "STATUS / SYNC", t("Blue LED: effect on. Click the LED or the word SYNC: tempo sync of the RATE; the LED then blinks in time and SYNC glows.", "LED bleue : effet actif. Clic sur la LED ou sur le mot SYNC : synchro tempo du RATE ; la LED clignote alors en mesure et SYNC s'illumine.")],
            ["4", "Footswitch", t("Effect on / bypass. Its ring lights up with the effect.", "Effet / bypass. Son anneau s'allume avec l'effet.")],
            ["5", t("Status line", "Ligne d'état"), t("Appears only while you adjust something (speed, mode, preset, MIDI...), then fades out.", "N'apparaît que pendant un réglage (vitesse, mode, preset, MIDI...), puis s'efface en fondu.")],
            ["6 / 7", "OUTPUT / INPUT", t("Jacks on top of the pedal (decorative). Mono or stereo input.", "Jacks sur le dessus de la pédale (décoratifs). Entrée mono ou stéréo.")]]
    b += [("h1", t("3. The interface", "3. L'interface")),
          ("side", "annotated.png", 80, [("table", rows, [10, 26, None], {"total": 89})]),
          ("img", "on_bypass.png", 172, t("Left: effect on (DEPTH, LEDs lit) · Right: bypass (DIN., LEDs off)", "À gauche : effet actif (DEPTH, LED allumées) · À droite : bypass (DIN., LED éteintes)")),
          ("pb",)]
    b += [("h1", t("4. Controls", "4. Les commandes")),
          ("h2", t("RATE knob", "Potard RATE")),
          ("bullets", [t("Range: about 0.42 Hz (fully left) to 9.4 Hz (fully right), centre about 2.06 Hz. The status line shows the speed in Hz.", "Plage : environ 0,42 Hz (tout à gauche) à 9,4 Hz (tout à droite), milieu environ 2,06 Hz. La ligne d'état affiche la vitesse en Hz."),
                       t("Taper of the original 1 M “ccw log” pot in series with 47 k: the first half of the travel covers the classic slow chorus speeds (0.4 to 2 Hz), the second half rises quickly to rotary / vibrato speeds.", "Courbe du potard d'origine, un 1 M « ccw log » en série avec 47 k : la première moitié de la course couvre les vitesses de chorus classiques (0,4 à 2 Hz), la seconde monte vite vers les vitesses rotary / vibrato."),
                       t("Mouse: drag up or right to increase (the full travel takes the same mouse movement whatever the size of the window), mouse wheel for small steps, <b>Shift</b> = 4x finer, <b>double-click</b> = centre. The knob turns over ±135°, like the printed scale; speed changes glide over about 30 ms, as with a real pot (no clicks).", "Souris : tirer vers le haut ou la droite pour augmenter (toute la course demande le même déplacement quelle que soit la taille de la fenêtre), molette pour les petits pas, <b>Maj</b> = 4x plus fin, <b>double-clic</b> = milieu. Le potard tourne sur ±135°, comme la sérigraphie ; les changements de vitesse glissent sur 30 ms environ, comme un vrai potard (aucun clic)."),
                       t("With tempo sync on, the knob selects a note value instead: 2 bars, 1 bar, 1/2, 1/4., 1/4, 1/4T, 1/8, 1/8T, 1/16.", "Avec la synchro tempo, le potard choisit une valeur de note : 2 mesures, 1 mesure, 1/2, 1/4., 1/4, 1/4T, 1/8, 1/8T, 1/16.")]),
          ("h2", t("DIN. / DEPTH switch", "Switch DIN. / DEPTH")),
          ("side", "din_depth.png", 45, [("bullets", [t("<b>DIN.</b> (lever up): a 2.7 k resistor to ground divides the modulation by about 3 and shortens the average delay (about 2.6 to 3.1 ms). Light doubling / thickening, ideal for clean rhythm parts.", "<b>DIN.</b> (levier en haut) : une résistance de 2,7 k à la masse divise la modulation par 3 environ et raccourcit le délai moyen (environ 2,6 à 3,1 ms). Doublage, épaississement léger, idéal pour les rythmiques en son clair."),
                                                      t("<b>DEPTH</b> (lever down): full modulation (about 3.0 to 5.6 ms at slow speeds). The deep, seasick Small Clone sound.", "<b>DEPTH</b> (levier en bas) : modulation complète (environ 3,0 à 5,6 ms aux vitesses lentes). Le son Small Clone profond, presque « mal de mer »."),
                                                      t("Click the lever to toggle, or click directly on the “DIN.” or “DEPTH” label.", "Cliquez sur le levier pour basculer, ou directement sur l'inscription « DIN. » ou « DEPTH ».")]),
                                         ("small", t("Left: DIN. (lever up) · Right: DEPTH (lever down)", "À gauche : DIN. (levier en haut) · À droite : DEPTH (levier en bas)"))]),
          ("h2", t("How the controls interact", "Interactions entre les réglages")),
          ("bullets", [t("In DEPTH, the 10 µF capacitor between the LFO and the clock rounds off the triangle: the faster the RATE, the narrower and smoother the sweep (about 3.6 to 4.3 ms at 6 Hz). This keeps fast settings musical, a rotary-speaker shimmer instead of an out-of-tune warble.", "En DEPTH, le condensateur de 10 µF entre le LFO et l'horloge arrondit le triangle : plus le RATE est rapide, plus le balayage se resserre et s'adoucit (environ 3,6 à 4,3 ms à 6 Hz). Les vitesses rapides restent musicales : un scintillement de haut-parleur tournant plutôt qu'un son faux."),
                       t("In DIN. the filtering is about three times faster, so the shallow sweep stays almost triangular at every speed.", "En DIN., ce filtrage est environ trois fois plus rapide : le balayage léger reste presque triangulaire à toutes les vitesses."),
                       t("Flipping the switch makes the delay glide for about half a second while the 10 µF recharges, exactly like the pedal.", "Basculer le switch fait glisser le délai pendant environ une demi-seconde, le temps que le 10 µF se recharge, comme sur la pédale.")]),
          ("imgs", ["graph_rate.png", "graph_delay.png"], 84, t("Left: LFO speed vs RATE position · Right: BBD delay over 2 seconds for three settings", "À gauche : vitesse du LFO selon la position du RATE · À droite : délai du BBD sur 2 secondes pour trois réglages")),
          ("pb",)]
    b += [("h1", t("5. Footswitch, LEDs and tempo sync", "5. Footswitch, LED et synchro tempo")),
          ("bullets", [t("<b>Footswitch</b>: effect on / bypass. Bypass is fully transparent (the dry signal passes untouched) and the switch-over is a 10 ms crossfade, so there is no click.", "<b>Footswitch</b> : effet / bypass. Le bypass est totalement transparent (le signal direct passe intact) et le passage se fait en fondu de 10 ms : aucun clic."),
                       t("<b>LEDs</b>: the STATUS LED and the footswitch ring are lit when the effect is on; the RATE ring pulses with the LFO (it can stay steady: right-click &gt; Options &gt; <i>Rate ring pulses with the LFO</i>).", "<b>LED</b> : la LED STATUS et l'anneau du footswitch s'allument avec l'effet ; l'anneau du RATE pulse au rythme du LFO (il peut rester fixe : clic droit &gt; Options &gt; <i>Rate ring pulses with the LFO</i>).")]),
          ("h2", t("Tempo sync", "Synchro tempo")),
          ("p", t("Click the STATUS LED or the word <b>SYNC</b> next to it (or right-click &gt; Options &gt; <i>Rate synced to host tempo</i>). The LFO then follows the DAW tempo and the RATE knob selects the note value. The status line briefly shows the value and tempo (“TEMPO SYNC - 1/4 @ 120 BPM”), the STATUS LED blinks once per LFO cycle, in time with the DAW, and SYNC glows. Click again to return to the free RATE speed. The setting is saved with the project, can be automated and can be driven by MIDI (section 6).",
                  "Cliquez sur la LED STATUS ou sur le mot <b>SYNC</b> à côté (ou clic droit &gt; Options &gt; <i>Rate synced to host tempo</i>). Le LFO suit alors le tempo du DAW et le potard RATE choisit la valeur de note. La ligne d'état affiche brièvement la valeur et le tempo (« TEMPO SYNC - 1/4 @ 120 BPM »), la LED STATUS clignote à chaque cycle du LFO, en mesure avec le DAW, et SYNC s'illumine. Recliquez pour revenir à la vitesse libre. Le réglage est enregistré avec le projet, automatisable, et se pilote en MIDI (section 6).")),
          ("img", "status_lines.png", 72, t("Status line while adjusting: RATE, then tempo sync (it disappears afterwards)", "Ligne d'état pendant un réglage : RATE, puis synchro tempo (elle disparaît ensuite)"))]
    midi = [[t("Control", "Commande"), "Type"],
            ["Footswitch", t("Footswitch. Latching (default): 64-127 = on, 0-63 = bypass. Momentary: each press toggles.", "Footswitch. À accrochage (défaut) : 64-127 = effet, 0-63 = bypass. Momentané : chaque appui bascule.")],
            ["RATE", t("Continuous: 0-127 = whole knob range (note value when synced). Learn your expression pedal here.", "Continu : 0-127 = toute la course du potard (valeur de note en synchro). À apprendre sur la pédale d'expression.")],
            ["DIN. / DEPTH", t("Switch: 0-63 = DIN., 64-127 = DEPTH.", "Bascule : 0-63 = DIN., 64-127 = DEPTH.")],
            ["SYNC (STATUS LED)", t("Switch: 64-127 = tempo sync on, 0-63 = free RATE.", "Bascule : 64-127 = synchro tempo, 0-63 = RATE libre.")],
            ["Program Change", t("Not learnable: program n loads factory preset n+1 (program 0 = Classic Deep).", "Non apprenable : le programme n charge le preset usine n+1 (programme 0 = Classic Deep).")]]
    b += [("h1", "6. MIDI"),
          ("p", t("Every control can be driven from a MIDI footswitch, expression pedal or controller. <b>No CC is assigned by default</b>: everything goes through <b>MIDI Learn</b>.",
                  "Chaque commande peut être pilotée par un footswitch, une pédale d'expression ou un contrôleur MIDI. <b>Aucun CC n'est assigné par défaut</b> : tout passe par le <b>MIDI Learn</b>.")),
          ("bullets", [t("<b>Right-click a control</b> (RATE knob, DIN. / DEPTH switch, footswitch, STATUS LED or the word SYNC) and choose <b>MIDI Learn: &lt;control&gt; (CC n / none)</b>.", "<b>Clic droit sur une commande</b> (potard RATE, switch DIN. / DEPTH, footswitch, LED STATUS ou mot SYNC) puis <b>MIDI Learn: &lt;commande&gt; (CC n / none)</b>."),
                       t("The status line shows <b>MIDI LEARN: move a control for X</b> (it stays on while waiting). Move a pedal or press a button: the first CC received is assigned and the status line confirms <b>X = CC n</b> for 2 seconds.", "La ligne d'état affiche <b>MIDI LEARN: move a control for X</b> (elle reste affichée pendant l'attente). Bougez une pédale ou appuyez sur un bouton : le premier CC reçu est assigné et la ligne d'état confirme <b>X = CC n</b> pendant 2 secondes."),
                       t("<b>Clear MIDI: &lt;control&gt;</b> removes the assignment; <b>Cancel MIDI learn</b> (or choosing the same Learn again) stops waiting. A CC already used by another control is taken away from it.", "<b>Clear MIDI: &lt;commande&gt;</b> supprime l'assignation ; <b>Cancel MIDI learn</b> (ou rechoisir le même Learn) arrête l'attente. Un CC déjà utilisé par une autre commande lui est retiré."),
                       t("<b>Right-click elsewhere &gt; MIDI</b>: <b>Channel</b> (Omni by default or 1 to 16), <b>Learn</b> for every control with its current CC, <b>Clear all MIDI assignments</b>, latching or momentary footswitch.", "<b>Clic droit ailleurs &gt; MIDI</b> : <b>Channel</b> (Omni par défaut ou 1 à 16), <b>Learn</b> de chaque commande avec son CC actuel, <b>Clear all MIDI assignments</b>, footswitch à accrochage ou momentané."),
                       t("Assignments are saved with the project; all parameters can also be automated from the DAW.", "Les assignations sont enregistrées avec le projet ; tous les paramètres sont aussi automatisables depuis le DAW."),
                       t("<b>Older projects</b>: a project that still had the former factory assignments, untouched, opens with no assignment; a project in which you had changed an assignment keeps all its assignments.", "<b>Anciens projets</b> : un projet resté sur les anciennes assignations d'usine, jamais modifiées, s'ouvre sans aucune assignation ; un projet où vous aviez changé une assignation garde toutes ses assignations.")]),
          ("keep", [("space", 1), ("table", midi, [42, None])]),
          ("cond", 120),
          ("h1", t("7. Window and status line", "7. Fenêtre et ligne d'état")),
          ("bullets", [t("The window opens at the default size, <b>60 %</b> unless you choose another one, the same as Holyverb and the other NINE HANDS | DSP pedals, and can never be made smaller than 60 %.", "La fenêtre s'ouvre à la taille par défaut, <b>60 %</b> sauf si vous en choisissez une autre, comme Holyverb et les autres pédales NINE HANDS | DSP, et ne peut jamais être plus petite que 60 %."),
                       t("Right-click &gt; <b>Plugin size</b>: <b>60 %</b>, <b>75 %</b> or <b>100 %</b> for this window (the current size is ticked); <b>(default)</b> is shown next to the default size you have chosen. You can also enlarge the window from its corner, up to 150 %.", "Clic droit &gt; <b>Plugin size</b> : <b>60 %</b>, <b>75 %</b> ou <b>100 %</b> pour cette fenêtre (la taille actuelle est cochée) ; <b>(default)</b> est affiché à côté de la taille par défaut que vous avez choisie. On peut aussi agrandir la fenêtre par son coin, jusqu'à 150 %."),
                       t("<b>Plugin size &gt; Default size (new windows)</b>: chooses the size at which every new Small Tone window opens (a setting common to all instances, saved on your computer); the open window takes this size straight away.", "<b>Plugin size &gt; Default size (new windows)</b> : choisit la taille d'ouverture de toutes les nouvelles fenêtres de Small Tone (réglage commun à toutes les instances, enregistré sur l'ordinateur) ; la fenêtre ouverte prend aussitôt cette taille."),
                       t("Once the window of an instance has been resized (menu or corner), that size is saved with the project and stays this instance's size when the project is reopened; an instance whose window was never resized opens at the default size.", "Dès que la fenêtre d'une instance a été redimensionnée (menu ou coin), cette taille est enregistrée avec le projet et reste celle de l'instance à la réouverture ; une instance dont la fenêtre n'a jamais été redimensionnée s'ouvre à la taille par défaut."),
                       t("The status line under the NINE HANDS | DSP logo only appears while you adjust something (speed, mode, footswitch, preset, tempo sync, MIDI) and fades out after about two seconds, leaving the pedal clean. It stays on while a MIDI Learn is waiting.", "La ligne d'état sous le logo NINE HANDS | DSP n'apparaît que pendant un réglage (vitesse, mode, footswitch, preset, synchro tempo, MIDI) et s'efface en fondu après deux secondes environ, laissant la pédale nette. Elle reste affichée tant qu'un MIDI Learn attend.")]),
          ("keep", [("h2", t("Right-click menu", "Menu du clic droit")),
                    ("table", [[t("Entry", "Entrée"), t("Content", "Contenu")],
                               [t("MIDI Learn (on a control)", "MIDI Learn (sur une commande)"), "MIDI Learn / Clear MIDI / Cancel MIDI learn"],
                               ["Factory presets", t("9 presets (section 8)", "9 presets (section 8)")],
                               ["Load / Save user preset", "User 1 ... 9"],
                               ["Plugin size", "60 % · 75 % · 100 % · Default size (new windows)"],
                               ["Options", t("Rate synced to host tempo · Stereo spread (right channel LFO inverted) · BBD hiss · Rate ring pulses with the LFO", "Rate synced to host tempo · Stereo spread (LFO inversé à droite) · BBD hiss (souffle) · Rate ring pulses with the LFO (anneau qui pulse)")],
                               ["MIDI", t("Channel · Learn x4 · Clear all MIDI assignments · latching / momentary footswitch", "Channel · Learn x4 · Clear all MIDI assignments · footswitch à accrochage / momentané")]],
                     [52, None])]),
          ("pb",)]
    pre = [["Preset", "Switch", "RATE", t("Character", "Caractère")]]
    for i, (nm, hz, d) in enumerate(FACTORY):
        pre.append([nm, "DEPTH" if d else "DIN.", hz if en else hz.replace(".", ","), DESC[lang][i]])
    b += [("h1", "8. Presets"),
          ("p", t("The 9 factory presets are VST3 programs: they appear in the DAW preset menu (Reaper: preset field of the FX window) and under right-click &gt; Factory presets. 9 user presets are shared by all instances (%APPDATA%\\NINE HANDS | DSP\\Small Tone\\user_presets.xml or ~/Library/NINE HANDS | DSP/Small Tone/).",
                  "Les 9 presets usine sont des programmes VST3 : ils apparaissent dans le menu des presets du DAW (Reaper : champ preset de la fenêtre FX) et sous clic droit &gt; Factory presets. 9 presets utilisateur sont communs à toutes les instances (%APPDATA%\\NINE HANDS | DSP\\Small Tone\\user_presets.xml ou ~/Library/NINE HANDS | DSP/Small Tone/).")),
          ("table", pre, [38, 18, 20, None]),
          ("h1", t("9. Tips", "9. Conseils")),
          ("bullets", [t("<b>Reaper chain</b>: place Small Tone before your amp simulator (Two Notes Genome...), like a pedal in front of an amp, with your other NINE HANDS | DSP pedals. For a cleaner, more “studio” chorus, try it after the amp sim instead (FX-loop style).", "<b>Chaîne Reaper</b> : placez Small Tone avant la simulation d'ampli (Two Notes Genome...), comme une pédale devant un ampli, avec vos autres pédales NINE HANDS | DSP. Pour un chorus plus propre, plus « studio », essayez-le après la simulation (façon boucle d'effets)."),
                       t("<b>7-string / low tunings</b>: the delayed signal is filtered below about 70 Hz, so a low G string keeps a firm, un-chorused fundamental. For heavy low riffs prefer DIN. or the Bass Chorus preset; keep DEPTH for chords and cleans.", "<b>7 cordes / accordages graves</b> : le signal retardé est filtré sous 70 Hz environ, un Sol grave garde une fondamentale ferme, sans chorus. Pour les riffs graves préférez DIN. ou le preset Bass Chorus ; gardez DEPTH pour les accords et les sons clairs."),
                       t("<b>Stereo</b>: the original pedal is mono. Right-click &gt; Options &gt; Stereo spread inverts the LFO on the right channel for a wide image.", "<b>Stéréo</b> : la pédale d'origine est mono. Clic droit &gt; Options &gt; Stereo spread inverse le LFO du canal droit pour une image large."),
                       t("<b>Expression pedal</b>: learn RATE on your expression pedal (MIDI Learn) to sweep from slow chorus to fast rotary in real time; learn SYNC on a MIDI footswitch to switch tempo sync on stage.", "<b>Pédale d'expression</b> : apprenez RATE sur votre pédale d'expression (MIDI Learn) pour passer en direct du chorus lent au rotary rapide ; apprenez SYNC sur un footswitch MIDI pour basculer la synchro tempo en live."),
                       t("Turn off <b>BBD hiss</b> (Options) for a perfectly silent background when stacking many tracks.", "Coupez le souffle du BBD (<b>BBD hiss</b>, Options) pour un fond parfaitement silencieux quand vous empilez beaucoup de pistes.")]),
          ("pb",),
          ("h1", t("10. Specifications", "10. Caractéristiques techniques")),
          ("table", [[t("Item", "Élément"), t("Value", "Valeur")],
                     ["Format", t("VST3 - Windows 64-bit, macOS universal (Apple Silicon + Intel) - NINE HANDS | DSP, Fx | Modulation", "VST3 - Windows 64 bits, macOS universel (Apple Silicon + Intel) - NINE HANDS | DSP, Fx | Modulation")],
                     [t("Original pedal", "Pédale d'origine"), "Electro-Harmonix Small Clone (EH-4600)"],
                     [t("Channels", "Canaux"), t("mono to stereo, stereo to stereo", "mono vers stéréo, stéréo vers stéréo")],
                     ["LFO", t("LM358 integrator (2.2 µF) + hysteresis comparator (120k / 470k), triangle 0.86 - 2.79 V, 0.42 - 9.4 Hz", "intégrateur LM358 (2,2 µF) + comparateur à hystérésis (120k / 470k), triangle 0,86 - 2,79 V, 0,42 - 9,4 Hz")],
                     [t("Delay", "Retard"), t("MN3207 BBD, 1024 stages, clock about 85 - 195 kHz, delay 1024 / (2 f) about 2.6 - 6 ms", "BBD MN3207, 1024 étages, horloge environ 85 - 195 kHz, délai 1024 / (2 f) environ 2,6 - 6 ms")],
                     [t("Filters", "Filtres"), t("4th-order anti-alias ~6.2 kHz, reconstruction ~5.6 kHz, wet path high-pass 70 Hz", "anti-repliement 4e ordre ~6,2 kHz, reconstruction ~5,6 kHz, passe-haut 70 Hz sur le signal traité")],
                     ["Mix", t("dry + delayed 50 / 50, level-compensated; bypass crossfade 10 ms; latency 0", "direct + retardé 50 / 50, niveau compensé ; fondu de bypass 10 ms ; latence 0")],
                     [t("Sample rates", "Fréquences d'échantillonnage"), t("44.1 - 192 kHz (LFO independent of the sample rate)", "44,1 - 192 kHz (LFO indépendant de la fréquence)")],
                     ["Presets", t("9 factory (VST3 programs) + 9 user presets shared by all instances", "9 usine (programmes VST3) + 9 utilisateur communs à toutes les instances")],
                     ["MIDI", t("MIDI Learn on every control (footswitch, Rate, Depth switch, Sync), no CC assigned by default, channel Omni / 1-16, latching or momentary footswitch, Program Change; saved with the project", "MIDI Learn sur chaque commande (footswitch, Rate, switch Depth, Sync), aucun CC assigné par défaut, canal Omni / 1-16, footswitch à accrochage ou momentané, Program Change ; enregistré avec le projet")],
                     [t("Window", "Fenêtre"), t("Plugin size 60 % / 75 % / 100 %, default size of new windows selectable (60 % at first), never smaller than 60 %, up to 150 % by the corner", "Plugin size 60 % / 75 % / 100 %, taille par défaut des nouvelles fenêtres au choix (60 % au départ), jamais moins de 60 %, jusqu'à 150 % par le coin")],
                     [t("Windows stability", "Stabilité Windows"), t("anti-freeze v2: the audio thread never calls the host, window refresh driven by a timer with a watchdog", "anti-gel v2 : le thread audio n'appelle jamais l'hôte, rafraîchissement de la fenêtre piloté par un timer avec chien de garde")]],
           [44, None])]
    return b


L.build(OUT, "Small Tone", VERSION, "#8B5CF6", "S M A L L &nbsp;&nbsp; T O N E", TEXTS, content,
        footer="Small Tone " + VERSION + " \u00b7 NINE HANDS | DSP")
