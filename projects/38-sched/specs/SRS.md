<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-sched](#software-requirements-specification-srs--dp-sched)
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

# Software Requirements Specification (SRS) — dp-sched

| Field                     | Value                                            |
| :------------------------ | :----------------------------------------------- |
| Document ID               | SRS-38                                           |
| Project                   | `38-sched` — Greedy Interval Activity Scheduling |
| Product                   | `dp-sched` (canonical name)                      |
| Version                   | 1.0.0                                            |
| Status                    | Approved (pre-written by the curriculum)         |
| Parent document           | `URD.md` (URD-38)                                |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)     |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018             |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-sched`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-sched` reads activities from the file named by its operand or from standard input, one per
fixed-width line (start time in columns 1–5, finish time in columns 6–10), checks every line,
sorts the activities by finish time, selects a largest set of mutually compatible activities
with the greedy rule, and writes a heading followed by the selected lines exactly as they
appear in the input.

### 1.3 Definitions

| Term         | Definition                                                                                                                                                                                                                                                                     |
| :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR       | The bytes `0x0A` and `0x0D`                                                                                                                                                                                                                                                    |
| Input        | The byte sequence read from the file named by the operand, or from standard input when the operand is `-`                                                                                                                                                                      |
| Source       | The operand exactly as given (so `-` for standard input), used in diagnostics                                                                                                                                                                                                  |
| Line         | A maximal run of bytes other than LF, terminated by an LF or by the end of the input. An input that ends with an LF has no empty line after that LF; an empty input has no lines. The _line number_ of a line is 1 plus the number of LF bytes before its first byte (CONV-32) |
| Text         | A line with one CR at its end removed, if present (FR-02)                                                                                                                                                                                                                      |
| Field        | Bytes 1–5 (the start field) or bytes 6–10 (the finish field) of a text, counted from 1                                                                                                                                                                                         |
| Activity     | A valid text together with its start time _s_ and finish time _f_ (FR-03), and its position in the input (1 for the first line)                                                                                                                                                |
| Compatible   | Activities _a_ and _b_ are compatible if _s_(_b_) ≥ _f_(_a_) or _s_(_a_) ≥ _f_(_b_): an activity occupies the half-open interval [_s_, _f_)                                                                                                                                    |
| Sorted order | The activities ordered by ascending finish time; activities with equal finish times keep their input order (FR-04)                                                                                                                                                             |
| Schedule     | The activities selected by FR-05, in the order they are selected                                                                                                                                                                                                               |

### 1.4 References

- URD-38: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §7.9 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-sched` is a standalone executable. Its interfaces are the command line, the input file or
standard input, standard output, standard error, and the exit status. It belongs to the
curriculum's applications-programming track (Projects 11–52) and adapts §7.9 of Johnsonbaugh &
Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Read the input named by the operand.
2. Check every line before any output is produced.
3. Sort the activities by finish time, keeping input order among equal finish times.
4. Select activities greedily and write the heading and the selected lines.
5. Report unreadable input and malformed lines; display help and version information; detect
   and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, except for the design requirement of
  NFR-05, which is checked by design review.

### 2.4 Assumptions

- The input may contain any bytes; only lines in the format of FR-03 are activities.
- Times are abstract whole units (for example minutes or hours); the tool attaches no meaning
  to them beyond their order.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §7.9 reads the file named by its first command-line argument, in which
each line holds a start time in columns 1–5 and a finish time in columns 6–10, sorts the lines
by finish time with a general-purpose string-sorting routine that compares a chosen substring
of each line, selects activities greedily (the first in sorted order, then every activity whose
start time is not before the finish time of the last one selected), and prints
`Optimal schedule:`, a blank line, and the selected lines as they were read. `dp-sched` keeps:

- the line format, the required file operand, and the greedy rule, including that an activity
  may start at the very time the previous one finishes;
- the report exactly: the heading `Optimal schedule:`, one blank line, and the selected lines
  byte for byte as they appear in the input (without their line endings), in the order they
  are selected. The blank line is kept because it is part of the report itself, not a
  separator from echoed keyboard input: the program reads no keyboard input.

It changes the following, for the reasons given:

- **A specified tie rule.** The textbook's sort, a quicksort, is not stable, so when several
  activities finish at the same time, which of them is selected depended on the sort's
  internal order.
  The number of activities selected is the same either way, but the lines printed are not.
  FR-04 requires a stable order (input order among equal finish times), so every
  implementation prints the same schedule.
- **The section's expected result for `sched.in` is wrong.** Its description lists the
  schedule `1 5`, `5 7`, `10 14`, `13 16`, but `10 14` and `13 16` overlap (13 < 14), so that
  is not a schedule at all. The greedy rule selects `   `9 `,
