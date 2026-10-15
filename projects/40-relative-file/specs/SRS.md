<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-relfile](#software-requirements-specification-srs--dp-relfile)
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

# Software Requirements Specification (SRS) — dp-relfile

| Field                     | Value                                                                  |
| :------------------------ | :--------------------------------------------------------------------- |
| Document ID               | SRS-40                                                                 |
| Project                   | `40-relative-file` — Direct-Access Hashed Relative File Storage Engine |
| Product                   | `dp-relfile` (canonical name)                                          |
| Version                   | 1.0.0                                                                  |
| Status                    | Approved (pre-written by the curriculum)                               |
| Parent document           | `URD.md` (URD-40)                                                      |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                           |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                                   |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-relfile`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output and **byte-identical relative files** for every invocation. It is the
authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope

`dp-relfile` keeps records in a _relative file_: a binary file of exactly 100 fixed-size slots
of 35 bytes, in which a record's position is computed from its key by hashing (key mod 97),
collisions are resolved by linear probing with wrap-around, and removed records leave
tombstones that later additions reuse. Records are added, found, and removed either with
subcommands (`add`, `find`, `remove`) or through the textbook's numbered menu dialog read from
standard input; the subcommand `slots` lists the occupied and deleted slots. The file is created
and initialized when it does not exist, and a file of the wrong size or with an invalid record
is rejected.

### 1.3 Definitions

| Term             | Definition                                                                                                                                            |
| :--------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR, TAB      | The bytes `0x0A`, `0x0D`, and `0x09`                                                                                                                  |
| FILE             | The value of `-f`/`--file`, or `relative.dat` if neither is given                                                                                     |
| Relative file    | The file named by FILE                                                                                                                                |
| Slot             | One of the 100 record positions 0 … 99 of the relative file; slot _s_ occupies the 35 bytes at offsets 35·_s_ … 35·_s_ + 34 (its _address_ is 35·_s_) |
| Record           | The 35 bytes of a slot: a status byte, a 4-byte key field, and a 30-byte data field (FR-01, FR-02)                                                    |
| Status           | The first byte of a slot: `0` (FREE, never used), `1` (TAKEN, holds a record), or `2` (DELETED, a tombstone)                                          |
| Key              | A string of exactly 4 ASCII digits `0`–`9` (FR-03); its _value_ _K_ is its decimal value, 0 … 9999                                                    |
| Data             | A string of 0 … 30 bytes in the range `0x20` … `0x7E` that does not end in a space (FR-04)                                                            |
| Home slot        | _K_ mod 97 for a key of value _K_; always 0 … 96                                                                                                      |
| Probe sequence   | The slots _h_, _h_+1, … taken modulo 100, starting at the home slot _h_ (FR-05)                                                                       |
| Tombstone        | A slot whose status is DELETED                                                                                                                        |
| Command mode     | An invocation with a COMMAND operand (FR-10)                                                                                                          |
| Dialog mode      | An invocation without operands, which reads the menu dialog from standard input (FR-12)                                                               |
| Operation        | One add, find, or remove (FR-06 … FR-08), in either mode                                                                                              |
| Failed operation | An add of a key that exists (duplicate) or into a full file, or a find or remove of a key that does not exist                                         |
| Decimal          | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                |

### 1.4 References

- URD-40: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §8.8 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-relfile` is a standalone executable. Its interfaces are the command line, the relative
file (read, and created or written in place), standard input (dialog mode only), standard
output, standard error, and the exit status. It belongs to the curriculum's
applications-programming track (Projects 11–52) and adapts §8.8 of Johnsonbaugh & Kalin,
_Applications Programming in ANSI C_.

### 2.2 Product functions

1. Create and initialize the relative file (100 free slots, 3500 bytes) if it does not exist.
2. Check that an existing relative file is well formed before using it.
3. Add, find, and remove records by key, addressing slots by hashing and linear probing.
4. List the slots that are not free, for inspection.
5. Run the textbook's menu dialog from standard input, with optional prompts.
6. Report failed operations, malformed dialog input, corrupted files, and file errors.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior and the file format.
- The relative file MUST be accessed _directly_: each operation positions the file at a slot's
  address and reads or writes that record (FR-11). Loading the file into a hash table in memory
  and rewriting the whole file is not a conforming design.

### 2.4 Assumptions

- No other process accesses the relative file while the tool runs. Locking is out of scope.
- Relative paths are relative to the current working directory.
- The relative file is not modified between the start-up check (FR-02) and the end of the run
  except by the tool itself.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §8.8 opens the relative file `relative.dat`, creating it with 100 free
records if it does not exist, and then loops over a numbered menu — 1 add, 2 find, 3 remove,
0 exit — reading a key (and, to add, the data) for each choice. `dp-relfile` keeps:

- the file format exactly: 100 slots of 35 bytes; the status byte `0`, `1`, or `2`; a 4-byte
  key; 30 bytes of data; a fresh file of 3500 bytes in which every slot is `0` followed by 34
  spaces; the default name `relative.dat`;
- the addressing exactly: address = (key mod 97) × 35, linear probing one record at a time with
  wrap-around from the last slot to the first, tombstones that searches pass over and additions
  reuse, and the detection of duplicate keys and a full file;
- the menu dialog: the four choices with their numbers, the menu text and the prompt
  `Please pick a number:` as the section's description shows them, and a key and data read for
  each choice; choice 0 ends the run.

It changes the following, for the reasons given:

- **Subcommands as well as the menu** (FR-10). Each operation can be run as a single command
  (`dp-relfile add 1234 'Ada Lovelace'`), which makes the tool scriptable and lets black-box
  tests observe persistence by running the tool again. Without a command, the menu dialog runs
  as in the textbook (FR-12).
- **The `slots` command** (FR-09) lists every slot that is not free, with its status, key, and
  data, so collisions, wrap-around, and tombstones can be seen; every success message names the
  slot used. The textbook had no way to inspect the file's layout.
- **Prompts are optional and go to standard error** (FR-13), so standard output holds only the
  results. The prompts for the key and the data, which the section's description does not show,
  are written in the menu's voice.
- **Duplicate detection is exact** (FR-05, FR-06): an add searches the whole probe sequence for
  the key — past tombstones — before it reuses the first tombstone, so a key can never be stored
  twice. Inserting into the first tombstone without searching further could duplicate a key
  stored beyond it.
- **Probing is bounded** (FR-05): a search examines at most 100 slots, so a file with no free
  slot (all slots taken or deleted) cannot cause an endless loop.
- **Input is validated** (FR-03, FR-04, FR-14): a key is exactly 4 digits, and data is at most
  30 printable ASCII characters, with trailing spaces removed because the padding makes them
  indistinguishable. The textbook did not check its input.
- **A corrupted file is rejected** (FR-02) instead of being read as if it were valid: a wrong
  size or an invalid record stops the tool before any operation or prompt.
- **Failures are diagnosed** on standard error with fixed messages, and reflected in the exit
  status (FR-06 … FR-08, FR-15); the data file can be chosen with `-f`/`--file` (FR-01).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics CONV-13 …
CONV-16, and exit statuses CONV-18. Of the conventions for Projects 11–52:

| Convention | Use in this SRS                                                                                                                                                                                                                                                                   |
| :--------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-32    | Not applicable as tokens: the dialog input is read as _lines_ (FR-12). Line numbers are as defined in CONV-32.                                                                                                                                                                    |
| CONV-33    | Not applicable: keys use their own grammar of exactly 4 digits (FR-03), and the choice is one of four strings.                                                                                                                                                                    |
| CONV-34    | Used for malformed dialog input, with the standard message `unexpected end of input` and the further messages `invalid choice '<text>'`, `invalid key '<text>'`, `invalid character in data`, and `data too long (maximum 30 characters)` (FR-14), with the default consequences. |
| CONV-35    | Not applicable: no real number is written.                                                                                                                                                                                                                                        |
| CONV-36    | `-p`, `--prompt` with three prompts in dialog mode (FR-13).                                                                                                                                                                                                                       |
| CONV-37    | Applies to the dialog input, which is _text data_ (FR-12). It does not apply to the relative file, which is binary.                                                                                                                                                               |
| CONV-38    | Not applicable: nothing is random.                                                                                                                                                                                                                                                |

**Extensions of CONV-13** (usage errors, exit status 2, followed by the CONV-14 line):
`unknown command '<word>'`, `invalid key '<key>'`, `invalid character in data`, and
`data too long (maximum 30 characters)` (FR-18). **Extensions of CONV-16:** the reasons
`not a relative file (size <n>, expected 3500)` and `slot <s>: invalid record` (FR-02).
Standard input is read only in dialog mode (CONV-26). The first operand is a command word, not
a file (CONV-10 does not apply to it).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-relfile [-f FILE | --file=FILE] [-p | --prompt]
dp-relfile [-f FILE | --file=FILE] add KEY DATA
dp-relfile [-f FILE | --file=FILE] find KEY
dp-relfile [-f FILE | --file=FILE] remove KEY
dp-relfile [-f FILE | --file=FILE] slots
dp-relfile --help
dp-relfile --version
```

### 3.2 Options

| Short | Long        | Argument        | Default        | Description                                                                                      |
| :---- | :---------- | :-------------- | :------------- | :----------------------------------------------------------------------------------------------- |
| `-f`  | `--file`    | FILE (required) | `relative.dat` | Use the relative file FILE (FR-01)                                                               |
| `-p`  | `--prompt`  | none            | off            | In dialog mode, write the menu and prompts of FR-13 to standard error; no effect in command mode |
| —     | `--help`    | none            | —              | Print the help text and exit 0                                                                   |
| —     | `--version` | none            | —              | Print the version line and exit 0                                                                |

Option syntax (`-fFILE`, `--file FILE`, bundling, `--`, repetition, and scan order) follows
CONV-07 … CONV-12. Options may appear anywhere, before or after the command and its operands
(CONV-10); an operand that begins with `-` (for example data `-5 degrees`) must follow `--`. If
`-f` is repeated, the last occurrence wins (CONV-11). An empty FILE is an invalid option value
(FR-18).

### 3.3 Operands

None (dialog mode), or a COMMAND word followed by exactly the operands it takes: `add KEY DATA`,
`find KEY`, `remove KEY`, `slots` (FR-10).

### 3.4 Standard input

Read only in dialog mode (FR-12), as raw bytes, one line at a time; no newline translation of
any kind is performed on any platform.

### 3.5 Standard output

The result line of each successful operation (FR-06 … FR-08) and the lines of `slots` (FR-09),
in order. On a usage error, or when `--help` / `--version` is handled, the output is as
specified by FR-16 … FR-19 instead.

### 3.6 Standard error

Prompts (FR-13, only with `--prompt` in dialog mode) and diagnostics (section 6).

### 3.7 Files

The relative file FILE is created if it does not exist (FR-01). It is then opened for reading
and writing (`add`, `remove`, dialog mode) or for reading only (`find`, `slots`), and written in
place, one record at a time (FR-11); its length is always 3500 bytes. No other file is created,
and no file is deleted, renamed, or truncated.

### 3.8 Exit status

| Status | Condition                                                                                                                                                                 |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0      | Every operation succeeded (including a dialog with no operations, and `slots`), or `--help` / `--version` was handled                                                     |
| 1      | At least one operation failed (FR-06 … FR-08), the dialog input was malformed (FR-14), the relative file is not valid (FR-02), or a file or output error occurred (FR-15) |
| 2      | Usage error (FR-18)                                                                                                                                                       |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n`, `\r`, `\t` denote LF, CR, and TAB. Unless `-f` is shown, the
relative file is `relative.dat` and does not exist when the test starts. Public fixtures in
`tests/fixtures/`: `people.dat`, a valid relative file whose non-free slots are 55 (taken, key
`4711`, data `Edsger Dijkstra`), 70 (taken, `1234`, `Ada Lovelace`), 71 (deleted, `1331`,
`Grace Hopper`), 72 (taken, `0070`, `Alan Turing`), and 73 (taken, `0167`, `Barbara Liskov`);
`short.dat`, 3499 bytes; `badstatus.dat`, 3500 bytes in which the status byte of slot 5 is `X`;
`session.txt`, the dialog input
`1\n1234\nAda Lovelace\n1\n0097\nGrace Hopper\n1\n0000\nAlan Turing\n2\n0000\n3\n1234\n0\n`.

**FR-01: The relative file and its initialization.**
The relative file is FILE: the value of `-f`/`--file`, or `relative.dat` in the current
directory. After a successful scan of the arguments, and before any operation, any prompt, or
any read of standard input, the tool MUST check whether FILE exists. If it does not, the tool
MUST create it and write exactly 3500 bytes: 100 FREE records, each the byte `0` followed by 34
spaces (`0x20`). This happens in every mode and for every command, including `find` and `slots`,
and also when the dialog input is empty. An existing file is never re-initialized, whatever its
contents (an existing empty file is invalid, FR-02).
_AC:_ `dp-relfile slots` → no output, exit 0, and a later `dp-relfile slots` again exits 0 (the
created file passed FR-02, so it has exactly 3500 bytes). _(UR-01)_

**FR-02: File validation.**
Before the first operation (and before the first prompt in dialog mode), the tool MUST check the
whole relative file, created or existing, and reject it if

1. its length is not 3500 bytes: `dp-relfile: <FILE>: not a relative file (size <n>, expected 3500)`,
   where `<n>` is the decimal of its length; otherwise
2. a slot, examined in ascending order, is invalid: `dp-relfile: <FILE>: slot <s>: invalid record`
   for the first such slot _s_. A slot is valid when its status byte is `0` and its other 34
   bytes are spaces, or its status byte is `1` or `2`, its key field is 4 ASCII digits, and its
   data field is 30 bytes in the range `0x20` … `0x7E`.

`<FILE>` is FILE exactly as given. On rejection the tool performs no operation, writes no prompt,
reads no standard input, does not modify the file, and exits with status 1. Validation does not
check that keys are unique or reachable from their home slot.
_AC:_ `dp-relfile -f short.dat slots` →
`dp-relfile: short.dat: not a relative file (size 3499, expected 3500)\n`, exit 1;
`dp-relfile -f badstatus.dat find 0005` → `dp-relfile: badstatus.dat: slot 5: invalid record\n`,
exit 1; an existing empty file → `… not a relative file (size 0, expected 3500)`. _(UR-09)_

**FR-03: Keys.**
A key MUST consist of exactly 4 bytes, each an ASCII digit `0`–`9`. Leading zeros are
significant to the key field (`0042` is stored as the bytes `0042`) and part of the key's
spelling; the key's value _K_ is its decimal value (`0042` → 42). In command mode an invalid key
is a usage error (FR-18); in dialog mode it is a data error (FR-14). Keys are compared as their
4 bytes.
_AC:_ `dp-relfile add 123 'too short'` → `dp-relfile: invalid key '123'` + the CONV-14 line,
exit 2; `12a4` and `12345` are invalid; `0000` and `9999` are valid. _(UR-02)_

**FR-04: Data.**
The data of a record is the given string with all trailing spaces (`0x20`) removed. After that
removal it MUST consist only of bytes `0x20` … `0x7E` (otherwise: `invalid character in data`)
and be at most 30 bytes long (otherwise: `data too long (maximum 30 characters)`); the
character check is made first. Empty data is valid. Leading and inner spaces are kept. The data
is stored in the data field padded on the right with spaces to 30 bytes; when it is read back,
trailing spaces are removed, which yields exactly the data that was stored.
_AC:_ `add 0001 'abcdefghijklmnopqrstuvwxyz0123'` (30 bytes) succeeds; 31 bytes →
`dp-relfile: data too long (maximum 30 characters)`, exit 2; `'Zoë'` →
`dp-relfile: invalid character in data`, exit 2; `'trailing spaces dropped        '` stores
`trailing spaces dropped`; `'  leading'` keeps its two leading spaces; `''` is stored as 30
spaces. _(UR-02)_

**FR-05: Hashing and probing.**
For a key of value _K_, let _h_ = _K_ mod 97 (the home slot; byte address 35·_h_). To _locate_
the key, the tool MUST examine the slots *s*ᵢ = (_h_ + _i_) mod 100 for _i_ = 0, 1, …, 99 in
order, stopping as follows:

- status FREE: stop; the key is **not present**. The _insertion slot_ is the first DELETED slot
  examined before this one, if any, otherwise this FREE slot;
- status TAKEN and key field equal to the key: stop; the key is **present** in *s*ᵢ;
- status DELETED: if no DELETED slot has been examined yet, remember this one; continue. A
  tombstone never matches, even if its key field equals the key;
- status TAKEN with another key: continue.

If all 100 slots are examined without stopping, the key is not present, and the insertion slot
is the first DELETED slot examined, or there is none. Because the probe sequence covers every
slot, there is no insertion slot exactly when all 100 slots are TAKEN. Each examination reads
the record at its address (FR-11). Slots 97, 98, and 99 are never a home slot and are reached
only by probing.
_AC:_ `add 0000 first`, `add 0097 second`, `add 9700 third` (all with home slot 0) → slots 0, 1,
and 2; `add 0096`, `0193`, `0290`, `0387`, `0484` (home slot 96) → slots 96, 97, 98, 99, and 0.
_(UR-03, UR-04)_

**FR-06: Add.**
To add a key and data (both valid), the tool MUST locate the key (FR-05). If it is present, the
add fails with `dp-relfile: cannot add <key>: duplicate key`. Otherwise, if there is no
insertion slot, it fails with `dp-relfile: cannot add <key>: file is full`. Otherwise the tool
MUST write the 35-byte record — the byte `1`, the 4 key bytes, and the data padded to 30 bytes
(FR-04) — at the insertion slot's address, and write `Added <key> in slot <s>` + LF to standard
output, where `<s>` is the decimal of the slot. A failed add changes nothing.
_AC:_ `dp-relfile add 1234 'Ada Lovelace'` → `Added 1234 in slot 70\n` (1234 mod 97 = 70);
a second `dp-relfile add 1234 y` → stderr `dp-relfile: cannot add 1234: duplicate key\n`,
exit 1. After `add 0000 a`, `add 0097 b`, `add 0194 c`, `remove 0097`, the add of `0291` (home
slot 0) reuses the tombstone: `Added 0291 in slot 1`. In a file whose 100 slots are all taken,
an add fails with `file is full`. _(UR-03, UR-05, UR-06)_

**FR-07: Find.**
To find a key, the tool MUST locate it (FR-05). If it is present in slot _s_, the tool MUST write
`Found <key> in slot <s>: <data>` + LF, where `<data>` is the slot's data field with trailing
spaces removed; when that data is empty, the line is `Found <key> in slot <s>:` + LF (no space
after the colon). If the key is not present, the find fails with
`dp-relfile: cannot find <key>: no such record`. A find never modifies the file.
_AC:_ `dp-relfile -f people.dat find 0167` → `Found 0167 in slot 73: Barbara Liskov\n` (the
search starts at slot 70, passes the tombstone in slot 71, and continues); `find 4321` on a new
file → `dp-relfile: cannot find 4321: no such record\n`, exit 1; in a file with no free slot, a
find of a missing key examines 100 slots and fails. _(UR-03, UR-04, UR-05)_

**FR-08: Remove.**
To remove a key, the tool MUST locate it (FR-05). If it is present in slot _s_, the tool MUST
write the single byte `2` at the slot's address (the key and data fields are left as they were,
so the slot becomes a tombstone) and write `Removed <key> from slot <s>` + LF. If the key is not
present, the remove fails with `dp-relfile: cannot remove <key>: no such record`.
_AC:_ after `add 0000 a`, `add 0097 b`, `add 0194 c`, `dp-relfile remove 0097` →
`Removed 0097 from slot 1\n`; `find 0194` then → `Found 0194 in slot 2: c\n`; and `slots` lists
`1 deleted 0097 b`. Removing a key twice fails the second time. _(UR-04, UR-05)_

