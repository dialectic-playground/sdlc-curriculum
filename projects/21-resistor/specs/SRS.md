<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-resistor](#software-requirements-specification-srs--dp-resistor)
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

# Software Requirements Specification (SRS) — dp-resistor

| Field                     | Value                                              |
| :------------------------ | :------------------------------------------------- |
| Document ID               | SRS-21                                             |
| Project                   | `21-resistor` — Resistor 3-Band Color Code Decoder |
| Product                   | `dp-resistor` (canonical name)                     |
| Version                   | 1.0.0                                              |
| Status                    | Approved (pre-written by the curriculum)           |
| Parent document           | `URD.md` (URD-21)                                  |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)       |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018               |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-resistor`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-resistor` writes a guide to the resistor color codes and then conducts a dialog read as
tokens from standard input or from one file: three color codes, the resistance they denote,
an answer whether to decode another resistor, and so on. Each resistance is computed exactly
and written in ohms, kilo-ohms, or mega-ohms with six decimals. Invalid codes are reported and
asked for again; invalid answers, an input that ends in the middle of a resistor, and
unreadable files end the run with fixed diagnostics. Prompts can be written to standard error.

### 1.3 Definitions

| Term                     | Definition                                                                                                                                                        |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                       | The line-feed byte, `0x0A`                                                                                                                                        |
| Input                    | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source                   | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number       | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| End-of-input line number | As defined in CONV-32: 1 plus the number of LF bytes in the whole input                                                                                           |
| Color code               | A token of exactly one byte that is one of the twenty ASCII letters `B N R O Y G E V A W b n r o y g e v a w` (FR-05)                                             |
| Digit value              | The value 0 … 9 that the color table (FR-03) assigns to a color code                                                                                              |
| Code set                 | Three consecutive tokens read as the bands of one resistor (FR-04)                                                                                                |
| Answer                   | The token read after a resistance, which decides whether another resistor is decoded (FR-09)                                                                      |
| Resistance               | The exact integer _R_ computed from a code set (FR-06)                                                                                                            |
| Result line              | The output line for one resistor (FR-07)                                                                                                                          |
| Complete token           | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                |

### 1.4 References

- URD-21: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §4.4 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-resistor` is a standalone executable. Its interfaces are the command line, standard input
or the file named by its operand, standard output, standard error, and the exit status. It
belongs to the curriculum's applications-programming track (Projects 11–52) and adapts §4.4 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Write the color guide.
2. Read code sets as tokens and decode each band through one color table.
3. Compute each resistance exactly and write it in the unit its magnitude calls for.
4. Report invalid color codes and ask for the code set again.
5. Read an answer after each resistance and continue or stop.
6. Optionally write prompts to standard error before each read.
7. Report invalid answers, an input that ends inside a code set, and unreadable input files.
8. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The resistance MUST be computed in exact integer arithmetic (FR-06).

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-11.
- The input may contain any bytes; only the tokens listed in FR-05 are color codes.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §4.4 prints a menu of the color codes, reads the three one-letter codes
of a resistor from the keyboard, rejects an invalid code and asks again, prints the resistance
in ohms, kilo-ohms, or mega-ohms with six decimals, and asks
`Decode another resistor (1 = yes, 0 = no)?`dp-resistor` keeps:

- the ten colors, their one-letter codes (`B N R O Y G E V A W`), and their digit values;
- the formula (10 × first digit + second digit) × 10^third digit, the thresholds 1000 and
  1 000 000 (each inclusive in the larger unit), the unit words `ohms`, `kilo-ohms`, and
  `mega-ohms`, and six decimals (`470.000000 ohms`, `4.700000 kilo-ohms`);
- the dialog: menu first, then codes, resistance, and the answer `1` or `0`, repeated;
- the answer prompt word for word, and re-entry of the codes after an invalid code.

It changes the following, for the reasons given:

- **Exact arithmetic.** The resistance is an exact integer (at most 99 000 000 000), and the
  number written is its exact decimal value in the chosen unit (FR-06), so no implementation
  can differ in the last digit.
- **Tokens.** Each code is one whitespace-separated token (FR-04), so `Y V R` on one line, the
  three codes on three lines, and CRLF files all read the same. Three letters written together
  (`YVR`) form one token, which is not a color code; the textbook's character-by-character
  reading would have accepted it, but token reading keeps each code set aligned with its line
  numbers and lets the diagnostic quote exactly what was typed.
