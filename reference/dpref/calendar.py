"""Reference implementation of dp-calendar (projects/19-calendar/specs/SRS.md).

The codes are read incrementally (CONV-32), one attempt (a day code and a leap-year code) at a
time, so the calendar appears as soon as a valid pair has been typed.
"""

from __future__ import annotations

from typing import BinaryIO

from . import common
from .common import (PROMPT, DataError, InputError, InputStream, Option, UsageError,
                     data_failure, file_failure, handle_action, open_input,
                     parse_args, parse_count, parse_int_token, prompt, usage_failure)

TOOL = "dp-calendar"
PROMPT_TEXT = "Enter day and leap year codes: "
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")
DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
HEADER = "Sun  Mon  Tue  Wed  Thu  Fri  Sat"
HELP_TEXT = """\
Usage: dp-calendar [OPTION]... [FILE]
  or:  dp-calendar [OPTION]... --year=YEAR
Print a calendar of the twelve months of a year.

With no FILE, or when FILE is -, read standard input.  The input holds two
whole numbers: the day code of January 1 (0 = Sunday, 1 = Monday, ...,
6 = Saturday) and the leap year code (1 = leap year, 0 = common year).  A pair
whose day code is not 0 to 6 is reported and skipped, and the next pair is
read.  With --year, the codes are derived from a Gregorian year instead.

Options:
  -p, --prompt      write the prompt 'Enter day and leap year codes: ' to
                      standard error before each pair of codes is read
  -y, --year=YEAR   print the calendar of the Gregorian year YEAR (1 to 9999)
                      instead of reading codes
      --help        display this help and exit
      --version     output version information and exit
"""

OPTIONS: list[Option] = [PROMPT, Option("year", short="y", long="year", takes_value=True)]


def year_codes(year: int) -> tuple[int, int]:
    """Day code of January 1 and leap-year code of a proleptic Gregorian year."""
    y = year - 1
    day = (1 + 5 * (y % 4) + 4 * (y % 100) + 6 * (y % 400)) % 7
    leap = 1 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 0
    return day, leap


def calendar(day_code: int, leap: int) -> bytes:
    lines: list[str] = []
    for month, name in enumerate(MONTHS):
        days = DAYS_IN_MONTH[month] + (leap if month == 1 else 0)
        if month:
            lines.append("")
        lines += [name, "", HEADER]
        week = " " * (5 * day_code)  # blank cells before day 1
        for day in range(1, days + 1):
            weekday = (day_code + day - 1) % 7
            if weekday and day > 1:
                week += "  "
            week += f"{day:3d}"
            if weekday == 6:
                lines.append(week)
                week = ""
        if week:
            lines.append(week)
        day_code = (day_code + days) % 7
    return ("\n".join(lines) + "\n").encode()


def read_codes(handle: BinaryIO, source: str, prompting: bool) -> tuple[int, int]:
    stream = InputStream(handle)
    while True:
        prompt(prompting, PROMPT_TEXT)
        day_token = stream.require(source)
        day = parse_int_token(day_token, source)
        leap_token = stream.require(source)
        leap = parse_int_token(leap_token, source)
        if not 0 <= day <= 6:
            common.err.write(f"{TOOL}: {source}:{day_token.line}: ".encode()
                             + b"invalid day code '" + day_token.text + b"'\n")
            common.err.flush()
            continue
        if leap not in (0, 1):
            raise DataError(source, leap_token.line,
                            b"value out of range '" + leap_token.text + b"'")
        return day, leap


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        year = None
        if "year" in parsed.values:
            year = parse_count(str(parsed.values["year"]), parsed.spelled["year"], 1, 9999)
            if parsed.operands:
                raise UsageError(f"extra operand '{parsed.operands[0]}'")
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    if year is not None:
        common.write(calendar(*year_codes(year)))
        return 0

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        codes = read_codes(handle, source, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if source != "-":
            handle.close()
    common.write(calendar(*codes))
    return 0