**FR-09: Slots.**
The command `slots` MUST write one line for each slot whose status is TAKEN or DELETED, in
ascending slot order: the decimal of the slot, a space, `taken` or `deleted`, a space, the 4 key
bytes, and — unless the data field consists only of spaces — a space and the data field with
trailing spaces removed; then LF. FREE slots are not listed; a file with no such slot produces
no output. `slots` never modifies the file and always succeeds on a valid file (exit 0).
_AC:_ `dp-relfile -f people.dat slots` →
`55 taken 4711 Edsger Dijkstra\n70 taken 1234 Ada Lovelace\n71 deleted 1331 Grace Hopper\n72 taken 0070 Alan Turing\n73 taken 0167 Barbara Liskov\n`.
_(UR-07)_

**FR-10: Command mode.**
If there is at least one operand, the first is the COMMAND, which MUST be `add`, `find`,
`remove`, or `slots`; it is followed by exactly two operands (KEY, DATA), one (KEY), one (KEY),
or none, respectively. The operands are validated (FR-03, FR-04) before the relative file is
opened; any problem is a usage error (FR-18). The tool then opens (and if necessary creates)
and validates the file (FR-01, FR-02), performs the one operation, and exits with status 0 if it
succeeded and 1 if it failed. `--prompt` has no effect in command mode.
_AC:_ `dp-relfile add 1234 x` → exit 0; `dp-relfile find 4321` → exit 1;
`dp-relfile --prompt slots` behaves like `dp-relfile slots`. _(UR-05, UR-08)_

