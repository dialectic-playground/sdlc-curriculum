<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-cars1](#software-requirements-specification-srs--dp-cars1)
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

# Software Requirements Specification (SRS) — dp-cars1

| Field                     | Value                                                      |
| :------------------------ | :--------------------------------------------------------- |
| Document ID               | SRS-26                                                     |
| Project                   | `26-cars` — Car Dealership Daily Sales & Inventory Tracker |
| Product                   | `dp-cars1` (canonical name)                                |
| Version                   | 1.0.0                                                      |
| Status                    | Approved (pre-written by the curriculum)                   |
| Parent document           | `URD.md` (URD-26)                                          |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)               |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                       |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-cars1`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-cars1` reads integer tokens from standard input or from one file: the opening stock of
twelve car brands, then sales as (brand, quantity) pairs until a negative brand or the end of
the input. It refuses impossible sales with a diagnostic and goes on, and finally writes the
`DAILY REPORT`: for each brand, the opening stock, the cars sold, the closing stock, and the
sales as a percentage of the opening stock. It can write prompts to standard error before each
read. It reports invalid tokens, an input that ends too early, and unreadable files with fixed
messages, in which case no report is written.

### 1.3 Definitions

| Term                                         | Definition                                                                                                                                                                                                     |
| :------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                                           | The line-feed byte, `0x0A`                                                                                                                                                                                     |
| Input                                        | The byte sequence read from standard input or from the FILE operand                                                                                                                                            |
| Source                                       | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)                                                            |
| Token, line number, end-of-input line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`; 1 plus the number of LF bytes before its first byte; 1 plus the number of LF bytes in the whole input |
| Brand                                        | An integer _b_ with 0 ≤ _b_ ≤ 11. There are exactly 12 brands                                                                                                                                                  |
| Opening stock _S_<sub>_b_</sub>              | The number of cars of brand _b_ at the start of the day, 0 ≤ _S_<sub>_b_</sub> ≤ 999999 (FR-03)                                                                                                                |
| Sales total _T_<sub>_b_</sub>                | The sum of the quantities of the accepted sales of brand _b_; 0 at the start of the sales phase                                                                                                                |
| Remaining stock                              | _S_<sub>_b_</sub> − _T_<sub>_b_</sub>                                                                                                                                                                          |
| Sale                                         | A brand token followed by a quantity token, read in the sales phase (FR-04)                                                                                                                                    |
| Sentinel                                     | A brand token whose value is negative; it ends the sales phase                                                                                                                                                 |
| Accepted sale, refused sale                  | A sale that passes the checks of FR-05 and is added to _T_<sub>_b_</sub>; a sale that fails one of them, is reported, and is not added                                                                         |
| Report                                       | The 14 lines of FR-06                                                                                                                                                                                          |
| Decimal                                      | The plain ASCII decimal representation of an integer: a `-` for negative values only, no leading zeros (zero is `0`), no digit grouping (CONV-06)                                                              |

### 1.4 References

- URD-26: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §5.3 (informative; see §2.5)
- SRS-28 (`projects/28-cars-modular/specs/SRS.md`): the modular revision, `dp-cars2`, whose
  default behavior is required to be identical to this tool's (informative here)

## 2. Overall description

### 2.1 Product perspective

`dp-cars1` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §5.3 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_. Project 28 (`dp-cars2`) adapts the
textbook's revision of the same program (§5.6), in which the report is produced by a separate
component; SRS-28 requires `dp-cars2` to reproduce this tool's behavior exactly by default.

### 2.2 Product functions

1. Read the opening stock of the 12 brands.
2. Read sales as (brand, quantity) pairs until a negative brand or the end of the input,
   accumulating the accepted sales per brand.
3. Refuse sales of an unknown brand, of a negative quantity, or of more cars than remain, with
   a diagnostic, and continue.
4. Write the daily report once the sales phase has ended.
5. Optionally write prompts to standard error before each read.
6. Report invalid tokens, an input that ends too early, and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Stock and sales are counted in exact integer arithmetic. The percentage is computed in IEEE
  754 binary64 exactly as FR-07 prescribes.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-08 and FR-05.
- The input may contain any bytes; only tokens that match the _integer_ grammar are values.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §5.3 keeps the opening stock and the sales of twelve brands in two
arrays indexed by brand number. It asks `Cars in stock for brand:or each brand, then
repeatedly asks `Which brand was sold?nd `How many cars in sale?` ding each quantity to
the brand's sales, until a negative brand is entered; it then prints a `DAILY REPORT` with, for
every brand, the opening stock, the sales, the closing stock (stock − sales), and the sales as
a percentage of the stock, 100.0 × sales / stock, with six decimals and a `%` sign.
`dp-cars1` keeps:

- the twelve brands numbered 0 … 11, the two-phase dialog, and the negative-brand sentinel;
- the three prompt texts, and the order in which the values are asked for;
- the report title `DAILY REPORT`, one line per brand in brand order, its four figures, and the
  percentage 100 × sales / stock written with six decimals and `%` (FR-07);
- accumulation of several sales of the same brand.

It changes the following, for the reasons given:

- **The report layout is defined exactly** (FR-06). The section's description names the
  columns but not their widths or headings, so the layout is designed here: right-aligned
  fixed-width columns under one heading line, with no blank lines and no trailing spaces.
- **A brand with no opening stock shows `n/a`** instead of a percentage (FR-07). The
  textbook's formula divides by zero for such a brand; since a sale from an empty lot is
  refused, its sales are always 0, and 0 of 0 has no meaningful percentage.
- **Impossible sales are refused** (FR-05). The section's description adds whatever quantity
  is typed, so a negative quantity, or more cars than are on the lot, would produce a negative
  closing stock or a percentage outside 0 … 100; it leaves brands ≥ 12 to be "ignored or
  rejected". Here each of these sales is reported with a located diagnostic and not counted,
  and the dialog continues, as an interactive program should. The exit status is 1 to tell a
  script that some entry was refused (§3.7).
- **A sale is always a pair.** The quantity is read even after an unknown brand, so a mistyped
  brand in a file never shifts the remaining tokens out of step (FR-04).
- **The opening stock is limited to 0 … 999999** per brand (FR-03), which bounds every figure
  in the report and keeps its columns fixed.
- **The end of the input also closes the day** (FR-04), so a file or pipe need not end with a
  sentinel; but an input that ends during the opening stock or between a brand and its
  quantity is an error, and no report is written from incomplete data (FR-09).
- **Invalid input is diagnosed.** A token that is not an integer stops the textbook program's
  reading in an unspecified way; here it is reported with its line number (FR-09).
- **Prompts are optional and go to standard error** (FR-08), so the report on standard output
  is the same with and without them. The stock prompt ends with the brand number and an LF,
  so that the typed count is not read as part of the number on screen.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full. From section 10 it incorporates: CONV-32 (the input is
read as tokens; line numbers), CONV-33 (every token uses the _integer_ grammar; the opening
stock is further restricted to 0 … 999999), CONV-34 (data diagnostics, with the standard
messages `invalid integer`, `value out of range`, and `unexpected end of input`, plus the three
refused-sale messages of FR-05), CONV-35 (`FIX(x, 6)` for the percentage), CONV-36 (`-p`,
`--prompt`, with the prompts of FR-08), and CONV-37 (the input is _text data_). CONV-38 does
not apply, because nothing is random.

There is **one override**: the three refused-sale diagnostics of FR-05 use the CONV-34 format
but, contrary to CONV-34's default, do **not** end processing; the dialog continues and the
report is written. The exit status is then 1, which is consistent with CONV-18 ("at least one
operation failed"), so the exit-status table is CONV-18's. Option syntax follows CONV-07 …
CONV-12, diagnostics follow CONV-13 … CONV-16, and standard input is read as permitted by
CONV-26. `dp-cars1` copies no input bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-cars1 [-p | --prompt] [FILE]
dp-cars1 --help
dp-cars1 --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                   |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-08 to standard error before each read |
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

The report (FR-06), written once, after the sales phase has ended, and only if no error of
FR-09 or FR-10 occurred. Nothing else. On a usage error, or when `--help` / `--version` is
handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-08, only with `--prompt`), refused-sale diagnostics (FR-05), and the other
diagnostics of section 6. When every sale is accepted and `--prompt` is not given, nothing is
written to standard error.

### 3.7 Exit status

| Status | Condition                                                                                                                                                                                                                                          |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The report was written and no sale was refused, or `--help` / `--version` was handled                                                                                                                                                              |
| 1      | The report was written but at least one sale was refused (FR-05); or no report was written because the input could not be opened or read (FR-10) or contained an invalid token or ended too early (FR-09); or standard output could not be written |
| 2      | Usage error (FR-13)                                                                                                                                                                                                                                |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are public fixture files in
`tests/fixtures/`. Each of the first four begins with the line
`15 8 20 4 0 12 7 30 3 10 25 6\n` (the opening stock of brands 0 … 11, called _O_ below):

- `day.txt`: _O_, then the sales `0 3`, `2 5`, `3 4`, `7 10`, `0 2`, `10 1`, `6 2`, `8 1`, one
  per line, then `-1\n`, then the line `Anything after the sentinel is never read.\n`;
- `rejected.txt`: _O_, then `1 2`, `12 1`, `5 -2`, `3 3`, `3 2`, `4 1`, `4 0`, `1 6`, one per
  line (on lines 2 … 9), then `-1\n`;
- `cut.txt`: _O_, then `2 5\n7\n`;
- `noend.txt`: twelve lines `9\r\n`, then `5 6\r\n9 9\r\n5 1\r\n` and no sentinel;
- `bad.txt`: the opening stock one value per line, with `2O` (digit 2, letter O) on line 3.

`R` denotes the report of `day.txt`, given in full in FR-06.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
_AC:_ `dp-cars1 day.txt`, `dp-cars1 < day.txt`, and `dp-cars1 - < day.txt` each write `R` and
exit 0. _(UR-09)_

**FR-02: Tokens.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
consumed in order by FR-03 and FR-04. Every token that is consumed MUST be a valid _integer_
(CONV-33); a sign (`+5`, `-0`) and leading zeros (`007`) are allowed, and the value is used, not
the spelling. Line structure has no meaning: tokens may be separated by any mixture of space,
TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF input, and a sale's two tokens may
be on different lines. A token that is not a valid _integer_ is handled by FR-09.
_AC:_ `dp-cars1 noend.txt` (CRLF line endings) writes a report with opening stock 9 for every
brand, sales 7 for brand 5 and 9 for brand 9, exit 0. _(UR-01, UR-10)_

**FR-03: Opening stock.**
The first 12 tokens are the opening stock _S_<sub>0</sub> … _S_<sub>11</sub>, in brand order.
Each MUST be a valid _integer_ with 0 ≤ _S_<sub>_b_</sub> ≤ 999999; a valid _integer_ outside
that range is handled by FR-09 (`value out of range`). If the input ends before the twelfth
value has been read, FR-09 applies (`unexpected end of input`).
_AC:_ the hidden fixture with opening stock `999999 512 3 3 1 7 0 0 0 0 0 100` is accepted;
an opening stock of `1000000` or `-1` gives `value out of range`; an input holding only 11
values gives `unexpected end of input` at the end-of-input line number. _(UR-01, UR-07)_

**FR-04: Sales phase.**
After the opening stock, the tool MUST repeat the following steps until the sales phase ends:

1. Read the next token, the _brand token_. If the input has ended instead, the sales phase
   ends.
2. If the brand token's value is negative (the sentinel), the sales phase ends. The tool reads
   no further input: any bytes after the sentinel are ignored, whatever they contain.
3. Otherwise read the next token, the _quantity token_, whatever the brand's value (also when
   it is 12 or more). If the input has ended instead, FR-09 applies
   (`unexpected end of input`).
4. Apply the checks of FR-05. If the sale passes them, add the quantity to
   _T_<sub>_b_</sub>, where _b_ is the brand token's value; otherwise the sale is refused.

The brand and the quantity may be any valid _integer_ (−2⁶³ … 2⁶³−1). `-0` is brand 0, not the
sentinel. When the sales phase ends, the report is written (FR-06).
_AC:_ `dp-cars1 day.txt` → `R`, in which brand 0 has sales 5 (3 + 2) and the line after the
sentinel, which contains no integers, causes no error. `dp-cars1 cut.txt` → stdout empty,
stderr `dp-cars1: cut.txt:4: unexpected end of input\n`, exit 1. _(UR-02, UR-03, UR-07)_

**FR-05: Refused sales.**
A sale with brand value _b_ (≥ 0) and quantity value _q_ MUST be checked in this order, and
the first check that fails refuses the sale:

1. If _b_ ≥ 12: `dp-cars1: <source>:<line>: no such brand '<token>'`, where `<line>` and
   `<token>` are those of the brand token.
2. If _q_ < 0: `dp-cars1: <source>:<line>: negative quantity '<token>'`, where `<line>` and
   `<token>` are those of the quantity token.
3. If _q_ > _S_<sub>_b_</sub> − _T_<sub>_b_</sub>:
   `dp-cars1: <source>:<line>: not enough cars in stock for brand <b> '<token>'`, where `<b>` is
   the decimal of _b_ (its value, not its spelling), and `<line>` and `<token>` are those of
   the quantity token.

The comparison in check 3 MUST be exact for every _q_ up to 2⁶³−1 (compare _q_ with the
remaining stock; computing _T_<sub>_b_</sub> + _q_ can overflow a 64-bit integer). A quantity
of 0 passes every check when _b_ < 12 and changes nothing. `<source>` is as defined in section
1.3 and `<token>` is the token's exact bytes. The diagnostic MUST be written to standard error,
and standard error flushed, as soon as the quantity token has been read and before the next
read; the sales phase then continues with step 1 of FR-04. Each refused sale produces exactly
one diagnostic. A refused sale does not change any total. If at least one sale was refused,
the report is still written, and the exit status is 1.
Because every accepted sale satisfies the checks, 0 ≤ _T_<sub>_b_</sub> ≤ _S_<sub>_b_</sub>
holds for every brand at every moment, and an opening stock of 0 admits only sales of 0 cars.
_AC:_ `dp-cars1 rejected.txt` → stderr
`dp-cars1: rejected.txt:3: no such brand '12'\n`,
`dp-cars1: rejected.txt:4: negative quantity '-2'\n`,
`dp-cars1: rejected.txt:6: not enough cars in stock for brand 3 '2'\n`,
`dp-cars1: rejected.txt:7: not enough cars in stock for brand 4 '1'\n`, in that order; stdout
the report with sales 8 for brand 1, 3 for brand 3, and 0 for every other brand; exit 1. A sale
`9223372036854775807 1` is refused as `no such brand`, and `1 9223372036854775807` as
`not enough cars in stock for brand 1`. _(UR-02, UR-05)_

**FR-06: Report.**
When the sales phase has ended, the tool MUST write exactly 14 lines to standard output, each
ending with a single LF:

1. `DAILY REPORT`
2. `Brand    Start    Sales      End      Sales %` (45 bytes: `Brand`, 4 spaces, `Start`,
   4 spaces, `Sales`, 6 spaces, `End`, 6 spaces, `Sales %`)
3. … 14. one line for each brand _b_ = 0, 1, …, 11, in that order, made of five fields with no
   separators: the decimal of _b_ right-aligned in 5 columns; the decimal of
   _S_<sub>_b_</sub> right-aligned in 9 columns; the decimal of _T_<sub>_b_</sub> in 9
   columns; the decimal of _S_<sub>_b_</sub> − _T_<sub>_b_</sub> in 9 columns; and the
   percentage field of FR-07 right-aligned in 13 columns.

"Right-aligned in _w_ columns" means preceded by as many spaces (`0x20`) as are needed to make
the field _w_ bytes long; with the limits of FR-03 no field is ever longer than its width, so
every brand line is exactly 45 bytes plus LF. There are no blank lines and no trailing spaces.
The report is written once, after all input has been consumed, and standard output is flushed
before the tool exits.
_AC:_ `dp-cars1 day.txt` → stdout `R`, which is exactly:

```text
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
    1        8        0        8    0.000000%
    2       20        5       15   25.000000%
    3        4        4        0  100.000000%
    4        0        0        0          n/a
    5       12        0       12    0.000000%
    6        7        2        5   28.571429%
    7       30       10       20   33.333333%
    8        3        1        2   33.333333%
    9       10        0       10    0.000000%
   10       25        1       24    4.000000%
   11        6        0        6    0.000000%
