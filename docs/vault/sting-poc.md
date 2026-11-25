# Sting MIDI bench experiment

## Recorded observation

The maintainer saw Sting list a loopMIDI port named `LPMiniMK3 MIDI`. Deleting the port and restarting Live removed the entry. The first note-input test has since passed. See the Windows bench result below.

## Proposed Python experiment

The initial Windows input test requires loopMIDI. Create a virtual port named `LPMiniMK3 MIDI` in loopMIDI and leave it running while testing Sting. For bidirectional acceptance, use an endpoint with independent send and receive paths.

Use a disposable Live set and Sting's Algo main page. Disable Live's MIDI input/output for the controller ports, remove control-surface assignments for them and set monitoring on the Sting track to Off. Select the virtual port in Sting. For listening, route the musical output to a second instrument track. [Sting monitoring notes](https://www.if-tah.com/guides/sting-launchpad-mini-x-mk3.pdf)

1. Capture controller-bound messages from before port selection through the first refresh. Record direction. If the cable echoes Sting's writes to its input, use a paired endpoint before interpreting results.
2. Set Type above 1 with the mouse. Send the top-left grid press and release on channel 1 (hex 90 51 7F and 80 51 00). Expect Type to change to 1.
3. Send Generate Pattern (hex B0 13 7F and B0 13 00). Check the displayed pattern. This exercises the CC path.
4. With the sender idle, change Type with the mouse. Capture the controller-bound LED update and identify the addressed pads.
5. Once both directions work, repeat with the physical APC and observe its LEDs during a mouse change. Hold and release a momentary page button and check that Sting returns to the main page.

Append Windows, Live and Sting versions, endpoint names, backend, device generation, raw bytes with direction, and observed UI or LED changes. Preserve startup traffic if initialization stalls.

## Running the probe

Use Python 3.12 from the repository root. Install the pinned dependencies in
a virtual environment, then list the port names as the probe sees them.

```text
python -m pip install -r tools/requirements-poc.txt
python tools/sting_probe.py ports
python tools/sting_probe.py capture "<bridge-side input>" --seconds 60
python tools/sting_probe.py send "<bridge-side output>" type-one
python tools/sting_probe.py send "<bridge-side output>" generate
```

Start capture in its own terminal before selecting the device in Sting. Use
the output of a paired endpoint to send into Sting and the input of that
endpoint to receive Sting's replies. A shared loopMIDI port is useful for
discovery and initial input probes. Use a separated return path for a
definitive bidirectional result. The probe emits JSON Lines with monotonic
timestamps, message bytes and the direction as seen by the probe.

### Running the full-grid APC probe

From the repository root, run the bidirectional probe with the exact four
names reported by the ports command. This example uses the last Windows
bench enumeration.

```text
python -m tools.sting_grid_probe "APC MINI 0" "APC MINI 1" "LPMiniMK3 MIDI 1" "LPMiniMK3 MIDI 2" --seconds 120 --trace
```

The arguments are APC input, APC output, Sting feedback input and Sting
control output. The probe forwards grid notes and maps the lower and right
APC buttons to Launchpad CCs. Change a Sting setting after opening the ports
to request a fresh LED frame. For the first CC test, tap the right-hand
button beside the bottom grid row, directly above Shift. It should send
CC 19 with values 127 then 0 and generate a pattern on Sting's main page.

The bench palette uses yellow for Type and Length, green for Density and
red for Keyboard. The root note and highlighted step have separate colours.
Explicit black turns a pad off. The LED path handles the all-RGB SysEx
frames observed on the bench. Other lighting modes and edge-button LEDs
are pending live captures. The run releases held controls and clears its
active LEDs on exit. The optional trace reports up to 128 translated input
events after shutdown.

## Host acceptance

| Platform | Host and format | Live evidence |
| --- | --- | --- |
| Windows | Ableton Live / VST3 | Type, Density, Length, Root, Generate Pattern and overlapping Step Edit gestures passed on the shared loopMIDI bench. Separated endpoint validation pending. |
| macOS | Logic Pro / AU | Awaiting host run |
| Linux | REAPER / CLAP | Awaiting host run |

For each row record a visible Type change after a simulated pad press and an
independent MIDI return after a mouse change. Record the exact setup with the
trace. The unit tests use a simulated MIDI backend and run without Sting.

## 2026-11-24 Windows bench result

**Passed: simulated grid pad activates Sting.** Ableton Live 12 Suite on Windows hosted Sting VST3. Sting selected the loopMIDI port named LPMiniMK3 MIDI. The Python probe ran with Python 3.13.3 and Mido/RtMidi and opened the enumerated output LPMiniMK3 MIDI 1.

The type-two gesture sent channel 1 note 82 with hex bytes 90 52 7F (press) and 80 52 00 (release). The maintainer observed Type move one step right from RANDOM to xANDOM. loopMIDI showed a cumulative count of 5,837 bytes. The counter measures aggregate traffic. The observed Type change is the evidence for the input path.

**Passed: Sting emits RGB pad updates.** With no APC attached and no Python sender running, a read-only probe on `LPMiniMK3 MIDI 0` received Launchpad Mini MK3 SysEx frames starting with `F0 00 20 29 02 0D 03` and ending with `F7`. Two captured frames differed at pad address 83 (top row, third column). Its decimal RGB values changed from `90 80 0` to `0 0 0` and back on a subsequent frame. The packet format matches the [Novation programmer reference](https://downloads.novationmusic.com/novation/launchpad-mk3/launchpad-mini-mk3-0).

Still to verify on Windows: CC input, simultaneous operation over an endpoint with independent directions, and live response time.

**Passed: direct APC mini MK1 input and LED output.** On Windows 10 build 19045, Python/Mido with RtMidi opened both APC ports on the current USB-C adapter. Sending `90 00 01` to `APC MINI 1` lit the bottom-left grid pad green, as observed by the maintainer. Pressing and releasing it produced `90 00 7F` and `80 00 7F` respectively on `APC MINI 0`. After release the probe sent `90 00 00` and the maintainer saw the LED turn off. This exercise used the physical APC directly. The complete APC-to-Sting and Sting-to-APC translation remains to be tested.

### Physical Type pad experiment

Use the exact input and output names reported by the probe. With Sting set to
RANDOM, run the pad phase and press and release the third pad from the left in
the top grid row. Expect Type to move to its third value. After the process
exits, run the LED phase and move Type between its second and third values
with the mouse. Expect the same physical pad to switch off and yellow.

```text
python tools/apc_type_probe.py pad "<APC input>" "<loopMIDI output>"
python tools/apc_type_probe.py led "<loopMIDI input>" "<APC output>"
```

Each phase listens for 60 seconds. The LED phase accepts the observed
Launchpad RGB frames. Other pad positions and LED formats are outside
this experiment.

### 2026-11-24 physical Type pad results

**Passed: APC pad changes Type in Sting.** With the APC and loopMIDI disabled for Live's own MIDI routing, the pad phase forwarded `90 53 7F` and `80 53 7F` from the third pad in the APC's top row to Sting via loopMIDI. The maintainer confirmed that Type moved from RANDOM to its third value.

**Passed: Sting updates the physical APC LED.** In a separate run, the probe converted Sting's RGB updates for Launchpad address 83 to off and yellow commands `90 3A 00` and `90 3A 05` on the physical APC output. The maintainer saw the LED light and then turn off while changing Type. A follow-up run logged three yellow/off pairs. The maintainer confirmed that the pad consistently stayed off at xANDOM and lit at RxANDOM.

### 2026-11-25 simultaneous Type pad result

**Passed: one physical pad with both forwarding directions active.** An inline Python 3.13.3 probe reused the Type translator and opened both directions with Mido/RtMidi. The setup used an APC mini MK1, Windows 10 build 19045, Ableton Live 12.4.16, Sting VST3 and the shared `LPMiniMK3 MIDI` loopMIDI port. The Sting plug-in version was unrecorded.

- APC → probe → Sting: pressing and releasing the third pad in the top row forwarded `90 53 7F` and `80 53 7F`. The maintainer saw Type select `RxANDOM` and the pad light up.
- Sting → probe → APC: the trace recorded repeated LED commands `90 3A 05` (yellow) and `90 3A 00` (off). The maintainer confirmed that turning Type down with the mouse to `xANDOM` extinguished the pad. Above `RxANDOM`, the pad stayed lit until Type returned to `xANDOM`.

The converter collapses every accepted nonblack RGB value to yellow. The trace recorded forwarded APC commands. See the raw capture below for the source of the Type behaviour. Separated endpoint validation, other controls and physical latency measurement remain open.

### 2026-11-25 Type LED capture

**Observed: the Type row fills from the left through the selected value.** On the same Windows and Live setup, a read-only Mido/RtMidi listener on `LPMiniMK3 MIDI 1` captured Sting's controller output while the maintainer moved Type with the mouse from `RANDOM` up to position 5 and back. The updated top rows had `2 → 3 → 4 → 5 → 4 → 3 → 2 → 1` lit pads. The eight updates were 328-byte Launchpad Mini MK3 lighting SysEx frames, each with an RGB entry for every one of the 64 grid pads. The lit Type pads shared RGB `(90, 80, 0)` and the remaining Type pads carried `(0, 0, 0)`.

The third pad (address 83) received `03 53 5A 50 00` at Type positions 3 through 5 and `03 53 00 00 00` at positions 2 and 1. The third APC pad staying lit above `RxANDOM` matches the fill sent by Sting.

### 2026-11-25 Length test via simulated Launchpad pads

**Passed: Length input and LED clears.** With Sting VST3 in Ableton Live 12.4.16 on Windows 10 build 19045, the Python 3.13.3 Mido/RtMidi probe sent short channel-1 note gestures on `LPMiniMK3 MIDI 2` and captured replies on `LPMiniMK3 MIDI 1`. The probe simulated `16 → 8 → 4 → 16` with 80 ms presses on Launchpad notes 38, 48, 44 and 38 and paused five seconds at each value. The maintainer confirmed the same sequence in Sting's Steps display. The first 16 produced no LED frame. The shared port echoed the eight outgoing note messages.

Each of the three changes produced a complete Launchpad grid frame with 64 RGB entries. The Length pads use addresses 41–48 for steps 1–8 and 31–38 for steps 9–16, matching the [Launchpad layout](https://www.if-tah.com/guides/sting-launchpad-mini-x-mk3.pdf).

| Steps | Active addresses | Explicit black `(0, 0, 0)` |
| --- | --- | --- |
| 8 | 41–48 | 31–38 |
| 4 | 41–44 | 45–48 and 31–38 |
| 16 | 41–48 and 31–38 | None |

Active steps used RGB `(70, 70, 70)`. Address 41 was highlighted in `(110, 0, 55)` in all three frames.

### 2026-11-25 Length feedback on APC mini MK1

**Passed: physical Length LEDs turn off and relight.** On the same Windows, Live and Sting VST3 setup, an inline Python 3.13.3 Mido/RtMidi probe simulated Launchpad presses over shared loopMIDI. It read the resulting Sting RGB frames on `LPMiniMK3 MIDI 1` and sent LED messages to `APC MINI 1`. Launchpad addresses 41–48 mapped to APC notes 24–31 in the fifth grid row from the top. Addresses 31–38 mapped to APC notes 16–23 in the sixth grid row. For this bench test all active LEDs used steady green (`90 <note> 01`), and black mapped to off (`90 <note> 00`).

After an initial move to 8, the trace confirmed five RGB frames and 48 APC LED commands across setup and the `16 → 8 → 4 → 16` sweep. The move to 8 sent off to notes 16–23. The move to 4 additionally sent off to notes 28–31. The final move to 16 relit those twelve pads. The maintainer confirmed the expected on and off states on the physical controller. The probe cleared its LEDs on exit.

### 2026-11-25 APC Length taps and Step Edit hold

On the same Windows, Live and Sting VST3 setup, a Python 3.13.3 Mido/RtMidi bench probe read `APC MINI 0`, forwarded channel-1 note presses and releases through `LPMiniMK3 MIDI 2`, and translated Sting's RGB replies from `LPMiniMK3 MIDI 1` to green or off on `APC MINI 1`. All three gestures used the fifth grid row from the top.

| Gesture | APC → Launchpad note | Sting RGB response |
| --- | --- | --- |
| Tap the rightmost pad | 31 → 48 | Eight Length pads active |
| Tap the fourth pad | 27 → 44 | Four Length pads active |
| Hold the second pad for 2.177 s | 25 → 42 | Step Edit frame while held. Release restored the exact preceding frame with four Length pads active. |

The Step Edit frame first appeared about 0.5 s after the hold began. Sting sent 46 identical Step Edit frames during that hold and 33 during a second hold of 1.696 s. Each hold sent 15 changed APC LEDs on entry and 15 on return. Repeated frames yielded zero additional APC writes. Both releases restored the exact preceding frame with four active Length pads.

The maintainer confirmed the fifth-row response and observed lit Keyboard pads in the bottom two rows. Those rows kept the same on/off states during Step Edit, but the incoming RGB values changed. The test palette renders all active pads green, so these colour changes are visible in the capture only.

### 2026-11-25 full-grid probe smoke test

The repository probe opened both APC mini MK1 ports and both sides of the shared loopMIDI port with Mido/RtMidi on the same Windows, Live and Sting VST3 setup. The reference probe sent two Type gestures to `LPMiniMK3 MIDI 2`. The grid probe received two Sting RGB frames on `LPMiniMK3 MIDI 1` and sent 65 LED commands to `APC MINI 1` before shutdown. The run verifies software forwarding to the live APC output.

### 2026-11-25 Generate Pattern and APC grid colours

On the same Windows, Live and Sting VST3 setup, the grid probe read the
physical APC mini MK1 via `APC MINI 0` and sent four identical pairs to
`LPMiniMK3 MIDI 2`. Each pair was `B0 13 7F` on press and `B0 13 00` on
release (channel 1, CC 19). During the same run the probe received 25
Sting RGB frames on `LPMiniMK3 MIDI 1` and sent 480 LED updates to
`APC MINI 1`. These counts are totals for the run.

The maintainer confirmed that the physical Stop All Clips button changed
the note sequence in Sting. A photo taken after a mouse-driven Type
update showed light yellow Type pads, green-to-turquoise Density pads and
red Keyboard pads with a light yellow root note. The three regions were
visually distinguishable on the APC mini MK1 in this bench palette.

### 2026-11-25 Density and Root via physical APC pads

On the same Windows, Live and Sting VST3 setup, the Mido/RtMidi
grid probe translated four APC mini MK1 pad taps from `APC MINI 0`
to Launchpad notes 64, 52, 12 and 11 on `LPMiniMK3 MIDI 2`.
Each tap forwarded a channel-1 Note On and Note Off with velocity 127.
The probe received four Sting RGB frames on `LPMiniMK3 MIDI 1` and
sent 74 LED messages to `APC MINI 1` across the run.

The maintainer confirmed that Density changed to 4 and then 10 and that
the green fill followed both values. Tapping the second and then the first
pad of the bottom row changed Root and moved the yellow Keyboard
highlight accordingly. The individual note names were unrecorded.

### 2026-11-25 overlapping APC pad gestures

On the same Windows, Live and Sting VST3 bench, the Mido/RtMidi grid probe
forwarded four overlapping gestures from `APC MINI 0` to
`LPMiniMK3 MIDI 2`. For each gesture it sent Note On for Launchpad
address 42 (Length step 2), Note On and Note Off for a Keyboard address,
and then Note Off for address 42. The Keyboard targets were 14, 13, 15
and 13. All events retained channel 1 and velocity 127.

The 397 RGB frames from Sting on `LPMiniMK3 MIDI 1` showed that in all
four trials the second pad changed the selected step note and Step Edit
stayed active after that pad was released. Only release of the Length pad
restored the main layout. Length remained four and the main-page root
highlight remained on address 11. Reopening Step Edit showed the previous
trial's selected step note. The maintainer confirmed that changing the
note using the bottom keyboard row while holding the Length pad worked
and that the new selection persisted. The probe sent 268 LED commands to
`APC MINI 1` during the run.

## Local OSC bench with Sting's Monome mode

The Windows target is Sting VST3 1.0.5 in Ableton Live 12.4.16 with the APC
mini MK1. Use the built-in USB MIDI stack for the physical APC. The probe
advertises a `monome 64` over serialosc discovery on `127.0.0.1:12002` and
uses a second loopback UDP socket for key events and grid LEDs. Keep the
loopMIDI tray app closed. The probe opens only the two physical APC ports
and uses Python sockets to talk to Sting. [Monome OSC reference](https://monome.org/docs/serialosc/osc/)

From the repository root, use the existing [PoC MIDI dependencies](../../tools/requirements-poc.txt)
for the APC run. Omit both port arguments to check discovery and incoming
LED traffic with Python's standard library alone.

```powershell
python -B -m tools.sting_osc_probe --seconds 180 --trace
python -B -m tools.sting_osc_probe "APC MINI 0" "APC MINI 1" --seconds 180 --trace
python -B -m tools.sting_osc_probe "APC MINI 0" "APC MINI 1" --seconds 300 --watch-pad 8 3
```

Use an empty or disposable Live set. Disable the APC input and output in
Live's MIDI settings and clear its control-surface assignment. Start the
probe, then open Sting's control-surface selector, choose the discovered
Monome grid and use its default rotation. Set monitoring to Off on the
Sting track. Keep musical MIDI routed through Live.

| Check | Expected observation |
| --- | --- |
| Discovery | Sting lists and opens the grid. The probe records a discovery reply and device configuration. |
| Type and LED feedback | Press a Type pad on the APC to change Sting. Turn Type with the mouse and verify the corresponding LED changes, including its off state. |
| Grid coverage | Check Density, 16 → 8 → 4 → 16 Steps and Root. Verify removed steps dim or go out according to Sting's OSC levels and check the result on the APC. |
| Overlapping holds | Hold a step in the Length region, select a note in the keyboard region and release the note. Step Edit stays open until the Length pad is released. Reopen it and verify that the new note persists. |
| Generate Pattern | From the main page, tap row 8 pad 8 (PAGE) to open Slots. Tap row 8 pad 1 (GEN). Confirm the sequence changes. |

Use the [Monome Grid 64 layout](https://www.if-tah.com/guides/sting-monome-64.pdf)
for pad positions. The probe preserves physical grid positions. The first
palette assigns the APC colours by pairs of rows. Start at `--min-level 1`
to show all nonzero levels and use the raw OSC levels to choose a threshold
if Sting sends a dim background. Use Sting's native Monome grid positions
and page gestures for the OSC workflow.

For a Step Edit blink check, set Steps to eight and open the main page.
Hold row 5 pad 2, tap pad 3 of row 8, and keep holding the step for a few
seconds before releasing. `--watch-pad ROW PAD` records changes in Sting's
OSC brightness and the LED values sent to that APC pad with monotonic
timestamps. Read the report on exit. MIDI send timestamps measure the
software path up to the MIDI API call, while visual feedback is checked
on the physical APC.

Record the Sting build and the host/device observations. The automated UDP
test verifies discovery, setup, overlapping key events and LED updates
with a simulated host and controller. Real Sting connection, APC playability
and timing need live validation.

### 2026-11-25 Windows OSC discovery, Type and Length

With loopMIDI closed on the Windows 10 bench, Sting VST3 1.0.5 in Live
12.4.16 connected to the probe's `monome 64`. The maintainer saw the grid
light up on connection. APC pads changed Type in Sting, and mouse changes
to Type updated the corresponding APC LEDs. The maintainer also confirmed
that the Length control worked. The same run ended after 300 seconds, and
the maintainer observed the APC LEDs go dark as the probe shut down.

The probe reported two discovery replies and eight device configuration
messages. It sent 51 APC key transitions to Sting, processed 1,136 LED
messages from Sting and sent 554 LED updates to the APC. The final captured
grid used OSC levels 0, 7 and 15. Step Edit with a second held gesture and
Generate Pattern from the Monome Slots page still need host confirmation.

### 2026-11-25 OSC keyboard feedback during Step Edit

On the same bench, the probe sent 32 key transitions, including complete
press and release pairs for bottom-row pads while row 5 pad 2 was held.
It received 979 LED messages from Sting and sent 475 updates to the APC.
The maintainer saw the keyboard pads in red and could not verify which
step note was selected. The probe rendered every nonzero keyboard level in
red. The final frame showed only one active Length step. Test again with
Steps set to eight before holding step 2. Inspect the step note in Sting's
expanded note editor or reopen Step Edit and compare the pad highlight.
The Root control indicates the pattern root throughout the gesture.

The probe now maps the brightest keyboard level to yellow, lower visible
levels to red, and zero to off. With `--trace` it retains the last 24
changes in the lower two rows as raw OSC levels. Pad positions follow the
native Monome coordinates.

In the follow-up with Steps set to eight, the maintainer held row 5 pad 2,
selected a new note on the bottom row, released the pads and reopened the
same step. The new note was highlighted again. This confirms that the
step note persists through the OSC input and feedback path. The maintainer
also observed row 7 pad 8 alternating between red and yellow. Limit yellow
note highlighting to the first seven columns in the bottom two rows, so
brightness changes on the rightmost grid controls keep the same colour.
Check the result on the APC in the next host run.

### 2026-11-25 OSC Slots and Generate Pattern

On the same Windows 10 bench and native Monome layout, the maintainer
opened Slots with PAGE and confirmed repeated GEN presses produced new
patterns. The trace recorded press and release pairs at `(7, 7)` for PAGE
and `(0, 7)` for GEN on Slots, using OSC coordinates from the top left.
The maintainer also saw Sting's smiley rendered on the APC. The final raw
grid contained the smiley frame before shutdown.

The probe sent 38 APC key transitions to Sting, received 532 LED messages
from Sting and sent 846 LED updates to the APC. It ended normally after
300 seconds and the maintainer reported that the APC LEDs went dark.

### 2026-11-25 OSC Step Edit LED timing

With Steps set to eight on the same Windows bench, the maintainer reported
that row 8 pad 3 stayed yellow while holding step 2. The targeted trace
recorded OSC level 15 at 48.480 seconds and the next level change to 12 at
58.452 seconds. The probe sent one yellow command for the first event and
no further command for that pad during the 9.972-second interval. Earlier
in the same session, that coordinate received alternating levels 0 and
15. The trace does not associate those earlier changes with a specific
gesture or view. The sustained Step Edit highlight needs no blink rate
adjustment based on this run.

After the run, the maintainer reported that row 1 pad 7 remained yellow.
The final OSC frame put that pad at level 7, which the probe rendered
yellow. The probe had exited and the LED remained on after disconnecting
Sting. A direct MIDI Note On with velocity 0 for APC note 62 completed
without an API error, but the maintainer saw no change. Unplugging and
reconnecting the APC cleared the LED. Windows then listed `APC MINI 0`
for input and `APC MINI 1` for output. Recheck that pad and its neighbour
with direct press/release LED feedback, then verify clearing on probe exit.
The cause of the retained LED state on the first run is unconfirmed.

In the direct comparison with Sting disconnected, APC pads 1,7 and 1,6
each sent two complete press and release pairs. The maintainer confirmed
that both lit yellow on press and went dark on release. For an OSC shutdown
check run the probe with `--watch-pad 1 7`. Keep that pad lit until the end.
The trace labels a successful MIDI API call to clear the pad on shutdown
as `cleanup_midi`. Verify the physical LED goes out as well.

The follow-up OSC run confirmed the shutdown behaviour. The maintainer
verified pad 1,7 was lit during the run and dark after the normal
120-second exit. The final OSC level for the pad was 7. The trace shows
the probe sent MIDI velocity 0 for that pad during cleanup and the send
returned successfully. The run processed 253 OSC LED messages and sent
417 APC updates before cleanup. The original retained LED did not recur.
