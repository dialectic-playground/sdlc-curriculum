<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-convert](#software-requirements-specification-srs--dp-convert)
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

# Software Requirements Specification (SRS) — dp-convert

| Field                     | Value                                             |
| :------------------------ | :------------------------------------------------ |
| Document ID               | SRS-12                                            |
| Project                   | `12-convert` — Interactive Length Unit Conversion |
| Product                   | `dp-convert` (canonical name)                     |
| Version                   | 1.0.0                                             |
| Status                    | Approved (pre-written by the curriculum)          |
| Parent document           | `URD.md` (URD-12)                                 |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)      |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018              |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-convert`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-convert` reads lengths in yards as integer tokens from standard input or from one file. For
each non-negative length it writes a three-line block giving the length in yards, feet, and
inches. The first negative value is the sentinel: the tool writes `*** END OF PROGRAM ***` and
stops without reading further. It can write a prompt to standard error before each value is
read. It reports invalid values and an input that ends before the sentinel with line numbers,
and unreadable files with fixed messages.

### 1.3 Definitions

| Term                                         | Definition                                                                                                                                                                                                                                                                     |
| :------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                                           | The line-feed byte, `0x0A`                                                                                                                                                                                                                                                     |
| Input                                        | The byte sequence read from standard input or from the FILE operand                                                                                                                                                                                                            |
| Source                                       | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)                                                                                                                            |
| Token, line number, end-of-input line number | As defined in CONV-32: a token is a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`; its line number is the number of LF bytes before its first byte, plus 1; the end-of-input line number is the number of LF bytes in the whole input, plus 1 |
| Value                                        | The integer _V_ of a token that is a valid _integer_ (CONV-33), −2⁶³ ≤ _V_ ≤ 2⁶³−1                                                                                                                                                                                             |
| MAX_YARDS                                    | 256204778801521550, the largest _Y_ for which 36 × _Y_ ≤ 2⁶³−1 (that is, ⌊(2⁶³−1) / 36⌋)                                                                                                                                                                                       |
| Length                                       | A value _Y_ with 0 ≤ _Y_ ≤ MAX_YARDS                                                                                                                                                                                                                                           |
| Sentinel                                     | A value _V_ < 0. `-0` has the value 0 and is a length, not a sentinel                                                                                                                                                                                                          |
| Block                                        | The three report lines for one length (FR-04)                                                                                                                                                                                                                                  |
| Banner                                       | The 22 bytes `*** END OF PROGRAM ***` followed by LF                                                                                                                                                                                                                           |
| Complete token                               | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                                                                                                                             |
| Decimal                                      | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                                                                                                                                         |

### 1.4 References

- URD-12: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §1.2 (informative; see §2.5)
- SRS-13 (`projects/13-taxes/specs/SRS.md`): a streaming tool of the same track that reads to
  the end of the input instead of to a sentinel

## 2. Overall description

### 2.1 Product perspective

`dp-convert` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §1.2 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Read values as integer tokens, one at a time, until the sentinel.
2. Convert each length exactly to feet and inches and write its block as soon as it is read.
3. On the sentinel, write the banner and stop without reading further.
4. Optionally write a prompt to standard error before each value is read.
5. Report invalid values, an input that ends before the sentinel, and unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Conversions MUST be computed in exact integer arithmetic (FR-03).

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-06.
- The input may contain any bytes; only tokens that match the _integer_ grammar are values.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §1.2 prompts `Enter next lengthreads a number of yards, prints it
as yards, feet, and inches, and repeats until a negative number is entered, when it prints
`*** END OF PROGRAM ***`. `dp-convert` keeps:

- the conversion factors (3 feet and 36 inches to the yard) and integer lengths;
- the sentinel rule: any negative number ends the loop, and is not converted; a negative
  number as the first value ends the program without any conversion;
- the report wording exactly: `<Y> yd =`, `<F> ft`, `<I> in`, and the banner
  `*** END OF PROGRAM ***`, each on its own line;
