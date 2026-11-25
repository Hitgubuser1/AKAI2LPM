# Controller protocol

Sting opens the Launchpad ports directly and selects Programmer Mode. Rows below count from the bottom starting at zero, columns from the left starting at zero. Addresses are decimal. These mappings are derived from published sources and await hardware verification. [Sting controller reference](https://www.if-tah.com/guides/sting-launchpad-mini-x-mk3.pdf)

| Position | APC MK1 input | Launchpad input to Sting on channel 1 |
| --- | --- | --- |
| Grid row r, column c | Note 8r + c | Note 11 + 10r + c |
| Lower row, left to right | Notes 64-71 | CC 91-98 |
| Right column, top to bottom | Notes 82-89 | CC 89, 79, 69, 59, 49, 39, 29, 19 |
| Shift | Note 98 | Unassigned |
| Faders, master last | CC 48-56 | Unassigned |

The bottom-left pad maps from note 0 to 11. The top-left maps from 56 to 81. Preserve both press and release for held modifiers.

## LED feedback

Novation supports palette events, flashing, pulsing and grouped SysEx updates. Capture the forms Sting actually sends. APC grid velocities are 0 for off, 1/2 for steady/blinking green, 3/4 for red and 5/6 for yellow. The edge buttons each have one colour. Check slot occupancy, playback position and selected values for readability on hardware. [Novation programmer reference](https://downloads.novationmusic.com/novation/launchpad-mk3/launchpad-mini-mk3-0) and [independent APC mini MK1 implementation](https://github.com/gastonmorixe/lib-midi-akai-apc-mini)

The APC profile should give Type, Density and Keyboard distinct colours. Choose the palette so that adjacent regions serving different functions use different colours when colours are reused elsewhere. Preserve explicit LED-off states and verify that shortening Length turns off the steps removed from the pattern. Preserve the left-to-right Type fill observed in the [Type LED capture](sting-poc.md#2026-11-25-type-led-capture).
