"""Reference implementation of dp-find (projects/06-find-lite/specs/SRS.md).

Processing is split into the phases the SRS describes:

1. :func:`scan`   - split the arguments into start paths and expression tokens, validate
                    every primary's arguments, and honour ``--help`` / ``--version`` (FR-02).
2. :class:`Parser` - build the expression tree with find's precedence rules (FR-03, FR-04).
3. :func:`traverse` - walk each start path pre-order, evaluating the tree per entry (FR-05).
"""

from __future__ import annotations

import os
import stat
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from . import common
from ._find_glob import compile_glob
from .common import (
    UsageError,
    diagnose,
    encode_arg,
    file_error_reason,
    usage_failure,
    write,
)

TOOL = "dp-find"
HELP_TEXT = """\
Usage: dp-find [PATH]... [EXPRESSION]
Search directory trees, evaluating EXPRESSION for every entry found.

With no PATH, search the current directory '.'.  If EXPRESSION contains no
action, -print is applied to every entry for which EXPRESSION is true.

Operators (highest precedence first):
  ( EXPR )             group EXPR
  ! EXPR, -not EXPR    true if EXPR is false
  EXPR EXPR, EXPR -a EXPR
                       true if both are true (the right one is skipped
                       if the left one is false)
  EXPR -o EXPR         true if either is true (the right one is skipped
                       if the left one is true)

Global options (always true):
  -maxdepth N          descend at most N levels below the starting points
  -mindepth N          do not evaluate entries fewer than N levels deep

Tests:
  -name GLOB           base name matches GLOB (* ? [...] [!...] \\)
  -iname GLOB          like -name, but ASCII letters match either case
  -type f|d            entry is a regular file (f) or a directory (d)
  -size [+|-]N[ckMG]   size rounded up to whole units (c bytes, k KiB,
                       M MiB, G GiB, default 512-byte blocks) is more
                       than (+), less than (-), or exactly N
  -mtime [+|-]N        last modified more than (+), less than (-), or
                       exactly N whole days ago
  -empty               entry is an empty regular file or empty directory

Actions:
  -print               print the path followed by a newline; true
  -exec COMMAND ;      run COMMAND with every {} replaced by the path;
                       true if it exits with status 0

Options:
      --help           display this help and exit
      --version        output version information and exit
"""