- **Either letter case.** The section describes upper-case codes. Lower-case codes are accepted
  as well and written in upper case (FR-05), because nothing is ambiguous and technicians often
  type in lower case. Case is folded by ASCII rules only, never by the locale (NFR-02).
- **Invalid codes are diagnostics.** The textbook notifies the user and asks again. Here every
  invalid code of a set is reported on standard error in the CONV-34 format, the whole set is
  discarded, and the dialog continues with a new set (FR-08). Standard output therefore holds
  only the guide and correct results, and the exit status tells a script that a code was
  rejected.
- **Invalid answers are fatal.** The textbook does not validate the answer. Here the answer must
  be the integer 0 or 1; anything else is a CONV-34 diagnostic that ends the run (FR-09), rather
  than a guess whether `2` or `yes` means "decode another".
- **End of input is defined everywhere.** The textbook stops only on the answer 0. Here the end
  of the input before a code set or in place of an answer ends the dialog normally, so a file of
  codes needs no final `0`; an end inside a code set is reported (FR-10).
- **Output layout.** The menu is written once, at the start, as a table without blank lines.
  Each result line names the codes it belongs to (`Resistance of Y V R = …`), so redirected
  output can be read without the input beside it (FR-07). Lines that only separated output from
  echoed keyboard input are dropped.
- **Prompts are optional and go to standard error** (FR-12), and each result is flushed before
  more input is read (FR-11).

The section's README states that `B N O` is 10 × 10³ = 10 000 ohms, `10.000000` kilo-ohms. That
is incorrect: black is 0 and brown is 1, so the two digits form 01 and the resistance is
1 × 10³ = 1000 ohms, `1.000000 kilo-ohms` (as the same README correctly states elsewhere, and
as test 06 verifies).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full. From section 10 it incorporates: CONV-32 (the input is
read as tokens; line numbers), CONV-33 (each answer uses the _integer_ grammar, further
restricted to 0 … 1), CONV-34 (data diagnostics, with the standard messages
`invalid integer`, `value out of range`, and `unexpected end of input`, plus the additional
message `invalid color code`), CONV-35 (`FIX(x, 6)` for the resistance), CONV-36 (`-p`,
`--prompt`), and CONV-37 (the input is _text data_). CONV-38 does not apply, because nothing is
random. Option syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the
exit statuses are those of CONV-18. Standard input is read as permitted by CONV-26.
`dp-resistor` copies no input bytes to its output except the bytes of an invalid token quoted in
a diagnostic, so CONV-04 does not otherwise apply.

The only override is the one CONV-34 permits: the diagnostic `invalid color code` does **not**
end processing. The dialog continues (FR-08), and the exit status is 1 at the end of the run.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-resistor [-p | --prompt] [FILE]
dp-resistor --help
dp-resistor --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                   |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-12 to standard error before each read |
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

The color guide (FR-03), then the result lines (FR-07) in input order. Nothing else. On a usage
error, or when `--help` / `--version` is handled, the output is as specified by FR-14 … FR-17
instead.

### 3.6 Standard error

