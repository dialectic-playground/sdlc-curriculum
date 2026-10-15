"""Reference implementation of dp-tromino (projects/24-tromino/specs/SRS.md).

The input is read incrementally, one token at a time, so the tool can be used interactively:
each tiling is written, and standard output flushed, as soon as the missing square's second
coordinate is complete. A run of 0x1A bytes is held back until the next byte shows whether it
reaches the end of the input (CONV-37).
"""

from __future__ import annotations

import sys
from collections.abc import Iterator

from .common import (
    PROMPT,
    DataError,
    InputError,
    InputStream,
    Option,
    UsageError,
    data_failure,
    file_failure,
    handle_action,
    open_input,
    out,
    parse_args,
    parse_int_token,
    prompt,
    usage_failure,
    write,
)

TOOL = "dp-tromino"
HELP_TEXT = """\
Usage: dp-tromino [OPTION]... [FILE]
Tile a 2^k-by-2^k board with one missing square using L-shaped trominoes.

Read whitespace-separated answers from FILE, or from standard input when FILE
is absent or -.  Each round gives a board size (2, 4, 8, 16, 32, or 64; 0 to
quit) and the x and y coordinates of the missing square (0 to size-1, with
0 0 the lower-left square).  For each tromino placed, in divide-and-conquer
order, a line gives the center of its 2-by-2 block and its orientation (UL,
UR, LR, or LL: the corner where its two arms meet).

Options:
  -d, --draw      after each tiling, draw the board with numbered trominoes
  -p, --prompt    write prompts to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
"""
SIZE_PROMPT = "Enter size of board (0 to quit): "
SQUARE_PROMPT = "Enter coordinates of missing square: "
MAX_SIZE = 64
VALID_SIZES = {2**k for k in range(1, 7)}
DRAW = Option("draw", short="d", long="draw")

# Orientation of a tromino = the corner of its 2x2 block opposite the uncovered square.
# Corners are (right, upper) pairs.
NAMES = {(0, 1): "UL", (1, 1): "UR", (1, 0): "LR", (0, 0): "LL"}
QUADRANT_ORDER = ((0, 1), (1, 1), (1, 0), (0, 0))  # UL, UR, LR, LL


def tile(
    x_board: int, y_board: int, x_missing: int, y_missing: int, size: int
) -> Iterator[tuple[int, int, str]]:
    """Trominoes (center x, center y, orientation) in the order of SRS-24 FR-04."""
    if size < 2:
        return
    half = size // 2
    x_center, y_center = x_board + half, y_board + half
    hole = (int(x_missing >= x_center), int(y_missing >= y_center))
    yield x_center, y_center, NAMES[(1 - hole[0], 1 - hole[1])]
    for right, upper in QUADRANT_ORDER:
        x_sub = x_center if right else x_board
        y_sub = y_center if upper else y_board
        if (right, upper) == hole:
            sub_missing = (x_missing, y_missing)
        else:
            sub_missing = (
                x_center if right else x_center - 1,
                y_center if upper else y_center - 1,
            )
        yield from tile(x_sub, y_sub, *sub_missing, half)


def covered(x: int, y: int, name: str) -> list[tuple[int, int]]:
    """The three squares covered by the tromino with block center (x, y)."""
    elbow = next(corner for corner, text in NAMES.items() if text == name)
    missing = (1 - elbow[0], 1 - elbow[1])
    return [
        (x - 1 + dx, y - 1 + dy)
        for dx in (0, 1)
        for dy in (0, 1)
        if (dx, dy) != missing
    ]


def report(size: int, x_missing: int, y_missing: int, draw: bool) -> bytes:
    trominoes = list(tile(0, 0, x_missing, y_missing, size))
    lines = ["Tiling", "------"]
    lines += [f"{x} {y} {name}" for x, y, name in trominoes]
    if draw:
        width = len(str(len(trominoes)))
        board: list[list[str]] = [["X".rjust(width)] * size for _ in range(size)]
        for number, (x, y, name) in enumerate(trominoes, start=1):
            for col, row in covered(x, y, name):
                board[row][col] = str(number).rjust(width)
        lines += ["Board", "-----"]
        lines += [" ".join(board[row]) for row in range(size - 1, -1, -1)]
    return ("\n".join(lines) + "\n").encode("ascii")


def session(reader: InputStream, source: str, prompts: bool, draw: bool) -> None:
    while True:
        prompt(prompts, SIZE_PROMPT)
        token = reader.token()
        if token is None:
            return
        size = parse_int_token(token, source)
        if size == 0:
            return
        if size not in VALID_SIZES:
            raise DataError(
                source, token.line, b"invalid board size '" + token.text + b"'"
            )
        prompt(prompts, SQUARE_PROMPT)
        x_missing = parse_int_token(reader.require(source), source, 0, size - 1)
        y_missing = parse_int_token(reader.require(source), source, 0, size - 1)
        write(report(size, x_missing, y_missing, draw))
        out.flush()


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [DRAW, PROMPT])
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        stream = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        session(
            InputStream(stream),
            source,
            bool(parsed.values.get("prompt")),
            bool(parsed.values.get("draw")),
        )
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0
