# Design decisions

## 2026-11-24 - Resource use

Keep the installed application small and its background RAM and CPU use low. Use a small native settings window and event-driven MIDI I/O. Let the process sleep when idle. Suspend UI refresh when the window is hidden. Use standard OS drawing and keep dedicated GPU hardware and GPU compute optional to running the application.

Before release, record download size, installed footprint including bundled dependencies, resident memory, CPU and GPU activity on each validated OS. Measure the release build with a controller connected in three states: idle with the window closed, active pad and LED traffic with the window closed, and settings or diagnostics visible. Record versions, hardware, sample durations and values so regressions can be compared. Set numerical budgets from the first measured release build. Check any resource optimization against the live latency requirement below.

## 2026-11-24 - Live performance latency

Pad presses and releases must reach Sting, and Sting's LED updates must reach the controller, without perceptible delay during live playing. Forward events as they arrive. Keep GUI refresh, diagnostic logging and disk writes off the forwarding path. Preserve event order and press/release pairs under load.

Measure added bridge latency separately in each direction using monotonic timestamps at MIDI ingress and egress. Record median, 95th and 99th percentiles and maximum during ordinary use and bursts of pad and LED traffic. Check the complete path on real hardware for response and jitter while playing. Automated timing measurements characterize the bridge. Physical play and LED response determine live acceptance.

## 2026-11-24 - First release

Use a software bridge on Windows between one original APC mini and one Sting instance in Ableton Live. The APC uses its existing firmware and the Windows USB MIDI stack. The bridge uses local OSC to reach Sting's Monome control surface. Keep physical pad orientation, playing steps and active slots distinguishable in both workflows.

## 2026-11-24 - Distribution

Publish under MIT and offer the finished application free of charge. Maintain project knowledge alongside the implementation so reviews can track both together.

## 2026-11-26 - Selectable controller workflows over OSC

Offer two controller workflows in the bridge. Both use the same local
OSC transport, and Sting stays set to Monome in either case. The Monome
workflow uses native Grid 64 positions and gestures. The Launchpad Mini
workflow translates APC pad positions, gestures and LED feedback to the
familiar Launchpad Mini MK3 layout where Sting's Monome surface supports
the actions. Implement the Launchpad Mini workflow first. Keep workflow
translation independent of the physical controller profile and the OSC
session. Record any gaps against the earlier Launchpad MIDI bench.

## Open choices

The initial Launchpad MIDI proof of concept used loopMIDI for the Windows test. Use the Python OSC bench for the shared release transport. Choose the shipping language and toolkit after comparing live latency, resource use and packaging on the target platforms.

Fader assignments, multiple Sting instances and the order of platform and controller additions remain open.

## 2026-11-24 - Desktop portability and controller profiles

Follow the desktop platforms and plug-in formats Iftah publishes for Sting. The first validation target is Sting VST3 in Ableton Live on Windows. Extend support to macOS and Linux, with AU on macOS and VST3 and CLAP in compatible hosts where available. Record the OS, host, Sting build and MIDI backend for each support claim. [Official Sting availability](https://www.if-tah.com/devices/sting/)

Keep Sting message translation independent of the operating system's MIDI endpoints and of the controller profiles. Evaluate toolchains against bidirectional MIDI access, local OSC and packaging on the target platforms after the proof of concept. VST3, AU and CLAP are Sting integration targets to validate in hosts.

Offer selectable profiles for additional pad controllers in later releases. Each profile describes the input mapping and LED capabilities of the exact hardware generation. The APC mini MK2 and APC40 are candidates.
