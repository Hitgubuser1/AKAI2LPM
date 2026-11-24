# Sting MIDI bench experiment

## Recorded observation

The maintainer saw Sting list a loopMIDI port named `LPMiniMK3 MIDI`. Deleting the port and restarting Live removed the entry. Initialization, input handling and LED feedback still await verification.

## Proposed Python experiment

Use a disposable Live set and Sting's Algo main page. Disable Live's MIDI input/output for the controller ports, remove control-surface assignments for them and set monitoring on the Sting track to Off. Select the virtual port in Sting. For listening, route the musical output to a second instrument track. [Sting monitoring notes](https://www.if-tah.com/guides/sting-launchpad-mini-x-mk3.pdf)

1. Capture controller-bound messages from before port selection through the first refresh. Record direction. If the cable echoes Sting's writes to its input, use a paired endpoint before interpreting results.
2. Set Type above 1 with the mouse. Send the top-left grid press and release on channel 1 (hex 90 51 7F and 80 51 00). Expect Type to change to 1.
3. Send Generate Pattern (hex B0 13 7F and B0 13 00). Check the displayed pattern. This exercises the CC path.
4. With the sender idle, change Type with the mouse. Capture the controller-bound LED update and identify the addressed pads.
5. Once both directions work, repeat with the physical APC and observe its LEDs during a mouse change. Hold and release a momentary page button and check that Sting returns to the main page.

Append Windows, Live and Sting versions, endpoint names, backend, device generation, raw bytes with direction, and observed UI or LED changes. Preserve startup traffic if initialization stalls.
