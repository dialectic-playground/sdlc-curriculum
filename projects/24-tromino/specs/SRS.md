# Software Requirements Specification (SRS) — dp-tromino

| Field | Value |
| :-- | :-- |
| Document ID | SRS-24 |
| Project | `24-tromino` — Divide-and-Conquer Tromino Deficiency Tiling |
| Product | `dp-tromino` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-24) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-tromino`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-tromino` reads rounds — a board size followed by the two coordinates of the board's missing
square — as integer tokens from standard input or from one file, until a size of 0 or the end
of the input. For each round it tiles the deficient board with L-shaped trominoes by a
specified divide-and-conquer rule and writes one line per tromino, in a specified order; on
request it also draws the tiled board. It can write prompts to standard error before each
read. It reports invalid answers with their line numbers and unreadable files with fixed
messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |
| Board size *n* | The side length of the board, in squares: one of 2, 4, 8, 16, 32, 64 |
| Square (*x*, *y*) | The square in column *x* and row *y* of the board, 0 ≤ *x*, *y* < *n*. Columns are numbered from left to right and rows **from bottom to top**: (0, 0) is the lower-left square and (*n*−1, *n*−1) the upper-right square |
| Lattice point (*x*, *y*) | The corner shared by squares (*x*−1, *y*−1), (*x*, *y*−1), (*x*−1, *y*), and (*x*, *y*); that is, the lower-left corner of square (*x*, *y*) |
| Block | Four squares forming a 2 × 2 square. The block whose lower-left square is (*a*, *b*) has the squares LL = (*a*, *b*), LR = (*a*+1, *b*), UL = (*a*, *b*+1), and UR = (*a*+1, *b*+1); its **center** is the lattice point (*a*+1, *b*+1) |
| Corner names | `UL` (upper left), `UR` (upper right), `LR` (lower right), `LL` (lower left). The **opposite** of a corner is the diagonally opposite one: `UL`↔`LR`, `UR`↔`LL` |
| Tromino | Three squares of a block: the block minus one square, the *omitted* square. The tromino's **orientation** is the name of the corner opposite the omitted square — the corner in which its two arms meet. A tromino is identified by its block's center and its orientation |
| Round | One board size followed by the two coordinates of the missing square (FR-02) |
| *T*(*n*) | The number of trominoes in a tiling of an *n* × *n* deficient board: (*n*² − 1) / 3, that is 1, 5, 21, 85, 341, 1365 for *n* = 2 … 64 |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`) (CONV-06) |

### 1.4 References
- URD-24: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §4.9 (informative; see §2.5)
- S. W. Golomb, "Checker boards and polyominoes", *American Mathematical Monthly* 61 (1954)
  (informative: the theorem the algorithm proves)

## 2. Overall description

### 2.1 Product perspective
`dp-tromino` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §4.9 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read rounds (board size, x, y) as integer tokens until a size of 0 or the end of the input.
2. Tile each deficient board by the divide-and-conquer rule of FR-04.
3. Write one line per tromino, in the order of FR-04, under a heading.
4. Optionally draw each tiled board, numbering the trominoes in list order.
5. Optionally write prompts to standard error before each read.
6. Report invalid answers and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The tiling MUST be the one defined by FR-04, listed in the order FR-04 defines. Any other
  correct tiling, or the same tiling in another order, is a conformance failure.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-08.
- The input may contain any bytes; only tokens that match the *integer* grammar can be answers.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §4.9 repeatedly asks for the size of a board (0 to quit) and the
coordinates of the missing square, then prints `Tiling` and a dashed line, followed by one line
per tromino giving two coordinates and an orientation code. It places one tromino at the
center of the board, covering one square of each quarter that does not contain the missing
square, and then tiles the quarters recursively in the order upper left, upper right, lower
right, lower left; on a 2 × 2 board it prints the board's center and the orientation that
leaves the missing corner uncovered (missing lower left → `UR`, missing upper left → `LR`,
missing lower right → `UL`, missing upper right → `LL`). `dp-tromino` keeps:

- the dialog: a size, 0 to quit, then two coordinates, repeated;
- the heading `Tiling` / `------` and the line format `<x> <y> <orientation>`;
- the algorithm, the printed position (the center of the tromino's 2 × 2 block, computed as
  the board's or quarter's lower-left corner plus half its side), the four orientation codes
  and their meaning, and the recursion order upper left, upper right, lower right, lower left,
  with each tromino printed before the quarters below it are tiled.

**The sample session in the section's description cannot be reproduced, because it is not a
valid tiling.** For size 4 and missing square `1 2` it lists `2 2 LR`, `2 3 LL`, `1 3 UR`,
`2 1 UL`, `1 1 UR`. Under any reading of the coordinates and codes, the four trominoes after
the central one must lie in four different quarters, so their block centers must differ by 2
in at least one coordinate, but `2 3` and `1 3` differ by 1 (their blocks would overlap); and
the central tromino's code `LR` places the missing square in the upper-left quarter, so the
other three quarters must contribute the orientations `UR`, `LR`, and `LL`, but the sample has
no `LR` and two `UR`s. A brute-force check of every axis assignment, axis direction, and
meaning of the printed point confirms that no interpretation makes the five listed trominoes
disjoint. This SRS therefore specifies the rule that the description itself states (center
formula, base-case table, quarter order), which reproduces the sample's first line, `2 2 LR`,
exactly; for that round it yields `2 2 LR`, `1 3 UL`, `3 3 UR`, `3 1 LR`, `1 1 LL`
(FR-04, FR-05).

It changes the following, for the reasons given:

- **A defined coordinate system.** The description says only that coordinates run from 0 to
  *n*−1. FR-04 fixes x as the column (left to right), y as the row (bottom to top), and the
  printed point as the lattice point at the center of the tromino's block, so the list, the
  drawing (FR-06), and the user's mental picture agree.
- **The base case is not special.** The 2 × 2 table of the textbook is exactly what the
  general step produces for a 2 × 2 board, so FR-04 states one rule; this removes a common
  source of disagreement between implementations.
- **A size limit.** The textbook accepts any size its integers can hold and does not check that
  it is a power of 2. Sizes are restricted to 2 … 64 (FR-03): 64 already gives 1365 lines, and
  the limit keeps every round fast and every drawing printable.
- **Invalid answers are diagnosed.** A size that is not an allowed power of 2, a coordinate
  outside the board, or a token that is not an integer is reported with its line number, and
  the tool stops with exit status 1 (FR-09). The textbook would recurse forever, print
  nonsense, or loop on such input.
- **The end of the input ends the session** normally (exit status 0), like a size of 0.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **Prompts are optional and go to standard error.** The textbook's two prompts are written
  only with `-p`, `--prompt` (FR-07), so standard output holds only the tilings. The blank line
  that the textbook printed before `Tiling`, which only separated the report from the echoed
  keyboard input, is dropped.
- **An optional drawing.** `-d`, `--draw` adds a numbered drawing of each tiled board (FR-06).
  Without it, the output is the textbook's report.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (every answer uses
the *integer* grammar; the size is further restricted to 0, 2, 4, 8, 16, 32, 64 and each
coordinate to 0 … *n*−1), CONV-34 (data diagnostics, with the standard messages
`invalid integer`, `value out of range`, and `unexpected end of input`, one further message,
`invalid board size`, and the default consequences), CONV-36 (`-p`, `--prompt`, with two
prompts), and CONV-37 (the input is *text data*). CONV-35 does not apply, because no real
number is written, and CONV-38 does not apply, because nothing is random. Option syntax follows
CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of
CONV-18. Standard input is read as permitted by CONV-26. `dp-tromino` copies no input bytes to
its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-tromino [-d | --draw] [-p | --prompt] [FILE]
dp-tromino --help
dp-tromino --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-d` | `--draw` | none | off | After the list of each round, write a numbered drawing of the tiled board (FR-06) |
| `-p` | `--prompt` | none | off | Write the prompts of FR-07 to standard error before each read |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling such as `-dp`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. Giving a flag more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
One report per completed round (FR-05, and FR-06 with `--draw`), in input order. Nothing else.
On a usage error, or when `--help` / `--version` is handled, the output is as specified by
FR-11 … FR-14 instead.

