<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-taxes](#software-requirements-specification-srs--dp-taxes)
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

# Software Requirements Specification (SRS) — dp-taxes

| Field                     | Value                                                       |
| :------------------------ | :---------------------------------------------------------- |
| Document ID               | SRS-13                                                      |
| Project                   | `13-taxes` — Stream-Based Progressive Income Tax Calculator |
| Product                   | `dp-taxes` (canonical name)                                 |
| Version                   | 1.0.0                                                       |
| Status                    | Approved (pre-written by the curriculum)                    |
| Parent document           | `URD.md` (URD-13)                                           |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                        |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-taxes`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-taxes` reads incomes as integer tokens from standard input or from one file until the end
of the input. For each income it writes a two-line record giving the income and the tax due
under a two-bracket progressive rule, computed exactly in integer arithmetic. It can write a
prompt to standard error before each income is read. It reports invalid incomes with their
line numbers and unreadable files with fixed messages.

### 1.3 Definitions

| Term               | Definition                                                                                                                                                        |
| :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                 | The line-feed byte, `0x0A`                                                                                                                                        |
| Input              | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source             | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Income             | The value _I_ of a token that is a valid _integer_ (CONV-33) with 0 ≤ _I_ ≤ 9223372036854775807 (2⁶³−1)                                                           |
| Tax                | The value _T_ computed from an income by the tax rule (FR-03)                                                                                                     |
| Record             | The two report lines for one income (FR-04)                                                                                                                       |
| Complete token     | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                |
| Decimal            | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                            |

### 1.4 References

- URD-13: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §1.6 (informative; see §2.5)
- SRS-14 (`projects/14-taxes-file/specs/SRS.md`): the batch variant, which specifies the same
  tax rule and record format word for word (FR-03, FR-04)

## 2. Overall description

### 2.1 Product perspective

`dp-taxes` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §1.6 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. Its batch counterpart,
`dp-taxes-file` (Project 14), reads a file and writes a file, using the same tax rule and
record format.

### 2.2 Product functions

1. Read incomes as integer tokens until the end of the input.
2. Compute the tax on each income exactly, under the two-bracket rule.
3. Write one record per income as soon as the income has been read.
4. Optionally write a prompt to standard error before each income is read.
5. Report invalid incomes and unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The tax MUST be computed in exact integer arithmetic (FR-03). Binary floating point MUST NOT
  be used to compute or round it.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-05.
- The input may contain any bytes; only tokens that match the _integer_ grammar are incomes.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §1.6 reads integers from the keyboard until end-of-file and, for each,
prints `Income = … greenbacks` and `Tax = … greenbacks`, taxing incomes below 6000 at 30% and
all others at 60%, with the tax converted to an integer. `dp-taxes` keeps:

- the two-bracket rule, the threshold 6000 (inclusive in the upper bracket), and the two rates;
- the report wording and layout exactly: two lines per income, no blank lines, no header;
- reading until end of input, with the income printed before its tax.

It changes the following, for the reasons given:

- **Exact arithmetic.** The textbook multiplies by the binary floating-point constants 0.30 and
  0.60 and converts the product to an integer. That is exact for every income the textbook
  could hold, but not in general: for incomes above 2⁵³ the binary64 product can differ from
  the true value (0.6 × 10000000000000003 evaluates to 6000000000000002, while the exact tax is
  6000000000000001). FR-03 therefore defines the tax as the exact quotient, rounded down, and
  requires it for every 64-bit income.
- **Negative incomes are rejected.** The textbook computes a negative "tax" for a negative
  income, truncated toward zero. A negative income is not meaningful here, so it is reported as
  `value out of range` (FR-07). This also removes any question about rounding negative
  quotients.
- **Invalid input is diagnosed.** A token that is not an integer stops the textbook program's
  reading loop in an unspecified way (it may never advance past the token). `dp-taxes` reports
  it with its line number and exits with status 1 (FR-07).
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **Prompts are optional and go to standard error.** The section's description shows no prompt
  in the program's output. For interactive use, `-p`, `--prompt` writes `Enter income: ` before
  each income is read (FR-06); without it, nothing is written but the records.
- **Streaming is required.** Each record is written and flushed before more input is read
  (FR-05), so the tool answers immediately at a keyboard even when its output is a pipe.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
_integer_ grammar, further restricted to 0 … 2⁶³−1), CONV-34 (data diagnostics, with the
standard messages `invalid integer` and `value out of range` and the default consequences),
CONV-36 (`-p`, `--prompt`), and CONV-37 (the input is _text data_). CONV-35 does not apply,
because no real number is ever written, and CONV-38 does not apply, because nothing is random.
Option syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit
statuses are those of CONV-18. Standard input is read as permitted by CONV-26. `dp-taxes`
copies no input bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-taxes [-p | --prompt] [FILE]
dp-taxes --help
dp-taxes --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                            |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the prompt `Enter income: ` to standard error before each income is read (FR-06) |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                                         |
| —     | `--version` | none     | —       | Print the version line and exit 0                                                      |

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

