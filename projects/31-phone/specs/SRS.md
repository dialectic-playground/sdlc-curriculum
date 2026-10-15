<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-phone](#software-requirements-specification-srs--dp-phone)
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

# Software Requirements Specification (SRS) — dp-phone

| Field                     | Value                                                                    |
| :------------------------ | :----------------------------------------------------------------------- |
| Document ID               | SRS-31                                                                   |
| Project                   | `31-phone` — Student Directory Lookup via Selection Sort & Binary Search |
| Product                   | `dp-phone` (canonical name)                                              |
| Version                   | 1.0.0                                                                    |
| Status                    | Approved (pre-written by the curriculum)                                 |
| Parent document           | `URD.md` (URD-31)                                                        |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                             |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                                     |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-phone`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-phone` reads a file of fixed-width student records (by default `students.dat`), checks
every record, and sorts the records with selection sort. It then reads last names, one per
line, from standard input or from one file, and answers each one, using binary search, with
the student's record or a not-found message. Each answer is written as soon as its name has
been read. With `--prompt`, it writes a prompt to standard error before each name is read.

### 1.3 Definitions

| Term                                    | Definition                                                                                                                                                                                                                                                                                                                                                      |
| :-------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR                                  | The bytes `0x0A` and `0x0D`                                                                                                                                                                                                                                                                                                                                     |
| STUDENTS                                | The value of `-f`/`--file`, or `students.dat` if neither is given                                                                                                                                                                                                                                                                                               |
| NAMES                                   | The FILE operand, or `-` if there is none                                                                                                                                                                                                                                                                                                                       |
| Student file                            | The byte sequence read from the file STUDENTS, or from standard input when STUDENTS is `-`                                                                                                                                                                                                                                                                      |
| Name input                              | The byte sequence read from the file NAMES, or from standard input when NAMES is `-`                                                                                                                                                                                                                                                                            |
| Line                                    | A maximal run of bytes other than LF, terminated by an LF or by the end of the input. An input that ends with an LF has no empty line after that LF; an empty input has no lines. The _line number_ of a line is 1 plus the number of LF bytes before its first byte (CONV-32). Before a line is used, one CR at its end, if present, is removed (FR-02, FR-05) |
| Record                                  | A line of the student file, after CR removal; exactly 62 bytes (FR-02)                                                                                                                                                                                                                                                                                          |
| Last name, first name, telephone number | Bytes 1–25, 26–50, and 51–62 of a record (columns, counted in bytes from 1)                                                                                                                                                                                                                                                                                     |
| Name                                    | A line of the name input, after CR removal (FR-05)                                                                                                                                                                                                                                                                                                              |
| Key                                     | The 25-byte string compared with last names: the name followed by 25 − _n_ spaces (`0x20`), where _n_ ≤ 25 is the length of the name in bytes (FR-06)                                                                                                                                                                                                           |
| Byte order                              | Comparison of two byte strings as sequences of unsigned bytes (`0x00` … `0xFF`): the first differing byte decides; if one string is a prefix of the other, the shorter is smaller. It is independent of locale and case-sensitive (`Z` < `a`)                                                                                                                   |
| Directory                               | The list of records in the order produced by FR-04                                                                                                                                                                                                                                                                                                              |

### 1.4 References

- URD-31: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §5.11 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-phone` is a standalone executable. Its interfaces are the command line, the student file,
the name input, standard output, standard error, and the exit status. It belongs to the
curriculum's applications-programming track (Projects 11–52) and adapts §5.11 of Johnsonbaugh
& Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Read the student file (`students.dat` by default) and check every record.
2. Sort the records with selection sort.
3. Read names one line at a time and look each up with binary search.
4. Write the student's record, or a not-found message, for each name.
5. Optionally prompt for each name on standard error.
6. Report unreadable files and malformed records; display help and version information;
   detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, except for the algorithm requirements of
  FR-04, FR-06, and NFR-05, which are checked by design review.
- Library sorting and searching routines MUST NOT be used for the sort of FR-04 or the search
  of FR-06.

### 2.4 Assumptions

- The current working directory is where the default file `students.dat` is looked for.
- Names and records may contain any bytes; they are compared as bytes, never decoded.
- Nothing else writes the student file while the tool reads it.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §5.11 reads the records of `students.dat` (last name in columns 1–25,
first name in columns 26–50, telephone number in columns 51–62) into memory, sorts them with
selection sort by comparing whole records, and then repeatedly prompts for a last name, pads it
with blanks to 25 characters, looks it up with binary search on the first 25 characters of the
records, and prints either `Record:nd the record or the name followed by
`not in our directory.`, until end-of-file. `dp-phone` keeps:

- the record layout, the file name `students.dat` as the default in the current directory, and
  the requirement that the whole file is loaded before the first name is read;
- selection sort by whole record and binary search on the blank-padded 25-column last name, as
  design requirements (FR-04, FR-06, NFR-05), with exact, case-sensitive matching;
- the answer wording exactly: `Record:ollowed by the record, or the name followed by
`not in our directory.`;
- the prompt text `Enter a student's name, or signal EOF to halt:nd the loop until end of
  input, which ends the tool with exit status 0.

It changes the following, for the reasons given:

- **A name is a whole line.** Last names may contain spaces (`Von Neumann` is in the textbook's
  own data, and its description calls it a boundary case), so a name is the whole input line,
  not a whitespace-delimited word; CONV-32 tokens are not used. Empty lines are ignored, so
  pressing Enter by mistake produces no answer (FR-05). A name longer than 25 bytes cannot be a
  last name and is answered as not in the directory (FR-06); the section gives such input no
  defined meaning.
- **Layout for redirected output.** The section's sample session separates each answer from
  the echoed keyboard input with blank lines and indents the not-found message with a TAB.
  Those bytes exist only to make the terminal session readable, so they are dropped: each
  answer is exactly one line with no leading or trailing whitespace (FR-07), and the prompt,
  when requested, goes to standard error (FR-08, CONV-36) so that standard output is identical
  with and without it.
- **Exact algorithms.** The section describes the binary search only in outline. FR-06 fixes
  the midpoint rule, so that when several records share a last name, every implementation
  reports the same one (the textbook reports exactly one record per name, too).
- **Records are checked** (FR-02, FR-03). The section's description assumes a well-formed
  file of 30 records; here every record must be exactly 62 bytes, a malformed record is
  reported with its line number before any name is answered, and there is no fixed limit on
  the number of records.
- **Sources can be chosen.** `-f`, `--file` overrides `students.dat`, and an optional FILE
  operand supplies the names instead of the keyboard (FR-01, FR-05). Unreadable files are
  diagnosed (FR-09); the section's description specifies no behavior for them.
- **Data files** with CRLF line endings and a trailing Ctrl-Z marker are accepted, for both
  the student file and the name input (FR-02, FR-05).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (only its definition of line numbers; neither input is read as tokens),
CONV-34 (data diagnostics, with one message of this tool's own, `invalid record length`; because
of FR-09, no answer has been written when one is reported), CONV-36 (`-p`, `--prompt`), and
CONV-37 (the student file and the name input are both _text data_). CONV-33 and CONV-35 do not
apply, because no number is read or written as a value; CONV-38 does not apply, because nothing
is random. Option syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and
the exit statuses are those of CONV-18. Standard input is read only when STUDENTS or NAMES is
`-` (CONV-26). Records and names are copied to standard output byte for byte, but a CR at the
end of a line is removed (FR-02, FR-05); this is the "unless the SRS says otherwise" case of
CONV-04.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-phone [-f FILE | --file=FILE] [-p | --prompt] [FILE]
dp-phone --help
dp-phone --version
```

### 3.2 Options

| Short | Long        | Argument        | Default        | Description                                                         |
| :---- | :---------- | :-------------- | :------------- | :------------------------------------------------------------------ |
| `-f`  | `--file`    | FILE (required) | `students.dat` | Read the student records from FILE; `-` is standard input (FR-01)   |
| `-p`  | `--prompt`  | none            | off            | Write the prompt to standard error before each name is read (FR-08) |
| —     | `--help`    | none            | —              | Print the help text and exit 0                                      |
| —     | `--version` | none            | —              | Print the version line and exit 0                                   |

Option syntax (bundling, `-fFILE`, `--file FILE`, `--`, repetition, and scan order) follows
CONV-07 … CONV-12. If `--file` is repeated, the last occurrence wins; giving `-p` more than once
has the same effect as giving it once (CONV-11). The value of `-f` may begin with `-` when it is
attached (`--file=-x`, `-f-x`) or supplied as the next token (`-f -x`). An empty value, and the
value `-` when NAMES is also `-`, are invalid option values (FR-12).

### 3.3 Operands

At most one FILE operand: the name input. The operand `-` denotes standard input (CONV-10).
Every token after `--` is an operand, even if it begins with `-`. The operand is used and
echoed exactly as given (CONV-19).

### 3.4 Standard input

Read when STUDENTS is `-` (the student file) or NAMES is `-` (the name input), never both
(FR-12). Read as raw bytes; no newline translation of any kind is performed on any platform.

### 3.5 Standard output

One answer line per non-empty name (FR-07), in input order. Nothing else. On a usage error, or
when `--help` / `--version` is handled, the output is as specified by FR-10 … FR-13 instead.

### 3.6 Standard error

Prompts (FR-08, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                        |
| :----- | :------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The end of the name input was reached (whether or not any name was found), or `--help` / `--version` was handled                 |
| 1      | A file could not be read (FR-09), the student file contained a malformed record (FR-03), or standard output could not be written |
| 2      | Usage error (FR-12)                                                                                                              |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are public fixture files in
`tests/fixtures/`: `students.dat` is the textbook's file of 30 records (from the companion
disk); `names.txt` is `Turing\nKnuth\nLovelace\nGosling\n`; `edges.txt` is
`Apl\nVon Neumann\nAbel\nZuse\nturing\nVon\n`; `more.dat` holds five records, in this order,
for Adams Cy, Clark Dee, Adams Ann, Baker Eve, and Adams Bob; `dups.txt` is
`Adams\nBaker\nClark\nAdam\n`; `bad.dat` is `students.dat` with the last byte of record 4
removed. `T` denotes the 71 bytes
`Record: Turing                   Alan                     508-416-0633\n`.

**FR-01: Student file.**
If STUDENTS is `-`, the tool MUST read standard input to its end as the student file.
Otherwise it MUST open the file STUDENTS (a path relative to the current directory unless
absolute) and read it to its end as raw bytes. Without `-f`/`--file`, STUDENTS is
`students.dat`.
_AC:_ `dp-phone < names.txt` answers from `students.dat`; `dp-phone -f - names.txt <
students.dat` writes the same answers. _(UR-01, UR-06)_

**FR-02: Records.**
The student file is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to
the very end of the file is ignored. The remaining bytes are divided into lines (section 1.3).
From each line, one CR at its end, if present, is removed; the result MUST be exactly 62 bytes
long, and is a record. The fields are not otherwise checked: any byte other than LF may appear
in any column, and the blanks that pad a field are part of the record. An empty student file
(or one that is only a Ctrl-Z run) has no records and is valid.
_AC:_ `students.dat` yields 30 records; a file whose lines end in CRLF and that ends with
Ctrl-Z bytes yields the same records as the same file with LF endings; a final record without
an LF is accepted. _(UR-01, UR-09)_

**FR-03: Malformed records.**
If a line, after CR removal, is not exactly 62 bytes long, the tool MUST write
`dp-phone: <source>:<line>: invalid record length <n>, expected 62`, where `<source>` is
STUDENTS exactly as given (`-` for standard input), `<line>` is the line number, and `<n>` is
the line's length in bytes after CR removal, in decimal. An empty line in the student file
(for example a blank line between records, or at the end after the final LF) has length 0 and
is therefore malformed; so is a line that holds only a `0x1A` byte followed by an LF, because
that byte does not extend to the end of the file. Only the first malformed line is reported.
The tool then exits with status 1, before any name is read and before any prompt is written
(FR-09).
_AC:_ `dp-phone -f bad.dat names.txt` → stdout empty, stderr
`dp-phone: bad.dat:4: invalid record length 61, expected 62\n`, exit 1. A line with one
trailing space gives `invalid record length 63, expected 62`. _(UR-08, UR-10)_

**FR-04: Selection sort.**
After all records have been read and checked, the tool MUST sort them into ascending byte
order of the **whole record** (62 bytes) with selection sort: for _i_ = 0, 1, …, _N_ − 2
(where _N_ is the number of records, indexed from 0), find the index _m_ of a smallest record
among positions _i_ … _N_ − 1, and exchange the records at positions _i_ and _m_. Because two
records that compare equal are identical, the resulting directory is the same for every
correct sort. Records are sorted, never removed: identical records remain as duplicates.
_AC:_ the directory of `students.dat` begins with the record of `Apl` and ends with the record
of `Von Neumann`; both are found (FR-06). _(UR-13)_

**FR-05: Names.**
If NAMES is `-`, names are read from standard input; otherwise from the file NAMES, opened as
raw bytes. The name input is _text data_ (CONV-37) and is divided into lines (section 1.3). A
run of `0x1A` bytes that extends to the very end of the input is ignored: it is removed from
the end of the last line, and a last line that consists only of such bytes is not a line at
all. A `0x1A` byte followed by any other byte is ordinary data. From each line, one CR at its
end, if present, is removed; the result is the name. A name may contain any bytes, including
spaces and TABs; leading and trailing spaces are part of the name. Names are processed one at a
time in input order: an empty name (zero bytes) produces no answer, and every other name
produces exactly one answer line (FR-07). As soon as a line is complete (its LF has been read,
or the input has ended), the tool MUST write and flush the answer before it waits for further
input bytes; it MUST NOT wait for the end of the input before answering.
_AC:_ `dp-phone < names.txt` → stdout `T` + `Knuth is not in our directory.\n` +
`Record: Lovelace                 Ada                      212-789-0979\n` +
`Gosling is not in our directory.\n`, stderr empty, exit 0. A line `\r\n` is an empty name;
`Hopper\x1a\x1a` at the end of the input is the name `Hopper`. `dp-phone` with empty standard
input → stdout and stderr empty, exit 0. _(UR-02, UR-04, UR-07, UR-09)_

**FR-06: Binary search.**
For a name of _n_ bytes with _n_ ≤ 25, the tool MUST form the key (section 1.3) and search the
directory with this binary search, comparing in byte order: set _low_ = 0 and _high_ = _N_ − 1;
while _low_ ≤ _high_, let _mid_ = ⌊(_low_ + _high_) / 2⌋ and compare the key with the last name
of the record at position _mid_: if they are equal, the search succeeds with that record; if
the key is smaller, set _high_ = _mid_ − 1; otherwise set _low_ = _mid_ + 1. When _low_ >
_high_, the search fails. Because the records are sorted by whole record and the last name is
its first 25 bytes, the last names are in ascending order too. When several records share the
key, the record reported is the one this procedure reaches first. A name of more than 25 bytes
cannot equal a 25-byte last name: no search is made, and the name is not found. Consequently
matching is exact and case-sensitive, trailing spaces in a name up to a total of 25 bytes do
not matter (`Turinginds `Turing`), and leading spaces do (`Trn`is not found).
_AC:_`dp-phone edges.txt`→`Apl`and`Von Neumann`found;`Abel`, `Zuse`, `turing`, and `Von`not found.`dp-phone -f more.dat dups.txt`reports`Adams Cy`for`Adams`(the directory is
Adams Ann, Adams Bob, Adams Cy, Baker Eve, Clark Dee, and the first midpoint is position 2) and`Adam is not in our directory.` A name of exactly 25 bytes equal to a last name is found; the
same name with one more byte is not. _(UR-02, UR-03, UR-13)_

