"""Incremental token reader for the keyboard dialogs of dp-resistor (Project 21) and dp-dice
(Project 22).

Tokens (CONV-32) are returned as soon as each is complete, so a dialog can answer each
response before the next one is typed; a trailing run of Ctrl-Z bytes is ignored (CONV-37).
"""

from __future__ import annotations

from typing import BinaryIO

from .common import DataError, Token, WHITESPACE

CHUNK_SIZE = 64 * 1024


class TokenStream:
    """CONV-32 tokens yielded as soon as each is complete; CONV-37 applies at the end."""

    def __init__(self, handle: BinaryIO):
        self.handle = handle
        self.line = 1
        self.pending: list[Token] = []
        self.current = bytearray()
        self.token_line = 1
        self.eof = False

    def next(self) -> Token | None:
        while not self.pending and not self.eof:
            chunk = self.handle.read1(CHUNK_SIZE)  # type: ignore[attr-defined]
            if not chunk:
                self.eof = True
                text = bytes(self.current).rstrip(b"\x1a")
                if text:
                    self.pending.append(Token(text, self.token_line))
                break
            for byte in chunk:
                if byte in WHITESPACE:
                    if self.current:
                        self.pending.append(Token(bytes(self.current), self.token_line))
                        self.current.clear()
                    if byte == 0x0A:
                        self.line += 1
                else:
                    if not self.current:
                        self.token_line = self.line
                    self.current.append(byte)
        return self.pending.pop(0) if self.pending else None

    def unexpected_end(self, source: str) -> DataError:
        return DataError(source, self.line, "unexpected end of input")
