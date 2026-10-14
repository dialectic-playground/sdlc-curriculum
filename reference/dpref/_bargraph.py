"""The bar-graph engine shared by dp-bargraph and dp-bargraph2.

Specified identically in projects/16-bargraph/specs/SRS.md (FR-01 ... FR-10) and
projects/20-bargraph-grade/specs/SRS.md (FR-01 ... FR-06), so the two reference tools differ
only in their canonical name and help text. The model reads the whole input before writing;
for every input that can be read to the end this gives the same bytes as the record-by-record
streaming the SRSs require.
"""

from __future__ import annotations

from .common import (DataError, Token, UsageError, data_failure, end_line, file_failure,
                     handle_action, parse_args, parse_int_token, read_all, strip_eof_marker,
                     usage_failure, write)

MIN_VALUE, MAX_VALUE = 0, 10000
BLANK = b" \t\n\v\f\r"  # the CONV-32 whitespace bytes


def split_lines(data: bytes) -> list[bytes]:
    """Lines of ``data`` without their LF, each with one trailing CR removed (SRS FR-02)."""
    if not data:
        return []
    lines = data.split(b"\n")
    if data.endswith(b"\n"):
        lines.pop()  # no final line after the last LF
    return [line[:-1] if line.endswith(b"\r") else line for line in lines]


def is_blank(line: bytes) -> bool:
    return not line.strip(BLANK)


def echo_line(title: bytes) -> bytes:
    """The title line exactly as read, plus LF."""
    return title + b"\n"


def print_stars(value: int) -> bytes:
    """One '*' for every 2 units of ``value`` (integer division), plus LF."""
    return b"*" * (value // 2) + b"\n"


def records(data: bytes, source: str) -> tuple[list[tuple[bytes, int]], DataError | None]:
    """Parse the whole input into (title, value) records, stopping at the first data error."""
    lines = split_lines(data)
    while lines and is_blank(lines[-1]):
        lines.pop()  # blank lines after the last record are ignored (FR-04)
    parsed: list[tuple[bytes, int]] = []
    for index in range(0, len(lines), 2):
        title = lines[index]
        if index + 1 == len(lines):
            return parsed, DataError(source, end_line(data), "unexpected end of input")
        text = lines[index + 1].strip(BLANK)
        try:
            value = parse_int_token(Token(text, index + 2), source, MIN_VALUE, MAX_VALUE)
        except DataError as error:
            return parsed, error
        parsed.append((title, value))
    return parsed, None


def run_bargraph(tool: str, help_text: str, argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [])
        if handle_action(tool, parsed, help_text):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(tool, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        data = strip_eof_marker(read_all(source))
    except OSError as error:
        file_failure(tool, source, error)
        return 1
    good, error = records(data, source)
    write(b"".join(echo_line(title) + print_stars(value) for title, value in good))
    if error is not None:
        return data_failure(tool, error)
    return 0
