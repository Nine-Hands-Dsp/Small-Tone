#include "PluginEditor.h"
#include "BinaryData.h"
#include "WigaWindowSize.h"
#include "NineHandsGlow.h"

using namespace juce;

namespace
{
    const Colour ink (0xffeeecf2);                 // serigraphie blanche
    const Colour titleEdge (0xff7a5cbe);           // contour violet du titre SMALL TONE
    const Colour ringViolet (0xff966cff), ringCoreCol (0xffd6c6ff);
    const Colour syncLit (0xffc8d7ff), ledBlue (0xff4f8cff);
    const Colour barFill (0xff08080a), barEdge (0xff3a3842), barInk (0xffe8e8ec);
    const Colour menuAccent (0xffa98bff);          // pastille des en-tetes de menu (violet de la pedale)
    constexpr float knobSweep = MathConstants<float>::pi * 0.75f;      // +/- 135 degres (graduations)
    constexpr float arrowW = 34.0f;
}

static Image png (const void* d, int n) { return ImageCache::getFromMemory (d, n); }

//==============================================================================
SmallToneEditor::SmallToneEditor (SmallToneProcessor& p)
    : AudioProcessorEditor (p), proc (p)
{
    background  = png (BinaryData::background_png, BinaryData::background_pngSize);
    glowRing    = png (BinaryData::glow_ring_png, BinaryData::glow_ring_pngSize);
    ringCore    = png (BinaryData::ring_core_png, BinaryData::ring_core_pngSize);
    glowLed     = png (BinaryData::glow_led_png, BinaryData::glow_led_pngSize);
    ledOn       = png (BinaryData::led_on_png, BinaryData::led_on_pngSize);
    fsRefl      = png (BinaryData::fs_refl_png, BinaryData::fs_refl_pngSize);
    toggleStrip = png (BinaryData::toggle_strip_png, BinaryData::toggle_strip_pngSize);
    mediumFace  = Typeface::createSystemTypefaceFor (BinaryData::PoppinsMedium_ttf, BinaryData::PoppinsMedium_ttfSize);
    boldFace    = Typeface::createSystemTypefaceFor (BinaryData::PoppinsBold_ttf, BinaryData::PoppinsBold_ttfSize);
    lightFace   = Typeface::createSystemTypefaceFor (BinaryData::PoppinsLight_ttf, BinaryData::PoppinsLight_ttfSize);
    regularFace = Typeface::createSystemTypefaceFor (BinaryData::PoppinsRegular_ttf, BinaryData::PoppinsRegular_ttfSize);
    menuLnf.f = { regularFace, mediumFace, boldFace };
    if (auto xml = XmlDocument::parse (String::fromUTF8 (BinaryData::NineHandsLogo_svg, BinaryData::NineHandsLogo_svgSize)))
        logo = Drawable::createFromSVG (*xml);
    buildPrint();
    glow = (float) NineHandsGlow::percent (JucePlugin_Name) / 100.0f;

    // taille : 493 px par defaut (« 60 % ») = taille minimale, proportions bloquees ;
    // ouverture a la taille enregistree pour cette instance, sinon a la taille par defaut choisie dans le menu
    const double aspect = (double) baseW / (double) baseH;
    const int h0 = sizeHeight (NineHandsWindow::openIndex (JucePlugin_Name, proc.uiSizeIdx.load(), numSizes));
    setResizable (true, true);
    setResizeLimits (roundToInt (stui::heightDefault * aspect), stui::heightDefault,
                     roundToInt (stui::heightMax * aspect), stui::heightMax);
    getConstrainer()->setFixedAspectRatio (aspect);
    hostLock.setLimits (roundToInt (stui::heightDefault * aspect), stui::heightDefault, roundToInt (stui::heightMax * aspect), stui::heightMax);
    setOpaque (true);
    openHeight = h0;
    setSize (roundToInt (h0 * aspect), h0);
    rebuildCaches();

    const bool on = proc.isOn();
    ringLevel = ledLevel = footLevel = on ? 1.0f : 0.0f;
    syncLevel = proc.apvts.getRawParameterValue ("sync")->load() > 0.5f ? 1.0f : 0.0f;
    shownDeep = proc.isDeep();
    lastRate = proc.getRate(); lastDeep = proc.isDeep(); lastOn = on; lastSync = syncLevel > 0.5f;
    lastPresetCounter = proc.presetCounter.load();
    presetText = presetLine();
    startTimerHz (30);
}

SmallToneEditor::~SmallToneEditor()
{
    PopupMenu::dismissAllActiveMenus();
    stopTimer();
}

//==============================================================================
// Anti-gel v2 (NINE HANDS | DSP) : moteur logiciel sous Windows, caches refaits par le timer seulement,
// chien de garde des redessins, aucun appel a l'hote depuis le thread audio (voir PluginProcessor).
void SmallToneEditor::useSoftwareRenderer()
{
    auto* peer = getPeer();
    if (peer != lastPeer) { lastPeer = peer; repaint(); }
   #if JUCE_WINDOWS
    if (peer != nullptr)
    {
        int sw = peer->getAvailableRenderingEngines().indexOf ("Software Renderer");
        if (sw < 0) sw = 0;
        if (peer->getCurrentRenderingEngine() != sw)
            peer->setCurrentRenderingEngine (sw);
    }
   #endif
}

