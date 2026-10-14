"""Reference implementation of dp-taxes-file (projects/14-taxes-file/specs/SRS.md).

The whole input is read and validated before the output file is opened, so a missing or
invalid input never creates, truncates, or modifies the output file.
"""

from __future__ import annotations

import os

from . import common
from ._taxes_rule import MAX_INCOME, record
from .common import (DataError, Option, UsageError, data_failure, file_failure,
                     handle_action, invalid_argument, parse_args, parse_int_token, read_all,
                     strip_eof_marker, tokenize, usage_failure)

TOOL = "dp-taxes-file"
DEFAULT_INPUT = "incomes.dat"
DEFAULT_OUTPUT = "out.dat"
HELP_TEXT = """\
Usage: dp-taxes-file [OPTION]...
Compute the progressive income tax for every income in an input file and
write the report to an output file.

Incomes are whole numbers from 0 to 9223372036854775807, separated by
whitespace.  An income below 6000 greenbacks is taxed at 30%, any other
income at 60%; the tax is rounded down to a whole number.  The whole input is
checked before the output file is opened: if the input cannot be read or
contains an invalid income, the output file is not created or changed.

Options:
  -i, --input=FILE    read the incomes from FILE (default incomes.dat);
                        - means standard input
  -o, --output=FILE   write the report to FILE, replacing its contents
                        (default out.dat); - means standard output
      --help          display this help and exit
      --version       output version information and exit
"""

OPTIONS = [
    Option("input", short="i", long="input", takes_value=True),
    Option("output", short="o", long="output", takes_value=True),
]


def path_option(parsed: common.Parsed, dest: str, default: str) -> str:
    value = str(parsed.values.get(dest, default))
    if value == "":
        raise invalid_argument(value, parsed.spelled[dest])
    return value


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if parsed.operands:
            raise UsageError(f"extra operand '{parsed.operands[0]}'")
        source = path_option(parsed, "input", DEFAULT_INPUT)
        target = path_option(parsed, "output", DEFAULT_OUTPUT)
    except UsageError as error:
        return usage_failure(TOOL, error)

    try:
        data = strip_eof_marker(read_all(source))
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        incomes = [parse_int_token(token, source, 0, MAX_INCOME) for token in tokenize(data)]
    except DataError as error:
        return data_failure(TOOL, error)
    report = b"".join(record(income) for income in incomes)

    if target == "-":
        common.write(report)
        return 0
    try:
        if os.path.isdir(target):
            raise IsADirectoryError(target)
        handle = open(target, "wb")
    except OSError as error:
        file_failure(TOOL, target, error)
        return 1
    try:
        with handle:
            handle.write(report)
    except OSError:
        common.diagnose(TOOL, f"{target}: Input/output error")
        return 1
    return 0
