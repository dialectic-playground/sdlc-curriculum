<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-line-ed](#software-requirements-specification-srs--dp-line-ed)
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
    - [4.1 Files and input](#41-files-and-input)
    - [4.2 Buffer and commands](#42-buffer-and-commands)
    - [4.3 Errors, end of input, and prompts](#43-errors-end-of-input-and-prompts)
    - [4.4 Help, version, and usage](#44-help-version-and-usage)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-line-ed

| Field                     | Value                                              |
| :------------------------ | :------------------------------------------------- |
| Document ID               | SRS-44                                             |
| Project                   | `44-line-editor` — Modal Line-Oriented Text Editor |
| Product                   | `dp-line-ed` (canonical name)                      |
| Version                   | 1.0.0                                              |
| Status                    | Approved (pre-written by the curriculum)           |
| Parent document           | `URD.md` (URD-44)                                  |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)       |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018               |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-line-ed`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output and file contents for every invocation. It is the authoritative
source for design (HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-line-ed` loads the file named by its operand into a buffer of lines (an empty buffer if the
file does not exist), then reads commands from standard input, one per line, and executes them
against the buffer and its current line: insert lines (`i`), delete lines (`d`), type lines
(`t`), move forward (`m`), find a line (`f`), substitute text (`s`), and write the file and quit
(`q`). It reports a bad command with its line number and continues. It can write a prompt to
standard error before each command is read.

### 1.3 Definitions

| Term              | Definition                                                                                                                                          |
| :---------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR            | The bytes `0x0A` and `0x0D`                                                                                                                         |
| Blank             | The byte `0x20` (space) or `0x09` (TAB)                                                                                                             |
| FILE              | The operand, exactly as given: the path of the file that is loaded and written                                                                      |
| Text line         | A byte string that contains no LF; it may contain any other bytes, including CR and NUL                                                             |
| Buffer            | The sequence of text lines L1 … L*n* (_n_ ≥ 0) being edited, preceded by the sentinel                                                               |
| Sentinel, `[BOF]` | Position 0, before L1. It holds no text line and is never written to FILE                                                                           |
| Current line      | A position _c_ with 0 ≤ _c_ ≤ _n_: the sentinel (_c_ = 0) or the text line L*c*                                                                     |
| Type              | To _type_ a position is to write to standard output the bytes of its text line followed by one LF, or, for the sentinel, the 6 bytes `[BOF]` and LF |
| Input line        | A line of standard input as defined by FR-03, with its line number                                                                                  |
| Command line      | An input line read while the editor waits for a command (not in insert mode)                                                                        |
| Word              | A maximal run of bytes other than blanks                                                                                                            |
| Count             | A word that is a valid _integer_ (CONV-33) with a value from 1 to 9223372036854775807 (FR-05)                                                       |
| Delimited string  | A string enclosed in a pair of delimiter bytes (FR-10)                                                                                              |
| Failed command    | A command for which a diagnostic of FR-14 was written                                                                                               |

### 1.4 References

- URD-44: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §10.3 (informative; see §2.5)
- POSIX.1-2017, `ed` utility (informative: the tradition this editor belongs to)

## 2. Overall description

### 2.1 Product perspective

`dp-line-ed` is a standalone executable. Its interfaces are the command line, the file FILE
(read once at start-up, written only by `q`), standard input (commands and inserted text),
standard output (typed lines), standard error, and the exit status. It belongs to the
curriculum's applications-programming track (Projects 11–52) and adapts §10.3 of Johnsonbaugh &
Kalin, _Applications Programming in ANSI C_. It builds on the singly linked lists of Project 43
(`dp-elephnt1`, `dp-elephnt2`).

### 2.2 Product functions

1. Load FILE into a buffer of text lines, or start with an empty buffer if FILE does not exist.
2. Read commands from standard input, one per line, and execute them: `i`, `d`, `t`, `m`, `f`,
   `s`, `q`.
3. Type lines to standard output as commands require.
4. Report a failed command, leave the buffer unchanged, and continue.
5. On `q`, write the buffer to FILE and exit; at the end of the input without `q`, exit without
   writing.
6. Optionally write the prompt `*` to standard error before each command is read.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, plus the buffer design of NFR-05.
- FILE MUST be read and written as raw bytes (NFR-02).

### 2.4 Assumptions

- Standard input may be a terminal, a pipe, or a file; standard output likewise. Behavior is the
  same in every case, apart from the timing guaranteed by FR-03.
- Nothing else modifies FILE while the editor runs. Relative paths are relative to the current
  working directory.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §10.3 asks for a file name, loads the file into a linked list that
starts with a `[BOF]` header node, and keeps a pointer to the current line. At its `*` prompt it
obeys `i` (insert lines after the current line until a terminating line), `d` (delete lines
after the current line), `t` (type: `.` the current line, `b` the top, `e` the bottom, or a
number of lines), `m` (move forward), `f` (find a delimited pattern), `s` (substitute a
delimited string), and `q` (write the file and quit). `dp-line-ed` keeps:

- the linked buffer headed by the `[BOF]` sentinel, and the current-line pointer (NFR-05);
- the seven commands, their letters, and their argument forms, including delimited patterns
  such as `'cat'` and the choice of delimiter (FR-05 … FR-13);
- a missing file as an empty buffer, and writing the file only on `q`, without the sentinel;
- the prompt `*`, written before each command and not in insert mode (FR-16).

It changes or fixes the following, for the reasons given:

- **The file name is an operand.** The textbook asks for it at run time. As an operand it is
  checked before any command is read, and a usage error (FR-19) replaces a prompt that a script
  would have to answer. Standard input is reserved for commands, so the operand `-` names an
  ordinary file called `-` (§2.6).
- **Every command has one specified outcome.** The section's description leaves open what
  happens when a command would move past the end of the buffer, when `d` runs out of lines, when
  a pattern is not found, and when a command is malformed. Here motion and counts are clamped
  to the end of the buffer without error (FR-07 … FR-09), a pattern that is not found and a
  malformed command are reported with the command's line number, the buffer is left unchanged,
  and the session continues (FR-14). The exit status records that a command failed, so a script
  can tell.
- **Insert mode ends with a line holding a single `.`**, the convention of `ed`, or at the end
  of the input (FR-06).
- **`s` types the changed line** (FR-12), as `f` and `m` type the line they reach, so that every
  change is visible; `t` with a count types the lines _after_ the current line and does not move
  it, so that `t N` shows exactly the lines a following `d N` deletes (FR-07, FR-08).
- **The end of the input without `q` does not write the file** (FR-15). The textbook does not
  define it. Quitting is the only way to commit changes, so a truncated script or an accidental
  Ctrl-D cannot overwrite the file with a half-edited buffer; the run ends with
  `unexpected end of input` and exit status 1.
- **Bytes are preserved.** FILE is read and written in binary mode; CR bytes are part of the
  lines, so a CRLF file keeps its line endings, and a trailing Ctrl-Z marker is understood
  (FR-02). Each written line ends with LF, so a final line without LF gains one.
- **Prompts are optional and go to standard error** (FR-16), so that typed lines are the only
  content of standard output whether or not the prompt is shown.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV with **two overrides**. (1) CONV-10: the operand `-` does not
denote standard input; it names a file called `-`, because standard input carries the commands
(§3.3). (2) CONV-34: a diagnostic about a command does not end processing; the buffer is left
unchanged, the session continues, and the exit status is 1 when the run ends (FR-14). The
diagnostic for an input that ends without `q` has the CONV-34 default consequences (FR-15).
From section 10 it incorporates: CONV-32 (only the definition of line numbers; standard input is
line-oriented, FR-03), CONV-33 (counts use the _integer_ grammar, further restricted to
1 … 2⁶³−1), CONV-34 (the diagnostic format, with the standard messages `invalid integer`,
`value out of range`, and `unexpected end of input`, and the project-specific messages of
FR-14), CONV-36 (`-p`, `--prompt`, with the single prompt `*`), and CONV-37 (both FILE and
standard input are _text data_). CONV-35 does not apply, because no real number is written;
CONV-38 does not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12,
diagnostics follow CONV-13 … CONV-16 (CONV-16 is applied to FILE both when it is loaded and when
it is written), and the exit statuses are those of CONV-18. CONV-04 applies to the bytes of
text lines, which are passed from FILE and standard input to standard output and FILE unchanged
apart from the rules of FR-02 and FR-03.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-line-ed [-p | --prompt] FILE
dp-line-ed --help
dp-line-ed --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the prompt `*` to standard error before each command is read (FR-16) |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                             |
| —     | `--version` | none     | —       | Print the version line and exit 0                                          |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands

Exactly one FILE operand. It is used and echoed exactly as given (CONV-19). Every token after
`--` is an operand, even if it begins with `-`. The operand `-` is an ordinary file name, not
standard input (§2.6). An empty operand names no file: it is loaded as an empty buffer (FR-01),
and `q` then fails with `No such file or directory` (FR-13).

### 3.4 Standard input

Commands and inserted text, read line by line as raw bytes (FR-03). No newline translation of
any kind is performed on any platform.

### 3.5 Standard output

Typed lines (FR-04), in the order the commands produce them. Nothing else. On a usage error, or
when `--help` / `--version` is handled, the output is as specified by FR-17 … FR-20 instead.

### 3.6 Standard error

The prompt (FR-16, only with `--prompt`) and diagnostics (section 6).

### 3.7 Files

FILE is opened for reading once, before the first command is read (FR-01), and closed. It is
created or truncated and written only by `q` (FR-13). No other file is created, modified,
deleted, or renamed.

### 3.8 Exit status

| Status | Condition                                                                                                                                                                                                                                                       |
| :----- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | `q` wrote FILE and no command failed; or `--help` / `--version` was handled                                                                                                                                                                                     |
| 1      | At least one command failed (FILE is still written if `q` follows, FR-14); the input ended without `q` (FILE not written, FR-15); FILE could not be loaded or written (FR-01, FR-13); standard input could not be read; or standard output could not be written |
| 2      | Usage error (FR-19)                                                                                                                                                                                                                                             |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF and `\r` CR, and the following are public fixture files
in `tests/fixtures/`: `poem.txt` holds the five lines L1 `The cat sat on the mat.`,
L2 `It saw a rat.`, L3 `The rat ran.`, L4 `The cat ran after the rat.`, and L5 `The end.`, each
followed by LF; `cmd-list.txt` is `t 1000000\nq\n`, which types the whole file and writes it
back unchanged. "A later `cmd-list.txt` step" means running `dp-line-ed FILE < cmd-list.txt`
again in the same directory to see what an earlier step wrote.

### 4.1 Files and input

**FR-01: Loading FILE.**
Before reading any command or writing any prompt, the tool MUST read FILE completely as raw
bytes and build the buffer from it (FR-02). If FILE does not exist — the path, or a directory
on it, is absent (`ENOENT`, `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND`) — the buffer is
empty and this is not an error; FILE is not created until `q`. If FILE is a directory, cannot be
opened or read for any other reason, the tool MUST write `dp-line-ed: <FILE>: <reason>` with
`<reason>` from the CONV-16 table and exit with status 1, without reading standard input.
After loading, the current line is the sentinel (_c_ = 0).
_AC:_ `dp-line-ed new.txt < cmd-new.txt` (insert two lines, then `q`) creates `new.txt`, and a
later `cmd-list.txt` step types the two lines; `dp-line-ed subdir < cmd-list.txt` →
`dp-line-ed: subdir: Is a directory`, stdout empty, exit 1; `dp-line-ed missing.txt <
cmd-list.txt` → stdout empty, exit 0. _(UR-01)_

**FR-02: Lines of FILE.**
The contents of FILE are _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to
the very end of the file is ignored. The rest is divided into text lines: each LF ends a line,
and bytes after the last LF, if there are any, form a final line. A file that ends with LF
therefore has no empty line after it, an empty file has no lines, and a file holding only `\n`
has one empty line. The LF is not part of the line. Every other byte, including CR, NUL, and
bytes that are not valid UTF-8, is part of the line and is preserved exactly: typed by FR-04,
matched by FR-11 and FR-12, and written by FR-13. A `0x1A` byte that is followed by any other
byte is ordinary data.
_AC:_ the hidden fixture `alpha\r\nbeta\r\ngamma` followed by `0x1A` loads as the lines
`alpha\r`, `beta\r`, `gamma`; typing them writes `alpha\r\nbeta\r\ngamma\n`; `one`, `0x1A`, LF,
`two`, LF, `0x1A 0x1A` loads as `one` + `0x1A` and `two`. _(UR-11)_

**FR-03: Standard input.**
Standard input is _text data_ (CONV-37) and is read one line at a time: each LF ends an input
line, and bytes after the last LF form a final input line, except that a run of `0x1A` bytes
reaching the very end of the input is ignored (if nothing else remains of the final line, there
is no final line). From each input line the LF is removed, and then one CR, if the line ends
with one; any other CR is an ordinary byte. The line number of an input line follows CONV-32.
The tool MUST process each input line as soon as it is complete — executing the command, writing
its output, and flushing standard output — before it waits for further input, and MUST NOT read
beyond the current line apart from ordinary buffering of bytes that are already available.
_AC:_ the hidden command file with CRLF line ends and a final `0x1A` gives the same results as
its LF version; at a terminal, `t e` and Enter shows the last line before anything else is typed
(manual check). _(UR-09, UR-11)_

### 4.2 Buffer and commands

**FR-04: Buffer, current line, and typing.**
The buffer consists of the sentinel followed by the text lines L1 … L*n*, and the current line
_c_ always satisfies 0 ≤ _c_ ≤ _n_. No command can move _c_ outside this range: every motion is
clamped to the last line (FR-08, FR-09). Typing a position writes its text line and LF, or
`[BOF]` and LF for the sentinel (section 1.3); a text line that happens to read `[BOF]` is typed
the same way.
_AC:_ `dp-line-ed poem.txt < cmd-type.txt` → the first command `t .` types `[BOF]`. _(UR-02)_

**FR-05: Command syntax.**
Each command line is processed as follows:

1. Leading and trailing blanks are removed. If nothing remains, the line is ignored: it is not a
   command, produces no output, and does not fail.
2. The first word is the _command word_. The rest of the line, with its leading blanks removed,
   is the _argument text_. The command word MUST be exactly one of `i`, `d`, `t`, `m`, `f`,
   `s`, `q` (lowercase); any other word fails with `unknown command '<word>'`, so `Q`, `quit`,
   and `d3` are unknown commands.
3. The argument text is checked from left to right against the command's form, and the first
   problem found fails the command:

   | Command  | Form                       | Arguments                                              |
   | :------- | :------------------------- | :----------------------------------------------------- |
   | `i`, `q` | `i`, `q`                   | none                                                   |
   | `d`      | `d [N]`                    | an optional count, default 1                           |
   | `t`      | `t .`, `t b`, `t e`, `t N` | one word: `.`, `b`, `e`, or else a count               |
   | `m`      | `m N`                      | one count                                              |
   | `f`      | `f 'PAT'`                  | one delimited string (FR-10), not empty                |
   | `s`      | `s 'OLD' 'NEW'`            | two delimited strings; OLD not empty, NEW may be empty |

   For `d`, `t`, and `m`, the argument text is divided into words. A required word that is
   absent fails with `missing argument`. A word that must be a count is checked by the
   _integer_ grammar of CONV-33: a word that does not match it, or lies outside
   −2⁶³ … 2⁶³−1, fails with `invalid integer '<word>'`; a valid integer below 1 fails with
   `value out of range '<word>'`. A sign and leading zeros are allowed (`+2`, `007`). For every
   command, a word left over after the last argument fails with `extra argument '<word>'`,
   naming the first such word.

4. Only a command that passes these checks is executed (FR-06 … FR-13); its own conditions
   (`no current line`, `pattern not found`) are checked after the syntax.

_AC:_ the hidden test `cmd-counts.txt` reports `d 0` and `m -1` as `value out of range`,
`t 9223372036854775808` as `invalid integer`, `m` and `t` as `missing argument`, `d 1 2` as
`extra argument '2'`, `t . x` as `extra argument 'x'`, and `Q` as `unknown command 'Q'`; it
accepts `m +2`, `t 007`, `t   e>1`, and ignores blank lines. _(UR-10)_

**FR-06: `i` — insert.**
`i` enters insert mode: each following input line is inserted into the buffer immediately after
the current line, which then moves to the inserted line, so the lines appear in the order typed.
Insert mode ends at an input line that consists of exactly one `.` byte (after the removal of
LF and CR, FR-03), which is consumed and not inserted, or at the end of the input. Inserted
lines are taken exactly as read: they are not trimmed, and a line `or `..`is inserted. No
prompt is written in insert mode and nothing is typed. When no line is inserted, the current
line is unchanged. A line that consists of exactly`.`cannot be inserted.
_AC:_`dp-line-ed poem.txt < cmd-insert.txt`inserts`A Poem`and`======`before L1 (after`t b`) and `-- Anonymous`after L5 (after`t e`); a later `cmd-list.txt` step types the eight
lines in that order. _(UR-04)_

**FR-07: `d [N]` — delete.**
`d N` deletes the lines L*c*+1 … L*m*, where _m_ = min(_c_ + _N_, _n_); `d` alone deletes one
line. The current line is not moved and is not deleted. If fewer than _N_ lines follow the
current line, only those are deleted; if none follow, nothing happens. Neither case is an error,
and `d` types nothing.
_AC:_ `dp-line-ed poem.txt < cmd-delete.txt` → after `m 1`, `d` deletes L2; after `d 2` the
buffer is L1, L5; a final `d 5` on the last line deletes nothing; a later `cmd-list.txt` step
types `The cat sat on the mat.` and `The end.`. _(UR-05)_

**FR-08: `t` — type.**

- `t .` types the current line (the sentinel types `[BOF]`).
- `t b` moves the current line to the sentinel and types L1; on an empty buffer it types
  nothing.
- `t e` moves the current line to L*n* and types it; on an empty buffer the current line is the
  sentinel, and `[BOF]` is typed.
- `t N` types the lines L*c*+1 … L*m*, where _m_ = min(_c_ + _N_, _n_), one per line, and does
  not move the current line. If no line follows the current line, it types nothing.

_AC:_ `dp-line-ed poem.txt < cmd-type.txt` → `t .` `[BOF]`; `t b` L1; `t 3` L1, L2, L3; `t .`
`[BOF]`; `m 2` L2; `t .` L2; `t 2` L3, L4; `t e` L5; `m 1` L5; `t b` L1; exit 0. _(UR-02)_

**FR-09: `m N` — move.**
`m N` moves the current line to position min(_c_ + _N_, _n_) and types it. When the current line
is already the last line, or the buffer is empty, it stays where it is and is typed again
(`[BOF]` for the sentinel). Moving backward is not possible.
_AC:_ in `cmd-type.txt`, `m 1` on L5 types L5 again. _(UR-03)_

**FR-10: Delimited strings.**
The argument of `f`, and each of the two arguments of `s`, is a delimited string. It begins at
the first byte of the remaining argument text, which is its _delimiter_ and MUST be a byte in
`0x21`–`0x7E` that is not an ASCII letter or digit (for example `'`, `"`, `/`, `|`, `#`, `.`).
The string consists of all bytes after the delimiter up to, but not including, the next
occurrence of the same delimiter byte; it may contain blanks and any other bytes. After the
closing delimiter, blanks are skipped, and the next argument (or the end of the argument text)
begins. Each string has its own delimiter, so `s "it's" 'it is'` is valid, and the two strings
of `s` may follow each other without a blank (`s 'a''b'`). A delimited string fails as follows,
in this order: no argument text left → `missing argument`; the first byte is not a valid
delimiter → `missing delimiter`; no closing delimiter → `unterminated string`. An empty `f`
pattern or `s` OLD string fails with `empty pattern` as soon as it has been read, before the
rest of the argument text is examined.
_AC:_ the hidden test `cmd-strings.txt` reports `f ''` and `s '' 'x'` as `empty pattern`,
`f abc` as `missing delimiter`, `f 'abc` as `unterminated string`, `s 'a'` as
`missing argument`, `f 'rat' extra` as `extra argument 'extra'`, and `s 'a' 'b'c` as
`extra argument 'c'`; it accepts `f<TAB>|rat|`, `s "rat" ''`, `s #t# #T#`, `f .cat.`, and
`s 'cat''lion'`. _(UR-06, UR-07)_

**FR-11: `f 'PAT'` — find.**
`f` searches the lines L*c*+1 … L*n*, in order, for the first line that contains PAT as a
contiguous byte sequence (case-sensitive; no wildcards). If one is found, the current line moves
to it and it is typed. Otherwise the command fails with `pattern not found` and the current line
is unchanged. The search does not wrap around to L1 and does not examine the current line.
_AC:_ `dp-line-ed poem.txt < cmd-replace.txt` → `f 'rat'` types L2; at the end, after `t b`,
`f |rat|` types L3, because L2 no longer contains `rat`. _(UR-06)_

**FR-12: `s 'OLD' 'NEW'` — substitute.**
`s` replaces the first (leftmost) occurrence of OLD in the current line by NEW, as byte
sequences, and types the changed line. The current line is not moved. If the current line is
the sentinel, the command fails with `no current line`; if OLD does not occur in the current
line, it fails with `pattern not found`. Either way the buffer is unchanged.
_AC:_ in `cmd-replace.txt`, `s 'rat' 'bat'` types `It saw a bat.`, and `s /cat/ /dog/` then
`s |the rat| |it|` on L4 type `The dog ran after the rat.` and `The dog ran after it.`; a later
`cmd-list.txt` step types the changed file. On an empty buffer, `s 'a' 'b'` fails with
`no current line`. _(UR-07)_

**FR-13: `q` — write and quit.**
`q` MUST create FILE if it does not exist, or truncate it if it does, write every text line
L1 … L*n* followed by one LF (and nothing for the sentinel), as raw bytes, close it, and exit.
An empty buffer produces an empty file. The exit status is 0 if no command failed during the
run and 1 otherwise (FR-14). If FILE cannot be created, opened, written, or closed, the tool
MUST write `dp-line-ed: <FILE>: <reason>`, with `<reason>` from the CONV-16 table
(`Input/output error` for a failure after opening), and exit with status 1; the contents of FILE
are then unspecified. Input after `q` is not read.
_AC:_ the public multi-step tests show the written file through a later `cmd-list.txt` step;
`dp-line-ed nodir/new.txt < cmd-new.txt`, where `nodir` does not exist, loads an empty buffer
and then fails at `q` with `dp-line-ed: nodir/new.txt: No such file or directory`, exit 1.
_(UR-08)_

### 4.3 Errors, end of input, and prompts

**FR-14: Failed commands.**
When a command fails (FR-05, FR-10 … FR-12), the tool MUST write
`dp-line-ed: -:<line>: <message>` to standard error, where `-` names standard input and `<line>`
is the command line's number (CONV-34), MUST leave the buffer and the current line exactly as
they were, MUST NOT type anything for the command, and MUST continue with the next command line.
The failure is remembered: the exit status at the end of the run is 1 even if `q` then writes
FILE successfully.
_AC:_ `dp-line-ed poem.txt < cmd-errors.txt` → six diagnostics on lines 2, 3, 4, 5, 6, and 8
(`unknown command 'x'`, `value out of range '0'`, `missing argument`, `pattern not found` twice,
`extra argument 'now'`), the final `q` writes the file, exit 1; a later `cmd-list.txt` step shows
that the valid `d` on line 7 took effect and nothing else changed. _(UR-10)_

**FR-15: End of input without `q`.**
If the input ends while the tool is waiting for a command — including directly after insert mode
ended at the end of the input — the tool MUST write
`dp-line-ed: -:<line>: unexpected end of input`, where `<line>` is the end-of-input line number
of standard input (CONV-32), MUST NOT create, truncate, or write FILE, and MUST exit with status

1. Every change made in the session is discarded.
   _AC:_ `dp-line-ed poem.txt < cmd-noquit.txt` (delete everything, insert one line, no `q`) →
   stderr `dp-line-ed: -:6: unexpected end of input\n`, exit 1; a later `cmd-list.txt` step types
   the original five lines. _(UR-08)_

**FR-16: Prompt.**
`-p`, `--prompt` enables the single prompt of this tool, the 1 byte `*` (no space, no LF). With
it, the tool MUST write the prompt to standard error, and flush standard error, immediately
before each attempt to read a command line, including one that reaches the end of the input
(CONV-36). The prompt is not written before input lines read in insert mode. A diagnostic about
a command follows the prompt on the same line of standard error. Standard output is the same
with and without the prompt. No prompt is written if FILE cannot be loaded.
_AC:_ `dp-line-ed --prompt poem.txt < cmd-type.txt` → stdout as without `--prompt`, stderr
`*` eleven times (once per command, the last before `q`), exit 0; the hidden test
`dp-line-ed -p poem.txt < cmd-insert-eof.txt` → stderr `***dp-line-ed: -:6: unexpected end of
input\n`. _(UR-12)_

### 4.4 Help, version, and usage

**FR-17: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. FILE is not read and standard input is
not read.
_AC:_ `dp-line-ed --help` matches the user manual exactly; `dp-line-ed extra --help` also prints
it. _(UR-13)_

**FR-18: Version.**
`--version` MUST write `dp-line-ed (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-13)_

**FR-19: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
missing FILE MUST be reported as `dp-line-ed: missing operand`, and a second operand as
`dp-line-ed: extra operand '<second operand>'`, after the whole argument list has been scanned
(CONV-12).
_AC:_ `dp-line-ed < cmd-list.txt` → `dp-line-ed: missing operand`; `dp-line-ed -x --help` →
`dp-line-ed: invalid option -- 'x'`; `dp-line-ed --prompt=yes poem.txt` →
`dp-line-ed: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-14, UR-15)_

**FR-20: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT read or write FILE, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; after `dp-line-ed -p poem.txt extra <
cmd-noquit.txt` (exit 2, no prompt), a `cmd-list.txt` step types the original `poem.txt`.
_(UR-14)_

## 5. Non-functional requirements

| ID     | Category                                         | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Verification                                                          |
| :----- | :----------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| NFR-01 | Portability                                      | Standard output, standard error, and the bytes written to FILE MUST be identical on Linux, macOS, and Windows, and every line terminator the tool generates MUST be LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | CI black-box tests on 3 OSes                                          |
| NFR-02 | Cross-platform focus: byte-exact file round trip | FILE MUST be read and written in binary mode on every platform: a text-mode stream would turn CRLF into LF when reading and LF into CRLF when writing on Windows, and would stop at a `0x1A` byte, so an unedited line would not survive a load/save round trip. CR bytes in FILE are data (FR-02); only FR-02 interprets a trailing Ctrl-Z run. Standard input MUST also be read in binary mode, and only FR-03 removes a CR before LF, so a command script with CRLF line ends behaves identically everywhere. Creating or truncating FILE MUST work whether or not it exists, and the CONV-16 reason MUST be derived portably (for example, a missing parent directory is `ENOENT` on POSIX and `ERROR_PATH_NOT_FOUND` on Windows, and both mean "does not exist" for FR-01 and `No such file or directory` for FR-13). At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST be recognized (FR-15). Standard output and standard error MUST be flushed so that typed lines and the prompt appear before the next read. | CI black-box tests on 3 OSes; integration tests; manual console check |
| NFR-03 | Performance                                      | Loading a FILE of 100 000 lines (about 4 MiB), executing 10 000 commands that each move, insert, delete, find, or type, typing the whole buffer once, and writing it back MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 64 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Insertion and deletion MUST take time proportional to the number of lines inserted or deleted, independent of the buffer size. Start-up and exit for an empty buffer MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Measurement                                                           |
| NFR-04 | Robustness                                       | The tool MUST NOT crash, panic, or print a stack trace for any argument list, FILE contents, or input bytes (CONV-24), including lines of any length, NUL bytes, invalid UTF-8, counts up to and beyond 2⁶³−1, and every command on an empty buffer and at the sentinel. A broken pipe on standard output ends the tool quietly (CONV-25). Every file the tool opens MUST be closed on every path.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Unit + black-box tests                                                |
| NFR-05 | Maintainability: linked buffer                   | The buffer MUST be a singly linked list of nodes headed by a sentinel node that represents `[BOF]` and holds no text line; the current line MUST be a reference to a node, not an index. `i` MUST link new nodes in after the current node, and `d` MUST unlink nodes after it, without copying or moving any other line. Option parsing, file loading and saving, input-line reading, command parsing (including delimited strings and counts), the buffer operations, and typing MUST be separate units; the buffer unit performs no I/O.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Design review                                                         |
| NFR-06 | Testability                                      | The buffer operations MUST be covered by unit tests on an empty buffer, at the sentinel, in the middle, and at the last line, including clamped counts. The command parser MUST be a pure function from a command line to a command or the first error, with a unit test for every message of section 6 that it can produce. The round trip of FR-02 and FR-13 MUST be covered by integration tests that inspect FILE's bytes directly: LF and CRLF files, a missing final LF, a trailing and a non-trailing `0x1A`, NUL bytes, an empty file, and a file holding only `\n`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Code review                                                           |
| NFR-07 | Build                                            | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | CI                                                                    |
| NFR-08 | Security                                         | The tool MUST read only FILE and standard input, MUST write only FILE and only on `q`, MUST NOT delete or rename any file, read environment variables, or run subprocesses. Patterns are matched as plain bytes, never interpreted as regular expressions or shell syntax.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Inspection                                                            |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-line-ed --help' for more
information.`

| Trigger                                      | Exact first line                                                                         |
| :------------------------------------------- | :--------------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `dp-line-ed: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `dp-line-ed: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `dp-line-ed: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| No FILE operand                              | `dp-line-ed: missing operand`                                                            |
| A second operand `X`                         | `dp-line-ed: extra operand 'X'`                                                          |

Failed commands (the session continues; the final exit status is 1). `L` is the command line's
number in standard input:

| Trigger                                                                      | Exact message                             |
| :--------------------------------------------------------------------------- | :---------------------------------------- |
| Command word `W` is not one of `i d t m f s q`                               | `dp-line-ed: -:L: unknown command 'W'`    |
| A required argument is absent                                                | `dp-line-ed: -:L: missing argument`       |
| A word `X` is left over after the last argument                              | `dp-line-ed: -:L: extra argument 'X'`     |
| A count `K` does not match the _integer_ grammar or is outside −2⁶³ … 2⁶³−1  | `dp-line-ed: -:L: invalid integer 'K'`    |
| A count `K` is a valid integer below 1                                       | `dp-line-ed: -:L: value out of range 'K'` |
| A delimited string does not begin with punctuation                           | `dp-line-ed: -:L: missing delimiter`      |
| A delimited string has no closing delimiter                                  | `dp-line-ed: -:L: unterminated string`    |
| The `f` pattern or the `s` OLD string is empty                               | `dp-line-ed: -:L: empty pattern`          |
| `s` while the current line is `[BOF]`                                        | `dp-line-ed: -:L: no current line`        |
| `f` finds no later line containing PAT; `s` finds no OLD in the current line | `dp-line-ed: -:L: pattern not found`      |

Runtime errors that end the run (exit status 1):

| Trigger                                                                           | Exact message                              |
| :-------------------------------------------------------------------------------- | :----------------------------------------- |
| The input ends while a command is expected (end-of-input line number `L`)         | `dp-line-ed: -:L: unexpected end of input` |
| FILE `F` exists but is a directory (at loading or at `q`)                         | `dp-line-ed: F: Is a directory`            |
| FILE `F` cannot be read or written because access is denied                       | `dp-line-ed: F: Permission denied`         |
| A component of FILE `F` is not a directory                                        | `dp-line-ed: F: Not a directory`           |
| At `q`, FILE `F` cannot be created because a directory on its path does not exist | `dp-line-ed: F: No such file or directory` |
| Any other failure to read, create, write, or close FILE `F`                       | `dp-line-ed: F: Input/output error`        |
| Standard input cannot be read                                                     | `dp-line-ed: -: Input/output error`        |
| Standard output cannot be written (other than a broken pipe)                      | `dp-line-ed: write error`                  |

When `--prompt` is given, a diagnostic about a command, and the end-of-input diagnostic, follow
the prompt on the same line of standard error (FR-16).

## 7. Verification

The black-box harness compares only standard output, standard error, and exit status, so tests
observe FILE indirectly: in multi-step tests, a later step runs `dp-line-ed FILE <
cmd-list.txt`, which types every line of the file an earlier step wrote (and writes it back
unchanged). Bytes that typing cannot reveal — a final LF added, a trailing Ctrl-Z dropped — are
covered by the integration tests of NFR-06.

| Method                                                                                            | Applies to                                         |
| :------------------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases; cases 02 … 05, 07, and 08 have several steps)  | FR-01, FR-04 … FR-17, FR-19, FR-20                 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 03, and 05 … 10 have several steps) | FR-01 … FR-20                                      |
| Unit test (written by the implementer)                                                            | FR-04 … FR-12, NFR-06                              |
| Integration test (written by the implementer, inspecting file bytes)                              | FR-02, FR-13, FR-15, NFR-06                        |
| Measurement                                                                                       | NFR-03                                             |
| Inspection / review                                                                               | FR-03 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command(s)                                                                    | Verifies                                               |
| :--- | :---------------------------------------------------------------------------- | :----------------------------------------------------- |
| 01   | `dp-line-ed poem.txt < cmd-type.txt`                                          | FR-01, FR-04, FR-08, FR-09, FR-13                      |
| 02   | `dp-line-ed poem.txt < cmd-insert.txt`; `dp-line-ed poem.txt < cmd-list.txt`  | FR-06, FR-08 (`t b`, `t e`), FR-13                     |
| 03   | `dp-line-ed poem.txt < cmd-delete.txt`; `dp-line-ed poem.txt < cmd-list.txt`  | FR-07 (default count, clamping), FR-13                 |
| 04   | `dp-line-ed poem.txt < cmd-replace.txt`; `dp-line-ed poem.txt < cmd-list.txt` | FR-10, FR-11, FR-12 (delimiters `'`, `"`, `/`, `\|`)   |
| 05   | `dp-line-ed new.txt < cmd-new.txt`; `dp-line-ed new.txt < cmd-list.txt`       | FR-01 (missing file), FR-06, FR-13 (file created)      |
| 06   | `dp-line-ed --prompt poem.txt < cmd-type.txt`                                 | FR-16                                                  |
| 07   | `dp-line-ed poem.txt < cmd-errors.txt`; `dp-line-ed poem.txt < cmd-list.txt`  | FR-05, FR-14 (session continues, file written, exit 1) |
| 08   | `dp-line-ed poem.txt < cmd-noquit.txt`; `dp-line-ed poem.txt < cmd-list.txt`  | FR-15 (file not written)                               |
| 09   | `dp-line-ed --help`                                                           | FR-17                                                  |
| 10   | `dp-line-ed < cmd-list.txt`                                                   | FR-19, FR-20                                           |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                      |
| :--------------- | :--------------------------------------- |
| UR-01            | FR-01, FR-13                             |
| UR-02            | FR-04, FR-08                             |
| UR-03            | FR-04, FR-09                             |
| UR-04            | FR-06                                    |
| UR-05            | FR-07                                    |
| UR-06            | FR-10, FR-11                             |
| UR-07            | FR-10, FR-12                             |
| UR-08            | FR-13, FR-15                             |
| UR-09            | FR-03, CONV-26                           |
| UR-10            | FR-05, FR-14, CONV-33, CONV-34           |
| UR-11            | FR-02, FR-03, NFR-02, CONV-37            |
| UR-12            | FR-16, CONV-36                           |
| UR-13            | FR-17, FR-18                             |
| UR-14            | FR-19, FR-20                             |
| UR-15            | NFR-01, NFR-02, FR-19, CONV-03, CLI-CONV |
| UR-16            | NFR-03, NFR-07                           |