void SmallToneEditor::parentHierarchyChanged() { useSoftwareRenderer(); hostLock.track (*this); }
void SmallToneEditor::visibilityChanged()      { useSoftwareRenderer(); if (isShowing()) repaint(); }

float SmallToneEditor::physicalScale() const
{
    if (forcedScale > 0.0f) return forcedScale;
    return jlimit (1.0f, 4.0f, (float) Component::getApproximateScaleFactorForComponent (this));
}

void SmallToneEditor::askRepaint (Rectangle<float> u)
{
    if (repaintAskedMs <= 0.0) repaintAskedMs = Time::getMillisecondCounterHiRes();
    repaint (u.transformedBy (AffineTransform::scale (k())).getSmallestIntegerContainer().expanded (2));
}

void SmallToneEditor::resized()
{
    // jamais de setSize ici ; seules les tailles choisies au menu sont enregistrees (pas celles tirees au coin)
    resizeSettle = 4;
}

int SmallToneEditor::sizeHeight (int idx)
{
    const int h[numSizes] = { stui::heightDefault, stui::height75, stui::height100 };
    return h[jlimit (0, numSizes - 1, idx)];
}

void SmallToneEditor::setWindowHeight (int h)
{
    h = jlimit (stui::heightDefault, stui::heightMax, h);
    setSize (roundToInt ((double) h * baseW / baseH), h);
    hostLock.enforce();
}

void SmallToneEditor::rebuildCaches (float sc)
{
    if (sc <= 0.0f) sc = cacheScale > 0.0f ? cacheScale : physicalScale();
    const int w = getWidth(), h = getHeight();
    if (w <= 0 || h <= 0) return;
    if (w == cacheW && h == cacheH && std::abs (sc - cacheScale) < 0.01f && bgScaled.isValid()) return;
    cacheW = w; cacheH = h; cacheScale = sc;
    const int pw = roundToInt ((float) w * sc), ph = roundToInt ((float) h * sc);
    bgScaled = (pw >= background.getWidth()) ? background : background.rescaled (pw, ph, Graphics::highResamplingQuality);
    repaint();
}

void SmallToneEditor::setGlowPercent (int pc)
{
    NineHandsGlow::setPercent (JucePlugin_Name, pc);
    glow = (float) jlimit (25, 100, pc) / 100.0f;
    repaint();
}

void SmallToneEditor::settleForCapture()
{
    const bool on = proc.isOn();
    ringLevel = on ? 1.0f : 0.0f; ledLevel = footLevel = on ? 1.0f : 0.0f;
    syncLevel = proc.apvts.getRawParameterValue ("sync")->load() > 0.5f ? 1.0f : 0.0f;
    if (syncLevel > 0.5f) ledLevel = on ? 1.0f : 0.55f;
    shownDeep = proc.isDeep(); toggleMidUntil = 0.0;
    presetText = presetLine();
    statusAlpha = Time::getMillisecondCounterHiRes() < statusUntil ? 1.0f : 0.0f;
    repaint();
}

//==============================================================================
// Serigraphie vectorielle (Layout.h) : construite une fois en chemins (unites du plugin)
//==============================================================================
static Path textPath (const layout::Txt& t, const Typeface::Ptr& face)
{
    const Font font (FontOptions (face).withPointHeight (t.em));
    const String s (t.s);
    float total = 0.0f;
    for (int i = 0; i < s.length(); ++i)
        total += GlyphArrangement::getStringWidth (font, String::charToString (s[i])) + (i > 0 ? t.track : 0.0f);
    const float base = (font.getAscent() - font.getDescent()) * 0.5f;
    GlyphArrangement ga;
    float x = t.align == 1 ? 0.0f : -total * 0.5f;
    for (int i = 0; i < s.length(); ++i)
    {
        const String ch = String::charToString (s[i]);
        ga.addLineOfText (font, ch, x, base);
        x += GlyphArrangement::getStringWidth (font, ch) + t.track;
    }
    Path p; ga.createPath (p);
    p.applyTransform (AffineTransform::rotation (-t.rot * MathConstants<float>::pi / 180.0f).translated (t.x, t.y));
    return p;
}

void SmallToneEditor::buildPrint()
{
    printPath.clear(); titlePath.clear(); syncPath.clear();
    auto faceOf = [this] (int f) { return f == 1 ? boldFace : (f == 2 ? lightFace : mediumFace); };
    for (const auto& t : layout::texts)
    {
        const auto p = textPath (t, faceOf (t.font));
        const String s (t.s);
        if (s == "SMALL" || s == "TONE") titlePath.addPath (p);
        else if (s == "SYNC")            { syncPath = p; syncHit = p.getBounds().expanded (8.0f, 9.0f); }
        else
        {
            printPath.addPath (p);
            if (s == "DIN.")  dinHit   = p.getBounds().expanded (10.0f, 8.0f);
            if (s == "DEPTH") depthHit = p.getBounds().expanded (8.0f, 8.0f);
        }
    }
    for (const auto& tk : layout::ticks)
    {
        Path seg; seg.startNewSubPath (tk.x0, tk.y0); seg.lineTo (tk.x1, tk.y1);
        Path stroked;
        PathStrokeType (tk.w, PathStrokeType::curved, PathStrokeType::rounded).createStrokedPath (stroked, seg);
        printPath.addPath (stroked);
    }
}