IS_WINDOWS = os.name == "nt"
SEPARATORS = "/\\" if IS_WINDOWS else "/"
MAX_DEPTH_VALUE = 2_147_483_647
MAX_NUMBER = 9_223_372_036_854_775_807
NS_PER_DAY = 86_400 * 1_000_000_000
SIZE_UNITS = {"c": 1, "k": 1024, "M": 1024**2, "G": 1024**3}
DEFAULT_SIZE_UNIT = 512
OPERATORS = {"(", ")", "!", "-not", "-a", "-o"}
NO_ARG_PRIMARIES = {"-empty", "-print"}
ONE_ARG_PRIMARIES = {
    "-name",
    "-iname",
    "-type",
    "-size",
    "-mtime",
    "-maxdepth",
    "-mindepth",
}
# Windows paths at or beyond this length need the extended-length prefix (NFR-02).
WINDOWS_LONG_PATH = 248
JUNCTION_TAG = getattr(stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


class HelpRequested(Exception):
    def __init__(self, action: str):
        super().__init__(action)
        self.action = action


# --- runtime context ----------------------------------------------------------------------


@dataclass
class Context:
    now_ns: int
    failed: bool = False


@dataclass
class Entry:
    """One visited file system entry. The directory listing is read at most once (FR-05)."""

    path: str
    name: str
    depth: int
    st: os.stat_result
    ctx: Context
    _listing: list[str] | None = None
    _listed: bool = False

    @property
    def is_dir(self) -> bool:
        # A Windows directory junction is a link, not a directory (FR-05).
        junction = getattr(self.st, "st_reparse_tag", 0) == JUNCTION_TAG
        return stat.S_ISDIR(self.st.st_mode) and not junction

    @property
    def is_file(self) -> bool:
        return stat.S_ISREG(self.st.st_mode)

    def listing(self) -> list[str] | None:
        """Child names in byte-wise order (CONV-21), or None if the directory is unreadable."""
        if not self._listed:
            self._listed = True
            try:
                names = os.listdir(fs_path(self.path))
                self._listing = sorted(names, key=encode_arg)
            except OSError as error:
                diagnose(TOOL, f"{self.path}: {file_error_reason(error)}")
                self.ctx.failed = True
        return self._listing


def fs_path(path: str) -> str:
    """The path to hand to the operating system; long Windows paths get ``\\\\?\\`` (NFR-02).

    Printed paths never carry the prefix: it is applied only at the system-call boundary.
    """
    if not IS_WINDOWS or path == "":
        return path
    full = os.path.abspath(path)
    if len(full) < WINDOWS_LONG_PATH or full.startswith("\\\\?\\"):
        return path
    if full.startswith("\\\\"):
        return "\\\\?\\UNC\\" + full[2:]
    return "\\\\?\\" + full


def join(parent: str, name: str) -> str:
    """Join with ``/`` (CONV-20), without doubling a separator the parent already ends with."""
    if parent and parent[-1] in SEPARATORS:
        return parent + name
    return parent + "/" + name


def base_name(path: str) -> str:
    """Base name of a start path (FR-08): text after the last separator, ignoring trailing ones."""
    stripped = path.rstrip(SEPARATORS)
    if not stripped:
        return path[:1]
    for index in range(len(stripped) - 1, -1, -1):
        if stripped[index] in SEPARATORS:
            return stripped[index + 1 :]
    return stripped


# --- expression tree -----------------------------------------------------------------------

Predicate = Callable[[Entry], bool]


@dataclass
class Node:
    evaluate: Predicate
    is_action: bool = False


def and_node(left: Node, right: Node) -> Node:
    return Node(
        lambda e: left.evaluate(e) and right.evaluate(e),
        left.is_action or right.is_action,
    )


def or_node(left: Node, right: Node) -> Node:
    return Node(
        lambda e: left.evaluate(e) or right.evaluate(e),
        left.is_action or right.is_action,
    )


def not_node(operand: Node) -> Node:
    return Node(lambda e: not operand.evaluate(e), operand.is_action)


def always_true(_entry: Entry) -> bool:
    return True


def print_entry(entry: Entry) -> bool:
    write(encode_arg(entry.path) + b"\n")
    return True


def is_empty(entry: Entry) -> bool:
    if entry.is_file:
        return entry.st.st_size == 0
    if entry.is_dir:
        names = entry.listing()
        return names is not None and not names
    return False


def compare(value: int, sign: str, number: int) -> bool:
    if sign == "+":
        return value > number
    if sign == "-":
        return value < number
    return value == number


def size_test(sign: str, number: int, unit: int) -> Predicate:
    def test(entry: Entry) -> bool:
        units = -(-entry.st.st_size // unit)  # round up to whole units (FR-11)
        return compare(units, sign, number)

    return test


def mtime_test(sign: str, number: int) -> Predicate:
    def test(entry: Entry) -> bool:
        age_days = (
            entry.ctx.now_ns - entry.st.st_mtime_ns
        ) // NS_PER_DAY  # floor (FR-12)
        return compare(age_days, sign, number)

    return test


def exec_action(command: list[str]) -> Predicate:
    def run(entry: Entry) -> bool:
        argv = [word.replace("{}", entry.path) for word in command]
        common.out.flush()  # keep our output ahead of the child's (FR-15)
        common.err.flush()
        try:
            completed = subprocess.run(argv, check=False)
        except OSError as error:
            diagnose(TOOL, f"{argv[0]}: {file_error_reason(error)}")
            entry.ctx.failed = True
            return False
        return completed.returncode == 0

    return run


# --- phase 1: scanning -------------------------------------------------------------------


@dataclass
class Token:
    """An expression token: an operator (``text`` only) or a primary (with ``node``)."""

    text: str
    node: Node | None = None


@dataclass
class Settings:
    max_depth: int | None = None
    min_depth: int = 0
    paths: list[str] = field(default_factory=list)


def parse_signed(value: str) -> tuple[str, str]:
    """Split an optional leading ``+`` or ``-`` from a numeric argument."""
    sign = value[:1] if value[:1] in ("+", "-") else ""
    return sign, value[len(sign) :]


def parse_digits(digits: str, value: str, primary: str, maximum: int) -> int:
    if not digits or not all("0" <= c <= "9" for c in digits) or int(digits) > maximum:
        raise common.invalid_argument(value, primary)
    return int(digits)


def make_primary(primary: str, value: str, settings: Settings) -> Node:
    if primary in ("-name", "-iname"):
        return Node(_name_test(compile_glob(value, fold=primary == "-iname")))
    if primary == "-type":
        if value == "f":
            return Node(lambda e: e.is_file)
        if value == "d":
            return Node(lambda e: e.is_dir)
        raise common.invalid_argument(value, primary)
    if primary == "-size":
        sign, rest = parse_signed(value)
        unit = DEFAULT_SIZE_UNIT
        if rest[-1:] in SIZE_UNITS:
            unit = SIZE_UNITS[rest[-1]]
            rest = rest[:-1]
        return Node(
            size_test(sign, parse_digits(rest, value, primary, MAX_NUMBER), unit)
        )
    if primary == "-mtime":
        sign, rest = parse_signed(value)
        return Node(mtime_test(sign, parse_digits(rest, value, primary, MAX_NUMBER)))
    depth = parse_digits(value, value, primary, MAX_DEPTH_VALUE)
    if primary == "-maxdepth":
        settings.max_depth = depth
    else:
        settings.min_depth = depth
    return Node(always_true)


def _name_test(matches: Callable[[str], bool]) -> Predicate:
    return lambda entry: matches(entry.name)


def is_expression_start(token: str) -> bool:
    return token.startswith("-") or token in ("(", ")", "!")


def scan(argv: list[str]) -> tuple[Settings, list[Token]]:
    """Phase 1 (FR-02): classify every argument left to right."""
    settings = Settings()
    index = 0
    while index < len(argv) and not is_expression_start(argv[index]):
        settings.paths.append(argv[index])
        index += 1
    tokens: list[Token] = []
    while index < len(argv):
        token = argv[index]
        index += 1
        if token in ("--help", "--version"):
            raise HelpRequested(token[2:])
        if token in OPERATORS:
            tokens.append(Token(token))
        elif token in NO_ARG_PRIMARIES:
            node = (
                Node(print_entry, is_action=True)
                if token == "-print"
                else Node(is_empty)
            )
            tokens.append(Token(token, node))
        elif token in ONE_ARG_PRIMARIES:
            if index >= len(argv):
                raise UsageError(f"missing argument to '{token}'")
            value = argv[index]
            index += 1
            tokens.append(Token(token, make_primary(token, value, settings)))
        elif token == "-exec":
            end = index
            while end < len(argv) and argv[end] != ";":
                end += 1
            if end >= len(argv) or end == index:
                raise UsageError("missing argument to '-exec'")
            tokens.append(
                Token(token, Node(exec_action(argv[index:end]), is_action=True))
            )
            index = end + 1
        elif token.startswith("-"):
            raise UsageError(f"unknown primary '{token}'")
        else:
            raise UsageError(f"paths must precede expression: '{token}'")
    return settings, tokens


# --- phase 2: parsing --------------------------------------------------------------------

BINARY = ("-a", "-o")
PREFIX = ("!", "-not")


class Parser:
    """Recursive descent over: or := and {-o and}; and := unary {[-a] unary};
    unary := (! | -not) unary | ( or ) | primary   (FR-03)."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.index = 0

    def peek(self) -> str | None:
        return self.tokens[self.index].text if self.index < len(self.tokens) else None

    def previous(self) -> str | None:
        return self.tokens[self.index - 1].text if self.index > 0 else None

    def parse(self) -> Node | None:
        if not self.tokens:
            return None
        node = self.parse_or()
        if self.peek() == ")":
            raise UsageError("unexpected ')'")
        return node

    def parse_or(self) -> Node:
        node = self.parse_and()
        while self.peek() == "-o":
            self.index += 1
            node = or_node(node, self.parse_and())
        return node

    def parse_and(self) -> Node:
        node = self.parse_unary()
        while True:
            upcoming = self.peek()
            if upcoming == "-a":
                self.index += 1
            elif upcoming is None or upcoming in (")", "-o"):
                return node
            node = and_node(node, self.parse_unary())

    def parse_unary(self) -> Node:
        upcoming = self.peek()
        if upcoming is None or upcoming == ")" or upcoming in BINARY:
            raise self.missing_operand(upcoming)
        token = self.tokens[self.index]
        self.index += 1
        if upcoming in PREFIX:
            return not_node(self.parse_unary())
        if upcoming == "(":
            node = self.parse_or()
            if self.peek() != ")":
                raise UsageError("missing ')'")
            self.index += 1
            return node
        assert token.node is not None
        return token.node

    def missing_operand(self, upcoming: str | None) -> UsageError:
        """The diagnostic for a missing operand, chosen as FR-04 specifies."""
        before = self.previous()
        if before in PREFIX or before in BINARY:
            return UsageError(f"expected an expression after '{before}'")
        if upcoming in BINARY:
            return UsageError(f"expected an expression before '{upcoming}'")
        if before == "(":
            return UsageError("empty parentheses" if upcoming == ")" else "missing ')'")
        return UsageError("unexpected ')'")


def build_expression(tokens: list[Token]) -> Node:
    """Parse the tokens and apply the default -print rule (FR-06)."""
    node = Parser(tokens).parse()
    printer = Node(print_entry, is_action=True)
    if node is None:
        return printer
    if not node.is_action:
        return and_node(node, printer)
    return node


# --- phase 3: traversal ------------------------------------------------------------------


def lstat_or_report(path: str, ctx: Context) -> os.stat_result | None:
    try:
        return os.lstat(fs_path(path))
    except OSError as error:
        diagnose(TOOL, f"{path}: {file_error_reason(error)}")
        ctx.failed = True
        return None


def traverse(start: str, expression: Node, settings: Settings, ctx: Context) -> None:
    """Pre-order walk of one start path (FR-05). Symbolic links are never followed."""
    stack: list[tuple[str, str, int]] = [(start, base_name(start), 0)]
    while stack:
        path, name, depth = stack.pop()
        st = lstat_or_report(path, ctx)
        if st is None:
            continue
        entry = Entry(path, name, depth, st, ctx)
        if depth >= settings.min_depth:
            expression.evaluate(entry)
        if entry.is_dir and (settings.max_depth is None or depth < settings.max_depth):
            names = entry.listing() or []
            stack.extend(
                (join(path, child), child, depth + 1) for child in reversed(names)
            )


def main(argv: list[str]) -> int:
    try:
        settings, tokens = scan(argv)
        expression = build_expression(tokens)
    except HelpRequested as request:
        write(
            HELP_TEXT.encode()
            if request.action == "help"
            else common.version_line(TOOL)
        )
        return 0
    except UsageError as error:
        return usage_failure(TOOL, error)
    ctx = Context(now_ns=time.time_ns())
    for start in settings.paths or ["."]:
        traverse(start, expression, settings, ctx)
    return 1 if ctx.failed else 0
