// Captures PNG de la fenetre reelle de Small Tone (meme code que le plugin), pour l'apercu et la notice.
#include "PluginProcessor.h"
#include "PluginEditor.h"
#include "BinaryData.h"
using namespace juce;

int main (int argc, char** argv)
{
    ScopedJuceInitialiser_GUI init;
    const String out = argc > 1 ? argv[1] : ".";
    SmallToneProcessor proc;
    proc.prepareToPlay (48000.0, 256);
    std::unique_ptr<AudioProcessorEditor> ed (proc.createEditor());
    auto* se = static_cast<SmallToneEditor*> (ed.get());
    std::printf ("taille par defaut : %d x %d\n", ed->getWidth(), ed->getHeight());

    auto pump = [] (int n) { for (int i = 0; i < n; ++i) MessageManager::getInstance()->runDispatchLoopUntil (35); };
    auto set = [&] (const char* id, float v) { if (auto* p = proc.apvts.getParameter (id)) p->setValueNotifyingHost (p->convertTo0to1 (v)); };
    auto run = [&] (int blocks) { AudioBuffer<float> b (2, 256); MidiBuffer m; for (int i = 0; i < blocks; ++i) { b.clear(); proc.processBlock (b, m); } };
    auto save = [&] (const String& name, float scale)
    {
        auto img = ed->createComponentSnapshot (ed->getLocalBounds(), true, scale);
        File f (out + "/" + name + ".png"); f.deleteFile();
        FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
        std::printf ("%s (%d x %d)\n", f.getFullPathName().toRawUTF8(), img.getWidth(), img.getHeight());
    };
    // etat : preset, effet, synchro ; status = texte de la ligne d'etat (vide = barre de presets)
    auto state = [&] (int preset, bool on, bool sync, int glowPc, const String& status)
    {
        proc.setCurrentProgram (preset);
        set ("on", on ? 1.f : 0.f); set ("sync", sync ? 1.f : 0.f);
        se->setGlowPercent (glowPc);
        run (40); pump (6);
        if (status.isNotEmpty()) se->flash (status, 60.0);
        se->settleForCapture();
        pump (2);
    };

    // fenetre par defaut (493 px, « 60 % »)
    se->forceRenderScale (2.0f);
    state (1, true, false, 100, {});
    save ("st_default", 2.0f);

    // rendu exact de la pedale seule (1235 x 1800)
    se->setWindowHeight (900);
    se->forceRenderScale (2.0f);
    pump (8);
    const float ex = 1800.0f / (float) ed->getHeight();
    state (1, true, false, 100, {});                         save ("st_exact_on", ex);
    state (0, false, false, 100, {});  set ("depth", 0.f); run (4); pump (3); se->settleForCapture(); pump (2);
                                                             save ("st_exact_bypass", ex);
    state (1, true, true, 100, "Tempo sync  1/4 @ 120 BPM"); save ("st_exact_sync", ex);
    state (1, true, false, 100, "Rate  1.5 Hz");             save ("st_exact_status", ex);
    state (1, true, false, 0, {});                           save ("st_glow_0", ex);
    state (1, true, false, 200, {});                         save ("st_glow_200", ex);
    se->setGlowPercent (100);

    // menus clic droit (design Octopus, NineHandsMenu.h) : rendu hors ecran avec le meme LookAndFeel que le plugin
    {
        NineHandsMenu::MenuLnf lnf;
        lnf.f = { Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize),
                  Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize) };
        struct It { String text; bool sep = false, sub = false, ticked = false, active = true; };
        auto render = [&] (const String& name, const String& title, const String& subtitle, int ico, const std::vector<It>& items, int hiIndex)
        {
            NineHandsMenu::Header hd (lnf.f, ico, Colour (0xffa98bff), title, subtitle);
            int w = 0, h = 0; hd.getIdealSize (w, h);
            const int border = lnf.getPopupMenuBorderSize();
            int totalH = border * 2 + h + 11, maxW = w;
            for (auto& it : items) { int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih); totalH += ih; maxW = jmax (maxW, iw + (it.sub ? 20 : 0)); }
            maxW += border * 2;
            Image img (Image::ARGB, maxW * 2, totalH * 2, true);
            Graphics g (img); g.addTransform (AffineTransform::scale (2.0f));
            lnf.drawPopupMenuBackground (g, maxW, totalH);
            int y = border;
            hd.setSize (maxW - border * 2, h);
            { Graphics::ScopedSaveState ss (g); g.setOrigin (border, y); hd.paint (g); }
            y += h;
            lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, 11 }, true, true, false, false, false, {}, {}, nullptr, nullptr); y += 11;
            for (size_t i = 0; i < items.size(); ++i)
            {
                const auto& it = items[i]; int iw, ih; lnf.getIdealPopupMenuItemSize (it.text, it.sep, 0, iw, ih);
                lnf.drawPopupMenuItem (g, { border, y, maxW - border * 2, ih }, it.sep, it.active, (int) i == hiIndex, it.ticked, it.sub, it.text, {}, nullptr, nullptr);
                y += ih;
            }
            File f (out + "/" + name + ".png"); f.deleteFile();
            FileOutputStream os (f); PNGImageFormat().writeImageToStream (img, os);
            std::printf ("%s\n", f.getFullPathName().toRawUTF8());
        };
        render ("st_menu", "Small Tone", "Analog chorus  v2.0.0", NineHandsMenu::icoPedal,
                { { "Plugin size", false, true }, { "Glow (halo of the lights)", false, true }, { "", true },
                  { "Factory presets", false, true }, { "Load user preset", false, true }, { "Save user preset", false, true }, { "", true },
                  { "Settings", false, true }, { "MIDI", false, true }, { "", true },
                  { "Small Tone v2.0.0  NINE HANDS | DSP", false, false, false, false } }, 1);
        std::vector<It> g;
        for (int pc : { 0, 25, 50, 75, 100, 125, 150, 175, 200 })
            g.push_back ({ "Glow " + String (pc) + " %" + (pc == 0 ? "  (off)" : pc == 100 ? "  (default)" : ""), false, false, pc == 100 });
        render ("st_menu_glow", "Glow", "Halo of the lights", NineHandsMenu::icoGlow, g, 6);
        render ("st_menu_knob", "Rate", "MIDI: not assigned", NineHandsMenu::icoKnob,
                { { "MIDI Learn: Rate" }, { "Clear MIDI: Rate", false, false, false, false }, { "", true },
                  { "Plugin size", false, true }, { "Glow (halo of the lights)", false, true } }, 0);
    }
    ed.reset();
    return 0;
}