and ` after `5 7`, the activity `6 10` is rejected (6 < 7), `9 12` is the next
  compatible activity to finish, and `6 14` and `10 14` are rejected (both start before 12).
  Four activities is the maximum. The acceptance criteria of this SRS were computed with the
  curriculum's reference model, not copied from the description.
- **Lines are checked** (FR-03). The section's description specifies no behavior for
  malformed lines; here every line must be exactly ten bytes, each field must hold a whole
  number from 0 to 99999, and the finish time must be later than the start time. A malformed
  line is reported with its line number, and no report is written (FR-06). The textbook's
  limit of 100 activities is removed.
- **Standard input** can be named with the operand `-`, and an empty input yields a report with
  no activities rather than undefined behavior; data files with CRLF line endings and a
  trailing Ctrl-Z marker are accepted (FR-02).
- **Failures are diagnosed** with the CONV-13, CONV-16, and CONV-34 messages (FR-06, FR-07,
  FR-10); the section's description specifies no behavior for a missing argument or a file
  that cannot be opened.
- **No prompts.** The textbook program reads only its file, so the tool has no prompts and does
  not accept `-p` (CONV-36 does not apply).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (only its definition of line numbers; the input is fixed-width, not read
as tokens), CONV-33 (each field, without its padding spaces, uses the _integer_ grammar, further
restricted to 0 … 99999), CONV-34 (data diagnostics, with the standard messages
`invalid integer` and `value out of range` and three messages of this tool's own; because of
FR-06, no report has been produced when one is written), and CONV-37 (the input is _text
data_). CONV-35 does not apply, because no real number is written; CONV-36 does not apply,
because the tool has no prompts; CONV-38 does not apply, because nothing is random. Option
syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit statuses
are those of CONV-18. Standard input is read only when the operand is `-` (CONV-26). Selected
lines are copied to standard output byte for byte, except that a CR at the end of a line is
removed (FR-02); this is the "unless the SRS says otherwise" case of CONV-04.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-sched FILE
dp-sched --help
dp-sched --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                       |
| :---- | :---------- | :------- | :------ | :-------------------------------- |
| —     | `--help`    | none     | —       | Print the help text and exit 0    |
| —     | `--version` | none     | —       | Print the version line and exit 0 |

Option syntax (`--` and scan order) follows CONV-07 … CONV-12.

### 3.3 Operands

Exactly one FILE operand, which is required. The operand `-` denotes standard input
(CONV-10). Every token after `--` is an operand, even if it begins with `-`. The operand is used
and echoed exactly as given (CONV-19).

### 3.4 Standard input

Read only when the operand is `-` (FR-01). Read as raw bytes; no newline translation of any
kind is performed on any platform.

### 3.5 Standard output

The report (FR-05) when the input is valid; otherwise nothing. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-08 … FR-11 instead.

### 3.6 Standard error

Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition                                                                                                           |
| :----- | :------------------------------------------------------------------------------------------------------------------ |
| 0      | The report was written (including a report with no activities), or `--help` / `--version` was handled               |
| 1      | The input could not be read (FR-07), it contained a malformed line (FR-06), or standard output could not be written |
| 2      | Usage error (FR-10)                                                                                                 |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `␣` denotes one space where spaces must be counted,
and the following are public fixture files in `tests/fixtures/`: `sched.in` is the textbook's
file of nine activities (from the companion disk; it has no final LF), in this order: 6 10,
1 5, 1 6, 9 12, 5 7, 6 14, 3 7, 10 14, 13 16, each written as two right-justified 5-byte fields;
`ties.in` holds, in the same format, 1 2, 4 6, 2 6, 6 9, 0 3, each line ending with LF;
`empty.in` is empty; `bad.in` is `1    5\n    1  six\n    9   12\n`.

**FR-01: Input.**
If the operand is `-`, the tool MUST read standard input to its end. Otherwise it MUST open the
file named by the operand (a path relative to the current directory unless absolute) and read
it to its end as raw bytes.
_AC:_ `dp-sched sched.in` and `dp-sched - < sched.in` write the same report. _(UR-01)_

**FR-02: Lines.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into lines (section 1.3). From each
line, one CR at its end, if present, is removed; the result is the line's text. A last line
without a terminating LF is a line like any other. An input with no lines (empty, or only a
Ctrl-Z run) has no activities and is valid.
_AC:_ `sched.in`, which has no final LF, yields nine activities; a file of CRLF lines followed by
a Ctrl-Z byte reads like the same file with LF lines; a last line `␣␣␣␣1␣␣␣␣3\r` without LF is
the activity 1 3. _(UR-02, UR-07)_

**FR-03: Line format.**
Every text MUST be exactly 10 bytes long. Its start field (bytes 1–5) and finish field
(bytes 6–10) are each interpreted as follows: the spaces (`0x20`) at both ends of the field
are removed, and what remains MUST be non-empty and a valid _integer_ (CONV-33) whose value
lies in 0 … 99999; that value is the start time _s_ or the finish time _f_. Only the space byte
is padding: a TAB or any other byte is part of the integer and makes it invalid. Fields are
normally right-justified (`␣␣␣12`), but left-justified or centred values (`12␣␣␣`, `␣12␣␣`), a
sign (`␣␣+12`), and leading zeros (`00012`) are accepted, and the two fields need no space
between them (`0000500010` is the activity 5 10). Finally, _f_ MUST be greater than _s_. The
checks are made in this order — length, start field, finish field, _f_ > _s_ — and the first
that fails is reported by FR-06.
_AC:_ each line of `sched.in` is valid; a file whose lines are `5␣␣␣␣10␣␣␣`, `+0001+0002`,
`00000␣␣␣␣1`, `␣␣␣12␣␣+13`, and `10␣␣␣12␣␣␣` holds the activities 5 10, 1 2, 0 1, 12 13, and
10 12. _(UR-02)_

**FR-04: Sorted order.**
After every line has been checked, the activities MUST be put in sorted order: ascending finish
time, and, among activities with equal finish times, ascending position in the input (a stable
sort). Start times play no part in the order.
_AC:_ the sorted order of `sched.in` is 1 5, 1 6, 5 7, 3 7, 6 10, 9 12, 6 14, 10 14, 13 16.
_(UR-05)_

**FR-05: Greedy selection and report.**
The tool MUST select activities by scanning the sorted order once: the first activity is
selected; each later activity is selected if its start time is greater than or equal to the
finish time of the activity selected most recently, and rejected otherwise. The selected
activities are pairwise compatible, and no compatible set is larger. The tool MUST then write
the report: the line `Optimal schedule:` (no trailing space) and LF, an empty line (a single
LF), and then, for each selected activity in the order of selection, its 10-byte text exactly as
it appears in the input (FR-02) followed by LF. Nothing else is written: no count, no trailing
blank line. With no activities, the report is the heading and the empty line only.
_AC:_ `dp-sched sched.in` → stdout
`Optimal schedule:\n\n    1    5\n    5    7\n    9   12\n   13   16\n`, stderr empty, exit 0
(see §2.5 about the section's description). `dp-sched ties.in` → selects 1 2, then 4 6 (which
precedes 2 6 in the input, so 2 6 is rejected), then 6 9, which starts when 4 6 finishes:
`Optimal schedule:\n\n    1    2\n    4    6\n    6    9\n`. `dp-sched empty.in` →
`Optimal schedule:\n\n`, exit 0. _(UR-03, UR-04, UR-05)_

**FR-06: Malformed lines.**
The whole input MUST be checked before any output is written. For the first line that violates
FR-03, the tool MUST write `dp-sched: <source>:<line>: <message>`, where `<line>` is the line
number and `<message>` is:

- `invalid line length <n>, expected 10`, where `<n>` is the text's length in bytes, in
  decimal, if the text is not 10 bytes long (an empty line in the middle of the input, or after
  the final LF, has length 0; a line holding only a `0x1A` byte followed by an LF has length 1);
- `missing start time` or `missing finish time` if the field consists only of spaces;
- `invalid integer '<value>'` if the field, without its padding spaces, is not a valid
  _integer_, where `<value>` is exactly those bytes (CONV-34);
- `value out of range '<value>'` if it is a valid _integer_ below 0 (for example `-1`);
- `finish time is not later than start time` if _f_ ≤ _s_.

The tool then exits with status 1 and writes nothing to standard output.
_AC:_ `dp-sched bad.in` → stdout empty, stderr `dp-sched: bad.in:3: invalid integer 'six'\n`,
exit 1. A line `␣␣␣␣5␣␣␣␣␣` gives `missing finish time`; `␣␣1.5␣␣␣␣3` gives
`invalid integer '1.5'`; `␣␣␣-1␣␣␣␣3` gives `value out of range '-1'`; `␣␣␣␣5␣␣␣␣5` gives
`finish time is not later than start time`; a line with one trailing space gives
`invalid line length 11, expected 10`. _(UR-06, UR-08)_

**FR-07: Unreadable input.**
If the file named by the operand does not exist, cannot be opened, is a directory, or a read
error occurs, the tool MUST write `dp-sched: <source>: <reason>` with `<reason>` from the
CONV-16 table, and exit with status 1 without writing to standard output.
_AC:_ `dp-sched missing.in` → stderr `dp-sched: missing.in: No such file or directory\n`,
stdout empty, exit 1; `dp-sched subdir`, where `subdir` is a directory →
`dp-sched: subdir: Is a directory`; `dp-sched -- -x` → `dp-sched: -x: No such file or
directory`. _(UR-08)_

**FR-08: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
_AC:_ `dp-sched --help` matches the user manual exactly; `dp-sched extra --help` also prints it.
_(UR-09)_

**FR-09: Version.**
`--version` MUST write `dp-sched (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-sched missing.in --version` also prints it and exits 0. _(UR-09)_

**FR-10: Usage errors.**
Unknown options (including `-p` and `--prompt`, which this tool does not have) and arguments
supplied to `--help` or `--version` MUST be reported with the CONV-13 messages followed by the
CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--he` is
unrecognized. If no operand is given, the tool MUST report `dp-sched: missing operand`; if more
than one is given, `dp-sched: extra operand '<second operand>'`. Operands are checked after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-sched` → `dp-sched: missing operand`; `dp-sched --` → the same;
`dp-sched sched.in ties.in` → `dp-sched: extra operand 'ties.in'`; `dp-sched -p sched.in` →
`dp-sched: invalid option -- 'p'`; `dp-sched --help=all` →
`dp-sched: option '--help' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-10, UR-12)_

