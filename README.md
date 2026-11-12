# Small Tone — NINE HANDS | DSP

Chorus analogique **VST3** (Windows 64 bits + macOS universel Apple Silicon/Intel) au format pédale,
modélisé composant par composant sur l'Electro-Harmonix **Small Clone** (EH-4600) : LFO LM358, horloge CD4047,
ligne à retard BBD MN3207 de 1024 étages. Version 2 : pédale entièrement redessinée (boîtier violet anodisé,
plaques noires biseautées, pièces photo, jacks sur le dessus), halos réglables (**Glow**) et menus clic droit NINE HANDS | DSP.

<p align="center">
  <a href="https://github.com/Nine-Hands-Dsp/Small-Tone/releases/latest/download/SmallTone-VST3-Windows.zip"><img alt="Télécharger pour Windows" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-Windows-0078D6?style=for-the-badge"></a>
  <a href="https://github.com/Nine-Hands-Dsp/Small-Tone/releases/latest/download/SmallTone-VST3-macOS.zip"><img alt="Télécharger pour macOS" src="https://img.shields.io/badge/%E2%AC%87%20T%C3%A9l%C3%A9charger-macOS-111111?style=for-the-badge&logo=apple&logoColor=white"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Small-Tone/releases/latest/download/SmallTone-Notice.pdf"><img alt="Télécharger la notice (PDF)" src="https://img.shields.io/badge/%F0%9F%93%96%20Notice-PDF-919496?style=for-the-badge"></a>
  <br>
  <a href="https://github.com/Nine-Hands-Dsp/Small-Tone/releases/latest"><img alt="Dernière version" src="https://img.shields.io/github/v/release/Nine-Hands-Dsp/Small-Tone?label=derni%C3%A8re%20version&color=919496"></a>
</p>

## Compiler avec GitHub
Un push sur `main` lance l'onglet **Actions** → *Build Small Tone VST3 (Windows + macOS)* : test du moteur chorus
(`dsp_test.cpp`), builds Windows et macOS, puis publication dans **Releases** (`SmallTone-VST3-Windows.zip`,
`SmallTone-VST3-macOS.zip`, `SmallTone-Notice.pdf`, liens fixes ci-dessus).

## Installation
- **Windows** : copie `Small Tone.vst3` dans `C:\Program Files\Common Files\VST3\`
- **macOS** : copie `Small Tone.vst3` dans `~/Library/Audio/Plug-Ins/VST3/` puis lance une fois
  `xattr -cr ~/Library/Audio/Plug-Ins/VST3/"Small Tone.vst3"`
- **Reaper** : re-scanne les plug-ins. Le plugin apparaît comme **Small Tone (NINE HANDS | DSP)**.

## Commandes
| Commande | Rôle |
|---|---|
| **RATE** | vitesse du LFO, ≈ 0,42 Hz → 9,4 Hz, courbe du potard 1M « ccw log » d'origine. Tirer haut/bas ou gauche/droite, molette, **Maj** = 4× plus fin, double-clic = milieu (≈ 2 Hz). L'anneau violet pulse avec le LFO |
| Inverseur **DIN. / DEPTH** | haut = **DIN.** (léger, doublage), bas = **DEPTH** (profond, le son « liquide »). Clic sur le levier ou sur les inscriptions |
| Footswitch | effet / bypass (anneau de la gorge, LED STATUS et anneau du RATE s'allument) |
| LED **STATUS** / mot **SYNC** | clic = synchro du RATE sur le tempo du DAW (le potard choisit la valeur de note) ; la LED clignote en mesure et SYNC s'illumine |
| Pastille presets / ligne d'état | au repos : flèches et nom du preset (clic = menu) ; pendant un réglage : la valeur en direct, puis retour à la barre de presets |
| OUTPUT / INPUT | jacks sur le dessus de la pédale |

Comme sur l'original, en **DEPTH** le condensateur de 10 µF arrondit le balayage : plus le RATE est rapide,
plus la modulation devient douce. Basculer l'inverseur fait glisser le délai pendant ~½ s (charge du 10 µF).

## Presets
Classic Deep, Grunge Water (Kurt Cobain, « Come As You Are »), Slow Ocean, Seasick, Rotary Fast, Subtle Thickener,
Shimmer Clean, Warble, Bass Chorus (programmes VST3). Clic droit → 9 presets utilisateur communs à toutes les instances.

## Clic droit (n'importe où, menu ouvert à l'endroit du clic)
- **Plugin size** : 60 % (taille minimale, par défaut), 75 %, 100 %, ou tirer le coin jusqu'à 150 % ;
  *Default size (new windows)* : taille d'ouverture des nouvelles fenêtres, commune à toutes les instances.
- **Glow (halo of the lights)** : 25 %, 50 %, 75 % ou 100 % (défaut), halo des lumières seulement.
- **Factory presets / Load user preset / Save user preset**.
- **Settings** : RATE synchronisé au tempo, stéréo élargie (LFO inversé à droite), souffle du BBD, anneau du RATE qui pulse avec le LFO.
- **MIDI** : canal, *Learn* (aucun CC assigné par défaut), *Clear all MIDI assignments*, footswitch MIDI à accrochage
  ou momentané, Program Change n = preset n+1. Clic droit sur une commande → « MIDI Learn » / « Clear MIDI ».

## Fonctionnement (résumé)
- **LFO** : intégrateur LM358 + 2,2 µF et comparateur à hystérésis 120k/470k : triangle 0,86 → 2,79 V,
  résistance de charge = potard 1M log + 47k.
- **DEPTH** : sortie LFO → 4,7k → nœud 10 µF → 39k → horloge. DIN. = shunt à la masse (diviseur ×0,53 + filtre plus rapide).
- **Horloge + BBD** : ≈ 75 → 200 kHz, délai 1024 / (2·f) ≈ 2,6 → 6,5 ms ; filtres anti-repliement et de
  reconstruction ~6 kHz, saturation douce du MN3207, léger souffle.
- **Mix** : sec + retardé à parts égales, niveau compensé.

Notice d'utilisation (français) : `docs/SmallTone_Notice_FR_v2.0.1.pdf`. Polices Poppins et Barlow Condensed (licence SIL OFL).

## Versions
- v1.1.0 : anti-gel v2 (JUCE 8.0.15, caches refaits par le timer, chien de garde, aucun appel à l'hôte depuis le thread audio)
- v1.1.1 : menu de taille de fenêtre en % (plus de taille en pixels)
- v1.2.0 : MIDI Learn au clic droit sur chaque commande
- v1.3.0 : taille par défaut des nouvelles fenêtres au choix
- v1.3.1 : plus aucun CC MIDI assigné par défaut
- v2.0.0 : pédale entièrement refaite (image 1235 × 1800 plein cadre, pièces photo, jacks sur le dessus, sérigraphie vectorielle Poppins,
  bevel des plaques), halo du footswitch façon Octopus, réglage Glow 25 / 50 / 75 / 100 %, pastille presets / ligne d'état unique,
  menus clic droit style Octopus, notice en français
- v2.0.1 : chorus plus présent (balayage DEPTH ≈ 3 → 6,3 ms, DIN. deux fois plus marqué, signal traité au même niveau que le direct)