- the prompt text `Enter next lengthwritten before every value is read, including the one
  that turns out to be the sentinel.

It changes the following, for the reasons given:

- **No blank line before each block.** In the section's sample dialog, a blank line separates
  each block from the typed length above it. That line exists only to separate the output from
  the keyboard echo; in a redirected report it is noise. Each block is therefore exactly three
  lines, and blocks and the banner follow one another without blank lines (FR-04).
- **Prompts are optional and go to standard error.** `-p`, `--prompt` writes the textbook's
  prompt to standard error (FR-08); without it, nothing is written but the report, so standard
  output is the same for a keyboard and a file.
- **A stated range.** The textbook computes with its C implementation's integers, whose range
  is implementation-defined (ANSI C guarantees only up to 32767, so 36 × yards may overflow
  above 910 yards); the section's description asks only for "reasonable inputs". `dp-convert`
  uses 64-bit arithmetic and accepts lengths up to MAX_YARDS, the largest whose inches fit in
  64 bits; larger lengths are reported as `value out of range` (FR-09).
- **End of input without the sentinel is diagnosed.** The section does not say what happens
  when the input ends before a negative number; a reading loop that never checks for the end of
  the input repeats or stalls. `dp-convert` reports `unexpected end of input` and exits with
  status 1 (FR-07), so that a truncated input file is noticed. The banner is not written in
  that case, because the program did not end the way it was asked to.
- **Invalid input is diagnosed.** A token that is not an integer is reported with its line
  number, and the tool exits with status 1 (FR-09).
- **Nothing after the sentinel is read.** The sentinel ends the input: tokens after it are
  neither read nor validated (FR-05), and the tool exits at once at a keyboard.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
_integer_ grammar; non-negative values are further restricted to 0 … MAX_YARDS), CONV-34 (data
diagnostics, with the standard messages `invalid integer`, `value out of range`, and
`unexpected end of input` and the default consequences), CONV-36 (`-p`, `--prompt`), and
CONV-37 (the input is _text data_). CONV-35 does not apply, because no real number is ever
written, and CONV-38 does not apply, because nothing is random. Option syntax follows
CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of
CONV-18. Standard input is read as permitted by CONV-26. `dp-convert` copies no input bytes to
its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-convert [-p | --prompt] [FILE]
dp-convert --help
dp-convert --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                           |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompt `Enter next lengtho standard error before each value is read (FR-08) |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                                        |
| —     | `--version` | none     | —       | Print the version line and exit 0                                                     |

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

