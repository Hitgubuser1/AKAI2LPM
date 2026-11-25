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

## Host acceptance

| Platform | Host and format | Live evidence |
| --- | --- | --- |
| Windows | Ableton Live / VST3 | Port discovery, note input, LED capture and simultaneous forwarding for one physical pad passed with shared loopMIDI. Separated endpoint validation pending. |
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

The third pad (address 83) received `03 53 5A 50 00` at Type positions 3 through 5 and `03 53 00 00 00` at positions 2 and 1. The third APC pad staying lit above `RxANDOM` matches the fill sent by Sting. Verify Density, Keyboard and Length clears with their own controls and captures.
