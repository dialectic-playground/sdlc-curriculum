"""Reference implementation of dp-average (projects/17-stream-filters/specs/SRS.md).

Every token is validated as a real number; only values greater than zero are summed, in input
order, and the single result line is written after the end of the input.
"""

from __future__ import annotations

import math

from ._token_stream import stream_tokens
from .common import (DataError, Option, UsageError, data_failure, file_failure, fix,
                     handle_action, open_input, parse_args, parse_real_token, usage_failure,
                     write)

TOOL = "dp-average"
HELP_TEXT = """\
Usage: dp-average [OPTION]... [FILE]
Print the average of the positive numbers in FILE.

With no FILE, or when FILE is -, read standard input.  Numbers are real
numbers separated by whitespace and are read until the end of the input.
Numbers less than or equal to zero are checked but otherwise ignored.  The
average is written with six digits after the decimal point.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    count = 0
    total = 0.0
    try:
        for token in stream_tokens(handle):
            x = parse_real_token(token, source)
            if x > 0.0:
                total = total + x
                count += 1
                if not math.isfinite(total):
                    raise DataError(source, token.line,
                                    b"arithmetic overflow at '" + token.text + b"'")
    except DataError as error:
        return data_failure(TOOL, error)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()

    if count == 0:
        write(b"no positive numbers read\n")
    else:
        write(f"average = {fix(total / float(count), 6)}\n")
    return 0