The blocks (FR-04), in input order, followed by the banner when the sentinel is read (FR-05).
Nothing else. On a usage error, or when `--help` / `--version` is handled, the output is as
specified by FR-11 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-08, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                           |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0      | The sentinel was read and the banner written, or `--help` / `--version` was handled                                                                                 |
| 1      | The input could not be opened or read (FR-10), it contained an invalid value (FR-09), it ended before the sentinel (FR-07), or standard output could not be written |
| 2      | Usage error (FR-13)                                                                                                                                                 |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `lengths.txt`, `mixed.txt`, `nosentinel.txt`, and
`bad.txt` are the public fixture files in `tests/fixtures/`: `lengths.txt` is `5\n0\n-1\n`;
`mixed.txt` is `+3 007\t1760\r\n-0\r\n\r\n  100 -5 junk\n`; `nosentinel.txt` is `12\n36\n`;
`bad.txt` is `10\n2.5\n-1\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
_AC:_ `dp-convert < lengths.txt`, `dp-convert lengths.txt`, and `dp-convert - < lengths.txt`
write the same output. _(UR-01, UR-05)_

**FR-02: Tokens and values.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order, one at a time, as FR-05 … FR-07 describe. Each token that is processed MUST
be a valid _integer_ (CONV-33); its value is either a length (0 … MAX_YARDS) or a sentinel
(below 0). A sign (`+3`, `-0`) and leading zeros (`007`) are allowed. Line structure has no
meaning: values may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF
input reads exactly like LF input. A token that is not a valid _integer_, or a non-negative
value above MAX_YARDS, is handled by FR-09.
_AC:_ `dp-convert mixed.txt` writes blocks for the lengths 3, 7, 1760, 0, and 100, in that
order, then the banner, exit 0. _(UR-01, UR-11)_

**FR-03: Conversion.**
For a length _Y_ (0 ≤ _Y_ ≤ MAX_YARDS), the number of feet MUST be _F_ = 3 × _Y_ and the
number of inches MUST be _I_ = 36 × _Y_, computed exactly in integer arithmetic. The limit
MAX_YARDS guarantees that _I_ ≤ 9223372036854775800 < 2⁶³, so a 64-bit signed implementation
cannot overflow.
_AC:_ 0 → 0 ft, 0 in; 5 → 15 ft, 180 in; 1760 → 5280 ft, 63360 in; 256204778801521550 →
768614336404564650 ft, 9223372036854775800 in. _(UR-02)_

**FR-04: Block format.**
The block for a length _Y_ MUST be exactly the three lines

```text
<Y> yd =
<F> ft
<I> in
```

where `<Y>`, `<F>`, and `<I>` are the decimals of _Y_, _F_, and _I_ (section 1.3), each line
ends with a single LF, and there are no other spaces: one space between the number and the
unit, one space before `=`, no leading or trailing spaces. The length is written as its value,
not as the token was spelled: `+3`, `007`, and `-0` are written as `3`, `7`, and `0`. Blocks
follow one another, and the banner follows the last block, with no blank lines, header, or
summary.
_AC:_ `dp-convert < lengths.txt` → stdout
`5 yd =\n15 ft\n180 in\n0 yd =\n0 ft\n0 in\n*** END OF PROGRAM ***\n`, stderr empty, exit 0.
_(UR-01, UR-02)_

**FR-05: Sentinel.**
When a processed token is a valid _integer_ below 0 (any value from −2⁶³ to −1), the tool MUST
write the banner to standard output and exit with status 0. The sentinel is not converted. The
tool MUST NOT read the input beyond the end of the sentinel's token, apart from ordinary
buffering of bytes that are already available, and MUST NOT examine, validate, or report any
token after it. A sentinel as the first token produces only the banner.
_AC:_ `dp-convert mixed.txt` ends with the banner after the block for 100, although the token
`junk` follows the sentinel `-5`, exit 0; a file `7 -9223372036854775808\n` → the block for 7
and the banner, exit 0. _(UR-03, UR-04, UR-06)_

**FR-06: Streaming.**
Values MUST be processed one at a time, in input order. As soon as a token is complete
(section 1.3) and is a valid length, the tool MUST write its block to standard output and flush
standard output, before it waits for any further input bytes. When the sentinel's token is
complete, the banner is written and the tool exits without waiting for further input. The tool
MUST NOT wait for the end of the input before writing a block.
_AC:_ at a terminal, typing `5` and Enter shows the block for 5 before anything else is typed,
and typing `-1` and Enter ends the program at once (manual check). _(UR-06)_

**FR-07: End of input before the sentinel.**
If the end of the input is reached when the next value is needed — that is, before any
sentinel has been read — the tool MUST write
`dp-convert: <source>:<line>: unexpected end of input`, where `<line>` is the end-of-input line
number (CONV-32), and exit with status 1. The banner MUST NOT be written. Blocks already
written are kept (CONV-34). An empty input, or one that contains only whitespace and a trailing
Ctrl-Z run, is reported in the same way.
_AC:_ `dp-convert nosentinel.txt` → stdout the blocks for 12 and 36, stderr
`dp-convert: nosentinel.txt:3: unexpected end of input\n`, exit 1; `dp-convert` with empty
standard input → stdout empty, stderr `dp-convert: -:1: unexpected end of input\n`, exit 1.
_(UR-08)_

**FR-08: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 18 bytes
`Enter next lengthending with one space, no LF). With prompts enabled, the tool MUST write
the prompt to standard error, and flush standard error, immediately before each attempt to read
a value: once before the first token, and once after each block has been written. No prompt is
written after the banner. A prompt is also written before an attempt that reaches the end of
the input (CONV-36). Therefore an input with _n_ lengths followed by the sentinel produces
_n_ + 1 prompts; an input with _n_ lengths and no sentinel produces _n_ + 1 prompts, the last
followed directly by the diagnostic of FR-07 on the same line; and an input whose _k_-th token
is invalid produces _k_ prompts, the last followed directly by the diagnostic of FR-09. Prompts
never change standard output. No prompt is written if the input cannot be opened.
_AC:_ `dp-convert --prompt < lengths.txt`→ stdout as in FR-04, stderr`Enter next length
three times with no LF, exit 0. `dp-convert -p` with empty standard input → stderr
`Enter next length dp-convert: -:1: unexpected end of input\n`, stdout empty, exit 1.
_(UR-07)_

**FR-09: Invalid values.**
If a processed token is not a valid _integer_ (CONV-33), including an integer outside
−2⁶³ … 2⁶³−1, the tool MUST write `dp-convert: <source>:<line>: invalid integer '<token>'`. If
it is a valid _integer_ greater than MAX_YARDS, the tool MUST write
`dp-convert: <source>:<line>: value out of range '<token>'`. `<source>` is as defined in
section 1.3, `<line>` is the token's line number (CONV-32), and `<token>` is the token's exact
bytes (CONV-34). The tool then stops: it reads no further input, writes no further block and no
banner, and exits with status 1. Blocks already written for earlier lengths are kept (CONV-34).
A token below −2⁶³ is an invalid integer, not a sentinel.
_AC:_ `dp-convert bad.txt` → stdout the block for 10, stderr
`dp-convert: bad.txt:2: invalid integer '2.5'\n`, exit 1. `256204778801521551` gives
`value out of range '256204778801521551'`; `9223372036854775808` and `yd` give
`invalid integer`. _(UR-02, UR-09)_

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-convert: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Blocks already written are kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-convert missing.txt` → stderr `dp-convert: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-convert subdir` where `subdir` is a directory →
`dp-convert: subdir: Is a directory`. _(UR-10)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-convert --help` matches the user manual exactly; `dp-convert extra --help` also
prints it. _(UR-12)_

**FR-12: Version.**
`--version` MUST write `dp-convert (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-12)_

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-convert: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-convert lengths.txt mixed.txt` → `dp-convert: extra operand 'mixed.txt'`;
`dp-convert -x --help` → `dp-convert: invalid option -- 'x'`; `dp-convert --prompt=yes` →
`dp-convert: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-12, UR-13)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-convert -p - extra < lengths.txt` writes no
prompt. _(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                            | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Verification                                                    |
| :----- | :-------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                         | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: an interactive console dialog | Each prompt MUST be flushed to standard error, and each block and the banner to standard output, before the tool blocks on input, on every platform and whether or not the streams are terminals, so the dialog never stalls behind a buffer. The tool MUST stop reading as soon as the sentinel's token is complete (at a keyboard: when Enter is pressed after it), and MUST NOT wait for an end-of-input signal; when the input does end early, the platform's own signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST be recognized as the end of the input. The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. Standard output and standard error MUST be written in binary mode (CONV-03). | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                         | Processing 1 000 000 lengths followed by a sentinel (about 8 MiB of input) MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of lengths; only the token being read is held. Start-up and exit for an input holding only a sentinel MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                               | Measurement                                                     |
| NFR-04 | Robustness                                          | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                     | Option parsing, the incremental tokenizer, value classification (length, sentinel, or error), the conversion, block formatting, and I/O MUST be separate units. The conversion factors 3 and 36 and the limit MAX_YARDS MUST each be defined in exactly one place, and MAX_YARDS SHOULD be derived from the factor 36 rather than written as a literal.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Design review                                                   |
| NFR-06 | Testability                                         | The conversion and the block formatter MUST be pure functions covered by unit tests, including every acceptance value of FR-03 and the lengths 0, 1, MAX_YARDS − 1, and MAX_YARDS; value classification MUST be unit-tested at −2⁶³, −1, `-0`, MAX_YARDS, MAX_YARDS + 1, and 2⁶³. The tokenizer MUST be unit-tested with the input split into reads at every byte position, and with a check that it consumes nothing after the sentinel's terminating byte.                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Code review                                                     |
| NFR-07 | Build                                               | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | CI                                                              |
| NFR-08 | Security                                            | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-convert --help' for more information.`

