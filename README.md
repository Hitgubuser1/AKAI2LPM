# AKAI2LPM

AKAI2LPM aims to let musicians play Iftah’s Sting with an original Akai APC mini (MK1). The planned Windows MIDI bridge translates its pads and buttons into Launchpad Mini MK3 messages and sends Sting’s visual feedback back to the APC. The goal is to plug in the APC, select `LPMiniMK3 MIDI` in Sting and jam without learning individual controls.

**Project status** — Design and protocol research. The maintainer has seen Sting list a virtual port with the expected name. Pad input and LED feedback still need a bench test. The first application release is planned as a free download.

The first target is one APC mini MK1 and one Sting instance in Ableton Live on Windows. The nine faders and support for other controllers, including the APC mini MK2 and APC40, are ideas for later versions.

## Development

Start with the [development vault](docs/vault/README.md) for design decisions, controller mappings and the proposed Python experiment. Contributors can find the Git workflow there. Repository-specific instructions for coding agents live in [AGENTS.md](AGENTS.md).

## License

AKAI2LPM is distributed under the [MIT License](LICENSE).