Prompts (FR-12, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when every code set is valid and the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                                                                              |
| :----- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The dialog ended normally (FR-10) and no invalid color code was reported, or `--help` / `--version` was handled                                                                                                        |
| 1      | At least one invalid color code was reported (FR-08), an answer was invalid (FR-09), the input ended inside a code set (FR-10), the input could not be opened or read (FR-13), or standard output could not be written |
| 2      | Usage error (FR-16)                                                                                                                                                                                                    |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `G` denotes the 12 lines of the color guide (FR-03),
and `codes.txt`, `mixed.txt`, `invalid.txt`, `bounds.txt`, and `answer.txt` are the public
fixture files in `tests/fixtures/`: `codes.txt` is `Y V R\n1\nR R B\n1\nN B E\n1\nB N O\n0\n`;
`mixed.txt` is `y v r 1 b\tn\to\r\n1 A w o 1\r\ng B e\r\n0\r\n`; `invalid.txt` is
`Y Q R\nYVR v r\nY V R\n0\n`; `bounds.txt` holds the nine code sets `B B B`, `W W B`, `A W N`,
`B N O`, `A W R`, `W W O`, `W W Y`, `B N E`, `W W W`, one per line, separated by lines holding
`1`, with no answer after the last; `answer.txt` is `Y V R\nyes\nN B E\n0\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the color guide). More than one operand is a usage
error (FR-16).
_AC:_ `dp-resistor < codes.txt`, `dp-resistor codes.txt`, and `dp-resistor - < codes.txt` write
the same output. _(UR-07)_

**FR-02: Tokens.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which the
dialog (FR-04) consumes one at a time, in order. Line structure has no meaning: tokens may be
separated by any mixture of space, TAB, VT, FF, CR, and LF, so several tokens may share a line
and CRLF input reads exactly like LF input. A `0x1A` byte that is followed by any other byte is
ordinary data and belongs to a token.
_AC:_ `dp-resistor mixed.txt` → stdout `G` followed by the result lines for `Y V R`, `B N O`,
`A W O`, and `G B E`, exit 0. _(UR-07, UR-10)_

**FR-03: Color guide.**
After the input has been opened, and before the first token is read or the first prompt is
written, the tool MUST write the color guide to standard output: exactly the following 12
lines, each ending with a single LF, with no trailing spaces (the columns are separated by
spaces only; the code column is 6 characters wide and the color column 8).

```text
Resistor color codes
Code  Color   Value
B     Black   0
N     Brown   1
R     Red     2
O     Orange  3
Y     Yellow  4
G     Green   5
E     Blue    6
V     Violet  7
A     Gray    8
W     White   9
```

The guide is written once per run, whatever the input.
_AC:_ `dp-resistor` with empty standard input → stdout exactly the 12 lines above
(201 bytes), stderr empty, exit 0. _(UR-01)_

**FR-04: Dialog.**
The tool MUST conduct the following dialog until it ends by FR-09 or FR-10:

1. Read a code set: the next three tokens, whatever they contain (the prompt of FR-12 is
   written once, before the first of them). The end of the input is handled by FR-10.
2. Validate the three tokens in order (FR-05). If any of them is not a color code, handle the
   set by FR-08 and continue with step 1.
3. Compute the resistance (FR-06), write the result line (FR-07), and flush standard output.
4. Read an answer (FR-09). If it is 1, continue with step 1; if it is 0, the dialog ends.

Tokens are never reread or skipped: after an invalid code set, the token that follows its third
token is the first token of the next code set. Tokens after the answer that ends the dialog are
neither read as part of the dialog nor validated.
_AC:_ `dp-resistor codes.txt` → stdout `G` followed by
`Resistance of Y V R = 4.700000 kilo-ohms\nResistance of R R B = 22.000000 ohms\nResistance of N B E = 10.000000 mega-ohms\nResistance of B N O = 1.000000 kilo-ohms\n`,
stderr empty, exit 0. _(UR-02, UR-04)_

**FR-05: Color codes.**
A token is a color code if and only if it consists of exactly one byte and that byte is one of
the letters in the color table below, in upper case (`0x41` … `0x5A`) or in the corresponding
lower case (the upper-case byte plus `0x20`). Its digit value is given by the table. Case MUST
be folded by this ASCII rule only, independent of the locale (CONV-06): no other byte, and no
multi-byte character, is a color code.

| Code | Color  | Digit value |
| :--- | :----- | :---------- |
| `B`  | Black  | 0           |
| `N`  | Brown  | 1           |
| `R`  | Red    | 2           |
| `O`  | Orange | 3           |
| `Y`  | Yellow | 4           |
| `G`  | Green  | 5           |
| `E`  | Blue   | 6           |
| `V`  | Violet | 7           |
| `A`  | Gray   | 8           |
| `W`  | White  | 9           |

_AC:_ `y`, `Y` → 4; `e` → 6; `a` → 8; `Q`, `i`, `0`, `YVR`, `BB`, and the two-byte UTF-8 token
`é` are not color codes. _(UR-02, UR-06)_

**FR-06: Resistance.**
For a code set with digit values *d*₁, *d*₂, *d*₃ the resistance MUST be the exact integer
_R_ = (10 × *d*₁ + *d*₂) × 10^*d*₃, so 0 ≤ _R_ ≤ 99 000 000 000. The unit and the number _x_
written are:

| Condition              | _x_             | Unit word   |
| :--------------------- | :-------------- | :---------- |
| _R_ < 1000             | _R_             | `ohms`      |
| 1000 ≤ _R_ < 1 000 000 | _R_ / 1000      | `kilo-ohms` |
| _R_ ≥ 1 000 000        | _R_ / 1 000 000 | `mega-ohms` |

The number is written as `FIX(x, 6)` (CONV-35). Because _R_ is a two-digit number times a power
of ten, _x_ never has more than one significant decimal digit (`8.9`, `3.4`), so the text
written is always the exact decimal value of _x_ with six decimals; an implementation may obtain
it by dividing in binary64 and applying `FIX`, or by integer formatting, with the same result.
The unit word is plural in every case, including `1.000000 kilo-ohms` and `0.000000 ohms`.
_AC:_ `B B B` → `0.000000 ohms`; `W W B` → `99.000000 ohms`; `A W N` → `890.000000 ohms`;
`B N O` → `1.000000 kilo-ohms`; `A W R` → `8.900000 kilo-ohms`; `Y V R` → `4.700000 kilo-ohms`;
`W W Y` → `990.000000 kilo-ohms`; `B N E` → `1.000000 mega-ohms`; `O Y G` →
`3.400000 mega-ohms`; `W W W` → `99000.000000 mega-ohms`. _(UR-02, UR-03)_

**FR-07: Result line.**
The result line for a valid code set MUST be exactly

```text
Resistance of <c1> <c2> <c3> = <x> <unit>
```

followed by a single LF, where `<c1>`, `<c2>`, `<c3>` are the three codes in upper case, in
input order, `<x>` and `<unit>` are as in FR-06, and there are no other spaces: one space
between the codes, one on each side of `=`, one before the unit word, no leading or trailing
spaces.
_AC:_ the code set `g B e` → `Resistance of G B E = 50.000000 mega-ohms\n`. _(UR-03, UR-07)_

**FR-08: Invalid color codes.**
If one or more tokens of a code set are not color codes, the tool MUST write, for each such
token in input order, the diagnostic `dp-resistor: <source>:<line>: invalid color code '<token>'`
to standard error, where `<source>` is as defined in section 1.3, `<line>` is the token's line
number (CONV-32), and `<token>` is the token's exact bytes, without escaping (CONV-34). No
result line and no answer belong to the set; the dialog continues with the next code set
(FR-04 step 1), writing the codes prompt again when prompts are enabled. Reporting an invalid
color code does not end processing (§2.6), but it makes the final exit status 1, however the
dialog ends.
_AC:_ `dp-resistor invalid.txt` → stdout `G` followed by
`Resistance of Y V R = 4.700000 kilo-ohms\n`, stderr
`dp-resistor: invalid.txt:1: invalid color code 'Q'\ndp-resistor: invalid.txt:2: invalid color code 'YVR'\n`,
exit 1. A set whose three tokens are all invalid produces three diagnostics. _(UR-05, UR-09)_

**FR-09: Answers.**
After each result line the tool MUST read one token as the answer. It MUST be a valid
_integer_ (CONV-33) whose value is 0 or 1; signs and leading zeros are allowed (`+1`, `01`, and
`-0` are valid). The value 1 continues the dialog with the next code set; 0 ends it. A token
that is not a valid _integer_ MUST be reported as
`dp-resistor: <source>:<line>: invalid integer '<token>'`, and a valid _integer_ other than 0 or
1 as `dp-resistor: <source>:<line>: value out of range '<token>'`. Either diagnostic ends the
run: no further input is read, nothing more is written to standard output, output already
written is kept, and the exit status is 1.
_AC:_ `dp-resistor answer.txt` → stdout `G` followed by
`Resistance of Y V R = 4.700000 kilo-ohms\n`, stderr
`dp-resistor: answer.txt:2: invalid integer 'yes'\n`, exit 1. An answer `2` gives
`value out of range '2'`; an answer `-0` ends the dialog with exit 0. _(UR-04, UR-09)_

**FR-10: End of input.**
When the end of the input is reached:

- where the first token of a code set is expected, or where an answer is expected, the dialog
  ends normally (an end of input in place of an answer means the same as the answer 0);
- where the second or third token of a code set is expected, the tool MUST write
  `dp-resistor: <source>:<line>: unexpected end of input`, where `<line>` is the end-of-input
  line number (CONV-32), and the exit status is 1.

When the dialog ends normally, the exit status is 0 if no invalid color code was reported
during the run, and 1 otherwise (FR-08). Output already written is always kept. An empty input,
or one that contains only whitespace and a trailing Ctrl-Z run, produces only the color guide.
_AC:_ `dp-resistor - < bounds.txt` → stdout `G` followed by the nine result lines of the FR-06
acceptance values for those sets, exit 0; an input `Y V R\n1\nG B\n` → stdout `G` and the result
line for `Y V R`, stderr `dp-resistor: <source>:4: unexpected end of input\n`, exit 1.
_(UR-04, UR-09)_

**FR-11: Streaming.**
The tool MUST NOT wait for the end of the input before writing a result line. As soon as the
third token of a valid code set is complete (section 1.3), it MUST write the result line and
flush standard output before it waits for any further input bytes. It MUST flush standard
output before every read that may wait for input, so that the color guide and every result
appear before the next prompt. It MUST NOT read the input beyond what it needs to complete the
current token, apart from ordinary buffering of bytes that are already available.
_AC:_ At a terminal, typing `Y V R` and Enter shows the result line before anything else is
typed (manual check). _(UR-08)_

**FR-12: Prompts.**
`-p`, `--prompt` enables the two prompts of this tool:

| Prompt        | Exact bytes (no LF)                                                         | Written                                                                                                                                                                                      |
| :------------ | :-------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Codes prompt  | `Enter the three color codes:29 bytes, ending with one space)               | Once before the first token of every code set is read, including a set that turns out to be invalid and an attempt that reaches the end of the input; never before the second or third token |
| Answer prompt | `Decode another resistor (1 = yes, 0 = no)?43 bytes, ending with one space) | After each result line, before the answer is read                                                                                                                                            |

With prompts enabled, the tool MUST write each prompt to standard error, and flush it,
immediately before the read it belongs to (CONV-36). A prompt is written even if the read
reaches the end of the input. A diagnostic that follows a prompt continues the same line of
standard error. Prompts never change standard output. No prompt is written if the input cannot
be opened.
_AC:_ `dp-resistor --prompt < codes.txt` → stdout as without `--prompt`, stderr the codes prompt
and the answer prompt alternately, four times each, with no LF, exit 0. `dp-resistor -p
invalid.txt` → stderr
`Enter the three color codes: dp-resistor: invalid.txt:1: invalid color code 'Q'\n`
followed by the same for `YVR` on line 2, then
`Enter the three color codes: Decode another resistor (1 = yes, 0 = no)?_(UR-08)_

