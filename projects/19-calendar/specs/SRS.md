<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-calendar](#software-requirements-specification-srs--dp-calendar)
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

# Software Requirements Specification (SRS) — dp-calendar

| Field                     | Value                                               |
| :------------------------ | :-------------------------------------------------- |
| Document ID               | SRS-19                                              |
| Project                   | `19-calendar` — Formatted Annual Calendar Generator |
| Product                   | `dp-calendar` (canonical name)                      |
| Version                   | 1.0.0                                               |
| Status                    | Approved (pre-written by the curriculum)            |
| Parent document           | `URD.md` (URD-19)                                   |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)        |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-calendar`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-calendar` reads pairs of integer tokens — a day code (the weekday of January 1) and a
leap-year code — from standard input or from one file, until it reads a pair whose day code is
valid; each pair with an invalid day code is reported and skipped. It then writes a calendar
of the twelve months in a fixed text grid. Alternatively, `--year` derives the two codes from a
Gregorian year and no input is read. The tool can write a prompt to standard error before each
pair is read, and it reports malformed input and unreadable files with fixed messages.

### 1.3 Definitions

| Term                 | Definition                                                                                                                                                        |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                   | The line-feed byte, `0x0A`                                                                                                                                        |
| Input                | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source               | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number   | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Complete token       | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                |
| Attempt              | One reading of a pair: a day-code token followed by a leap-year-code token (FR-02)                                                                                |
| Day code (_c_)       | The weekday of January 1: 0 = Sunday, 1 = Monday, …, 6 = Saturday                                                                                                 |
| Leap-year code (_L_) | 1 for a leap year, 0 for a common year                                                                                                                            |
| Weekday number       | 0 = Sunday, 1 = Monday, …, 6 = Saturday; the weekday number of a day is its column in the grid                                                                    |
| Decimal              | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros, no digit grouping (CONV-06)                                          |
| _x_ mod 7            | The remainder in 0 … 6 (all operands in this SRS are non-negative)                                                                                                |

### 1.4 References

- URD-19: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §3.6 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-calendar` is a standalone executable. Its interfaces are the command line, standard input
or the file named by its operand, standard output, standard error, and the exit status. It
belongs to the curriculum's applications-programming track (Projects 11–52) and adapts §3.6 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Read attempts (a day code and a leap-year code) until one has a valid day code, reporting
   and skipping each attempt whose day code is invalid.
2. Alternatively, derive the two codes from a Gregorian year (`--year`).
3. Compute the length and the first weekday of each month.
4. Write the twelve months as a text grid.
5. Optionally write a prompt to standard error before each attempt.
6. Report malformed input and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The calendar MUST be computed from the two codes alone, by the rules of FR-05 and FR-11. The
  tool MUST NOT consult the system clock, the time zone, the locale, or a platform calendar
  library.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only the tokens of the attempts are examined.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §3.6 prompts `Enter day and leap year codes:reads two integers,
prompts again while the day code is outside 0 … 6, and prints each month as its name, the
header `Sun Mon Tue Wed Thu Fri Sat`, and the days in 2-character fields aligned under the
weekday names, breaking the line after each Saturday; the next month's day code is the previous
one plus the month's length, modulo 7. `dp-calendar` keeps:

- the two codes and their meanings, and the rule that February has 29 days exactly when the
  leap-year code is 1;
- the prompt text, and asking again after an invalid day code (FR-03);
- the month names, the header text, and the column positions of the days: day 1 of a month
  that begins on weekday _w_ is preceded by 1 + 5*w* spaces and written in a 2-character field,
  that is, every day number is right-aligned under the last letter of its weekday's name;
- the blank line between each month name and its header, and the carrying forward of the
  weekday from month to month.

It changes the following, for the reasons given:

- **No trailing spaces, no stray lines.** The textbook writes three spaces after every day that
  is not a Saturday (so every month's last line, and the lines of months that end mid-week,
  carry trailing spaces), and writes a line break followed by a space after every Saturday (so
  a month that ends on a Saturday leaves a line holding a single space). FR-06 removes every
  trailing space and every empty week line, so the calendar can be compared, pasted, and
  printed cleanly.
