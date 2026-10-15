<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-infix](#software-requirements-specification-srs--dp-infix)
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

# Software Requirements Specification (SRS) — dp-infix

| Field                     | Value                                                  |
| :------------------------ | :----------------------------------------------------- |
| Document ID               | SRS-46                                                 |
| Project                   | `46-infix` — Shunting-Yard Infix to Postfix Conversion |
| Product                   | `dp-infix` (canonical name)                            |
| Version                   | 1.0.0                                                  |
| Status                    | Approved (pre-written by the curriculum)               |
| Parent document           | `URD.md` (URD-46)                                      |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)           |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                   |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-infix`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-infix` reads a dialog of lines from standard input or from one file: an infix expression,
the answer to `Another? (y/n)`, the next expression, and so on. It converts each expression to
postfix notation with the shunting-yard algorithm, checking it in the same left-to-right pass,
and writes the original and the converted expression to standard output. It reports malformed
expressions with the first error found and goes on with the dialog; it reports an answer it
does not understand and stops. It can write prompts to standard error before each read.

### 1.3 Definitions

| Term              | Definition                                                                                                                                                                              |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR            | The bytes `0x0A` and `0x0D`                                                                                                                                                             |
| Blank             | The byte `0x20` (space) or `0x09` (TAB)                                                                                                                                                 |
| Input             | The byte sequence read from standard input or from the FILE operand                                                                                                                     |
| Source            | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)                                     |
| Line, line number | As defined in FR-02; the line number of a line is 1 plus the number of LF bytes before its first byte (CONV-32)                                                                         |
| Operand character | An ASCII letter or digit: `0x30`–`0x39`, `0x41`–`0x5A`, `0x61`–`0x7A`                                                                                                                   |
| Operand           | A maximal run of operand characters in an expression line (FR-03)                                                                                                                       |
| Operator          | One of the bytes `+`, `-`, `*`, `/`, `%`                                                                                                                                                |
| Token             | An operand, an operator, `(`, or `)` (FR-03)                                                                                                                                            |
| Precedence        | 2 for `*`, `/`, `%`; 1 for `+`, `-`                                                                                                                                                     |
| Record            | The two report lines for one valid expression (FR-06)                                                                                                                                   |
| Trimmed           | With every leading and trailing blank removed                                                                                                                                           |
| Shown byte        | A byte as it appears in a diagnostic: the byte itself if it lies in `0x21`–`0x7E`, otherwise `\x` followed by its value as two uppercase hexadecimal digits (`0xC3` is shown as `\xC3`) |

### 1.4 References

- URD-46: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §10.5 (informative; see §2.5)
- E. W. Dijkstra, "Algol 60 translation", Mathematisch Centrum report MR 35, 1961 (the
  shunting-yard algorithm; informative)

## 2. Overall description

### 2.1 Product perspective

`dp-infix` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §10.5 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. It uses the stack that Project 45
(`dp-stack1`, `dp-stack2`) builds as an abstract data type.

### 2.2 Product functions

1. Read the dialog line by line: an expression, then an answer, until the answer is no or the
   input ends.
2. Divide each expression into operands, operators, and parentheses.
3. Convert each expression to postfix with an operator stack, checking it at the same time.
4. Write the original expression and its postfix form; report a malformed expression and go on.
5. Optionally write a prompt to standard error before each read.
6. Report invalid answers and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The conversion MUST use an explicit stack of pending operators and parentheses (NFR-05). The
  nesting depth of parentheses MUST NOT be limited by the depth of the call stack.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-08.
- The input may contain any bytes; bytes that are not allowed in an expression are reported
  (FR-05).

### 2.5 Relationship to the textbook program (informative)

The textbook program of §10.5 reads an infix expression, converts it to postfix with an
operator stack — operands go straight to the output, `(` is pushed, `)` pops to the matching
`(`, and an operator first pops every operator of greater or equal precedence — prints the
result, and asks `Another? (y/n)`. `dp-infix` keeps:

- the algorithm, the operators `+ - * / %`, the precedence table (`* / %` above `+ -`), and
  left associativity for all five operators (FR-04);