The records (FR-04), in input order. Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-09 … FR-12 instead.

### 3.6 Standard error

Prompts (FR-06, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                      |
| :----- | :----------------------------------------------------------------------------------------------------------------------------- |
| 0      | The whole input was processed (including an empty input), or `--help` / `--version` was handled                                |
| 1      | The input could not be opened or read (FR-08), it contained an invalid income (FR-07), or standard output could not be written |
| 2      | Usage error (FR-11)                                                                                                            |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `incomes.txt`, `mixed.txt`, and `bad.txt` are the
public fixture files in `tests/fixtures/`: `incomes.txt` is `5000\n6000\n10000\n`; `mixed.txt`
is `0 5999\t6000\r\n+4500   007\r\n\r\n  12345 1\n`; `bad.txt` is `4500\n6000\n12,000\n9000\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-11).
_AC:_ `dp-taxes < incomes.txt`, `dp-taxes incomes.txt`, and `dp-taxes - < incomes.txt` write
the same records. _(UR-01, UR-04)_

**FR-02: Tokens and incomes.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order. Each token MUST be a valid _integer_ (CONV-33) whose value lies in
0 … 9223372036854775807; that value is the income. A sign (`+5`, `-0`) and leading zeros
(`007`) are allowed. Line structure has no meaning: incomes may be separated by any mixture of
space, TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF input. A token that is not a
valid _integer_, or whose value lies outside that range, is handled by FR-07.
_AC:_ `dp-taxes mixed.txt` writes records for the incomes 0, 5999, 6000, 4500, 7, 12345, and 1,
in that order, exit 0. _(UR-01, UR-09)_

**FR-03: Tax rule.**
For an income _I_ (0 ≤ _I_ ≤ 2⁶³−1) the tax _T_ MUST be

- _T_ = ⌊_I_ × 30 / 100⌋ if _I_ < 6000 (lower bracket), and
- _T_ = ⌊_I_ × 60 / 100⌋ if _I_ ≥ 6000 (upper bracket),

where ⌊_x_⌋ is the largest integer not greater than _x_. _T_ MUST be the exact mathematical
value; since _I_ ≥ 0, rounding down is the same as truncation toward zero. The computation
MUST use integer arithmetic only. It MUST NOT overflow: the product _I_ × 60 exceeds 2⁶³−1 for
_I_ > 153722867280912930, so an implementation that uses 64-bit integers MUST rearrange the
computation, for example as _T_ = _r_ × _q_ + ⌊_r_ × _m_ / 100⌋ with _r_ the rate (30 or 60),
_q_ = ⌊_I_ / 100⌋, and _m_ = _I_ − 100 × _q_. The result always satisfies 0 ≤ _T_ ≤ _I_.
_(This requirement is word for word the same as SRS-14 FR-03.)_
_AC:_ 0 → 0; 1 → 0; 7 → 2; 4500 → 1350; 5000 → 1500; 5995 → 1798; 5999 → 1799; 6000 → 3600;
6009 → 3605; 10000 → 6000; 10000000000000003 → 6000000000000001;
9223372036854775807 → 5534023222112865484. _(UR-02)_

**FR-04: Record format.**
The record for an income _I_ with tax _T_ MUST be exactly the two lines

```text
Income = <I> greenbacks
Tax = <T> greenbacks
```

where `<I>` and `<T>` are the decimals of _I_ and _T_ (section 1.3), each line ends with a
single LF, and there are no other spaces: one space on each side of `=` and one before
`greenbacks`, no leading or trailing spaces. The income is written as its value, not as the
token was spelled: `+4500`, `007`, and `-0` are written as `4500`, `7`, and `0`. Records follow
one another with no blank lines, header, or summary.
_(This requirement is word for word the same as SRS-14 FR-04.)_
_AC:_ `dp-taxes < incomes.txt` → stdout
`Income = 5000 greenbacks\nTax = 1500 greenbacks\nIncome = 6000 greenbacks\nTax = 3600 greenbacks\nIncome = 10000 greenbacks\nTax = 6000 greenbacks\n`,
stderr empty, exit 0. _(UR-02, UR-03)_

**FR-05: Streaming.**
Incomes MUST be processed one at a time, in input order. As soon as a token is complete
(section 1.3) and valid, the tool MUST write its record to standard output and flush standard
output, before it waits for any further input bytes. The tool MUST NOT wait for the end of the
input before writing a record, and MUST NOT read the input beyond what it needs to complete
the current token, apart from ordinary buffering of bytes that are already available. When the
end of the input is reached, the tool exits with status 0. An empty input, or one that contains
only whitespace and a trailing Ctrl-Z run, produces no output and exit status 0.
_AC:_ `dp-taxes` with empty standard input → stdout and stderr empty, exit 0. At a terminal,
typing `5000` and Enter shows the record for 5000 before anything else is typed (manual
check). _(UR-01, UR-05)_

**FR-06: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 14 bytes
`Enter income: ` (ending with one space, no LF). With prompts enabled, the tool MUST write the
prompt to standard error, and flush standard error, immediately before each attempt to read an
income: once before the first token, and once after each record has been written. A prompt is
therefore also written before the attempt that reaches the end of the input (CONV-36): an input
with _n_ valid incomes produces _n_ + 1 prompts, and an input whose _k_-th token is invalid
produces _k_ prompts, the last followed directly by the diagnostic of FR-07 on the same line.
Prompts never change standard output. No prompt is written if the input cannot be opened.
_AC:_ `dp-taxes --prompt < incomes.txt` → stdout as in FR-04, stderr `Enter income: ` four
times with no LF, exit 0. `dp-taxes -p` with empty standard input → stderr `Enter income: `,
stdout empty, exit 0. _(UR-06)_

**FR-07: Invalid incomes.**
If a token is not a valid _integer_ (CONV-33), including an integer outside −2⁶³ … 2⁶³−1, the
tool MUST write `dp-taxes: <source>:<line>: invalid integer '<token>'`. If it is a valid
_integer_ below 0, the tool MUST write `dp-taxes: <source>:<line>: value out of range '<token>'`.
`<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32), and
`<token>` is the token's exact bytes (CONV-34). The tool then stops: it reads no further input,
writes no further record, and exits with status 1. Records already written for earlier incomes
are kept (CONV-34).
_AC:_ `dp-taxes bad.txt` → stdout the records for 4500 and 6000, stderr
`dp-taxes: bad.txt:3: invalid integer '12,000'\n`, exit 1. A token `-1` gives
`value out of range '-1'`; `9223372036854775808` and `4500.50` give `invalid integer`; a token
`4500` followed by a `0x1A` byte and an LF gives `invalid integer` because that Ctrl-Z byte does
not end the input. _(UR-07)_