- **Blank lines that only separated output from typed input are dropped.** The textbook's
  output begins with blank lines after the echoed codes. The calendar now begins with
  `January`, and consecutive months are separated by exactly one empty line (FR-06).
- **The re-prompt loop is defined for any input.** The textbook re-reads after an invalid day
  code with no message, and its behavior when the input ends, or holds something other than
  integers, is undefined (it may loop forever). `dp-calendar` reports each invalid day code with
  its line number and reads the next pair, so a keyboard user can simply type again and a file
  of answers behaves the same way (FR-03); the end of the input and malformed tokens end the
  run with a CONV-34 diagnostic (FR-09).
- **The leap-year code is validated.** The textbook treats every value other than 1 as a
  common year. A value other than 0 or 1 is now reported as `value out of range` (FR-04),
  because it is almost certainly a typing mistake.
- **Prompts are optional and go to standard error** (FR-08), so standard output holds only the
  calendar.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **`--year` is added** as a convenience (FR-11). The textbook interface remains primary:
  `--year` produces exactly the calendar of the corresponding codes.

The section's README shows the calendar's second and later week lines one column to the right
of the first line and of the header (`nstead of `6 7`)Tharendering is
inconsistent with its own rule (a line break and one space, then a 2-character field); FR-06
follows the rule, which keeps every day under its weekday name.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (both codes use the
_integer_ grammar, further restricted as stated in FR-03 and FR-04), CONV-34 (data diagnostics,
with the standard messages `invalid integer`, `value out of range`, and `unexpected end of
input`, and one further message, `invalid day code`, which — as CONV-34 permits an SRS to say —
does **not** end processing; FR-03), CONV-36 (`-p`, `--prompt`), and CONV-37 (the input is
_text data_). CONV-35 does not apply, because no real number is ever written, and CONV-38 does
not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12, diagnostics
follow CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. `dp-calendar` copies no input bytes to its output, so CONV-04 does not
apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-calendar [-p | --prompt] [FILE]
dp-calendar [-p | --prompt] (-y YEAR | --year=YEAR)
dp-calendar --help
dp-calendar --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                                  |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the prompt `Enter day and leap year codes:o standard error before each attempt (FR-08) |
| `-y`  | `--year`    | YEAR     | none    | Print the calendar of the Gregorian year YEAR instead of reading codes (FR-11)               |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                                               |
| —     | `--version` | none     | —       | Print the version line and exit 0                                                            |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once; if `--year` is repeated, the last
value is used (CONV-11).

### 3.3 Operands

Without `--year`, at most one FILE operand; with `--year`, none. The operand `-` denotes
standard input (CONV-10). Every token after `--` is an operand, even if it begins with `-`. The
operand is used and echoed exactly as given (CONV-19).

### 3.4 Standard input

Read when `--year` is not given and no operand is given or the operand is `-` (FR-01). Read as
raw bytes; no newline translation of any kind is performed on any platform.

### 3.5 Standard output

The calendar (FR-06). Nothing else. Nothing is written to standard output unless a valid pair
has been read (or `--year` was given). On a usage error, or when `--help` / `--version` is
handled, the output is as specified by FR-12 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-08, only with `--prompt`), the `invalid day code` diagnostics of FR-03, and the
diagnostics that end the run (section 6). Without `--prompt`, nothing is written to standard
error when the first attempt is valid.

### 3.7 Exit status