**FR-11: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, or write
anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-10)_

## 5. Non-functional requirements

| ID     | Category                                                       | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Verification                              |
| :----- | :------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| NFR-01 | Portability                                                    | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: fixed columns and deterministic ordering | The input MUST be read in binary mode on every platform, so that column positions are counted in bytes exactly as stored: a CRLF line MUST reach the line check with its CR (which FR-02 then removes), a `0x1A` byte MUST never be treated as end-of-file by the I/O layer, and the selected lines MUST be written without their CR, so a CRLF input gives the same report as an LF input. The sorted order MUST NOT depend on the platform's or the language's library sort: if a library sort is used, it MUST be one documented as stable, or the input position MUST be used as a secondary key, because unstable sorts differ between C libraries and runtimes and would select different lines for the same input. Integer conversion MUST NOT depend on locale. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                                    | Processing an input of 1 000 000 activities (about 11 MiB) MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 256 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). The sort MUST take O(_n_ log _n_) time; memory MAY grow linearly with the input, because the whole input is checked before any output is written (FR-06). Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                     | Measurement                               |
| NFR-04 | Robustness                                                     | The tool MUST NOT crash, panic, or print a stack trace for any argument list, input bytes, or file-system condition (CONV-24), including lines of any length and inputs with no lines. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Unit + black-box tests                    |
| NFR-05 | Maintainability                                                | Option parsing, line reading and checking, the sort, the greedy selection, report formatting, and I/O MUST be separate units. As in the textbook, the sort MUST be a general-purpose routine that knows nothing about activities: it receives the items and an ordering (a key or comparison function) as parameters. The selection MUST be one function of the sorted activities that is the only place the compatibility rule appears. The column widths MUST be defined once.                                                                                                                                                                                                                                                                                        | Design review                             |
| NFR-06 | Testability                                                    | The line parser, the sort, and the selection function MUST be pure functions covered by unit tests, including: no activities, one activity, all activities overlapping, activities that touch (_s_ = previous _f_), equal finish times in several input orders (checking the tie rule), the largest time 99999, and every message of FR-06. A unit test MUST check, for many small random inputs, that the number of activities selected equals the maximum found by exhaustive search.                                                                                                                                                                                                                                                                                 | Code review                               |
| NFR-07 | Build                                                          | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | CI                                        |
| NFR-08 | Security                                                       | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Inspection                                |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-sched --help' for more information.`

