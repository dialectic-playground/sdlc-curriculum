"""Reference implementation of dp-reverse (projects/33-reverse/specs/SRS.md).

Each string is reversed in place with converging indices. In character mode the bytes of
every multibyte character are first reversed in place, then the whole buffer is reversed, so
the characters come out in reverse order with their own bytes in the original order.
"""

from __future__ import annotations

from . import common
from ._strings import char_length, length, lines
from .common import (PROMPT, DataError, Option, UsageError, data_failure, file_failure,
                     handle_action, parse_args, prompt, read_all, strip_eof_marker, tokenize,
                     usage_failure)

TOOL = "dp-reverse"
PROMPT_TEXT = "Enter a string:\t"
MAX_LENGTH = 100
HELP_TEXT = """\
Usage: dp-reverse [OPTION]... [FILE]
Reverse each string read from FILE and print it.

With no FILE, or when FILE is -, read standard input.  A string is a word (a
run of bytes other than whitespace), or a whole line with -l.  A string may
be at most 100 characters long.  Characters are UTF-8 code points, and each
byte of an invalid sequence is one character; with -b, the string's bytes are
reversed and counted instead.

Options:
  -l, --lines    read each line as one string
  -b, --bytes    reverse and count bytes instead of characters
  -p, --prompt   write the prompt 'Enter a string:' and a tab to standard error
                   before each string is read
      --help     display this help and exit
      --version  output version information and exit
"""

OPTIONS = [
    Option("lines", short="l", long="lines"),
    Option("bytes", short="b", long="bytes"),
    PROMPT,
]


def reverse_range(buffer: bytearray, left: int, right: int) -> None:
    """Reverse buffer[left..right] (inclusive) in place with converging indices."""
    while left < right:
        buffer[left], buffer[right] = buffer[right], buffer[left]
        left += 1
        right -= 1


def reverse(buffer: bytearray, use_bytes: bool) -> None:
    if not use_bytes:
        pos = 0
        while pos < len(buffer):
            size = char_length(buffer, pos)
            reverse_range(buffer, pos, pos + size - 1)
            pos += size
    reverse_range(buffer, 0, len(buffer) - 1)


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
    prompting = bool(parsed.values.get("prompt"))
    use_bytes = bool(parsed.values.get("bytes"))
    try:
        data = read_all(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1

    if parsed.values.get("lines"):
        strings = lines(data)
    else:
        strings = [(token.text, token.line) for token in tokenize(strip_eof_marker(data))]
    unit = "bytes" if use_bytes else "characters"
    try:
        for text, line in strings:
            prompt(prompting, PROMPT_TEXT)
            if length(text, use_bytes) > MAX_LENGTH:
                raise DataError(source, line, f"string exceeds {MAX_LENGTH} {unit}")
            buffer = bytearray(text)
            reverse(buffer, use_bytes)
            common.write(b"Reversed string:\t" + bytes(buffer) + b"\n")
            common.out.flush()
        prompt(prompting, PROMPT_TEXT)
    except DataError as error:
        return data_failure(TOOL, error)
    return 0