**FR-08: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-taxes: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Records already written are kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-taxes missing.txt` → stderr `dp-taxes: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-taxes subdir` where `subdir` is a directory →
`dp-taxes: subdir: Is a directory`. _(UR-08)_

**FR-09: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-taxes --help` matches the user manual exactly; `dp-taxes extra --help` also prints it.
_(UR-10)_

**FR-10: Version.**
`--version` MUST write `dp-taxes (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-10)_

**FR-11: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-taxes: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-taxes incomes.txt mixed.txt` → `dp-taxes: extra operand 'mixed.txt'`;
`dp-taxes -x --help` → `dp-taxes: invalid option -- 'x'`; `dp-taxes --prompt=yes` →
`dp-taxes: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-11, UR-13)_

**FR-12: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-taxes -p - extra < incomes.txt` writes no
prompt. _(UR-11)_

## 5. Non-functional requirements

| ID     | Category                                            | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Verification                                                    |
| :----- | :-------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                         | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: end of input and line endings | The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03), and standard output MUST be flushed after each record (FR-05) even when it is a pipe or a file. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                         | Processing 1 000 000 incomes (about 7 MiB of input) MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of incomes; only the token being read is held. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                               | Measurement                                                     |
| NFR-04 | Robustness                                          | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                  | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                     | Option parsing, the incremental tokenizer, income validation, the tax rule, record formatting, and I/O MUST be separate units. The tax rule MUST be one function of the income that is the only place the threshold and the two rates appear.                                                                                                                                                                                                                                                                                                                                                       | Design review                                                   |
| NFR-06 | Testability                                         | The tax function and the record formatter MUST be pure functions covered by unit tests, including every acceptance value of FR-03, the incomes 5999, 6000, 153722867280912930, 153722867280912931, and 2⁶³−1, and a check that _T_ ≤ _I_ for a sample of large incomes. The tokenizer MUST be unit-tested with the input split into reads at every byte position.                                                                                                                                                                                                                                   | Code review                                                     |
| NFR-07 | Build                                               | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | CI                                                              |
| NFR-08 | Security                                            | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                       | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-taxes --help' for more information.`

