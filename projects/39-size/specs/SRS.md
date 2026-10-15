<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-size](#software-requirements-specification-srs--dp-size)
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
    - [3.7 Files](#37-files)
    - [3.8 Exit status](#38-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-size

| Field                     | Value                                        |
| :------------------------ | :------------------------------------------- |
| Document ID               | SRS-39                                       |
| Project                   | `39-size` — Binary File Byte Size Inspector  |
| Product                   | `dp-size` (canonical name)                   |
| Version                   | 1.0.0                                        |
| Status                    | Approved (pre-written by the curriculum)     |
| Parent document           | `URD.md` (URD-39)                            |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018         |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-size`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope

`dp-size` takes file names _without_ their extension, from its operands or from the lines of
standard input, appends an extension (`.c` unless another is chosen), opens each resulting file
in binary mode, counts its bytes by reading it to the end, and writes a two-line record giving
the file name and the byte size. It can write a prompt to standard error before each name is
read. Files that cannot be read and malformed names are reported with fixed messages, and the
remaining names are still processed.

### 1.3 Definitions

| Term        | Definition                                                                                                                             |
| :---------- | :------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR, NUL | The bytes `0x0A`, `0x0D`, and `0x00`                                                                                                   |
| TAB         | The byte `0x09`                                                                                                                        |
| Ctrl-Z      | The byte `0x1A`                                                                                                                        |
| EXT         | The extension: the value of `-e`/`--extension`, or `.c` if neither is given                                                            |
| Name        | A byte string naming a file without its extension: an operand other than `-`, or a line of the name input (FR-02)                      |
| Name input  | The bytes of standard input, when they are read for names (FR-01)                                                                      |
| Path        | The name followed immediately by EXT (FR-03)                                                                                           |
| Byte size   | The number of bytes in the file named by the path, counted by reading (FR-04)                                                          |
| Record      | The two output lines for one path (FR-05)                                                                                              |
| Decimal     | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References

- URD-39: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §8.3 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-size` is a standalone executable. Its interfaces are the command line, standard input (for
names), the files it measures (read only), standard output, standard error, and the exit
status. It belongs to the curriculum's applications-programming track (Projects 11–52) and
adapts §8.3 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Take names from operands, or from the lines of standard input.
2. Append the extension to each name to form a path.
3. Open each path in binary mode and count every byte by reading to the end of the file.
4. Write the path and its byte size as a two-line record.
5. Optionally write a prompt to standard error before each name is read.
6. Report unreadable files and malformed names, and carry on with the next name.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The byte size MUST be obtained by reading the file's contents (FR-04). File-system metadata
  (a `stat` size, a directory listing, `GetFileSizeEx`, or seeking to the end) MUST NOT be used
  to compute it.

### 2.4 Assumptions

- Relative paths are relative to the current working directory.
- Nothing writes a file while it is being measured; if something does, the result is the
  number of bytes actually read.
- The files measured may contain any bytes.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §8.3 prompts for a file name without its extension, appends `.c`,
opens the file in binary mode (`"rb"`), counts the characters it reads until end-of-file, and
prints the count. `dp-size` keeps:

- the dialog: a name typed without its extension, the extension `.c` appended to it, and the
  prompt text `File name (NO extension):` between two TABs;
- the counting method: the file is opened in binary mode and every byte is read and counted,
  so NUL, CR, and Ctrl-Z bytes count like any other (FR-04); the size is never taken from
  file-system metadata;
- the result line: a TAB, `Byte size:`, a TAB, and the count.

It changes the following, for the reasons given:

- **Several names, from operands or standard input** (FR-01, FR-02). The textbook measured one
  file per run. Reading every line of standard input, and accepting names as operands, makes
  the tool usable from scripts; the name `-` reads standard input at that point, as `dp-cat`
  does.
- **The extension can be changed or omitted** with `-e`/`--extension` (FR-03), so files other
  than C sources can be measured. EXT must be empty or begin with `.`, so that `-e txt` (a
  likely slip for `-e .txt`) is rejected rather than silently measuring `notestxt`. Unlike a
  file-name option, an empty EXT is valid: it means "append nothing".
- **Each record names its file** (FR-05). With several names, a bare `Byte size:` line could
  not be matched to its file, so each record starts with a `File name:` line in the same layout,
  giving the path as constructed. The blank lines with which the textbook separated its output
  from the echo of the typed name are not written.
- **Prompts are optional and go to standard error** (FR-09), so standard output holds only the
  records. The textbook's leading blank lines before the prompt existed only to separate it from
  earlier terminal output and are not written.
- **Failures are diagnosed** with the CONV-16 messages and the remaining names are still
  measured (FR-07, FR-10); the textbook did not check whether its file could be opened. Empty
  names and names containing NUL, which cannot name a file, are reported (FR-08).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics CONV-13 …
CONV-17, and exit statuses CONV-18. Of the conventions for Projects 11–52:

| Convention | Use in this SRS                                                                                                                                                                                                                    |
| :--------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-32    | Not applicable as tokens: the name input is read as _lines_ (FR-02). Line numbers in diagnostics are as defined in CONV-32 (1 plus the number of LF bytes before the line).                                                        |
| CONV-33    | Not applicable: no numeric value is read.                                                                                                                                                                                          |
| CONV-34    | Used for malformed names read from standard input, with the further messages `empty file name` and `file name contains a NUL byte`. **Override:** such a diagnostic does not end processing; the next line is read (FR-08, FR-10). |
| CONV-35    | Not applicable: no real number is written.                                                                                                                                                                                         |
| CONV-36    | `-p`, `--prompt` with one prompt (FR-09).                                                                                                                                                                                          |
| CONV-37    | Applies to the name input, which is _text data_ (FR-02). It does **not** apply to the measured files, which are binary data: every Ctrl-Z byte in them is counted (FR-04).                                                         |
| CONV-38    | Not applicable: nothing is random.                                                                                                                                                                                                 |

**Override of CONV-10:** an operand is a _name_, not a file; the operand `-` means "read names
from standard input here" (FR-01), not "measure standard input". `dp-size` copies no input
bytes to its output except the bytes of each path in its record (FR-05).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-size [-e EXT | --extension=EXT] [-p | --prompt] [NAME]...
dp-size --help
dp-size --version
```

### 3.2 Options

| Short | Long          | Argument       | Default | Description                                                                              |
| :---- | :------------ | :------------- | :------ | :--------------------------------------------------------------------------------------- |
| `-e`  | `--extension` | EXT (required) | `.c`    | Append EXT to each name instead of `.c`; EXT is empty or begins with `.` (FR-03)         |
| `-p`  | `--prompt`    | none           | off     | Write the prompt of FR-09 to standard error before each name is read from standard input |
| —     | `--help`      | none           | —       | Print the help text and exit 0                                                           |
| —     | `--version`   | none           | —       | Print the version line and exit 0                                                        |

Option syntax (`-eEXT`, `--extension EXT`, bundling such as `-pe.h`, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. If `-e` is repeated, the last occurrence wins (CONV-11); only
that value is checked (FR-13).

### 3.3 Operands

Zero or more NAME operands, processed in order (FR-01). The operand `-` reads names from
standard input. Every token after `--` is an operand, even if it begins with `-`. Names are used
and echoed exactly as given (CONV-05, CONV-19).

### 3.4 Standard input

Read for names when there are no operands, or when an operand is `-` (FR-01, FR-02). Read as raw
bytes; no newline translation of any kind is performed on any platform. Otherwise standard
input is not read (CONV-26).

### 3.5 Standard output

One record per successfully measured path (FR-05), in the order of the names. On a usage error,
or when `--help` / `--version` is handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error

Prompts (FR-09, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when every name is measured.

### 3.7 Files

Each path is opened for reading only, in binary mode, and closed before the next name is
processed. No file is created, modified, deleted, or renamed.

### 3.8 Exit status

| Status | Condition                                                                                                              |
| :----- | :--------------------------------------------------------------------------------------------------------------------- |
| 0      | Every name was measured (including when there was no name at all), or `--help` / `--version` was handled               |
| 1      | At least one name was malformed (FR-08) or its file could not be read (FR-07), or standard output could not be written |
| 2      | Usage error (FR-13)                                                                                                    |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n`, `\r`, `\t` denote LF, CR, and TAB, and the following are public
fixture files in `tests/fixtures/`: `size.c` (562 bytes of text with LF line endings);
`binary.c` (300 bytes: each byte value `0x00` … `0xFF` once, then 20 NUL bytes, ten `\r\n`
pairs, and four Ctrl-Z bytes); `crlf.c` (`first line\r\nsecond line\r\n\r\nlast line\r\n`,
38 bytes); `ctrlz.c` (`OLD DOS DATA\r\n` followed by one Ctrl-Z, 15 bytes); `empty.c` (0 bytes);
`notes.txt` (33 bytes); `license` (47 bytes, no extension); `sub/inner.c` (6 bytes); `dir.c`
(a directory); `size-name.txt` (`size\n`); `names.txt`
(`size\r\nbinary\n\nsub/inner\nmissing\nempty`, with no final LF). `S(p, n)` denotes the record
`\tFile name:\t<p>\n\tByte size:\t<n>\n`.

**FR-01: Sources of names.**
If there are no operands, the tool MUST read names from standard input (FR-02) until its end.
Otherwise it MUST process the operands in order: an operand `-` reads names from standard input
(FR-02) at that point, until its end; any other operand is a name. A second `-` finds standard
input already at its end and reads no name (but still writes a prompt, FR-09). Each name is
processed completely — path formed, file measured, record or diagnostic written — before the
next name is taken. When standard input yields no name at all, nothing is written and the exit
status is 0.
_AC:_ `dp-size size` → stdout `S(size.c, 562)`, exit 0; `dp-size < size-name.txt` → the same;
`dp-size crlf - empty < size-name.txt` → `S(crlf.c, 38)`, `S(size.c, 562)`, `S(empty.c, 0)` in
that order; `dp-size` with empty standard input → no output, exit 0. _(UR-01, UR-02)_

**FR-02: Names from standard input.**
The name input is _text data_ (CONV-37): a run of one or more Ctrl-Z bytes that extends to the
very end of standard input is ignored. The remaining bytes are divided into lines: each LF ends
a line, and the bytes after the last LF, if there are any, form a final line without an LF. The
name is the line without its LF and with **one** CR removed if the line then ends in CR. No
other byte is removed or interpreted: spaces, TABs, and a Ctrl-Z byte that is followed by any
other byte are part of the name. The line number of a line is 1 plus the number of LF bytes
before its first byte (CONV-32). A line that yields an empty name, or a name containing NUL, is
handled by FR-08. Lines MUST be read one at a time: the name on a line is processed before the
next line is read, so the tool answers each name at once when used interactively.
_AC:_ `dp-size < names.txt` → `S(size.c, 562)`, `S(binary.c, 300)`, `S(sub/inner.c, 6)`,
`S(empty.c, 0)` on stdout; stderr `dp-size: -:3: empty file name\n` and
`dp-size: missing.c: No such file or directory\n`; exit 1. With standard input
`size\r\nempty\r\n` followed by two Ctrl-Z bytes, the names are `size` and `empty`, exit 0.
With `ctrlz` Ctrl-Z `\nsize` Ctrl-Z, the names are `ctrlz` Ctrl-Z (the path `ctrlz` Ctrl-Z `.c`,
which does not exist) and `size`. _(UR-02, UR-08)_

**FR-03: Path construction.**
The path MUST be the name followed immediately by EXT, byte for byte, with nothing inserted,
removed, or normalized. Without `-e`/`--extension`, EXT is `.c`. A name may contain directory
separators; the path is then relative to the current directory unless absolute. EXT MUST be
empty or begin with `.` (FR-13); an empty EXT makes the path equal to the name. The path is
written in the record (FR-05) and in diagnostics (FR-07) exactly as constructed (CONV-16).
_AC:_ `dp-size --extension=.txt notes` → `S(notes.txt, 33)`; `dp-size -e '' license` →
`S(license, 47)`; `dp-size --extension= sub/inner.c` → `S(sub/inner.c, 6)`;
`dp-size sub/` → `dp-size: sub/.c: No such file or directory`. _(UR-03)_

**FR-04: Byte counting.**
The tool MUST open the path for reading in **binary** mode and read it from its first byte to
its end, counting every byte read. Every byte value counts as one byte: in particular NUL bytes,
CR bytes (no CRLF is translated), and Ctrl-Z bytes anywhere in the file, including a run at the
very end (CONV-37 does **not** apply to measured files). The count MUST NOT be obtained from
file-system metadata (section 2.3). The file MAY be read in blocks of any size, and memory use
MUST NOT depend on the size of the file (NFR-03). A file of 0 bytes has byte size 0.
_AC:_ `dp-size binary crlf ctrlz empty` → `S(binary.c, 300)`, `S(crlf.c, 38)`, `S(ctrlz.c, 15)`,
`S(empty.c, 0)`, exit 0; a file of 512 Ctrl-Z bytes has byte size 512; a file of 70000 bytes
has byte size 70000. _(UR-04)_

**FR-05: Record format.**
For each path whose file was read completely, the tool MUST write exactly the two lines

```text
<TAB>File name:<TAB><path>
<TAB>Byte size:<TAB><n>
```

where `<TAB>` is one TAB byte, `<path>` is the path's exact bytes (FR-03), `<n>` is the decimal
of the byte size, and each line ends with a single LF. There are no other spaces or blank lines,
no header, and no total. Standard output MUST be flushed after each record. Nothing is written
to standard output for a name that fails (FR-07, FR-08).
_AC:_ `dp-size size` → stdout exactly `\tFile name:\tsize.c\n\tByte size:\t562\n`. _(UR-05)_

**FR-06: Byte sizes up to 2⁶³−1.**
The byte size MUST be counted without overflow for every file of up to 2⁶³−1 bytes (for example
with a 64-bit counter).
_AC:_ the unit test of NFR-06; a file of 70000 bytes, larger than common block sizes, has byte
size 70000. _(UR-04)_

**FR-07: Unreadable files.**
If the file named by a path does not exist, cannot be opened, is a directory, or a read error
occurs, the tool MUST write `dp-size: <path>: <reason>` with `<path>` the constructed path
(FR-03) and `<reason>` from the CONV-16 table, write no record for it, and continue with the next
name. A path the platform rejects as malformed (for example, on Windows, one containing a control
character such as Ctrl-Z, which no Windows file name may contain) cannot name an existing file
and MUST be reported with the reason `No such file or directory`.
_AC:_ `dp-size missing size dir` → stdout `S(size.c, 562)`; stderr
`dp-size: missing.c: No such file or directory\n` then `dp-size: dir.c: Is a directory\n`;
exit 1. _(UR-06, UR-07)_

**FR-08: Malformed names.**
An empty name cannot name a file. For an empty operand, the tool MUST write
`dp-size: empty file name`. For an empty name read from standard input on line _L_, it MUST
write `dp-size: -:L: empty file name`; for a name read from standard input that contains a NUL
byte, `dp-size: -:L: file name contains a NUL byte` (CONV-34). In each case no path is formed,
no file is opened, no record is written, and the tool continues with the next name.
_AC:_ `dp-size '' size` → stderr `dp-size: empty file name\n`, stdout `S(size.c, 562)`, exit 1.
With standard input `bin` NUL `ary\n\r\n  size\nsize \n`: stderr
`dp-size: -:1: file name contains a NUL byte`, `dp-size: -:2: empty file name`,
`dp-size:   size.c: No such file or directory`, `dp-size: size .c: No such file or directory`
(the spaces are part of the names), exit 1. _(UR-07, UR-08)_

**FR-09: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 27 bytes
`<TAB>File name (NO extension):<TAB>` (a TAB, the 25 characters `File name (NO extension):`, and
a TAB; no LF). With prompts enabled, the tool MUST write the prompt to standard error, and flush
standard error, immediately before each attempt to read a line of standard input for a name:
before the first line, after each name read from standard input has been processed, and before
the attempt that reaches the end of standard input (CONV-36). Standard input yielding _n_ lines
therefore produces _n_ + 1 prompts for each `-` (or for the implicit standard input when there
are no operands). No prompt is written for a name given as an operand. A diagnostic that follows
a prompt continues the same line of standard error. Prompts never change standard output.
_AC:_ `dp-size --prompt < size-name.txt` → stdout `S(size.c, 562)`, stderr the prompt twice,
exit 0; `dp-size -p` with empty standard input → stderr the prompt once, exit 0;
`dp-size -p - - < size-name.txt` → the prompt three times. _(UR-09)_

**FR-10: Continuing after failures.**
A failure on one name (FR-07, FR-08) MUST NOT stop the processing of the remaining names
(CONV-17). The exit status is 1 if any name failed and 0 otherwise.
_AC:_ see FR-02, FR-07, FR-08. _(UR-06)_

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-size --help` matches the user manual exactly; `dp-size extra --help` also prints it.
_(UR-10)_

**FR-12: Version.**
`--version` MUST write `dp-size (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-size -e bad --version` also prints it and exits 0. _(UR-10)_

**FR-13: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--prompt=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--ext` is
unrecognized. An EXT that is not empty and does not begin with `.` MUST be reported as
`dp-size: invalid argument '<EXT>' for '<option>'`, where `<option>` is `-e` or `--extension` as
the user wrote it. Option values are checked after the whole argument list has been scanned
(CONV-12).
_AC:_ `dp-size -e txt notes` → `dp-size: invalid argument 'txt' for '-e'`; `dp-size -e` →
`dp-size: option requires an argument -- 'e'`; `dp-size --prompt=yes` →
`dp-size: option '--prompt' doesn't allow an argument`; `dp-size -x --help` →
`dp-size: invalid option -- 'x'`; each followed by the CONV-14 line, exit 2. _(UR-11, UR-12)_

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT read standard input or open any file, MUST NOT
write a prompt, and MUST NOT write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-11)_

## 5. Non-functional requirements

| ID     | Category                                      | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Verification                              |
| :----- | :-------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| NFR-01 | Portability                                   | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: binary versus text mode | Measured files MUST be opened in binary mode on every platform. In text mode, a Windows C runtime translates CRLF to LF (so `crlf.c` would measure 34 bytes instead of 38) and treats a Ctrl-Z byte as end-of-file (so `binary.c` would stop after 26 bytes); both are conformance failures. Standard input MUST also be read in binary mode, so that only FR-02 interprets CR and Ctrl-Z in names, and at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. On Windows, a name read from standard input is decoded as UTF-8 to form the path; a name that is not valid UTF-8 cannot name a file there and is reported as `No such file or directory`. Mapping open failures to CONV-16 reasons MUST be portable: opening a directory fails differently on each platform (`EISDIR`, or "access denied" on Windows) and MUST always be reported as `Is a directory`. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                   | Measuring a 1 GiB file MUST take under 5 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31) whatever the file size: the file is read in blocks, never held whole in memory. Reading one byte per system call is not acceptable; a buffered or block read is required. Start-up and exit for one small file MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Measurement                               |
| NFR-04 | Robustness                                    | The tool MUST NOT crash, panic, or print a stack trace for any argument list, name bytes, or file contents (CONV-24), including names of any length and non-UTF-8 bytes. Every file it opens MUST be closed before the next name is processed, including after a read error. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Unit + black-box tests                    |
| NFR-05 | Maintainability                               | Option parsing, splitting the name input into names, path construction, byte counting, record formatting, and diagnostics MUST be separate units. Byte counting MUST be one function that receives an open binary stream (or a path) and returns the count, with no output.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Design review                             |
| NFR-06 | Testability                                   | Name splitting (bytes → names with line numbers, including CR removal and the CONV-37 rule) and record formatting MUST be pure functions covered by unit tests. Byte counting MUST be unit-tested with an in-memory stream that returns data in blocks of different sizes, including empty reads before the end, and with a stream containing every byte value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Code review                               |
| NFR-07 | Build                                         | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | CI                                        |
| NFR-08 | Security                                      | The tool MUST open files for reading only, MUST NOT create, modify, delete, or rename any file, read environment variables, or run subprocesses. Paths are used exactly as constructed; the tool does not expand `~`, wildcards, or environment variables.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Inspection                                |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-size --help' for more information.`

| Trigger                                      | Exact first line                                                                      |
| :------------------------------------------- | :------------------------------------------------------------------------------------ |
| Unknown short option `x`                     | `dp-size: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-size: unrecognized option 'T'`                                                    |
| `-e` without an argument                     | `dp-size: option requires an argument -- 'e'`                                         |
| `--extension` without an argument            | `dp-size: option '--extension' requires an argument`                                  |
| `--prompt=…` / `--help=…` / `--version=…`    | `dp-size: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| EXT `V` not empty and not beginning with `.` | `dp-size: invalid argument 'V' for '-e'` (or `'--extension'`, as written)             |

Runtime errors (exit status 1 at the end; the tool continues with the next name):

| Trigger                                                      | Exact message                                                                                                    |
| :----------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------- |
| Path `P` does not exist, or is malformed for the platform    | `dp-size: P: No such file or directory`                                                                          |
| Path `P` cannot be opened or read because access is denied   | `dp-size: P: Permission denied`                                                                                  |
| Path `P` is a directory                                      | `dp-size: P: Is a directory`                                                                                     |
| A component of path `P` is not a directory                   | `dp-size: P: Not a directory`                                                                                    |
| Any other open or read failure of path `P`                   | `dp-size: P: Input/output error`                                                                                 |
| An empty operand                                             | `dp-size: empty file name`                                                                                       |
| Line `L` of standard input yields an empty name              | `dp-size: -:L: empty file name`                                                                                  |
| Line `L` of standard input contains a NUL byte               | `dp-size: -:L: file name contains a NUL byte`                                                                    |
| Standard input cannot be read                                | `dp-size: -: Input/output error` (the tool stops reading standard input; remaining operands are still processed) |
| Standard output cannot be written (other than a broken pipe) | `dp-size: write error` (the tool stops)                                                                          |

## 7. Verification

| Method                                                                                                    | Applies to                                        |
| :-------------------------------------------------------------------------------------------------------- | :------------------------------------------------ |
| Black-box test (public, `tests/public/`, 10 cases)                                                        | FR-01 … FR-05, FR-07 … FR-11, FR-13, FR-14        |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 03, 05, 06, and 08 … 10 have several steps) | FR-01 … FR-05, FR-07 … FR-14                      |
| Unit test (written by the implementer)                                                                    | FR-02 … FR-06, NFR-06                             |
| Measurement                                                                                               | NFR-03                                            |
| Inspection / review                                                                                       | section 2.3 (no metadata), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                                | Verifies                                                 |
| :--- | :------------------------------------- | :------------------------------------------------------- |
| 01   | `dp-size size`                         | FR-01, FR-03 (default `.c`), FR-04, FR-05                |
| 02   | `dp-size < size-name.txt`              | FR-01, FR-02 (the textbook dialog)                       |
| 03   | `dp-size --prompt < size-name.txt`     | FR-09                                                    |
| 04   | `dp-size binary crlf ctrlz empty`      | FR-04 (NUL, CRLF, Ctrl-Z, empty file)                    |
| 05   | `dp-size --extension=.txt notes`       | FR-03                                                    |
| 06   | `dp-size < names.txt`                  | FR-02 (CRLF, final line without LF), FR-07, FR-08, FR-10 |
| 07   | `dp-size missing size dir`             | FR-07, FR-10                                             |
| 08   | `dp-size crlf - empty < size-name.txt` | FR-01 (operands and `-` mixed)                           |
| 09   | `dp-size --help`                       | FR-11                                                    |
| 10   | `dp-size -e txt notes`                 | FR-13, FR-14                                             |

## 8. Traceability (URD → SRS)

| User requirement | System requirements            |
| :--------------- | :----------------------------- |
| UR-01            | FR-01, FR-03                   |
| UR-02            | FR-01, FR-02, CONV-26          |
| UR-03            | FR-03                          |
| UR-04            | FR-04, FR-06, NFR-02           |
| UR-05            | FR-05                          |
| UR-06            | FR-07, FR-10, CONV-17          |
| UR-07            | FR-07, FR-08, CONV-16, CONV-34 |
| UR-08            | FR-02, FR-08, NFR-02, CONV-37  |
| UR-09            | FR-09, CONV-36                 |
| UR-10            | FR-11, FR-12                   |
| UR-11            | FR-13, FR-14                   |
| UR-12            | FR-13, NFR-01, CLI-CONV        |
| UR-13            | NFR-03, NFR-07                 |