```

stderr empty, exit 0. _(UR-04)_

**FR-07: Sales percentage.**
If _S_<sub>_b_</sub> > 0, the percentage field MUST be `FIX(P, 6)` (CONV-35) followed by `%`,
where _P_ is the binary64 value of (100 × _T_<sub>_b_</sub>) / _S_<sub>_b_</sub> computed as
follows: 100 × _T_<sub>_b_</sub> is computed exactly (it is at most 99999900) and converted to
binary64 exactly, _S_<sub>_b_</sub> is converted to binary64 exactly, and the two are divided
once with IEEE 754 round-to-nearest-even. (Equivalently, _P_ is the binary64 value nearest to
the exact quotient.) `FIX` then rounds the exact value of _P_, ties to even. Because
_T_<sub>_b_</sub> ≤ _S_<sub>_b_</sub>, the field is between `0.000000%` and `100.000000%`. If
_S_<sub>_b_</sub> = 0, the field MUST be the three bytes `n/a`.
_AC:_ (_T_, _S_) = (5, 15) → `33.333333%`; (2, 7) → `28.571429%`; (2, 3) → `66.666667%`;
(1, 512) → `0.195312%` (the exact quotient 0.1953125 is a tie and rounds to even); (4, 4) →
`100.000000%`; (0, 8) → `0.000000%`; (999999, 999999) → `100.000000%`; (0, 0) → `n/a`.
_(UR-04, UR-06)_

**FR-08: Prompts.**
`-p`, `--prompt` enables these prompts (CONV-36):

| Prompt  | Bytes                                                             | Written                                                                     |
| :------ | :---------------------------------------------------------------- | :-------------------------------------------------------------------------- |
| P1(_b_) | `Cars in stock for brand:ollowed by the decimal of _b_ and one LF | immediately before the opening stock of brand _b_ is read, for _b_ = 0 … 11 |
| P2      | `Which brand was sold?22 bytes, ending with one space, no LF)     | immediately before each attempt to read a brand token (step 1 of FR-04)     |
| P3      | `How many cars in sale?23 bytes, ending with one space, no LF)    | immediately before each attempt to read a quantity token (step 3 of FR-04)  |