**FR-11: Direct access.**
Each examination in FR-05 MUST read the one record at the slot's address; an add MUST write
exactly the 35 bytes of the one record at the insertion slot's address; a remove MUST write
exactly the one status byte. No other byte of the file is ever written after initialization,
and the file's length never changes. Each write MUST be passed to the operating system (flushed
from any buffer of the tool) before the next operation begins and before the tool exits, so the
effect of every completed operation persists even if a later operation fails. FR-02 reads the
whole file once, at start-up; that is the only read that is not of a single record.
_AC:_ in a multi-step test, each step sees the records written by earlier steps: after
`dp-relfile < session.txt`, `dp-relfile slots` → `0 taken 0097 Grace Hopper\n1 taken 0000 Alan Turing\n70 deleted 1234 Ada Lovelace\n`.
_(UR-06, UR-07)_

**FR-12: Dialog mode.**
With no operands, the tool MUST run the menu dialog, reading standard input one line at a time.
Standard input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to its
very end is ignored. Each LF ends a line, and bytes after the last LF, if any, form a final line;
a line is used without its LF and with **one** CR removed if it then ends in CR. The line
number of a line is 1 plus the number of LF bytes before it (CONV-32). The dialog repeats:

1. Read a line: the _choice_. If the input has ended, the dialog ends. Remove leading and
   trailing spaces and TABs. If the result is `0`, the dialog ends; no more input is read. If it
   is not `1`, `2`, or `3`, it is an invalid choice (FR-14).
