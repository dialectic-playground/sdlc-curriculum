"""Reference implementation of dp-sched (projects/38-sched/specs/SRS.md).

The whole input is read and validated before the report is written. Activities are sorted
stably by finish time (ties keep input order) and selected greedily.
"""

from __future__ import annotations

import re

from . import common
from .common import (DataError, Option, UsageError, data_failure, file_failure,
                     handle_action, parse_args, read_all, strip_eof_marker, usage_failure)

TOOL = "dp-sched"
LINE_SIZE = 10
FIELD_SIZE = 5
MAX_TIME = 99999
_INTEGER = re.compile(rb"[+-]?[0-9]+\Z")
HELP_TEXT = """\
Usage: dp-sched [OPTION]... FILE
Find a largest set of activities that do not overlap.

Each line of FILE describes one activity: its start time in columns 1-5 and
its finish time in columns 6-10, as whole numbers from 0 to 99999 padded with
spaces.  An activity may start at the time another one finishes.  The
activities are sorted by finish time (equal finish times keep the order of the
file) and chosen greedily; the chosen lines are printed as they appear in
FILE.  When FILE is -, read standard input.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def parse_field(field: bytes, source: str, line: int, what: str) -> int:
    text = field.strip(b" ")
    if not text:
        raise DataError(source, line, f"missing {what} time")
    if not _INTEGER.match(text):
        raise DataError(source, line, b"invalid integer '" + text + b"'")
    value = int(text)
    if not 0 <= value <= MAX_TIME:
        raise DataError(source, line, b"value out of range '" + text + b"'")
    return value


def load_activities(data: bytes, source: str) -> list[tuple[int, int, bytes]]:
    """Parse and validate every line (FR-02, FR-03): (start, finish, line bytes)."""
    data = strip_eof_marker(data)
    if not data:
        return []
    lines = data.split(b"\n")
    if lines[-1] == b"":
        lines.pop()  # the final line ended with LF
    activities = []
    for number, raw in enumerate(lines, start=1):
        text = raw[:-1] if raw.endswith(b"\r") else raw
        if len(text) != LINE_SIZE:
            raise DataError(source, number,
                            f"invalid line length {len(text)}, expected {LINE_SIZE}")
        start = parse_field(text[:FIELD_SIZE], source, number, "start")
        finish = parse_field(text[FIELD_SIZE:], source, number, "finish")
        if finish <= start:
            raise DataError(source, number, "finish time is not later than start time")
        activities.append((start, finish, text))
    return activities


def select(activities: list[tuple[int, int, bytes]]) -> list[bytes]:
    """Stable sort by finish time, then greedy selection (FR-04, FR-05)."""
    ordered = sorted(activities, key=lambda activity: activity[1])  # sorted() is stable
    chosen: list[bytes] = []
    last_finish = None
    for start, finish, text in ordered:
        if last_finish is None or start >= last_finish:
            chosen.append(text)
            last_finish = finish
    return chosen


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if not parsed.operands:
            raise UsageError("missing operand")
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0]
    try:
        data = read_all(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        activities = load_activities(data, source)
    except DataError as error:
        return data_failure(TOOL, error)
    report = b"Optimal schedule:\n\n" + b"".join(text + b"\n" for text in select(activities))
    common.write(report)
    return 0
