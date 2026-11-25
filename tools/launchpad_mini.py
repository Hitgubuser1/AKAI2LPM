"""Launchpad Mini MK3 Programmer Mode addresses and observed RGB frames."""

GRID_NOTES = tuple(11 + 10 * row + column for row in range(8) for column in range(8))
TOP_CC = tuple(range(91, 99))
RIGHT_CC = tuple(range(89, 18, -10))
RGB_HEADER = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x0D, 0x03)


def decode_rgb_lighting(data):
    """Decode the all-RGB form used by Sting on the Windows bench."""
    if tuple(data[:7]) != RGB_HEADER or data[-1] != 0xF7:
        return {}

    entries = data[7:-1]
    if len(entries) % 5 or any(kind != 3 for kind in entries[::5]):
        return {}

    return {
        entries[index + 1]: tuple(entries[index + 2:index + 5])
        for index in range(0, len(entries), 5)
    }
