"""Shared input loop of dp-fact, dp-tower, dp-walk-r, and dp-walk-nr (projects/23-recursion).

Each tool reads integer tokens (CONV-32, CONV-33) from FILE or standard input until the end of
the input and answers each one as soon as its token is complete (SRS-23 FR-01 … FR-04). A
token is complete when the whitespace byte after it has been read, or at the end of the input;
a trailing run of 0x1A bytes is ignored (CONV-37).
"""

from __future__ import annotations

import sys
from typing import Callable

from . import common
from .common import (PROMPT, DataError, InputError, InputStream, Token, UsageError,
                     data_failure, file_failure, handle_action, open_input, parse_args, prompt,
                     usage_failure)


def run_tool(argv: list[str], tool: str, help_text: str, prompt_text: str,
             answer: Callable[[Token, str], None]) -> int:
    """Parse arguments, then call ``answer(token, source)`` for every token, in order.

    ``answer`` validates the token (raising DataError) and writes the record; this loop
    flushes standard output after each record and writes the prompt before each read.
    """
    try:
        parsed = parse_args(argv, [PROMPT])
        if handle_action(tool, parsed, help_text):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
    except UsageError as error:
        return usage_failure(tool, error)

    source = parsed.operands[0] if parsed.operands else "-"
    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(tool, source, error)
        return 1
    try:
        stream = InputStream(handle)
        while True:
            prompt(prompting, prompt_text)
            token = stream.token()
            if token is None:
                return 0
            answer(token, source)
            common.out.flush()
    except DataError as error:
        return data_failure(tool, error)
    except InputError as failure:
        file_failure(tool, source, failure.error)
        return 1
    finally:
        if handle is not sys.stdin.buffer:
            handle.close()