//==============================================================================
String SmallToneEditor::rateText() const
{
    const float r = proc.getRate();
    if (proc.apvts.getRawParameterValue ("sync")->load() > 0.5f)
        return "sync " + SmallToneProcessor::syncDivisionName (SmallToneProcessor::syncDivisionIndex (r));
    const double hz = smalltone::Engine::rateHz (r);
    return String (hz, hz < 1.0 ? 2 : 1) + " Hz";
}

String SmallToneEditor::syncText() const
{
    return SmallToneProcessor::syncDivisionName (SmallToneProcessor::syncDivisionIndex (proc.getRate()))
           + " @ " + String (proc.hostBpm.load(), 0) + " BPM";
}

String SmallToneEditor::presetLine() const
{
    return proc.presetName.isNotEmpty() ? proc.presetName : String ("Edited");
}

void SmallToneEditor::flash (const String& t, double seconds)
{
    statusText = t;
    statusUntil = Time::getMillisecondCounterHiRes() + seconds * 1000.0;
}

void SmallToneEditor::setParam (const String& id, float plain)
{
    if (auto* p = proc.apvts.getParameter (id))
    {
        p->beginChangeGesture();
        p->setValueNotifyingHost (p->convertTo0to1 (plain));
        p->endChangeGesture();
    }
}

void SmallToneEditor::setRate (float r)
{
    if (auto* p = proc.apvts.getParameter ("rate"))
        p->setValueNotifyingHost (jlimit (0.0f, 1.0f, r));
    proc.presetName = {};
}

//==============================================================================
void SmallToneEditor::timerCallback()
{
    const double now = Time::getMillisecondCounterHiRes();
    if (getPeer() != lastPeer || now - lastRendererCheckMs > 1000.0) { lastRendererCheckMs = now; useSoftwareRenderer(); }
    hostLock.track (*this);
    if (resizeSettle > 0 && --resizeSettle == 0) rebuildCaches();
    else if (resizeSettle == 0 && now - lastScaleCheckMs > 250.0)
    {
        lastScaleCheckMs = now;
        const float sc = physicalScale();
        if (std::abs (sc - cacheScale) > 0.01f) rebuildCaches (sc);
    }
    if (repaintAskedMs > 0.0 && isShowing() && now - repaintAskedMs > 1500.0 && lastPaintMs < repaintAskedMs)
    {
        repaintAskedMs = 0.0; lastPeer = nullptr;
        useSoftwareRenderer(); repaint();
    }

    // ---- reglages qui changent (souris, automation, MIDI) -> ligne d'etat ; chargement de preset -> barre seulement
    const float rate = proc.getRate();
    const bool deep = proc.isDeep(), on = proc.isOn(), sync = proc.apvts.getRawParameterValue ("sync")->load() > 0.5f;
    const int pc = proc.presetCounter.load();
    const bool presetLoaded = pc != lastPresetCounter;
    lastPresetCounter = pc;
    if (! presetLoaded)
    {
        if (std::abs (rate - lastRate) > 1.0e-4f) flash ("Rate  " + rateText());
        if (deep != lastDeep) flash (deep ? "Depth  (deep)" : "DIN.  (shallow)");
        if (on != lastOn)     flash (on ? "Effect on" : "Bypass", 1.6);
        if (sync != lastSync) flash (sync ? "Tempo sync  " + syncText() : "Tempo sync off  " + rateText());
    }
    lastRate = rate; lastDeep = deep; lastOn = on; lastSync = sync;

    if (const int lt = proc.learnTarget.load(); lt >= 0)
        flash ("MIDI LEARN  " + String (SmallToneProcessor::learnDef (lt).name), 0.25);
    if (const int learned = proc.lastLearned.exchange (-1); learned >= 0)
        flash (String (SmallToneProcessor::learnDef (learned).name) + " = CC " + String (proc.ccMap[learned].load()));

    const float st = now < statusUntil ? 1.0f : 0.0f;
    statusAlpha += (st - statusAlpha) * (st > statusAlpha ? 0.45f : 0.30f);      // ~120 ms a l'apparition, ~300 ms au retour
    if (statusAlpha < 0.005f) statusAlpha = 0.0f;
    if (statusAlpha > 0.995f) statusAlpha = 1.0f;
    presetText = presetLine();

    // ---- lumieres
    const bool follow = proc.apvts.getRawParameterValue ("ringlfo")->load() > 0.5f;
    const float lfo = proc.lfoVisual.load();
    const float ringTarget = on ? (follow ? 0.55f + 0.45f * lfo : 1.0f) : 0.0f;
    ringLevel += (ringTarget - ringLevel) * (ringTarget > ringLevel ? 0.45f : 0.28f);
    float ledTarget = on ? 1.0f : 0.0f;
    if (sync)
    {
        // synchro tempo : la LED STATUS clignote a chaque cycle du LFO (donc en mesure avec le DAW)
        if (lfo > 0.96f && ! ledArmed) { ledFlash = 1.0f; ledArmed = true; }
        if (lfo < 0.5f) ledArmed = false;
        ledFlash *= 0.84f;
        ledTarget = on ? 0.22f + 0.78f * ledFlash : 0.55f * ledFlash;
    }
    ledLevel  += (ledTarget - ledLevel) * (sync ? 0.6f : (ledTarget > ledLevel ? 0.45f : 0.28f));
    footLevel += ((on ? 1.0f : 0.0f) - footLevel) * (on ? 0.45f : 0.28f);
    syncLevel += ((sync ? 1.0f : 0.0f) - syncLevel) * 0.25f;
    for (auto* v : { &ringLevel, &ledLevel, &footLevel, &syncLevel })
    {
        if (*v < 0.003f) *v = 0.0f;
        if (*v > 0.997f) *v = 1.0f;
    }
    if (deep != shownDeep) { shownDeep = deep; toggleMidUntil = now + 55.0; }      // le levier passe par le point mort
    if (now - lastScaleCheckMs > 3000.0 && resizeSettle == 0)
        glow = (float) NineHandsGlow::percent (JucePlugin_Name) / 100.0f;           // reglage commun a toutes les fenetres

    // ---- redessins limites a ce qui change
    auto changed = [] (float& drawn, float v) { if (std::abs (drawn - v) < 0.003f) return false; drawn = v; return true; };
    const auto knobZone = layout::glowRing;
    if (changed (dRate, rate) | changed (dRing, ringLevel)) askRepaint (knobZone);
    if (changed (dLed, ledLevel) | changed (dSync, syncLevel)) { askRepaint (layout::glowLed); askRepaint (syncHit.expanded (12.0f)); }
    if (changed (dFoot, footLevel) || footDown != dFootDown)
    {
        dFootDown = footDown;
        askRepaint (Rectangle<float> (layout::fsS, layout::fsS).withCentre (layout::fsPos));
    }
    const bool moving = now < toggleMidUntil;
    if (shownDeep != dDeep || moving != dMoving)
    {
        dDeep = shownDeep; dMoving = moving;
        askRepaint (Rectangle<float> (layout::toggleS, layout::toggleS).withCentre (layout::togglePos));
    }
    if (changed (dStatus, statusAlpha) || statusText != dStatusText || presetText != dPresetText || hover != dHover)
    {
        dStatusText = statusText; dPresetText = presetText; dHover = hover;
        askRepaint (layout::presetRect.expanded (3.0f));
    }
}