| Status | Condition                                                                                                                                                                                         |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0      | The calendar was written (also when attempts with an invalid day code were skipped before it), or `--help` / `--version` was handled                                                              |
| 1      | The input could not be opened or read (FR-10), it ended or contained a malformed token or an invalid leap-year code before a valid pair was read (FR-09), or standard output could not be written |
| 2      | Usage error (FR-14)                                                                                                                                                                               |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\t` TAB, and `\r` CR. The public fixture files in
`tests/fixtures/` are: `tue.txt` = `2 0\n`; `retry.txt` = `9 0\n-1 1\n2 0\n`; `sat.txt` =
`6\t1\r\n`; `bad.txt` = `2\nzero\n`; `leapbad.txt` = `2 2\n`.

**FR-01: Input source.**
Unless `--year` is given (FR-11), the tool reads its input: standard input if no operand is
given or the operand is `-`, otherwise the file named by the operand, read as raw bytes. The
input is opened before anything is written (in particular before the first prompt). More than
one operand is a usage error (FR-14).
_AC:_ `dp-calendar < tue.txt`, `dp-calendar tue.txt`, and `dp-calendar - < tue.txt` write the
same calendar. _(UR-01, UR-06)_

**FR-02: Tokens and attempts.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
consumed in order, two per attempt. Line structure has no meaning: the two tokens of an attempt
may share a line or not, and CRLF input reads exactly like LF input. One attempt consists of
these steps, in this order:

1. If prompts are enabled, write the prompt (FR-08).
2. Take the next token as the day-code token. If there is none, the input has ended early
   (FR-09). If it is not a valid _integer_ (CONV-33), report it (FR-09).
3. Take the next token as the leap-year-code token. If there is none, the input has ended early
   (FR-09). If it is not a valid _integer_, report it (FR-09).
4. If the day code is outside 0 … 6, reject the attempt (FR-03) and start the next attempt.
5. If the leap-year code is neither 0 nor 1, report it (FR-04, FR-09).
6. Otherwise the attempt is accepted: the codes are _c_ and _L_.

A sign and leading zeros are allowed (`-0` and `+1` are the codes 0 and 1; `006` is 6).
_AC:_ `dp-calendar sat.txt` writes the same calendar as `--year 2000` (_c_ = 6, _L_ = 1); an
input `-0 +1\n` is accepted as _c_ = 0, _L_ = 1; an input `6 0\r\n` followed by two `0x1A`
bytes is accepted as _c_ = 6, _L_ = 0. _(UR-01, UR-11)_

**FR-03: Invalid day codes are skipped.**
When step 4 of FR-02 rejects an attempt, the tool MUST write
`dp-calendar: <source>:<line>: invalid day code '<token>'` to standard error, where `<line>` is
the line number of the day-code token and `<token>` its exact bytes, and then start the next
attempt (writing the prompt again if prompts are enabled). The leap-year-code token of a
rejected attempt is consumed, but its value is not checked against 0 … 1. There is no limit on
the number of rejected attempts. Rejected attempts do not affect the exit status: if a later
attempt is accepted, the calendar is written and the exit status is 0. If the input ends or a
fatal error of FR-09 occurs in a later attempt, that error ends the run with status 1, after
the `invalid day code` diagnostics already written.
_AC:_ `dp-calendar --prompt < retry.txt` → stdout the calendar of `tue.txt`, stderr
`Enter day and leap year codes: dp-calendar: -:1: invalid day code '9'\nEnter day and leap year codes: dp-calendar: -:2: invalid day code '-1'\nEnter day and leap year codes:
exit 0. _(UR-05)_

**FR-04: Leap-year code.**
The leap-year code of an attempt whose day code is valid MUST be 0 or 1; 1 means a leap year.
Any other valid _integer_ is reported as `value out of range` (FR-09).
_AC:_ `dp-calendar leapbad.txt` → stderr `dp-calendar: leapbad.txt:1: value out of range '2'\n`,
stdout empty, exit 1. _(UR-04, UR-09)_

**FR-05: Months.**
The months, in order, are January, February, March, April, May, June, July, August, September,
October, November, and December, with lengths 31, 28 + _L_, 31, 30, 31, 30, 31, 31, 30, 31, 30,
and 31 days. The weekday number of January 1 is _c_. The weekday number of the first day of each
later month is (_f_ + _n_) mod 7, where _f_ is the weekday number of the first day of the
previous month and _n_ that month's length. Within a month whose first day has weekday number
_f_, day _d_ has weekday number (_f_ + _d_ − 1) mod 7.
_AC:_ with _c_ = 2 and _L_ = 0, February begins on weekday 5 (Friday), August on weekday 4
(Thursday), and December 31 falls on weekday 2 (Tuesday); with _c_ = 1 and _L_ = 1, February
has 29 days and March begins on weekday 5 (Friday). _(UR-04)_

