"""Reference implementation of dp-resistor (projects/21-resistor/specs/SRS.md).

The dialog reads tokens incrementally (CONV-32) so that each resistance is written, and
standard output flushed, as soon as the third code of a resistor is complete.
"""

from __future__ import annotations

from . import common
from .common import (PROMPT, DataError, InputError, InputStream, Option, Token,
                     UsageError, data_failure, file_failure, handle_action, open_input,
                     parse_args, parse_int_token, prompt, usage_failure)

TOOL = "dp-resistor"
CODES_PROMPT = "Enter the three color codes: "
ANSWER_PROMPT = "Decode another resistor (1 = yes, 0 = no)? "
HELP_TEXT = """\
Usage: dp-resistor [OPTION]... [FILE]
Decode the color codes of 3-band resistors into resistances.

With no FILE, or when FILE is -, read standard input.  The color guide is
written first.  Each resistor is then given as three codes separated by
whitespace, one letter per band, in either case: B black 0, N brown 1,
R red 2, O orange 3, Y yellow 4, G green 5, E blue 6, V violet 7, A gray 8,
W white 9.  After each resistance, answer 1 to decode another resistor or 0
to stop.  An invalid code is reported and the three codes are asked for again.

Options:
  -p, --prompt    write prompts to standard error before each read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]

COLORS = [  # (code, color name), in the order of their digit values 0 ... 9
    ("B", "Black"), ("N", "Brown"), ("R", "Red"), ("O", "Orange"), ("Y", "Yellow"),
    ("G", "Green"), ("E", "Blue"), ("V", "Violet"), ("A", "Gray"), ("W", "White"),
]
DIGITS = {code.encode(): value for value, (code, _) in enumerate(COLORS)}
GUIDE = "Resistor color codes\nCode  Color   Value\n" + "".join(
    f"{code}     {name:<8}{value}\n" for value, (code, name) in enumerate(COLORS))


def code_value(token: Token) -> int | None:
    """The digit of a one-letter color code (ASCII letters only, either case)."""
    return DIGITS.get(token.text.upper()) if len(token.text) == 1 else None


def resistance_text(d1: int, d2: int, d3: int) -> str:
    ohms = (10 * d1 + d2) * 10 ** d3
    if ohms >= 1_000_000:
        return common.fix(ohms / 1_000_000, 6) + " mega-ohms"
    if ohms >= 1_000:
        return common.fix(ohms / 1_000, 6) + " kilo-ohms"
    return common.fix(float(ohms), 6) + " ohms"


def dialog(tokens: InputStream, source: str, prompting: bool) -> int:
    rejected = False
    while True:
        common.out.flush()
        prompt(prompting, CODES_PROMPT)
        first = tokens.token()
        if first is None:
            break
        bands = [first]
        for _ in range(2):
            bands.append(tokens.require(source))
        values = [code_value(token) for token in bands]
        if None in values:
            rejected = True
            common.out.flush()
            for token, value in zip(bands, values):
                if value is None:
                    data_failure(TOOL, DataError(
                        source, token.line, b"invalid color code '" + token.text + b"'"))
            continue
        letters = " ".join(COLORS[value][0] for value in values)  # type: ignore[index]
        common.write(f"Resistance of {letters} = {resistance_text(*values)}\n")  # type: ignore[arg-type]
        common.out.flush()
        prompt(prompting, ANSWER_PROMPT)
        token = tokens.token()
        if token is None or parse_int_token(token, source, 0, 1) == 0:
            break
    return 1 if rejected else 0


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        common.write(GUIDE)
        return dialog(InputStream(handle), source, bool(parsed.values.get("prompt")))
    except DataError as error:
        common.out.flush()
        return data_failure(TOOL, error)
    except InputError as failure:
        common.out.flush()
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if source != "-":
            handle.close()
