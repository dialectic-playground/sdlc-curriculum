"""Character and line rules shared by Projects 27 (dp-wrap), 29 (dp-strlen), 33 (dp-reverse).

Characters follow the decoding rule of SRS-04 FR-06 (the same rule dp-wc uses): a complete
well-formed UTF-8 sequence (Unicode Table 3-7) is one character, and every other byte is one
character on its own. Lines follow SRS-29 FR-04 / SRS-33 FR-03: text data (CONV-37) divided at
LF, with one CR removed before each LF and at the very end of the input.

The scan is written out byte by byte on purpose; it does not use a library UTF-8 decoder.
"""

from __future__ import annotations

# (lead-byte range, second-byte range, total length) per row of Unicode Table 3-7.
_ROWS = (
    (0xC2, 0xDF, 0x80, 0xBF, 2),
    (0xE0, 0xE0, 0xA0, 0xBF, 3),
    (0xE1, 0xEC, 0x80, 0xBF, 3),
    (0xED, 0xED, 0x80, 0x9F, 3),
    (0xEE, 0xEF, 0x80, 0xBF, 3),
    (0xF0, 0xF0, 0x90, 0xBF, 4),
    (0xF1, 0xF3, 0x80, 0xBF, 4),
    (0xF4, 0xF4, 0x80, 0x8F, 4),
)


def char_length(data: bytes, pos: int) -> int:
    """Length in bytes (1 … 4) of the character that starts at ``data[pos]``."""
    lead = data[pos]
    if lead < 0x80:
        return 1
    for low, high, second_low, second_high, length in _ROWS:
        if low <= lead <= high:
            if pos + length > len(data):
                return 1
            if not second_low <= data[pos + 1] <= second_high:
                return 1
            for offset in range(2, length):
                if not 0x80 <= data[pos + offset] <= 0xBF:
                    return 1
            return length
    return 1


def length(data: bytes, use_bytes: bool) -> int:
    """Count bytes or characters by an explicit scan from the first byte."""
    count = 0
    pos = 0
    while pos < len(data):
        pos += 1 if use_bytes else char_length(data, pos)
        count += 1
    return count


def lines(data: bytes) -> list[tuple[bytes, int]]:
    """Text-data lines with their line numbers: LF excluded, one CR before LF/end removed."""
    data = data.rstrip(b"\x1a")  # CONV-37
    result = []
    parts = data.split(b"\n")
    if parts[-1] == b"":
        parts.pop()  # the empty segment after a final LF (or an empty input) is no line
    for number, line in enumerate(parts, start=1):
        if line.endswith(b"\r"):
            line = line[:-1]
        result.append((line, number))
    return result
