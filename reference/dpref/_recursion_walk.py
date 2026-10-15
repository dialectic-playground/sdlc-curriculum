"""Robot-walk record and validation shared by dp-walk-r and dp-walk-nr (projects/23-recursion).

W(1) = 1, W(2) = 2, W(d) = W(d-1) + W(d-2): the number of ways to walk d meters in steps of
1 and 2 meters (SRS-23 FR-09 … FR-12). The two tools differ only in how W is computed and in
their largest distance.
"""

from __future__ import annotations

from collections.abc import Callable

from .common import DataError, Token, parse_int_token, write

PROMPT_TEXT = "Enter distance: "
NOT_POSITIVE = b"ERROR -- distance must be positive."


def answerer(
    walk: Callable[[int], int], max_distance: int
) -> Callable[[Token, str], None]:
    def answer(token: Token, source: str) -> None:
        distance = parse_int_token(token, source, maximum=max_distance)
        if distance < 1:
            raise DataError(source, token.line, NOT_POSITIVE)
        write(
            f"The robot can walk {distance} meters in {walk(distance)} ways.\n".encode(
                "ascii"
            )
        )

    return answer