| Trigger                                      | Exact first line                                                                         |
| :------------------------------------------- | :--------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-convert: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-convert: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-convert: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-convert: extra operand 'X'`                                                          |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                                  | Exact message                              |
| :----------------------------------------------------------------------- | :----------------------------------------- |
| FILE `F` does not exist                                                  | `dp-convert: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied               | `dp-convert: F: Permission denied`         |
| FILE `F` is a directory                                                  | `dp-convert: F: Is a directory`            |
| A component of FILE `F` is not a directory                               | `dp-convert: F: Not a directory`           |
| Any other open or read failure of FILE `F`                               | `dp-convert: F: Input/output error`        |
| Any of the above for standard input                                      | the same message with `F` = `-`            |
| Token `K` on line `L` of source `S` is not a valid _integer_             | `dp-convert: S:L: invalid integer 'K'`     |
| Token `K` on line `L` of source `S` is a valid _integer_ above MAX_YARDS | `dp-convert: S:L: value out of range 'K'`  |
| Source `S` ends, at end-of-input line `L`, before a sentinel was read    | `dp-convert: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)             | `dp-convert: write error`                  |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-08).

## 7. Verification

| Method                                                                                            | Applies to                                         |
| :------------------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                | FR-01 … FR-05, FR-07 … FR-11, FR-13, FR-14         |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03, 04, and 06 … 10 have several steps) | FR-02, FR-03, FR-05, FR-07 … FR-14                 |
| Unit test (written by the implementer)                                                            | FR-02 … FR-06, NFR-06                              |
| Measurement                                                                                       | NFR-03                                             |
| Inspection / review                                                                               | FR-06 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                             | Verifies                                                                                |
| :--- | :---------------------------------- | :-------------------------------------------------------------------------------------- |
| 01   | `dp-convert < lengths.txt`          | FR-01, FR-03, FR-04, FR-05                                                              |
| 02   | `dp-convert lengths.txt`            | FR-01                                                                                   |
| 03   | `dp-convert --prompt < lengths.txt` | FR-08                                                                                   |
| 04   | `dp-convert mixed.txt`              | FR-02 (CRLF, TAB, sign, leading zeros, `-0`), FR-05 (token after the sentinel not read) |
| 05   | `dp-convert - < mixed.txt`          | FR-01, FR-02                                                                            |
| 06   | `dp-convert nosentinel.txt`         | FR-07 (blocks kept, CONV-34)                                                            |
| 07   | `dp-convert bad.txt`                | FR-09 (blocks kept, CONV-34)                                                            |
| 08   | `dp-convert missing.txt`            | FR-10                                                                                   |
| 09   | `dp-convert --help`                 | FR-11                                                                                   |
| 10   | `dp-convert lengths.txt mixed.txt`  | FR-13, FR-14                                                                            |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                      |
| :--------------- | :--------------------------------------- |
| UR-01            | FR-02, FR-04, FR-06                      |
| UR-02            | FR-03, FR-04, FR-09                      |
| UR-03            | FR-05                                    |
| UR-04            | FR-05                                    |
| UR-05            | FR-01, CONV-26                           |
| UR-06            | FR-05, FR-06, NFR-02                     |
| UR-07            | FR-08, CONV-36                           |
| UR-08            | FR-07, CONV-34                           |
| UR-09            | FR-09, CONV-33, CONV-34                  |
| UR-10            | FR-10, CONV-16                           |
| UR-11            | FR-02, NFR-02, CONV-37                   |
| UR-12            | FR-11, FR-12, FR-13, FR-14               |
| UR-13            | NFR-01, NFR-02, FR-13, CONV-03, CLI-CONV |
| UR-14            | NFR-03, NFR-07                           |
