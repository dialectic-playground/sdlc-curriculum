"""Reference implementation of dp-grade (projects/20-bargraph-grade/specs/SRS.md).

Input is read incrementally, one token at a time, so the tool can be used interactively: a
token is complete as soon as the whitespace byte after it arrives. A run of 0x1A bytes is held
back until the next byte shows whether it reaches the end of the input (CONV-37).
"""

from __future__ import annotations

import sys

from .common import (PROMPT, DataError, InputError, InputStream, UsageError, data_failure,
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


def weight_thousandths(weight: float) -> int:
    """The weight rounded to the nearest 0.001, as an integer number of thousandths."""
    return int(fix(weight, 3).replace(".", ""))


def grade(mid_term: int, final: int, thousandths: int) -> str:
    """P when the weighted average exceeds 7, computed exactly in thousandths of a point."""
    average = thousandths * mid_term + (1000 - thousandths) * final
    return "P" if average > PASS_THOUSANDTHS else "F"


def session(reader: InputStream, source: str, prompts: bool) -> None:
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
        session(InputStream(stream), source, bool(parsed.values.get("prompt")))
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if stream is not sys.stdin.buffer:
            stream.close()
    return 0
