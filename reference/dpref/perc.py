"""Reference implementation of dp-perc (projects/32-percolation/specs/SRS.md).

Densities and answers are read incrementally, one token at a time, so the tool works
interactively: each simulation is written as soon as its density is complete. A run of 0x1A
bytes is held back until the next byte shows whether it reaches the end of the input
(CONV-37). One CONV-38 generator, seeded once, serves every simulation of a session.
"""

from __future__ import annotations

import sys
from typing import BinaryIO

from .common import (PROMPT, WHITESPACE, AnsiRand, DataError, Option, Token, UsageError,
                     data_failure, file_failure, fix, handle_action, open_input, out,
                     parse_args, parse_count, parse_int_token, parse_seed, prompt,
                     usage_failure, write)

TOOL = "dp-perc"
DEFAULT_SIZE = 25
MAX_SIZE = 78
DENSITY_PROMPT = "Enter density (1-100): "
AGAIN_PROMPT = "Again? (y/n) "
TREE, NO_TREE, BURNING = "T", " ", "*"
CTRL_Z = b"\x1a"
HELP_TEXT = """\
Usage: dp-perc [OPTION]... [FILE]
Simulate a forest fire spreading through a randomly planted square forest.

Read whitespace-separated responses from FILE, or from standard input when
FILE is absent or -: a tree density in percent (1-100), then after each
simulation an answer y or n to 'Again?'.  Each simulation plants the forest,
sets the top row on fire, lets the fire spread downward, and prints the forest
before and after the fire with statistics.

Options:
  -p, --prompt       write prompts to standard error before reading
  -s, --size=SIZE    use a SIZE by SIZE forest (1-78, default 25)
      --seed=SEED    seed the random number generator (0-4294967295,
                       default 1)
      --help         display this help and exit
      --version      output version information and exit
"""

OPTIONS = [
    PROMPT,
    Option("size", short="s", long="size", takes_value=True),
    Option("seed", long="seed", takes_value=True),
]


class InputError(Exception):
    """A read failure on the input (as opposed to a write failure on standard output)."""

    def __init__(self, error: OSError):
        super().__init__(error)
        self.error = error


class TokenReader:
    """CONV-32 tokens read one byte at a time, with CONV-37 applied on the fly."""

    def __init__(self, stream: BinaryIO):
        self.stream = stream
        self.pushback = b""
        self.line = 1  # 1 + LF bytes consumed so far

    def _raw(self) -> bytes:
        if self.pushback:
            byte, self.pushback = self.pushback[:1], self.pushback[1:]
            return byte
        try:
            return self.stream.read(1)
        except OSError as error:
            raise InputError(error) from error

    def _byte(self) -> bytes:
        byte = self._raw()
        if byte != CTRL_Z:
            return byte
        run = byte
        while True:
            following = self._raw()
            if following == b"":
                return b""  # the run reaches the end of the input: ignored
            if following != CTRL_Z:
                self.pushback = run[1:] + following + self.pushback
                return CTRL_Z
            run += following

    def token(self) -> Token | None:
        """The next token, or None at the end of the input."""
        byte = self._byte()
        while byte and byte in WHITESPACE:
            if byte == b"\n":
                self.line += 1
            byte = self._byte()
        if not byte:
            return None
        start_line, text = self.line, byte
        while True:
            byte = self._byte()
            if not byte:
                break
            if byte in WHITESPACE:
                if byte == b"\n":
                    self.line += 1
                break
            text += byte
        return Token(text, start_line)

    def require(self, source: str) -> Token:
        token = self.token()
        if token is None:
            raise DataError(source, self.line, "unexpected end of input")
        return token


Forest = list[list[str]]


def plant(size: int, density: int, rand: AnsiRand) -> Forest:
    """One draw per cell in row-major order; a tree iff (r mod 100) + 1 <= density."""
    return [[TREE if rand.next() % 100 + 1 <= density else NO_TREE for _ in range(size)]
            for _ in range(size)]


def burn(forest: Forest) -> Forest:
    """Ignite the top row, then spread the fire downward, one row at a time."""
    size = len(forest)
    burned = [row[:] for row in forest]
    burned[0] = [BURNING if cell == TREE else cell for cell in burned[0]]
    for r in range(1, size):
        above = burned[r - 1]
        for c in range(size):
            if burned[r][c] == TREE and BURNING in above[max(c - 1, 0):c + 2]:
                burned[r][c] = BURNING
    return burned


def render(title: str, forest: Forest) -> str:
    border = "+" + "-" * len(forest) + "+\n"
    rows = "".join("|" + "".join(row) + "|\n" for row in forest)
    return f"{title}\n{border}{rows}{border}"


def count_trees(forest: Forest) -> int:
    return sum(row.count(TREE) for row in forest)


def simulate(size: int, density: int, rand: AnsiRand) -> str:
    before = plant(size, density, rand)
    after = burn(before)
    trees = count_trees(before)
    actual = (100 * trees) / (size * size)
    return (render("Forest before fire:", before) + render("Forest after fire:", after)
            + f"Requested density: {density}%\n"
            + f"Actual density: {fix(actual, 2)}%\n"
            + f"Trees at start: {trees}\n"
            + f"Trees surviving: {count_trees(after)}\n")


def session(reader: TokenReader, source: str, prompts: bool, size: int,
            rand: AnsiRand) -> None:
    while True:
        prompt(prompts, DENSITY_PROMPT)
        density = parse_int_token(reader.require(source), source, 1, 100)
        write(simulate(size, density, rand))
        out.flush()
        prompt(prompts, AGAIN_PROMPT)
        token = reader.token()
        if token is None or token.text in (b"n", b"N"):
            return
        if token.text not in (b"y", b"Y"):
            raise DataError(source, token.line, b"invalid answer '" + token.text + b"'")


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        size = DEFAULT_SIZE
        if "size" in parsed.values:
            size = parse_count(str(parsed.values["size"]), parsed.spelled["size"], 1,
                               MAX_SIZE)
        seed = parse_seed(parsed)
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
        session(TokenReader(stream), source, bool(parsed.values.get("prompt")), size,
                AnsiRand(seed))
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0
