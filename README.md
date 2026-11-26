# AKAI2LPM

**A MIDI bridge project for playing Iftah's Sting with pad controllers.**

Created by **MixamSE** · [MIT License](LICENSE)

## How it will work

Connect an Akai APC mini MK1 and select the bridge's Monome grid in Sting. The bridge uses local OSC to send pad gestures and receive LED feedback. Choose the planned Launchpad Mini or Monome workflow in the bridge to set how the APC pads control Sting. Both workflows use the same connection to Sting.

## Project status

Live playability and low resource use are release requirements. Pad input and LED feedback should respond without perceptible delay, including during bursts of MIDI traffic. The app is designed for a small install, low background RAM and CPU use, and operation without a dedicated GPU.

**Pre-release.** The [Windows OSC proof of concept](docs/vault/sting-poc.md#local-osc-bench-with-stings-monome-mode) verified APC mini MK1 control and LED feedback in Sting VST3 in Ableton Live, with loopMIDI closed. The test covered Type, Density, Length, Root, Step Edit and Generate Pattern in the native Monome layout. After a probe restart, reconnecting in Sting restored pad input and LEDs. The next milestone is the Launchpad Mini workflow over the same OSC connection. The application is planned as a free download.

## Compatibility roadmap

| Area | First validation target | Longer-term direction |
| --- | --- | --- |
| Operating system | Windows | macOS and Linux, following Sting's desktop availability |
| Plug-in and host | Sting VST3 in Ableton Live | Validate Sting's VST3, AU and CLAP builds in compatible hosts |
| Pad controller | Akai APC mini MK1 | Selectable controller profiles, with the APC mini MK2 and APC40 as candidates |

Iftah lists downloads for Windows, macOS and Linux and publishes Sting in VST3, AU and CLAP formats. Bridge compatibility will be verified for each supported combination of host, Sting build, OSC connection and controller MIDI backend. [Official Sting downloads and system requirements](https://www.if-tah.com/devices/sting/)

## Development

- [Development vault](docs/vault/README.md) for design decisions and the Git workflow
- [Controller protocol](docs/vault/protocol.md) for MIDI mapping and LED feedback
- [Proof of concept](docs/vault/sting-poc.md) for the proposed Python experiment and bench results
- [AGENTS.md](AGENTS.md) for repository instructions
