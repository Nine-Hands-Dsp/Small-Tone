// genere par tools/make_art.py - ne pas modifier a la main (repere 617.5 x 900.0 = fond 1235 x 1800 px / 2)
#pragma once
#include <juce_graphics/juce_graphics.h>
namespace layout
{
    constexpr float frameW = 617.50f, frameH = 900.00f;
    const juce::Point<float> knobPos { 308.75f, 175.20f }; const float knobR = 72.81f;
    const float indexR0 = 21.84f, indexR1 = 66.98f, indexW = 5.46f;   // repere blanc du potard
    const juce::Point<float> ledPos { 508.15f, 181.26f }; const float ledS = 26.54f;
    const juce::Point<float> fsPos { 308.75f, 684.77f }; const float footR = 37.54f, fsS = 188.29f;
    const juce::Point<float> togglePos { 98.63f, 181.26f }; const float toggleS = 91.01f;
    const juce::Rectangle<float> glowRing { 148.97f, 15.17f, 319.55f, 319.55f }, glowLed { 416.95f, 90.00f, 182.02f, 182.02f };
    const float fsRingR = 40.45f, fsRingW = 2.53f;   // anneau lumineux dans la gorge du footswitch (dessin d'Octopus)
    const juce::Rectangle<float> presetRect { 108.53f, 800.14f, 400.45f, 38.02f };   // pastille unique : barre de presets / ligne d'etat
    const float presetFont = 23.0f;
    const juce::Rectangle<float> boxRect { 0.00f, 21.49f, 617.50f, 878.51f };
    // serigraphie vectorielle : texte, police (0 medium, 1 bold, 2 light), taille em, espacement, x, y, rotation, alignement (0 centre, 1 gauche)
    struct Txt { const char* s; int font; float em, track, x, y, rot; int align; };
    const Txt texts[] = {
        { "DIN.", 1, 15.17f, 1.62f, 98.63f, 126.66f, 0.00f, 0 },
        { "DEPTH", 1, 17.19f, 1.82f, 98.63f, 243.96f, 0.00f, 0 },
        { "RATE", 1, 19.21f, 2.43f, 308.75f, 296.54f, 0.00f, 0 },
        { "STATUS", 1, 17.19f, 1.82f, 512.20f, 237.89f, 0.00f, 0 },
        { "SYNC", 1, 13.65f, 1.62f, 527.87f, 181.26f, 0.00f, 1 },
        { "SMALL", 1, 93.03f, 2.02f, 308.75f, 444.19f, 0.00f, 0 },
        { "TONE", 1, 93.03f, 2.02f, 308.75f, 532.16f, 0.00f, 0 },
        { "FULL-CHORUS", 2, 26.29f, 2.63f, 308.75f, 589.80f, 0.00f, 0 },
        { "OUTPUT", 1, 17.19f, 1.82f, 98.63f, 61.94f, 0.00f, 0 },
        { "INPUT", 1, 17.19f, 1.82f, 512.44f, 61.94f, 0.00f, 0 }
    };
    struct Tick { float x0, y0, x1, y1, w; };
    const Tick ticks[] = { { 242.25f, 241.70f, 232.24f, 251.71f, 3.44f }, { 232.67f, 230.47f, 224.48f, 236.42f, 2.43f }, { 224.96f, 217.89f, 215.95f, 222.48f, 2.43f }, { 219.31f, 204.26f, 209.69f, 207.38f, 2.43f }, { 215.86f, 189.91f, 205.88f, 191.49f, 2.43f }, { 214.71f, 175.20f, 200.55f, 175.20f, 3.44f }, { 215.86f, 160.48f, 205.88f, 158.90f, 2.43f }, { 219.31f, 146.14f, 209.69f, 143.01f, 2.43f }, { 224.96f, 132.50f, 215.95f, 127.91f, 2.43f }, { 232.67f, 119.92f, 224.48f, 113.97f, 2.43f }, { 242.25f, 108.70f, 232.24f, 98.69f, 3.44f }, { 253.47f, 99.11f, 247.53f, 90.93f, 2.43f }, { 266.05f, 91.40f, 261.46f, 82.39f, 2.43f }, { 279.69f, 85.75f, 276.56f, 76.14f, 2.43f }, { 294.04f, 82.31f, 292.46f, 72.32f, 2.43f }, { 308.75f, 81.15f, 308.75f, 66.99f, 3.44f }, { 323.46f, 82.31f, 325.04f, 72.32f, 2.43f }, { 337.81f, 85.75f, 340.94f, 76.14f, 2.43f }, { 351.45f, 91.40f, 356.04f, 82.39f, 2.43f }, { 364.03f, 99.11f, 369.97f, 90.93f, 2.43f }, { 375.25f, 108.70f, 385.26f, 98.69f, 3.44f }, { 384.83f, 119.92f, 393.02f, 113.97f, 2.43f }, { 392.54f, 132.50f, 401.55f, 127.91f, 2.43f }, { 398.19f, 146.14f, 407.81f, 143.01f, 2.43f }, { 401.64f, 160.48f, 411.62f, 158.90f, 2.43f }, { 402.79f, 175.20f, 416.95f, 175.20f, 3.44f }, { 401.64f, 189.91f, 411.62f, 191.49f, 2.43f }, { 398.19f, 204.26f, 407.81f, 207.38f, 2.43f }, { 392.54f, 217.89f, 401.55f, 222.48f, 2.43f }, { 384.83f, 230.47f, 393.02f, 236.42f, 2.43f }, { 375.25f, 241.70f, 385.26f, 251.71f, 3.44f } };
    const juce::Point<float> logoPos { 308.75f, 864.86f }; const float logoW = 192.13f;
}
