"""Reference implementation of dp-primes (projects/18-primes/specs/SRS.md).

The bound n is the first token of the input. It is read incrementally (CONV-32) so that the
tool answers as soon as n has been typed, without waiting for the end of the input.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from . import common
from .common import (PROMPT, DataError, Option, Token, UsageError, WHITESPACE,
                     data_failure, file_failure, handle_action, open_input, parse_args,
                     parse_int_token, prompt, usage_failure)

TOOL = "dp-primes"
MAX_N = 10_000_000
PROMPT_TEXT = "\tThis program lists all primes <= n\n\nInput n: "
CHUNK_SIZE = 64 * 1024
HELP_TEXT = """\
Usage: dp-primes [OPTION]... [FILE]
List every prime number less than or equal to n.

With no FILE, or when FILE is -, read standard input.  n is the first whole
number in the input; anything after it is ignored.  n may be negative, but it
must not exceed 10000000.  The output is a header line (a TAB, then
'Primes <= n:'), a blank line, and the primes in ascending order, one per
line.

Options:
  -c, --count     write only the number of primes <= n
  -p, --prompt    write the program banner and the prompt 'Input n: ' to
                    standard error before n is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [Option("count", short="c", long="count"), PROMPT]


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
    text = bytes(current).rstrip(b"\x1a")
    if text:
        yield Token(text, token_line)
    else:
        yield Token(b"", line)  # end of input; the line is the end-of-input line number


def primes_up_to(n: int) -> list[int]:
    """All primes p with 2 <= p <= n, ascending (sieve of Eratosthenes)."""
    if n < 2:
        return []
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    p = 2
    while p * p <= n:
        if sieve[p]:
            sieve[p * p::p] = bytes(len(range(p * p, n + 1, p)))
        p += 1
    return [i for i in range(2, n + 1) if sieve[i]]


def report(n: int, count_only: bool) -> bytes:
    primes = primes_up_to(n)
    if count_only:
        return f"{len(primes)}\n".encode()
    lines = [f"\tPrimes <= {n}:\n\n", *(f"{p}\n" for p in primes)]
    return "".join(lines).encode()


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
    try:
        prompt(bool(parsed.values.get("prompt")), PROMPT_TEXT)
        token = next(stream_tokens(handle))
        if not token.text:
            raise DataError(source, token.line, "unexpected end of input")
        n = parse_int_token(token, source, maximum=MAX_N)
    except DataError as error:
        return data_failure(TOOL, error)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    finally:
        if source != "-":
            handle.close()
    common.write(report(n, bool(parsed.values.get("count"))))
    return 0
