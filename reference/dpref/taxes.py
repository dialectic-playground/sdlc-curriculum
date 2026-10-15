"""Reference implementation of dp-taxes (projects/13-taxes/specs/SRS.md).

Incomes are tokenized incrementally (CONV-32) so that each record is written, and standard
output flushed, as soon as the income's token is complete: the tool works interactively.
"""

from __future__ import annotations

from . import common
from ._taxes_rule import MAX_INCOME, record
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
    parse_args,
    parse_int_token,
    prompt,
    usage_failure,
)

TOOL = "dp-taxes"
PROMPT_TEXT = "Enter income: "
HELP_TEXT = """\
Usage: dp-taxes [OPTION]... [FILE]
Compute the progressive income tax for each income in FILE.

With no FILE, or when FILE is -, read standard input.  Incomes are whole
numbers from 0 to 9223372036854775807, separated by whitespace, and are read
until the end of the input.  An income below 6000 greenbacks is taxed at 30%,
any other income at 60%; the tax is rounded down to a whole number.

Options:
  -p, --prompt    write the prompt 'Enter income: ' to standard error before
                    each income is read
      --help      display this help and exit
      --version   output version information and exit
"""

OPTIONS: list[Option] = [PROMPT]


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
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        stream = InputStream(handle)
        while True:
            prompt(prompting, PROMPT_TEXT)
            token = stream.token()
            if token is None:
                return 0
            income = parse_int_token(token, source, 0, MAX_INCOME)
            common.write(record(income))  # write errors reach common.run (CONV-25)
            common.out.flush()
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as failure:
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if source != "-":
            handle.close()
