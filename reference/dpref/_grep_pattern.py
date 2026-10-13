"""Portable ERE subset for dp-grep (projects/05-grep-lite/specs/SRS.md, section 5).

The pattern is parsed and validated against the SRS grammar by this module, never by Python's
``re`` parser, so that every construct ``re`` would accept but the SRS excludes (backreferences,
lookaround, lazy quantifiers, ``\\d`` and friends) is rejected with the SRS diagnostic. A valid
pattern is then translated into an equivalent, fully explicit ``re`` byte pattern: every
bracket expression becomes an explicit byte set (with ASCII case folding applied when needed),
anchors become ``\\A`` / ``\\Z``, and groups become non-capturing.

Matching is byte-oriented: a line is a byte string and ``.`` matches exactly one byte.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MAX_BOUND = 255             # largest m or n in {m}, {m,}, {m,n}
MAX_REPEAT_PRODUCT = 1000   # largest product of nested repetition weights
MAX_DEPTH = 100             # deepest permitted group nesting

METACHARACTERS = frozenset(b"^.[]$()|*+?{}\\")
QUANTIFIER_STARTS = frozenset(b"*+?{")
INTERVAL = re.compile(rb"\{([0-9]+)(?:(,)([0-9]*))?\}")
WORD_BYTES = frozenset(b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_")


def _byte_range(first: int, last: int) -> frozenset[int]:
    return frozenset(range(first, last + 1))


_UPPER = _byte_range(0x41, 0x5A)
_LOWER = _byte_range(0x61, 0x7A)
_DIGIT = _byte_range(0x30, 0x39)
CHARACTER_CLASSES: dict[bytes, frozenset[int]] = {
    b"alpha": _UPPER | _LOWER,
    b"digit": _DIGIT,
    b"alnum": _UPPER | _LOWER | _DIGIT,
    b"upper": _UPPER,
    b"lower": _LOWER,
    b"space": _byte_range(0x09, 0x0D) | {0x20},
    b"blank": frozenset({0x09, 0x20}),
    b"punct": (_byte_range(0x21, 0x2F) | _byte_range(0x3A, 0x40)
               | _byte_range(0x5B, 0x60) | _byte_range(0x7B, 0x7E)),
    b"print": _byte_range(0x20, 0x7E),
    b"graph": _byte_range(0x21, 0x7E),
    b"cntrl": _byte_range(0x00, 0x1F) | {0x7F},
    b"xdigit": _DIGIT | _byte_range(0x41, 0x46) | _byte_range(0x61, 0x66),
}


class PatternError(Exception):
    """An invalid or unsupported pattern; ``reason`` is the SRS diagnostic reason (bytes)."""

    def __init__(self, reason: bytes):
        super().__init__(reason)
        self.reason = reason


# --- syntax tree ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Char:
    """One literal character: a single byte, or the bytes of one UTF-8 encoded character."""
    data: bytes


@dataclass(frozen=True)
class AnyByte:
    pass


@dataclass(frozen=True)
class ByteSet:
    members: frozenset[int]  # ASCII bytes named by the bracket expression
    negated: bool


@dataclass(frozen=True)
class Anchor:
    at_start: bool


@dataclass(frozen=True)
class Group:
    body: "Alternation"


@dataclass(frozen=True)
class Repeat:
    node: object
    minimum: int
    maximum: int | None  # None means unbounded


@dataclass(frozen=True)
class Alternation:
    branches: tuple[tuple[object, ...], ...]


# --- parsing -------------------------------------------------------------------------------

def utf8_length(data: bytes, index: int) -> int:
    """Length of the valid UTF-8 character starting at ``index``, or 1 for an invalid byte."""
    lead = data[index]
    if 0xC2 <= lead <= 0xDF:
        size = 2
    elif 0xE0 <= lead <= 0xEF:
        size = 3
    elif 0xF0 <= lead <= 0xF4:
        size = 4
    else:
        return 1
    try:  # a truncated, overlong, or surrogate sequence fails to decode
        data[index:index + size].decode("utf-8", "strict")
    except UnicodeDecodeError:
        return 1
    return size


class _Parser:
    """Left-to-right recursive-descent parser; the first error met is the one reported."""

    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def parse(self) -> Alternation:
        tree, _ = self.alternation(depth=0)
        if self.pos < len(self.data):  # only an unmatched ')' stops the top level early
            raise PatternError(b"unmatched )")
        return tree

    def peek(self) -> int | None:
        return self.data[self.pos] if self.pos < len(self.data) else None

    def alternation(self, depth: int) -> tuple[Alternation, int]:
        """Parse branches separated by '|'. Returns the tree and its repetition weight."""
        branches, weight = [], 1
        while True:
            branch, branch_weight = self.branch(depth)
            branches.append(branch)
            weight = max(weight, branch_weight)
            if self.peek() != ord("|"):
                return Alternation(tuple(branches)), weight
            self.pos += 1

    def branch(self, depth: int) -> tuple[tuple[object, ...], int]:
        pieces: list[object] = []
        weights: list[int] = []
        state = "empty"  # "empty" (nothing to repeat), "atom", or "quantified"
        while (byte := self.peek()) is not None and byte not in b"|)":
            if byte in QUANTIFIER_STARTS:
                if state == "empty":
                    raise PatternError(b"nothing to repeat")
                if state == "quantified":
                    raise PatternError(b"multiple repeat")
                minimum, maximum, factor = self.quantifier()
                weight = weights[-1] * factor
                if weight > MAX_REPEAT_PRODUCT:
                    raise PatternError(b"repetition too large")
                pieces[-1] = Repeat(pieces[-1], minimum, maximum)
                weights[-1] = weight
                state = "quantified"
                continue
            node, weight, quantifiable = self.atom(depth)
            pieces.append(node)
            weights.append(weight)
            state = "atom" if quantifiable else "empty"
        return tuple(pieces), max(weights, default=1)

    def quantifier(self) -> tuple[int, int | None, int]:
        """Parse a quantifier; returns (minimum, maximum, repetition weight)."""
        byte = self.data[self.pos]
        if byte != ord("{"):
            self.pos += 1
            return {ord("*"): (0, None, 1), ord("+"): (1, None, 1), ord("?"): (0, 1, 1)}[byte]
        match = INTERVAL.match(self.data, self.pos)
        if match is None:
            raise PatternError(b"invalid interval")
        minimum = int(match.group(1))
        if match.group(2) is None:
            maximum: int | None = minimum
        elif match.group(3):
            maximum = int(match.group(3))
        else:
            maximum = None
        if minimum > MAX_BOUND or (maximum is not None and
                                   (maximum > MAX_BOUND or minimum > maximum)):
            raise PatternError(b"invalid interval")
        self.pos = match.end()
        return minimum, maximum, max(minimum if maximum is None else maximum, 1)

    def atom(self, depth: int) -> tuple[object, int, bool]:
        """Parse one atom or anchor; returns (node, weight, quantifiable)."""
        data, byte = self.data, self.data[self.pos]
        if byte == ord("("):
            if depth + 1 > MAX_DEPTH:
                raise PatternError(b"nesting too deep")
            self.pos += 1
            body, weight = self.alternation(depth + 1)
            if self.peek() != ord(")"):
                raise PatternError(b"unmatched (")
            self.pos += 1
            return Group(body), weight, True
        if byte in b"^$":
            self.pos += 1
            return Anchor(byte == ord("^")), 1, False
        if byte == ord("."):
            self.pos += 1
            return AnyByte(), 1, True
        if byte == ord("["):
            return self.bracket(), 1, True
        if byte == ord("\\"):
            if self.pos + 1 >= len(data):
                raise PatternError(b"trailing backslash")
            escaped = data[self.pos + 1]
            if escaped not in METACHARACTERS:
                size = utf8_length(data, self.pos + 1)
                raise PatternError(b"unsupported escape \\" + data[self.pos + 1:self.pos + 1 + size])
            self.pos += 2
            return Char(bytes([escaped])), 1, True
        size = utf8_length(data, self.pos)
        self.pos += size
        return Char(data[self.pos - size:self.pos]), 1, True

    # bracket expressions

    def bracket(self) -> ByteSet:
        data = self.data
        self.pos += 1  # '['
        negated = self.peek() == ord("^")
        if negated:
            self.pos += 1
        members: set[int] = set()
        first = True
        while True:
            byte = self.peek()
            if byte is None:
                raise PatternError(b"unmatched [")
            if byte == ord("]") and not first:
                self.pos += 1
                return ByteSet(frozenset(members), negated)
            first = False
            element = self.bracket_element()
            if (self.peek() == ord("-") and self.pos + 1 < len(data)
                    and data[self.pos + 1] != ord("]")):
                if isinstance(element, frozenset):
                    raise PatternError(b"invalid range")
                self.pos += 1  # '-'
                if data[self.pos] == ord("[") and self.pos + 1 < len(data) \
                        and data[self.pos + 1] in b":.=":
                    raise PatternError(b"invalid range")
                last = self.bracket_element()
                assert isinstance(last, int)
                if element > last:
                    raise PatternError(b"invalid range")
                members.update(range(element, last + 1))
            elif isinstance(element, frozenset):
                members.update(element)
            else:
                members.add(element)

    def bracket_element(self) -> int | frozenset[int]:
        """One bracket member: an ASCII byte, or the byte set of a [:class:]."""
        data, byte = self.data, self.data[self.pos]
        if byte >= 0x80:
            raise PatternError(b"non-ASCII character in bracket expression")
        if byte == ord("[") and self.pos + 1 < len(data) and data[self.pos + 1] in b":.=":
            if data[self.pos + 1] != ord(":"):
                raise PatternError(b"unsupported bracket construct")
            end = data.find(b":]", self.pos + 2)
            if end < 0:
                raise PatternError(b"unmatched [")
            name = data[self.pos + 2:end]
            if name not in CHARACTER_CLASSES:
                raise PatternError(b"invalid character class")
            self.pos = end + 2
            return CHARACTER_CLASSES[name]
        self.pos += 1
        return byte


def parse(pattern: bytes) -> Alternation:
    """Validate ``pattern`` against the portable ERE grammar; raises :class:`PatternError`."""
    return _Parser(pattern).parse()


def literal(pattern: bytes) -> Alternation:
    """The tree of a fixed string (-F): one branch of single-byte literals."""
    return Alternation((tuple(Char(bytes([b])) for b in pattern),))


# --- translation to Python re ------------------------------------------------------------

def _fold(byte: int) -> int:
    if 0x41 <= byte <= 0x5A or 0x61 <= byte <= 0x7A:
        return byte ^ 0x20
    return byte


def _byte_class(members: set[int] | frozenset[int]) -> bytes:
    """An explicit re character class for a non-empty set of bytes."""
    parts, ordered, index = [], sorted(members), 0
    while index < len(ordered):
        start = end = ordered[index]
        while index + 1 < len(ordered) and ordered[index + 1] == end + 1:
            index += 1
            end = ordered[index]
        parts.append(b"\\x%02x" % start if start == end else b"\\x%02x-\\x%02x" % (start, end))
        index += 1
    return b"[" + b"".join(parts) + b"]"


def _translate(node: object, ignore_case: bool) -> bytes:
    if isinstance(node, Alternation):
        return b"|".join(b"".join(_translate(piece, ignore_case) for piece in branch)
                         for branch in node.branches)
    if isinstance(node, Char):
        if ignore_case and len(node.data) == 1 and _fold(node.data[0]) != node.data[0]:
            return _byte_class({node.data[0], _fold(node.data[0])})
        return b"(?:" + re.escape(node.data) + b")"
    if isinstance(node, AnyByte):
        return b"[\\x00-\\xff]"
    if isinstance(node, ByteSet):
        members = set(node.members)
        if ignore_case:
            members |= {_fold(b) for b in node.members}
        if node.negated:
            members = set(range(256)) - members
        return _byte_class(members)
    if isinstance(node, Anchor):
        return b"\\A" if node.at_start else b"\\Z"
    if isinstance(node, Group):
        return b"(?:" + _translate(node.body, ignore_case) + b")"
    if isinstance(node, Repeat):
        bounds = (b"{%d,}" % node.minimum if node.maximum is None
                  else b"{%d,%d}" % (node.minimum, node.maximum))
        return b"(?:" + _translate(node.node, ignore_case) + b")" + bounds
    raise TypeError(node)


_NON_WORD = _byte_class(set(range(256)) - WORD_BYTES)


class LineMatcher:
    """Decides whether a line (bytes without its LF) matches any of the patterns."""

    def __init__(self, trees: list[Alternation], *, ignore_case: bool, line_regexp: bool,
                 word_regexp: bool):
        self.full = line_regexp
        compiled = []
        for tree in trees:
            body = b"(?:" + _translate(tree, ignore_case) + b")"
            if word_regexp and not line_regexp:
                body = b"(?:\\A|" + _NON_WORD + b")" + body + b"(?:" + _NON_WORD + b"|\\Z)"
            compiled.append(re.compile(body))
        self.regexes = compiled

    def matches(self, line: bytes) -> bool:
        if self.full:
            return any(regex.fullmatch(line) for regex in self.regexes)
        return any(regex.search(line) for regex in self.regexes)
