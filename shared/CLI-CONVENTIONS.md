# Common CLI Conventions (CLI-CONV)

| Field | Value |
| :-- | :-- |
| Document ID | CLI-CONV |
| Version | 1.0.0 |
| Applies to | Every tool in `projects/00-hello-world` … `projects/10-sys-monitor` |
| Status | Normative |

This document defines behavior that every curriculum tool shares. Each project's Software
Requirements Specification (SRS) incorporates this document by reference. Where an SRS states
something different, **the SRS takes precedence** for that tool.

Requirement IDs in this document use the prefix `CONV-`. An SRS cites them in its traceability
section. The keywords **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are used as defined in
RFC 2119.

---

## 1. Program identity

- **CONV-01**: Every tool has a fixed *canonical name* (for example `dp-cat`), given in its SRS.
  Diagnostics, help text, and version output MUST use the canonical name. They MUST NOT use
  `argv[0]`, which differs across platforms, install methods, and file extensions such as
  `.exe`.
- **CONV-02**: The `--version` option MUST print exactly one line and exit with status 0:

  ```text
  <canonical-name> (dialectic-playground) 1.0.0
  ```

## 2. Bytes, encodings, and line endings

- **CONV-03**: Every line terminator a tool *generates* (in help text, diagnostics, reports, and
  so on) MUST be a single LF (`0x0A`) on every platform, including Windows. On Windows,
  implementations MUST write standard output and standard error in binary mode. Text-mode
  newline translation to CRLF is a conformance failure.
- **CONV-04**: Unless the tool's SRS says otherwise, data a tool *copies* from its input (file
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
  with status 0. If an option *syntax* error (unknown option, missing option argument, or an
  argument given to an option that takes none) is found earlier in the scan, that usage error
  is reported instead. Operands are only collected during the scan, and option *values* are
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

| Condition | Message |
| :-- | :-- |
| Unknown short option `x` | `<tool>: invalid option -- 'x'` |
| Unknown long option (full token as given, including any `=value`) | `<tool>: unrecognized option '<token>'` |
| Short option `x` missing its argument | `<tool>: option requires an argument -- 'x'` |
| Long option missing its argument | `<tool>: option '--<name>' requires an argument` |
| Long option given `=value` but takes no argument | `<tool>: option '--<name>' doesn't allow an argument` |
| Invalid option value | `<tool>: invalid argument '<value>' for '<option>'` |
| Required operand absent | `<tool>: missing operand` |
| Surplus operand (the first surplus one) | `<tool>: extra operand '<operand>'` |

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

| Condition | `<reason>` |
| :-- | :-- |
| Path does not exist (ENOENT, `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND`) | `No such file or directory` |
| Access denied (EACCES, EPERM, `ERROR_ACCESS_DENIED`) | `Permission denied` |
| A directory was given where a file was needed | `Is a directory` |
| A path component is not a directory (ENOTDIR) | `Not a directory` |
| Any other I/O failure | `Input/output error` |

- **CONV-17**: When a tool processes several operands, an error on one operand MUST NOT stop it
  from processing the rest, unless the SRS says otherwise. The final exit status is 1 if any
  operand failed.

## 5. Exit status

- **CONV-18**: Unless a tool's SRS overrides it:

| Status | Meaning |
| :-- | :-- |
| 0 | Success |
| 1 | Runtime failure (at least one operand or operation failed) |
| 2 | Usage error (CONV-13, CONV-14) |

  `dp-grep`, `dp-diff`, and `dp-env` define their own exit-status tables.

## 6. Paths and traversal

- **CONV-19**: Paths given by the user are echoed back exactly as given. Windows users may type
  `a\b`, and that is what gets echoed.
- **CONV-20**: When a tool *constructs* a path by joining a directory and an entry name (for
  example, during recursive traversal), it MUST use `/` as the separator on every platform.
  Windows APIs accept `/`, and this keeps output identical across operating systems.
- **CONV-21**: When a tool lists directory entries, it MUST visit them in ascending
  **byte-wise** order of their UTF-8-encoded names. That order is case-sensitive and
  locale-independent. The entries `.` and `..` are never visited.

## 7. Standard options and help text

- **CONV-22**: Every tool accepts `--help` and `--version`. Neither takes an argument.
- **CONV-23**: `--help` prints the tool's help text to **standard output** and exits with status
  0. The help text is given *verbatim* in the "Help output" section of the tool's user manual.
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
  in that case is unspecified.
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
