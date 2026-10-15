<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-queue1, dp-queue2, dp-stack1, dp-stack2](#software-requirements-specification-srs--dp-queue1-dp-queue2-dp-stack1-dp-stack2)
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
    - [4.1 Storage](#41-storage)
    - [4.2 Input and dialog](#42-input-and-dialog)
    - [4.3 Operations and output](#43-operations-and-output)
    - [4.4 Command line](#44-command-line)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-queue1, dp-queue2, dp-stack1, dp-stack2

| Field                     | Value                                                                |
| :------------------------ | :------------------------------------------------------------------- |
| Document ID               | SRS-45                                                               |
| Project                   | `45-queue-stack` — Comparative Queue & Stack ADT Implementations     |
| Products                  | `dp-queue1`, `dp-queue2`, `dp-stack1`, `dp-stack2` (canonical names) |
| Version                   | 1.0.0                                                                |
| Status                    | Approved (pre-written by the curriculum)                             |
| Parent document           | `URD.md` (URD-45)                                                    |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                         |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                                 |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-queue1`, `dp-queue2`, `dp-stack1`,
and `dp-stack2`, and the abstract-data-type structure they must share. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

The four tools run the same command dialog, read as tokens from standard input or one file:
`1` inserts a record, `2` removes one, `3` displays the contents, `0` quits. The _queue tools_
(`dp-queue1`, `dp-queue2`) hold customer records in first-in, first-out order; the _stack
tools_ (`dp-stack1`, `dp-stack2`) hold tray records in last-in, first-out order. The _array
tools_ (`dp-queue1`, `dp-stack1`) store at most 100 records in a fixed array; the _linked
tools_ (`dp-queue2`, `dp-stack2`) store records in a linked list with no fixed capacity. Each
result is written as soon as its command has been read. The tools can write prompts to
standard error, and report malformed commands with line numbers and unreadable files with
fixed messages. Requirements that apply to some tools name them; all others apply to all four.

### 1.3 Definitions

| Term               | Definition                                                                                                                                                       |
| :----------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR             | The bytes `0x0A` and `0x0D`                                                                                                                                      |
| Input              | The bytes of the FILE operand, or of standard input, with a trailing run of `0x1A` bytes ignored (CONV-37)                                                       |
| Source             | The FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) (CONV-34)                                                |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and 1 plus the number of LF bytes before its first byte |
| Kind               | _Queue_ (`dp-queue1`, `dp-queue2`) or _stack_ (`dp-stack1`, `dp-stack2`)                                                                                         |
| Partner            | The other tool of the same kind: `dp-queue1` and `dp-queue2` are partners, and so are `dp-stack1` and `dp-stack2`                                                |
| Command            | A token that selects an operation: 0, 1, 2, or 3 (FR-04)                                                                                                         |
| Record             | A customer (queue tools, FR-05) or a tray (stack tools, FR-07)                                                                                                   |
| Contents           | The sequence of records held, in removal order: front to rear for a queue, top to bottom for a stack                                                             |
| Capacity           | 100, the maximum number of records held by an array tool (FR-01)                                                                                                 |
| Amount             | A balance in exact hundredths, written and read as defined in FR-06                                                                                              |
| Decimal            | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                           |
| Record text        | The one-line rendering of a record (FR-11)                                                                                                                       |

### 1.4 References

- URD-45: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the four normative help texts)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §10.4 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

The four tools are standalone executables built from one project. Their interfaces are the
command line, standard input or the file named by the operand, standard output, standard error,
and the exit status. They belong to the curriculum's applications-programming track (Projects
11–52) and adapt the four programs of §10.4 of Johnsonbaugh & Kalin, _Applications Programming
in ANSI C_, which implements the queue and the stack as abstract data types, each with an array
and with a linked list.

### 2.2 Product functions

1. Read commands as tokens until the command 0 or the end of the input.
2. Insert a record at the rear of the queue or the top of the stack; report `QUEUE FULL` or
   `STACK FULL` when an array tool already holds 100 records.
3. Remove the record at the front of the queue or the top of the stack and write it; report
   `QUEUE EMPTY` or `STACK EMPTY` when there is none.
4. Display the contents without changing them.
5. Optionally write a menu prompt and a record prompt to standard error.
6. Report malformed commands and records, and unreadable input files; display help and version
   information; detect and report usage errors.

### 2.3 Constraints

- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through NFR-05, the data structures and
  decomposition of the code.
- Balances MUST be held and formatted in exact integer arithmetic (FR-06). Binary floating
  point MUST NOT be used to read, store, or write them.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-04.
- The input may contain any bytes; names and colors are copied, not interpreted.

### 2.5 Relationship to the textbook program (informative)

**Kept:** the two abstract data types and their records — a FIFO queue of customers with a last
name, a first name, an account number, and a balance, and a LIFO stack of cafeteria trays with
a color and an id number; two implementations of each, an array of 100 elements (`SIZE`) and a
linked list; the circular array for the queue, whose indices advance modulo 100; the linked
queue with front and rear references and the linked stack whose top node refers to the node
below; the messages `QUEUE FULL`, `QUEUE EMPTY`, `STACK FULL`, and `STACK EMPTY`; and an
interactive driver through which records are inserted, removed, and inspected.

**Changed, and why:**

- **The driver is fully specified.** The section describes its drivers only as menus that
  insert, remove, and inspect. SRS-45 defines one numbered command set for all four tools
  (FR-04), the order of a record's fields (FR-05, FR-07), and the exact output of every
  operation (FR-08 … FR-11), so that the four tools can be tested byte for byte and the array
  and linked tools of a kind can be compared directly (FR-12).
- **Prompts are optional and go to standard error** (CONV-36), in the same voice as the
  section's menus (FR-13), so standard output holds only results and can be redirected or
  compared.
- **Full and empty are results, not errors.** The four messages are written to standard output
  as the outcome of the command, and the session continues (FR-08 … FR-10). They do not change
  the exit status: the tool did what it was asked, and the ADT refused, as specified.
- **A record is read before the full check.** The record that follows `1` is always read and
  validated, and only then inserted or refused (FR-08). The input therefore means the same
  thing to both tools of a kind, whatever their capacity — the precondition for FR-12.
- **The stack capacity is exactly 100.** The section's README gives the stack-full test as
  `top >= SIZE - 1` with `SIZE` = 100 and an empty stack's `top` at −1; checked before a push,
  that admits 100 trays and refuses the 101st. SRS-45 states the capacity directly (FR-01), for
  both array tools.
- **Exact money.** A binary floating-point balance cannot hold most cent values exactly, and
  printing it to two places can round a value such as 0.125 or 2.675 in a direction a teller
  would not expect. Balances are therefore restricted to at most two decimal places, held as an
  integer number of cents, and written with exactly two (FR-06); CONV-35's `FIX` is not needed.
- **Invalid input is diagnosed.** A command or number that cannot be read stops the session
  with a located diagnostic (FR-14), instead of being skipped or misread; results already
  written are kept.
- **The end of the input is defined.** In place of a command it ends the session like `0`;
  inside a record it is an error (FR-04, FR-14).
- **Input sources.** Besides standard input, one FILE operand may be named; CRLF line endings
  and a trailing Ctrl-Z are accepted (FR-02, FR-03).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18: the full and
empty messages are results of successful commands, not failed operations in the sense of
CONV-18, so they do not make the exit status 1. Of the conventions for Projects 11–52:

| Convention | Use in this SRS                                                                                                                                                                                                                                                    |
| :--------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-32    | The input is read as tokens; line numbers follow CONV-32 (FR-03).                                                                                                                                                                                                  |
| CONV-33    | Commands, account numbers, and tray ids use the _integer_ grammar, further range-restricted (FR-04, FR-05, FR-07). Balances use the project grammar _amount_ of FR-06, not _real_.                                                                                 |
| CONV-34    | All data errors use its format, the standard messages `invalid integer`, `value out of range`, and `unexpected end of input`, and one additional message, `invalid amount` (FR-14). The default consequences apply: output already written is kept, exit status 1. |
| CONV-35    | Not applicable: balances are exact decimals with their own format (FR-06), and no other real number is written.                                                                                                                                                    |
| CONV-36    | Each tool has `-p`, `--prompt` with two prompts (FR-13).                                                                                                                                                                                                           |
| CONV-37    | The input is _text data_ (FR-03).                                                                                                                                                                                                                                  |
| CONV-38    | Not applicable: nothing is random.                                                                                                                                                                                                                                 |

CONV-04 does not constrain the output, because no input is copied through; names and colors are
written byte for byte as FR-05 and FR-07 define them.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-queue1 [-p | --prompt] [FILE]
dp-queue2 [-p | --prompt] [FILE]
dp-stack1 [-p | --prompt] [FILE]
dp-stack2 [-p | --prompt] [FILE]
<tool> --help | --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                  |
| :---- | :---------- | :------- | :------ | :------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-13 to standard error |
| —     | `--help`    | none     | —       | Print the help text and exit 0               |
| —     | `--version` | none     | —       | Print the version line and exit 0            |

All four tools have the same options. Option syntax (bundling, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. Giving `-p` more than once has the same effect as giving it
once (CONV-11).

### 3.3 Operands

At most one FILE operand. With no operand, or with the operand `-`, the tool reads standard
input. Every token after `--` is an operand. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input

Read when no operand is given or the operand is `-` (CONV-26), as raw bytes with no newline
translation on any platform, incrementally (FR-03), and not beyond the command 0.

### 3.5 Standard output

The results of the commands (FR-08 … FR-11), in command order, and nothing else. Nothing on a
usage error or a file error that occurs before the first command.

### 3.6 Standard error

Prompts (FR-13, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when a run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                                                            |
| :----- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The session ended with the command 0 or at the end of the input — whether or not any `QUEUE FULL`, `QUEUE EMPTY`, `STACK FULL`, or `STACK EMPTY` was written — or `--help` / `--version` was handled |
| 1      | The input could not be opened or read (FR-15), it contained a data error (FR-14), storage could not be obtained (NFR-02), or standard output could not be written                                    |
| 2      | Usage error (FR-18)                                                                                                                                                                                  |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF and the named files are the fixtures in
`tests/fixtures/`:

- `customers.txt` inserts `Smith Ann 1001 250.75`, `Jones Bob 1002 -12.5`, and
  `Lee Kim 1003 0`, then gives `3`, `2`, `2`, `3`, inserts `Diaz Rosa 1004 1000`, and gives
  `3` and `0`;
- `trays.txt` pushes `red 1`, `green 2`, and `blue 3`, then gives `3`, `2`, `3`, `2 2 2`
  (three pops on one line), `3`, and `0`;
- `full-queue.txt` inserts the 101 customers `Cust001 Pat 2001 1.25` … `Cust101 Pat 2101
101.25`, then gives `3` and `0`;
- `full-stack.txt` pushes the 101 trays `white 1` … `white 101`, then gives `2`, `2`, and `0`;
- `empty.txt` is `2\n3\n2\n0\n`;
- `bad-command.txt` is `1 red 7\n3\npop\n3\n0\n`.

### 4.1 Storage

**FR-01: Implementations and capacity.**
Each tool MUST hold its records in the structure named here, with the observable capacity
given:

| Tool        | Kind  | Storage                                                          | Capacity |
| :---------- | :---- | :--------------------------------------------------------------- | :------- |
| `dp-queue1` | queue | circular array of exactly 100 record places (NFR-05 (c))         | 100      |
| `dp-queue2` | queue | linked list with front and rear references (NFR-05 (d))          | none     |
| `dp-stack1` | stack | array of exactly 100 record places with a top index (NFR-05 (e)) | 100      |
| `dp-stack2` | stack | linked list whose top node links to the node below (NFR-05 (f))  | none     |

An array tool holds at most 100 records at a time; it can hold 100 records any number of times
during a session, whatever the history of insertions and removals. A linked tool has no limit
other than available memory (NFR-02).
_AC:_ `dp-queue1 full-queue.txt` holds 100 customers after 101 insertions; `dp-queue2
full-queue.txt` holds 101. _(UR-05, UR-06)_

### 4.2 Input and dialog

**FR-02: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-18).
_AC:_ `dp-queue1 < customers.txt` and `dp-queue2 customers.txt` write the same results. _(UR-12)_

**FR-03: Tokens.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored; a `0x1A` byte followed by any other byte is ordinary data and
belongs to a token. The input is read as tokens (CONV-32), so commands and fields may be
separated by any mixture of spaces, TABs, VT, FF, CR, and LF, and CRLF input reads exactly like
LF input. The input MUST be read incrementally: a token is complete, and MUST be processed, as
soon as the whitespace byte that follows it has been read, or the input has ended, without
waiting for further input; the only permitted lookahead is a run of `0x1A` bytes, which is held
back until the next byte shows whether it reaches the end of the input.
_AC:_ `trays.txt` gives three pop commands on one line; the hidden fixture `crlf-stack.txt`,
with CRLF line endings and two final `0x1A` bytes, is read like its LF version. _(UR-08, UR-12)_

**FR-04: Session.**
The tool MUST run the following loop:

1. Write prompt P1 (FR-13). Read the next token. If the input has ended, end the session.
2. The token is the command. It MUST be an _integer_ (CONV-33) with a value in 0 … 3.
3. Command 0: end the session. The rest of the input is not read or validated.
4. Command 1 (insert, or push): write prompt P2, read and validate the record (FR-05 or FR-07),
   then perform FR-08.
5. Command 2 (remove, or pop): perform FR-09.
6. Command 3 (display): perform FR-10.
7. Flush standard output and continue with step 1.

When the session ends, the tool exits with status 0. An end of the input in place of a command
is therefore the same as the command 0. The result of each command MUST be written, and
standard output flushed, before the next token is read.
_AC:_ `dp-queue2 - < empty.txt` → `QUEUE EMPTY\n` three times, exit 0; the hidden fixture
`quit.txt` holds a line that is not a valid command after the command 0; it is never read,
and the exit status is 0. _(UR-08, UR-09)_

**FR-05: Customer records (queue tools).**
After the command 1, a queue tool MUST read four tokens, validating each before reading the
next:

1. the _last name_: any token, kept as its exact bytes;
2. the _first name_: any token, kept as its exact bytes;
3. the _account number_: an _integer_ (CONV-33) in 0 … 9223372036854775807;
4. the _balance_: an _amount_ (FR-06).

Names cannot contain whitespace bytes (they are tokens), but MAY contain any other bytes,
including bytes that are not valid UTF-8 and `0x1A` bytes that do not end the input. The account
number is kept as its value: `007` and `+7` are the account 7.
_AC:_ `customers.txt` gives the customer `Jones, Bob; account 1002; balance -12.50`; the hidden
fixture `bad-account.txt` rejects the account `-5` as out of range. _(UR-01, UR-08, UR-10)_

**FR-06: Amounts.**
A balance token MUST match the grammar _amount_ in full:

```text
[+-]?[0-9]+(\.[0-9]{1,2})?        (ASCII only)
```

that is, an optional sign, one or more digits, and optionally a decimal point followed by one or
two digits. Its value is the exact decimal number written; leading zeros are allowed. The
magnitude MUST be at most 999999999999999.99. The value MUST be held exactly, as an integer
number of hundredths (cents), and never converted to binary floating point. A token that does not
match is `invalid amount`; a matching token with a larger magnitude is `value out of range`
(FR-14).
An amount _v_ in cents is written as: `-` if _v_ < 0; then the decimal of ⌊|_v_| / 100⌋; then
`.`; then the two digits of |_v_| mod 100 (with a leading zero below 10). Zero is written
`0.00`, never `-0.00`.
_AC:_ `250.75` → `250.75`; `-12.5` → `-12.50`; `0` → `0.00`; `1000` → `1000.00`; and in the
hidden fixture `amounts.txt`: `-0` → `0.00`, `+5` → `5.00`, `007.05` → `7.05`, `-0.01` →
`-0.01`, `999999999999999.99` and `-999999999999999.99` are written unchanged; `12.345` (hidden
fixture `bad-amount.txt`), `.5`, and `1,000` are `invalid amount`; `1000000000000000` (hidden
fixture `big-amount.txt`) is `value out of range`. _(UR-07)_

**FR-07: Tray records (stack tools).**
After the command 1, a stack tool MUST read two tokens, validating each before reading the next:

1. the _color_: any token, kept as its exact bytes (any non-whitespace bytes, as for names in
   FR-05);
2. the _id_: an _integer_ (CONV-33) in 0 … 9223372036854775807, kept as its value.

_AC:_ `trays.txt` gives the trays `color red, id 1`, `color green, id 2`, and `color blue,
id 3`; the hidden fixture `bad-id.txt` rejects the id `1.5` as an invalid integer.
_(UR-02, UR-08, UR-10)_

### 4.3 Operations and output

**FR-08: Insert and push.**
When the record of a command 1 has been read and validated, the tool MUST add it to the
contents: a queue tool at the rear, a stack tool at the top. If an array tool already holds 100
records, it MUST instead write `QUEUE FULL` (queue) or `STACK FULL` (stack) and LF to standard
output, and discard the record; the contents are unchanged and the session continues. A
successful insertion writes nothing.
_AC:_ `dp-queue1 full-queue.txt` writes `QUEUE FULL\n` once, for `Cust101`; `dp-stack1
full-stack.txt` writes `STACK FULL\n` once, for tray 101. _(UR-01, UR-02, UR-05)_

**FR-09: Remove and pop.**
For a command 2, a queue tool MUST remove the record at the front, and a stack tool the record
at the top, and write `Removed:queue) or `Popped:`(tck), the record text (FR-11), and
LF. If the contents are empty, the tool MUST instead write `QUEUE EMPTY`(queue) or`STACK EMPTY`(stack) and LF; the session continues.
_AC:_`dp-queue1 < customers.txt`writes`Removed: Smith, Ann; account 1001; balance 250.75\n`and then`Removed: Jones, Bob; account 1002; balance -12.50\n`; `dp-stack1 full-stack.txt`ends with`Popped: color white, id 100\nPopped: color white, id 99\n`. _(UR-01, UR-02, UR-04)_

**FR-10: Display.**
For a command 3, the tool MUST write one line per record held, in removal order — front to rear
for a queue, top to bottom for a stack — without changing the contents. The _k_-th line
(_k_ = 1, 2, …) is the decimal of _k_, `:a colon and one space), the record text (FR-11),
and LF. If the contents are empty, the tool MUST instead write `QUEUE EMPTY`(queue) or`STACK EMPTY`(stack) and LF. No header, blank line, or count is written.
_AC:_`dp-stack1 trays.txt`writes`1: color blue, id 3\n2: color green, id 2\n3: color red,
id 1\n`for its first display, and`STACK EMPTY\n` for its last. _(UR-03, UR-04)_

**FR-11: Record text.**
The record text of a customer MUST be the last name, `,the first name, `; account`h
decimal of the account number,`; balanceand the balance written by FR-06. The record text
of a tray MUST be `colorthe color, `, id`n the decimal of the id. Names and colors are
written as their exact bytes. There are no other spaces and no trailing spaces.
_AC:_`Smith, Ann; account 1001; balance 250.75`; `color blue, id 3`; the hidden fixture
`amounts.txt`writes the account`007`as`account 7` and the account 9223372036854775807
unchanged. _(UR-01, UR-02, UR-07)_

**FR-12: Equivalence of the array and linked tools.**
For every argument list and every input, a linked tool MUST write the same standard output, the
same standard error with its partner's name replaced by its own, and the same exit status as
its array partner, apart from the help text (FR-16) and version line (FR-17), **provided that
the array tool never writes `QUEUE FULL` or `STACK FULL`**. If it does, the outputs are
identical up to that line; at that point the linked tool inserts the record and writes nothing,
and the contents of the two tools differ from then on. Every requirement in this SRS other than
FR-01, FR-08's capacity rule, FR-16, and FR-17 applies to both tools of a kind in exactly the
same way.
_AC:_ public tests 01 and 02 (`customers.txt`) write identical output with `dp-queue1` and
`dp-queue2`; `dp-queue1 full-queue.txt` and `dp-queue2 full-queue.txt` differ only in that the
first writes `QUEUE FULL\n` and displays customers 1 … 100, while the second displays 1 … 101;
the hidden fixture `wrap.txt` — 100 insertions, 60 removals, 60 more insertions so that the
circular array wraps around, one insertion too many, a display, and a removal — gives the same
display order (`A061` … `A100`, `B001` … `B060`) in both queue tools, with `C001` displayed
last only by `dp-queue2`. _(UR-05, UR-06)_

**FR-13: Prompts.**
With `-p` or `--prompt`, the tool MUST write these prompts to standard error, with no line
feed, and flush standard error before the read that follows (CONV-36):

| Prompt | Tools | Exact bytes                                                                        | Written                                                                                                                  |
| :----- | :---- | :--------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------- |
| P1     | queue | `Enter 1 (insert), 2 (remove), 3 (display), 0 (quit):53 bytes, ending in a space)  | Before every read of a command, including the first and one that reaches the end of the input                            |
| P1     | stack | `Enter 1 (push), 2 (pop), 3 (display), 0 (quit):48 bytes, ending in a space)       | As for the queue tools                                                                                                   |
| P2     | queue | `Enter last name, first name, account number, balance:54 bytes, ending in a space) | Once per command 1, after the command has been validated and before the first field is read; not before the other fields |
| P2     | stack | `Enter color, id:17 bytes, ending in a space)                                      | As for the queue tools                                                                                                   |

Without the flag, no prompt is written. Standard output is the same with and without it, and
the prompts of the two tools of a kind are identical.
_AC:_ `dp-stack2 --prompt < trays.txt` → stdout as without `--prompt`; stderr is P1 P2 P1 P2
P1 P2, then P1 eight more times (for `3`, `2`, `3`, the three pops, `3`, and `0`),
concatenated. _(UR-11)_

**FR-14: Data errors.**
At the first invalid or missing token, the tool MUST write one CONV-34 diagnostic,
`<tool>: <source>:<line>: <message>`, read no further input, perform no operation for the
current command, and exit with status 1. Results already written are kept.

| Condition                                                                | `<line>`                               | `<message>`                    |
| :----------------------------------------------------------------------- | :------------------------------------- | :----------------------------- |
| A command, account number, or tray id is not a valid _integer_           | the token's line                       | `invalid integer '<token>'`    |
| A command is outside 0 … 3; an account number or tray id is below 0      | the token's line                       | `value out of range '<token>'` |
| A balance does not match _amount_ (FR-06)                                | the token's line                       | `invalid amount '<token>'`     |
| A balance's magnitude exceeds 999999999999999.99                         | the token's line                       | `value out of range '<token>'` |
| The input ends after a command 1 and before the last field of its record | the end-of-input line number (CONV-32) | `unexpected end of input`      |

`<token>` is the token's exact bytes (CONV-15). A prompt already written stays written, so with
`--prompt` the diagnostic follows the last prompt on the same line of standard error; P2 is not
written when the command is invalid.
_AC:_ `dp-stack1 bad-command.txt` → stdout `1: color red, id 7\n`, stderr
`dp-stack1: bad-command.txt:3: invalid integer 'pop'\n`, exit 1; the hidden fixture
`cut-record.txt` (`1 Doe Jane\n`) with `dp-queue1 -p` → stderr P1 P2 followed by
`dp-queue1: cut-record.txt:2: unexpected end of input\n`, exit 1. _(UR-10)_

**FR-15: File errors.**
If the FILE operand does not exist, cannot be opened, or is a directory, the tool MUST write
`<tool>: <FILE>: <reason>` with the CONV-16 reason, write nothing to standard output and no
prompt, and exit with status 1. If a read error occurs later, the results already written are
kept and the same diagnostic is written. A failure of standard input is reported with `<FILE>` =
`-`.
_AC:_ `dp-queue1 subdir` → `dp-queue1: subdir: Is a directory`, exit 1; `dp-stack2 missing.txt`
→ `dp-stack2: missing.txt: No such file or directory`, exit 1. _(UR-13)_

### 4.4 Command line

**FR-16: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read and no prompt
is written.
_AC:_ each tool's `--help` matches the user manual exactly; `dp-stack2 a b --help` prints the
help. _(UR-14)_

**FR-17: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ `dp-queue1 --version` → `dp-queue1 (dialectic-playground) 1.0.0\n`. _(UR-14)_

**FR-18: Usage errors.**
Unknown options, and an argument given to an option that takes none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08). A second operand MUST be reported
as `<tool>: extra operand '<second operand>'`; operands are checked only after the whole
argument list has been scanned (CONV-12).
_AC:_ `dp-queue1 a b` → `dp-queue1: extra operand 'b'`; `dp-queue2 -x --help` →
`dp-queue2: invalid option -- 'x'`; `dp-stack1 --prompt=1` →
`dp-stack1: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-14)_

**FR-19: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-queue1 -p - extra < customers.txt` writes no
prompt. _(UR-14)_

## 5. Non-functional requirements

| ID     | Category                                                                            | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Verification                                                    |
| :----- | :---------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                                                         | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line the tools generate MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: platform-independent capacity, storage, and interactive input | The capacity of the array tools MUST be the constant 100 on every platform — never derived from the platform's memory, page size, word size, or record size — and their storage MUST be obtained once, when the tool starts, so that no array-tool operation can fail for lack of memory. The linked tools MUST obtain storage for one node per insertion and release (or make reclaimable) a node when it is removed; if storage cannot be obtained, the tool MUST write `<tool>: out of memory` to standard error and exit with status 1, never crash (CONV-24). Account numbers and ids MUST be 64-bit on every platform, independent of the size of the platform's native integer types. The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-03 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the session normally. Prompts MUST reach a terminal before the tool waits for input, and each result before the next read: standard error and standard output MUST be flushed explicitly where the platform buffers them.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance                                                                         | Each tool MUST start, process the public fixtures, and exit in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware. Insert, remove, push, and pop MUST each take constant time, independent of the number of records held; a display takes time proportional to the number of records. A session of 1 000 000 insert and remove commands (about 15 MiB of input, never holding more than 100 records) MUST complete in under 3 s native (30 s interpreted). Peak memory MUST stay under 16 MiB for the array tools in every session, and for the linked tools whenever at most 1000 records are held (above the runtime's baseline for managed or interpreted runtimes, CONV-31); memory MUST NOT grow with the length of the input otherwise.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Measurement                                                     |
| NFR-04 | Robustness                                                                          | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24). Tokens of any length MUST be handled; an integer outside the 64-bit range is `invalid integer` and an over-long balance `invalid amount` or `value out of range`, never overflowed. A broken pipe on standard output ends a tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Unit + black-box tests                                          |
| NFR-05 | Maintainability: abstract data types                                                | (a) The queue MUST be defined by one interface — insert at the rear, remove from the front, test for empty, and a traversal that visits the records from front to rear without removing them — and the stack by one interface — push, pop, test for empty, and a traversal from top to bottom; each array implementation also reports whether it is full. (b) The command driver — token reading, validation, prompting, the session loop, and output formatting — MUST be one unit of source shared by the two tools of a kind (and SHOULD be shared by all four), which uses the records only through the interface; the two tools of a kind MUST differ only in the implementation bound to the interface. (c) `dp-queue1`: one array of exactly 100 record places, allocated once, with a front index and a count (or a rear index); an insertion goes to place (front + count) mod 100 and a removal advances the front to (front + 1) mod 100; records are never shifted, and the array is never reallocated. (d) `dp-queue2`: singly linked nodes, each holding one record and a link to the next node toward the rear, with a reference to the front node and one to the rear node; insertion links a new node after the rear node, removal unlinks the front node, and both take constant time. (e) `dp-stack1`: one array of exactly 100 record places, allocated once, with a top index (−1, or a count of 0, when empty). (f) `dp-stack2`: singly linked nodes, each holding one record and a link to the node below it, with a reference to the top node. (g) In (d) and (f), no built-in or library array, vector, list, deque, or other collection may hold the records or the nodes. (h) A balance MUST be held as an integer number of cents, and the parser and formatter of FR-06 MUST be pure functions. Command-line handling MUST be shared by the four tools (Principles 3, 13, 18). | Design review                                                   |
| NFR-06 | Testability                                                                         | Each ADT implementation MUST be unit-tested through its interface: FIFO or LIFO order; empty after as many removals as insertions; for the array implementations, full at exactly 100 records, still usable after a refused insertion, and full again after any mix of removals and insertions that brings it back to 100; for `dp-queue1`, order preserved across the wrap-around (insert 100, remove 60, insert 60). A comparison test MUST apply the same sequence of at least 10 000 pseudo-random operations to the array and the linked implementation of each kind, with at most 100 records held, and require identical results. The amount parser and formatter MUST be unit-tested with every value in the AC of FR-06, and the tokenizer with the input split into reads at every byte position.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | Code review                                                     |
| NFR-07 | Build                                                                               | Every BASE-MAKEFILE target MUST work for all four tools: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | CI                                                              |
| NFR-08 | Security                                                                            | The tools MUST read only the FILE operand or standard input, and MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2) are each followed by `Try '<tool> --help' for more information.`,
where `<tool>` is the canonical name of the tool that was run.