**FR-13: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-resistor: <source>: <reason>` with `<reason>` from the CONV-16 table,
and exit with status 1. If the input cannot be opened, nothing is written to standard output.
Output already written is kept. When standard input fails, `<source>` is `-`.
_AC:_ `dp-resistor missing.txt` → stderr
`dp-resistor: missing.txt: No such file or directory\n`, stdout empty, exit 1;
`dp-resistor subdir` where `subdir` is a directory → `dp-resistor: subdir: Is a directory`.
_(UR-09)_

**FR-14: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and nothing else is
written.
_AC:_ `dp-resistor --help` matches the user manual exactly; `dp-resistor extra --help` also
prints it. _(UR-11)_

**FR-15: Version.**
`--version` MUST write `dp-resistor (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-11)_

**FR-16: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-resistor: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-resistor codes.txt mixed.txt` → `dp-resistor: extra operand 'mixed.txt'`;
`dp-resistor -x --help` → `dp-resistor: invalid option -- 'x'`; `dp-resistor --prompt=yes` →
`dp-resistor: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-11, UR-13)_

**FR-17: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (in particular not the color guide).
_AC:_ stdout is empty in every exit-2 case; `dp-resistor -p - extra < codes.txt` writes no
prompt. _(UR-11)_

## 5. Non-functional requirements

