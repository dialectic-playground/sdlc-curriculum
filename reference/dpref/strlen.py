"""Reference implementation of dp-strlen (projects/29-strlen/specs/SRS.md).

Every length is obtained by the explicit scan in ``_strings.length``, never from a stored
length. The reference reads a whole input before measuring its lines; the observable bytes are
the same as for a streaming implementation.
"""

from __future__ import annotations

from . import common
from ._strings import length, lines
from .common import (Option, UsageError, encode_arg, file_failure, handle_action,
                     invalid_argument, parse_args, read_all, usage_failure)

TOOL = "dp-strlen"
HELP_TEXT = """\
Usage: dp-strlen [OPTION]... [STRING]...
Print the length of each STRING, or of each line of the input.

With no STRING, print the length of each line of standard input, or of FILE
with -f (the FILE - is standard input).  The LF that ends a line is not
counted, and neither is one CR before it.  Lengths count UTF-8 characters;
each byte of an invalid sequence counts as one character.  With -b, lengths
count bytes.

Options:
  -f, --file=FILE   read lines from FILE instead of standard input
  -b, --bytes       count bytes instead of characters
      --help        display this help and exit
      --version     output version information and exit
"""

OPTIONS = [
    Option("file", short="f", long="file", takes_value=True),
    Option("bytes", short="b", long="bytes"),
]


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        source = None
        if "file" in parsed.values:
            source = str(parsed.values["file"])
            if source == "":
                raise invalid_argument(source, parsed.spelled["file"])
            if parsed.operands:
                raise UsageError(f"extra operand '{parsed.operands[0]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    use_bytes = bool(parsed.values.get("bytes"))
    if parsed.operands:
        for operand in parsed.operands:
            common.write(f"{length(encode_arg(operand), use_bytes)}\n".encode())
        return 0

    source = source or "-"
    try:
        data = read_all(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    for line, _number in lines(data):
        common.write(f"{length(line, use_bytes)}\n".encode())
    return 0
