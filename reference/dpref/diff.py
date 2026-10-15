"""Reference implementation of dp-diff (projects/07-diff-lite/specs/SRS.md).

The comparison computes the *canonical edit script* of SRS section 4.2 directly from its
definition: a longest-common-subsequence table over line suffixes, followed by a forward walk
with fixed tie-breaking. No shortcut (prefix/suffix trimming, Myers, heuristics) is used, so
the model is the definition itself. It is quadratic in time and memory, which is fine for the
small fixture files it exists to verify.
"""

from __future__ import annotations

from dataclasses import dataclass

from .common import (
    Option,
    UsageError,
    encode_arg,
    file_failure,
    handle_action,
    open_input,
    parse_args,
    parse_count,
    usage_failure,
    write,
)

TOOL = "dp-diff"
DEFAULT_CONTEXT = 3
MAX_CONTEXT = 2147483647
NO_NEWLINE_MARKER = b"\\ No newline at end of file\n"
# Stands in for the absent value of a bare `--unified`; a NUL can never occur in a real
# command-line argument, so it cannot collide with user input.
BARE_UNIFIED = "\x00"

HELP_TEXT = """\
Usage: dp-diff [OPTION]... FILE1 FILE2
Compare two files line by line.

With no options, the differences are written in normal format. If FILE1 or
FILE2 is -, standard input is read; at most one operand may be -.

Options:
  -q, --brief               report only whether the files differ
  -u                        output unified format with 3 lines of context
  -U NUM, --unified[=NUM]   output unified format with NUM lines of context
                              (default 3)
      --strip-trailing-cr   remove a carriage return that precedes a line feed
                              in the input
      --help                display this help and exit
      --version             output version information and exit

Exit status is 0 if the files are the same, 1 if they differ, 2 if trouble.
"""

OPTIONS = [
    Option("brief", short="q", long="brief"),
    # -u, -U NUM, and --unified[=NUM] all set the context size; the last one wins.
    Option("context", short="u"),
    Option("context", short="U", long="unified", takes_value=True),
    Option("strip_cr", long="strip-trailing-cr"),
]


# --- argument handling ---------------------------------------------------------------------


def mark_bare_unified(argv: list[str]) -> list[str]:
    """Rewrite each bare ``--unified`` option token to ``--unified=<BARE_UNIFIED>``.

    ``--unified`` takes an *optional* argument (only ``--unified=NUM`` supplies one), which
    the shared parser does not model. The scan mirrors the parser so that a token consumed as
    the value of ``-U`` or following ``--`` is left untouched.
    """
    result: list[str] = []
    index = 0
    while index < len(argv):
        token = argv[index]
        index += 1
        if token == "--":
            result.append(token)
            result.extend(argv[index:])
            break
        if token == "--unified":
            result.append("--unified=" + BARE_UNIFIED)
            continue
        result.append(token)
        if token.startswith("-") and not token.startswith("--") and token != "-":
            position = token.find("U", 1)
            if position == len(token) - 1 and index < len(argv):
                result.append(argv[index])  # the separate value of -U
                index += 1
    return result


@dataclass(frozen=True)
class Settings:
    brief: bool
    context: int | None  # None selects normal format
    strip_cr: bool
    paths: tuple[str, str]


def parse_settings(argv: list[str]) -> Settings | None:
    """Return the settings, or None after --help/--version. Raises UsageError."""
    parsed = parse_args(mark_bare_unified(argv), OPTIONS)
    if handle_action(TOOL, parsed, HELP_TEXT):
        return None
    if len(parsed.operands) < 2:
        raise UsageError("missing operand")
    if len(parsed.operands) > 2:
        raise UsageError(f"extra operand '{parsed.operands[2]}'")
    if parsed.operands == ["-", "-"]:
        raise UsageError("'-' may be given as only one operand")
    context: int | None = None
    if "context" in parsed.values:
        value = parsed.values["context"]
        if value is True or value == BARE_UNIFIED:
            context = DEFAULT_CONTEXT
        else:
            context = parse_count(
                str(value), parsed.spelled["context"], maximum=MAX_CONTEXT
            )
    return Settings(
        brief=bool(parsed.values.get("brief")),
        context=context,
        strip_cr=bool(parsed.values.get("strip_cr")),
        paths=(parsed.operands[0], parsed.operands[1]),
    )


# --- input -----------------------------------------------------------------------------------


def split_lines(data: bytes) -> list[bytes]:
    """Split into lines, each keeping its LF; a final fragment without LF is a line too."""
    lines = data.split(b"\n")
    last = lines.pop()
    result = [line + b"\n" for line in lines]
    if last:
        result.append(last)
    return result


def read_lines(path: str, strip_cr: bool) -> list[bytes]:
    with open_input(path) as stream:  # closing stdin here is harmless: it is read once
        data = stream.read()
    if strip_cr:
        data = data.replace(b"\r\n", b"\n")
    return split_lines(data)


# --- the canonical edit script (SRS 4.2) ---------------------------------------------------


@dataclass(frozen=True)
class Change:
    """A maximal run of non-keep operations: a[i1:i2] is replaced by b[j1:j2] (0-based)."""

    i1: int
    i2: int
    j1: int
    j2: int