2. Read a line: the _key_. Remove leading and trailing spaces and TABs; it MUST be a valid key
   (FR-03).
3. For choice `1` only, read a line: the _data_, used as it is (FR-04 removes trailing spaces;
   TABs and other bytes are not removed and are invalid).
4. Perform the operation — `1` add (FR-06), `2` find (FR-07), `3` remove (FR-08) — and flush
   standard output. A failed operation is reported, and the dialog continues.

When the dialog ends, the exit status is 1 if any operation failed and 0 otherwise.
_AC:_ `dp-relfile < session.txt` → stdout
`Added 1234 in slot 70\nAdded 0097 in slot 0\nAdded 0000 in slot 1\nFound 0000 in slot 1: Alan Turing\nRemoved 1234 from slot 70\n`,
exit 0. With CRLF lines, a choice `1`, and a key `\t0042the record `0042`is added. After
a line`0`, the rest of the input is not read. _(UR-08, UR-10)_

**FR-13: Prompts.**
In dialog mode, `-p`, `--prompt` enables three prompts. With prompts enabled, the tool MUST
write each prompt to standard error, and flush standard error, immediately before the read it
belongs to, even if that read reaches the end of the input (CONV-36):

| Prompt | Exact bytes                                                                                                                                                                                                                                                                                                                                | Written before        |
| :----- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------- |
| MENU   | the 128 bytes `\t\t\t1   -- add a record\n\t\t\t2   -- find a record\n\t\t\t3   -- remove a record\n\t\t\t0   -- exit the program\n\n\t\t\tPlease pick a number:enu line is three TABs, the digit, three spaces, `--`, a space, and the text; then an empty line; then three TABs, `Please pick a number:`, and three spaces; no final LF) | each read of a choice |
| KEY    | the 27 bytes `\t\t\tEnter key (4 digits):TABs, the text, three spaces)                                                                                                                                                                                                                                                                     | each read of a key    |
| DATA   | the 39 bytes `\t\t\tEnter data (up to 30 characters):                                                                                                                                                                                                                                                                                      | each read of data     |