**FR-07: Answers.**
For a name that is found, the answer MUST be `Record:8 bytes, ending with one space)
followed by the 62 bytes of the record and an LF. For a name that is not found, the answer MUST
be the name's exact bytes followed by `not in our directory.`(beginning with one space)
and an LF. No other bytes are written: no blank lines, no indentation, no header or summary.
_AC:_ the answer for`Turing`is`T`; the answer for `Knuth`is`Knuth is not in our directory.\n`; the answer for a name of three spaces is
`r directory.\n` (four spaces). _(UR-02)_

**FR-08: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 47 bytes
`Enter a student's name, or signal EOF to halt:ending with one space, no LF). With prompts
enabled, the tool MUST write the prompt to standard error, and flush standard error,
immediately before each attempt to read a line of the name input: once before the first line,
and once after each line has been processed (whether it was answered or was empty). A prompt is
therefore also written before the attempt that reaches the end of the input (CONV-36): a name
input of _k_ lines produces _k_ + 1 prompts. Prompts never change standard output. No prompt is
written if the student file cannot be read, contains a malformed record, or the name input
cannot be opened.
_AC:_ `dp-phone --prompt < names.txt` → stdout as in FR-05, stderr the prompt five times with no
LF, exit 0. _(UR-05)_

**FR-09: Order of operations and unreadable files.**
After a successful scan of the arguments, the tool MUST proceed in exactly this order and stop
at the first failure: (1) read the whole student file (FR-01); (2) check every record (FR-02,
FR-03); (3) sort (FR-04); (4) open the name input; (5) prompt, read, and answer names until the
end of the name input (FR-05 … FR-08), then exit with status 0. If STUDENTS or NAMES does not
exist, cannot be opened, is a directory, or a read error occurs, the tool MUST write
`dp-phone: <path>: <reason>`, where `<path>` is STUDENTS or NAMES exactly as given (`-` for
standard input) and `<reason>` is from the CONV-16 table, and exit with status 1. A failure in
steps 1 … 4 therefore writes nothing to standard output; after a read error in step 5, the
answers already written are kept.
_AC:_ `dp-phone --file=missing.dat names.txt` → stderr
`dp-phone: missing.dat: No such file or directory\n`, stdout empty, exit 1;
`dp-phone missing.txt` → `dp-phone: missing.txt: No such file or directory`, exit 1;
`dp-phone -p subdir`, where `subdir` is a directory → `dp-phone: subdir: Is a directory`, no
prompt. _(UR-10)_