| Trigger                                      | Exact first line                                                         |
| :------------------------------------------- | :----------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-sched: invalid option -- 'x'`                                        |
| Unknown or abbreviated long option token `T` | `dp-sched: unrecognized option 'T'`                                      |
| `--help=…` / `--version=…`                   | `dp-sched: option '--help' doesn't allow an argument` (or `'--version'`) |
| No operand                                   | `dp-sched: missing operand`                                              |
| A second operand `X`                         | `dp-sched: extra operand 'X'`                                            |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                                            | Exact message                                             |
| :--------------------------------------------------------------------------------- | :-------------------------------------------------------- |
| FILE `F` does not exist                                                            | `dp-sched: F: No such file or directory`                  |
| FILE `F` cannot be opened or read because access is denied                         | `dp-sched: F: Permission denied`                          |
| FILE `F` is a directory                                                            | `dp-sched: F: Is a directory`                             |
| A component of FILE `F` is not a directory                                         | `dp-sched: F: Not a directory`                            |
| Any other open or read failure of FILE `F`                                         | `dp-sched: F: Input/output error`                         |
| Any of the above for standard input                                                | the same message with `F` = `-`                           |
| The text of line `L` of source `S` is `N` bytes long, not 10                       | `dp-sched: S:L: invalid line length N, expected 10`       |
| The start field of line `L` is all spaces                                          | `dp-sched: S:L: missing start time`                       |
| The finish field of line `L` is all spaces                                         | `dp-sched: S:L: missing finish time`                      |
| A field of line `L`, without its padding spaces, is `V`, not a valid _integer_     | `dp-sched: S:L: invalid integer 'V'`                      |
| A field of line `L`, without its padding spaces, is `V`, a valid _integer_ below 0 | `dp-sched: S:L: value out of range 'V'`                   |
| The finish time of line `L` is not greater than its start time                     | `dp-sched: S:L: finish time is not later than start time` |
| Standard output cannot be written (other than a broken pipe)                       | `dp-sched: write error`                                   |