A diagnostic that follows a prompt continues the same line of standard error. Prompts never
change standard output. No prompt is written in command mode, or if FILE cannot be opened or is
invalid (FR-02, FR-15).
_AC:_ `dp-relfile --prompt < session.txt` → stdout as without `--prompt`; stderr is MENU KEY
DATA, three times, then MENU KEY, twice, then MENU, concatenated; exit 0. _(UR-10)_

**FR-14: Malformed dialog input.**
In dialog mode the tool MUST stop at the first malformed line, write one of the following
(CONV-34, source `-`, `<L>` the line number of the offending line), and exit with status 1:

| Condition                                           | Message                                                                                                                            |
| :-------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------- |
| The choice is not `0`, `1`, `2`, or `3`             | `dp-relfile: -:<L>: invalid choice '<text>'`, with `<text>` the choice after removing spaces and TABs (it may be empty)            |
| The key is invalid (FR-03)                          | `dp-relfile: -:<L>: invalid key '<text>'`, with `<text>` the key after removing spaces and TABs                                    |
| The data has a byte outside `0x20` … `0x7E` (FR-04) | `dp-relfile: -:<L>: invalid character in data`                                                                                     |
| The data is longer than 30 bytes (FR-04)            | `dp-relfile: -:<L>: data too long (maximum 30 characters)`                                                                         |
| The input ends where a key or data is required      | `dp-relfile: -:<E>: unexpected end of input`, with `<E>` the end-of-input line number (1 plus the number of LF bytes in the input) |

