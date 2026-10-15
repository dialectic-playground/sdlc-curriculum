<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Common CLI Conventions (CLI-CONV)](#common-cli-conventions-cli-conv)
  - [1. Program identity](#1-program-identity)
  - [2. Bytes, encodings, and line endings](#2-bytes-encodings-and-line-endings)
  - [3. Option syntax](#3-option-syntax)
  - [4. Diagnostics](#4-diagnostics)
    - [4.1 Usage errors (exit status 2)](#41-usage-errors-exit-status-2)
    - [4.2 Runtime errors (exit status 1 unless the SRS says otherwise)](#42-runtime-errors-exit-status-1-unless-the-srs-says-otherwise)
  - [5. Exit status](#5-exit-status)
  - [6. Paths and traversal](#6-paths-and-traversal)
  - [7. Standard options and help text](#7-standard-options-and-help-text)
  - [8. Robustness](#8-robustness)
  - [9. Conditions under the black-box test harness](#9-conditions-under-the-black-box-test-harness)
  - [10. Data input, numbers, prompts, and randomness](#10-data-input-numbers-prompts-and-randomness)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Common CLI Conventions (CLI-CONV)

| Field       | Value                                                              |
| :---------- | :----------------------------------------------------------------- |
| Document ID | CLI-CONV                                                           |
| Version     | 1.0.0                                                              |
| Applies to  | Every tool in `projects/00-hello-world` … `projects/52-spacecraft` |
| Status      | Normative                                                          |

This document defines behavior that every curriculum tool shares. Each project's Software
Requirements Specification (SRS) incorporates this document by reference. Where an SRS states
something different, **the SRS takes precedence** for that tool.

Requirement IDs in this document use the prefix `CONV-`. An SRS cites them in its traceability
section. The keywords **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used as defined in
RFC 2119.

---

## 1. Program identity

- **CONV-01**: Every tool has a fixed _canonical name_ (for example `dp-cat`), given in its SRS.
  Diagnostics, help text, and version output MUST use the canonical name. They MUST NOT use
  `argv[0]`, which differs across platforms, install methods, and file extensions such as
  `.exe`.
- **CONV-02**: The `--version` option MUST print exactly one line and exit with status 0:

  ```text
  <canonical-name> (dialectic-playground) 1.0.0
  ```

## 2. Bytes, encodings, and line endings

- **CONV-03**: Every line terminator a tool _generates_ (in help text, diagnostics, reports, and
  so on) MUST be a single LF (`0x0A`) on every platform, including Windows. On Windows,
  implementations MUST write standard output and standard error in binary mode. Text-mode
  newline translation to CRLF is a conformance failure.
- **CONV-04**: Unless the tool's SRS says otherwise, data a tool _copies_ from its input (file
  contents, stdin) MUST be passed through byte-for-byte. CR (`0x0D`) bytes in the input are data,
  not line terminators, and are preserved.
- **CONV-05**: Command-line arguments are text. On POSIX they are bytes, interpreted as UTF-8.
  On Windows they are the UTF-16 command line, converted to UTF-8. When a tool echoes an
  argument (in output or in a diagnostic), it MUST emit the argument's UTF-8 encoding exactly.
- **CONV-06**: Tools MUST NOT change their behavior based on locale environment variables
  (`LANG`, `LC_ALL`, `LC_*`) or terminal type. Output contains no ANSI color or escape
  sequences unless the SRS explicitly specifies them. Numbers are written in plain ASCII decimal
  with no digit grouping.

## 3. Option syntax

Unless a tool's SRS specifies different parsing (for example, `dp-echo` and `dp-env` do):

- **CONV-07: Short options.** A short option is `-` followed by one letter. Short options that
  take no argument MAY be bundled: `-nb` means `-n -b`. If a short option takes an argument, the
  argument is either the rest of the same token (`-n5`) or, when that is empty, the next token
  (`-n 5`). Once a short option inside a bundle takes an argument, it consumes the rest of the
  token.
- **CONV-08: Long options.** A long option is `--` followed by its full name. Abbreviations are
  **not** accepted. A long option that takes a required argument accepts `--name=value` or
  `--name value`.
- **CONV-09: Terminator.** The token `--` ends option processing. It is consumed, and every
  token after it is an operand.
- **CONV-10: Operands.** A token that does not start with `-`, or that is exactly `-`, is an
  operand. Options and operands MAY be interleaved (`dp-cat a.txt -n` is the same as
  `dp-cat -n a.txt`). Where a tool reads files, the operand `-` means standard input.
- **CONV-11: Repetition.** If an option that takes a value is repeated, the last occurrence
  wins. Repeating a flag (an option with no value) has the same effect as giving it once.
- **CONV-12: Scan order.** Arguments are examined from left to right. As soon as the first
  `--help` or `--version` is reached, the tool prints the help or version output and exits
  with status 0. If an option _syntax_ error (unknown option, missing option argument, or an
  argument given to an option that takes none) is found earlier in the scan, that usage error
  is reported instead. Operands are only collected during the scan, and option _values_ are
  only recorded. Errors about operands (missing or extra) and about option values are
  detected after the scan completes, so they never take precedence over `--help` or
  `--version`. For example, `<tool> extra --help` and `<tool> --count 0 --help` print the help,
  while `<tool> -x --help` reports the invalid option. Usage errors are always detected before
  any input is read or any output is written.

## 4. Diagnostics

Every diagnostic is written to **standard error** as one line. It starts with the canonical
name, a colon, and a space. Text in angle brackets is replaced as described. All other text is
literal.

### 4.1 Usage errors (exit status 2)

- **CONV-13**: Usage errors use the following exact formats:

| Condition                                                         | Message                                               |
| :---------------------------------------------------------------- | :---------------------------------------------------- |
| Unknown short option `x`                                          | `<tool>: invalid option -- 'x'`                       |
| Unknown long option (full token as given, including any `=value`) | `<tool>: unrecognized option '<token>'`               |
| Short option `x` missing its argument                             | `<tool>: option requires an argument -- 'x'`          |
| Long option missing its argument                                  | `<tool>: option '--<name>' requires an argument`      |
| Long option given `=value` but takes no argument                  | `<tool>: option '--<name>' doesn't allow an argument` |
| Invalid option value                                              | `<tool>: invalid argument '<value>' for '<option>'`   |
| Required operand absent                                           | `<tool>: missing operand`                             |
| Surplus operand (the first surplus one)                           | `<tool>: extra operand '<operand>'`                   |

In the "Invalid option value" row, `<option>` is the option as written, without any value: for
example `-n` or `--lines`.

- **CONV-14**: Every usage error message MUST be followed by this line, after which the tool
  exits with status **2** without reading input:

  ```text
  Try '<tool> --help' for more information.
  ```

- **CONV-15**: Values are inserted between the single quotes exactly as given, with no escaping.
  An empty value appears as `''`.

### 4.2 Runtime errors (exit status 1 unless the SRS says otherwise)

- **CONV-16**: Errors that involve a file path use the format `<tool>: <path>: <reason>`.
  `<path>` is the path as the user wrote it, or as the tool constructed it (see CONV-20).
  `<reason>` is taken from this fixed table, never from the operating system's message text:

| Condition                                                                    | `<reason>`                  |
| :--------------------------------------------------------------------------- | :-------------------------- |
| Path does not exist (ENOENT, `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND`) | `No such file or directory` |
| Access denied (EACCES, EPERM, `ERROR_ACCESS_DENIED`)                         | `Permission denied`         |
| A directory was given where a file was needed                                | `Is a directory`            |
| A path component is not a directory (ENOTDIR)                                | `Not a directory`           |
| Any other I/O failure                                                        | `Input/output error`        |

- **CONV-17**: When a tool processes several operands, an error on one operand MUST NOT stop it
  from processing the rest, unless the SRS says otherwise. The final exit status is 1 if any
  operand failed.

## 5. Exit status

- **CONV-18**: Unless a tool's SRS overrides it:

| Status | Meaning                                                    |
| :----- | :--------------------------------------------------------- |
| 0      | Success                                                    |
| 1      | Runtime failure (at least one operand or operation failed) |
| 2      | Usage error (CONV-13, CONV-14)                             |

`dp-grep`, `dp-diff`, `dp-env`, and `dp-chk-sort` define their own exit-status tables.

## 6. Paths and traversal

- **CONV-19**: Paths given by the user are echoed back exactly as given. Windows users may type
  `a\b`, and that is what gets echoed.
- **CONV-20**: When a tool _constructs_ a path by joining a directory and an entry name (for
  example, during recursive traversal), it MUST use `/` as the separator on every platform.
  Windows APIs accept `/`, and this keeps output identical across operating systems.
- **CONV-21**: When a tool lists directory entries, it MUST visit them in ascending
  **byte-wise** order of their UTF-8-encoded names. That order is case-sensitive and
  locale-independent. The entries `.` and `..` are never visited.

## 7. Standard options and help text

- **CONV-22**: Every tool accepts `--help` and `--version`. Neither takes an argument.
- **CONV-23**: `--help` prints the tool's help text to **standard output** and exits with status 0. The help text is given _verbatim_ in the "Help output" section of the tool's user manual.
  It is part of the specification and MUST be reproduced byte-for-byte, including a trailing
  LF on the last line. Help text follows this layout:

  ```text
  Usage: <tool> [OPTION]... <operands>
  <one-line summary>

  <optional paragraphs>

  Options:
    -x, --long-name        description
        --help             display this help and exit
        --version          output version information and exit
  ```

## 8. Robustness

- **CONV-24**: A tool MUST NOT crash, print a stack trace, or panic for any input or argument
  combination. Every failure is reported through the diagnostics defined above.
- **CONV-25**: If writing to standard output fails because the reader has gone away (EPIPE, a
  broken pipe), the tool MUST terminate promptly without printing a diagnostic. Its exit status
  in that case is unspecified. If writing to standard output fails for any other reason (for
  example, a full disk), the tool writes `<tool>: write error` to standard error and exits with
  status 1, unless its SRS specifies another status.
- **CONV-26**: Tools MUST NOT read standard input unless their SRS says they do. A tool that
  reads stdin MUST work when stdin is empty, redirected from a file, or a pipe.

- **CONV-31: Resource limits and runtimes.** Memory limits in a project's NFRs apply to
  natively compiled implementations. An implementation on a managed runtime or interpreter
  (for example the JVM, .NET, Node.js, Python, Ruby, Perl, PHP, or Julia) meets a memory
  limit when its peak memory, minus the runtime's own baseline, is within the limit. The
  baseline is the peak memory of starting the runtime with an empty program. Run-time limits
  state their interpreted-runtime allowance explicitly.

## 9. Conditions under the black-box test harness

`shared/tools/run-tests.py` runs every test under these conditions, which implementations can
rely on:

- **CONV-27**: The tool is started directly, never through a shell. A tool may be a native
  executable or a script with a `#!` line. On Windows, the runner starts such a script's
  interpreter directly, resolving the `#!` interpreter on `PATH`. Its working directory is a
  fresh temporary copy of the suite's `fixtures/` directory, and the copied files have fresh
  modification times.
- **CONV-28**: Standard input is empty (the null device) unless the test redirects it with
  `< file`.
- **CONV-29**: The environment is minimal: `PATH`, plus the variables Windows needs to start
  processes (`SYSTEMROOT`, `WINDIR`, `COMSPEC`, `PATHEXT`, `TEMP`, `TMP`), plus whatever the
  test sets explicitly.
- **CONV-30**: Standard output, standard error, and the exit status are each compared
  **byte-for-byte** against the expected-output files.

## 10. Data input, numbers, prompts, and randomness

The tools of Projects 11–52 read numeric and textual _data_ rather than arbitrary files, and
several of them come from interactive programs. This section gives them one shared vocabulary.
A convention in this section applies to a tool only where its SRS says so; the SRS states which
inputs are read as tokens, which numeric grammar each value uses, and which prompts exist.

- **CONV-32: Tokens and line numbers.** When an SRS says an input is read as _tokens_, the
  input is divided into maximal runs of non-whitespace bytes. The whitespace bytes are exactly
  `0x20` (space), `0x09` (TAB), `0x0A` (LF), `0x0B` (VT), `0x0C` (FF), and `0x0D` (CR), so CRLF
  input reads exactly like LF input. The _line number_ of a token is 1 plus the number of LF
  bytes that precede its first byte. The _end-of-input line number_ is 1 plus the number of LF
  bytes in the whole input. Tokens are compared and echoed as bytes; no decoding is applied.

- **CONV-33: Numeric grammars.** A token is valid for a numeric value only if it matches the
  value's grammar in full. No other spelling is accepted: no digit grouping, no hexadecimal,
  no `inf` or `nan`, no leading or trailing characters.

  | Grammar   | Pattern (ASCII only)                                   | Value                                                                                                                                                                                   |
  | :-------- | :----------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | _integer_ | `[+-]?[0-9]+`                                          | The decimal value. It MUST lie in −2⁶³ … 2⁶³−1; otherwise the token is invalid. Leading zeros are allowed.                                                                              |
  | _real_    | `[+-]?([0-9]+(\.[0-9]*)?\|\.[0-9]+)([eE][+-]?[0-9]+)?` | The IEEE 754 binary64 value nearest to the exact decimal value (round to nearest, ties to even). A token whose converted value overflows to infinity is invalid. `-0` is negative zero. |

  An SRS MAY further restrict a value's range. Such a restriction is checked after the grammar
  and reported with its own message (CONV-34).

- **CONV-34: Data diagnostics.** A problem with the _content_ of an input is reported on
  standard error as one line:

  ```text
  <tool>: <source>:<line>: <message>
  ```

  `<source>` is the operand naming the input, exactly as given, or `-` for standard input.
  `<line>` is the line number of the offending token or line (CONV-32), or the end-of-input
  line number when the input ends early. The standard messages are:

  | Condition                                                   | `<message>`                    |
  | :---------------------------------------------------------- | :----------------------------- |
  | A token is not a valid _integer_                            | `invalid integer '<token>'`    |
  | A token is not a valid _real_                               | `invalid number '<token>'`     |
  | A valid number lies outside the range the SRS allows        | `value out of range '<token>'` |
  | The input ends where the SRS requires another value or line | `unexpected end of input`      |

  `<token>` is inserted as its exact bytes, without escaping (CONV-15). An SRS MAY define
  further messages in the same format. Unless the SRS says otherwise, a data diagnostic ends
  processing of that input, output already produced for earlier records is kept, and the exit
  status is 1. An SRS MAY instead declare a diagnostic _continuing_: processing goes on after
  it (for example, a dialog asks again), and the final exit status is 1 unless the SRS says
  otherwise.

- **CONV-35: Number formatting.** Real numbers are written with one of two rules, which every
  SRS names explicitly:

  - **`FIX(x, n)`**: _x_ rounded to exactly _n_ digits after the decimal point, computed from the
    **exact** binary64 value of _x_ (not from a rounded product), with an exact tie rounded to
    the even digit. No exponent is used; _n_ = 0 writes no decimal point. If the rounded value
    is zero, no minus sign is written (`-0.0000001` with _n_ = 6 is `0.000000`). This is C's
    `printf("%.nf")` with negative zero suppressed.
  - **`GEN(x, p)`**: _x_ with _p_ significant digits, as C's `printf("%.pg")`. Let _X_ be the
    decimal exponent of _x_ after rounding to _p_ significant digits (ties to even, from the
    exact value). If −4 ≤ _X_ < _p_, the value is written as `FIX(x, p − 1 − X)`; otherwise in
    exponential form `d.ddd…e±XX` with _p_ − 1 fraction digits and at least two exponent digits.
    In both forms, trailing zeros in the fraction are removed, and so is a decimal point left
    with no digits after it. Zero is `0` (never `-0`). For example, with _p_ = 6:
    `8.688323` → `8.68832`, `63567.0` → `63567`, `1234567.0` → `1.23457e+06`, `0.0001` →
    `0.0001`, `0.00001` → `1e-05`.

  Integers are written in plain decimal (CONV-06). A `-` precedes negative integers.

- **CONV-36: Prompts.** A tool whose SRS lists prompts accepts the flag `-p`, `--prompt`.
  Without it, no prompt is ever written. With it, the tool writes each prompt to **standard
  error**, byte for byte as the SRS gives it, immediately before the read the prompt belongs
  to, and flushes standard error before reading. Prompts are never written to standard output,
  so standard output is identical with and without `--prompt`. A prompt is written even if the
  read that follows reaches the end of the input. Nothing is inserted after a prompt: a
  diagnostic that follows it on standard error continues the same line.

- **CONV-37: Legacy end-of-file marker.** For inputs that an SRS designates as _text data_, a
  run of one or more `0x1A` bytes (Ctrl-Z, the CP/M and MS-DOS end-of-file marker) that extends
  to the very end of the input is ignored, as if the input ended before it. A `0x1A` byte
  followed by any other byte is ordinary data. A tool that processes its input as a stream
  meets this rule by treating a final token or line made only of `0x1A` bytes as absent.

- **CONV-38: Pseudo-random numbers.** Tools that simulate chance use the portable generator
  given as an example in the ANSI C standard's description of `rand()`, so every
  implementation draws the same numbers. The generator has a 32-bit unsigned state _S_. Each
  draw sets _S_ ← (_S_ × 1103515245 + 12345) mod 2³² and yields _r_ = ⌊_S_ / 65536⌋ mod 32768,
  an integer in 0 … 32767. The initial state is the seed. The seed is 1 by default, as in C
  when `srand` is never called, and is set with the option `--seed=SEED`, where SEED consists
  only of ASCII digits and lies in 0 … 4294967295; any other SEED is an invalid option value
  (CONV-13). The SRS states every derived quantity (for example a die face is 1 + (_r_ mod 6))
  and the exact order of draws.