**FR-10: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No file is read and no prompt is
written.
_AC:_ `dp-phone --help` matches the user manual exactly; `dp-phone extra --help` also prints it.
_(UR-11)_

**FR-11: Version.**
`--version` MUST write `dp-phone (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-phone -f missing.dat --version` also prints it and exits 0. _(UR-11)_

**FR-12: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--prompt=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--fi` is
unrecognized. An empty STUDENTS value MUST be reported as
`dp-phone: invalid argument '' for '<option>'`, where `<option>` is `-f` or `--file` as the
user wrote it. Because standard input cannot supply both the records and the names, STUDENTS
`-` when NAMES is also `-` (no operand, or the operand `-`) MUST be reported as
`dp-phone: invalid argument '-' for '<option>'`. Only the winning occurrence of a repeated
`--file` is checked (CONV-11). A second operand MUST be reported as
`dp-phone: extra operand '<second operand>'`. Option values and operands are checked after the
whole argument list has been scanned (CONV-12).
_AC:_ `dp-phone names.txt edges.txt` → `dp-phone: extra operand 'edges.txt'`;
`dp-phone -f ''` → `dp-phone: invalid argument '' for '-f'`; `dp-phone -f - < names.txt` →
`dp-phone: invalid argument '-' for '-f'`; `dp-phone --prompt=yes` →
`dp-phone: option '--prompt' doesn't allow an argument`; `dp-phone -pf` →
`dp-phone: option requires an argument -- 'f'`; each followed by the CONV-14 line, exit 2.
_(UR-12, UR-14)_