The key is checked as soon as it is read, before the data prompt and data. Operations performed
before the malformed line remain in the file and their output remains written.
_AC:_ `dp-relfile -p` with standard input `1\n` → stderr MENU KEY then
`dp-relfile: -:2: unexpected end of input\n` on the same line, exit 1. With an invalid choice
`x` on line 11, the records added on earlier lines persist (a later `slots` lists them).
_(UR-08, UR-09)_

**FR-15: File errors.**
If FILE cannot be created (because a directory in it does not exist, access is denied, or any
other reason), cannot be opened, or is a directory, the tool MUST write
`dp-relfile: <FILE>: <reason>` with `<reason>` from the CONV-16 table and exit with status 1
before any operation, prompt, or read of standard input. `add`, `remove`, and dialog mode open
the file for reading and writing, so a read-only file fails for them with `Permission denied`;
`find` and `slots` open it for reading only. If a read or write of the relative file fails
during an operation, the tool MUST write `dp-relfile: <FILE>: Input/output error` and exit with
status 1 at once. If standard output cannot be written, the tool MUST write
`dp-relfile: write error` and exit with status 1, except that a broken pipe ends the tool quietly
(CONV-25).
_AC:_ `dp-relfile -f subdir slots` (a directory) → `dp-relfile: subdir: Is a directory\n`,
exit 1; `dp-relfile -f nodir/r.dat slots` → `dp-relfile: nodir/r.dat: No such file or directory\n`,
exit 1. _(UR-09)_

**FR-16: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No file is opened or created and no
input is read.
_AC:_ `dp-relfile --help` matches the user manual exactly; `dp-relfile frob --help` also prints
it. _(UR-11)_