Each prompt is written to standard error, and standard error flushed, before the read it
belongs to; a prompt is written even if that read reaches the end of the input. So a day with
_n_ sales (accepted or refused) produces P1(0) … P1(11), then _n_ times P2 followed by P3,
then one final P2 (before the sentinel or the end of the input). No prompt is written after
the sentinel, after an error of FR-09, or if the input cannot be opened. A diagnostic that
follows a prompt continues the same line of standard error. Without the flag, no prompt is
written. Prompts never change standard output.
_AC:_ `dp-cars1 --prompt < day.txt` → stdout `R`; stderr the twelve lines
`Cars in stock for brand: 0\n` … `Cars in stock for brand: 11\n`, then eight times
`Which brand was sold? How many cars in sale?then `Which brand was sold?`xt 0.`dp-cars1 -p`with empty standard input → stderr`Cars in stock for brand: 0\ndp-cars1: -:1: unexpected end of input\n`, exit 1. _(UR-08)_

**FR-09: Invalid tokens and incomplete input.**
The tool MUST write one of the following diagnostics and stop: it reads no further input,
writes **no report**, and exits with status 1. Refused-sale diagnostics already written
(FR-05) are kept.

- A consumed token that is not a valid _integer_ (CONV-33), including an integer outside
  −2⁶³ … 2⁶³−1: `dp-cars1: <source>:<line>: invalid integer '<token>'`.
- An opening stock that is a valid _integer_ outside 0 … 999999:
  `dp-cars1: <source>:<line>: value out of range '<token>'`.
- The input ends while an opening stock (FR-03) or a quantity (FR-04 step 3) is expected:
  `dp-cars1: <source>:<line>: unexpected end of input`, where `<line>` is the end-of-input
  line number.

`<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32), and
`<token>` is the token's exact bytes (CONV-34).
_AC:_ `dp-cars1 bad.txt` → stdout empty, stderr `dp-cars1: bad.txt:3: invalid integer '2O'\n`,
exit 1. A quantity `9223372036854775808` gives `invalid integer`. A token `3` followed by a
`0x1A` byte and an LF gives `invalid integer '3<0x1A>'`, because that Ctrl-Z byte does not end
the input; a `0x1A` run at the very end of the input (even directly after the last digit) is
ignored. _(UR-07, UR-10)_

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-cars1: <source>: <reason>` with `<reason>` from the CONV-16 table, write
no report, and exit with status 1. When standard input fails, `<source>` is `-`.
_AC:_ `dp-cars1 missing.txt` → stderr `dp-cars1: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-cars1 subdir` where `subdir` is a directory →
`dp-cars1: subdir: Is a directory`. _(UR-11)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-cars1 --help` matches the user manual exactly; `dp-cars1 extra --help` also prints it.
_(UR-12)_

