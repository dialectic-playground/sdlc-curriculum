<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-kinder](#software-requirements-specification-srs--dp-kinder)
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

# Software Requirements Specification (SRS) — dp-kinder

| Field                     | Value                                                   |
| :------------------------ | :------------------------------------------------------ |
| Document ID               | SRS-11                                                  |
| Project                   | `11-kinder` — Console Output & Environment Verification |
| Product                   | `dp-kinder` (canonical name)                            |
| Version                   | 1.0.0                                                   |
| Status                    | Approved (pre-written by the curriculum)                |
| Parent document           | `URD.md` (URD-11)                                       |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)            |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                    |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-kinder`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-kinder` writes one fixed line of text to standard output and exits. It has no options of
its own besides `--help` and `--version`, takes no operands, reads no input, and touches no
files.

### 1.3 Definitions

| Term    | Definition                                                                                                                                 |
| :------ | :----------------------------------------------------------------------------------------------------------------------------------------- |
| LF      | The line-feed byte, `0x0A`                                                                                                                 |
| Message | The 29 bytes `ANSI--A kinder and gentler C!` followed by LF (30 bytes in all)                                                              |
| Operand | An argument that is not an option (CONV-10): a token that does not start with `-`, the token `-`, the empty token, or any token after `--` |

### 1.4 References

- URD-11: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §1.1 (informative; see §2.5)
- SRS-00 (`projects/00-hello-world/specs/SRS.md`): the curriculum's first tool, whose option
  handling this tool shares

## 2. Overall description

### 2.1 Product perspective

`dp-kinder` is a standalone executable. Its interfaces are the command line, standard output,
standard error, and the exit status. It belongs to the curriculum's applications-programming
track (Projects 11–52) and adapts §1.1 of Johnsonbaugh & Kalin, _Applications Programming in
ANSI C_. It is the track's environment check: the smallest program that exercises the build,
install, and test contract and the CLI-CONV argument scan.

### 2.2 Product functions

1. Print the message `ANSI--A kinder and gentler C!`.
2. Display help and version information.
3. Detect and report usage errors, including operands.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.

### 2.4 Assumptions

- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Standard input may be a terminal, a pipe, a file, or the null device. It is never read.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §1.1 prints the line `ANSI--A kinder and gentler C!` and returns a
success status. `dp-kinder` keeps:

- the message, byte for byte: capital letters, the two hyphens, the spaces, and the final `!`,
  followed by exactly one line terminator and nothing else;
- the absence of input and of any other output;
- exit status 0 on success.

It changes the following, for the reasons given:

- **Standard options.** Like every curriculum tool, `dp-kinder` answers `--help` and
  `--version` (FR-05, FR-06). It deliberately gains no option that changes the message: a
  tool that greets a chosen name a chosen number of times already exists as `dp-hello`
  (Project 00), and this project's purpose is to verify the environment, not to add features.
- **Arguments are checked.** The textbook program ignores its command line. `dp-kinder`
  rejects every operand and every unknown option with a CONV-13 usage error and exit status 2
  (FR-04, FR-07), so that a mistyped invocation in a script is noticed.
- **Line endings are fixed.** On MS-DOS and Windows, the textbook program's line terminator
  becomes CR LF when standard output is in text mode. `dp-kinder` writes LF only on every
  platform (CONV-03, NFR-02).
- **No prompts.** The program reads nothing, so `-p`, `--prompt` (CONV-36) does not exist.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. None of CONV-32 … CONV-38
applies: the tool reads no data (CONV-32 … CONV-34, CONV-37), writes no real numbers
(CONV-35), has no prompts (CONV-36), and uses no randomness (CONV-38). Option syntax follows
CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-15, and the exit statuses are those of
CONV-18. Standard input is not read (CONV-26). The tool copies no input to its output, so
CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-kinder
dp-kinder --help
dp-kinder --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                       |
| :---- | :---------- | :------- | :------ | :-------------------------------- |
| —     | `--help`    | none     | —       | Print the help text and exit 0    |
| —     | `--version` | none     | —       | Print the version line and exit 0 |

The tool has no short options. Option syntax (`--`, scan order) follows CONV-08 … CONV-12.

### 3.3 Operands

`dp-kinder` accepts **no operands** (FR-04).

### 3.4 Standard input

Not read (CONV-26), whatever it is connected to (FR-02).

### 3.5 Standard output

The message on success (FR-01), the help text (FR-05), or the version line (FR-06). Nothing on
a usage error.

