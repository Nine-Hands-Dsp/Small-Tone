#pragma once
#include <juce_core/juce_core.h>
#include "NineHandsFolder.h"

// NINE HANDS | DSP : reglage « Glow » du clic droit (regle des skills, nov. 2026) : intensite du halo des lumieres
// (anneaux, LED) sur la facade, de 0 % (halo coupe, la lumiere elle-meme reste allumee) a 200 %.
// Commun a toutes les fenetres du plugin, enregistre a cote de la taille par defaut :
//   Windows : %APPDATA%\Nine Hands DSP\<Plugin>\settings.xml   macOS : ~/Library/Application Support/Nine Hands DSP/<Plugin>/settings.xml
namespace NineHandsGlow
{
    constexpr int numSteps = 9;
    constexpr int steps[numSteps] = { 0, 25, 50, 75, 100, 125, 150, 175, 200 };

    inline juce::File file (const juce::String& plugin)
    {
        return juce::File::getSpecialLocation (juce::File::userApplicationDataDirectory)
                   .getChildFile (nhd::folderName()).getChildFile (plugin).getChildFile ("settings.xml");
    }

    inline int percent (const juce::String& plugin)
    {
        const auto f = file (plugin);
        if (f.existsAsFile())
            if (auto x = juce::XmlDocument::parse (f))
                return juce::jlimit (0, 200, x->getIntAttribute ("glowPercent", 100));
        return 100;
    }

    inline void setPercent (const juce::String& plugin, int pc)
    {
        const auto f = file (plugin);
        juce::XmlElement x ("StudioWigaSettings");
        if (f.existsAsFile())
            if (auto old = juce::XmlDocument::parse (f))
                x = *old;
        x.setAttribute ("glowPercent", juce::jlimit (0, 200, pc));
        f.getParentDirectory().createDirectory();
        x.writeTo (f);
    }
}