- the report layout of the section's description, `Infix:` and `Postfix:` with the labels
  padded so the expressions line up, and postfix tokens separated by single spaces (FR-06);
- the `Another? (y/n)` dialog: each expression is followed by an answer, and `y` asks for
  another (FR-07).

It changes the following, for the reasons given:

- **Multi-character operands.** The textbook treats each letter or digit as an operand of its
  own, so `AB` means two operands and `40` means `4` and `0`. Here an operand is a maximal run
  of letters and digits (FR-03), which allows names and numbers such as `rate` and `40`.
  Expressions written with single-letter operands separated by operators or blanks, like every
  example in the section, convert exactly as before.
- **Every expression is validated** (FR-05). The textbook converts whatever it is given:
  `(A + B` or `A + * B` produce a postfix string that is not a valid expression, and unknown
  characters are silently passed on or dropped. Here a malformed expression is reported with
  its line number and the first error found, and no record is written for it.
- **The dialog survives a malformed expression.** Rejecting an expression is not a reason to
  end an interactive session, so the tool reports it, asks `Another? (y/n)`, and goes on; the
  exit status at the end records that something was rejected (FR-07, FR-12). This overrides
  the CONV-34 default (§2.6).
- **Answers are strict, and the end of input ends the session.** The textbook continues on `y`
  and stops otherwise. Here `y`/`Y` continue, `n`/`N` stop, the end of the input stops (it is
  the scripted equivalent of quitting), and any other answer is reported and ends the run with
  status 1, because a script whose answers are out of step with its expressions would otherwise
  be misread silently (FR-07).
- **Prompts are optional and go to standard error.** With `-p`, `--prompt` the tool writes
  `Enter infix expression: ` before each expression and `Another? (y/n) ` before each answer
  (FR-09). The section's description gives the second prompt; the first is written in the same
  voice. Without the flag no prompt is written, and the blank lines and spacing that separated
  the textbook's output from the echo of the keyboard are not reproduced: standard output holds
  only the records.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings, a missing final LF, and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full, with **one override**: a CONV-34 data diagnostic about a
malformed _expression_ does not end processing; the dialog continues and the exit status at the
end is 1 (FR-05, FR-07). A diagnostic about an invalid _answer_ has the CONV-34 default
consequences. From section 10 it incorporates: CONV-32 (only the definition of line numbers;
the input is line-oriented, FR-02, and is not read as tokens), CONV-34 (the diagnostic format,
with the project-specific messages of FR-05 and FR-07), CONV-36 (`-p`, `--prompt`, with two
prompts), and CONV-37 (the input is _text data_). CONV-33 does not apply, because operands are
names, not numbers, and are never given a numeric value; CONV-35 does not apply, because no
real number is written; CONV-38 does not apply, because nothing is random. Option syntax
follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit statuses are
those of CONV-18. Standard input is read as permitted by CONV-26. The `Infix:` line copies the
bytes of a valid expression, which are all ASCII (FR-03), so CONV-04 is satisfied trivially.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-infix [-p | --prompt] [FILE]
dp-infix --help
dp-infix --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                   |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-09 to standard error before each read |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                |
| —     | `--version` | none     | —       | Print the version line and exit 0                             |

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

The records (FR-06), in input order. Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-09, only with `--prompt`) and diagnostics (section 6).

### 3.7 Exit status