//==============================================================================
void SmallToneEditor::paint (Graphics& g)
{
    lastPaintMs = Time::getMillisecondCounterHiRes();
    repaintAskedMs = 0.0;
    g.fillAll (Colour (0xff111112));          // derriere les jacks : le fond de l'image est transparent
    const Image& bg = bgScaled.isValid() ? bgScaled : background;
    g.setImageResamplingQuality (&bg == &background ? Graphics::highResamplingQuality : Graphics::lowResamplingQuality);
    if (bg.isValid()) g.drawImage (bg, getLocalBounds().toFloat());

    g.addTransform (AffineTransform::scale (k()));
    g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    drawGlows (g);
    // inverseur : meme rectangle pour les trois images (haut = DIN., milieu pendant la bascule, bas = DEPTH)
    if (toggleStrip.isValid())
    {
        const int fs = toggleStrip.getWidth();
        const bool moving = Time::getMillisecondCounterHiRes() < toggleMidUntil;
        const int row = moving ? 1 : (shownDeep ? 2 : 0);
        const auto r = Rectangle<float> (layout::toggleS, layout::toggleS).withCentre (layout::togglePos);
        g.setImageResamplingQuality (Graphics::highResamplingQuality);
        g.drawImage (toggleStrip, r.getX(), r.getY(), r.getWidth(), r.getHeight(), 0, row * fs, fs, fs);
        g.setImageResamplingQuality (Graphics::mediumResamplingQuality);
    }
    drawFootRing (g);
    drawPrint (g);
    drawIndex (g);
    drawBar (g);
}

void SmallToneEditor::drawGlows (Graphics& g)
{
    // halos sur la facade (calques alpha precalcules), doses par le reglage Glow (25 a 100 %), sous la serigraphie
    auto layer = [&] (const Image& im, Rectangle<float> r, float level)
    {
        if (level <= 0.003f || ! im.isValid()) return;
        g.setOpacity (jmin (1.0f, level)); g.drawImage (im, r);
        if (level > 1.0f) { g.setOpacity (jmin (1.0f, level - 1.0f)); g.drawImage (im, r); }
        g.setOpacity (1.0f);
    };
    layer (glowRing, layout::glowRing, ringLevel * glow);
    layer (ringCore, layout::glowRing, ringLevel);                      // l'anneau lui-meme n'est jamais dose
    layer (glowLed, layout::glowLed, ledLevel * glow);
    const float hs = layout::ledS * 0.5f;
    layer (ledOn, { layout::ledPos.x - hs, layout::ledPos.y - hs, hs * 2.0f, hs * 2.0f }, ledLevel);
    layer (fsRefl, Rectangle<float> (layout::fsS, layout::fsS).withCentre (layout::fsPos), footLevel * 0.35f);
}

