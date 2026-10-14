"""Reference implementation of dp-max (projects/25-max/specs/SRS.md).

The whole input is read and validated before the single result line is written.
"""

from __future__ import annotations

import sys

from .common import (PROMPT, DataError, UsageError, data_failure, file_failure, handle_action,
                     open_input, parse_args, parse_int_token, prompt, strip_eof_marker,
                     tokenize, unexpected_end, usage_failure, write)

TOOL = "dp-max"
HELP_TEXT = """\
Usage: dp-max [OPTION]... [FILE]
Print the largest of one to four integers.

Read the integers from FILE, or from standard input when FILE is absent or -,
until the end of the input.  They are whole numbers from -9223372036854775808
to 9223372036854775807, separated by whitespace.

Options:
  -p, --prompt    write a prompt to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
"""
PROMPT_TEXT = "Enter one to four integers\ngenerate EOF when done\n"
MAX_VALUES = 4


def maximum(first: int, *rest: int) -> int:
    """The largest of one or more integers (the variadic function of SRS-25 NFR-05)."""
    largest = first
    for value in rest:
        if value > largest:
            largest = value
    return largest


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        prompt(prompting, PROMPT_TEXT)
        data = handle.read()
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if handle is not sys.stdin.buffer:
            handle.close()
    data = strip_eof_marker(data)
    tokens = tokenize(data)
    try:
        values = [parse_int_token(token, source) for token in tokens[:MAX_VALUES]]
        if len(tokens) > MAX_VALUES:
            extra = tokens[MAX_VALUES]
            raise DataError(source, extra.line, b"too many values '" + extra.text + b"'")
        if not values:
            raise unexpected_end(source, data)
    except DataError as error:
        return data_failure(TOOL, error)
    write(f"Maximum integer = {maximum(*values)}\n")
    return 0
