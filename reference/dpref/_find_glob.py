"""Glob matching for dp-find ``-name`` / ``-iname`` (projects/06-find-lite/specs/SRS.md, FR-08).

The pattern language is deliberately small and fully specified by the SRS, so it is
implemented here rather than borrowed from :mod:`fnmatch` (which has no backslash escape and
case-folds on Windows). A pattern is translated once into an anchored regular expression.
"""

from __future__ import annotations

import re
from collections.abc import Callable

_NEVER = "(?!)"  # matches nothing: a non-negated bracket expression with an empty set


def fold_ascii(text: str) -> str:
    """Map ``A``-``Z`` to ``a``-``z``; every other character is unchanged (FR-09)."""
    return text.translate(_ASCII_FOLD)


_ASCII_FOLD = {code: code + 32 for code in range(ord("A"), ord("Z") + 1)}


def _bracket(pattern: str, start: int) -> tuple[str, int] | None:
    """Translate the bracket expression whose ``[`` is at ``start``.

    Returns (regex, index after the closing ``]``), or None when there is no closing ``]``,
    in which case the ``[`` is an ordinary character.
    """
    index = start + 1
    negate = index < len(pattern) and pattern[index] == "!"
    if negate:
        index += 1
    members: list[str] = []
    first = True
    while index < len(pattern):
        char = pattern[index]
        if char == "]" and not first:
            break
        first = False
        if char == "\\" and index + 1 < len(pattern):
            index += 1
            char = pattern[index]
        index += 1
        # A range is c1 '-' c2, where the '-' is not the last member before ']'.
        if (
            index + 1 < len(pattern)
            and pattern[index] == "-"
            and pattern[index + 1] != "]"
        ):
            high_index = index + 1
            high = pattern[high_index]
            if high == "\\" and high_index + 1 < len(pattern):
                high_index += 1
                high = pattern[high_index]
            index = high_index + 1
            if char <= high:
                members.append(f"{re.escape(char)}-{re.escape(high)}")
            continue
        members.append(re.escape(char))
    else:
        return None
    body = "".join(members)
    if not body:
        regex = "." if negate else _NEVER
    else:
        regex = f"[{'^' if negate else ''}{body}]"
    return regex, index + 1


def translate(pattern: str) -> str:
    """Translate a dp-find glob into an equivalent Python regular expression."""
    parts: list[str] = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        index += 1
        if char == "*":
            parts.append(".*")
        elif char == "?":
            parts.append(".")
        elif char == "\\":
            if index < len(pattern):
                parts.append(re.escape(pattern[index]))
                index += 1
            else:
                parts.append(re.escape("\\"))
        elif char == "[":
            bracket = _bracket(pattern, index - 1)
            if bracket is None:
                parts.append(re.escape("["))
            else:
                regex, index = bracket
                parts.append(regex)
        else:
            parts.append(re.escape(char))
    return "".join(parts)


def compile_glob(pattern: str, *, fold: bool = False) -> Callable[[str], bool]:
    """Return a predicate testing whether a whole base name matches ``pattern``."""
    if fold:
        regex = re.compile(translate(fold_ascii(pattern)), re.DOTALL)
        return lambda name: regex.fullmatch(fold_ascii(name)) is not None
    regex = re.compile(translate(pattern), re.DOTALL)
    return lambda name: regex.fullmatch(name) is not None