| ID     | Category                                                                  | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Verification                                                    |
| :----- | :------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                                               | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: locale-independent case folding and console dialogs | Color codes MUST be recognized by comparing bytes, with case folded by the ASCII rule of FR-05 only; library functions whose case mapping depends on the locale or on a code page (for example under a Turkish locale, or a Windows console code page) MUST NOT decide whether a token is a color code. The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output MUST be flushed as FR-11 requires even when it is a pipe or a file, and standard output and standard error MUST be written in binary mode (CONV-03). | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                                               | Decoding 100 000 code sets with answers (about 1 MiB of input) MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of code sets; only the current set is held. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                       | Measurement                                                     |
| NFR-04 | Robustness                                                                | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, non-UTF-8 bytes, and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                                           | Option parsing, the incremental tokenizer, the dialog loop, code decoding, the resistance and unit computation, formatting, and I/O MUST be separate units. The color table MUST be a single data structure that is the only place the codes, color names, and digit values appear; both the color guide (FR-03) and decoding (FR-05) MUST be derived from it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Design review                                                   |
| NFR-06 | Testability                                                               | Decoding, the resistance computation, and the result formatter MUST be pure functions covered by unit tests, including every code in both cases, every acceptance value of FR-06, and each side of both unit thresholds. The dialog MUST be unit-tested for the end of the input at each of the four positions in FR-10 (before the first, second, and third token of a code set, and in place of an answer), and the tokenizer with the input split into reads at every byte position.                                                                                                                                                                                                                                                                                                                                                                                                             | Code review                                                     |
| NFR-07 | Build                                                                     | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | CI                                                              |
| NFR-08 | Security                                                                  | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-resistor --help' for more information.`

