<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-cat](#software-requirements-specification-srs--dp-cat)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
    - [1.5 Deviations](#15-deviations)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
    - [4.1 Operands, options, and input handling](#41-operands-options-and-input-handling)
    - [4.2 The output model](#42-the-output-model)
    - [4.3 Making bytes visible](#43-making-bytes-visible)
    - [4.4 Errors](#44-errors)
    - [4.5 Help, version, and usage errors](#45-help-version-and-usage-errors)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
    - [6.1 Runtime diagnostics (exit status 1; processing continues except for the write error)](#61-runtime-diagnostics-exit-status-1-processing-continues-except-for-the-write-error)
    - [6.2 Usage errors (exit status 2)](#62-usage-errors-exit-status-2)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-cat

| Field                     | Value                                        |
| :------------------------ | :------------------------------------------- |
| Document ID               | SRS-02                                       |
| Project                   | `02-cat` — Concatenate & Number Files        |
| Product                   | `dp-cat` (canonical name)                    |
| Version                   | 1.0.0                                        |
| Status                    | Approved (pre-written by the curriculum)     |
| Parent document           | `URD.md` (URD-02)                            |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018         |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-cat`. It is complete and precise
enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-cat` reads its operands (files, or standard input for `-`) in order and writes their bytes
to standard output. Optional _transforming options_ number lines, squeeze repeated blank lines,
and render non-printing bytes, tabs, and line ends visibly. Unreadable operands are reported and
skipped.

### 1.3 Definitions

| Term                | Definition                                                                                                                                                                               |
| :------------------ | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                  | The line-feed byte, `0x0A`                                                                                                                                                               |
| CR                  | The carriage-return byte, `0x0D`                                                                                                                                                         |
| TAB                 | The horizontal-tab byte, `0x09`                                                                                                                                                          |
| Operand             | A command-line argument that is not an option (CONV-10): a file path, or `-` for standard input                                                                                          |
| Input stream (S)    | The concatenation, in operand order, of every byte successfully read from the operands (§4.2)                                                                                            |
| Line                | A maximal run of bytes in S that ends with an LF (a _terminated line_), or the non-empty run of bytes after the last LF of S when S does not end with LF (the _unterminated final line_) |
| Content             | The bytes of a line excluding its terminating LF                                                                                                                                         |
| Empty line          | A terminated line whose content has length 0. A line whose content is a single CR is **not** empty                                                                                       |
| Transforming option | Any of `-A`, `-b`, `-E`, `-n`, `-s`, `-T`, `-v` and their long forms                                                                                                                     |
| Rendering           | The bytes written to standard output for a content byte (§4.4, FR-11 … FR-13)                                                                                                            |

### 1.4 References

- URD-02: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- GNU coreutils `cat` 9.x, whose semantics this specification follows except where §1.5 says
  otherwise (informative)

### 1.5 Deviations

From **CLI-CONV**:

- CONV-04 (byte-for-byte pass-through) applies only when no transforming option is given
  (FR-06). The transforming options change the output by design (FR-07 … FR-13).

There are no other deviations from CLI-CONV.

From **GNU `cat`** (informative; the requirements below are normative):

- Usage errors exit with status 2 (CONV-18), not 1.
- The GNU-only options `-e`, `-t`, and `-u` are not supported and are usage errors.
- `dp-cat` does not detect that an input file is also the output file (GNU: "input file is
  output file"). That situation is outside this specification (§2.4).

## 2. Overall description

### 2.1 Product perspective

`dp-cat` is a standalone executable. Its interfaces are the command line, the files named as
operands, standard input, standard output, standard error, and the exit status. It is the
first curriculum tool that reads files; projects 03 to 07 reuse its operand-handling and
streaming patterns.

### 2.2 Product functions

1. Concatenate any number of files and standard input to standard output.
2. Copy data byte-for-byte, including binary data and CRLF line endings.
3. Number all lines (`-n`) or non-empty lines (`-b`), continuously across operands.
4. Squeeze runs of empty lines (`-s`).
5. Render non-printing bytes (`-v`), tabs (`-T`), and line ends (`-E`) visibly.
6. Report unreadable operands and continue with the rest.
7. Display help and version information, and detect usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.

### 2.4 Assumptions

- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Operands do not name the file that standard output is redirected to. If one does, the
  behavior is not specified.
- Operand files are not modified while `dp-cat` reads them.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-cat [-AbEnsTv] [FILE]...
dp-cat --help
dp-cat --version
```

### 3.2 Options

None of the options takes an argument.

| Short | Long                 | Description                                                            | Requirement |
| :---- | :------------------- | :--------------------------------------------------------------------- | :---------- |
| `-A`  | `--show-all`         | Same as `-v -E -T`                                                     | FR-04       |
| `-b`  | `--number-nonblank`  | Number non-empty output lines; overrides `-n`                          | FR-09       |
| `-E`  | `--show-ends`        | Write `$` before each LF; render a CR directly before an LF as `^M`    | FR-13       |
| `-n`  | `--number`           | Number all output lines                                                | FR-08       |
| `-s`  | `--squeeze-blank`    | Suppress every empty line that follows an empty line                   | FR-10       |
| `-T`  | `--show-tabs`        | Render TAB as `^I`                                                     | FR-12       |
| `-v`  | `--show-nonprinting` | Render control bytes, DEL, and bytes ≥ `0x80` in `^` and `M-` notation | FR-11       |
| —     | `--help`             | Print the help text and exit 0                                         | FR-18       |
| —     | `--version`          | Print the version line and exit 0                                      | FR-19       |

Option syntax follows CONV-07 … CONV-12. Options are flags, so they can be bundled (`-nET`,
`-sb`), repeated (no additional effect, CONV-11), and interleaved with operands
(`dp-cat a.txt -n` is the same as `dp-cat -n a.txt`). An option applies to the whole run,
whatever its position among the operands. Long options are not abbreviated: `--num` is
unrecognized.

### 3.3 Operands

Zero or more FILE operands. Each is a path, interpreted relative to the working directory, or
the single character `-`, which means standard input. With no operands, the tool behaves as if
the single operand `-` were given. The empty string is a path that does not exist. Tokens after
`--` are operands even if they start with `-` (CONV-09); the token `-` remains standard input
after `--`.

### 3.4 Standard input

Read only for each `-` operand, or when there are no operands (CONV-26). Read in binary mode.
Standard input may be empty, a file, a pipe, or a terminal.

### 3.5 Standard output

The output defined by §4.2 and FR-06 … FR-13. Nothing else is ever written to standard output,
except the help text or version line.

### 3.6 Standard error

Diagnostics only (§6). Nothing when every operand was read successfully.

### 3.7 Exit status

| Status | Condition                                                                                                        |
| :----- | :--------------------------------------------------------------------------------------------------------------- |
| 0      | Every operand was read to its end and all output was written; or `--help` / `--version` was handled              |
| 1      | At least one operand could not be opened or read (FR-14, FR-15), or standard output could not be written (FR-16) |
| 2      | Usage error (FR-20)                                                                                              |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.

### 4.1 Operands, options, and input handling

**FR-01: Operand processing order.**
The tool MUST process the operands strictly from left to right. It MUST finish with one
operand (read it to end-of-file, or detect its failure) before opening the next. With no
operands, it MUST process standard input as if `-` had been given.
_AC:_ `dp-cat alpha.txt beta.txt` writes the bytes of `alpha.txt` followed by those of
`beta.txt`. `dp-cat < stdin.txt` writes the bytes of `stdin.txt`. _(UR-01, UR-02)_

**FR-02: Standard input operand.**
Each `-` operand MUST read standard input from its current position until end-of-file. The
tool MUST NOT close standard input after a `-` operand, so `-` may appear any number of times.
A later `-` continues reading where the previous one stopped. When standard input is a file or
a pipe that has reached end-of-file, a later `-` contributes no bytes. When it is a terminal,
each `-` reads until the user signals end-of-file.
_AC:_ `dp-cat alpha.txt - beta.txt < stdin.txt` writes alpha, stdin, beta in that order.
`dp-cat - alpha.txt - < stdin.txt` writes stdin's bytes once, followed by alpha. _(UR-02)_

**FR-03: File handling.**
Each file operand MUST be opened for reading in binary mode. No newline translation, character
decoding, or end-of-file-byte (`0x1A`) handling of any kind may be applied. The file MUST be
closed when its end is reached or a failure is detected, before the next operand is opened.
At most one operand file is open at any time. Naming the same file several times reads it
afresh each time.
_AC:_ `dp-cat folder crlf.txt` writes `crlf.txt` with its CR bytes intact.
`dp-cat -T - < controls.bin` passes the `0x1A` byte and everything after it through. _(UR-03, UR-10)_

**FR-04: Option interaction.**
`-A` MUST have exactly the effect of `-v -E -T` together. The effects of `-v`, `-T`, and `-E`
combine as described in FR-11 … FR-13. Numbering and squeezing combine with them as described
in FR-07 … FR-10. `-b` overrides `-n` (FR-09). Every combination of options is valid.
_AC:_ `dp-cat -A controls.bin no-eol.txt` equals `dp-cat -vET controls.bin no-eol.txt`.
_(UR-06, UR-13)_

### 4.2 The output model

**FR-05: One continuous stream.**
The output MUST equal the transformation of the input stream S, the concatenation of the bytes
read from all operands in order, as if S were a single file. Operand boundaries are invisible.
In particular:

- line numbering continues from one operand to the next;
- a line that is not terminated at the end of one operand continues with the first bytes of the
  next operand. It receives no new line number, and no `$` or LF is inserted between them;
- squeezing (FR-10) and the CR-before-LF rule (FR-13) apply across operand boundaries;
- an operand that fails (FR-14, FR-15) contributes to S exactly the bytes that were read from it
  before the failure. That is no bytes when it could not be opened.

_AC:_ `dp-cat -nE no-eol.txt alpha.txt` writes
`thout newlinealpha one$\n     2\talpha two$\n`.
`dp-cat -n alpha.txt beta.txt no-eol.txt` numbers lines 1 to 5. _(UR-04, UR-13)_

**FR-06: Plain copy.**
When no transforming option is given, the output MUST be exactly S, byte for byte. This
includes NUL bytes, CR bytes, bytes that are not valid UTF-8, and a missing final LF
(CONV-04).
_AC:_ `dp-cat alpha.txt beta.txt` and `dp-cat folder crlf.txt` reproduce their inputs exactly.
_(UR-01, UR-03)_

**FR-07: Line rendering.**
When at least one transforming option is given, the tool MUST divide S into lines (§1.3) and
write each line that is not suppressed by FR-10 as the concatenation of:

1. the line-number prefix, if the line is numbered (FR-08, FR-09);
2. the rendering of each content byte, in order (FR-11, FR-12, FR-13);
3. for a terminated line: `$` followed by LF if `-E` is in effect, otherwise LF alone. For the
   unterminated final line: nothing.

No other bytes are written. In particular, the tool never adds a final LF that S lacks.
_AC:_ `dp-cat -n alpha.txt beta.txt no-eol.txt` ends with
`thout newline` and no LF. _(UR-03, UR-04)_

**FR-08: Number all lines (`-n`).**
With `-n` and without `-b`, every output line MUST be numbered, including empty lines. A
counter starts at 0 for each run of the tool and is incremented before each numbered line is
written, so the first numbered line gets 1. The prefix is the counter in ASCII decimal without
leading zeros, right-aligned with spaces in a field 6 characters wide, followed by one TAB. In
other words, `printf "%6d\t"`. A counter of more than six digits is written in full with no
padding (`1000000\t`). Lines suppressed by `-s` are not numbered and do not advance the
counter. Implementations MUST count correctly to at least 999 999 999 999 (12 digits).
_AC:_ `dp-cat -n alpha.txt beta.txt no-eol.txt` writes `…`5\t…`
_(UR-04)_

**FR-09: Number non-empty lines (`-b`).**
With `-b`, exactly the non-empty output lines MUST be numbered, using the counter and prefix of
FR-08. Empty lines get no prefix and do not advance the counter. `-b` overrides `-n`, whatever
their order on the command line. A line whose content is only a CR is not empty and is
numbered.
_AC:_ `dp-cat -b blanks.txt` numbers `first`, `second`, and `third` as 1, 2, and 3, and leaves
the blank lines unnumbered. `dp-cat -sn -b crlf.txt blanks.txt` numbers the CR-only line of
`crlf.txt`. _(UR-04, UR-07)_

**FR-10: Squeeze blank lines (`-s`).**
With `-s`, an empty line MUST be suppressed (written neither as a prefix nor as bytes) when the
line immediately before it in S is also empty. Of each run of consecutive empty lines, exactly
the first is written. An empty line at the very start of S has no preceding line and is
written. Runs extend across operand boundaries (FR-05). Lines whose content is a CR are not
empty, so CRLF blank lines are never squeezed.
_AC:_ `dp-cat -s blanks.txt` writes `\nfirst\n\nsecond\n\nthird\n\n`.
`dp-cat empty.txt nope.txt -n -s blanks.txt blanks.txt` writes the trailing blank run of the
first `blanks.txt` and the leading blank run of the second as one numbered empty line.
_(UR-05)_

### 4.3 Making bytes visible

**FR-11: Show non-printing bytes (`-v`).**
With `-v`, each content byte _b_ MUST be rendered as follows:

| Byte value _b_                                                   | Rendering                                                                                                                                                                                                        |
| :--------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `0x00`–`0x08`, `0x0A`–`0x1F` (except LF, which is never content) | `^` followed by the byte _b_ + `0x40` (for example `0x00` → `^@`, `0x01` → `^A`, `0x0D` → `^M`, `0x1B` → `^[`, `0x1F` → `^_`)                                                                                    |
| `0x09` (TAB)                                                     | TAB unchanged (unless FR-12 applies)                                                                                                                                                                             |
| `0x20`–`0x7E`                                                    | the byte unchanged                                                                                                                                                                                               |
| `0x7F` (DEL)                                                     | `^?`                                                                                                                                                                                                             |
| `0x80`–`0xFF`                                                    | `M-` followed by the rendering of _b_ − `0x80` by the rows above, except that `0x89` and `0x8A` become `M-^I` and `M-^J` (for example `0x80` → `M-^@`, `0x9B` → `M-^[`, `0xA0` → `M-`0xC3`→`M-C`, `0xFF`→`M-^?`) |

All rendered bytes are ASCII. Bytes `0x80`–`0xFF` are rendered one byte at a time, never
decoded as UTF-8: the UTF-8 sequence for `é` (`0xC3 0xA9`) renders as `M-CM-)`.
_AC:_ `dp-cat -v controls.bin` writes `tab\there\n^@^A^Z^[^?\nM-^@M-^IM-^JM-^[M- M-CM-)M-^?\nbell^G^Mend\n`.
_(UR-06)_

**FR-12: Show tabs (`-T`).**
With `-T`, each TAB content byte MUST be rendered as `^I`. Without `-v`, all other bytes are
unaffected (but see FR-13).
_AC:_ `dp-cat -T - < controls.bin` renders only the TAB, as `^I`, and copies every other byte.
_(UR-06)_

**FR-13: Show line ends (`-E`).**
With `-E`, each terminated line's LF MUST be preceded by `$` (FR-07, item 3). In addition, when
the last content byte of a terminated line is a CR, that CR MUST be rendered as `^M`, even
without `-v`. A CR anywhere else (not directly followed by LF in S, including a CR at the very
end of S) is rendered by FR-11 under `-v`, and otherwise written unchanged. Because a CR may be
the last byte read from one buffer or operand and the LF the first byte of the next, a
streaming implementation must defer the decision about a trailing CR until the next byte of S
is known, or S ends. This is the curriculum's **CRLF lesson**: `-A` shows CRLF line ends as
`^M$`, and `-E` alone shows them the same way.
_AC:_ `dp-cat -A crlf.txt` writes `first^M$\nsecond^M$\n^M$\nthird^M$\n`.
`dp-cat -E controls.bin crlf.txt` writes the CR inside `bell\x07\rend` unchanged and every
CRLF as `^M$\n`. _(UR-06, UR-07)_

### 4.4 Errors

**FR-14: Unopenable operand.**
If an operand cannot be opened, or names a directory, the tool MUST write the diagnostic
`dp-cat: <operand>: <reason>` (CONV-16), with the operand exactly as given (CONV-19) and the
reason from the CONV-16 table. It MUST then continue with the next operand (CONV-17) and
finally exit with status 1. A directory operand is reported with the reason `Is a directory`
on every platform, whether the failure is detected when opening or when reading. A directory
contributes no bytes to S.
_AC:_ `dp-cat alpha.txt missing.txt beta.txt` writes alpha and beta to standard output,
`dp-cat: missing.txt: No such file or directory` to standard error, and exits 1.
`dp-cat folder crlf.txt` reports `dp-cat: folder: Is a directory`, writes `crlf.txt`, and
exits 1. _(UR-08)_

**FR-15: Read failure.**
If reading an operand fails after it was opened, the tool MUST keep the output derived from
the bytes already read, write `dp-cat: <operand>: <reason>` (CONV-16; the operand is `-` for
standard input), close the file, continue with the next operand, and exit with status 1.
_AC:_ Verified by unit test with an injected read failure. _(UR-08)_

**FR-16: Write failure.**
If writing to standard output fails because the reader has gone away (broken pipe), the tool
MUST stop at once without a diagnostic (CONV-25). If it fails for any other reason (for
example, the device is full), the tool MUST write `dp-cat: write error` to standard error,
stop processing operands, and exit with status 1.
_AC:_ `dp-cat big.txt | head -1` terminates promptly without a diagnostic. On Linux,
`dp-cat alpha.txt > /dev/full` prints `dp-cat: write error` and exits 1. _(UR-08)_

**FR-17: Diagnostic ordering.**
Before writing a diagnostic for an operand, the tool MUST have written to standard output all
output derived from the bytes of S read so far. The only exception is a CR deferred under
FR-13. This keeps the output and the diagnostics in order when both go to the same terminal or
file.
_AC:_ `dp-cat alpha.txt missing.txt beta.txt 2>&1` shows alpha's lines before the diagnostic.
_(UR-08)_

### 4.5 Help, version, and usage errors

**FR-18: Help.**
`--help` MUST write the help text from user-manual §"HELP OUTPUT" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No operand is read.
_AC:_ `dp-cat --help` matches the user manual exactly. _(UR-11)_

**FR-19: Version.**
`--version` MUST write `dp-cat (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02). No
operand is read.
_AC:_ `dp-cat --version --show-al` prints the version and exits 0, because the scan reaches
`--version` first. _(UR-11)_

**FR-20: Usage errors.**
Unknown options (including `-e`, `-t`, `-u`), abbreviated long options, and any `=value`
attached to a long option MUST be reported with the CONV-13 messages, followed by the CONV-14
line, and exit status 2. Usage errors MUST be detected before any operand is opened, so
standard output stays empty and no file diagnostic is printed.
_AC:_ `dp-cat alpha.txt --number-nonblank=yes` → stderr
`dp-cat: option '--number-nonblank' doesn't allow an argument` and the `Try` line, stdout
empty, exit 2. _(UR-09)_

## 5. Non-functional requirements

| ID     | Category            | Requirement                                                                                                                                                                                                                                                                                                                                                                                  | Verification                                                |
| :----- | :------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| NFR-01 | Portability         | Output MUST be byte-identical on Linux, macOS, and Windows. Files, standard input, and standard output MUST all be used in binary mode. On Windows this means no CRLF↔LF translation in either direction, and no treatment of `0x1A` (Ctrl-Z) as end-of-file. Lines the tool generates (help, version, diagnostics) end in LF only (CONV-03).                                                | CI black-box tests on 3 OSes (public 07, hidden 02, 04, 05) |
| NFR-02 | Memory              | Peak memory MUST NOT depend on the size of the input or on the length of its lines. The tool MUST NOT read a whole file, or a whole line, into memory. A 4 GiB file consisting of a single line MUST be processed with every option combination. Peak resident memory for such a run MUST stay below 64 MiB for a natively compiled build (128 MiB for an interpreted runtime).              | Measurement, code review                                    |
| NFR-03 | Performance         | Input MUST be read and output written in blocks of at least 64 KiB (128 KiB recommended), never one byte or one line per system call. Without transforming options, throughput SHOULD be at least 500 MiB/s for a native build (100 MiB/s interpreted) when copying a cached file to the null device on CI hardware. Start-up and exit SHOULD take under 100 ms native (300 ms interpreted). | Measurement                                                 |
| NFR-04 | Streaming           | Data read from a pipe or terminal MUST be written to standard output before the tool waits for more input. A read that returns fewer bytes than requested is processed at once, rather than waiting for a full block. The only data that may be held back is a CR deferred under FR-13.                                                                                                      | Manual test (`producer \| dp-cat \| consumer`), code review |
| NFR-05 | Resource management | At most one operand file is open at any time. Every opened file MUST be closed on every path (end-of-file, read error, write error) before the next operand is opened. Standard input is never closed by the tool. A run with 10 000 operands naming the same file MUST succeed without exhausting file descriptors or handles.                                                              | Unit test, code review                                      |
| NFR-06 | Robustness          | The tool MUST NOT crash, panic, or print a stack trace for any argument list or any input bytes (CONV-24).                                                                                                                                                                                                                                                                                   | Unit + black-box tests                                      |
| NFR-07 | Maintainability     | Option parsing, operand iteration and I/O, the stream formatter (FR-05 … FR-13), and diagnostics MUST be separate units (Principles 13, 18).                                                                                                                                                                                                                                                 | Design review                                               |
| NFR-08 | Testability         | The stream formatter MUST be a stateful unit that takes byte chunks and returns output bytes without performing I/O. Its output MUST NOT depend on how S is divided into chunks. Unit tests MUST show this by feeding the same input with every possible split point, including a split between a CR and its LF.                                                                             | Unit test                                                   |
| NFR-09 | Build               | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                        | CI                                                          |
| NFR-10 | Security            | The tool MUST read only its operands and standard input, MUST NOT write any file, MUST NOT read environment variables, and MUST run no subprocesses.                                                                                                                                                                                                                                         | Inspection                                                  |

## 6. Diagnostics (complete list)

### 6.1 Runtime diagnostics (exit status 1; processing continues except for the write error)

| Trigger                                                                        | Exact line                             |
| :----------------------------------------------------------------------------- | :------------------------------------- |
| Operand `P` does not exist (including the empty operand)                       | `dp-cat: P: No such file or directory` |
| Operand `P` cannot be opened or read: access denied                            | `dp-cat: P: Permission denied`         |
| Operand `P` is a directory                                                     | `dp-cat: P: Is a directory`            |
| A component of operand `P` is not a directory                                  | `dp-cat: P: Not a directory`           |
| Any other open or read failure of operand `P` (`-` for standard input)         | `dp-cat: P: Input/output error`        |
| Standard output cannot be written (other than a broken pipe); processing stops | `dp-cat: write error`                  |

### 6.2 Usage errors (exit status 2)

Each is followed by `Try 'dp-cat --help' for more information.` Nothing is read or written to
standard output.

| Trigger                                                 | Exact first line                                    |
| :------------------------------------------------------ | :-------------------------------------------------- |
| Unknown short option `x` (for example `-e`, `-t`, `-u`) | `dp-cat: invalid option -- 'x'`                     |
| Unknown or abbreviated long option token `T`            | `dp-cat: unrecognized option 'T'`                   |
| Long option `--name` given `=value`                     | `dp-cat: option '--name' doesn't allow an argument` |

The CONV-13 messages for missing option arguments, invalid values, and missing or extra
operands cannot occur: no option takes an argument, and any number of operands is accepted.

## 7. Verification

| Method                                              | Applies to                                         |
| :-------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)  | FR-01, FR-02, FR-04 … FR-11, FR-13, FR-14, FR-18   |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-01 … FR-06, FR-08 … FR-14, FR-19, FR-20         |
| Unit test (written by the implementer)              | FR-05, FR-07 … FR-13, FR-15, FR-16, NFR-05, NFR-08 |
| Measurement                                         | NFR-02, NFR-03, NFR-04                             |
| Inspection / review                                 | FR-17, NFR-07, NFR-10                              |

The fixture files are shared by both suites (`tests/fixtures/`):

| File                    | Contents                                                                                                                              |
| :---------------------- | :------------------------------------------------------------------------------------------------------------------------------------ |
| `alpha.txt`, `beta.txt` | Two LF-terminated lines each                                                                                                          |
| `stdin.txt`             | One line, used as redirected standard input                                                                                           |
| `crlf.txt`              | Four CRLF-terminated lines; the third has no content other than its CR                                                                |
| `controls.bin`          | A TAB, control bytes including NUL, `0x1A`, and ESC, DEL, bytes `0x80`–`0xFF` (including UTF-8 `é`), and a CR in the middle of a line |
| `no-eol.txt`            | One line without a terminating LF                                                                                                     |
| `blanks.txt`            | Runs of empty lines at the start, in the middle, and at the end                                                                       |
| `empty.txt`             | Zero bytes                                                                                                                            |
| `folder/`               | A directory (it contains only `.keep`)                                                                                                |

Public test map:

| Test | Command                                   | Verifies             |
| :--- | :---------------------------------------- | :------------------- |
| 01   | `dp-cat alpha.txt beta.txt`               | FR-01, FR-06         |
| 02   | `dp-cat < stdin.txt`                      | FR-01 (no operands)  |
| 03   | `dp-cat alpha.txt - beta.txt < stdin.txt` | FR-02                |
| 04   | `dp-cat -n alpha.txt beta.txt no-eol.txt` | FR-05, FR-07, FR-08  |
| 05   | `dp-cat -b blanks.txt`                    | FR-09                |
| 06   | `dp-cat -s blanks.txt`                    | FR-10                |
| 07   | `dp-cat -A crlf.txt`                      | FR-04, FR-13, NFR-01 |
| 08   | `dp-cat -v controls.bin`                  | FR-11                |
| 09   | `dp-cat alpha.txt missing.txt beta.txt`   | FR-14, CONV-17       |
| 10   | `dp-cat --help`                           | FR-18                |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                          |
| :--------------- | :------------------------------------------- |
| UR-01            | FR-01, FR-06                                 |
| UR-02            | FR-01, FR-02                                 |
| UR-03            | FR-03, FR-06, FR-07, CONV-04                 |
| UR-04            | FR-05, FR-07, FR-08, FR-09                   |
| UR-05            | FR-10                                        |
| UR-06            | FR-04, FR-11, FR-12, FR-13                   |
| UR-07            | FR-09, FR-13                                 |
| UR-08            | FR-14, FR-15, FR-16, FR-17, CONV-16, CONV-17 |
| UR-09            | FR-20, CONV-13, CONV-14                      |
| UR-10            | FR-03, NFR-02, NFR-03, NFR-04, NFR-05        |
| UR-11            | FR-18, FR-19                                 |
| UR-12            | NFR-01, CONV-03                              |
| UR-13            | FR-04, FR-05, §1.5, CLI-CONV                 |
| UR-14            | NFR-09                                       |
