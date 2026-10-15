"""Reference implementation of dp-wrap (projects/27-line-wrap/specs/SRS.md).

Greedy word wrapping: words are placed one after another, separated by single spaces, and a
word that would make the line longer than the line length starts a new line. The reference
reads the whole input before wrapping; the observable bytes are the same as for a streaming
implementation.
"""

from __future__ import annotations

from . import common
from ._strings import length
from .common import (
    INT64_MAX,
    DataError,
    Option,
    UsageError,
    data_failure,
    encode_arg,
    file_failure,
    handle_action,
    parse_args,
    parse_count,
    parse_int_token,
    read_all,
    strip_eof_marker,
    tokenize,
    unexpected_end,
    usage_failure,
)

TOOL = "dp-wrap"
HELP_TEXT = """\
Usage: dp-wrap [OPTION]... [FILE]
Fill the words of FILE into lines no longer than a given line length.

With no FILE, or when FILE is -, read standard input.  Words are separated by
whitespace and are written greedily, separated by single spaces, so that no
line is longer than the line length.  Without -w, the first word of the input
is the line length.  Lengths count UTF-8 characters unless -b is given.  A
word longer than the line length is reported and written on a line of its own.

Options:
  -w, --width=WIDTH   use WIDTH (1 or more) as the line length; the first word
                        of the input is then text
  -b, --bytes         measure words in bytes instead of characters
      --help          display this help and exit
      --version       output version information and exit
"""

OPTIONS = [
    Option("width", short="w", long="width", takes_value=True),
    Option("bytes", short="b", long="bytes"),
]


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        width = None
        if "width" in parsed.values:
            width = parse_count(
                str(parsed.values["width"]), parsed.spelled["width"], 1, INT64_MAX
            )
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    use_bytes = bool(parsed.values.get("bytes"))
    try:
        data = strip_eof_marker(read_all(source))
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1

    tokens = tokenize(data)
    try:
        if width is None:
            if not tokens:
                raise unexpected_end(source, data)
            width = parse_int_token(tokens[0], source, 1, INT64_MAX)
            tokens = tokens[1:]
    except DataError as error:
        return data_failure(TOOL, error)

    status = 0
    current = 0  # length of the current output line; 0 before the first word
    for token in tokens:
        size = length(token.text, use_bytes)
        if size > width:
            common.err.write(
                encode_arg(f"{TOOL}: {source}:{token.line}: ")
                + b"word length exceeds line length '"
                + token.text
                + b"'\n"
            )
            status = 1
        if current == 0:
            common.write(token.text)
            current = size
        elif size < width - current:  # current + 1 + size <= width, without overflow
            common.write(b" " + token.text)
            current += 1 + size
        else:
            common.write(b"\n" + token.text)
            current = size
    if tokens:
        common.write(b"\n")
    return status