| Trigger                                      | Exact first line                                                                          |
| :------------------------------------------- | :---------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-resistor: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-resistor: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-resistor: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-resistor: extra operand 'X'`                                                          |

Data diagnostic that does not stop the dialog (the exit status becomes 1, FR-08):

| Trigger                                                                              | Exact message                              |
| :----------------------------------------------------------------------------------- | :----------------------------------------- |
| Token `K` on line `L` of source `S`, read as part of a code set, is not a color code | `dp-resistor: S:L: invalid color code 'K'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                                                                         | Exact message                               |
| :-------------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| FILE `F` does not exist                                                                                         | `dp-resistor: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                                                      | `dp-resistor: F: Permission denied`         |
| FILE `F` is a directory                                                                                         | `dp-resistor: F: Is a directory`            |
| A component of FILE `F` is not a directory                                                                      | `dp-resistor: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                                                      | `dp-resistor: F: Input/output error`        |
| Any of the above for standard input                                                                             | the same message with `F` = `-`             |
| Answer token `K` on line `L` of source `S` is not a valid _integer_                                             | `dp-resistor: S:L: invalid integer 'K'`     |
| Answer token `K` on line `L` of source `S` is a valid _integer_ other than 0 and 1                              | `dp-resistor: S:L: value out of range 'K'`  |
| The input of source `S` ends after the first or second token of a code set; `L` is the end-of-input line number | `dp-resistor: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)                                                    | `dp-resistor: write error`                  |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-12).

## 7. Verification

| Method                                                                                               | Applies to                                         |
| :--------------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                   | FR-01 … FR-10, FR-12 … FR-14, FR-16, FR-17         |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 04, 05, 06, and 09 have several steps) | FR-02 … FR-17                                      |
| Unit test (written by the implementer)                                                               | FR-04 … FR-07, FR-10, NFR-06                       |
| Measurement                                                                                          | NFR-03                                             |
| Inspection / review                                                                                  | FR-11 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                              | Verifies                                                           |
| :--- | :----------------------------------- | :----------------------------------------------------------------- |
| 01   | `dp-resistor < codes.txt`            | FR-01, FR-03, FR-04, FR-06, FR-07                                  |
| 02   | `dp-resistor mixed.txt`              | FR-02 (lower case, TAB, CRLF, several tokens per line), FR-05      |
| 03   | `dp-resistor invalid.txt`            | FR-08 (diagnostics, set discarded, dialog continues, exit 1)       |
| 04   | `dp-resistor --prompt < codes.txt`   | FR-12                                                              |
| 05   | `dp-resistor` (empty standard input) | FR-03, FR-10                                                       |
| 06   | `dp-resistor - < bounds.txt`         | FR-06 (both thresholds, minimum, maximum), FR-10 (no final answer) |
| 07   | `dp-resistor answer.txt`             | FR-09 (output kept, CONV-34)                                       |
| 08   | `dp-resistor missing.txt`            | FR-13                                                              |
| 09   | `dp-resistor --help`                 | FR-14                                                              |
| 10   | `dp-resistor codes.txt mixed.txt`    | FR-16, FR-17                                                       |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                                   |
| :--------------- | :---------------------------------------------------- |
| UR-01            | FR-03                                                 |
| UR-02            | FR-04, FR-05, FR-06                                   |
| UR-03            | FR-06, FR-07, CONV-35                                 |
| UR-04            | FR-04, FR-09, FR-10                                   |
| UR-05            | FR-08                                                 |
| UR-06            | FR-05, NFR-02                                         |
| UR-07            | FR-01, FR-02, FR-07, CONV-26                          |
| UR-08            | FR-11, FR-12, CONV-36                                 |
| UR-09            | FR-08, FR-09, FR-10, FR-13, CONV-16, CONV-33, CONV-34 |
| UR-10            | FR-02, NFR-02, CONV-37                                |
| UR-11            | FR-14, FR-15, FR-16, FR-17                            |
| UR-12            | NFR-01, NFR-02, CONV-03, CONV-06                      |
| UR-13            | FR-16, CLI-CONV                                       |
| UR-14            | NFR-03, NFR-07                                        |
