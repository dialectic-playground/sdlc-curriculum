<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-calc](#software-requirements-specification-srs--dp-calc)
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

# Software Requirements Specification (SRS) — dp-calc

| Field                     | Value                                          |
| :------------------------ | :--------------------------------------------- |
| Document ID               | SRS-37                                         |
| Project                   | `37-calc` — Interactive Accumulator Calculator |
| Product                   | `dp-calc` (canonical name)                     |
| Version                   | 1.0.0                                          |
| Status                    | Approved (pre-written by the curriculum)       |
| Parent document           | `URD.md` (URD-37)                              |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)   |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018           |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-calc`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-calc` keeps a 64-bit signed accumulator that starts at 0. It reads lines from standard
input or from one file; each line is a sequence of operator-operand pairs that is applied to
the accumulator strictly from left to right. For each accepted line it writes the old value,
the line, and the new value. A line with a syntax error, a division by zero, or an overflow is
reported on standard error with its line number and leaves the accumulator unchanged. The
operator `!` ends the calculation with a closing banner. With `--prompt`, the current value of
the accumulator is written to standard error before each line is read.

### 1.3 Definitions

| Term                         | Definition                                                                                                                                                    |
| :--------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| LF                           | The line-feed byte, `0x0A`                                                                                                                                    |
| Input                        | The byte sequence read from standard input or from the FILE operand                                                                                           |
| Source                       | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)           |
| Line, line number            | As defined in FR-02                                                                                                                                           |
| Whitespace                   | The bytes `0x20` (space), `0x09` (TAB), `0x0B` (VT), `0x0C` (FF), and `0x0D` (CR): the CONV-32 whitespace bytes other than LF, which ends a line              |
| Token                        | A maximal run of non-whitespace bytes within one line (CONV-32 applied to the line)                                                                           |
| Operator                     | One of the five one-byte tokens `+`, `-`, `*`, `/`, `%`                                                                                                       |
| Stop token                   | The one-byte token `!`                                                                                                                                        |
| Operand                      | A token that is a valid _integer_ (CONV-33): `[+-]?[0-9]+` with a value in −2⁶³ … 2⁶³−1                                                                       |
| Accumulator _A_              | The current value, an integer in −9223372036854775808 … 9223372036854775807 (−2⁶³ … 2⁶³−1); initially 0                                                       |
| Pair                         | An operator token followed by the next token of the same line, which must be an operand                                                                       |
| Decimal                      | The plain ASCII decimal representation of an integer: a `-` for negative values, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06, CONV-35) |
| Accepted line, rejected line | As defined in FR-04 and FR-08                                                                                                                                 |

### 1.4 References