### 3.6 Standard error

Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition                                                       |
| :----- | :-------------------------------------------------------------- |
| 0      | The message was printed, or `--help` / `--version` was handled  |
| 1      | Standard output could not be written (other than a broken pipe) |
| 2      | Usage error                                                     |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `input.txt` is the fixture file in
`tests/fixtures/`.

**FR-01: Message.**
When the arguments are valid and request neither help nor version, the tool MUST write exactly
the message (section 1.3) to standard output, write nothing to standard error, and exit with
status 0. The message has no leading or trailing spaces, no byte-order mark, and no CR.
_AC:_ `dp-kinder` → stdout `ANSI--A kinder and gentler C!\n`, stderr empty, exit 0.
_(UR-01, UR-02)_

**FR-02: Standard input is not read.**
The tool MUST NOT read standard input (CONV-26). Its output MUST NOT depend on what standard
input is connected to, and it MUST NOT wait for input at a terminal.
_AC:_ `dp-kinder < input.txt` → the same output as FR-01, exit 0. _(UR-03)_

**FR-03: Terminator.**
The token `--` ends option processing and is consumed (CONV-09). `--` with nothing after it
leaves no operand, so the invocation is valid; every token after the first `--`, including a
second `--`, `-`, and `--help`, is an operand (FR-04).
_AC:_ `dp-kinder --` → the message, exit 0; `dp-kinder -- --help` →
`dp-kinder: extra operand '--help'`, exit 2. _(UR-07)_

**FR-04: Operands rejected.**
If the scan (CONV-12) collects any operand, the tool MUST report
`dp-kinder: extra operand '<first operand>'` followed by the CONV-14 line, and exit with
status 2. The operand is echoed exactly as given (CONV-05, CONV-15): an empty operand appears
as `''`, `-` as `'-'`, and a non-ASCII operand as its UTF-8 bytes. Operands are checked only
after the whole argument list has been scanned, so `--help` or `--version` anywhere in the list
takes precedence (FR-08).
_AC:_ `dp-kinder extra` → `dp-kinder: extra operand 'extra'`; `dp-kinder -` →
`dp-kinder: extra operand '-'`; `dp-kinder a b` → `dp-kinder: extra operand 'a'`;
`dp-kinder ''` → `dp-kinder: extra operand ''`; each exit 2. _(UR-06)_

**FR-05: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in FR-08.
_AC:_ `dp-kinder --help` matches the user manual exactly. _(UR-04)_

**FR-06: Version.**
`--version` MUST write `dp-kinder (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-05)_

**FR-07: Unknown and malformed options.**
Every token that starts with `-`, is not exactly `-` or `--`, and appears before any `--` is an
option. Because the tool has no short options, any short option letter MUST be reported as
`dp-kinder: invalid option -- '<letter>'`, naming the first letter after the `-`. Any long
option other than `--help` and `--version` MUST be reported as
`dp-kinder: unrecognized option '<token>'` with the whole token, including any `=value`. Long
options MUST NOT be abbreviated (CONV-08): `--hel` is unrecognized, and so is `---`.
`--help=…` and `--version=…` MUST be reported as
`dp-kinder: option '--help' doesn't allow an argument` (or `'--version'`). Each message is
followed by the CONV-14 line, and the exit status is 2.
_AC:_ `dp-kinder -x` → `dp-kinder: invalid option -- 'x'`; `dp-kinder -h` →
`dp-kinder: invalid option -- 'h'`; `dp-kinder --verbose` →
`dp-kinder: unrecognized option '--verbose'`; `dp-kinder --help=yes` →
`dp-kinder: option '--help' doesn't allow an argument`; each exit 2. _(UR-06, UR-07)_

**FR-08: Scan order.**
Arguments MUST be examined from left to right (CONV-12). The first `--help` or `--version`
reached ends the scan: the tool prints the help or version output and exits 0, ignoring every
later argument. An option syntax error (FR-07) reached earlier in the scan is reported instead.
Operand errors (FR-04) are detected only after a scan that reaches neither `--help` nor
`--version`.
_AC:_ `dp-kinder extra --help` → the help, exit 0; `dp-kinder -x --help` →
`dp-kinder: invalid option -- 'x'`, exit 2; `dp-kinder --help -x` → the help, exit 0;
`dp-kinder --version --help` → the version line, exit 0; `dp-kinder --help --version` → the
help, exit 0. _(UR-04, UR-05, UR-07)_

**FR-09: Error atomicity.**
When a usage error occurs, the tool MUST NOT write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-06)_

## 5. Non-functional requirements