**FR-17: Version.**
`--version` MUST write `dp-relfile (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match; `dp-relfile -f '' --version` also prints it and exits 0. _(UR-11)_

**FR-18: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--prompt=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08). After the
whole argument list has been scanned (CONV-12), the following are checked in this order, and
the first problem found is reported as a usage error:

1. an empty FILE: `dp-relfile: invalid argument '' for '<option>'`, with `<option>` `-f` or
   `--file` as written;
2. a COMMAND that is not one of the four: `dp-relfile: unknown command '<word>'`;
3. too few operands for the command: `dp-relfile: missing operand`; too many:
   `dp-relfile: extra operand '<first surplus operand>'`;
4. an invalid KEY: `dp-relfile: invalid key '<KEY>'`;
5. invalid DATA (`add` only): `dp-relfile: invalid character in data` or
   `dp-relfile: data too long (maximum 30 characters)` (FR-04).

_AC:_ `dp-relfile frob` → `dp-relfile: unknown command 'frob'`; `dp-relfile find` →
`dp-relfile: missing operand`; `dp-relfile slots extra` → `dp-relfile: extra operand 'extra'`;
`dp-relfile -f '' slots` → `dp-relfile: invalid argument '' for '-f'`; `dp-relfile -x --version`
→ `dp-relfile: invalid option -- 'x'`; each followed by the CONV-14 line, exit 2. _(UR-12, UR-13)_

**FR-19: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT create, open, or modify any file, MUST NOT read
standard input or write a prompt, and MUST NOT write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                   | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Verification                              |
| :----- | :----------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------- |
| NFR-01 | Portability                                | Output, diagnostics, and the bytes of the relative file MUST be identical on Linux, macOS, and Windows, and every line written to standard output or standard error MUST end in LF only (CONV-03). A relative file written on one platform MUST be usable unchanged on the others.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | CI black-box tests on 3 OSes              |
| NFR-02 | Cross-platform focus: binary random access | The relative file MUST be opened in binary mode on every platform and positioned by absolute byte offsets (35 × slot). Text mode is a conformance failure: on Windows it translates line endings and makes file positions unreliable for seeking. Creation MUST write exactly 3500 bytes; updates MUST write in place without truncating or extending the file (no "write whole file" or append mode). The CONV-16 reason for FILE MUST be derived portably: opening a directory fails with `EISDIR` on Linux and macOS but with "access denied" on Windows, and both MUST be reported as `Is a directory`. Standard input MUST be read in binary mode so that only FR-12 interprets CR and `0x1A`; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the dialog normally. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance                                | Each command MUST complete in under 100 ms for a natively compiled build (300 ms for an interpreted runtime) on CI hardware, including start-up and validation. A dialog of 10 000 operations MUST complete in under 2 s native (20 s interpreted). An operation reads at most 100 records. Peak memory MUST stay under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31) and MUST NOT grow with the number of operations.                                                                                                                                                                                                                                                                                                                                                                                                                   | Measurement                               |
| NFR-04 | Robustness                                 | The tool MUST NOT crash, panic, or print a stack trace for any argument list, dialog input, or file contents (CONV-24), including lines of any length, non-UTF-8 bytes, and arbitrary bytes in the relative file (which FR-02 rejects). Probing MUST terminate after at most 100 examinations whatever the file contains. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Unit + black-box tests                    |
| NFR-05 | Maintainability                            | Option and command parsing, key and data validation, the record layout (encoding and decoding one 35-byte record), slot access (reading and writing one record at a slot's address), the hash and probe logic, the operations, the dialog, and output formatting MUST be separate units. The constants 100, 35, 4, 30, and 97 and the three status bytes MUST each be defined once. Command mode and dialog mode MUST call the same operation functions.                                                                                                                                                                                                                                                                                                                                                                                                                      | Design review                             |
| NFR-06 | Testability                                | The probe logic (FR-05) MUST be unit-tested against an in-memory slot store, covering: a direct hit, a collision chain, wrap-around from slot 99 to slot 0, a tombstone before the key, a tombstone before a FREE slot (insertion into the tombstone), a key stored beyond a tombstone (no duplicate), a file with no FREE slot, and a full file. Record encoding, validation (FR-02), and the dialog's line splitting MUST be pure functions with unit tests.                                                                                                                                                                                                                                                                                                                                                                                                                | Code review                               |
| NFR-07 | Build                                      | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | CI                                        |
| NFR-08 | Security                                   | The tool MUST create or modify only FILE, MUST NOT delete, rename, or truncate any file, read environment variables, or run subprocesses. It MUST NOT write any byte of the relative file that FR-01, FR-06, or FR-08 does not specify.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Inspection                                |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-relfile --help' for more
information.`

