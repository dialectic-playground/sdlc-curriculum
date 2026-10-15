<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-koch](#software-requirements-specification-srs--dp-koch)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
    - [2.5 Relationship to the textbook program (informative)](#25-relationship-to-the-textbook-program-informative)
    - [2.6 Relationship to CLI-CONV](#26-relationship-to-cli-conv)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-koch

| Field                     | Value                                                      |
| :------------------------ | :--------------------------------------------------------- |
| Document ID               | SRS-51                                                     |
| Project                   | `51-koch` — Recursive Fractal Geometry: The Koch Snowflake |
| Product                   | `dp-koch` (canonical name)                                 |
| Version                   | 1.0.0                                                      |
| Status                    | Approved (pre-written by the curriculum)                   |
| Parent document           | `URD.md` (URD-51)                                          |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)               |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                       |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-koch`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-koch` computes the von Koch curve of a given recursion level (0 to 6), or the closed
snowflake made of three such curves, and writes it as a list of vertex coordinates or as an
SVG document. The level is either given with `--level`, or read in a dialog from standard
input or a file: a level, then after each figure an answer saying whether to draw another. The
coordinates are computed by a fully specified sequence of binary64 floating-point operations,
so every implementation prints the same digits. The tool can write the dialog's prompts to
standard error, and reports invalid dialog input with its line number.

### 1.3 Definitions

| Term                                         | Definition                                                                                                                                          |
| :------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                                           | The line-feed byte, `0x0A`                                                                                                                          |
| Input                                        | The byte sequence read from standard input or from the FILE operand                                                                                 |
| Source                                       | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number, end-of-input line number | As defined in CONV-32                                                                                                                               |
| Level                                        | An integer _k_ with 0 ≤ _k_ ≤ 6, the recursion depth of a curve                                                                                     |
| LENGTH                                       | The length _L_ of the base segment of a curve: an integer 1 … 1000000, default 729                                                                  |
| Direction code                               | An integer _d_ in 0 … 5 denoting the direction _d_ × 60° counter-clockwise from the +x axis                                                         |
| Curve                                        | The Koch curve of level _k_ over one base segment: 4^_k_ segments (FR-03)                                                                           |
| Snowflake                                    | Three curves of the same level drawn one after another around an equilateral triangle: 3 × 4^_k_ segments (FR-03)                                   |
| Figure                                       | One curve or one snowflake, as selected by `--snowflake`                                                                                            |
| Vertex                                       | A point (_x_, _y_) where a segment starts or ends; a figure of _n_ segments has _n_ + 1 vertices, listed in drawing order                           |
| Answer                                       | The token read after each figure in the dialog: `y` or `Y` (yes), `n` or `N` (no)                                                                   |
| binary64                                     | The IEEE 754 double-precision format; every operation is correctly rounded to nearest, ties to even                                                 |
| `FIX(x, n)`                                  | The number formatting rule of CONV-35 (no negative zero)                                                                                            |

### 1.4 References

- URD-51: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §11.4 (informative; see §2.5)
- W3C, _Scalable Vector Graphics (SVG) 1.1_ (informative; the format of FR-06 is a valid SVG
  document)

## 2. Overall description

### 2.1 Product perspective

`dp-koch` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §11.4 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_, which drew the von Koch snowflake
with graphics primitives. `dp-koch` replaces the screen with a fully specified text format and
an optional SVG document, so the drawing can be tested byte for byte.

### 2.2 Product functions

1. Compute the vertices of a Koch curve or snowflake of level 0 … 6 by multi-branch recursion.
2. Write each figure as a list of coordinates or as an SVG document.
3. Run the textbook's dialog: read a level, draw, ask whether to draw another.
4. Draw a single figure from the command line without reading input.
5. Optionally write the dialog's prompts to standard error.
6. Report invalid dialog input and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Coordinates MUST be computed in binary64 arithmetic exactly as FR-04 prescribes. No other
  precision (single, extended, or decimal) and no other order of operations may be used.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-07.
- The platform provides IEEE 754 binary64 arithmetic with correctly rounded addition,
  subtraction, multiplication, division, and square root, as every supported platform does.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §11.4 asks for a level, draws the von Koch snowflake on the screen with
relative line-drawing primitives, then asks `Do another (y = yes, n = no)?It tracks the
drawing direction as one of six 60° codes and, at level 0, moves by a displacement taken from
a table that uses the factor √3/2. `dp-koch` keeps:

- the levels 0 … 6, the six direction codes and their displacements, the recursion (each
  segment becomes four segments of one third the length, turned by 0°, +60°, −120°, and +60°),
  and therefore the 4^_k_ segments of a curve of level _k_;
- the closed snowflake of three curves, and the dialog: a level, a figure, then the question
  `Do another (y = yes, n = no)?repeated while the answer is yes.

It changes the following, for the reasons given:

- **Text instead of graphics.** The textbook's output existed only on a DOS graphics screen.
  `dp-koch` writes the vertices as text (FR-05) or as an SVG document (FR-06), both specified
  to the byte, so the result can be compared, plotted, or viewed in any browser.
- **Reproducible arithmetic.** The textbook accumulated screen coordinates in whatever
  precision its compiler chose. FR-04 fixes every floating-point operation and its order, and
  CONV-35 fixes the rounding of the printed digits, so all implementations agree to the last
  digit — including the sign of coordinates that should be zero but come out as tiny negative
  numbers (`FIX` never writes `-0.000000`).
- **Fixed geometry instead of screen fitting.** The textbook positioned and scaled the drawing
  for its screen. Here the figure always starts at (0, 0) in the +x direction, the y axis
  points up, and the base length is an option (`--length`, default 729 = 3⁶, so that at level 6
  every segment has length 1 and the x coordinates are exact).
- **Curve or snowflake.** The textbook always drew the snowflake. A single curve is the natural
  unit of the recursion, so it is the default and `--snowflake` selects the closed figure.
- **A non-interactive mode.** `--level` draws one figure without any dialog, which suits
  scripts and SVG files.
- **Strict dialog input.** The textbook's keyboard reads had no answer for a mistyped level or
  answer. Here a level outside 0 … 6, a token that is not an integer, and an answer other than
  `y`, `Y`, `n`, `N` are reported with their line numbers (FR-09). The end of the input in
  place of an answer ends the dialog normally, like answering `n`; the end of the input in
  place of a level is an error, because the user asked for a figure and gave none.
- **Prompts are optional and go to standard error** (FR-08). The level prompt
  `Enter level (0-6):s written in the voice of the textbook's question; the question
  itself is kept byte for byte.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV and makes **no overrides**. Option syntax follows CONV-07 …
CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Standard input is read as
permitted by CONV-26, and only in dialog mode. Of the conventions for Projects 11–52:

| Convention | Use in this SRS                                                                                                                                                             |
| :--------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-32    | The dialog input is read as tokens; line numbers locate data errors (FR-02, FR-09).                                                                                         |
| CONV-33    | A level uses the _integer_ grammar, further restricted to 0 … 6 (FR-02).                                                                                                    |
| CONV-34    | Data errors use its format, the standard messages `invalid integer`, `value out of range`, and `unexpected end of input`, and the further message `invalid answer` (FR-09). |
| CONV-35    | Every coordinate is written as `FIX(x, 6)` (FR-05, FR-06).                                                                                                                  |
| CONV-36    | `-p`, `--prompt` writes the two dialog prompts (FR-08).                                                                                                                     |
| CONV-37    | Applies: the dialog input is _text data_ (FR-02).                                                                                                                           |
| CONV-38    | Not applicable: nothing is random.                                                                                                                                          |

`dp-koch` copies no input bytes to its output except the offending token in a diagnostic, so
CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-koch [-s] [-L LENGTH] [--svg] [-p] [FILE]
dp-koch -l LEVEL [-s] [-L LENGTH] [--svg]
dp-koch --help
dp-koch --version
```

### 3.2 Options

| Short | Long          | Argument          | Default | Description                                                          |
| :---- | :------------ | :---------------- | :------ | :------------------------------------------------------------------- |
| `-l`  | `--level`     | LEVEL (required)  | —       | Draw one figure of level LEVEL and read no input (FR-01)             |
| `-s`  | `--snowflake` | none              | off     | Draw the snowflake instead of a single curve (FR-03)                 |
| `-L`  | `--length`    | LENGTH (required) | `729`   | Length of the base segment (FR-04)                                   |
| —     | `--svg`       | none              | off     | Write each figure as an SVG document (FR-06) instead of text (FR-05) |
| `-p`  | `--prompt`    | none              | off     | Write the dialog prompts to standard error (FR-08)                   |
| —     | `--help`      | none              | —       | Print the help text and exit 0                                       |
| —     | `--version`   | none              | —       | Print the version line and exit 0                                    |

Option syntax (bundling, `-l3`, `--level=3`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. If `--level` or `--length` is repeated, the last occurrence wins; repeating a flag has
the same effect as giving it once (CONV-11). LEVEL MUST consist only of ASCII digits and have a
value in 0 … 6; LENGTH MUST consist only of ASCII digits and have a value in 1 … 1000000.
Leading zeros are allowed (`006` is 6). Any other value is an invalid option value (FR-13).
`-p` is accepted together with `--level` and then has no effect, because no input is read.

### 3.3 Operands

At most one FILE operand, and none when `--level` is given. The operand `-` denotes standard
input (CONV-10). Every token after `--` is an operand, even if it begins with `-`. The operand is
used and echoed exactly as given (CONV-19).

### 3.4 Standard input

Read in dialog mode when no operand is given or the operand is `-` (FR-01). Read as raw bytes;
no newline translation of any kind is performed on any platform. Never read with `--level`.

### 3.5 Standard output

The figures (FR-05 or FR-06), in the order they are drawn. Nothing else. On a usage error, or
when `--help` / `--version` is handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-08, only with `--prompt` in dialog mode) and diagnostics (section 6). Without
`--prompt`, nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                             |
| :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The figure was drawn (`--level`), or the dialog ended with a `n`/`N` answer or with the end of the input in place of an answer, or `--help` / `--version` was handled |
| 1      | The input could not be opened or read (FR-10), it contained invalid dialog input or ended in place of a level (FR-09), or standard output could not be written        |
| 2      | Usage error (FR-13)                                                                                                                                                   |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `two.txt` and `bad.txt` are the public fixture
files in `tests/fixtures/`: `two.txt` is `0\ny\n2\nn\n`; `bad.txt` is `1\ny\n7\n`.

**FR-01: Modes and input source.**
With `--level`, the tool MUST draw exactly one figure of that level (FR-03 … FR-06) and exit
with status 0; it reads no input and writes no prompt. Without `--level`, the tool runs the
dialog (FR-07): if no operand is given, or the operand is `-`, it reads standard input;
otherwise it opens the file named by the operand and reads it as raw bytes. The input is opened
before anything is written (in particular before the first prompt).
_AC:_ `dp-koch --level 1` → stdout as in FR-05, stderr empty, exit 0. `dp-koch < two.txt`,
`dp-koch two.txt`, and `dp-koch - < two.txt` write the same output. _(UR-01, UR-04, UR-05)_

**FR-02: Dialog tokens.**
The dialog input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to
the very end of the input is ignored. The remaining input is divided into tokens (CONV-32),
which are consumed in order, alternately as a level and as an answer, starting with a level.
Line structure has no meaning, so CRLF input reads exactly like LF input. A level token MUST be
a valid _integer_ (CONV-33) with a value in 0 … 6; a sign and leading zeros are allowed (`+3`,
`03`). An answer token MUST be exactly one of the single bytes `y`, `Y` (draw another), `n`,
`N` (stop). Tokens after a stopping answer are never examined. Invalid tokens are handled by
FR-09.
_AC:_ `dp-koch < two.txt` → the figure of level 0, then the figure of level 2, exit 0. An input
`1\r\nY\r\n0\r\nN\r\n2\r\n` followed by two `0x1A` bytes draws levels 1 and 0, exit 0. _(UR-04,
UR-09)_

**FR-03: Geometry.**
A curve of level _k_ with base direction _d_ is the sequence of 4^_k_ segment direction codes
`C(k, d)` defined by `C(0, d)` = (_d_) and, for _k_ ≥ 1, `C(k, d)` = `C(k−1, d)`,
`C(k−1, (d+1) mod 6)`, `C(k−1, (d+5) mod 6)`, `C(k−1, d)` concatenated in this order (turns of
0°, +60°, −120°, +60° relative to the previous piece). A single curve is `C(k, 0)`. The
snowflake is `C(k, 0)`, `C(k, 4)`, `C(k, 2)` concatenated in this order: the three sides of an
equilateral triangle traversed clockwise, below the first side, so that every bump points
outward. A curve has 4^_k_ segments; a snowflake has 3 × 4^_k_.
_AC:_ level 1 curve → direction codes 0, 1, 5, 0; level 6 curve → 4096 segments; level 1
snowflake → 12 segments; level 0 snowflake → the triangle with codes 0, 4, 2. _(UR-02)_

**FR-04: Coordinates.**
The coordinates MUST be computed in binary64 exactly as follows, every operation being a single
correctly rounded binary64 operation:

1. _h_ = sqrt(3) / 2, computed once: the square root of 3.0, then divided by 2.0.
2. _s_ = _L_ (LENGTH, converted exactly), then _k_ times _s_ ← _s_ / 3.0.
3. _a_ = _s_ / 2.0 and _b_ = _s_ × _h_.
4. The displacement (Δ*x*, Δ*y*) of direction code 0 … 5 is (_s_, 0), (_a_, _b_), (−*a*, _b_),
   (−*s*, 0), (−*a*, −*b*), (_a_, −*b*), where −*v* is exact negation and 0 is +0.0.
5. The first vertex is (_x_, _y_) = (0.0, 0.0). For each segment, in the order of FR-03,
   _x_ ← _x_ + Δ*x* and _y_ ← _y_ + Δ*y*, and the new (_x_, _y_) is the next vertex. The snowflake
   continues from the end of one side to the next without resetting.

An implementation MUST NOT use extended precision for intermediate results, fused
multiply-add, or any algebraic rearrangement (such as computing _L_ / 3^_k_ in one step, or
multiplying a segment count by a displacement). Because of rounding, a coordinate that is zero
in exact arithmetic may come out as a tiny positive or negative number, and the last vertex of
a snowflake may differ slightly from (0, 0); `FIX` (FR-05) hides both.
_AC:_ `dp-koch -l 1` gives the vertex `364.500000 210.444173`; `dp-koch -l 2 -L 5` gives the
vertex `3.333333 0.000000`, whose exact binary64 _y_ is −1.1102230246251565 × 10⁻¹⁶; the last
vertex of `dp-koch -s -l 3 -L 100` is `0.000000 0.000000`. _(UR-02, UR-03)_

**FR-05: Text format.**
Without `--svg`, a figure MUST be written as a heading line followed by one line per vertex, in
drawing order. The heading is `Koch curve, level <k>: <n> segments` for a curve and
`Koch snowflake, level <k>: <n> segments` for a snowflake, where `<k>` is the level and `<n>`
the number of segments in decimal; when _n_ = 1 (only the level-0 curve), the last word is
`segment`. A vertex line is `FIX(x, 6)`, one space, `FIX(y, 6)`. Every line ends with a single
LF; there are no other spaces, no blank lines, and nothing between consecutive figures.
_AC:_ `dp-koch --level 1` → stdout
`Koch curve, level 1: 4 segments\n0.000000 0.000000\n243.000000 0.000000\n364.500000 210.444173\n486.000000 0.000000\n729.000000 0.000000\n`;
`dp-koch -l0` → `Koch curve, level 0: 1 segment\n0.000000 0.000000\n729.000000 0.000000\n`.
_(UR-03)_

**FR-06: SVG format.**
With `--svg`, a figure MUST be written as the following lines, each ending with a single LF:

1. `<svg xmlns="http://www.w3.org/2000/svg" viewBox="X0 Y0 W H">`
2. `<title>HEADING</title>`, where HEADING is the heading line of FR-05
3. `<polyline fill="none" stroke="black" stroke-width="1" vector-effect="non-scaling-stroke" points="`
4. one line per vertex, in drawing order: `FIX(x, 6)`, a comma, `FIX(−y, 6)`
5. `"/>`
6. `</svg>`

SVG's y axis points down, so the vertex's _y_ is negated (exactly) before formatting. X0, Y0,
W, and H are integers written in decimal (with a `-` when negative), computed from the exact
binary64 vertex coordinates of the figure: X0 = ⌊min _x_⌋ − 1, Y0 = ⌊min(−*y*)⌋ − 1,
W = ⌈max _x_⌉ + 1 − X0, H = ⌈max(−*y*)⌉ + 1 − Y0, the minima and maxima taken over all vertices.
Each figure drawn is one complete document; when the dialog draws several figures, the
documents follow one another.
_AC:_ `dp-koch --svg -l 2` → first line
`<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -212 731 213">`, 17 vertex lines from
`0.000000,0.000000` to `729.000000,0.000000`, last line `</svg>`; `dp-koch --svg -s -l 2 -L 1` →
`viewBox="-2 -2 4 4"`, because the smallest _x_ is −2.7755575615628914 × 10⁻¹⁶. _(UR-06)_

**FR-07: Dialog and streaming.**
The dialog MUST proceed as follows: (1) read a level; if the input ends instead, report
`unexpected end of input` (FR-09); (2) draw the figure of that level, write it completely to
standard output, and flush standard output; (3) read an answer; if the input ends instead, or
the answer is `n` or `N`, exit with status 0; if it is `y` or `Y`, go to (1). The tool MUST NOT
wait for more input than it needs to complete the current token before drawing, apart from
ordinary buffering of bytes that are already available. LENGTH, `--snowflake`, and `--svg` apply
to every figure of the dialog.
_AC:_ `dp-koch < two.txt` → two figures, exit 0; `dp-koch` with empty standard input → stdout
empty, stderr `dp-koch: -:1: unexpected end of input\n`, exit 1; an input `1\n` → one figure,
exit 0; an input `1\nY\n` → one figure, then `dp-koch: <source>:3: unexpected end of input`,
exit 1. At a terminal, typing `2` and Enter shows the figure before the question is answered
(manual check). _(UR-04, UR-05)_

**FR-08: Prompts.**
`-p`, `--prompt` enables two prompts in dialog mode: the level prompt, the 19 bytes
`Enter level (0-6):and the answer prompt, the 30 bytes `Do another (y = yes, n = no)?`(each ending with one space, no LF). With prompts enabled, the tool MUST write the level prompt
to standard error, and flush it, immediately before each attempt to read a level, and the
answer prompt immediately before each attempt to read an answer — also when that attempt
reaches the end of the input (CONV-36). Prompts never change standard output. No prompt is
written if the input cannot be opened, and none with`--level`.
_AC:_ `dp-koch --prompt two.txt`→ stdout as without`--prompt`, stderr
`Enter level (0-6): Do another (y = yes, n = no)? Enter level (0-6): Do another (y = yes, n = no)?
exit 0. _(UR-07)_

**FR-09: Invalid dialog input.**
The tool MUST report, as a CONV-34 diagnostic `dp-koch: <source>:<line>: <message>`:

- a level token that is not a valid _integer_: `invalid integer '<token>'`;
- a level token that is a valid _integer_ outside 0 … 6: `value out of range '<token>'`;
- an answer token other than `y`, `Y`, `n`, `N`: `invalid answer '<token>'`;
- the end of the input where a level is required: `unexpected end of input`, with the
  end-of-input line number.

`<line>` is the token's line number (CONV-32) and `<token>` its exact bytes. The tool then
stops reading and exits with status 1. Figures already written are kept (CONV-34). With
`--prompt`, the diagnostic follows the last prompt on the same line of standard error.
_AC:_ `dp-koch bad.txt` → stdout the figure of level 1, stderr
`dp-koch: bad.txt:3: value out of range '7'\n`, exit 1. With an input `0\nyes\n` and `-p`,
stderr ends with `Do another (y = yes, n = no)? dp-koch: <source>:2: invalid answer 'yes'\n`. A
token `0` followed by a `0x1A` byte and an LF gives `invalid integer`, because that Ctrl-Z byte
does not end the input. _(UR-08)_

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-koch: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Figures already written are kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-koch missing.txt` → stderr `dp-koch: missing.txt: No such file or directory\n`, stdout
empty, exit 1; `dp-koch subdir` where `subdir` is a directory → `dp-koch: subdir: Is a
directory`. _(UR-10)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-koch --help` matches the user manual exactly; `dp-koch extra --help` also prints it.
_(UR-11)_

**FR-12: Version.**
`--version` MUST write `dp-koch (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-11)_

**FR-13: Usage errors.**
Unknown options, a missing argument of `-l`/`--level`/`-L`/`--length`, and arguments supplied to
options that take none (`--snowflake=…`, `--svg=…`, `--prompt=…`, `--help=…`, `--version=…`)
MUST be reported with the CONV-13 messages followed by the CONV-14 line, with exit status 2.
Long options MUST NOT be abbreviated (CONV-08). After the whole argument list has been scanned
(CONV-12), the tool checks, in this order, and reports the first failure: an invalid LEVEL
(`dp-koch: invalid argument '<LEVEL>' for '<option>'`), an invalid LENGTH (the same message for
the LENGTH option), an operand together with `--level`
(`dp-koch: extra operand '<first operand>'`), and a second operand
(`dp-koch: extra operand '<second operand>'`). `<option>` is the option as written for the
winning occurrence (`-l`, `--level`, `-L`, or `--length`).
_AC:_ `dp-koch --level 9` → `dp-koch: invalid argument '9' for '--level'`; `dp-koch -L 1000001 -l 7`
→ `dp-koch: invalid argument '7' for '-l'`; `dp-koch --length 0` →
`dp-koch: invalid argument '0' for '--length'`; `dp-koch -l 2 two.txt` →
`dp-koch: extra operand 'two.txt'`; `dp-koch -x --help` → `dp-koch: invalid option -- 'x'`;
`dp-koch --svg=1` → `dp-koch: option '--svg' doesn't allow an argument`; each followed by the
CONV-14 line, exit 2. _(UR-12, UR-14)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                          | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Verification                                                               |
| :----- | :------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------------------------------------------------------------------------- |
| NFR-01 | Portability                                       | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                             | CI black-box tests on 3 OSes                                               |
| NFR-02 | Cross-platform focus: reproducible floating point | Every coordinate MUST be the result of the binary64 operations of FR-04, in that order, on every platform and compiler: no x87 80-bit intermediates, no fused multiply-add contraction, no "fast math" reassociation, no single precision, and a correctly rounded square root. Printing MUST follow CONV-35 exactly (round from the exact binary value, ties to even, no negative zero), never a platform `printf` whose rounding or `-0` handling differs. The dialog input MUST be read in binary mode, so CR and `0x1A` bytes reach the tokenizer and only FR-02 interprets them. | CI black-box tests on 3 OSes; code review of compiler flags and formatting |
| NFR-03 | Performance                                       | The largest figure (`dp-koch -s -l 6 -L 1000000`, 12 289 vertices, about 340 KiB of output) MUST be produced in under 200 ms for a natively compiled build (under 2 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). A dialog of 1000 figures of level 3 MUST take under 2 s native (20 s interpreted).                                                                                                                                                                       | Measurement                                                                |
| NFR-04 | Robustness                                        | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. The recursion depth is bounded by the level limit of 6. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                            | Unit + black-box tests                                                     |
| NFR-05 | Maintainability                                   | Option parsing, the incremental tokenizer, the dialog, the recursive generation of direction codes, coordinate accumulation, and the two output formats MUST be separate units (Principles 13, 18). The curve MUST be generated by one recursive function that follows FR-03's definition, calling itself four times per level; the displacement table MUST appear in exactly one place.                                                                                                                                                                                              | Design review                                                              |
| NFR-06 | Testability                                       | Direction-code generation and coordinate computation (level, length, curve/snowflake → vertices) and both formatters MUST be pure functions covered by unit tests, including the segment counts 4^_k_ and 3 × 4^_k_ for every level, the acceptance values of FR-04, and a check that the snowflake closes within 10⁻⁶.                                                                                                                                                                                                                                                               | Code review                                                                |
| NFR-07 | Build                                             | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | CI                                                                         |
| NFR-08 | Security                                          | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                         | Inspection                                                                 |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-koch --help' for more information.`

| Trigger                                                             | Exact first line                                                             |
| :------------------------------------------------------------------ | :--------------------------------------------------------------------------- |
| Unknown short option `x`                                            | `dp-koch: invalid option -- 'x'`                                             |
| Unknown or abbreviated long option token `T`                        | `dp-koch: unrecognized option 'T'`                                           |
| `-l` / `-L` without an argument                                     | `dp-koch: option requires an argument -- 'l'` (or `'L'`)                     |
| `--level` / `--length` without an argument                          | `dp-koch: option '--level' requires an argument` (or `'--length'`)           |
| `--snowflake=…`, `--svg=…`, `--prompt=…`, `--help=…`, `--version=…` | `dp-koch: option '--svg' doesn't allow an argument` (with the option's name) |
| Invalid LEVEL `V`                                                   | `dp-koch: invalid argument 'V' for '-l'` (or `'--level'`)                    |
| Invalid LENGTH `V`                                                  | `dp-koch: invalid argument 'V' for '-L'` (or `'--length'`)                   |
| An operand `X` together with `--level`                              | `dp-koch: extra operand 'X'`                                                 |
| A second operand `X`                                                | `dp-koch: extra operand 'X'`                                                 |

Runtime errors (exit status 1; the tool stops at the first one; figures already written are
kept):

| Trigger                                                                        | Exact message                           |
| :----------------------------------------------------------------------------- | :-------------------------------------- |
| FILE `F` does not exist                                                        | `dp-koch: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                     | `dp-koch: F: Permission denied`         |
| FILE `F` is a directory                                                        | `dp-koch: F: Is a directory`            |
| A component of FILE `F` is not a directory                                     | `dp-koch: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                     | `dp-koch: F: Input/output error`        |
| Any of the above for standard input                                            | the same message with `F` = `-`         |
| Level token `K` on line `L` of source `S` is not a valid _integer_             | `dp-koch: S:L: invalid integer 'K'`     |
| Level token `K` on line `L` of source `S` is an _integer_ outside 0 … 6        | `dp-koch: S:L: value out of range 'K'`  |
| Answer token `K` on line `L` of source `S` is not `y`, `Y`, `n`, or `N`        | `dp-koch: S:L: invalid answer 'K'`      |
| Source `S` ends where a level is required; `L` is the end-of-input line number | `dp-koch: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)                   | `dp-koch: write error`                  |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-08).

## 7. Verification

| Method                                                                                            | Applies to                                         |
| :------------------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                | FR-01 … FR-11, FR-13, FR-14                        |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03, 04, and 06 … 10 have several steps) | FR-01 … FR-10, FR-12 … FR-14                       |
| Unit test (written by the implementer)                                                            | FR-02 … FR-06, NFR-06                              |
| Measurement                                                                                       | NFR-03                                             |
| Inspection / review                                                                               | FR-07 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                    | Verifies                                         |
| :--- | :------------------------- | :----------------------------------------------- |
| 01   | `dp-koch --level 1`        | FR-01, FR-03, FR-04, FR-05                       |
| 02   | `dp-koch < two.txt`        | FR-01, FR-02, FR-05 (singular heading), FR-07    |
| 03   | `dp-koch --prompt two.txt` | FR-08                                            |
| 04   | `dp-koch -s -l 1`          | FR-03 (snowflake), FR-04                         |
| 05   | `dp-koch --svg -l 2`       | FR-06                                            |
| 06   | `dp-koch -l 2 -L 5`        | FR-04 (inexact length, negative zero suppressed) |
| 07   | `dp-koch bad.txt`          | FR-09 (figures kept, CONV-34)                    |
| 08   | `dp-koch missing.txt`      | FR-10                                            |
| 09   | `dp-koch --help`           | FR-11                                            |
| 10   | `dp-koch --level 9`        | FR-13, FR-14                                     |

## 8. Traceability (URD → SRS)

| User requirement | System requirements           |
| :--------------- | :---------------------------- |
| UR-01            | FR-01, FR-05                  |
| UR-02            | FR-03, FR-04                  |
| UR-03            | FR-04, FR-05, NFR-02, CONV-35 |
| UR-04            | FR-01, FR-02, FR-07           |
| UR-05            | FR-01, FR-07                  |
| UR-06            | FR-06                         |
| UR-07            | FR-08, CONV-36                |
| UR-08            | FR-09, CONV-33, CONV-34       |
| UR-09            | FR-02, NFR-02, CONV-37        |
| UR-10            | FR-10, CONV-16                |
| UR-11            | FR-11, FR-12                  |
| UR-12            | FR-13, FR-14                  |
| UR-13            | NFR-01, NFR-02, CONV-03       |
| UR-14            | FR-13, CLI-CONV               |
| UR-15            | NFR-03, NFR-07                |
