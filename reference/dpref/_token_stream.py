"""Streaming CONV-32 tokenizer shared by dp-stats (projects/15-stats) and dp-average and
dp-chk-sort (projects/17-stream-filters).

The tools of these projects must run in constant memory and dp-chk-sort must stop reading at
the first inversion, so tokens are produced incrementally from chunked reads instead of from a
whole-input buffer. Only the token being read is held.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from .common import WHITESPACE, Token

CHUNK_SIZE = 64 * 1024


def stream_tokens(handle: BinaryIO) -> Iterator[Token]:
    """Yield CONV-32 tokens as each is complete; CONV-37 (text data) applies at the end."""
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
    # A run of 0x1A bytes that reaches the end of the input is ignored (CONV-37). Only the
    # last token can contain it, because the run must not be followed by any other byte.
    text = bytes(current).rstrip(b"\x1a")
    if text:
        yield Token(text, token_line)
