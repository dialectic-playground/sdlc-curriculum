"""Worker protocol shared by dp-sort-host and dp-sort-child (projects/34-parallel-sort).

The worker reads a request (a count, then that many values) as CONV-32 tokens, stops reading
as soon as the last value is complete, selection-sorts the values, and writes the reply (one
decimal value per line). dp-sort-child serves one request on its standard streams; the
dp-sort-host reference serves it in a thread over a pipe pair.
"""

from __future__ import annotations

from typing import BinaryIO, Iterator

from .common import WHITESPACE, DataError, Token, parse_int_token

MAX_VALUES = 100000


class TokenStream:
    """Incremental CONV-32 tokenizer that never reads past the token it is completing."""

    def __init__(self, handle: BinaryIO, source: str):
        self.handle = handle
        self.source = source
        self.line = 1  # 1 + the LF bytes consumed so far
        self.buffer = b""
        self.position = 0
        self.at_end = False

    def _fill(self) -> bool:
        if self.at_end:
            return False
        chunk = self.handle.read1(65536)  # type: ignore[attr-defined]
        if not chunk:
            self.at_end = True
            return False
        self.buffer, self.position = chunk, 0
        return True

    def next(self) -> Token | None:
        """The next complete token, or None at the end of the input (CONV-37 applied).

        The whitespace byte that completes a token is left unconsumed, so no read is made
        after it.
        """
        current = bytearray()
        token_line = self.line
        while True:
            while self.position < len(self.buffer):
                byte = self.buffer[self.position]
                if byte in WHITESPACE:
                    if current:
                        return Token(bytes(current), token_line)
                    if byte == 0x0A:
                        self.line += 1
                elif not current:
                    token_line = self.line
                    current.append(byte)
                else:
                    current.append(byte)
                self.position += 1
            if not self._fill():
                text = bytes(current).rstrip(b"\x1a")
                return Token(text, token_line) if text else None

    def end_error(self) -> DataError:
        """``unexpected end of input`` at the end-of-input line number (CONV-32, CONV-34)."""
        return DataError(self.source, self.line, "unexpected end of input")


def read_request(handle: BinaryIO, source: str) -> list[int]:
    """Read the count and the values of one request (FR-03 of SRS-34)."""
    stream = TokenStream(handle, source)
    token = stream.next()
    if token is None:
        raise stream.end_error()
    count = parse_int_token(token, source, 0, MAX_VALUES)
    values = []
    for _ in range(count):
        token = stream.next()
        if token is None:
            raise stream.end_error()
        values.append(parse_int_token(token, source))
    return values


def selection_sort(values: list[int]) -> None:
    """Selection sort in place: the first smallest remaining value is exchanged into place."""
    for i in range(len(values) - 1):
        smallest = values.index(min(values[i:]), i)
        if smallest != i:
            values[i], values[smallest] = values[smallest], values[i]


def reply_lines(values: list[int]) -> Iterator[bytes]:
    for value in values:
        yield b"%d\n" % value


def serve(request: BinaryIO, reply: BinaryIO, source: str) -> None:
    """Serve one request: read it, sort it, write and flush the reply."""
    values = read_request(request, source)
    selection_sort(values)
    reply.write(b"".join(reply_lines(values)))
    reply.flush()