### 3.6 Standard error
Prompts (FR-07, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The session ended with a size of 0 or at the end of the input (including an empty input), or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-10), it contained an invalid answer or ended inside a round (FR-09), or standard output could not be written |
| 2 | Usage error (FR-13) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are the public fixture files in
`tests/fixtures/`: `readme.txt` is `4\n1 2\n0\n`; `boards.txt` is `2\n0 0\n8\n5 6\n0\n`;
`corners.txt` is `2 0 0\n2 1 0\n2 0 1\n2 1 1\n`; `bad-size.txt` is `4\n1 2\n6\n0 0\n`;
`bad-square.txt` is `8\n3 8\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
*AC:* `dp-tromino < readme.txt`, `dp-tromino readme.txt`, and `dp-tromino - < readme.txt`
write the same report. *(UR-07)*

**FR-02: Tokens and the session.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
consumed in order by this session:

1. Write prompt P1 (FR-07). Read the next token. If the input has ended, the session ends and
   the tool exits with status 0.
2. Validate the token as the board size *n* (FR-03). If *n* = 0, the session ends and the tool
   exits with status 0 **without reading any further input**: tokens after the 0, valid or not,
   are never examined.
3. Write prompt P2. Read the next token and validate it as *x*; then read the next token and
   validate it as *y* (FR-03). If the input ends before either token, that is the error
   `unexpected end of input` (FR-09).
4. Write the report of the round (FR-05, FR-06), and continue at step 1.

Line structure has no meaning: the three answers of a round may share a line or be spread over
several, and answers may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF
input reads exactly like LF input.
*AC:* `dp-tromino corners.txt` writes four reports and exits 0 at the end of the input, which
has no closing 0; an input `0 junk\n` writes nothing and exits 0. *(UR-02, UR-10)*

**FR-03: Validating answers.**
Each answer MUST be a valid *integer* (CONV-33). A sign and leading zeros are allowed (`+04`
is 4; `-0` is 0). The board size MUST be 0 or one of 2, 4, 8, 16, 32, 64. Each coordinate MUST
satisfy 0 ≤ *x* ≤ *n* − 1 and 0 ≤ *y* ≤ *n* − 1 for the size *n* of its round. The coordinate
*x* is validated before *y* is read. Violations are handled by FR-09.
*AC:* sizes `1`, `3`, `-2`, and `128` are rejected with `invalid board size`; with size 4, the
coordinates `-1` and `4` are rejected with `value out of range` and `1.5` with
`invalid integer`; `+04\r\n001 -0\r\n` followed by two `0x1A` bytes is the round *n* = 4,
*x* = 1, *y* = 0, after which the input ends. *(UR-08)*

**FR-04: Tiling rule and order.**
The tiling of a round with board size *n* and missing square (*x*, *y*) MUST be the sequence of
trominoes produced by TILE(0, 0, *n*, *x*, *y*), where TILE(*a*, *b*, *s*, *h*ₓ, *h*ᵧ) tiles
the sub-board of side *s* whose lower-left square is (*a*, *b*) and which contains exactly one
square, the *hole* (*h*ₓ, *h*ᵧ), that must not be covered (the missing square, or a square
already covered by an earlier tromino):

1. If *s* = 1, produce nothing.
2. Let *m* = *s* / 2, *c*ₓ = *a* + *m*, and *c*ᵧ = *b* + *m*. The sub-board has four quarters
   of side *m*, with lower-left squares UL = (*a*, *c*ᵧ), UR = (*c*ₓ, *c*ᵧ), LR = (*c*ₓ, *b*),
   and LL = (*a*, *b*). The hole lies in quarter *Q*, whose name has `L` (left) as its second
   letter if *h*ₓ < *c*ₓ and `R` otherwise, and `L` (lower) as its first letter if *h*ᵧ < *c*ᵧ
   and `U` otherwise.
3. Produce the **central tromino**: center (*c*ₓ, *c*ᵧ), orientation the opposite of *Q*. It
   covers the three squares of the central block — UL (*c*ₓ−1, *c*ᵧ), UR (*c*ₓ, *c*ᵧ),
   LR (*c*ₓ, *c*ᵧ−1), LL (*c*ₓ−1, *c*ᵧ−1) — other than the one in quarter *Q*.
4. For each quarter in the order **UL, UR, LR, LL**, produce TILE(lower-left square of the
   quarter, *m*, hole′), where hole′ is (*h*ₓ, *h*ᵧ) for quarter *Q* and, for each other
   quarter, that quarter's square of the central block listed in step 3.

The output order is therefore a pre-order walk: each tromino comes before every tromino of the
four quarters below it, and the quarters are visited in the order UL, UR, LR, LL. For *s* = 2
the rule places the block's single tromino, which yields the table: missing LL → `UR`, missing
UL → `LR`, missing LR → `UL`, missing UR → `LL`, printed at the block's center. The tiling has
exactly *T*(*n*) trominoes; they cover every square of the board except (*x*, *y*), and no
square twice.
*AC:* size 2 with missing square (0, 0), (1, 0), (0, 1), (1, 1) → `1 1 UR`, `1 1 UL`,
`1 1 LR`, `1 1 LL` respectively (`corners.txt`); size 4 with (1, 2) → `2 2 LR`, `1 3 UL`,
`3 3 UR`, `3 1 LR`, `1 1 LL`; size 8 with (5, 6) → 21 trominoes, the first `4 4 LL`, the
second `2 6 UL`, the last `1 1 LL`; size 64 with (63, 63) → 1365 trominoes, the first
`32 32 LL`. *(UR-01, UR-03, UR-04)*

**FR-05: Report format.**
The report of a round MUST be the line `Tiling`, the line `------` (six hyphen-minus
characters), and then one line per tromino in the order of FR-04:

```text
<cx> <cy> <orientation>
```

where `<cx>` and `<cy>` are the decimals of the tromino's center and `<orientation>` is one of
`UL`, `UR`, `LR`, `LL`, separated by single spaces. Every line ends with a single LF and has no
leading or trailing spaces. Reports of consecutive rounds follow one another with no blank
line. With `--draw`, the drawing of FR-06 follows the last tromino line of each report.
*AC:* `dp-tromino < readme.txt` → stdout
`Tiling\n------\n2 2 LR\n1 3 UL\n3 3 UR\n3 1 LR\n1 1 LL\n`, stderr empty, exit 0.
*(UR-01, UR-03)*

**FR-06: Drawing.**
With `-d` or `--draw`, the report of each round MUST continue with the line `Board`, the line
`-----` (five hyphen-minus characters), and then *n* lines that draw the board, one line per
row from the top row (*y* = *n* − 1) down to the bottom row (*y* = 0). The line of row *y*
consists of *n* fields for *x* = 0, 1, …, *n* − 1, separated by single spaces. Each field is
exactly *w* characters wide, where *w* is the number of decimal digits of *T*(*n*), and holds,
right-aligned and padded on the left with spaces:

- `X` for the missing square (*x*, *y*), or
- the decimal of *k* for a square covered by the *k*-th tromino of the list (1 ≤ *k* ≤ *T*(*n*),
  numbered from 1 in the order of FR-04).

There are no other characters: no trailing spaces, no frame, no blank lines.
*AC:* `dp-tromino --draw readme.txt` → stdout as in FR-05 followed by
`Board\n-----\n2 2 3 3\n2 X 1 3\n5 1 1 4\n5 5 4 4\n`, exit 0; for size 2 with missing square
(0, 0) the drawing is `1 1\nX 1\n`; for size 8 (*w* = 2) each field is two characters wide, as
in ` X` and `21`. *(UR-05)*

**FR-07: Prompts.**
`-p`, `--prompt` enables two prompts, neither of which ends with an LF:

| Prompt | Exact bytes | Written |
| :-- | :-- | :-- |
| P1 | `Enter size of board (0 to quit): ` (33 bytes, ending with one space) | Before each attempt to read a board size (FR-02 step 1) |
| P2 | `Enter coordinates of missing square: ` (37 bytes, ending with one space) | Once per round, after a valid nonzero size and before *x* is read (FR-02 step 3); not again before *y* |

With prompts enabled, the tool MUST write each prompt to standard error, and flush standard
error, immediately before the read it belongs to. P1 is therefore also written before the
attempt that reaches the end of the input, or reads the size 0 (CONV-36). A prompt already
written stays written, so a diagnostic of FR-09 follows the last prompt on the same line of
standard error. Prompts never change standard output. No prompt is written if the input cannot
be opened.
*AC:* `dp-tromino --prompt readme.txt` → stdout as in FR-05, stderr exactly
`Enter size of board (0 to quit): Enter coordinates of missing square: Enter size of board (0 to quit): `,
exit 0. `dp-tromino -p` with empty standard input → stderr
`Enter size of board (0 to quit): `, stdout empty, exit 0. *(UR-06)*

**FR-08: Streaming.**
Rounds MUST be processed one at a time, in input order. As soon as the token *y* of a round is
complete (section 1.3) and valid, the tool MUST write the round's whole report to standard
output and flush standard output, before it waits for any further input bytes. It MUST NOT
wait for the end of the input, or for the next round, before writing a report. Within a report,
the tool SHOULD buffer its output rather than flush each line (NFR-02).
*AC:* at a terminal, typing `4`, Enter, `1 2`, Enter shows the whole report before anything
else is typed (manual check). *(UR-02, UC-5)*

**FR-09: Invalid answers.**
If an answer is not a valid *integer* (CONV-33), including an integer outside
−2⁶³ … 2⁶³−1, the tool MUST write `dp-tromino: <source>:<line>: invalid integer '<token>'`. If
a board size is a valid *integer* other than 0, 2, 4, 8, 16, 32, 64, it MUST write
`dp-tromino: <source>:<line>: invalid board size '<token>'`. If a coordinate is a valid
*integer* outside 0 … *n* − 1, it MUST write
`dp-tromino: <source>:<line>: value out of range '<token>'`. If the input ends after a nonzero
size and before both coordinates have been read, it MUST write
`dp-tromino: <source>:<line>: unexpected end of input`. `<source>` is as defined in section 1.3,
`<line>` is the token's line number or, at the end of the input, the end-of-input line number
(CONV-32), and `<token>` is the token's exact bytes (CONV-34). The tool then stops: it reads no
further input, writes no further report, and exits with status 1. Reports already written for
earlier rounds are kept (CONV-34); nothing of the failing round has been written.
*AC:* `dp-tromino bad-size.txt` → stdout the report for size 4 and square (1, 2), stderr
`dp-tromino: bad-size.txt:3: invalid board size '6'\n`, exit 1; `dp-tromino bad-square.txt`
→ stdout empty, stderr `dp-tromino: bad-square.txt:2: value out of range '8'\n`, exit 1; an
input `8\n3\n` gives `unexpected end of input` on line 3; a size token `four` gives
`invalid integer 'four'`; a lone `0x1A` byte followed by an LF, where a size is expected,
gives `invalid integer` because that Ctrl-Z byte does not end the input. *(UR-08)*

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-tromino: <source>: <reason>` with `<reason>` from the CONV-16 table,
and exit with status 1. Reports already written are kept. When standard input fails,
`<source>` is `-`.
*AC:* `dp-tromino missing.txt` → stderr `dp-tromino: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-tromino subdir` where `subdir` is a directory →
`dp-tromino: subdir: Is a directory`. *(UR-09)*

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-tromino --help` matches the user manual exactly; `dp-tromino a b --help` also prints
it. *(UR-11)*

**FR-12: Version.**
`--version` MUST write `dp-tromino (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-11)*

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--draw=…`, `--prompt=…`,
`--help=…`, `--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14
line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--dra` is
unrecognized. A second operand MUST be reported as `dp-tromino: extra operand '<second operand>'`,
after the whole argument list has been scanned (CONV-12).
*AC:* `dp-tromino readme.txt boards.txt` → `dp-tromino: extra operand 'boards.txt'`;
`dp-tromino -x --help` → `dp-tromino: invalid option -- 'x'`; `dp-tromino --draw=yes` →
`dp-tromino: option '--draw' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-12, UR-13)*

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: bulk output and interactive flushing | A round of size 64 writes 1367 lines (66 more with `--draw`), and a session may hold many rounds. Standard output MUST be written in binary mode (CONV-03) through a buffer, and flushed once per report (FR-08) rather than once per line, so that output speed does not depend on whether standard output is a Windows console, a POSIX terminal, a pipe, or a file. Standard error MUST be flushed after each prompt (FR-07). The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. | CI black-box tests on 3 OSes; measurement; code review; manual console check |
| NFR-03 | Performance | An input of 100 rounds of size 64, run with `--draw` (about 3.2 MB of output), MUST be processed in under 0.5 s for a natively compiled build (under 5 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of rounds. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and sizes such as 2⁶² that a careless power-of-2 test or recursion would mishandle. The recursion depth never exceeds log₂ 64 + 1 = 7 levels. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the incremental tokenizer, answer validation, the tiling procedure, the report and drawing formatters, and I/O MUST be separate units. The tiling MUST be one recursive procedure that implements FR-04 directly (one rule, no separate 2 × 2 table) and delivers the trominoes in order to its caller — for example by returning a sequence or calling a supplied function — without writing output itself. | Design review |
| NFR-06 | Testability | The tiling procedure and the formatters MUST be pure and covered by unit tests, including every acceptance value of FR-04 and an exhaustive check, for every size 2 … 64 and every missing square, that the trominoes number *T*(*n*), lie inside the board, avoid the missing square, and never overlap. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-tromino --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-tromino: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-tromino: unrecognized option 'T'` |
| `--draw=…`, `--prompt=…`, `--help=…`, `--version=…` | `dp-tromino: option '--draw' doesn't allow an argument` (or `'--prompt'`, `'--help'`, `'--version'`) |
| A second operand `X` | `dp-tromino: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-tromino: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-tromino: F: Permission denied` |
| FILE `F` is a directory | `dp-tromino: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-tromino: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-tromino: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *integer* | `dp-tromino: S:L: invalid integer 'K'` |
| Board size `K` on line `L` is a valid *integer* other than 0, 2, 4, 8, 16, 32, 64 | `dp-tromino: S:L: invalid board size 'K'` |
| Coordinate `K` on line `L` is a valid *integer* outside 0 … *n* − 1 | `dp-tromino: S:L: value out of range 'K'` |
| The input ends after a nonzero size, before both coordinates (end-of-input line `L`) | `dp-tromino: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe) | `dp-tromino: write error` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-07).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-07, FR-09, FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03 … 05 and 07 … 09 have several steps) | FR-01 … FR-14 |
| Unit test (written by the implementer) | FR-02 … FR-06, NFR-06 |
| Measurement | NFR-02, NFR-03 |
| Inspection / review | FR-08 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-tromino < readme.txt` | FR-01, FR-02, FR-04, FR-05 |
| 02 | `dp-tromino --prompt readme.txt` | FR-01, FR-07 |
| 03 | `dp-tromino boards.txt` | FR-02 (several rounds), FR-04 (recursion order on 8 × 8), FR-05 |
| 04 | `dp-tromino corners.txt` | FR-02 (end of input ends the session), FR-04 (every 2 × 2 case) |
| 05 | `dp-tromino --draw readme.txt` | FR-06 |
| 06 | `dp-tromino -d - < boards.txt` | FR-01, FR-06 (field width 1 and 2) |
| 07 | `dp-tromino bad-size.txt` | FR-03, FR-09 (reports kept, CONV-34) |
| 08 | `dp-tromino bad-square.txt` | FR-03, FR-09 |
| 09 | `dp-tromino --help` | FR-11 |
| 10 | `dp-tromino readme.txt boards.txt` | FR-13, FR-14 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-03, FR-04, FR-05 |
| UR-02 | FR-02, FR-08 |
| UR-03 | FR-04, FR-05 |
| UR-04 | FR-04, NFR-05 |
| UR-05 | FR-06 |
| UR-06 | FR-07, CONV-36 |
| UR-07 | FR-01, CONV-26 |
| UR-08 | FR-03, FR-09, CONV-33, CONV-34 |
| UR-09 | FR-10, CONV-16 |
| UR-10 | FR-02, NFR-02, CONV-37 |
| UR-11 | FR-11, FR-12 |
| UR-12 | FR-13, FR-14 |
| UR-13 | NFR-01, NFR-02, FR-13, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
