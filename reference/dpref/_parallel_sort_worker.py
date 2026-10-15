"""Worker protocol shared by dp-sort-host and dp-sort-child (projects/34-parallel-sort).

The worker reads a request (a count, then that many values) as CONV-32 tokens, stops reading
as soon as the last value is complete, selection-sorts the values, and writes the reply (one
decimal value per line). dp-sort-child serves one request on its standard streams; the
dp-sort-host reference serves it in a thread over a pipe pair.
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import BinaryIO

from .common import InputStream, parse_int_token

MAX_VALUES = 100000


def read_request(handle: BinaryIO, source: str) -> list[int]:
    """Read the count and the values of one request (FR-03 of SRS-34).

    No read is made after the last value is complete. Read failures raise InputError.
    """
    stream = InputStream(handle)
    count = parse_int_token(stream.require(source), source, 0, MAX_VALUES)
    return [parse_int_token(stream.require(source), source) for _ in range(count)]


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