**FR-12: Version.**
`--version` MUST write `dp-cars1 (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-12)_

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-cars1: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-cars1 day.txt rejected.txt` → `dp-cars1: extra operand 'rejected.txt'`;
`dp-cars1 -x --help` → `dp-cars1: invalid option -- 'x'`; `dp-cars1 --prompt=yes` →
`dp-cars1: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-13, UR-15)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-cars1 -p - extra < day.txt` writes no prompt.
_(UR-13)_

## 5. Non-functional requirements

| ID     | Category                                            | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Verification                                                    |
| :----- | :-------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                         | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: an interactive console dialog | The dialog MUST work the same at a POSIX terminal and in a Windows console. Each prompt MUST reach the terminal before the tool waits for the answer, and each refused-sale diagnostic before the next prompt: standard error MUST be flushed explicitly after each prompt and diagnostic, on platforms where it is buffered. The tool MUST NOT wait for more input than the token it needs (a token is complete when the whitespace byte after it, or the end of the input, has been read), so that typing a value and Enter is enough. The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 interprets a trailing Ctrl-Z run. The platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03). | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                         | A day of 1 000 000 sales (about 8 MiB of input) MUST be processed in under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of sales: only the 24 totals and the token being read are held. Start-up and exit for a short input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Measurement                                                     |
| NFR-04 | Robustness                                          | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and quantities near 2⁶³−1 (FR-05). A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Unit + black-box tests                                          |
| NFR-05 | Maintainability: indexed collections                | The opening stocks MUST be held in one indexed collection of 12 elements and the sales totals in another, both indexed by brand number; no per-brand variables and no per-brand code. The number of brands (12) and the stock limit (999999) MUST each appear exactly once, as named constants. Option parsing, the incremental tokenizer, the dialog (stock and sales phases), the sale checks of FR-05, the percentage function of FR-07, report formatting, and I/O MUST be separate units (Principles 12, 13, 18).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Design review                                                   |
| NFR-06 | Testability                                         | The sale checks, the percentage function, and the report formatter MUST be pure functions covered by unit tests, including every acceptance value of FR-07, a brand with zero opening stock, the limits 0 and 999999, and quantities 0, −1, and 2⁶³−1. The tokenizer MUST be unit-tested with the input split into reads at every byte position, and with a trailing and a non-trailing `0x1A`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Code review                                                     |
| NFR-07 | Build                                               | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | CI                                                              |
| NFR-08 | Security                                            | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-cars1 --help' for more information.`

