<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-wc](#software-requirements-specification-srs--dp-wc)
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
    - [2.5 Relationship to traditional `wc` (informative)](#25-relationship-to-traditional-wc-informative)
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

# Software Requirements Specification (SRS) — dp-wc

| Field                     | Value                                        |
| :------------------------ | :------------------------------------------- |
| Document ID               | SRS-04                                       |
| Project                   | `04-wc` — Word, Line, and Byte Counter       |
| Product                   | `dp-wc` (canonical name)                     |
| Version                   | 1.0.0                                        |
| Status                    | Approved (pre-written by the curriculum)     |
| Parent document           | `URD.md` (URD-04)                            |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018         |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-wc`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope

`dp-wc` reads files or standard input as raw bytes and reports, for each input, any selection of
five counts: lines, words, characters, bytes, and maximum line length. When more than one input
operand is given it also prints a total line. Every count is defined on bytes and on a fixed
UTF-8 decoding rule, so results never depend on locale, platform, or read-buffer size.

### 1.3 Definitions

| Term                 | Definition                                                                                                                                  |
| :------------------- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| LF                   | The line-feed byte, `0x0A`                                                                                                                  |
| Whitespace byte      | Exactly one of the six bytes `0x20` (space), `0x09` (TAB), `0x0A` (LF), `0x0B` (VT), `0x0C` (FF), `0x0D` (CR). No other byte is whitespace. |
| Input                | The complete byte sequence of one operand: a file's contents, or the bytes read from standard input                                         |
| Well-formed sequence | A byte sequence matching one row of the table in FR-06 (Unicode Standard, Table 3-7)                                                        |
| Character            | One unit produced by the decoding rule of FR-06: either a well-formed sequence or a single byte that does not begin one                     |
| Line segment         | A maximal run of characters containing no LF: the characters before the first LF, between two consecutive LFs, or after the last LF         |
| Count set            | The five numbers _lines_, _words_, _chars_, _bytes_, _maxlen_ computed for one input                                                        |
| Selected columns     | The subset of the count set that is printed (FR-01, FR-02)                                                                                  |
| Operand              | A command-line argument that is not an option (CONV-10)                                                                                     |
| Report               | Everything `dp-wc` writes to standard output: one row per successfully counted input, plus an optional total row                            |
| W                    | The common field width of the report (FR-09)                                                                                                |

### 1.4 References

- URD-04: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- The Unicode Standard, Version 15.0, §3.9, Table 3-7 "Well-Formed UTF-8 Byte Sequences";
  RFC 3629 "UTF-8, a transformation format of ISO 10646"

## 2. Overall description

### 2.1 Product perspective

`dp-wc` is a standalone executable in the tradition of POSIX `wc`. Its interfaces are the
command line, the files named by its operands, standard input, standard output, standard error,
and the exit status. It is the fourth curriculum project that reads files, and the first whose
central problem is _interpreting_ bytes (as words and as UTF-8 characters) rather than copying
or slicing them.

### 2.2 Product functions

1. Count LF-terminated lines, ASCII-whitespace-delimited words, UTF-8 characters, and bytes.
2. Measure the longest line in characters.
3. Print any selection of these counts in a fixed column order.
4. Count several inputs and print a total.
5. Report unreadable inputs and continue with the rest.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- All counting MUST be implemented from the byte-level definitions in this document. Library
  facilities whose results depend on locale or platform (locale-aware `isspace`/`iswspace`,
  multibyte-conversion functions such as `mbrtowc`, platform "text mode" file reading) MUST NOT
  determine any count (NFR-02).

### 2.4 Assumptions

- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Inputs may be of any size, may contain any byte values (including NUL), and need not be valid
  UTF-8 or end with LF.

### 2.5 Relationship to traditional `wc` (informative)

`dp-wc` deliberately deviates from GNU and BSD `wc` wherever their behavior depends on locale,
terminal, or file size. The deviations are: words are delimited only by the six ASCII
whitespace bytes, in every locale; characters follow the fixed decoding rule of FR-06; `-L`
counts characters (TAB counts as 1, CR does not end a line) instead of display columns; the
column width follows FR-09 instead of being derived from file sizes; a failed operand prints no
row; standard input is read to end-of-file at most once (FR-12); file names are printed without
quoting or escaping. The GNU options `--files0-from` and `--total` are not provided.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. In particular: option syntax
follows CONV-07 … CONV-12; diagnostics follow CONV-13 … CONV-16; processing continues after a
failed operand (CONV-17); the exit statuses are those of CONV-18; standard input is read as
permitted by CONV-26. `dp-wc` copies no input to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-wc [-l] [-w] [-m] [-c] [-L] [FILE]...
dp-wc --help
dp-wc --version
```

### 3.2 Options

| Short | Long                | Argument | Selects column | Description                                                 |
| :---- | :------------------ | :------- | :------------- | :---------------------------------------------------------- |
| `-l`  | `--lines`           | none     | lines          | Print the number of LF bytes                                |
| `-w`  | `--words`           | none     | words          | Print the number of words                                   |
| `-m`  | `--chars`           | none     | chars          | Print the number of characters                              |
| `-c`  | `--bytes`           | none     | bytes          | Print the number of bytes                                   |
| `-L`  | `--max-line-length` | none     | maxlen         | Print the length of the longest line segment, in characters |
| —     | `--help`            | none     | —              | Print the help text and exit 0                              |
| —     | `--version`         | none     | —              | Print the version line and exit 0                           |

No option takes an argument. Option syntax (bundling such as `-lwc`, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. Repeating a selection option has the same effect as giving it
once (CONV-11).

### 3.3 Operands

Zero or more FILE operands, processed in the order given. The operand `-` denotes standard
input (CONV-10). Every token after `--` is an operand, even if it begins with `-`. Operands are
used and echoed exactly as given (CONV-19).

### 3.4 Standard input

Read when no operand is given (FR-03) and for each `-` operand, subject to FR-12. Read as raw
bytes; no newline translation of any kind is performed on any platform.

### 3.5 Standard output

The report (FR-09 … FR-11). On a usage error, or when `--help` / `--version` is handled, the
output is as specified by FR-14 … FR-17 instead.

### 3.6 Standard error

Diagnostics only (section 6). Nothing when every operand is counted successfully.

### 3.7 Exit status

| Status | Condition                                                      |
| :----- | :------------------------------------------------------------- |
| 0      | Every input was counted, or `--help` / `--version` was handled |
| 1      | At least one operand could not be opened or read (FR-13)       |
| 2      | Usage error (FR-16)                                            |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `poem.txt`, `utf8.txt`, and `crlf.txt` are the
public fixture files in `tests/fixtures/`.

**FR-01: Default selection.**
If none of `-l`, `-w`, `-m`, `-c`, `-L` (or their long forms) is given, the selected columns
MUST be lines, words, and bytes, exactly as if `-l -w -c` had been given.
_AC:_ `dp-wc poem.txt` → stdout `5 93 poem.txt\n`, exit 0. _(UR-01)_

**FR-02: Column selection and order.**
If one or more selection options are given, exactly the columns they select MUST be printed,
and no others. Columns MUST always appear in the fixed order **lines, words, chars, bytes,
maxlen**, regardless of the order or repetition of the options on the command line.
_AC:_ `dp-wc -L -c -m -w -l utf8.txt` → ` 54 93 19 utf8.txt\n`; `dp-wc -mc utf8.txt` →
`54 93 utf8.txt\n`. _(UR-02, UR-03)_

**FR-03: Inputs.**
Each operand is one input, processed in command-line order. A file operand MUST be opened and
read as raw bytes from its first byte to end-of-file. The operand `-` denotes standard input.
If no operand is given, the tool MUST read standard input exactly as if a single operand had
been given, except that its row has no name field (FR-10).
_AC:_ `dp-wc < poem.txt` → `5 93\n`. _(UR-09)_

**FR-04: Line count.**
_lines_ MUST equal the number of LF (`0x0A`) bytes in the input. A final line segment that is
not terminated by LF does not add to _lines_. CR bytes are not line terminators.
_AC:_ `dp-wc -l poem.txt` → `5 poem.txt\n`; `crlf.txt` (four CRLF-terminated lines) has
_lines_ = 4. _(UR-02)_

**FR-05: Word count.**
_words_ MUST equal the number of maximal non-empty runs of consecutive non-whitespace bytes in
the input, where the whitespace bytes are exactly `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, and
`0x0D` (section 1.3). Every other byte value — including NUL, other control bytes, `0x7F`, and
every byte `0x80`–`0xFF` whether or not it belongs to a valid UTF-8 sequence — is a word byte.
Consequently, non-ASCII Unicode spaces (for example U+00A0 NO-BREAK SPACE, U+3000 IDEOGRAPHIC
SPACE) do not separate words, and an invalid byte inside a word does not split it.
Equivalently: _words_ is the number of positions _i_ such that byte _i_ is a word byte and
either _i_ = 0 or byte *i*−1 is a whitespace byte.
_AC:_ `dp-wc --words poem.txt` → `15 poem.txt\n`. A file containing
`a\tb\vc\fd e` + U+00A0 + `f` + U+3000 + `g\n` has 5 words. _(UR-02, UR-06)_

**FR-06: Character count.**
_chars_ MUST equal the number of characters produced by decoding the entire input with the
following algorithm. Let the input be bytes _b_[0] … _b_[*n*−1] and set _p_ = 0, _chars_ = 0.
While _p_ < _n_:

1. If the bytes starting at _b_[_p_] form a complete well-formed sequence of length _k_ — that
   is, _b_[_p_] … _b_[_p_+*k*−1] all exist in the input and match one row of the table below —
   then add 1 to _chars_ and set _p_ = _p_ + _k_.
2. Otherwise add 1 to _chars_ and set _p_ = _p_ + 1.

Well-formed UTF-8 byte sequences (The Unicode Standard, Table 3-7):

| Code points        | Byte 1    | Byte 2    | Byte 3    | Byte 4    |
| :----------------- | :-------- | :-------- | :-------- | :-------- |
| U+0000..U+007F     | `00`–`7F` |           |           |           |
| U+0080..U+07FF     | `C2`–`DF` | `80`–`BF` |           |           |
| U+0800..U+0FFF     | `E0`      | `A0`–`BF` | `80`–`BF` |           |
| U+1000..U+CFFF     | `E1`–`EC` | `80`–`BF` | `80`–`BF` |           |
| U+D000..U+D7FF     | `ED`      | `80`–`9F` | `80`–`BF` |           |
| U+E000..U+FFFF     | `EE`–`EF` | `80`–`BF` | `80`–`BF` |           |
| U+10000..U+3FFFF   | `F0`      | `90`–`BF` | `80`–`BF` | `80`–`BF` |
| U+40000..U+FFFFF   | `F1`–`F3` | `80`–`BF` | `80`–`BF` | `80`–`BF` |
| U+100000..U+10FFFF | `F4`      | `80`–`8F` | `80`–`BF` | `80`–`BF` |

Consequences, all normative: every valid UTF-8 code point counts as 1; each byte of an invalid
or truncated sequence counts as 1 (`E2 82 41` counts 3: two invalid bytes and `A`); overlong
forms (`C0`, `C1`, `E0 80`–`9F`, `F0 80`–`8F`), encoded surrogates (`ED A0`–`BF …`), values
above U+10FFFF (`F4 90`–`BF …`, `F5`–`FF`), and lone continuation bytes (`80`–`BF`) count 1 per
byte; a sequence truncated by end-of-input counts 1 per byte present; a byte-order mark
(`EF BB BF`) is an ordinary character and counts 1; NUL counts 1. The algorithm is applied to
the input as a whole: how the input is divided into reads MUST NOT affect the result (NFR-05).
Note that this rule counts invalid input per byte; it is _not_ the "maximal subpart" replacement
count of the Unicode Standard §3.9, under which `E2 82 41` would count 2.
_AC:_ `dp-wc -mc utf8.txt` → `54 93 utf8.txt\n`. The hidden fixture `invalid.bin`, which
contains every kind of invalid sequence listed above, yields _chars_ = 85 for 90 bytes.
_(UR-04, UR-05, UR-06)_

**FR-07: Maximum line length.**
_maxlen_ MUST equal the largest number of characters (FR-06) in any line segment of the input
(section 1.3), or 0 if the input is empty. The LF bytes that delimit line segments are never
counted. The final segment after the last LF counts as a segment even though it has no LF (an
empty final segment has length 0). Every character other than LF counts exactly 1, including
TAB, CR, VT, FF, other control characters, combining marks, wide (East Asian) characters, and
invalid bytes. Decoding (FR-06) is applied to the whole input before it is divided into
segments; because `0A` can never be part of a multibyte well-formed sequence, the two orders
give the same result.
_Deliberate deviation from GNU `wc -L`:_ GNU expands TAB to the next multiple of 8 columns, uses
terminal display widths (0 for non-printing and combining characters, 2 for wide characters),
and treats CR and FF as ending a line. `dp-wc` does none of these, so that the value is a pure
function of the bytes.
_AC:_ `dp-wc --max-line-length poem.txt` → `37 poem.txt\n`; for `crlf.txt` _maxlen_ = 19
(`delta epsilon zeta` plus its CR). _(UR-11, UR-06)_

**FR-08: Byte count.**
_bytes_ MUST equal the total number of bytes in the input. It MUST be obtained by reading the
input (or by an equivalent exact method for regular files); no newline translation or
end-of-file marker interpretation (such as Ctrl-Z on Windows) may alter it.
_AC:_ `poem.txt` has _bytes_ = 93; `crlf.txt` has _bytes_ = 41 on every platform. _(UR-02, UR-15)_

**FR-09: Report format and field width.**
Every row of the report MUST consist of the values of the selected columns, in the order of
FR-02, each written in ASCII decimal without sign, leading zeros, or digit grouping (zero is
`0`) and right-aligned with leading spaces (`0x20`) to the common width **W**, with exactly one
space between consecutive values. The row continues with the name field, if any (FR-10), and
ends with a single LF.
**W** MUST be the number of decimal digits of the largest value printed anywhere in the report,
considering every selected column of every row, including the total row (FR-11). W is at least

1. No other padding, prefix, or trailing space is written. Because W depends on all values, the
   report is written after the last operand has been processed; diagnostics (section 6) MAY be
   written as soon as each failure is detected.
   _AC:_ `dp-wc poem.txt utf8.txt` →
   `  93 poem.txt\n  4   9  93 utf8.txt\n  9  24 186 total\n` (W = 3, from 186);
   `dp-wc -l poem.txt` → `5 poem.txt\n` (W = 1). _(UR-08, UR-15)_

**FR-10: Name field.**
For an input named by an operand, the name field is one space followed by the operand exactly
as given, encoded in UTF-8 (CONV-05, CONV-19), with no quoting or escaping; for the operand `-`
it is `. When standard input is read because no operand was given (FR-03), the row has no
name field: it ends immediately after the last value.
_AC:_ `dp-wc < poem.txt`→`5 93\n`; `dp-wc - < poem.txt`→`51 93 -\n`. _(UR-07, UR-09)_

**FR-11: Total row.**
If **two or more operands** are given, the report MUST end with a total row whose name field is
`tal`. Its _lines_, _words_, _chars_, and _bytes_ values are the sums over all inputs that
were counted successfully; its _maxlen_ value is the **maximum** of their _maxlen_ values (0 if
none). Inputs that failed (FR-13) contribute nothing. The total row is printed whenever two or
more operands are given, even if some or all of them failed. With zero operands or one operand,
no total row is printed. An operand whose text is `total` is not treated specially.
_AC:_ `dp-wc poem.txt missing.txt crlf.txt` → total row ` 134 total`; `dp-wc subdir
missing.txt` (both fail) → stdout `0 0 0 total\n`, exit 1. _(UR-07, UR-10)_

**FR-12: Standard input read at most once.**
Standard input MUST be read to end-of-file at most once per invocation. The first input that
denotes standard input (the implicit input of FR-03, or the first `-` operand) reads it to
end-of-file. Every later `-` operand MUST NOT read standard input again; its count set is all
zeros, and it still produces a row named `-` and contributes zeros to the total.
_AC:_ `dp-wc - poem.txt - < poem.txt` →
`  93 -\n  5  15  93 poem.txt\n  0   0   0 -\n 10  30 186 total\n`. _(UR-09)_

**FR-13: Unreadable inputs.**
If an operand cannot be opened, is a directory, or a read error occurs before end-of-file, the
tool MUST write `dp-wc: <operand>: <reason>` to standard error, with `<reason>` taken from the
CONV-16 table, and continue with the next operand (CONV-17). The failed input produces **no row**
and contributes nothing to the total, even if some bytes were read before the error. When
standard input fails, `<operand>` is `-` (also for the implicit input of FR-03). If any operand
failed, the exit status MUST be 1.
_AC:_ `dp-wc poem.txt missing.txt crlf.txt` → stderr
`dp-wc: missing.txt: No such file or directory\n`, rows for `poem.txt` and `crlf.txt` and the
total, exit 1; `dp-wc subdir` where `subdir` is a directory → `dp-wc: subdir: Is a directory`.
_(UR-10)_

**FR-14: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
_AC:_ `dp-wc --help` matches the user manual exactly. _(UR-13)_

**FR-15: Version.**
`--version` MUST write `dp-wc (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-13)_

**FR-16: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--lines=…`, `--help=…`,
and so on), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with exit
status 2. Long options MUST NOT be abbreviated (CONV-08): `--char` is unrecognized. `dp-wc`
accepts any number of operands, so `missing operand` and `extra operand` never occur.
_AC:_ `dp-wc -lz poem.txt` → `dp-wc: invalid option -- 'z'`; `dp-wc --bytes=1 poem.txt` →
`dp-wc: option '--bytes' doesn't allow an argument`; each followed by the CONV-14 line, exit 2.
_(UR-14, UR-16)_

**FR-17: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any operand, read standard input, or write
anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-14)_

**FR-18: Empty input and missing final LF.**
An empty input MUST yield all-zero counts and still produce its row. An input whose last byte is
not LF MUST be counted by the same rules: its final line segment contributes to _words_,
_chars_, _bytes_, and _maxlen_, but not to _lines_.
_AC:_ `dp-wc empty.txt noeol.txt`, where `noeol.txt` is `first line\nsecond line has no
newline`, → `  0 empty.txt\n 1  7 37 noeol.txt\n 1  7 37 total\n`. _(UR-01, UR-02)_

## 5. Non-functional requirements

| ID     | Category                                          | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Verification                                                     |
| :----- | :------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :--------------------------------------------------------------- |
| NFR-01 | Portability                                       | The report and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | CI black-box tests on 3 OSes                                     |
| NFR-02 | Cross-platform focus: locale-independent counting | Every count MUST be computed from the byte-level definitions of FR-04 … FR-08. Results MUST NOT depend on locale variables (`LANG`, `LC_ALL`, `LC_CTYPE`, …), the platform's default encoding or wide-character size (for example 16-bit `wchar_t` on Windows), the console code page, or text-mode I/O. Inputs MUST be opened in binary mode on every platform, and standard input MUST be switched to binary mode where the platform distinguishes it.                                                                                                                                                                                                                        | CI black-box tests on 3 OSes; code review                        |
| NFR-03 | Memory                                            | Memory use MUST be bounded by a constant independent of input size: inputs MUST be processed in a streaming fashion with a fixed-size read buffer of at most 1 MiB, never loading an entire input. The only state that may grow is the per-operand report row (O(number of operands)). Peak memory MUST stay under 64 MiB when counting a 1 GiB file.                                                                                                                                                                                                                                                                                                                           | Measurement; code review                                         |
| NFR-04 | Performance                                       | Counting all five columns of a 100 MiB file MUST take under 2 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                  | Measurement                                                      |
| NFR-05 | Streaming correctness                             | Every count MUST be independent of how the input is divided into reads. In particular a multibyte sequence, a word, or a line segment split across two (or more) buffers MUST be counted exactly once, and a truncated sequence at a buffer boundary MUST NOT be classified as invalid until the following bytes (or end-of-input) are known. Implementers MUST provide unit tests that feed the same input to the counting engine in chunks of every size from 1 to at least 8 bytes and compare the results with a single-chunk run, including inputs in which a 2-, 3-, and 4-byte sequence is split at every possible offset and inputs that end with a truncated sequence. | Unit tests; hidden black-box test with a file larger than 64 KiB |
| NFR-06 | Robustness                                        | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24). Counts MUST use integers of at least 64 bits.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Unit + black-box tests                                           |
| NFR-07 | Maintainability                                   | Option parsing, the incremental counting engine, report formatting, and I/O MUST be separate units.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Design review                                                    |
| NFR-08 | Testability                                       | The counting engine (state + "feed chunk" + "finish") and the report formatter (rows → bytes, including W) MUST be pure, I/O-free units covered by unit tests.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | Code review                                                      |
| NFR-09 | Build                                             | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | CI                                                               |
| NFR-10 | Security                                          | The tool MUST read only the files named by its operands and standard input, MUST NOT modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Inspection                                                       |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-wc --help' for more information.`