- URD-37: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §7.5 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-calc` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §7.5 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. Unlike `dp-infix` (Project 46),
which honors operator precedence, it evaluates strictly from left to right.

### 2.2 Product functions

1. Read the input line by line until `!` or the end of the input.
2. Divide each line into tokens and apply its operator-operand pairs from left to right to a
   copy of the accumulator.
3. Commit the result and write the line `OLD LINE == NEW` when every pair succeeds.
4. Report a line with an error, a division by zero, or an overflow, keep the accumulator
   unchanged, and continue with the next line.
5. End the calculation at `!` with ` **** End of Calculation ****`.
6. Optionally write the accumulator as a prompt to standard error before each line is read.
7. Report unreadable input files; display help and version information; detect and report
   usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- All arithmetic MUST give the exact mathematical results defined in FR-05; results outside
  the 64-bit range MUST be detected (FR-06), never wrapped, saturated, or computed in floating
  point.
- Input/output and evaluation MUST be separate units (NFR-05), as in the textbook's division
  into an input/output module and an evaluation module.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-11.
- The input may contain any bytes; only lines that match the grammar of FR-03 are accepted.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §7.5 keeps an accumulator that starts at 0, shows it as a prompt
followed by a space, reads a line of operator-operand pairs, applies them from left to right,
and prints the old value, the line, `==`, and the new value. An unknown operator or invalid
syntax leaves the accumulator unchanged, and the operator `!` ends the program with
` **** End of Calculation ****`. The program is split into an input/output module and an
evaluation module. `dp-calc` keeps:

- the accumulator starting at 0, the five operators `+ - * / %`, strict left-to-right
  evaluation, and the stop operator `!`;
- the result line `<old> <line> == <new>` and the banner text ` **** End of Calculation ****`
  (with its leading space) exactly;
- the rule that a malformed line leaves the accumulator unchanged, and the prompt
  `<accumulator> ` before each line;
- the separation of input/output from evaluation, now as a design requirement (NFR-05).

It changes or settles the following, for the reasons given:

- **Prompts are optional and go to standard error.** The textbook writes its prompt, preceded
  by an empty line, to the screen, and the user's typing appears after it. `dp-calc` writes
  the prompt `<accumulator> ` only with `-p`, `--prompt`, to standard error (FR-12), and drops
  the empty line, which only separated the dialog on the screen. Standard output is the same
  with or without prompts, so a saved tape holds exactly one line per accepted input line.
- **The banner is followed by nothing.** The textbook writes an empty line after the banner;
  it separated the banner from the shell prompt and is dropped. After the banner the tool
  stops: it reads no more input and writes nothing else (FR-09).
- **Tokens are separated by whitespace.** Operators and operands are separate tokens, so
  `+ 5` is a pair while `+5` is not an operator (FR-03). This removes every ambiguity between
  the operators `+`/`-` and the signs of operands: `- -5` subtracts −5.
- **The echoed line is normalized.** The line is echoed as its evaluated tokens, exactly as
  typed, separated by single spaces, so stray spaces, tabs, and CR bytes never appear in the
  tape (FR-07).
- **Arithmetic is fully defined.** Division and remainder truncate toward zero, as in C99 and
  later (FR-05); results outside the 64-bit range and division by zero reject the line instead
  of producing undefined or platform-dependent results (FR-06). The remainder of −2⁶³ by −1 is
  0, although some processors fault on it.
- **Every rejected line is diagnosed.** The textbook silently ignores a malformed line. `dp-calc`
  writes a CONV-34 diagnostic naming the line and the problem, continues with the next line,
  and finally exits with status 1, so scripts can tell that the tape is incomplete (FR-08).
- **`!` after pairs.** A line such as `* 3 ! + 4` applies the pairs before `!`, writes their
  result line, and then ends the calculation (FR-09). An error before the `!` rejects the line,
  and then the `!` is not reached.
- **End of input without `!`.** The calculation also ends at the end of the input, quietly and
  without the banner (FR-10), so that the banner always means that `!` was typed.
- **Blank lines** are ignored without a diagnostic (FR-10).
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full. From section 10 it incorporates: CONV-32 (each line is
divided into tokens by the CONV-32 whitespace bytes; line numbers), CONV-33 (each operand uses
the _integer_ grammar), CONV-34 (diagnostics in the format `<tool>: <source>:<line>: <message>`,
with the standard message `invalid integer` and four further messages defined in FR-08),
CONV-36 (`-p`, `--prompt`), and CONV-37 (the input is _text data_). It makes **one override**,
which CONV-34 permits: a data diagnostic does **not** end processing; the line is rejected and
the tool continues with the next line, and the exit status is 1 at the end (FR-08). CONV-35
applies only in that integers are written in plain decimal; no real number is ever written.
CONV-38 does not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12,
diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard
input is read as permitted by CONV-26. `dp-calc` copies tokens, not input bytes, to its output,
so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-calc [-p | --prompt] [FILE]
dp-calc --help
dp-calc --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                          |
| :---- | :---------- | :------- | :------ | :----------------------------------------------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the prompt `<accumulator> ` to standard error before each line is read (FR-12) |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                                       |
| —     | `--version` | none     | —       | Print the version line and exit 0                                                    |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands

At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input

Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output

The result lines (FR-07) and the banner (FR-09), in input order. Nothing else. On a usage
error, or when `--help` / `--version` is handled, the output is as specified by FR-14 … FR-17
instead.

### 3.6 Standard error

Prompts (FR-12, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when every line is accepted.

### 3.7 Exit status

| Status | Condition                                                                                                                                           |
| :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The calculation ended (at `!` or at the end of the input, including an empty input) and no line was rejected, or `--help` / `--version` was handled |
| 1      | At least one line was rejected (FR-08), the input could not be opened or read (FR-13), or standard output could not be written                      |
| 2      | Usage error (FR-16)                                                                                                                                 |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\r` CR, `\t` TAB, and the files are the public
fixtures in `tests/fixtures/`: `session.txt` is `+ 5 * 10\n- 20 / 3\n!\n`; `acs.txt` is
`+ 10 * 5\n/ 4\n% 5\n!\n`; `messy.txt` is
`  +   007\t*  3\r\n\r\n   \n-\t+21 + 0\r\n% 5\n`; `negative.txt` is
`- 7 / 2\n- 4 % 2\n+ 8 % -3\n- 8 / -3\n* -1 % 3\n`; `errors.txt` is
`+ 10\n+ 10 ? 5\n/ 0\n+ x\n* 2 -\n- 3\n!\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-16).
_AC:_ `dp-calc < session.txt`, `dp-calc session.txt`, and `dp-calc - < session.txt` write the
same output. _(UR-09)_

**FR-02: Lines.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into lines: each LF ends a line
(the LF is not part of it), and the bytes after the last LF, if there are any, form a final
line without an LF. An empty input has no lines; an input ending with LF has no empty line
after the last LF. Lines are numbered from 1 in input order; the line number of a line is 1
plus the number of LF bytes before its first byte (CONV-32). CR is whitespace (FR-03), so CRLF
input reads exactly like LF input. A `0x1A` byte that is followed by any other byte is ordinary
data.
_AC:_ a file `+ 5\r\n` + `0x1A 0x1A` → `0 + 5 == 5\n`, exit 0; a file `+ 5` + `0x1A` + `\n+ 1\n`
→ stderr `dp-calc: midz.txt:1: invalid integer '5` + `0x1A` + `'`, then `0 + 1 == 1\n`, exit 1.
_(UR-10)_

**FR-03: Line syntax.**
Each line MUST be divided into tokens (section 1.3). A line with no tokens is _blank_ (FR-10).
A non-blank line is examined from left to right as follows, starting at its first token:

1. If the token is the stop token `!`, the line ends here (FR-09); the tokens after it, if
   any, are ignored.
2. If the token is not an operator, the line is rejected: `invalid operator '<token>'`.
3. If the operator is the last token of the line, the line is rejected:
   `missing operand after '<operator>'`.
4. If the next token is not an operand (CONV-33), including an integer outside
   −2⁶³ … 2⁶³−1, the line is rejected: `invalid integer '<token>'`.
5. Otherwise the operator and the operand form a pair, which is applied (FR-04); then
   examination continues with the token after the operand. If there is none, the line ends.

Tokens are compared as bytes: `+5`, `x`, `**`, and `÷` are not operators, and `!` is not an
operand. The operand grammar allows a sign and leading zeros (`+21`, `-5`, `007`).
_AC:_ in `messy.txt`, line 1 is the two pairs `+ 007` and `* 3`; a line `+5` is rejected with
`invalid operator '+5'`; a line `+ !` with `invalid integer '!'`; a line `* 2 -` with
`missing operand after '-'`; a line `\t+\v4\f* 2 ` is the pairs `+ 4` and `* 2`. _(UR-02,
UR-05, UR-10)_

**FR-04: Left-to-right evaluation.**
A line is evaluated on a working value _W_, which starts equal to the accumulator _A_. Each
pair `<op> <n>` MUST be applied in order as _W_ ← _W_ `op` _n_ (FR-05), with no operator
precedence. If every pair of the line is applied without error, the line is _accepted_: _A_
becomes the final _W_ and the result line is written (FR-07). If any step rejects the line
(FR-03, FR-06), _A_ MUST remain exactly as it was before the line, even if earlier pairs of the
line had been applied to _W_.
_AC:_ `dp-calc < session.txt` → stdout
`0 + 5 * 10 == 50\n50 - 20 / 3 == 10\n **** End of Calculation ****\n`, stderr empty, exit 0
((0 + 5) × 10 = 50, (50 − 20) / 3 = 10); in `errors.txt`, the line `* 2 -` is rejected after
`* 2` has been applied to _W_, and the next line `- 3` is applied to 10, giving 7. _(UR-01,
UR-02)_

**FR-05: Arithmetic.**
For a working value _W_ and an operand _n_, the operators MUST compute the exact
mathematical values

- `+`: _W_ + _n_; `-`: _W_ − _n_; `*`: _W_ × _n_;
- `/`: the quotient _q_ of _W_ and _n_ truncated toward zero: |_q_| = ⌊|_W_| / |_n_|⌋, and _q_
  is negative exactly when _W_ and _n_ are non-zero and have opposite signs;
- `%`: the remainder _W_ − _n_ × _q_, with _q_ as for `/`. The remainder is 0 or has the sign
  of _W_, and its magnitude is less than |_n_|.

These rules apply to every pair of values, including _W_ = −9223372036854775808 with
_n_ = −1, for which `%` gives 0 (FR-06 rejects the corresponding `/`).
_AC:_ `dp-calc acs.txt` → `0 + 10 * 5 == 50\n50 / 4 == 12\n12 % 5 == 2\n **** End of Calculation ****\n`;
`dp-calc - < negative.txt` → `0 - 7 / 2 == -3\n-3 - 4 % 2 == -1\n-1 + 8 % -3 == 1\n1 - 8 / -3 == 2\n2 * -1 % 3 == -2\n`
(−7 / 2 = −3, −7 % 2 = −1, 7 % −3 = 1, −7 / −3 = 2, −2 % 3 = −2), exit 0. _(UR-04)_

**FR-06: Division by zero and overflow.**
Before a `/` or `%` pair is applied, if _n_ = 0 the line MUST be rejected with
`division by zero`. If the exact result of any pair lies outside
−9223372036854775808 … 9223372036854775807, the line MUST be rejected with `integer overflow`;
this is checked for every pair, so an intermediate overflow rejects the line even if later
pairs would bring the value back into range. The only overflowing `/` is
−9223372036854775808 / −1. Implementations MUST detect overflow without relying on
wrapped, saturated, or undefined arithmetic.
_AC:_ from 9223372036854775807, the lines `+ 1` and `* 2 / 2` are rejected with
`integer overflow`; from −9223372036854775808, `/ -1` and `* -1` are rejected with
`integer overflow` and `% -1` gives 0; from 0, `- -9223372036854775808` is rejected with
`integer overflow`, while `+ -9223372036854775808` gives −9223372036854775808; from 10, `/ 0`
is rejected with `division by zero`. _(UR-04, UR-05)_

**FR-07: Result line.**
For an accepted line that contains at least one pair, the tool MUST write exactly
`<old> <tokens> == <new>` + LF, where `<old>` and `<new>` are the decimals of _A_ before and
after the line, and `<tokens>` is the line's evaluated tokens — every token before the stop
token, or all tokens if there is none — each exactly as it appears in the input, joined by
single spaces. Leading and trailing whitespace and the whitespace between tokens are not
reproduced; operands keep their spelling (`007`, `+21`). There is exactly one space on each
side of `==` and no trailing space.
_AC:_ `dp-calc messy.txt` → `0 + 007 * 3 == 21\n21 - +21 + 0 == 0\n0 % 5 == 0\n`, exit 0.
_(UR-03)_

**FR-08: Rejected lines.**
When a line is rejected, the tool MUST write one diagnostic to standard error,
`dp-calc: <source>:<line>: <message>`, where `<source>` is as defined in section 1.3,
`<line>` is the line number (FR-02), and `<message>` is the message of the **first** problem
found when examining the line from left to right (FR-03, FR-06):

| Problem                                                     | `<message>`                          |
| :---------------------------------------------------------- | :----------------------------------- |
| A token in operator position is neither an operator nor `!` | `invalid operator '<token>'`         |
| An operator is the last token of the line                   | `missing operand after '<operator>'` |
| The token after an operator is not a valid _integer_        | `invalid integer '<token>'`          |
| `/` or `%` with operand 0                                   | `division by zero`                   |
| A result outside −2⁶³ … 2⁶³−1                               | `integer overflow`                   |

`<token>` and `<operator>` are inserted as their exact bytes (CONV-15). Nothing is written to
standard output for a rejected line, and the accumulator is unchanged (FR-04). Processing then
**continues** with the next line (overriding CONV-34's default), and the final exit status is
1, whether the calculation ends at `!` or at the end of the input.
_AC:_ `dp-calc errors.txt` → stdout `0 + 10 == 10\n10 - 3 == 7\n **** End of Calculation ****\n`,
stderr
`dp-calc: errors.txt:2: invalid operator '?'\ndp-calc: errors.txt:3: division by zero\ndp-calc: errors.txt:4: invalid integer 'x'\ndp-calc: errors.txt:5: missing operand after '-'\n`,
exit 1. _(UR-05, UR-09)_

**FR-09: Stop.**
When the examination of a line reaches the stop token (FR-03 step 1), the calculation ends:
if the line had at least one pair before the `!`, the line is accepted and its result line is
written first (FR-07); then the tool MUST write the banner ` **** End of Calculation ****` + LF
(one leading space, four asterisks on each side, no trailing space), flush standard output, and
exit. It MUST NOT read any further input, write any further prompt, or write anything after
the banner. The exit status is 0, or 1 if an earlier line was rejected. A `!` that follows a
rejected step is never reached, so that line is rejected and the calculation continues.
_AC:_ a file `+ 2\n/ 0 !\n* 3 ! + 4\nthis line is never read\n` → stdout
`0 + 2 == 2\n2 * 3 == 6\n **** End of Calculation ****\n`, stderr
`dp-calc: stop.txt:2: division by zero\n`, exit 1; a line `!   ignored tokens` ends the
calculation with only the banner. _(UR-06)_

**FR-10: Blank lines and the end of the input.**
A blank line (no tokens, for example an empty line or one of spaces, TABs, and CR) MUST be
ignored: no output, no diagnostic, and the accumulator is unchanged. When the end of the input
is reached without a stop token, the calculation ends quietly: no banner is written, and the
exit status is 0, or 1 if a line was rejected. An empty input produces no output.
_AC:_ `dp-calc` with empty standard input → stdout and stderr empty, exit 0; `dp-calc messy.txt`
ignores lines 2 and 3 and ends after line 5 without a banner, exit 0. _(UR-01, UR-10)_

**FR-11: Streaming.**
Lines MUST be processed one at a time, in input order. As soon as a line is complete (its LF
has been read, or the end of the input has been reached), the tool MUST process it, write its
result line or diagnostic, and flush the stream written, before it waits for any further input
bytes. The tool MUST NOT wait for the end of the input before answering a line.
_AC:_ at a terminal, typing `+ 5` and Enter shows `0 + 5 == 5` before anything else is typed
(manual check). _(UR-07)_

**FR-12: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool: the decimal of the current
accumulator _A_ followed by one space (`0 `, `50 `, `-3 `), with no LF. With prompts enabled,
the tool MUST write the prompt to standard error, and flush standard error, immediately before
each attempt to read a line: once before the first line, and once after each line has been
processed (accepted, rejected, or blank), except after a line that ends the calculation with
`!`. A prompt is therefore also written before the attempt that reaches the end of the input
(CONV-36). A diagnostic for a rejected line follows that line's prompt on the same line of
standard error. Prompts never change standard output. No prompt is written if the input
cannot be opened.
_AC:_ `dp-calc --prompt < session.txt` → stdout as in FR-04, stderr `0 50 10 ` (no LF), exit 0;
`dp-calc -p` with empty standard input → stderr `0 `, stdout empty, exit 0; `dp-calc -p errors.txt`
→ stderr begins `0 10 dp-calc: errors.txt:2: invalid operator '?'\n10 dp-calc: errors.txt:3: …`
and ends `10 7 `. _(UR-08)_

**FR-13: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-calc: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Output already written is kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-calc missing.txt` → stderr `dp-calc: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-calc subdir` where `subdir` is a directory →
`dp-calc: subdir: Is a directory`. _(UR-11)_