| Trigger                                                                  | Exact first line                                                                         |
| :----------------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| Unknown short option `x`                                                 | `dp-relfile: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T`                             | `dp-relfile: unrecognized option 'T'`                                                    |
| `-f` without an argument                                                 | `dp-relfile: option requires an argument -- 'f'`                                         |
| `--file` without an argument                                             | `dp-relfile: option '--file' requires an argument`                                       |
| `--prompt=…` / `--help=…` / `--version=…`                                | `dp-relfile: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| Empty FILE                                                               | `dp-relfile: invalid argument '' for '-f'` (or `'--file'`, as written)                   |
| COMMAND `W` is not `add`, `find`, `remove`, or `slots`                   | `dp-relfile: unknown command 'W'`                                                        |
| Too few operands for the command                                         | `dp-relfile: missing operand`                                                            |
| Surplus operand `X` (the first)                                          | `dp-relfile: extra operand 'X'`                                                          |
| KEY `K` is not exactly 4 digits                                          | `dp-relfile: invalid key 'K'`                                                            |
| DATA has a byte outside `0x20` … `0x7E` (after removing trailing spaces) | `dp-relfile: invalid character in data`                                                  |
| DATA is longer than 30 bytes (after removing trailing spaces)            | `dp-relfile: data too long (maximum 30 characters)`                                      |

Runtime errors (exit status 1). Failed operations do not stop a dialog; every other runtime
error stops the tool:

| Trigger                                                                   | Exact message                                                |
| :------------------------------------------------------------------------ | :----------------------------------------------------------- |
| Add of key `K` that is present                                            | `dp-relfile: cannot add K: duplicate key`                    |
| Add of key `K` when all 100 slots are taken                               | `dp-relfile: cannot add K: file is full`                     |
| Find of key `K` that is not present                                       | `dp-relfile: cannot find K: no such record`                  |
| Remove of key `K` that is not present                                     | `dp-relfile: cannot remove K: no such record`                |
| FILE `F` does not have 3500 bytes (it has `N`)                            | `dp-relfile: F: not a relative file (size N, expected 3500)` |
| Slot `S` of FILE `F` is invalid (the first)                               | `dp-relfile: F: slot S: invalid record`                      |
| A directory in FILE `F` does not exist                                    | `dp-relfile: F: No such file or directory`                   |
| FILE `F` cannot be created or opened because access is denied             | `dp-relfile: F: Permission denied`                           |
| FILE `F` is a directory                                                   | `dp-relfile: F: Is a directory`                              |
| A component of FILE `F` is not a directory                                | `dp-relfile: F: Not a directory`                             |
| Any other failure to create, open, read, or write FILE `F`                | `dp-relfile: F: Input/output error`                          |
| Dialog choice on line `L` is invalid                                      | `dp-relfile: -:L: invalid choice 'C'`                        |
| Dialog key on line `L` is invalid                                         | `dp-relfile: -:L: invalid key 'K'`                           |
| Dialog data on line `L` has an invalid byte                               | `dp-relfile: -:L: invalid character in data`                 |
| Dialog data on line `L` is too long                                       | `dp-relfile: -:L: data too long (maximum 30 characters)`     |
| Dialog input ends where a key or data is required (end-of-input line `E`) | `dp-relfile: -:E: unexpected end of input`                   |
| Standard input cannot be read                                             | `dp-relfile: -: Input/output error`                          |
| Standard output cannot be written (other than a broken pipe)              | `dp-relfile: write error`                                    |

## 7. Verification

The black-box harness compares only standard output, standard error, and exit status, so tests
observe the relative file indirectly: multi-step tests run `dp-relfile` again in the same
directory and inspect the file with `find` and `slots`. A file that was created with the wrong
size or contents would be rejected by the next step (FR-02).

| Method                                                                                           | Applies to                                          |
| :----------------------------------------------------------------------------------------------- | :-------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases; cases 01 … 04 and 06 … 08 have several steps) | FR-01 … FR-14, FR-16, FR-18, FR-19                  |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 10 have several steps)            | FR-01 … FR-19                                       |
| Unit test (written by the implementer)                                                           | FR-02 … FR-05, FR-12, NFR-06                        |
| Integration test (written by the implementer, inspecting file bytes)                             | FR-01, FR-06, FR-08, FR-11                          |
| Measurement                                                                                      | NFR-03                                              |
| Inspection / review                                                                              | section 2.3 (direct access), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command(s)                                                                                                           | Verifies                                                             |
| :--- | :------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| 01   | `dp-relfile add 1234 'Ada Lovelace'`; `find 1234`; `slots`                                                           | FR-01 (creation), FR-05 … FR-07, FR-09, FR-11                        |
| 02   | `add 0000 first`; `add 0097 second`; `add 9700 third`; `find 9700`; `slots`                                          | FR-05 (collisions), FR-06, FR-07                                     |
| 03   | `add 0000 a`; `add 0097 b`; `add 0194 c`; `remove 0097`; `find 0194`; `slots`; `add 0291 d`; `slots`                 | FR-05 (tombstones), FR-08 (tombstone reuse), FR-09                   |
| 04   | `dp-relfile < session.txt`; `dp-relfile slots`                                                                       | FR-11 (persistence), FR-12                                           |
| 05   | `dp-relfile --prompt < session.txt`                                                                                  | FR-13                                                                |
| 06   | `add 1234 x`; `add 1234 y`; `find 4321`; `remove 4321`                                                               | FR-06 … FR-08 (failed operations), FR-10                             |
| 07   | `-f people.dat slots`; `--file=people.dat find 0167`; `-f people.dat add 1428 'Donald Knuth'`; `-f people.dat slots` | FR-01 (`-f`), FR-05 (probing past a tombstone), FR-06 (reuse), FR-09 |
| 08   | `-f short.dat slots`; `-f badstatus.dat find 0005`                                                                   | FR-02                                                                |
| 09   | `dp-relfile --help`                                                                                                  | FR-16                                                                |
| 10   | `dp-relfile add 123 'too short'`                                                                                     | FR-03, FR-18, FR-19                                                  |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                   |
| :--------------- | :------------------------------------ |
| UR-01            | FR-01                                 |
| UR-02            | FR-03, FR-04                          |
| UR-03            | FR-05, FR-06, FR-07                   |
| UR-04            | FR-05, FR-07, FR-08                   |
| UR-05            | FR-06, FR-07, FR-08, FR-10            |
| UR-06            | FR-06, FR-11                          |
| UR-07            | FR-09, FR-11                          |
| UR-08            | FR-10, FR-12, FR-14, CONV-37          |
| UR-09            | FR-02, FR-14, FR-15, CONV-16, CONV-34 |
| UR-10            | FR-12, FR-13, CONV-36                 |
| UR-11            | FR-16, FR-17                          |
| UR-12            | FR-18, FR-19                          |
| UR-13            | NFR-01, NFR-02, CLI-CONV              |
| UR-14            | NFR-03, NFR-07                        |
