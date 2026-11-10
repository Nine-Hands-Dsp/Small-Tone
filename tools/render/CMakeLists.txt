# Outil hors plugin : compile le processeur + la fenetre de SMALL TONE sous Linux et exporte des captures PNG (apercu, notice)
#   cmake -B build-render -S tools/render -DJUCE_DIR=/chemin/vers/JUCE && cmake --build build-render -j4
#   build-render/SmallToneRender_artefacts/SmallToneRender <dossier de sortie>
cmake_minimum_required(VERSION 3.22)
project(SmallToneRender VERSION 1.0.0)
set(CMAKE_CXX_STANDARD 17)
add_subdirectory(${JUCE_DIR} JUCE)
set(W ${CMAKE_CURRENT_SOURCE_DIR}/../..)
juce_add_binary_data(SmallToneAssets SOURCES
  ${W}/background.png ${W}/glow_ring.png ${W}/ring_core.png ${W}/glow_led.png ${W}/led_on.png ${W}/fs_refl.png ${W}/toggle_strip.png
  ${W}/Poppins-Regular.ttf ${W}/Poppins-Medium.ttf ${W}/Poppins-Bold.ttf ${W}/Poppins-Light.ttf ${W}/NineHandsLogo.svg)
juce_add_console_app(SmallToneRender PRODUCT_NAME "SmallToneRender")
target_sources(SmallToneRender PRIVATE main.cpp ${W}/PluginProcessor.cpp ${W}/PluginEditor.cpp)
target_include_directories(SmallToneRender PRIVATE ${W})
target_compile_definitions(SmallToneRender PRIVATE JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_ALSA=0 JUCE_JACK=0
  JUCE_USE_XRANDR=0 JUCE_USE_XINERAMA=0 JUCE_USE_XCURSOR=0 JUCE_USE_XSHM=0 JucePlugin_Name="Small Tone" JucePlugin_Build_VST3=0
  JucePlugin_VersionString="2.0.0" JUCE_STANDALONE_APPLICATION=1 JUCE_MODAL_LOOPS_PERMITTED=1)
target_link_libraries(SmallToneRender PRIVATE SmallToneAssets juce::juce_audio_utils juce::juce_recommended_config_flags)