**FR-14: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-calc --help` matches the user manual exactly; `dp-calc extra --help` also prints it.
_(UR-11)_

**FR-15: Version.**
`--version` MUST write `dp-calc (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-11)_

**FR-16: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-calc: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-calc session.txt acs.txt` → `dp-calc: extra operand 'acs.txt'`; `dp-calc -x --help` →
`dp-calc: invalid option -- 'x'`; `dp-calc --prompt=yes` →
`dp-calc: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-11, UR-13)_

**FR-17: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-calc -p - extra < session.txt` writes no
prompt. _(UR-11)_

## 5. Non-functional requirements

| ID     | Category                                                  | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Verification                                                    |
| :----- | :-------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :-------------------------------------------------------------- |
| NFR-01 | Portability                                               | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: integer semantics and console input | The arithmetic of FR-05 and FR-06 MUST give the same results on every platform and in every language: implementations MUST NOT rely on the host language's division or remainder operator where it rounds differently (for example toward negative infinity), on signed overflow behavior, or on hardware traps (−2⁶³ / −1 and −2⁶³ % −1 fault on some processors). The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03) and flushed as FR-11 and FR-12 require, even when they are pipes or files. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                               | Processing 1 000 000 lines of 10 pairs each (about 30 MiB of input) MUST take under 3 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31) for lines of up to 64 KiB. Memory MUST NOT grow with the number of lines; only the current line is held. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                       | Measurement                                                     |
| NFR-04 | Robustness                                                | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including lines of any length, tokens far outside the 64-bit range, and every overflow case. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                           | Input/output (reading lines, prompts, writing results and diagnostics) and evaluation MUST be separate units, as in the textbook's division into modules: the evaluator MUST be a function that takes the accumulator and a line's tokens and returns either the new accumulator (with the number of evaluated tokens and whether `!` was reached) or the rejection message, and performs no I/O. Option parsing, tokenizing, the arithmetic of one pair, and result formatting MUST also be separate units.                                                                                                                                                                                                                                                                                                                                                                                                                    | Design review                                                   |
| NFR-06 | Testability                                               | The evaluator and the arithmetic of one pair MUST be pure functions covered by unit tests, including every acceptance value of FR-05 and FR-06, all sign combinations of `/` and `%`, and the operand pairs (−2⁶³, −1), (−2⁶³, 1), (2⁶³−1, −1), and (2⁶³−1, 2⁶³−1) for each operator.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Code review                                                     |
| NFR-07 | Build                                                     | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | CI                                                              |
| NFR-08 | Security                                                  | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-calc --help' for more information.`