| Trigger                                      | Exact first line                                                                       |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-cars1: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-cars1: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-cars1: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `dp-cars1: extra operand 'X'`                                                          |

Refused sales (processing continues, the report is written, and the final exit status is 1):

| Trigger                                                                               | Exact message                                             |
| :------------------------------------------------------------------------------------ | :-------------------------------------------------------- |
| Brand token `K` on line `L` of source `S` has a value of 12 or more                   | `dp-cars1: S:L: no such brand 'K'`                        |
| Quantity token `K` on line `L` of source `S` is negative                              | `dp-cars1: S:L: negative quantity 'K'`                    |
| Quantity token `K` on line `L` of source `S` exceeds the remaining stock of brand `B` | `dp-cars1: S:L: not enough cars in stock for brand B 'K'` |

Runtime errors (exit status 1; the tool stops at the first one and writes no report):

| Trigger                                                                                                  | Exact message                            |
| :------------------------------------------------------------------------------------------------------- | :--------------------------------------- |
| FILE `F` does not exist                                                                                  | `dp-cars1: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                                               | `dp-cars1: F: Permission denied`         |
| FILE `F` is a directory                                                                                  | `dp-cars1: F: Is a directory`            |
| A component of FILE `F` is not a directory                                                               | `dp-cars1: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                                               | `dp-cars1: F: Input/output error`        |
| Any of the above for standard input                                                                      | the same message with `F` = `-`          |
| Token `K` on line `L` of source `S` is not a valid _integer_                                             | `dp-cars1: S:L: invalid integer 'K'`     |
| Opening stock token `K` on line `L` of source `S` is outside 0 … 999999                                  | `dp-cars1: S:L: value out of range 'K'`  |
| The input of source `S` ends, at end-of-input line `L`, where an opening stock or a quantity is expected | `dp-cars1: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)                                             | `dp-cars1: write error`                  |

When `--prompt` is given, a diagnostic follows the last prompt on the same line of standard
error (FR-08).

## 7. Verification

| Method                                                                                            | Applies to                                                   |
| :------------------------------------------------------------------------------------------------ | :----------------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                | FR-01 … FR-11, FR-13, FR-14                                  |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03, 04, and 06 … 10 have several steps) | FR-02 … FR-14                                                |
| Unit test (written by the implementer)                                                            | FR-02 … FR-07, NFR-06                                        |
| Measurement                                                                                       | NFR-03                                                       |
| Inspection / review                                                                               | FR-05 and FR-08 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                         | Verifies                                            |
| :--- | :------------------------------ | :-------------------------------------------------- |
| 01   | `dp-cars1 day.txt`              | FR-01, FR-03, FR-04, FR-06, FR-07 (`n/a`)           |
| 02   | `dp-cars1 < day.txt`            | FR-01                                               |
| 03   | `dp-cars1 --prompt < day.txt`   | FR-08                                               |
| 04   | `dp-cars1 rejected.txt`         | FR-05 (all three refusals, exit 1 with a report)    |
| 05   | `dp-cars1 noend.txt`            | FR-02 (CRLF), FR-04 (end of input closes the day)   |
| 06   | `dp-cars1 cut.txt`              | FR-04, FR-09 (`unexpected end of input`, no report) |
| 07   | `dp-cars1 bad.txt`              | FR-09 (`invalid integer`)                           |
| 08   | `dp-cars1 missing.txt`          | FR-10                                               |
| 09   | `dp-cars1 --help`               | FR-11                                               |
| 10   | `dp-cars1 day.txt rejected.txt` | FR-13, FR-14                                        |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                   |
| :--------------- | :------------------------------------ |
| UR-01            | FR-02, FR-03                          |
| UR-02            | FR-04, FR-05                          |
| UR-03            | FR-04                                 |
| UR-04            | FR-06, FR-07                          |
| UR-05            | FR-05                                 |
| UR-06            | FR-07                                 |
| UR-07            | FR-03, FR-04, FR-09, CONV-33, CONV-34 |
| UR-08            | FR-08, CONV-36                        |
| UR-09            | FR-01, CONV-26                        |
| UR-10            | FR-02, FR-09, NFR-02, CONV-37         |
| UR-11            | FR-10, CONV-16                        |
| UR-12            | FR-11, FR-12                          |
| UR-13            | FR-13, FR-14                          |
| UR-14            | NFR-01, NFR-02, CONV-03               |
| UR-15            | FR-13, CLI-CONV                       |
| UR-16            | NFR-03, NFR-07                        |