void SmallToneEditor::drawFootRing (Graphics& g)
{
    // anneau lumineux dans la gorge du footswitch (dessin d'Octopus) : halo dose par Glow, trait net, coeur clair
    const auto c = layout::fsPos;
    const float lvl = footLevel;
    if (lvl > 0.003f)
    {
        Path ring;
        ring.addEllipse (c.x - layout::fsRingR, c.y - layout::fsRingR, layout::fsRingR * 2.0f, layout::fsRingR * 2.0f);
        const float kr = layout::fsRingR / 33.2f;
        if (glow > 0.0f)
            for (float hw = 20.0f; hw > 3.0f; hw -= 1.5f)
            {
                g.setColour (ringViolet.withAlpha (jmin (1.0f, 0.075f * glow) * lvl));
                g.strokePath (ring, PathStrokeType (hw * kr));
            }
        g.setColour (ringViolet.withAlpha (0.85f * lvl));
        g.strokePath (ring, PathStrokeType (layout::fsRingW));
        g.setColour (ringCoreCol.withAlpha (0.9f * lvl));
        g.strokePath (ring, PathStrokeType (layout::fsRingW * 0.42f));
    }
    if (footDown)       // bouton enfonce (fonctionnement d'Echoflex)
    {
        const float r = layout::footR * 0.98f;
        g.setColour (Colours::black.withAlpha (0.25f));
        g.fillEllipse (c.x - r, c.y - r, r * 2.0f, r * 2.0f);
    }
}

void SmallToneEditor::drawPrint (Graphics& g)
{
    g.setColour (ink);
    g.fillPath (printPath);
    // titre SMALL TONE : blanc legerement violace avec un fin contour violet
    g.setColour (titleEdge);
    g.strokePath (titlePath, PathStrokeType (3.2f, PathStrokeType::curved, PathStrokeType::rounded));
    g.setColour (Colour (0xfff4f2fa));
    g.fillPath (titlePath);
    // SYNC : s'eclaire en bleu quand la synchro tempo est active (halo dose par Glow)
    if (syncLevel > 0.003f && glow > 0.0f)
        for (float w = 7.0f; w > 1.0f; w -= 1.5f)
        {
            g.setColour (ledBlue.withAlpha (jmin (1.0f, 0.05f * glow) * syncLevel * (0.6f + 0.4f * ledLevel)));
            g.strokePath (syncPath, PathStrokeType (w, PathStrokeType::curved, PathStrokeType::rounded));
        }
    g.setColour (ink.interpolatedWith (syncLit, syncLevel));
    g.fillPath (syncPath);
    if (logo != nullptr)
    {
        const auto vb = logo->getDrawableBounds();
        const float w = layout::logoW, h = w * vb.getHeight() / jmax (1.0f, vb.getWidth());
        logo->drawWithin (g, { layout::logoPos.x - w * 0.5f, layout::logoPos.y - h * 0.5f, w, h }, RectanglePlacement::centred, 0.92f);
    }
}

void SmallToneEditor::drawIndex (Graphics& g)
{
    // repere blanc du potard : seul le repere tourne, les reflets du chapeau (dans le fond) restent fixes
    const auto c = layout::knobPos;
    const float a = (proc.getRate() - 0.5f) * 2.0f * knobSweep;
    const Point<float> dir (std::sin (a), -std::cos (a));
    Path line; line.startNewSubPath (c + dir * layout::indexR0); line.lineTo (c + dir * layout::indexR1);
    g.setColour (Colours::black.withAlpha (0.45f));
    g.strokePath (line, PathStrokeType (layout::indexW * 1.15f, PathStrokeType::curved, PathStrokeType::rounded),
                  AffineTransform::translation (layout::knobR * 0.010f, layout::knobR * 0.016f));
    const float facing = 0.5f + 0.5f * std::cos (a + MathConstants<float>::pi * 0.25f);
    g.setColour (Colour (0xfff6f6f8).withMultipliedBrightness (0.92f + 0.08f * facing));
    g.strokePath (line, PathStrokeType (layout::indexW, PathStrokeType::curved, PathStrokeType::rounded));
}

void SmallToneEditor::drawBar (Graphics& g)
{
    // pastille unique (400 x 38, reference Strong Pickle) : barre de presets au repos, ligne d'etat pendant les reglages
    const auto r = layout::presetRect;
    const bool barHot = hover == Hit::presetPrev || hover == Hit::presetName || hover == Hit::presetNext;
    g.setColour (barFill);
    g.fillRoundedRectangle (r, r.getHeight() * 0.5f);
    g.setColour (barEdge.brighter (barHot && statusAlpha <= 0.0f ? 0.6f : 0.0f));
    g.drawRoundedRectangle (r.reduced (0.5f), r.getHeight() * 0.5f, 1.0f);
    const Font f (FontOptions (mediumFace).withHeight (layout::presetFont));
    g.setFont (f);
    if (statusAlpha > 0.0f)
    {
        g.setColour (barInk.withAlpha (statusAlpha));
        g.drawFittedText (statusText, r.reduced (r.getHeight() * 0.5f, 0.0f).toNearestInt(), Justification::centred, 1, 0.6f);
    }
    const float a = 1.0f - statusAlpha;
    if (a <= 0.0f) return;
    auto arrow = [&] (Rectangle<float> ar, bool left, bool hot)
    {
        Path p; const auto c = ar.getCentre(); const float sz = 5.5f;
        if (left) p.addTriangle (c.x + sz * 0.6f, c.y - sz, c.x + sz * 0.6f, c.y + sz, c.x - sz * 0.8f, c.y);
        else      p.addTriangle (c.x - sz * 0.6f, c.y - sz, c.x - sz * 0.6f, c.y + sz, c.x + sz * 0.8f, c.y);
        g.setColour (barInk.withAlpha ((hot ? 1.0f : 0.6f) * a));
        g.fillPath (p);
    };
    arrow (r.withWidth (arrowW), true, hover == Hit::presetPrev);
    arrow (r.withTrimmedLeft (r.getWidth() - arrowW), false, hover == Hit::presetNext);
    g.setColour (barInk.withAlpha ((hover == Hit::presetName ? 1.0f : 0.92f) * a));
    g.drawFittedText (presetText, r.reduced (arrowW, 0.0f).toNearestInt(), Justification::centred, 1, 0.7f);
}