| Trigger                                      | Exact first line                                                                      |
| :------------------------------------------- | :------------------------------------------------------------------------------------ |
| Unknown short option `x`                     | `dp-calc: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-calc: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-calc: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-calc: extra operand 'X'`                                                          |

Line diagnostics (the line is rejected, processing continues, final exit status 1; `S` is the
source and `L` the line number):

| Trigger                                                       | Exact message                             |
| :------------------------------------------------------------ | :---------------------------------------- |
| Token `K` in operator position is neither an operator nor `!` | `dp-calc: S:L: invalid operator 'K'`      |
| Operator `O` is the last token of its line                    | `dp-calc: S:L: missing operand after 'O'` |
| Token `K` after an operator is not a valid _integer_          | `dp-calc: S:L: invalid integer 'K'`       |
| `/` or `%` with operand 0                                     | `dp-calc: S:L: division by zero`          |
| A result outside −2⁶³ … 2⁶³−1                                 | `dp-calc: S:L: integer overflow`          |

Runtime errors (exit status 1; the tool stops):

| Trigger                                                      | Exact message                           |
| :----------------------------------------------------------- | :-------------------------------------- |
| FILE `F` does not exist                                      | `dp-calc: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied   | `dp-calc: F: Permission denied`         |
| FILE `F` is a directory                                      | `dp-calc: F: Is a directory`            |
| A component of FILE `F` is not a directory                   | `dp-calc: F: Not a directory`           |
| Any other open or read failure of FILE `F`                   | `dp-calc: F: Input/output error`        |
| Any of the above for standard input                          | the same message with `F` = `-`         |
| Standard output cannot be written (other than a broken pipe) | `dp-calc: write error`                  |

When `--prompt` is given, a line diagnostic follows the prompt written before that line, on
the same line of standard error (FR-12).

## 7. Verification

| Method                                                                                | Applies to                                         |
| :------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                    | FR-01, FR-03 … FR-10, FR-12 … FR-14, FR-16, FR-17  |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 05 … 09 have several steps) | FR-02 … FR-10, FR-12, FR-13, FR-15 … FR-17         |
| Unit test (written by the implementer)                                                | FR-03 … FR-07, NFR-06                              |
| Measurement                                                                           | NFR-03                                             |
| Inspection / review                                                                   | FR-11 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                          | Verifies                                                                           |
| :--- | :------------------------------- | :--------------------------------------------------------------------------------- |
| 01   | `dp-calc < session.txt`          | FR-01, FR-04, FR-07, FR-09                                                         |
| 02   | `dp-calc acs.txt`                | FR-01, FR-05 (`/`, `%`)                                                            |
| 03   | `dp-calc --prompt < session.txt` | FR-12                                                                              |
| 04   | `dp-calc messy.txt`              | FR-02 (CRLF), FR-03, FR-07 (normalized echo), FR-10 (blank lines, end without `!`) |
| 05   | `dp-calc - < negative.txt`       | FR-01, FR-05 (truncation toward zero)                                              |
| 06   | `dp-calc errors.txt`             | FR-04 (accumulator kept), FR-06, FR-08                                             |
| 07   | `dp-calc` (empty standard input) | FR-10                                                                              |
| 08   | `dp-calc missing.txt`            | FR-13                                                                              |
| 09   | `dp-calc --help`                 | FR-14                                                                              |
| 10   | `dp-calc session.txt acs.txt`    | FR-16, FR-17                                                                       |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                  |
| :--------------- | :----------------------------------- |
| UR-01            | FR-04, FR-10                         |
| UR-02            | FR-03, FR-04                         |
| UR-03            | FR-07                                |
| UR-04            | FR-05, FR-06                         |
| UR-05            | FR-03, FR-06, FR-08, CONV-34         |
| UR-06            | FR-09                                |
| UR-07            | FR-11, NFR-02                        |
| UR-08            | FR-12, CONV-36                       |
| UR-09            | FR-01, FR-08, CONV-26                |
| UR-10            | FR-02, FR-03, FR-10, NFR-02, CONV-37 |
| UR-11            | FR-13 … FR-17, CONV-16               |
| UR-12            | NFR-01, NFR-02, CONV-03              |
| UR-13            | FR-16, CLI-CONV                      |
| UR-14            | NFR-03, NFR-07                       |