| Trigger                                                                                        | Exact first line                                   |
| :--------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| Unknown short option `x`                                                                       | `dp-wc: invalid option -- 'x'`                     |
| Unknown or abbreviated long option token `T`                                                   | `dp-wc: unrecognized option 'T'`                   |
| `--NAME=…` for any of `lines`, `words`, `chars`, `bytes`, `max-line-length`, `help`, `version` | `dp-wc: option '--NAME' doesn't allow an argument` |

Runtime errors (the tool continues with the next operand; final exit status 1):

| Trigger                                                       | Exact message                         |
| :------------------------------------------------------------ | :------------------------------------ |
| Operand `F` does not exist                                    | `dp-wc: F: No such file or directory` |
| Operand `F` cannot be opened or read because access is denied | `dp-wc: F: Permission denied`         |
| Operand `F` is a directory                                    | `dp-wc: F: Is a directory`            |
| A component of operand `F` is not a directory                 | `dp-wc: F: Not a directory`           |
| Any other open or read failure of operand `F`                 | `dp-wc: F: Input/output error`        |
| Any of the above for standard input                           | the same message with `F` = `-`       |

## 7. Verification

| Method                                              | Applies to                                  |
| :-------------------------------------------------- | :------------------------------------------ |
| Black-box test (public, `tests/public/`, 10 cases)  | FR-01 … FR-11, FR-13, FR-14                 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-02, FR-04 … FR-13, FR-15 … FR-18, NFR-05 |
| Unit test (written by the implementer)              | FR-04 … FR-09, FR-11, NFR-05, NFR-08        |
| Measurement                                         | NFR-03, NFR-04                              |
| Inspection / review                                 | NFR-02, NFR-07, NFR-10                      |

