"""Reference implementation of dp-taxes (projects/13-taxes/specs/SRS.md).

Incomes are tokenized incrementally (CONV-32) so that each record is written, and standard
output flushed, as soon as the income's token is complete: the tool works interactively.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from . import common
from ._taxes_rule import MAX_INCOME, record
from .common import (PROMPT, DataError, Option, Token, UsageError, WHITESPACE,
                     data_failure, file_failure, handle_action, open_input, parse_args,
                     parse_int_token, prompt, usage_failure)

TOOL = "dp-taxes"
PROMPT_TEXT = "Enter income: "
CHUNK_SIZE = 64 * 1024
HELP_TEXT = """\
Usage: dp-taxes [OPTION]... [FILE]
Compute the progressive income tax for each income in FILE.

With no FILE, or when FILE is -, read standard input.  Incomes are whole
numbers from 0 to 9223372036854775807, separated by whitespace, and are read
until the end of the input.  An income below 6000 greenbacks is taxed at 30%,
any other income at 60%; the tax is rounded down to a whole number.

Options:
  -p, --prompt    write the prompt 'Enter income: ' to standard error before
                    each income is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]


def stream_tokens(handle: BinaryIO) -> Iterator[Token]:
    """Yield CONV-32 tokens as soon as each is complete; CONV-37 applies at the end."""
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
    # A run of 0x1A bytes reaching the end of the input is ignored (CONV-37). Only the last
    # token can contain it, because the run must not be followed by any other byte.
    text = bytes(current).rstrip(b"\x1a")
    if text:
        yield Token(text, token_line)


class _WriteFailure(Exception):
    """Carries a standard-output failure past the input-error handler to common.run."""

    def __init__(self, error: OSError):
        super().__init__(error)
        self.error = error


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
            token = next(tokens, None)
            if token is None:
                return 0
            income = parse_int_token(token, source, 0, MAX_INCOME)
            try:
                common.write(record(income))
                common.out.flush()
            except OSError as error:
                raise _WriteFailure(error) from error
    except DataError as error:
        return data_failure(TOOL, error)
    except _WriteFailure as failure:
        raise failure.error from None  # common.run: CONV-25 or `write error`
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()
