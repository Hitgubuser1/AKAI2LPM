"""Original APC mini mapping for the Sting bench probe."""

from .launchpad_mini import GRID_NOTES, RIGHT_CC, TOP_CC

NOTE_OFF = 0x80
NOTE_ON = 0x90
CONTROL_CHANGE = 0xB0

EDGE_CC = dict(zip(range(64, 72), TOP_CC))
EDGE_CC.update(zip(range(82, 90), RIGHT_CC))
APC_GRID_NOTES = {address: note for note, address in enumerate(GRID_NOTES)}

OFF, GREEN, RED, YELLOW = 0, 1, 3, 5
STING_COLOURS = {
    (0, 0, 0): OFF,
    (90, 80, 0): YELLOW,     # Type
    (0, 80, 90): GREEN,      # Density
    (70, 70, 70): YELLOW,    # Length
    (110, 0, 55): RED,       # Highlighted step
    (64, 0, 127): RED,       # Keyboard
    (100, 90, 0): YELLOW,    # Root note
    (0, 100, 0): YELLOW,     # Selected Step Edit value
}


def launchpad_event(data):
    if len(data) != 3 or data[0] not in (NOTE_OFF, NOTE_ON):
        return None

    status, note, velocity = data
    if 0 <= note < len(GRID_NOTES):
        return status, GRID_NOTES[note], velocity

    controller = EDGE_CC.get(note)
    if controller is not None:
        return CONTROL_CHANGE, controller, velocity if status == NOTE_ON else 0

    return None


def grid_led(address, rgb):
    note = APC_GRID_NOTES.get(address)
    if note is not None:
        return NOTE_ON, note, STING_COLOURS.get(rgb, GREEN)
    return None
