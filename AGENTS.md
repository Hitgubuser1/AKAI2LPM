# Working on AKAI2LPM

These instructions apply throughout the repository.

- Read the [vault index](docs/vault/README.md) and the page relevant to the change. Check the working tree before editing and preserve unrelated changes.
- Target the original APC mini MK1. Verify the hardware generation when citing MIDI addresses. Keep device-specific mappings identifiable so future controllers can supply their own.
- Preserve pad position, press and release, simultaneous holds, and message direction. Route Sting's performance notes through the host. The bridge handles controller traffic.
- Record protocol facts with their sources. For bench results, record the setup, expected and observed behavior, and direction of traffic. A simulated message and a physical pad press establish different things.
- Update the relevant vault page when a decision changes or a test resolves an open question. Keep the README accurate for someone looking to download or use the project.
- Use the [Git workflow](docs/vault/README.md#git-workflow). Report which checks actually ran. Build and test commands belong here once the implementation defines them.