**FR-13: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any file, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-phone -p -f- - < names.txt` writes no prompt.
_(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                                 | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Verification                                                    |
| :----- | :------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                              | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: fixed-width bytes and line endings | Both inputs MUST be read in binary mode on every platform, so that column positions are counted in bytes exactly as stored: a CRLF line MUST reach the record check with its CR (which FR-02 then removes), a `0x1A` byte MUST never be treated as end-of-file by the I/O layer, and no text-mode or locale conversion may change the length of a record. Comparisons MUST be byte comparisons of unsigned bytes, never locale collation or case folding, so that non-ASCII last names (such as UTF-8 `Zoë`, 4 bytes) sort and match identically everywhere; a field's width is 25 bytes, not 25 characters. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the name input normally, and each answer MUST be flushed (FR-05) even when standard output is a pipe or a file. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance                                              | Loading and sorting a student file of 2 000 records and answering 100 000 names MUST take under 1 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MAY grow linearly with the number of records but MUST NOT grow with the number of names. Each lookup MUST make at most ⌊log₂ _N_⌋ + 1 key comparisons. Start-up and exit for an empty name input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                  | Measurement; unit test                                          |
| NFR-04 | Robustness                                               | The tool MUST NOT crash, panic, or print a stack trace for any argument list, input bytes, or file-system condition (CONV-24), including lines of any length and an empty student file. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Unit + black-box tests                                          |
| NFR-05 | Maintainability                                          | Option parsing, record loading and checking, the sort, the search, answer formatting, and I/O MUST be separate units. The sort MUST be one function that implements the selection sort of FR-04 and the search one function that implements the binary search of FR-06, each written by the implementer without library sort or search routines; neither may read input or write output. The field widths 25, 25, and 12 MUST each be defined once.                                                                                                                                                                                                                                                                                                                                                                                                                               | Design review                                                   |
| NFR-06 | Testability                                              | The sort and search functions MUST be pure (apart from the in-place exchange of FR-04) and covered by unit tests: an empty directory, one record, the first and last records, names below the first and above the last last name, duplicate last names (checking which record FR-06 reports), identical records, and keys that differ only in a byte above `0x7F`. The line reader MUST be unit-tested with the input split into reads at every byte position, including inside a CRLF pair.                                                                                                                                                                                                                                                                                                                                                                                      | Code review                                                     |
| NFR-07 | Build                                                    | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | CI                                                              |
| NFR-08 | Security                                                 | The tool MUST read only STUDENTS and NAMES (or standard input), MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-phone --help' for more information.`

