#pragma once
#include <juce_gui_basics/juce_gui_basics.h>
#include <juce_audio_processors/juce_audio_processors.h>
#include "PluginProcessor.h"
#include "Layout.h"
#include "NineHandsMenu.h"

//==============================================================================
// SMALL TONE v2 (NINE HANDS | DSP) : pedale simple, fond 1235 x 1800 px plein cadre (repere 617,5 x 900, Layout.h).
// Le fond contient boitier, plaques, potard (sans repere), LED eteinte, footswitch et jacks (pieces photo du kit) ;
// l'editeur dessine par-dessus : halos (dosés par le reglage Glow du clic droit), anneaux allumes, LED, inverseur,
// serigraphie vectorielle (Poppins), logo NINE HANDS | DSP, repere du potard, pastille presets / ligne d'etat.
//==============================================================================
class SmallToneEditor : public juce::AudioProcessorEditor,
                        private juce::Timer
{
public:
    explicit SmallToneEditor (SmallToneProcessor&);
    ~SmallToneEditor() override;

    void paint (juce::Graphics&) override;
    void resized() override;
    void parentHierarchyChanged() override;

    void mouseDown (const juce::MouseEvent&) override;
    void mouseDrag (const juce::MouseEvent&) override;
    void mouseUp (const juce::MouseEvent&) override;
    void mouseDoubleClick (const juce::MouseEvent&) override;
    void mouseMove (const juce::MouseEvent&) override;
    void mouseExit (const juce::MouseEvent&) override;
    void mouseWheelMove (const juce::MouseEvent&, const juce::MouseWheelDetails&) override;

    static constexpr float baseW = layout::frameW, baseH = layout::frameH;
    static constexpr int numSizes = 3;           // 60 % (defaut) / 75 % / 100 %
    static int sizeHeight (int idx);
    void setWindowHeight (int h);
    // outil de rendu (captures) : echelle forcee, etat lumineux immediat, menu
    void forceRenderScale (float sc) { forcedScale = sc; rebuildCaches (sc); }
    void settleForCapture();
    void setGlowPercent (int pc);
    void flash (const juce::String& text, double seconds = 2.5);

private:
    void timerCallback() override;
    void visibilityChanged() override;
    void useSoftwareRenderer();
    float physicalScale() const;
    void askRepaint (juce::Rectangle<float> unitsRect);
    void rebuildCaches (float sc = 0.0f);
    float k() const { return (float) getHeight() / baseH; }
    juce::Point<float> toUnits (juce::Point<float> p) const { return p / k(); }

    enum class Hit { none, knob, toggle, din, depth, foot, led, presetPrev, presetName, presetNext };
    Hit hitAt (juce::Point<float> u) const;

    void setParam (const juce::String& id, float plain);
    void setRate (float r01);
    juce::String rateText() const;
    juce::String syncText() const;
    juce::String presetLine() const;
    void stepPreset (int delta);
    void showPresetMenu();
    void showContextMenu (int learnIdx = -1);
    void askUserPresetName (int slot);
    void buildPrint();

    void drawGlows (juce::Graphics&);
    void drawFootRing (juce::Graphics&);
    void drawPrint (juce::Graphics&);
    void drawIndex (juce::Graphics&);
    void drawBar (juce::Graphics&);

    SmallToneProcessor& proc;
    NineHandsMenu::MenuLnf menuLnf;
    juce::Typeface::Ptr mediumFace, boldFace, lightFace, regularFace;
    std::unique_ptr<juce::Drawable> logo;
    juce::Path printPath, titlePath, syncPath;      // serigraphie (unites du plugin) ; titre SMALL TONE (contour violet) ; SYNC
    juce::Rectangle<float> syncHit, dinHit, depthHit;

    juce::Image background, bgScaled, glowRing, ringCore, glowLed, ledOn, fsRefl, toggleStrip;
    int cacheW = 0, cacheH = 0;
    float cacheScale = 0.0f, forcedScale = 0.0f;
    int resizeSettle = 0, openHeight = 0;
    void* lastPeer = nullptr;
    double lastPaintMs = 0.0, repaintAskedMs = 0.0, lastScaleCheckMs = 0.0, lastRendererCheckMs = 0.0;

    // etat affiche
    float glow = 1.0f;                              // reglage Glow (1 = 100 %)
    float ringLevel = 1.0f, ledLevel = 1.0f, footLevel = 1.0f, syncLevel = 0.0f;
    float ledFlash = 0.0f; bool ledArmed = false;
    bool footDown = false;
    bool shownDeep = true; double toggleMidUntil = 0.0;
    Hit dragging = Hit::none, hover = Hit::none;
    float dragStartRate = 0.0f; juce::Point<float> dragStart;

    // pastille unique : barre de presets au repos, ligne d'etat pendant les reglages (fondu croise)
    juce::String statusText, presetText;
    double statusUntil = 0.0;
    float statusAlpha = 0.0f;
    float lastRate = -1.0f; bool lastDeep = false, lastOn = false, lastSync = false;
    int lastPresetCounter = 0;

    // dernier etat dessine (on ne redessine une zone que si elle a change)
    float dRate = -1.0f, dRing = -1.0f, dLed = -1.0f, dFoot = -1.0f, dSync = -1.0f, dStatus = -1.0f;
    bool dDeep = false, dMoving = false, dFootDown = false;
    Hit dHover = Hit::none;
    juce::String dStatusText, dPresetText;

    std::unique_ptr<juce::AlertWindow> nameDialog;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SmallToneEditor)
};
