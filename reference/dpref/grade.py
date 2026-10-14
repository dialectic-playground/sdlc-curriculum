"""Reference implementation of dp-grade (projects/20-bargraph-grade/specs/SRS.md).

Input is read incrementally, one token at a time, so the tool can be used interactively: a
token is complete as soon as the whitespace byte after it arrives. A run of 0x1A bytes is held
back until the next byte shows whether it reaches the end of the input (CONV-37).
"""

from __future__ import annotations

import sys
from typing import BinaryIO

from .common import (PROMPT, WHITESPACE, DataError, Token, UsageError, data_failure,
                     file_failure, fix, handle_action, open_input, out, parse_args,
                     parse_int_token, parse_real_token, prompt, usage_failure, write)

TOOL = "dp-grade"
HELP_TEXT = """\
Usage: dp-grade [OPTION]... [FILE]
Assign a pass/fail grade from a mid-term score, a final-exam score, and the
weight of the mid term.

Read whitespace-separated answers from FILE, or from standard input when FILE
is absent or -.  Each round starts with 1 (compute a grade) or 0 (stop); after
1 come the mid-term and final scores (whole numbers 0-10) and the mid-term
weight (0-1, used to the nearest 0.001).  The grade is P when
weight*midterm + (1-weight)*final exceeds 7, and F otherwise.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
"""
ANSWER_PROMPT = "Compute another grade (1 = Yes, 0 = No)? "
RECORD_PROMPT = "Enter mid term, final, weight: "
MIN_SCORE, MAX_SCORE = 0, 10
PASS_THOUSANDTHS = 7000  # an average of 7 in thousandths of a point
CTRL_Z = b"\x1a"


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
                return b""  # the run reaches the end of input: ignored
            if following != CTRL_Z:
                self.pushback = run[1:] + following + self.pushback
                return CTRL_Z
            run += following

    def token(self) -> Token | None:
        """The next token, or None at the end of input."""
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


def weight_thousandths(weight: float) -> int:
    """The weight rounded to the nearest 0.001, as an integer number of thousandths."""
    return int(fix(weight, 3).replace(".", ""))


def grade(mid_term: int, final: int, thousandths: int) -> str:
    """P when the weighted average exceeds 7, computed exactly in thousandths of a point."""
    average = thousandths * mid_term + (1000 - thousandths) * final
    return "P" if average > PASS_THOUSANDTHS else "F"


def session(reader: TokenReader, source: str, prompts: bool) -> None:
    while True:
        prompt(prompts, ANSWER_PROMPT)
        token = reader.token()
        if token is None:
            return
        if parse_int_token(token, source, 0, 1) == 0:
            return
        prompt(prompts, RECORD_PROMPT)
        mid_term = parse_int_token(reader.require(source), source, MIN_SCORE, MAX_SCORE)
        final = parse_int_token(reader.require(source), source, MIN_SCORE, MAX_SCORE)
        token = reader.require(source)
        weight = parse_real_token(token, source)
        if not 0.0 <= weight <= 1.0:
            raise DataError(source, token.line, b"value out of range '" + token.text + b"'")
        write(f"Grade is: {grade(mid_term, final, weight_thousandths(weight))}\n")
        out.flush()


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, [PROMPT])
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
        session(TokenReader(stream), source, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0