| Trigger                                      | Exact first line                                                                     |
| :------------------------------------------- | :----------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `<tool>: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `<tool>: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `<tool>: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `<tool>: extra operand 'X'`                                                          |

File errors (exit status 1):

| Trigger                                | Exact message                             |
| :------------------------------------- | :---------------------------------------- |
| FILE does not exist                    | `<tool>: FILE: No such file or directory` |
| Access to FILE is denied               | `<tool>: FILE: Permission denied`         |
| FILE is a directory                    | `<tool>: FILE: Is a directory`            |
| A component of FILE is not a directory | `<tool>: FILE: Not a directory`           |
| Any other open or read failure         | `<tool>: FILE: Input/output error`        |
| Any of the above for standard input    | the same message with `FILE` = `-`        |

Data errors (exit status 1; results already written are kept):

| Trigger                                                  | Exact message                                     |
| :------------------------------------------------------- | :------------------------------------------------ |
| Command, account number, or tray id not an _integer_     | `<tool>: SOURCE:LINE: invalid integer 'TOKEN'`    |
| Command outside 0 … 3; account number or tray id below 0 | `<tool>: SOURCE:LINE: value out of range 'TOKEN'` |
| Balance not an _amount_ (queue tools)                    | `<tool>: SOURCE:LINE: invalid amount 'TOKEN'`     |
| Balance magnitude above 999999999999999.99 (queue tools) | `<tool>: SOURCE:LINE: value out of range 'TOKEN'` |
| Input ends inside a record                               | `<tool>: SOURCE:LINE: unexpected end of input`    |

Resource and output errors (exit status 1):

| Trigger                                                               | Exact message           |
| :-------------------------------------------------------------------- | :---------------------- |
| A linked tool cannot obtain storage for a node (NFR-02)               | `<tool>: out of memory` |
| Standard output cannot be written (other than a broken pipe, CONV-25) | `<tool>: write error`   |

`QUEUE FULL`, `QUEUE EMPTY`, `STACK FULL`, and `STACK EMPTY` are not diagnostics: they are
results, written to standard output (FR-08 … FR-10). When `--prompt` is given, a data
diagnostic follows the last prompt on the same line of standard error (FR-14).

## 7. Verification

| Method                                                                            | Applies to                                         |
| :-------------------------------------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                | FR-01 … FR-14, FR-16                               |
| Black-box test (hidden, `tests/private/`, 10 cases; every case has several steps) | FR-01 … FR-19                                      |
| Unit test (written by the implementer)                                            | FR-03, FR-05 … FR-12, NFR-06                       |
| Measurement                                                                       | NFR-03                                             |
| Inspection / review / demonstration                                               | FR-03 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                          | Verifies                              |
| :--- | :------------------------------- | :------------------------------------ |
| 01   | `dp-queue1 < customers.txt`      | FR-04 … FR-06, FR-08 … FR-11          |
| 02   | `dp-queue2 customers.txt`        | FR-02, FR-12 (same output as test 01) |
| 03   | `dp-stack1 trays.txt`            | FR-03, FR-07, FR-09 … FR-11           |
| 04   | `dp-stack2 --prompt < trays.txt` | FR-12, FR-13                          |
| 05   | `dp-queue1 full-queue.txt`       | FR-01, FR-08 (`QUEUE FULL`), FR-10    |
| 06   | `dp-queue2 full-queue.txt`       | FR-01, FR-12 (no capacity)            |
| 07   | `dp-stack1 full-stack.txt`       | FR-01, FR-08 (`STACK FULL`), FR-09    |
| 08   | `dp-queue2 - < empty.txt`        | FR-04, FR-09, FR-10 (`QUEUE EMPTY`)   |
| 09   | `dp-queue1 --help`               | FR-16                                 |
| 10   | `dp-stack1 bad-command.txt`      | FR-14                                 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                    |
| :--------------- | :------------------------------------- |
| UR-01            | FR-05, FR-08, FR-09, FR-11             |
| UR-02            | FR-07, FR-08, FR-09, FR-11             |
| UR-03            | FR-10                                  |
| UR-04            | FR-09, FR-10                           |
| UR-05            | FR-01, FR-08, FR-12                    |
| UR-06            | FR-01, FR-12, NFR-05, NFR-06           |
| UR-07            | FR-06, FR-11                           |
| UR-08            | FR-03, FR-04, FR-05, FR-07             |
| UR-09            | FR-04                                  |
| UR-10            | FR-05, FR-07, FR-14, CONV-33, CONV-34  |
| UR-11            | FR-13, CONV-36                         |
| UR-12            | FR-02, FR-03, NFR-02, CONV-26, CONV-37 |
| UR-13            | FR-15, CONV-16                         |
| UR-14            | FR-16 … FR-19                          |
| UR-15            | NFR-01, NFR-02, CONV-03                |
| UR-16            | FR-18, NFR-03, NFR-07, CLI-CONV        |
