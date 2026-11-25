# Design decisions

## 2026-11-24 - Resource use

Keep the installed application small and its background RAM and CPU use low. Use a small native settings window and event-driven MIDI I/O. Let the process sleep when idle. Suspend UI refresh when the window is hidden. Use standard OS drawing and keep dedicated GPU hardware and GPU compute optional to running the application.

Before release, record download size, installed footprint including bundled dependencies, resident memory, CPU and GPU activity on each validated OS. Measure the release build with a controller connected in three states: idle with the window closed, active pad and LED traffic with the window closed, and settings or diagnostics visible. Record versions, hardware, sample durations and values so regressions can be compared. Set numerical budgets from the first measured release build. Check any resource optimization against the live latency requirement below.

## 2026-11-24 - Live performance latency

Pad presses and releases must reach Sting, and Sting's LED updates must reach the controller, without perceptible delay during live playing. Forward events as they arrive. Keep GUI refresh, diagnostic logging and disk writes off the forwarding path. Preserve event order and press/release pairs under load.

Measure added bridge latency separately in each direction using monotonic timestamps at MIDI ingress and egress. Record median, 95th and 99th percentiles and maximum during ordinary use and bursts of pad and LED traffic. Check the complete path on real hardware for response and jitter while playing. Automated timing measurements characterize the bridge. Physical play and LED response determine live acceptance.

## 2026-11-24 - First release

Use a software bridge on Windows between one original APC mini and one Sting instance in Ableton Live. This preserves Sting's page logic and lets the APC use its existing firmware. In Launchpad mode, present the port name `LPMiniMK3 MIDI` to Sting and map the upper Launchpad row to the lower APC row. In either workflow, preserve grid orientation and keep playing steps and active slots distinguishable.

## 2026-11-24 - Distribution

Publish under MIT and offer the finished application free of charge. Maintain project knowledge alongside the implementation so reviews can track both together.

## 2026-11-25 - Selectable Sting workflows

Let users choose between Sting's native Launchpad and Monome workflows in
the bridge. The layouts, page controls and LED feedback differ. Keep the
Sting workflow choice independent of the physical controller profile.
Offer native Monome over local OSC as the path demonstrated on Windows 10
with the built-in USB MIDI stack for the APC. Offer native Launchpad over
MIDI when a compatible, distributable virtual endpoint is available and
has been validated with Sting on that platform.

## Open choices

Use loopMIDI for the initial Windows PoC. The desktop bridge should provision and manage its own virtual MIDI endpoint through an OS backend if Sting can discover and open that endpoint and exchange pad events and LED feedback reliably. In that case loopMIDI can be removed from the installation requirements.

Python is proposed for the experiment. Choose the shipping language and virtual-port backend after observing traffic on Windows. A production endpoint needs independent send and receive paths. [Microsoft virtual device documentation](https://microsoft.github.io/MIDI/kb/virtual-device-app/)

Fader assignments, multiple Sting instances and the order of platform and controller additions remain open.

## 2026-11-24 - Desktop portability and controller profiles

Follow the desktop platforms and plug-in formats Iftah publishes for Sting. The first validation target is Sting VST3 in Ableton Live on Windows. Extend support to macOS and Linux, with AU on macOS and VST3 and CLAP in compatible hosts where available. Record the OS, host, Sting build and MIDI backend for each support claim. [Official Sting availability](https://www.if-tah.com/devices/sting/)

Keep Sting message translation independent of the operating system's MIDI endpoints and of the controller profiles. Evaluate toolchains against bidirectional MIDI access, local OSC and packaging on the target platforms after the proof of concept. VST3, AU and CLAP are Sting integration targets to validate in hosts.

Offer selectable profiles for additional pad controllers in later releases. Each profile describes the input mapping and LED capabilities of the exact hardware generation. The APC mini MK2 and APC40 are candidates.
