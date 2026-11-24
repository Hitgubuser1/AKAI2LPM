# Design decisions

## 2026-11-24 - First release

Use a software bridge on Windows between one original APC mini and one Sting instance in Ableton Live. This preserves Sting's page logic and lets the APC use its existing firmware. Present the port name `LPMiniMK3 MIDI` to Sting. Preserve the grid orientation and map the upper Launchpad row to the lower APC row. Translate visual cues so that playing steps and active slots remain distinguishable.

## 2026-11-24 - Distribution

Publish under MIT and offer the finished application free of charge. Maintain project knowledge alongside the implementation so reviews can track both together.

## Open choices

Python is proposed for the experiment. Choose the shipping language and virtual-port backend after observing traffic on Windows. A production endpoint needs independent send and receive paths. [Microsoft virtual device documentation](https://microsoft.github.io/MIDI/kb/virtual-device-app/)

Faders, multiple instances and selectable controllers are ideas for later versions. Additional devices will need their own input and LED mappings.