**FR-06: Calendar layout.**
The calendar MUST consist of twelve month blocks, January first, separated by exactly one empty
line (a single LF). There is no empty line before January or after December. Every line ends
with a single LF, and no line has leading spaces other than those specified below or any
trailing spaces. A month block consists of:

1. the month name (as in FR-05, with that capitalization) on a line by itself;
2. an empty line;
3. the header line `Sun  Mon  Tue  Wed  Thu  Fri  Sat` (each name followed by two spaces, the
   last by none: 33 bytes);
4. the week lines.

Each day _d_ of the month is written as its _cell_: the decimal of _d_ right-aligned in a field
of 3 characters, padded on the left with spaces (`1).A eek line holds the cells of
consecutive days from the first day of the month or a Sunday, up to and including the next
Saturday or the last day of the month, whichever comes first. A week line consists of 5 × _w_
spaces, where _w_ is the weekday number of its first day, followed by its cells separated by two
spaces. Consequently _w_ is 0 for every week line but the first, and the cell of a day with
weekday number _w_ occupies columns 5*w* + 1 … 5*w* + 3 (counting from 1), so its last digit lies
under the last letter of its weekday's name. A line ends immediately after its last cell; a
month that ends on a Saturday therefore has no empty or blank week line after its last week.
_AC:_ `dp-calendar < tue.txt` → exit 0, stderr empty, stdout of 109 lines (2450 bytes) that
begins

```text
January

Sun  Mon  Tue  Wed  Thu  Fri  Sat
            1    2    3    4    5
  6    7    8    9   10   11   12
 13   14   15   16   17   18   19
 20   21   22   23   24   25   26
 27   28   29   30   31

February
```

(the first week line is 12 spaces and `1    2    3    4    5`), whose August block ends with
the line `  26   27   28   29   30   31` followed by the empty line and `September`, and whose
last line is `  30   31`. _(UR-02, UR-03)_

**FR-07: Reading.**
The tool MUST read the input only as far as it needs to complete the tokens of its attempts
(section 1.3), apart from ordinary buffering of bytes that are already available. As soon as the
leap-year-code token of an attempt is complete, the tool MUST decide the attempt; when it is
accepted, it MUST write the calendar without waiting for the end of the input, so a user who
types `2 0` and Enter at a terminal sees the calendar at once. Bytes after the accepted
attempt's last token are not examined: they need not form valid tokens, and they cause no
diagnostic. Nothing is written to standard output before an attempt has been accepted, so a
run that ends with a diagnostic of FR-09 writes nothing to standard output.
_AC:_ an input `1 0 garbage\n` gives the calendar for _c_ = 1, _L_ = 0 with exit status 0. At
a terminal, typing `2 0` and Enter shows the calendar and ends the tool (manual check).
_(UR-01, UR-09)_

**FR-08: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 31 bytes
`Enter day and leap year codes:ending with one space, no LF). With prompts enabled, the
tool MUST write the prompt to standard error, and flush standard error, at the start of each
attempt (step 1 of FR-02): once before the first token is read, and once more after each
rejected attempt's diagnostic. A prompt is written even if the input then ends (CONV-36); a
diagnostic that follows a prompt continues the same line. Prompts never change standard output.
No prompt is written if the input cannot be opened, on a usage error, or with `--year`.
_AC:_ `dp-calendar --prompt < retry.txt`→ stderr as in FR-03 (three prompts); with a file`onlybad.txt`=`7 0\n`, `dp-calendar -p onlybad.txt`→ stdout empty, stderr`Enter day and leap year codes: dp-calendar: onlybad.txt:1: invalid day code '7'\n`followed by`Enter day and leap year codes: dp-calendar: onlybad.txt:2: unexpected end of input\n`, exit 1.
_(UR-08)_