Public test map:

| Test | Command                               | Verifies                               |
| :--- | :------------------------------------ | :------------------------------------- |
| 01   | `dp-wc poem.txt`                      | FR-01, FR-09, FR-10                    |
| 02   | `dp-wc -l poem.txt`                   | FR-02, FR-04                           |
| 03   | `dp-wc --words poem.txt`              | FR-02, FR-05                           |
| 04   | `dp-wc -mc utf8.txt`                  | FR-02, FR-06, FR-08, CONV-07           |
| 05   | `dp-wc --max-line-length poem.txt`    | FR-07                                  |
| 06   | `dp-wc -L -c -m -w -l utf8.txt`       | FR-02, FR-04 … FR-09                   |
| 07   | `dp-wc poem.txt utf8.txt`             | FR-09, FR-11                           |
| 08   | `dp-wc < poem.txt`                    | FR-03, FR-10                           |
| 09   | `dp-wc poem.txt missing.txt crlf.txt` | FR-05 (CR is whitespace), FR-11, FR-13 |
| 10   | `dp-wc --help`                        | FR-14                                  |

Fixture contents for the public tests (`tests/fixtures/`): `poem.txt` is 93 bytes of ASCII
text in five LF-terminated lines, including a TAB, a doubled space, an empty line, and leading
and trailing spaces; `utf8.txt` is 93 bytes of UTF-8 text in four lines containing 2-, 3-, and
4-byte sequences; `crlf.txt` is 41 bytes in four CRLF-terminated lines, one of them empty.

## 8. Traceability (URD → SRS)

| User requirement | System requirements                   |
| :--------------- | :------------------------------------ |
| UR-01            | FR-01, FR-18                          |
| UR-02            | FR-02, FR-04, FR-05, FR-08, FR-18     |
| UR-03            | FR-02                                 |
| UR-04            | FR-06                                 |
| UR-05            | FR-06                                 |
| UR-06            | FR-05, FR-06, FR-07, NFR-02, CONV-06  |
| UR-07            | FR-10, FR-11                          |
| UR-08            | FR-09                                 |
| UR-09            | FR-03, FR-10, FR-12, CONV-26          |
| UR-10            | FR-11, FR-13, CONV-16, CONV-17        |
| UR-11            | FR-07                                 |
| UR-12            | NFR-03, NFR-04, NFR-05                |
| UR-13            | FR-14, FR-15                          |
| UR-14            | FR-16, FR-17                          |
| UR-15            | FR-08, FR-09, NFR-01, NFR-02, CONV-03 |
| UR-16            | FR-16, CLI-CONV                       |
| UR-17            | NFR-09                                |
