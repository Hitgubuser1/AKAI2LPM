# Development vault

| Page | Purpose |
| --- | --- |
| [Decisions](decisions.md) | Scope, design choices and open questions |
| [Controller protocol](protocol.md) | MIDI addresses, capabilities and sources |
| [Sting bench experiment](sting-poc.md) | Prior observation, procedure and results |

## Git workflow

Keep main usable at the maturity described in the README. Start each change on a short-lived branch from main, for example docs/controller-notes or poc/sting-midi. Keep commits focused and describe the change in the subject. Once hosted, use pull requests into main. Describe the checks run and hardware assumptions in each review. Tag published releases as vMAJOR.MINOR.PATCH and associate downloads with their release tag.

## Maintaining the vault

Record dated design choices and their rationale in Decisions. Update the protocol when evidence changes a mapping. Add repeatable observations to the bench record with hardware, software versions and message direction.