**FR-09: Errors that end the run.**
The tool MUST write one of the following diagnostics, write nothing to standard output, and
exit with status 1:

- the input has no further token where step 2 or step 3 of FR-02 needs one:
  `dp-calendar: <source>:<line>: unexpected end of input`, where `<line>` is the end-of-input
  line number (CONV-32);
- a day-code or leap-year-code token is not a valid _integer_ (CONV-33), including an integer
  outside −2⁶³ … 2⁶³−1: `dp-calendar: <source>:<line>: invalid integer '<token>'`;
- the leap-year code of an attempt with a valid day code is neither 0 nor 1:
  `dp-calendar: <source>:<line>: value out of range '<token>'`.

`<source>` is as defined in section 1.3, `<line>` is the token's line number unless stated
otherwise, and `<token>` is the token's exact bytes (CONV-34). Diagnostics of FR-03 written
before the fatal one are kept.
_AC:_ `dp-calendar bad.txt` → stderr `dp-calendar: bad.txt:2: invalid integer 'zero'\n`,
stdout empty, exit 1; `dp-calendar` with empty standard input →
`dp-calendar: -:1: unexpected end of input`; an input `3\n` → `unexpected end of input` on
line 2; `99999999999999999999 0` → `invalid integer '99999999999999999999'`; `6 0` followed by
a `0x1A` byte and an LF → `invalid integer '0<0x1A>'`, because that Ctrl-Z byte does not end
the input. _(UR-09)_

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-calendar: <source>: <reason>` with `<reason>` from the CONV-16 table,
write nothing to standard output, and exit with status 1. When standard input fails,
`<source>` is `-`.
_AC:_ `dp-calendar missing.txt` → stderr
`dp-calendar: missing.txt: No such file or directory\n`, stdout empty, exit 1;
`dp-calendar subdir` where `subdir` is a directory → `dp-calendar: subdir: Is a directory`.
_(UR-10)_

**FR-11: Calendar of a Gregorian year.**
With `-y YEAR`, `--year=YEAR`, the tool MUST NOT read any input and MUST NOT write a prompt.
YEAR MUST consist only of ASCII digits (leading zeros allowed) and denote a value _Y_ with
1 ≤ _Y_ ≤ 9999; any other value, including an empty one or one with a sign, is an invalid option
value (CONV-13, FR-14). The codes are derived from _Y_ in the proleptic Gregorian calendar,
with _y_ = _Y_ − 1:

- _c_ = (1 + 5 × (_y_ mod 4) + 4 × (_y_ mod 100) + 6 × (_y_ mod 400)) mod 7;
- _L_ = 1 if _Y_ is divisible by 4 and either not divisible by 100 or divisible by 400;
  otherwise _L_ = 0.

The tool then writes the calendar for _c_ and _L_ exactly as FR-06 specifies; the output does
not show the year, so `--year` and the corresponding codes give identical bytes. Exit status 0.
_AC:_ the codes are (1, 0) for 1, (1, 0) for 1900, (6, 1) for 2000, (0, 1) for 2012, (2, 0) for
2019, (1, 1) for 2024, and (5, 0) for 9999; `dp-calendar --year 2024` writes the same bytes as
an input `1 1`, and `dp-calendar --year 2012` the same as `0 1`. _(UR-07)_

**FR-12: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-calendar --help` matches the user manual exactly; `dp-calendar extra --help` also
prints it. _(UR-12)_