//==============================================================================
// Souris
//==============================================================================
SmallToneEditor::Hit SmallToneEditor::hitAt (Point<float> u) const
{
    if (u.getDistanceFrom (layout::knobPos) <= layout::knobR * 1.05f) return Hit::knob;
    if (u.getDistanceFrom (layout::togglePos) <= layout::toggleS * 0.30f) return Hit::toggle;
    if (dinHit.contains (u)) return Hit::din;
    if (depthHit.contains (u)) return Hit::depth;
    if (u.getDistanceFrom (layout::fsPos) <= layout::footR * 1.35f) return Hit::foot;
    if (u.getDistanceFrom (layout::ledPos) <= layout::ledS * 0.75f || syncHit.contains (u)) return Hit::led;
    const auto r = layout::presetRect;
    if (r.contains (u))
        return u.x < r.getX() + arrowW ? Hit::presetPrev : (u.x > r.getRight() - arrowW ? Hit::presetNext : Hit::presetName);
    return Hit::none;
}

void SmallToneEditor::mouseMove (const MouseEvent& e)
{
    hover = hitAt (toUnits (e.position));
    setMouseCursor (hover == Hit::none ? MouseCursor::NormalCursor
                  : hover == Hit::knob ? MouseCursor::UpDownResizeCursor : MouseCursor::PointingHandCursor);
}

void SmallToneEditor::mouseExit (const MouseEvent&) { hover = Hit::none; }

void SmallToneEditor::mouseDown (const MouseEvent& e)
{
    const auto h = hitAt (toUnits (e.position));
    if (e.mods.isPopupMenu())
    {
        // clic droit sur une commande : son MIDI Learn en tete du menu
        showContextMenu (h == Hit::foot ? 0 : h == Hit::knob ? 1
                         : (h == Hit::toggle || h == Hit::din || h == Hit::depth) ? 2 : h == Hit::led ? 3 : -1);
        return;
    }
    if (statusAlpha > 0.0f && layout::presetRect.contains (toUnits (e.position)))
    {   // la ligne d'etat ne bloque pas : un clic fait revenir la barre de presets
        statusUntil = 0.0;
        return;
    }
    dragging = Hit::none;
    switch (h)
    {
        case Hit::knob:
            dragging = Hit::knob; dragStart = e.position; dragStartRate = proc.getRate();
            if (auto* p = proc.apvts.getParameter ("rate")) p->beginChangeGesture();
            flash ("Rate  " + rateText());
            break;
        case Hit::toggle: case Hit::din: case Hit::depth:
        {
            const bool deep = h == Hit::toggle ? ! proc.isDeep() : (h == Hit::depth);
            setParam ("depth", deep ? 1.0f : 0.0f);
            proc.presetName = {};
            break;
        }
        case Hit::foot:
            footDown = true;
            setParam ("on", proc.isOn() ? 0.0f : 1.0f);
            break;
        case Hit::led:      // LED STATUS / SYNC = synchro du RATE sur le tempo du DAW
            setParam ("sync", proc.apvts.getRawParameterValue ("sync")->load() < 0.5f ? 1.0f : 0.0f);
            break;
        case Hit::presetPrev: stepPreset (-1); break;
        case Hit::presetNext: stepPreset (1); break;
        case Hit::presetName: showPresetMenu(); break;
        case Hit::none: break;
    }
}

void SmallToneEditor::mouseDrag (const MouseEvent& e)
{
    if (dragging != Hit::knob) return;
    const auto d = e.position - dragStart;
    // course complete = 420 px de souris quelle que soit la taille de la fenetre (Maj = 4x plus fin)
    const float range = 420.0f * (e.mods.isShiftDown() ? 4.0f : 1.0f);
    setRate (dragStartRate + (d.x - d.y) / range);
}

void SmallToneEditor::mouseUp (const MouseEvent&)
{
    if (dragging == Hit::knob)
        if (auto* p = proc.apvts.getParameter ("rate")) p->endChangeGesture();
    dragging = Hit::none;
    footDown = false;
}

void SmallToneEditor::mouseDoubleClick (const MouseEvent& e)
{
    if (hitAt (toUnits (e.position)) == Hit::knob) setRate (0.5f);
}

void SmallToneEditor::mouseWheelMove (const MouseEvent& e, const MouseWheelDetails& w)
{
    const auto h = hitAt (toUnits (e.position));
    const float step = (std::abs (w.deltaY) > 1.0e-6f ? w.deltaY : w.deltaX) * (w.isReversed ? -1.0f : 1.0f);
    if (h == Hit::knob) setRate (proc.getRate() + step * (e.mods.isShiftDown() ? 0.008f : 0.03f));
    else if (h == Hit::toggle && std::abs (step) > 0.0f) { setParam ("depth", step < 0 ? 1.0f : 0.0f); proc.presetName = {}; }
}

