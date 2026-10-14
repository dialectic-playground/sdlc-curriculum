"""Reference implementation of dp-convert (projects/12-convert/specs/SRS.md).

Lengths are tokenized incrementally (CONV-32) so that each block is written, and standard
output flushed, as soon as the length's token is complete; nothing after the sentinel is read.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from . import common
from .common import (PROMPT, DataError, Option, Token, UsageError, WHITESPACE,
                     data_failure, file_failure, handle_action, open_input, parse_args,
                     parse_int_token, prompt, usage_failure)

TOOL = "dp-convert"
PROMPT_TEXT = "Enter next length "
END_BANNER = b"*** END OF PROGRAM ***\n"
FEET_PER_YARD = 3
INCHES_PER_YARD = 36
MAX_YARDS = (2 ** 63 - 1) // INCHES_PER_YARD  # 256204778801521550
CHUNK_SIZE = 64 * 1024
HELP_TEXT = """\
Usage: dp-convert [OPTION]... [FILE]
Convert lengths in yards to feet and inches.

With no FILE, or when FILE is -, read standard input.  Lengths are whole
numbers of yards from 0 to 256204778801521550, separated by whitespace.  A
negative number ends the input: it prints '*** END OF PROGRAM ***', and
nothing after it is read.

Options:
  -p, --prompt    write the prompt 'Enter next length ' to standard error
                    before each length is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]


class EndOfInput(Exception):
    """The input ended before the sentinel; carries the end-of-input line number."""

    def __init__(self, line: int):
        super().__init__(line)
        self.line = line


def stream_tokens(handle: BinaryIO) -> Iterator[Token]:
    """Yield CONV-32 tokens as soon as each is complete; CONV-37 applies at the end.

    When the input is exhausted, raises EndOfInput with the end-of-input line number.
    """
    line = 1
    current = bytearray()
    token_line = 1
    while True:
        chunk = handle.read1(CHUNK_SIZE)  # type: ignore[attr-defined]
        if not chunk:
            break
        for byte in chunk:
            if byte in WHITESPACE:
                if current:
                    yield Token(bytes(current), token_line)
                    current.clear()
                if byte == 0x0A:
                    line += 1
            else:
                if not current:
                    token_line = line
                current.append(byte)
    # A trailing run of 0x1A bytes contains no LF, so it never changes the line count.
    text = bytes(current).rstrip(b"\x1a")
    if text:
        yield Token(text, token_line)
    raise EndOfInput(line)


def block(yards: int) -> bytes:
    """The three output lines for one length of 0 … MAX_YARDS yards."""
    feet = yards * FEET_PER_YARD
    inches = yards * INCHES_PER_YARD
    return f"{yards} yd =\n{feet} ft\n{inches} in\n".encode("ascii")


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
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        tokens = stream_tokens(handle)
        while True:
            prompt(prompting, PROMPT_TEXT)
            try:
                token = next(tokens)
            except EndOfInput as end:
                raise DataError(source, end.line, "unexpected end of input") from None
            yards = parse_int_token(token, source)
            if yards < 0:
                common.write(END_BANNER)
                return 0
            if yards > MAX_YARDS:
                raise DataError(source, token.line,
                                b"value out of range '" + token.text + b"'")
            common.write(block(yards))
            common.out.flush()
    except DataError as error:
        return data_failure(TOOL, error)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()