**FR-13: Version.**
`--version` MUST write `dp-calendar (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-12)_

**FR-14: Usage errors.**
The following MUST be reported with the CONV-13 messages followed by the CONV-14 line, with exit
status 2: unknown options; arguments supplied to options that take none (`--prompt=…`,
`--help=…`, `--version=…`); `-y` or `--year` without a value; an invalid YEAR (FR-11), reported
as `dp-calendar: invalid argument '<YEAR>' for '<option>'` with the option as written (`-y` or
`--year`); with `--year`, any operand, reported as `dp-calendar: extra operand '<first
operand>'`; without `--year`, a second operand, reported as `dp-calendar: extra operand
'<second operand>'`. Long options MUST NOT be abbreviated (CONV-08). The value of YEAR and the
operands are checked after the whole argument list has been scanned (CONV-12), YEAR first. When
a usage error occurs, the tool MUST NOT open the operand, read standard input, write a prompt,
or write anything to standard output.
_AC:_ `dp-calendar --year 0` → `dp-calendar: invalid argument '0' for '--year'`;
`dp-calendar -y +2024` → `dp-calendar: invalid argument '+2024' for '-y'`;
`dp-calendar --year 2024 tue.txt` → `dp-calendar: extra operand 'tue.txt'`;
`dp-calendar tue.txt retry.txt` → `dp-calendar: extra operand 'retry.txt'`; `dp-calendar -y` →
`dp-calendar: option requires an argument -- 'y'`; `dp-calendar -x --help` →
`dp-calendar: invalid option -- 'x'`; each followed by the CONV-14 line, stdout empty, exit 2.
_(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                                       | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Verification                                                    |
| :----- | :------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                                    | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: an exact text grid and interactive input | The grid MUST be built from explicit spaces only (never TAB characters or terminal cursor movement) and written in binary mode, so a Windows console, a Unix pipe, and a file receive the same bytes; no line may carry trailing spaces, which some editors and version-control settings strip or flag. The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the tool MUST answer as soon as a valid pair is entered (FR-07); the platform's end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) given instead MUST produce the `unexpected end of input` diagnostic, not a hang or a crash. Standard error MUST be flushed after each prompt and each `invalid day code` diagnostic. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                                    | A run with `--year`, or whose input holds at most 100 attempts, MUST finish in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Reading an input of 1 000 000 rejected attempts (about 4 MiB) MUST take under 2 s native (20 s interpreted) and MUST NOT need memory that grows with the number of attempts.                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Measurement                                                     |
| NFR-04 | Robustness                                                     | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                                | Option parsing, reading attempts, validation, the year-to-codes rule, month computation, grid formatting, and I/O MUST be separate units. The month names and lengths MUST be defined in one table, and the header text and the cell width in one place each. The function that formats a month MUST depend only on the month's name, length, and first weekday.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Design review                                                   |
| NFR-06 | Testability                                                    | The calendar formatter MUST be a pure function of (_c_, _L_), covered by unit tests for all 14 combinations, including checks that no line has trailing spaces, that every day appears exactly once, and that the cell of each day lies under its weekday's name. The year-to-codes rule MUST be a pure function, unit-tested for every year in 1 … 9999 against an independent oracle (for example, counting days from a known date, or a platform calendar used only in the test).                                                                                                                                                                                                                                                                                                                                                                                                                                              | Code review                                                     |
| NFR-07 | Build                                                          | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | CI                                                              |
| NFR-08 | Security                                                       | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables or the system clock, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-calendar --help' for more information.`

