"""Reference implementation of dp-stats (projects/15-stats/specs/SRS.md).

Single pass, constant memory: count, minimum, maximum, sum, and sum of squares are updated
token by token in the exact binary64 operation order of SRS-15 FR-04 and FR-05.
"""

from __future__ import annotations

import math

from ._token_stream import stream_tokens
from .common import (DataError, Option, UsageError, data_failure, file_failure, fix,
                     handle_action, open_input, parse_args, parse_real_token, usage_failure,
                     write)

TOOL = "dp-stats"
HELP_TEXT = """\
Usage: dp-stats [OPTION]... [FILE]
Print summary statistics of the real numbers in FILE.

With no FILE, or when FILE is -, read standard input.  Numbers are separated
by whitespace and read in a single pass until the end of the input.  The
report gives the count, maximum, minimum, sum, mean, population variance
(sum of squares / N - mean * mean), and standard deviation, each real number
with six digits after the decimal point.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = []


def overflow(source: str, token) -> DataError:
    return DataError(source, token.line, b"arithmetic overflow at '" + token.text + b"'")


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
    smallest = largest = total = squares = 0.0
    try:
        for token in stream_tokens(handle):
            x = parse_real_token(token, source)
            square = x * x
            if count == 0:
                smallest = largest = total = x
                squares = square
            else:
                if x > largest:
                    largest = x
                if x < smallest:
                    smallest = x
                total = total + x
                squares = squares + square
            count += 1
            if not (math.isfinite(square) and math.isfinite(total)
                    and math.isfinite(squares)):
                raise overflow(source, token)
    except DataError as error:
        return data_failure(TOOL, error)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()

    if count == 0:
        write(b"0 data items read\n")
        return 0
    n = float(count)
    mean = total / n
    variance = squares / n - mean * mean
    if variance < 0.0:
        variance = 0.0
    deviation = math.sqrt(variance)
    write(f"{count} data items read\n"
          f"maximum value read = {fix(largest, 6)}\n"
          f"minimum value read = {fix(smallest, 6)}\n"
          f"sum of all values read = {fix(total, 6)}\n"
          f"mean = {fix(mean, 6)}\n"
          f"variance = {fix(variance, 6)}\n"
          f"standard deviation = {fix(deviation, 6)}\n")
    return 0