| Trigger                                      | Exact first line                                                                       |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-taxes: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-taxes: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-taxes: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-taxes: extra operand 'X'`                                                          |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                          | Exact message                            |
| :--------------------------------------------------------------- | :--------------------------------------- |
| FILE `F` does not exist                                          | `dp-taxes: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied       | `dp-taxes: F: Permission denied`         |
| FILE `F` is a directory                                          | `dp-taxes: F: Is a directory`            |
| A component of FILE `F` is not a directory                       | `dp-taxes: F: Not a directory`           |
| Any other open or read failure of FILE `F`                       | `dp-taxes: F: Input/output error`        |
| Any of the above for standard input                              | the same message with `F` = `-`          |
| Token `K` on line `L` of source `S` is not a valid _integer_     | `dp-taxes: S:L: invalid integer 'K'`     |
| Token `K` on line `L` of source `S` is a valid _integer_ below 0 | `dp-taxes: S:L: value out of range 'K'`  |
| Standard output cannot be written (other than a broken pipe)     | `dp-taxes: write error`                  |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-06).

## 7. Verification

| Method                                                                                | Applies to                                         |
| :------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                    | FR-01 … FR-09, FR-11, FR-12                        |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 06 … 10 have several steps) | FR-02 … FR-12                                      |
| Unit test (written by the implementer)                                                | FR-02 … FR-05, NFR-06                              |
| Measurement                                                                           | NFR-03                                             |
| Inspection / review                                                                   | FR-05 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                           | Verifies                                                          |
| :--- | :-------------------------------- | :---------------------------------------------------------------- |
| 01   | `dp-taxes < incomes.txt`          | FR-01, FR-03, FR-04                                               |
| 02   | `dp-taxes incomes.txt`            | FR-01                                                             |
| 03   | `dp-taxes mixed.txt`              | FR-02 (CRLF, TAB, sign, leading zeros), FR-03 (boundaries), FR-04 |
| 04   | `dp-taxes - < mixed.txt`          | FR-01, FR-02                                                      |
| 05   | `dp-taxes --prompt < incomes.txt` | FR-06                                                             |
| 06   | `dp-taxes` (empty standard input) | FR-05                                                             |
| 07   | `dp-taxes bad.txt`                | FR-07 (records kept, CONV-34)                                     |
| 08   | `dp-taxes missing.txt`            | FR-08                                                             |
| 09   | `dp-taxes --help`                 | FR-09                                                             |
| 10   | `dp-taxes incomes.txt mixed.txt`  | FR-11, FR-12                                                      |

## 8. Traceability (URD → SRS)

| User requirement | System requirements     |
| :--------------- | :---------------------- |
| UR-01            | FR-01, FR-02, FR-05     |
| UR-02            | FR-03, FR-04            |
| UR-03            | FR-04                   |
| UR-04            | FR-01, CONV-26          |
| UR-05            | FR-05, NFR-02           |
| UR-06            | FR-06, CONV-36          |
| UR-07            | FR-07, CONV-33, CONV-34 |
| UR-08            | FR-08, CONV-16          |
| UR-09            | FR-02, NFR-02, CONV-37  |
| UR-10            | FR-09, FR-10            |
| UR-11            | FR-11, FR-12            |
| UR-12            | NFR-01, NFR-02, CONV-03 |
| UR-13            | FR-11, CLI-CONV         |
| UR-14            | NFR-03, NFR-07          |