## 7. Verification

| Method                                                                                            | Applies to                  |
| :------------------------------------------------------------------------------------------------ | :-------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                | FR-01 … FR-08, FR-10, FR-11 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 05 and 07 … 10 have several steps) | FR-01 … FR-11               |
| Unit test (written by the implementer)                                                            | FR-03 … FR-05, NFR-06       |
| Measurement                                                                                       | NFR-03                      |
| Inspection / review                                                                               | NFR-02, NFR-05, NFR-08      |

Public test map:

| Test | Command                     | Verifies                                      |
| :--- | :-------------------------- | :-------------------------------------------- |
| 01   | `dp-sched sched.in`         | FR-01 … FR-05 (textbook data, no final LF)    |
| 02   | `dp-sched - < sched.in`     | FR-01 (standard input)                        |
| 03   | `dp-sched ties.in`          | FR-04 (tie rule), FR-05 (touching activities) |
| 04   | `dp-sched empty.in`         | FR-02, FR-05 (no activities)                  |
| 05   | `dp-sched bad.in`           | FR-03, FR-06 (nothing written)                |
| 06   | `dp-sched missing.in`       | FR-07                                         |
| 07   | `dp-sched --help`           | FR-08                                         |
| 08   | `dp-sched`                  | FR-10 (missing operand), FR-11                |
| 09   | `dp-sched sched.in ties.in` | FR-10 (extra operand), FR-11                  |
| 10   | `dp-sched -p sched.in`      | FR-10 (no prompts), FR-11                     |

## 8. Traceability (URD → SRS)

| User requirement | System requirements     |
| :--------------- | :---------------------- |
| UR-01            | FR-01, CONV-26          |
| UR-02            | FR-02, FR-03            |
| UR-03            | FR-05                   |
| UR-04            | FR-05                   |
| UR-05            | FR-04, NFR-02           |
| UR-06            | FR-03, FR-06, CONV-34   |
| UR-07            | FR-02, NFR-02, CONV-37  |
| UR-08            | FR-06, FR-07, CONV-16   |
| UR-09            | FR-08, FR-09            |
| UR-10            | FR-10, FR-11            |
| UR-11            | NFR-01, NFR-02, CONV-03 |
| UR-12            | FR-10, CLI-CONV         |
| UR-13            | NFR-03, NFR-07          |