| Status | Condition                                                                                                                                                            |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The session ended (FR-07) and every expression read was valid, including an empty input; or `--help` / `--version` was handled                                       |
| 1      | At least one expression was malformed (FR-05), an answer was invalid (FR-07), the input could not be opened or read (FR-10), or standard output could not be written |
| 2      | Usage error (FR-13)                                                                                                                                                  |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\r` CR, and `\t` TAB, and the following are public
fixture files in `tests/fixtures/`: `readme.txt` holds the six expressions of the section's
description, `(A + B) * C - D / E`, `A + B`, `A + B * C`, `(A + B) * C`, `(A + B) * (C - D)`,
and `A - B - C`, each followed by an answer line (`y` five times, then `n`); `mixed.txt` is
`rate * (hours + 40) % 7\r\nY\r\n((x1))\r\ny\r\n\t a/b/c*d \r\nN\r\n`; `errors.txt` is
`(A + B\ny\nA + * B\ny\nA $ B\ny\nA + B\nn\n`; `stop.txt` is `A * B\nn\nC + D\ny\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
_AC:_ `dp-infix readme.txt` and `dp-infix < readme.txt` write the same records. _(UR-05)_

**FR-02: Lines.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into lines: each LF ends a line,
and bytes after the last LF, if there are any, form a final line without an LF. An input that
ends with an LF therefore has no empty line after it, and an empty input has no lines. From
each line the LF is removed, and then one CR, if the line ends with one; any other CR is an
ordinary byte. Lines are read one at a time, in order, alternately as expression lines and
answer lines (FR-07); the line number of a line follows CONV-32 and counts both kinds.
_AC:_ `dp-infix mixed.txt` (CRLF) writes three records, exit 0; the hidden fixture
`A%B\ny\nC-D`, without a final LF, gives two records; `A+B\r\ny\r\nC*D\r\n` followed by one
`0x1A` byte gives two records, exit 0; `A+B` followed by `0x1A` and LF reports
`invalid character '\x1A'` on line 1, because that Ctrl-Z byte does not end the input.
_(UR-04, UR-10)_

**FR-03: Tokens.**
An expression line is scanned from left to right. Blanks separate tokens and are otherwise
ignored. A maximal run of operand characters is one operand token, written later exactly as
spelled (`007` stays `007`, `0x1f` is one operand). Each of the bytes `+ - * / % ( )` is a
token by itself, whatever surrounds it, so `A+B` and `A + B` are the same expression. Every
other byte — including CR inside the line, VT, FF, `_`, `.`, and every byte `0x80`–`0xFF` — is
an invalid character, reported by FR-05 when the scan reaches it.
_AC:_ `rate * (hours + 40) % 7` has the tokens `rate`, `*`, `(`, `hours`, `+`, `40`, `)`, `%`,
`7`; `A_B` is reported as `invalid character '_'`. _(UR-01, UR-02)_

**FR-04: Conversion.**
A valid expression (FR-05) MUST be converted with the following algorithm, using an output
sequence and a stack, both initially empty, and processing the tokens in order:

1. An operand is appended to the output.
2. `(` is pushed onto the stack.
3. `)` pops operators from the stack and appends them to the output until the top of the stack
   is `(`; that `(` is popped and discarded.
4. An operator _o_ first pops and appends every operator on top of the stack whose precedence
   is greater than or equal to the precedence of _o_, stopping at `(` or an empty stack; then
   _o_ is pushed. All five operators are therefore left-associative.
5. After the last token, every remaining operator is popped and appended.

The postfix form is the output sequence. Parentheses never appear in it.
_AC:_ `(A + B) * C - D / E` → `A B + C * D E / -`; `A + B` → `A B +`; `A + B * C` →
`A B C * +`; `(A + B) * C` → `A B + C *`; `(A + B) * (C - D)` → `A B + C D - *`;
`A - B - C` → `A B - C -`; `a/b*c%d` → `a b / c * d %`; `a+b*c-d/e%f` →
`a b c * + d e / f % -`; `((a+b)*(c-d))/(e%f)` → `a b + c d - * e f % /`; `((x1))` → `x1`.
_(UR-01)_

**FR-05: Malformed expressions.**
An expression is checked during the same left-to-right scan as FR-03 and FR-04, with a state
that is either _operand expected_ (at the start, after an operator, and after `(`) or
_operator expected_ (after an operand and after `)`). The first of the following conditions
that occurs, in scan order, makes the expression malformed:

| Condition                                                                   | `<message>`                          |
| :-------------------------------------------------------------------------- | :----------------------------------- |
| An invalid character _c_ is reached (in either state)                       | `invalid character '<shown byte c>'` |
| An operand _x_ when an operator is expected                                 | `unexpected operand '<x>'`           |
| An operator _o_ when an operand is expected                                 | `unexpected operator '<o>'`          |
| `(` when an operator is expected                                            | `unexpected '('`                     |
| `)` when an operand is expected                                             | `unexpected ')'`                     |
| `)` when the stack holds no `(`                                             | `unmatched ')'`                      |
| The line holds no token at all (it is empty or holds only blanks)           | `empty expression`                   |
| The line ends when an operand is expected                                   | `unexpected end of expression`       |
| The line ends when an operator is expected, and the stack still holds a `(` | `unmatched '('`                      |

The last three conditions are checked, in this order, only at the end of the line. For a
malformed expression the tool MUST write `dp-infix: <source>:<line>: <message>`, where
`<line>` is the expression line's number, MUST NOT write a record, and MUST continue the dialog
with the answer line (FR-07); the exit status at the end of the run is then 1.
_AC:_ `dp-infix errors.txt` → stdout the record for `A + B`, stderr
`dp-infix: errors.txt:1: unmatched '('\n`, `dp-infix: errors.txt:3: unexpected operator '*'\n`,
and `dp-infix: errors.txt:5: invalid character '$'\n`, exit 1. In the hidden tests: `(` and
`A +` give `unexpected end of expression`; `()` and `)A` give `unexpected ')'`; `A)` gives
`unmatched ')'`; `A B` gives `unexpected operand 'B'`; `A(B)` gives `unexpected '('`; `-A`
gives `unexpected operator '-'`; `((A)` gives `unmatched '('`; `A + é` (UTF-8) gives
`invalid character '\xC3'`. _(UR-08, UR-09)_

**FR-06: Record format.**
For a valid expression the tool MUST write exactly the two lines

```text
Infix:   <expression>
Postfix: <postfix>
```

where `Infix:` is followed by three spaces and `Postfix:` by one, so both expressions start in
column 10; `<expression>` is the expression line trimmed (its interior bytes, including TABs and
repeated blanks, exactly as read); and `<postfix>` is the postfix tokens of FR-04 joined by
single spaces. Each line ends with one LF and has no trailing spaces. Records follow one another
with no blank lines, header, or summary.
_AC:_ `dp-infix < readme.txt` → stdout begins
`Infix:   (A + B) * C - D / E\nPostfix: A B + C * D E / -\nInfix:   A + B\nPostfix: A B +\n`;
`\t a/b/c*d ` in `mixed.txt` gives `Infix:   a/b/c*d\nPostfix: a b / c / d *\n`. _(UR-03)_

**FR-07: Dialog.**
The tool MUST run the following loop:

1. Write prompt P1 (FR-09). Read the next line. If the input has ended, end the session.
2. Convert the line as an expression (FR-03 … FR-05) and write its record (FR-06) or its
   diagnostic (FR-05).
3. Write prompt P2 (FR-09). Read the next line. If the input has ended, end the session.
4. The trimmed line is the answer. If it is `y` or `Y`, continue with step 1. If it is `n` or
   `N`, end the session. Otherwise write `dp-infix: <source>:<line>: invalid answer '<answer>'`,
   where `<answer>` is the trimmed line's exact bytes (CONV-34), read no further input, and exit
   with status 1; records already written are kept.

When the session ends, the tool exits with status 1 if any expression was malformed and 0
otherwise. Lines after an answer `n` are not read or checked.
_AC:_ `dp-infix stop.txt` → only the record for `A * B`, exit 0; `dp-infix` with empty standard
input → stdout and stderr empty, exit 0; an input whose second line is `yes` →
`dp-infix: <source>:2: invalid answer 'yes'`, exit 1; an empty answer line gives
`invalid answer ''`; the answers `Y`, `\ty\t`, and `N` are accepted. _(UR-04, UR-09)_

**FR-08: Streaming.**
Lines MUST be processed one at a time. As soon as a line is complete (its LF has been read, or
the input has ended), the tool MUST process it — writing and flushing the record, or writing the
diagnostic — before it waits for any further input. It MUST NOT read the input beyond the
current line, apart from ordinary buffering of bytes that are already available.
_AC:_ at a terminal, typing `A+B` and Enter shows the record before anything else is typed
(manual check). _(UR-06)_

**FR-09: Prompts.**
`-p`, `--prompt` enables two prompts, written to standard error with no LF, immediately before
the read they belong to, after flushing standard output; standard error is flushed after each
(CONV-36):

| Prompt | Exact bytes                                              | Written                                                                                                 |
| :----- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------ |
| P1     | `Enter infix expression: ` (24 bytes, ending in a space) | Before every read of an expression line (FR-07 step 1), including one that reaches the end of the input |
| P2     | `Another? (y/n) ` (15 bytes, ending in a space)          | Before every read of an answer line (FR-07 step 3), including one that reaches the end of the input     |

A diagnostic for an expression follows P1 on the same line of standard error, and a diagnostic
for an answer follows P2. Without the flag, no prompt is written. Standard output is the same
with and without it. No prompt is written if the input cannot be opened.
_AC:_ `dp-infix --prompt < readme.txt` → stdout as without `--prompt`, stderr P1 P2 six times
concatenated, exit 0; `dp-infix -p` with empty standard input → stderr P1 only, exit 0.
_(UR-07)_

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-infix: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Records already written are kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-infix missing.txt` → stderr `dp-infix: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-infix subdir`, where `subdir` is a directory →
`dp-infix: subdir: Is a directory`. _(UR-09)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-infix --help` matches the user manual exactly; `dp-infix extra --help` also prints it.
_(UR-11)_

**FR-12: Version.**
`--version` MUST write `dp-infix (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-11)_

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-infix: extra operand '<second operand>'`, after the whole
argument list has been scanned (CONV-12).
_AC:_ `dp-infix readme.txt mixed.txt` → `dp-infix: extra operand 'mixed.txt'`;
`dp-infix -x --help` → `dp-infix: invalid option -- 'x'`; `dp-infix --prompt=yes` →
`dp-infix: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-12, UR-13)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-infix -p - extra < readme.txt` writes no
prompt. _(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                                         | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Verification                                                    |
| :----- | :--------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                                      | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: line-oriented input and interactive dialog | The input MUST be read in binary mode on every platform, so that the I/O layer neither translates CRLF nor treats a `0x1A` byte as end-of-file; only FR-02 decides what a final CR or a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the session normally, at either kind of read. Prompts MUST reach the terminal before the tool waits for input, and each record before the next read, on every platform: standard output and standard error MUST be flushed explicitly where the platform buffers them, and written in binary mode (CONV-03). | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                                      | Converting an input of 100 000 expressions of about 40 bytes each, or one expression line of 1 000 000 bytes with parentheses nested 100 000 deep, MUST take under 1 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware, with peak memory under 64 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MAY grow linearly with the length of the longest line, and MUST NOT grow with the number of lines. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                           | Measurement                                                     |
| NFR-04 | Robustness                                                       | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including lines of any length, any nesting depth, NUL bytes, and invalid UTF-8. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                             | Unit + black-box tests                                          |
| NFR-05 | Maintainability: stack-based design                              | The operator stack MUST be an explicit last-in-first-out data structure with push, pop, top, and is-empty operations, separate from the converter, so that the stack ADT of Project 45 can be reused; the converter MUST NOT use recursion. Option parsing, line reading, tokenizing, conversion with validation, record formatting, and the dialog MUST be separate units. The precedence table MUST be defined in exactly one place.                                                                                                                                                                                                                                               | Design review                                                   |
| NFR-06 | Testability                                                      | The converter MUST be a pure function from an expression line to either the postfix token sequence or the first error, covered by unit tests that include every acceptance value of FR-04 and every row of the FR-05 table, with an example of each row reached in each scanner state where applicable.                                                                                                                                                                                                                                                                                                                                                                              | Code review                                                     |
| NFR-07 | Build                                                            | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | CI                                                              |
| NFR-08 | Security                                                         | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-infix --help' for more information.`

| Trigger                                      | Exact first line                                                                       |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-infix: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-infix: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-infix: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-infix: extra operand 'X'`                                                          |

Data diagnostics about expressions (the dialog continues; the final exit status is 1). `S` is
the source and `L` the expression line's number:

| Trigger                                    | Exact message                                 |
| :----------------------------------------- | :-------------------------------------------- |
| Invalid character, shown as `C` (FR-05)    | `dp-infix: S:L: invalid character 'C'`        |
| Operand `X` where an operator is expected  | `dp-infix: S:L: unexpected operand 'X'`       |
| Operator `O` where an operand is expected  | `dp-infix: S:L: unexpected operator 'O'`      |
| `(` where an operator is expected          | `dp-infix: S:L: unexpected '('`               |
| `)` where an operand is expected           | `dp-infix: S:L: unexpected ')'`               |
| `)` without a matching `(`                 | `dp-infix: S:L: unmatched ')'`                |
| No token in the line                       | `dp-infix: S:L: empty expression`             |
| The line ends after an operator or `(`     | `dp-infix: S:L: unexpected end of expression` |
| A `(` is still open at the end of the line | `dp-infix: S:L: unmatched '('`                |

Runtime errors that end the run (exit status 1):

| Trigger                                                                     | Exact message                            |
| :-------------------------------------------------------------------------- | :--------------------------------------- |
| Answer line `L` of source `S`, trimmed to `A`, is not `y`, `Y`, `n`, or `N` | `dp-infix: S:L: invalid answer 'A'`      |
| FILE `F` does not exist                                                     | `dp-infix: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                  | `dp-infix: F: Permission denied`         |
| FILE `F` is a directory                                                     | `dp-infix: F: Is a directory`            |
| A component of FILE `F` is not a directory                                  | `dp-infix: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                  | `dp-infix: F: Input/output error`        |
| Any of the above for standard input                                         | the same message with `F` = `-`          |
| Standard output cannot be written (other than a broken pipe)                | `dp-infix: write error`                  |

When `--prompt` is given, a diagnostic follows the last prompt on the same line of standard
error (FR-09).

## 7. Verification

| Method                                                                                    | Applies to                                         |
| :---------------------------------------------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                        | FR-01 … FR-07, FR-09 … FR-11, FR-13, FR-14         |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 04, 06 … 10 have several steps) | FR-01 … FR-14                                      |
| Unit test (written by the implementer)                                                    | FR-03 … FR-06, NFR-06                              |
| Measurement                                                                               | NFR-03                                             |
| Inspection / review                                                                       | FR-08 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                           | Verifies                                                                                                       |
| :--- | :-------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| 01   | `dp-infix readme.txt`             | FR-01, FR-04 (the section's examples), FR-06, FR-07                                                            |
| 02   | `dp-infix < readme.txt`           | FR-01                                                                                                          |
| 03   | `dp-infix mixed.txt`              | FR-02 (CRLF), FR-03 (multi-character operands, blanks, TAB), FR-04 (`%`, left associativity), FR-07 (`Y`, `N`) |
| 04   | `dp-infix --prompt < readme.txt`  | FR-09                                                                                                          |
| 05   | `dp-infix errors.txt`             | FR-05 (the dialog continues; exit 1)                                                                           |
| 06   | `dp-infix stop.txt`               | FR-07 (`n` ends the session; later lines are not read)                                                         |
| 07   | `dp-infix` (empty standard input) | FR-07 (an empty input)                                                                                         |
| 08   | `dp-infix missing.txt`            | FR-10                                                                                                          |
| 09   | `dp-infix --help`                 | FR-11                                                                                                          |
| 10   | `dp-infix readme.txt mixed.txt`   | FR-13, FR-14                                                                                                   |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                      |
| :--------------- | :--------------------------------------- |
| UR-01            | FR-03, FR-04                             |
| UR-02            | FR-03                                    |
| UR-03            | FR-06                                    |
| UR-04            | FR-02, FR-07                             |
| UR-05            | FR-01, CONV-26                           |
| UR-06            | FR-08, NFR-02                            |
| UR-07            | FR-09, CONV-36                           |
| UR-08            | FR-05, CONV-34                           |
| UR-09            | FR-05, FR-07, FR-10, CONV-16             |
| UR-10            | FR-02, NFR-02, CONV-37                   |
| UR-11            | FR-11, FR-12                             |
| UR-12            | FR-13, FR-14                             |
| UR-13            | NFR-01, NFR-02, FR-13, CONV-03, CLI-CONV |
| UR-14            | NFR-03, NFR-07                           |