//==============================================================================
// Presets
//==============================================================================
void SmallToneEditor::stepPreset (int delta)
{
    const int n = (int) SmallToneProcessor::factoryPresets().size();
    int cp = proc.getCurrentProgram();
    if (proc.presetName != SmallToneProcessor::factoryPresets()[(size_t) jlimit (0, n - 1, cp)].name)
        cp = delta > 0 ? -1 : 0;
    proc.setCurrentProgram ((cp + delta + n) % n);
    proc.updateHostDisplay (AudioProcessor::ChangeDetails().withProgramChanged (true));
}

void SmallToneEditor::askUserPresetName (int slot)
{
    nameDialog = std::make_unique<AlertWindow> ("Save user preset " + String (slot), "Preset name:", MessageBoxIconType::NoIcon, this);
    nameDialog->addTextEditor ("name", proc.presetName.isNotEmpty() ? proc.presetName : "User " + String (slot));
    nameDialog->addButton ("Save", 1, KeyPress (KeyPress::returnKey));
    nameDialog->addButton ("Cancel", 0, KeyPress (KeyPress::escapeKey));
    nameDialog->enterModalState (true, ModalCallbackFunction::create ([this, slot] (int r)
    {
        if (r == 1 && nameDialog != nullptr)
        {
            auto n = nameDialog->getTextEditorContents ("name").trim();
            if (n.isEmpty()) n = "User " + String (slot);
            proc.saveUserPreset (slot, n);
            flash ("Saved  " + n);
        }
        nameDialog.reset();
    }), false);
}

void SmallToneEditor::showPresetMenu()
{
    PopupMenu m;
    m.setLookAndFeel (&menuLnf);
    NineHandsMenu::addHeader (m, menuLnf.f, NineHandsMenu::icoPreset, menuAccent, "Presets", presetLine());
    m.addSectionHeader ("Factory presets");
    const auto& fp = SmallToneProcessor::factoryPresets();
    for (int i = 0; i < (int) fp.size(); ++i)
        m.addItem (100 + i, String (i + 1) + ". " + fp[(size_t) i].name, true, proc.presetName == fp[(size_t) i].name);
    m.addSeparator();
    PopupMenu load, save;
    for (int s = 1; s <= 9; ++s)
    {
        const auto n = proc.userPresetName (s);
        load.addItem (200 + s, "User " + String (s) + (n.isNotEmpty() ? "  " + n : String ("  (empty)")), n.isNotEmpty());
        save.addItem (300 + s, "User " + String (s) + (n.isNotEmpty() ? "  " + n + "  (overwrite)" : String()));
    }
    m.addSubMenu ("Load user preset", load);
    m.addSubMenu ("Save user preset", save);
    const auto area = layout::presetRect.transformedBy (AffineTransform::scale (k())).getSmallestIntegerContainer();
    m.showMenuAsync (PopupMenu::Options().withTargetScreenArea (localAreaToGlobal (area)),
        [safe = Component::SafePointer<SmallToneEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& pr = safe->proc;
            if (r >= 100 && r < 200)
            {
                pr.setCurrentProgram (r - 100);
                pr.updateHostDisplay (AudioProcessor::ChangeDetails().withProgramChanged (true));
            }
            else if (r > 200 && r < 300) pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400) safe->askUserPresetName (r - 300);
        });
}