| Trigger                                      | Exact first line                                                                       |
| :------------------------------------------- | :------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-phone: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-phone: unrecognized option 'T'`                                                    |
| `-f` without an argument                     | `dp-phone: option requires an argument -- 'f'`                                         |
| `--file` without an argument                 | `dp-phone: option '--file' requires an argument`                                       |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-phone: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| Empty STUDENTS for `-f` or `--file`          | `dp-phone: invalid argument '' for '-f'` (or `'--file'`)                               |
| STUDENTS is `-` and NAMES is `-`             | `dp-phone: invalid argument '-' for '-f'` (or `'--file'`)                              |
| A second operand `X`                         | `dp-phone: extra operand 'X'`                                                          |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                                 | Exact message                                         |
| :---------------------------------------------------------------------- | :---------------------------------------------------- |
| STUDENTS or NAMES `F` does not exist                                    | `dp-phone: F: No such file or directory`              |
| `F` cannot be opened or read because access is denied                   | `dp-phone: F: Permission denied`                      |
| `F` is a directory                                                      | `dp-phone: F: Is a directory`                         |
| A component of `F` is not a directory                                   | `dp-phone: F: Not a directory`                        |
| Any other open or read failure of `F`                                   | `dp-phone: F: Input/output error`                     |
| Any of the above for standard input                                     | the same message with `F` = `-`                       |
| Line `L` of student file `S` is `N` bytes long after CR removal, not 62 | `dp-phone: S:L: invalid record length N, expected 62` |
| Standard output cannot be written (other than a broken pipe)            | `dp-phone: write error`                               |

When `--prompt` is given, a read error on the name input is reported after the last prompt, on
the same line of standard error (CONV-36). Problems with the student file are always reported
before the first prompt.

## 7. Verification

| Method                                                                                       | Applies to                                                                    |
| :------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                           | FR-01 … FR-10, FR-12                                                          |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 04 … 08 and 10 have several steps) | FR-01 … FR-13                                                                 |
| Unit test (written by the implementer)                                                       | FR-02, FR-04 … FR-07, NFR-06                                                  |
| Measurement                                                                                  | NFR-03                                                                        |
| Inspection / review                                                                          | FR-04, FR-06 (algorithms), FR-05 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                                 | Verifies                                                                            |
| :--- | :-------------------------------------- | :---------------------------------------------------------------------------------- |
| 01   | `dp-phone < names.txt`                  | FR-01 (default file), FR-02, FR-04 … FR-07                                          |
| 02   | `dp-phone --prompt < names.txt`         | FR-08                                                                               |
| 03   | `dp-phone edges.txt`                    | FR-04 (first and last records), FR-05 (names with spaces), FR-06 (case, boundaries) |
| 04   | `dp-phone -f more.dat dups.txt`         | FR-01 (`-f`), FR-04, FR-06 (duplicate last names, midpoint rule)                    |
| 05   | `dp-phone -f bad.dat names.txt`         | FR-03, FR-09 (nothing answered)                                                     |
| 06   | `dp-phone --file=missing.dat names.txt` | FR-09 (student file)                                                                |
| 07   | `dp-phone` (empty standard input)       | FR-05 (no names, exit 0)                                                            |
| 08   | `dp-phone --help`                       | FR-10                                                                               |
| 09   | `dp-phone missing.txt`                  | FR-09 (name input)                                                                  |
| 10   | `dp-phone names.txt edges.txt`          | FR-12, FR-13                                                                        |

## 8. Traceability (URD → SRS)

| User requirement | System requirements               |
| :--------------- | :-------------------------------- |
| UR-01            | FR-01, FR-02                      |
| UR-02            | FR-05, FR-06, FR-07               |
| UR-03            | FR-05, FR-06                      |
| UR-04            | FR-05, NFR-02                     |
| UR-05            | FR-08, CONV-36                    |
| UR-06            | FR-01, FR-05, FR-12, CONV-26      |
| UR-07            | FR-05, FR-07                      |
| UR-08            | FR-03, FR-09, CONV-34             |
| UR-09            | FR-02, FR-05, NFR-02, CONV-37     |
| UR-10            | FR-03, FR-09, CONV-16             |
| UR-11            | FR-10, FR-11                      |
| UR-12            | FR-12, FR-13                      |
| UR-13            | FR-04, FR-06, NFR-05, NFR-06      |
| UR-14            | NFR-01, NFR-02, CONV-03, CLI-CONV |
| UR-15            | NFR-03, NFR-07                    |
