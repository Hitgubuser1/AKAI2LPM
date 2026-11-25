# AKAI2LPM

**A MIDI bridge project for playing Iftah's Sting with pad controllers.**

Created by **MixamSE** · [MIT License](LICENSE)

## How it will work

Connect an Akai APC mini MK1, select `LPMiniMK3 MIDI` in Sting, and use the pads to generate patterns or change length, type and root note. The bridge translates pad and button events into Launchpad Mini MK3 messages and converts Sting's LED feedback into colours and states the controller can display.

## Project status

Live playability and low resource use are release requirements. Pad input and LED feedback should respond without perceptible delay, including during bursts of MIDI traffic. The app is designed for a small install, low background RAM and CPU use, and operation without a dedicated GPU.

**Pre-release.** On the Windows bench with Ableton Live and loopMIDI, the APC mini MK1 changed Type and Length and triggered Generate Pattern from a physical button. LED feedback cleared inactive Length pads and returned to the main layout after releasing a Step Edit hold. The [full-grid Python probe](docs/vault/sting-poc.md#running-the-full-grid-apc-probe) supports further hardware testing. The application is planned as a free download.

## Compatibility roadmap

| Area | First validation target | Longer-term direction |
| --- | --- | --- |
| Operating system | Windows | macOS and Linux, following Sting's desktop availability |
| Plug-in and host | Sting VST3 in Ableton Live | Validate Sting's VST3, AU and CLAP builds in compatible hosts |
| Pad controller | Akai APC mini MK1 | Selectable controller profiles, with the APC mini MK2 and APC40 as candidates |

Iftah already lists downloads for Windows, macOS and Linux and publishes Sting in VST3, AU and CLAP formats. Bridge compatibility will be verified for each combination of host, Sting build and MIDI backend that the project supports. [Official Sting downloads and system requirements](https://www.if-tah.com/devices/sting/)

## Development

- [Development vault](docs/vault/README.md) for design decisions and the Git workflow
- [Controller protocol](docs/vault/protocol.md) for MIDI mapping and LED feedback
- [Proof of concept](docs/vault/sting-poc.md) for the proposed Python experiment and bench results
- [AGENTS.md](AGENTS.md) for repository instructions
