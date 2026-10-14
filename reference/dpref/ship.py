"""Reference implementation of dp-ship (projects/52-spacecraft/specs/SRS.md).

The spacecraft is one encapsulated class (default and full construction, velocity adjustment
clamped at 0, basics report, trip time). With no FILE the textbook scenario runs; otherwise a
command script is read whole and executed line by line, stopping at the first data error.
"""

from __future__ import annotations

import math

from . import common
from .common import (DataError, Option, Token, UsageError, data_failure, file_failure, gen,
                     handle_action, parse_args, parse_int_token, parse_real_token, read_all,
                     strip_eof_marker, tokenize, usage_failure)

TOOL = "dp-ship"
PRECISION = 6
HELP_TEXT = """\
Usage: dp-ship [OPTION]... [FILE]
Model spacecraft and report their basics and trip times.

With no FILE, run the textbook scenario.  Otherwise run the command script in
FILE (standard input when FILE is -), one command per line:
  new ID                          create ship ID with default values
  new ID MASS VEL DIST CAP NAME   create ship ID with the given values
  adjust ID DIFF                  add DIFF to the velocity (never below 0)
  print ID                        report the ship's basics
  trip ID                         report the time the ship needs for its trip
Empty lines and lines whose first word starts with # are ignored.

Options:
      --help      display this help and exit
      --version   output version information and exit
"""

SCENARIO = b"""\
new s1
print s1
new s2 5000 63567 560989 4 MightyMite
print s2
adjust s2 2000
adjust s2 -1000
print s2
trip s2
"""

OPTIONS: list[Option] = []
ARITY = {b"adjust": (2,), b"print": (1,), b"trip": (1,), b"new": (1, 6)}


class Spacecraft:
    """A spacecraft whose state is reachable only through its operations."""

    def __init__(self, mass: float = 0.0, velocity: float = 0.0, distance: float = 0.0,
                 capacity: int = 0, name: bytes = b"???"):
        self._mass = mass
        self._velocity = velocity
        self._distance = distance
        self._capacity = capacity
        self._name = name

    @property
    def name(self) -> bytes:
        return self._name

    @property
    def mass(self) -> float:
        return self._mass

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def distance(self) -> float:
        return self._distance

    @property
    def capacity(self) -> int:
        return self._capacity

    def adjust_velocity(self, difference: float) -> bool:
        """Add ``difference``; a negative result becomes 0. False if the sum overflows."""
        result = self._velocity + difference
        if math.isinf(result):
            return False
        self._velocity = 0.0 if result < 0 else result
        return True

    def trip_time(self) -> float | None:
        """Hours for the trip, or None when distance / velocity is not a finite number."""
        if self._velocity == 0:
            return None
        hours = self._distance / self._velocity
        return hours if math.isfinite(hours) else None

    def basics(self) -> bytes:
        return (self._name + f" has a mass of {gen(self._mass, PRECISION)}\n"
                f"and a velocity of {gen(self._velocity, PRECISION)} and holds "
                f"{self._capacity} astronauts for a trip of "
                f"{gen(self._distance, PRECISION)} kilometers.\n\n".encode())

    def trip_report(self) -> bytes:
        hours = self.trip_time()
        if hours is None:
            return self._name + (" cannot make the trip at a velocity of "
                                 f"{gen(self._velocity, PRECISION)}.\n").encode()
        return self._name + f" requires {gen(hours, PRECISION)} hours for trip.\n".encode()


def non_negative_real(token: Token, source: str) -> float:
    value = parse_real_token(token, source)
    if value < 0:
        raise DataError(source, token.line, b"value out of range '" + token.text + b"'")
    return value


def execute(fields: list[Token], ships: dict[bytes, Spacecraft], source: str) -> None:
    command, arguments = fields[0], fields[1:]
    line = command.line
    arity = ARITY.get(command.text)
    if arity is None:
        raise DataError(source, line, b"unknown command '" + command.text + b"'")
    if len(arguments) > max(arity):
        raise DataError(source, line, b"extra argument '" + arguments[max(arity)].text + b"'")
    if len(arguments) not in arity:
        raise DataError(source, line, b"missing argument for '" + command.text + b"'")
    ident = arguments[0].text
    if command.text == b"new":
        if ident in ships:
            raise DataError(source, line, b"ship '" + ident + b"' already exists")
        if len(arguments) == 1:
            ships[ident] = Spacecraft()
            return
        mass, velocity, distance = (non_negative_real(t, source) for t in arguments[1:4])
        capacity = parse_int_token(arguments[4], source, 0)
        ships[ident] = Spacecraft(mass, velocity, distance, capacity, arguments[5].text)
        return
    ship = ships.get(ident)
    if ship is None:
        raise DataError(source, line, b"unknown ship '" + ident + b"'")
    if command.text == b"adjust":
        difference = parse_real_token(arguments[1], source)
        if not ship.adjust_velocity(difference):
            raise DataError(source, line,
                            b"value out of range '" + arguments[1].text + b"'")
    elif command.text == b"print":
        common.write(ship.basics())
    else:
        common.write(ship.trip_report())


def run_script(data: bytes, source: str) -> None:
    ships: dict[bytes, Spacecraft] = {}
    for number, text in enumerate(strip_eof_marker(data).split(b"\n"), start=1):
        fields = [Token(t.text, number) for t in tokenize(text)]
        if not fields or fields[0].text.startswith(b"#"):
            continue
        execute(fields, ships, source)


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    if not parsed.operands:
        run_script(SCENARIO, "-")
        return 0
    source = parsed.operands[0]
    try:
        data = read_all(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        run_script(data, source)
    except DataError as error:
        return data_failure(TOOL, error)
    return 0