| ID     | Category                                         | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Verification                                       |
| :----- | :----------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| NFR-01 | Portability                                      | Output MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | CI black-box tests on 3 OSes                       |
| NFR-02 | Cross-platform focus: binary-mode console output | Standard output and standard error MUST be written in binary mode on every platform, so the message ends in exactly one LF and never in CR LF, whether the output goes to a console, a pipe, or a file. No byte-order mark, code-page conversion, or console-specific API may change the bytes written; the message is plain ASCII, so it displays the same under any console code page. All output MUST be flushed before the process exits, and the exit status MUST be observable by the caller on every platform (`$?` in POSIX shells, `%ERRORLEVEL%` in `cmd.exe`, `$LASTEXITCODE` in PowerShell), including when the tool is started through a language-runtime launcher. | CI black-box tests on 3 OSes; manual console check |
| NFR-03 | Performance                                      | Wall-clock run time MUST be under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 32 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31).                                                                                                                                                                                                                                                                                                                                                                                                                                      | Measurement                                        |
| NFR-04 | Robustness                                       | The tool MUST NOT crash, panic, or print a stack trace for any argument list (CONV-24). A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Unit + black-box tests                             |
| NFR-05 | Maintainability                                  | Argument scanning, the decision of what to print, and output MUST be separate units (Principles 13, 18). The message MUST appear in exactly one place in the source.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Design review                                      |
| NFR-06 | Testability                                      | The argument scanner MUST be a pure function of the argument list, returning the action (message, help, version, or a usage error with its message) without performing output, and MUST be covered by unit tests for every acceptance criterion of FR-03, FR-04, FR-07, and FR-08.                                                                                                                                                                                                                                                                                                                                                                                               | Code review                                        |
| NFR-07 | Build                                            | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | CI                                                 |
| NFR-08 | Security                                         | The tool MUST read no files, no standard input, and no environment variables, and MUST run no subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Inspection                                         |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-kinder --help' for more information.`

| Trigger                                      | Exact first line                                                          |
| :------------------------------------------- | :------------------------------------------------------------------------ |
| Short option token `-xyz…` (any letter)      | `dp-kinder: invalid option -- 'x'`                                        |
| Unknown or abbreviated long option token `T` | `dp-kinder: unrecognized option 'T'`                                      |
| `--help=…` / `--version=…`                   | `dp-kinder: option '--help' doesn't allow an argument` (or `'--version'`) |
| Operand `X` (the first one)                  | `dp-kinder: extra operand 'X'`                                            |

Runtime errors (exit status 1):

| Trigger                                                      | Exact message            |
| :----------------------------------------------------------- | :----------------------- |
| Standard output cannot be written (other than a broken pipe) | `dp-kinder: write error` |

## 7. Verification

| Method                                                                                | Applies to                         |
| :------------------------------------------------------------------------------------ | :--------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                    | FR-01 … FR-07, FR-09               |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 10 have several steps) | FR-01, FR-03, FR-04, FR-06 … FR-09 |
| Unit test (written by the implementer)                                                | FR-03, FR-04, FR-07, FR-08, NFR-06 |
| Measurement                                                                           | NFR-03                             |
| Inspection / review                                                                   | NFR-02, NFR-05, NFR-08             |

Public test map:

| Test | Command                 | Verifies     |
| :--- | :---------------------- | :----------- |
| 01   | `dp-kinder`             | FR-01        |
| 02   | `dp-kinder --help`      | FR-05        |
| 03   | `dp-kinder --version`   | FR-06        |
| 04   | `dp-kinder < input.txt` | FR-02        |
| 05   | `dp-kinder --`          | FR-03        |
| 06   | `dp-kinder extra`       | FR-04, FR-09 |
| 07   | `dp-kinder -`           | FR-04        |
| 08   | `dp-kinder -x`          | FR-07        |
| 09   | `dp-kinder --verbose`   | FR-07        |
| 10   | `dp-kinder --help=yes`  | FR-07        |

## 8. Traceability (URD → SRS)

| User requirement | System requirements           |
| :--------------- | :---------------------------- |
| UR-01            | FR-01                         |
| UR-02            | FR-01, §3.7                   |
| UR-03            | FR-02, CONV-26                |
| UR-04            | FR-05, FR-08                  |
| UR-05            | FR-06, FR-08                  |
| UR-06            | FR-04, FR-07, FR-09           |
| UR-07            | FR-03, FR-07, FR-08, CLI-CONV |
| UR-08            | NFR-01, NFR-02, CONV-03       |
| UR-09            | NFR-03                        |
| UR-10            | NFR-07                        |
