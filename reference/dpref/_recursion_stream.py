"""Shared input loop of dp-fact, dp-tower, dp-walk-r, and dp-walk-nr (projects/23-recursion).

Each tool reads integer tokens (CONV-32, CONV-33) from FILE or standard input until the end of
the input and answers each one as soon as its token is complete (SRS-23 FR-01 … FR-04). A
token is complete when the whitespace byte after it has been read, or at the end of the input;
a trailing run of 0x1A bytes is ignored (CONV-37).
"""

from __future__ import annotations

import sys
from typing import BinaryIO, Callable, Iterator

from . import common
from .common import (PROMPT, WHITESPACE, DataError, Token, UsageError, data_failure,
                     file_failure, handle_action, open_input, parse_args, prompt,
                     usage_failure)

CHUNK_SIZE = 64 * 1024


class InputError(Exception):
    """A read failure on the input (as opposed to a write failure on standard output)."""

    def __init__(self, error: OSError):
        super().__init__(error)
        self.error = error


def _read(handle: BinaryIO) -> bytes:
    try:
        return handle.read1(CHUNK_SIZE)  # type: ignore[attr-defined]
    except OSError as error:
        raise InputError(error) from error


def stream_tokens(handle: BinaryIO) -> Iterator[Token]:
    """Yield CONV-32 tokens as soon as each is complete; CONV-37 applies at the end."""
    line = 1
    token_line = 1
    current = bytearray()
    while True:
        chunk = _read(handle)
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
    # Only the last token can end in a run of 0x1A bytes that reaches the end of the input.
    text = bytes(current).rstrip(b"\x1a")
    if text:
        yield Token(text, token_line)


def run_tool(argv: list[str], tool: str, help_text: str, prompt_text: str,
             answer: Callable[[Token, str], None]) -> int:
    """Parse arguments, then call ``answer(token, source)`` for every token, in order.

    ``answer`` validates the token (raising DataError) and writes the record; this loop
    flushes standard output after each record and writes the prompt before each read.
    """
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(tool, parsed, help_text):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(tool, error)

    source = parsed.operands[0] if parsed.operands else "-"
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(tool, source, error)
        return 1
    try:
        tokens = stream_tokens(handle)
        while True:
            prompt(prompting, prompt_text)
            token = next(tokens, None)
            if token is None:
                return 0
            answer(token, source)
            common.out.flush()
    except DataError as error:
        return data_failure(tool, error)
    except InputError as failure:
        file_failure(tool, source, failure.error)
        return 1
    finally:
        if handle is not sys.stdin.buffer:
            handle.close()