//==============================================================================
// Menu clic droit (design d'Octopus, NineHandsMenu.h), toujours ouvert a l'endroit du clic
//==============================================================================
PopupMenu SmallToneEditor::buildContextMenu (int learnIdx)
{
    using namespace NineHandsMenu;
    PopupMenu menu;
    menu.setLookAndFeel (&menuLnf);
    auto ccText = [this] (int i) { const int cc = proc.ccMap[i].load(); return cc >= 0 ? "CC " + String (cc) : String ("not assigned"); };
    const int lt = proc.learnTarget.load();
    if (learnIdx >= 0)
    {
        // menu d'une commande (tronc commun) : en-tete, MIDI Learn, Clear MIDI, Cancel MIDI learn
        const String name = SmallToneProcessor::learnDef (learnIdx).name;
        const int ico = learnIdx == 0 ? icoPedal : learnIdx == 1 ? icoKnob : learnIdx == 2 ? icoSwitch : icoSettings;
        addHeader (menu, menuLnf.f, ico, menuAccent, name, "MIDI: " + ccText (learnIdx));
        menu.addItem (1000 + learnIdx, "MIDI Learn: " + name, true, lt == learnIdx);
        menu.addItem (1100 + learnIdx, "Clear MIDI: " + name, proc.ccMap[learnIdx].load() >= 0);
        menu.addItem (1200, "Cancel MIDI learn", lt >= 0);
        return menu;
    }

    addHeader (menu, menuLnf.f, icoPedal, menuAccent, "Small Tone", "Analog chorus  v" + String (JucePlugin_VersionString));
    PopupMenu factory;
    const auto& fp = SmallToneProcessor::factoryPresets();
    for (int i = 0; i < (int) fp.size(); ++i)
        factory.addItem (100 + i, String (i + 1) + ". " + fp[(size_t) i].name, true, proc.presetName == fp[(size_t) i].name);
    menu.addSubMenu ("Factory presets", factory);
    PopupMenu load, save;
    for (int s = 1; s <= 9; ++s)
    {
        const auto n = proc.userPresetName (s);
        load.addItem (200 + s, "User " + String (s) + (n.isNotEmpty() ? " : " + n : String ("  (empty)")), n.isNotEmpty());
        save.addItem (300 + s, "User " + String (s) + (n.isNotEmpty() ? " : " + n + "  (overwrite)" : String()));
    }
    menu.addSubMenu ("Load user preset", load);
    menu.addSubMenu ("Save user preset", save);
    menu.addSeparator();

    auto flag = [this] (const char* id) { return proc.apvts.getRawParameterValue (id)->load() > 0.5f; };
    PopupMenu settings;
    settings.addItem (501, "Rate synced to host tempo (" + String (proc.hostBpm.load(), 1) + " BPM)", true, flag ("sync"));
    settings.addItem (502, "Stereo spread (right channel LFO inverted)", true, flag ("stereo"));
    settings.addItem (503, "BBD hiss (analog noise floor)", true, flag ("noise"));
    settings.addItem (504, "Rate ring pulses with the LFO", true, flag ("ringlfo"));
    menu.addSubMenu ("Settings", settings);
    menu.addSeparator();

    PopupMenu midi;
    midi.addSectionHeader ("MIDI Learn");
    for (int i = 0; i < SmallToneProcessor::numLearn; ++i)
        midi.addItem (1000 + i, "Learn: " + String (SmallToneProcessor::learnDef (i).name) + "  (" + ccText (i) + ")", true, lt == i);
    midi.addSeparator();
    midi.addItem (1200, "Cancel MIDI learn", lt >= 0);
    midi.addItem (1201, "Clear all MIDI assignments");
    midi.addSeparator();
    NineHandsWindow::addMidiFootswitchMode (midi, ! flag ("ccmomentary"));
    midi.addSeparator();
    NineHandsWindow::addProgramChangeInfo (midi);
    menu.addSubMenu ("MIDI", midi);
    menu.addSeparator();

    const char* names[numSizes] = { "60 %", "75 %", "100 %" };
    const int heights[numSizes] = { sizeHeight (0), sizeHeight (1), sizeHeight (2) };
    menu.addSubMenu ("Plugin size", NineHandsWindow::sizeMenu (JucePlugin_Name, numSizes, names, heights, getHeight()));
    menu.addSubMenu ("Glow intensity", NineHandsWindow::glowMenu (roundToInt (glow * 100.0f)));
    return menu;
}

void SmallToneEditor::showContextMenu (int learnIdx)
{
    auto menu = buildContextMenu (learnIdx);
    menu.showMenuAsync (PopupMenu::Options().withMousePosition(),       // toujours la ou l'on clique
        [safe = Component::SafePointer<SmallToneEditor> (this)] (int r)
        {
            if (safe == nullptr || r == 0) return;
            auto& ed = *safe;
            auto& pr = ed.proc;
            auto toggleFlag = [&] (const char* id) { ed.setParam (id, pr.apvts.getRawParameterValue (id)->load() > 0.5f ? 0.0f : 1.0f); };
            int inst = pr.uiSizeIdx.load();
            const int sz = NineHandsWindow::handleSize (r, JucePlugin_Name, numSizes, inst);
            if (sz >= 0) { pr.uiSizeIdx = inst; ed.setWindowHeight (sizeHeight (sz)); return; }
            if (const int pc = NineHandsWindow::handleGlow (r, JucePlugin_Name)) { ed.setGlowPercent (pc); ed.flash ("Glow  " + String (pc) + " %"); return; }
            if (r >= 100 && r < 200)
            {
                pr.setCurrentProgram (r - 100);
                pr.updateHostDisplay (AudioProcessor::ChangeDetails().withProgramChanged (true));
            }
            else if (r > 200 && r < 300) pr.loadUserPreset (r - 200);
            else if (r > 300 && r < 400) ed.askUserPresetName (r - 300);
            else if (r == 501) toggleFlag ("sync");
            else if (r == 502) { toggleFlag ("stereo"); ed.flash (pr.apvts.getRawParameterValue ("stereo")->load() > 0.5f ? "Stereo spread" : "Mono (original)"); }
            else if (r == 503) toggleFlag ("noise");
            else if (r == 504) toggleFlag ("ringlfo");
            else if (r == NineHandsWindow::idLatch || r == NineHandsWindow::idMomentary) ed.setParam ("ccmomentary", r == NineHandsWindow::idMomentary ? 1.0f : 0.0f);
            else if (r >= 1000 && r < 1000 + SmallToneProcessor::numLearn)
            {
                const int t = r - 1000;
                pr.learnTarget.store (pr.learnTarget.load() == t ? -1 : t);       // re-cliquer annule
            }
            else if (r >= 1100 && r < 1100 + SmallToneProcessor::numLearn)
            {
                pr.ccMap[r - 1100].store (-1);
                ed.flash (String (SmallToneProcessor::learnDef (r - 1100).name) + "  MIDI cleared");
            }
            else if (r == 1200) pr.learnTarget.store (-1);
            else if (r == 1201) { pr.learnTarget.store (-1); pr.resetMidiMap(); ed.flash ("All MIDI cleared"); }
        });
}