| Trigger                                                        | Exact first line                                                                          |
| :------------------------------------------------------------- | :---------------------------------------------------------------------------------------- |
| Unknown short option `x`                                       | `dp-calendar: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T`                   | `dp-calendar: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`                        | `dp-calendar: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| `-y` without a value                                           | `dp-calendar: option requires an argument -- 'y'`                                         |
| `--year` without a value                                       | `dp-calendar: option '--year' requires an argument`                                       |
| Invalid YEAR `V` given with option `O` (`-y` or `--year`)      | `dp-calendar: invalid argument 'V' for 'O'`                                               |
| An operand `X` together with `--year` (the first such operand) | `dp-calendar: extra operand 'X'`                                                          |
| A second operand `X` without `--year`                          | `dp-calendar: extra operand 'X'`                                                          |

Warnings (written to standard error; the run continues, and they do not affect the exit
status):

| Trigger                                                                             | Exact message                            |
| :---------------------------------------------------------------------------------- | :--------------------------------------- |
| The day-code token `K` on line `L` of source `S` is a valid _integer_ outside 0 … 6 | `dp-calendar: S:L: invalid day code 'K'` |

Runtime errors (exit status 1; the tool stops at the first one and writes nothing to standard
output):

| Trigger                                                                                                                              | Exact message                               |
| :----------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| FILE `F` does not exist                                                                                                              | `dp-calendar: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                                                                           | `dp-calendar: F: Permission denied`         |
| FILE `F` is a directory                                                                                                              | `dp-calendar: F: Is a directory`            |
| A component of FILE `F` is not a directory                                                                                           | `dp-calendar: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                                                                           | `dp-calendar: F: Input/output error`        |
| Any of the above for standard input                                                                                                  | the same message with `F` = `-`             |
| Source `S` ends where a code is needed; `L` is its end-of-input line number                                                          | `dp-calendar: S:L: unexpected end of input` |
| A code token `K` on line `L` of source `S` is not a valid _integer_                                                                  | `dp-calendar: S:L: invalid integer 'K'`     |
| The leap-year-code token `K` on line `L` of source `S`, in an attempt with a valid day code, is a valid _integer_ other than 0 and 1 | `dp-calendar: S:L: value out of range 'K'`  |
| Standard output cannot be written (other than a broken pipe)                                                                         | `dp-calendar: write error`                  |

When `--prompt` is given, each `invalid day code` warning and the final data diagnostic follow
a prompt on the same line of standard error (FR-08).

## 7. Verification

| Method                                                                               | Applies to                                         |
| :----------------------------------------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                   | FR-01 … FR-06, FR-08 … FR-12, FR-14                |
| Black-box test (hidden, `tests/private/`, 10 cases; several have more than one step) | FR-02, FR-03, FR-05 … FR-11, FR-13, FR-14          |
| Unit test (written by the implementer)                                               | FR-02 … FR-06, FR-11, NFR-06                       |
| Measurement                                                                          | NFR-03                                             |
| Inspection / review                                                                  | FR-07 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                              | Verifies                                                            |
| :--- | :----------------------------------- | :------------------------------------------------------------------ |
| 01   | `dp-calendar < tue.txt`              | FR-01, FR-05, FR-06 (the README example; August ends on a Saturday) |
| 02   | `dp-calendar --year 2024`            | FR-05 (leap February), FR-06, FR-11                                 |
| 03   | `dp-calendar --prompt < retry.txt`   | FR-03, FR-08                                                        |
| 04   | `dp-calendar sat.txt`                | FR-01, FR-02 (TAB, CRLF), FR-05, FR-06 (January 1 on a Saturday)    |
| 05   | `dp-calendar bad.txt`                | FR-09 (invalid integer, line number)                                |
| 06   | `dp-calendar` (empty standard input) | FR-09 (unexpected end of input)                                     |
| 07   | `dp-calendar leapbad.txt`            | FR-04, FR-09                                                        |
| 08   | `dp-calendar missing.txt`            | FR-10                                                               |
| 09   | `dp-calendar --help`                 | FR-12                                                               |
| 10   | `dp-calendar --year 0`               | FR-11, FR-14                                                        |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                     |
| :--------------- | :-------------------------------------- |
| UR-01            | FR-01, FR-02, FR-07                     |
| UR-02            | FR-06                                   |
| UR-03            | FR-06, NFR-02                           |
| UR-04            | FR-04, FR-05                            |
| UR-05            | FR-03                                   |
| UR-06            | FR-01, CONV-26                          |
| UR-07            | FR-11                                   |
| UR-08            | FR-08, CONV-36                          |
| UR-09            | FR-04, FR-07, FR-09, CONV-33, CONV-34   |
| UR-10            | FR-10, CONV-16                          |
| UR-11            | FR-02, NFR-02, CONV-37                  |
| UR-12            | FR-12, FR-13, FR-14, CLI-CONV           |
| UR-13            | NFR-01, NFR-02, NFR-03, NFR-07, CONV-03 |