def lcs_table(a: list[bytes], b: list[bytes]) -> list[list[int]]:
    """L[i][j] = length of a longest common subsequence of a[i:] and b[j:]."""
    n, m = len(a), len(b)
    table = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n - 1, -1, -1):
        row, below = table[i], table[i + 1]
        for j in range(m - 1, -1, -1):
            if a[i] == b[j]:
                row[j] = below[j + 1] + 1
            else:
                row[j] = max(below[j], row[j + 1])
    return table


def edit_script(a: list[bytes], b: list[bytes]) -> str:
    """The canonical edit script as a string of 'K' (keep), 'D' (delete), 'I' (insert)."""
    table = lcs_table(a, b)
    ops: list[str] = []
    i = j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            ops.append("K")
            i += 1
            j += 1
        elif table[i + 1][j] >= table[i][j + 1]:
            ops.append("D")
            i += 1
        else:
            ops.append("I")
            j += 1
    ops.extend("D" * (len(a) - i))
    ops.extend("I" * (len(b) - j))
    return "".join(ops)


def changes(ops: str) -> list[Change]:
    result: list[Change] = []
    i = j = 0
    start: tuple[int, int] | None = None
    for op in ops + "K":  # the sentinel keep closes a trailing change
        if op == "K":
            if start is not None:
                result.append(Change(start[0], i, start[1], j))
                start = None
            i += 1
            j += 1
            continue
        if start is None:
            start = (i, j)
        if op == "D":
            i += 1
        else:
            j += 1
    return result


# --- output formats --------------------------------------------------------------------------


def output_line(prefix: bytes, line: bytes) -> bytes:
    if line.endswith(b"\n"):
        return prefix + line
    return prefix + line + b"\n" + NO_NEWLINE_MARKER


def normal_range(first: int, last: int) -> str:
    """1-based inclusive line range in normal format."""
    return str(first) if first == last else f"{first},{last}"


def normal_format(a: list[bytes], b: list[bytes], found: list[Change]) -> bytes:
    parts: list[bytes] = []
    for change in found:
        if change.i1 == change.i2:
            command = f"{change.i1}a{normal_range(change.j1 + 1, change.j2)}"
        elif change.j1 == change.j2:
            command = f"{normal_range(change.i1 + 1, change.i2)}d{change.j1}"
        else:
            command = (
                f"{normal_range(change.i1 + 1, change.i2)}c"
                f"{normal_range(change.j1 + 1, change.j2)}"
            )
        parts.append(command.encode() + b"\n")
        parts.extend(output_line(b"< ", line) for line in a[change.i1 : change.i2])
        if change.i1 != change.i2 and change.j1 != change.j2:
            parts.append(b"---\n")
        parts.extend(output_line(b"> ", line) for line in b[change.j1 : change.j2])
    return b"".join(parts)


def unified_range(start: int, count: int) -> str:
    """Hunk-header range for the 0-based half-open range starting at ``start``."""
    if count == 0:
        return f"{start},0"
    if count == 1:
        return str(start + 1)
    return f"{start + 1},{count}"


def group_hunks(found: list[Change], context: int) -> list[list[Change]]:
    """Group changes whose separating run of kept lines is at most 2*context long."""
    hunks: list[list[Change]] = []
    for change in found:
        if hunks and change.i1 - hunks[-1][-1].i2 <= 2 * context:
            hunks[-1].append(change)
        else:
            hunks.append([change])
    return hunks


def unified_format(
    a: list[bytes],
    b: list[bytes],
    found: list[Change],
    context: int,
    paths: tuple[str, str],
) -> bytes:
    parts = [encode_arg(f"--- {paths[0]}\n+++ {paths[1]}\n")]
    for hunk in group_hunks(found, context):
        first, last = hunk[0], hunk[-1]
        lead = min(context, first.i1)
        trail = min(context, len(a) - last.i2)
        a_lo, a_hi = first.i1 - lead, last.i2 + trail
        b_lo, b_hi = first.j1 - lead, last.j2 + trail
        parts.append(
            f"@@ -{unified_range(a_lo, a_hi - a_lo)} "
            f"+{unified_range(b_lo, b_hi - b_lo)} @@\n".encode()
        )
        position = a_lo
        for change in hunk:
            parts.extend(output_line(b" ", line) for line in a[position : change.i1])
            parts.extend(output_line(b"-", line) for line in a[change.i1 : change.i2])
            parts.extend(output_line(b"+", line) for line in b[change.j1 : change.j2])
            position = change.i2
        parts.extend(output_line(b" ", line) for line in a[position:a_hi])
    return b"".join(parts)


# --- entry point -----------------------------------------------------------------------------


def main(argv: list[str]) -> int:
    try:
        settings = parse_settings(argv)
    except UsageError as error:
        return usage_failure(TOOL, error)
    if settings is None:
        return 0

    contents: list[list[bytes]] = []
    for path in settings.paths:  # CONV-17: report every unreadable operand
        try:
            contents.append(read_lines(path, settings.strip_cr))
        except OSError as error:
            file_failure(TOOL, path, error)
    if len(contents) != 2:
        return 2
    a, b = contents

    if a == b:
        return 0
    if settings.brief:
        write(f"Files {settings.paths[0]} and {settings.paths[1]} differ\n")
        return 1
    found = changes(edit_script(a, b))
    if settings.context is None:
        write(normal_format(a, b, found))
    else:
        write(unified_format(a, b, found, settings.context, settings.paths))
    return 1
