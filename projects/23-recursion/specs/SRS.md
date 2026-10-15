<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-fact, dp-tower, dp-walk-r, dp-walk-nr](#software-requirements-specification-srs--dp-fact-dp-tower-dp-walk-r-dp-walk-nr)
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
    - [4.1 Input, prompts, and data errors (all tools)](#41-input-prompts-and-data-errors-all-tools)
    - [4.2 dp-fact](#42-dp-fact)
    - [4.3 dp-tower](#43-dp-tower)
    - [4.4 dp-walk-r and dp-walk-nr](#44-dp-walk-r-and-dp-walk-nr)
    - [4.5 All tools](#45-all-tools)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-fact, dp-tower, dp-walk-r, dp-walk-nr

| Field                     | Value                                                              |
| :------------------------ | :----------------------------------------------------------------- |
| Document ID               | SRS-23                                                             |
| Project                   | `23-recursion` — Recursion vs. Iteration Comparative Suite         |
| Products                  | `dp-fact`, `dp-tower`, `dp-walk-r`, `dp-walk-nr` (canonical names) |
| Version                   | 1.0.0                                                              |
| Status                    | Approved (pre-written by the curriculum)                           |
| Parent document           | `URD.md` (URD-23)                                                  |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                       |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                               |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-fact`, `dp-tower`, `dp-walk-r`,
and `dp-walk-nr`, and the recursive and iterative designs each must have. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope

All four tools read whole numbers as integer tokens from standard input or from one file until
the end of the input, and answer each number as soon as it has been read. `dp-fact` prints the
factorial of each number. `dp-tower` prints the moves that solve the Tower of Hanoi for each
number of disks. `dp-walk-r` and `dp-walk-nr` print the number of ways a robot can walk each
distance in steps of 1 and 2 meters; they produce identical answers, but `dp-walk-r` computes
them by plain tree recursion and `dp-walk-nr` by iteration. Each tool can write a prompt to
standard error before each number is read, and reports invalid numbers with their line numbers
and unreadable files with fixed messages. Requirements that apply to some tools name them; all
others apply to all four.

### 1.3 Definitions

| Term               | Definition                                                                                                                                                        |
| :----------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF, CR             | The bytes `0x0A` and `0x0D`                                                                                                                                       |
| Tool               | One of `dp-fact`, `dp-tower`, `dp-walk-r`, `dp-walk-nr`; `<tool>` in a message is its canonical name                                                              |
| Walk tools         | `dp-walk-r` and `dp-walk-nr`                                                                                                                                      |
| Input              | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source             | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Number             | The value of a token that is a valid _integer_ (CONV-33), −2⁶³ … 2⁶³−1                                                                                            |
| Complete token     | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                |
| Answer             | Everything a tool writes to standard output for one number (FR-06, FR-08, FR-10)                                                                                  |
| Decimal            | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                            |
| W(_d_)             | The robot-walk count of FR-09                                                                                                                                     |

### 1.4 References

- URD-23: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the four normative help texts)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §4.8 (informative; see §2.5)
- SRS-13 (`projects/13-taxes/specs/SRS.md`): the same streaming input model for a single tool

## 2. Overall description

### 2.1 Product perspective

The four tools are standalone executables built from one project. Their interfaces are the
command line, standard input or the file named by the operand, standard output, standard error,
and the exit status. They belong to the curriculum's applications-programming track (Projects
11–52) and adapt the four programs of §4.8 of Johnsonbaugh & Kalin, _Applications Programming
in ANSI C_, the section that introduces recursion: a recursive factorial, the Tower of Hanoi,
and a robot-walk count computed both recursively and without recursion.

### 2.2 Product functions

1. All tools: read numbers as integer tokens until the end of the input, and write each answer
   as soon as its number has been read; optionally write a prompt to standard error before each
   read.
2. `dp-fact`: print _n_! for 0 ≤ _n_ ≤ 20, computed by a recursive function.
3. `dp-tower`: print the 2ⁿ − 1 moves that carry _n_ ≤ 20 disks from peg A to peg B, generated
   by a recursive procedure; print `There's nothing to move!` for _n_ < 1.
4. `dp-walk-r`, `dp-walk-nr`: print W(_d_), the number of robot walks of _d_ meters, by tree
   recursion (1 ≤ _d_ ≤ 45) and by iteration (1 ≤ _d_ ≤ 91) respectively, with identical
   answers wherever both apply.
5. All tools: report invalid and out-of-range numbers and unreadable input files; display help
   and version information; detect and report usage errors.

### 2.3 Constraints

- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through NFR-05, the recursive and
  iterative structure of the computations.
- Every result MUST be computed in exact integer arithmetic. Each tool's limit (FR-02) is the
  largest argument whose result, and every intermediate value of the required computation,
  lies in 0 … 2⁶³−1, so a signed 64-bit integer type suffices and no overflow can occur.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-03.
- The input may contain any bytes; only tokens that match the _integer_ grammar are numbers.

### 2.5 Relationship to the textbook program (informative)

The section's four programs each read one number from the keyboard and print a result:
_n_! defined by 0! = 1 and _n_! = _n_ × (_n_ − 1)!; the moves of the Tower of Hanoi, each
written as `Move top disk from peg … to peg ….`, or `There's nothing to move!` when there are
fewer than one disk; and the sentence `The robot can walk … meters in … ways.`, or
`ERROR -- distance must be positive.` for a distance below 1, with the count computed by the
recursion W(1) = 1, W(2) = 2, W(_d_) = W(_d_ − 1) + W(_d_ − 2) in one program and by a loop in
the other. The tools keep:

- the three definitions, the recursive algorithm for the tower (move _n_ − 1 disks to the
  spare peg, move the top disk to the destination, move the _n_ − 1 disks from the spare peg
  to the destination), and the split of the robot walk into a recursive and an iterative
  program (as NFR-05, checked by design review);
- the texts `Move top disk from peg … to peg ….`, `There's nothing to move!`,
  `The robot can walk … meters in … ways.`, and `ERROR -- distance must be positive.` word for
  word, including `1 meters` and `1 ways`, which are not made singular;
- the peg names of the section's description: the tower moves from peg A to peg B, with peg C
  as the spare.

It changes the following, for the reasons given:

- **Explicit 64-bit limits.** The textbook computed in C's `int` and `long`, whose widths differ
  between platforms (`long` is 32 bits on 64-bit Windows and 64 bits on 64-bit Linux and
  macOS), and an overflowing result was silently wrong. Every tool here has a fixed limit
  (FR-02): 20 for `dp-fact` (20! = 2432902008176640000 is the largest factorial below 2⁶³) and
  91 for `dp-walk-nr` (W(91) = 7540113804746346429; W(92) exceeds 2⁶³ − 1). A larger number is
  rejected with `value out of range` instead of producing a wrong answer.
- **Practical limits for exponential work.** `dp-tower` accepts at most 20 disks, which is
  1 048 575 moves and 36 700 125 bytes of output; `dp-walk-r` accepts distances up to 45, which
  already needs about 2.3 × 10⁹ recursive evaluations (NFR-03). Both results would fit in 64
  bits for larger arguments; the limits keep the run time and output bounded.
- **A negative factorial is a data error.** The section requires an error for negative input
  but gives no text, so `dp-fact` uses the standard `value out of range` diagnostic (FR-05).
- **The walk error becomes a diagnostic.** `ERROR -- distance must be positive.` is kept word
  for word but written as a located CONV-34 diagnostic on standard error, with exit status 1,
  so a script can tell it from an answer (FR-05). `There's nothing to move!` remains an
  ordinary answer on standard output, because zero disks (or fewer) is a valid, if trivial,
  tower; this includes negative numbers, exactly as in the textbook.
- **Many numbers per run.** Each tool answers every number in its input, in order, instead of
  one number per run, so the walk tools can be compared over a whole list of distances, and
  reads from a FILE operand as well as from standard input (FR-01). CRLF line endings and a
  trailing Ctrl-Z marker are accepted (FR-02).
- **Prompts are optional and go to standard error.** The textbook programs asked for their
  number at the keyboard; the section's description gives no prompt texts, so the prompts of
  FR-04 are written in the same voice. They appear only with `-p`, `--prompt`, and never change
  standard output. Blank lines that only separated the output from the echo of the user's
  typing are not written.
- **Invalid input is diagnosed** with its line number (FR-05) instead of leaving the result
  unspecified.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and the exit statuses are those of CONV-18.
Standard input is read as permitted by CONV-26. No tool copies input bytes to its output, so
CONV-04 does not apply. Of the conventions for Projects 11–52:

| Convention | Use in this SRS                                                                                                                                                                                                               |
| :--------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CONV-32    | Every tool reads its input as tokens, with CONV-32 line numbers (FR-02).                                                                                                                                                      |
| CONV-33    | Every token uses the _integer_ grammar, further range-restricted per tool (FR-02).                                                                                                                                            |
| CONV-34    | Data diagnostics use its format, the standard messages `invalid integer` and `value out of range`, and one further message for the walk tools, `ERROR -- distance must be positive.` (FR-05). The default consequences apply. |
| CONV-35    | Not applicable: no real number is ever written.                                                                                                                                                                               |
| CONV-36    | Every tool has `-p`, `--prompt` with one prompt (FR-04).                                                                                                                                                                      |
| CONV-37    | The input of every tool is _text data_ (FR-02).                                                                                                                                                                               |
| CONV-38    | Not applicable: nothing is random.                                                                                                                                                                                            |

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-fact [-p | --prompt] [FILE]
dp-tower [-p | --prompt] [FILE]
dp-walk-r [-p | --prompt] [FILE]
dp-walk-nr [-p | --prompt] [FILE]
<tool> --help
<tool> --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                                  |
| :---- | :---------- | :------- | :------ | :--------------------------------------------------------------------------- |
| `-p`  | `--prompt`  | none     | off     | Write the tool's prompt (FR-04) to standard error before each number is read |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                               |
| —     | `--version` | none     | —       | Print the version line and exit 0                                            |

All four tools have the same options. Option syntax (bundling, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. Giving `-p` more than once has the same effect as giving it
once (CONV-11).

### 3.3 Operands

At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input

Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output

The answers (FR-06, FR-08, FR-10), in input order. Nothing else. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-13 … FR-16 instead.

### 3.6 Standard error

Prompts (FR-04, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                      |
| :----- | :--------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | The whole input was processed (including an empty input), or `--help` / `--version` was handled                                                |
| 1      | The input could not be opened or read (FR-12), it contained an invalid or out-of-range number (FR-05), or standard output could not be written |
| 2      | Usage error (FR-15)                                                                                                                            |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the named files are the public fixtures in
`tests/fixtures/`: `facts.txt` is `0\n1\n5\n+7 010\r\n20\n`; `three.txt` is `3\n`; `disks.txt`
is `2\n0\n`; `dists.txt` holds the distances 1 to 10, one per line; `far.txt` is `40\n91\n`;
`neg.txt` is `5\n-1\n6\n`; `stop.txt` is `3\n0\n4\n`.

### 4.1 Input, prompts, and data errors (all tools)

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-15).
_AC:_ `dp-walk-nr dists.txt` and `dp-walk-nr - < dists.txt` write the same answers.
_(UR-01, UR-09)_

**FR-02: Tokens and numbers.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order. Each token MUST be a valid _integer_ (CONV-33); a sign (`+5`, `-0`) and
leading zeros (`010`) are allowed, and the number is the token's value. Line structure has no
meaning: numbers may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF
input reads exactly like LF input. Each tool accepts the following numbers:

| Tool         | Accepted numbers                                         | Below the range                       | Above the range      |
| :----------- | :------------------------------------------------------- | :------------------------------------ | :------------------- |
| `dp-fact`    | 0 … 20                                                   | `value out of range`                  | `value out of range` |
| `dp-tower`   | every number up to 20 (numbers below 1 are valid; FR-08) | —                                     | `value out of range` |
| `dp-walk-r`  | 1 … 45                                                   | `ERROR -- distance must be positive.` | `value out of range` |
| `dp-walk-nr` | 1 … 91                                                   | `ERROR -- distance must be positive.` | `value out of range` |

A token that is not a valid _integer_, or a number outside the tool's range, is handled by
FR-05.
_AC:_ `dp-fact facts.txt` answers 0, 1, 5, 7, 10, and 20, in that order, exit 0.
_(UR-01, UR-02, UR-13)_

**FR-03: Streaming.**
Numbers MUST be processed one at a time, in input order. As soon as a token is complete
(section 1.3) and valid, the tool MUST write the number's answer to standard output and flush
standard output, before it waits for any further input bytes. The tool MUST NOT wait for the
end of the input before writing an answer, and MUST NOT read the input beyond what it needs to
complete the current token, apart from ordinary buffering of bytes that are already available.
Lines of a long answer (FR-08) MAY be written before the whole answer has been computed. When
the end of the input is reached, the tool exits with status 0. An empty input, or one that
contains only whitespace and a trailing Ctrl-Z run, produces no output and exit status 0.
_AC:_ `dp-fact -p` with empty standard input → stdout empty, exit 0. At a terminal, typing `5`
and Enter to `dp-fact` shows `5! = 120` before anything else is typed (manual check).
_(UR-01, UR-11)_

**FR-04: Prompts.**
`-p`, `--prompt` enables the tool's single prompt:

| Tool                      | Prompt (exact bytes, no LF)     | Length   |
| :------------------------ | :------------------------------ | :------- |
| `dp-fact`                 | `Enter a nonnegative integer: ` | 29 bytes |
| `dp-tower`                | `Enter number of disks: `       | 23 bytes |
| `dp-walk-r`, `dp-walk-nr` | `Enter distance: `              | 16 bytes |

Each prompt ends with one space. With prompts enabled, the tool MUST write its prompt to
standard error, and flush standard error, immediately before each attempt to read a number:
once before the first token, and once after each answer has been written. A prompt is
therefore also written before the attempt that reaches the end of the input (CONV-36): an
input with _n_ valid numbers produces _n_ + 1 prompts, and an input whose _k_-th token is
rejected produces _k_ prompts, the last followed directly by the diagnostic of FR-05 on the
same line. Prompts never change standard output. No prompt is written if the input cannot be
opened, or on a usage error.
_AC:_ `dp-tower --prompt < disks.txt` → stdout as without `--prompt`, stderr
`Enter number of disks: ` three times with no LF, exit 0. _(UR-10)_

**FR-05: Data errors.**
At the first token that is rejected, the tool MUST write one diagnostic,
`<tool>: <source>:<line>: <message>`, where `<source>` is as defined in section 1.3 and
`<line>` is the token's line number (CONV-32):

| Condition                                                                               | Tools      | `<message>`                           |
| :-------------------------------------------------------------------------------------- | :--------- | :------------------------------------ |
| The token is not a valid _integer_ (CONV-33), including an integer outside −2⁶³ … 2⁶³−1 | all        | `invalid integer '<token>'`           |
| The number is below 0 or above 20                                                       | `dp-fact`  | `value out of range '<token>'`        |
| The number is above 20                                                                  | `dp-tower` | `value out of range '<token>'`        |
| The number is below 1                                                                   | walk tools | `ERROR -- distance must be positive.` |
| The number is above 45 (`dp-walk-r`) or above 91 (`dp-walk-nr`)                         | walk tools | `value out of range '<token>'`        |

`<token>` is the token's exact bytes (CONV-34). The message `ERROR -- distance must be
positive.` is the textbook's text and is written exactly, ending with the period; it does not
quote the token. The tool then stops: it reads no further input, writes no further answer,
and exits with status 1. Nothing of the rejected number's answer is written; answers already
written for earlier numbers are kept (CONV-34).
_AC:_ `dp-fact neg.txt` → stdout `5! = 120\n`, stderr
`dp-fact: neg.txt:2: value out of range '-1'\n`, exit 1. `dp-walk-r stop.txt` → stdout
`The robot can walk 3 meters in 3 ways.\n`, stderr
`dp-walk-r: stop.txt:2: ERROR -- distance must be positive.\n`, exit 1. A token `21` gives
`value out of range '21'` for `dp-fact` and `dp-tower`; `9223372036854775808` and `four` give
`invalid integer`; a token `3` followed by a `0x1A` byte and an LF gives `invalid integer`,
because that Ctrl-Z byte does not end the input. _(UR-08)_

### 4.2 dp-fact

**FR-06: Factorial.**
For a number _n_ (0 ≤ _n_ ≤ 20), `dp-fact` MUST write the line

```text
<n>! = <F>
```

where `<n>` is the decimal of _n_ (so `+7` is written `7` and `010` is written `10`), `<F>` is
the decimal of _n_!, with 0! = 1 and _n_! = _n_ × (_n_ − 1)! for _n_ > 0, and the line ends
with a single LF. There is one space on each side of `=` and no other space.
_AC:_ `dp-fact facts.txt` → `0! = 1\n1! = 1\n5! = 120\n7! = 5040\n10! = 3628800\n20! = 2432902008176640000\n`,
stderr empty, exit 0. _(UR-02)_

### 4.3 dp-tower

**FR-07: Move sequence.**
For _n_ ≥ 1 disks, the moves are the sequence _H_(_n_, A, B, C), where _H_(_k_, _o_, _d_,
_s_) — move _k_ disks from peg _o_ to peg _d_, using peg _s_ as the spare — is defined by

- _H_(1, _o_, _d_, _s_) = the single move _o_ → _d_;
- _H_(_k_, _o_, _d_, _s_) = _H_(_k_ − 1, _o_, _s_, _d_), then _o_ → _d_, then
  _H_(_k_ − 1, _s_, _d_, _o_), for _k_ > 1.

The sequence has exactly 2ⁿ − 1 moves; it carries the whole tower from peg A to peg B and never
places a disk on a smaller one.
_AC:_ for _n_ = 3 the moves are A → B, A → C, B → C, A → B, C → A, C → B, A → B. _(UR-03)_

**FR-08: Tower answer.**
For a number _n_ with 1 ≤ _n_ ≤ 20, `dp-tower` MUST write one line per move of FR-07, in order,
each exactly

```text
Move top disk from peg <o> to peg <d>.
```

where `<o>` and `<d>` are the single capital letters `A`, `B`, or `C`, and the line ends with a
single LF (35 bytes per line). For a number _n_ < 1 (zero or negative), it MUST write the
single line `There's nothing to move!` + LF, where the apostrophe is the ASCII byte `0x27`. The
answers of successive numbers follow one another with no separator.
_AC:_ `dp-tower < three.txt` → the seven lines of FR-07, exit 0; `dp-tower --prompt < disks.txt`
→ stdout `Move top disk from peg A to peg C.\nMove top disk from peg A to peg B.\nMove top disk from peg C to peg B.\nThere's nothing to move!\n`.
_(UR-03, UR-04)_

### 4.4 dp-walk-r and dp-walk-nr

**FR-09: Walk count.**
W(_d_), for _d_ ≥ 1, is the number of sequences of steps of 1 and 2 meters whose lengths add
up to _d_ meters. It is given by W(1) = 1, W(2) = 2, and W(_d_) = W(_d_ − 1) + W(_d_ − 2) for
_d_ > 2 (the Fibonacci sequence shifted by one place). W(91) = 7540113804746346429 is the
largest value below 2⁶³; W(92) exceeds 2⁶³ − 1.
_AC:_ W(1 … 10) = 1, 2, 3, 5, 8, 13, 21, 34, 55, 89; W(25) = 121393; W(40) = 165580141;
W(45) = 1836311903; W(46) = 2971215073. _(UR-05)_

**FR-10: Walk answer.**
For an accepted distance _d_ (FR-02), a walk tool MUST write the line

```text
The robot can walk <d> meters in <W> ways.
```

where `<d>` is the decimal of _d_, `<W>` is the decimal of W(_d_), and the line ends with a
single LF. The words are never made singular: _d_ = 1 gives
`The robot can walk 1 meters in 1 ways.`
_AC:_ `dp-walk-nr far.txt` → `The robot can walk 40 meters in 165580141 ways.\nThe robot can walk 91 meters in 7540113804746346429 ways.\n`,
exit 0. _(UR-05)_

**FR-11: Agreement of the walk tools.**
For every argument list (apart from `--help` and `--version`) and every input whose numbers
all lie in 1 … 45, or that is rejected (FR-05) before any number above 45, `dp-walk-r` and
`dp-walk-nr` MUST write the same standard output and exit with the same status, and their
standard error MUST differ only in the tool name. A number in 46 … 91 is answered by
`dp-walk-nr` and rejected by `dp-walk-r` with `value out of range`. How each tool computes
W(_d_) is prescribed by NFR-05 and checked by design review and measurement (NFR-03), not by
the black-box tests.
_AC:_ `dp-walk-r dists.txt` and `dp-walk-nr - < dists.txt` both write the ten lines for the
distances 1 to 10, the fifth being `The robot can walk 5 meters in 8 ways.`; for a file
`25\n46\n`, `dp-walk-r` answers 25 and then reports `value out of range '46'`, while
`dp-walk-nr` answers both. _(UR-06, UR-07)_

### 4.5 All tools

**FR-12: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `<tool>: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. No prompt is written when the input cannot be opened. Answers already
written are kept. When standard input fails, `<source>` is `-`.
_AC:_ `dp-fact missing.txt` → stderr `dp-fact: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-tower subdir` where `subdir` is a directory →
`dp-tower: subdir: Is a directory`. _(UR-12)_

**FR-13: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read and no prompt
is written.
_AC:_ each tool's `--help` matches the user manual exactly; `dp-fact extra1 extra2 --help`
also prints the help. _(UR-14)_

**FR-14: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ `dp-walk-nr --version` → `dp-walk-nr (dialectic-playground) 1.0.0\n`. _(UR-14)_

**FR-15: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `<tool>: extra operand '<second operand>'`, after the whole
argument list has been scanned (CONV-12).
_AC:_ `dp-walk-nr dists.txt extra` → `dp-walk-nr: extra operand 'extra'`; `dp-tower -x --help`
→ `dp-tower: invalid option -- 'x'`; `dp-walk-nr --prompt=yes` →
`dp-walk-nr: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. _(UR-15, UR-17)_

**FR-16: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case; `dp-tower -p - extra < three.txt` writes no
prompt. _(UR-15)_

## 5. Non-functional requirements

| ID     | Category                                                 | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Verification                                                    |
| :----- | :------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                              | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: integer width and call-stack depth | Every result and intermediate value MUST be held in an integer type that is at least 64 bits wide on every platform. A type whose width differs between platforms (for example C's `long`, which is 32 bits on 64-bit Windows and 64 bits on 64-bit Linux and macOS) MUST NOT be used for them; with such a type, 13! and W(46) already overflow on Windows. The recursion of NFR-05 MUST NOT depend on the platform's default call-stack size: its depth is at most 21 frames for `dp-fact`, 20 for `dp-tower`, and 45 for `dp-walk-r`, which fits the smallest default stack of any supported platform (1 MiB for the main thread on Windows), and the tools MUST NOT raise or rely on any stack or recursion-depth setting. Inputs MUST be read in binary mode, so only FR-02 interprets CR and `0x1A`; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally; prompts and answers MUST be flushed as FR-03 and FR-04 require, even when standard output is a pipe or a file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance                                              | On CI hardware, for a natively compiled build (interpreted-runtime allowance in parentheses): every tool MUST start, answer one number below 10, and exit in under 100 ms (300 ms); `dp-fact` MUST answer 1 000 000 numbers in under 2 s (20 s); `dp-tower` MUST write the 1 048 575 moves for 20 disks in under 2 s (20 s); `dp-walk-nr` MUST answer 100 000 distances of 91 in under 2 s (20 s); `dp-walk-r` MUST answer the distance 40 (204 668 309 evaluations, NFR-05) in under 5 s, and the distance 30 in under 10 s for an interpreted runtime. Peak memory MUST stay under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31), and MUST NOT grow with the number of numbers or with the number of moves: moves are written as they are generated, never collected. The run time of `dp-walk-r` grows by a factor of about 1.618 per meter (about 11 per 5 meters), as NFR-05 implies; `dp-walk-nr`'s grows linearly.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Measurement                                                     |
| NFR-04 | Robustness                                               | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range; no computation may start for a number outside the tool's range. A broken pipe on standard output ends a tool quietly (CONV-25), also in the middle of a tower's moves.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Unit + black-box tests                                          |
| NFR-05 | Maintainability: recursive and iterative design          | (a) `dp-fact`: _n_! MUST be computed by one function that, for _n_ > 0, calls itself once with _n_ − 1 and multiplies the result by _n_, and returns 1 for _n_ = 0, with no loop. (b) `dp-tower`: the moves MUST be generated by one recursive procedure that receives the number of disks and the three pegs (origin, destination, spare) as parameters and implements FR-07 directly — two recursive calls around one move — with no loop over moves, no explicit stack, and no closed-form move formula. (c) `dp-walk-r`: W(_d_) MUST be computed by plain tree recursion — one function returning _d_ for _d_ ≤ 2 and otherwise the sum of its own results for _d_ − 1 and _d_ − 2 — with no loop, no memoization or cache, no table of earlier results, and no closed formula, so that computing W(_d_) evaluates the function exactly C(_d_) times, where C(1) = C(2) = 1 and C(_d_) = 1 + C(_d_ − 1) + C(_d_ − 2), that is C(_d_) = 2·W(_d_ − 1) − 1 for _d_ ≥ 2. (d) `dp-walk-nr`: W(_d_) MUST be computed by one loop of _d_ − 2 iterations that keeps only the last two counts (O(_d_) time, O(1) space), with no recursion. (e) The four computations MUST be pure functions (or, for the tower, a procedure whose only effect is to hand each move to an output callback or stream), separate from token reading, validation, prompting, and output. (f) Command-line handling and the token-reading loop common to the four tools MUST be shared rather than duplicated, and the answer text of the two walk tools MUST come from one shared unit (Principles 3, 13, 18). | Design review                                                   |
| NFR-06 | Testability                                              | The computations MUST be covered by unit tests: _n_! for every _n_ in 0 … 20; W(_d_) of both walk tools compared for every _d_ in 1 … 30 and of `dp-walk-nr` checked for 91; the evaluation count C(_d_) of `dp-walk-r` checked for _d_ = 1 … 20 by instrumenting the recursive function (a counter visible only to tests); for _n_ = 1 … 10, the tower's move count 2ⁿ − 1 and a simulation of the three pegs proving that every move takes a top disk, never places it on a smaller disk, and ends with all disks on peg B. The tokenizer MUST be unit-tested with the input split into reads at every byte position.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Code review                                                     |
| NFR-07 | Build                                                    | Every BASE-MAKEFILE target MUST work for all four tools: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | CI                                                              |
| NFR-08 | Security                                                 | The tools MUST read only the file named by the operand or standard input, and MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try '<tool> --help' for more information.`,
where `<tool>` is the tool's canonical name.

| Trigger                                      | Exact first line                                                                     |
| :------------------------------------------- | :----------------------------------------------------------------------------------- |
| Unknown short option `x`                     | `<tool>: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T` | `<tool>: unrecognized option 'T'`                                                    |
| `--prompt=…`, `--help=…`, `--version=…`      | `<tool>: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                         | `<tool>: extra operand 'X'`                                                          |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                               | Exact message                          |
| :-------------------------------------------------------------------- | :------------------------------------- |
| FILE `F` does not exist                                               | `<tool>: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied            | `<tool>: F: Permission denied`         |
| FILE `F` is a directory                                               | `<tool>: F: Is a directory`            |
| A component of FILE `F` is not a directory                            | `<tool>: F: Not a directory`           |
| Any other open or read failure of FILE `F`                            | `<tool>: F: Input/output error`        |
| Any of the above for standard input                                   | the same message with `F` = `-`        |
| Standard output cannot be written (other than a broken pipe, CONV-25) | `<tool>: write error`                  |

Data errors (exit status 1; earlier answers kept; `S` is the source, `L` the token's line, `K`
the token):

| Tool       | Trigger                        | Exact message                                      |
| :--------- | :----------------------------- | :------------------------------------------------- |
| all        | Token is not a valid _integer_ | `<tool>: S:L: invalid integer 'K'`                 |
| dp-fact    | Number below 0 or above 20     | `dp-fact: S:L: value out of range 'K'`             |
| dp-tower   | Number above 20                | `dp-tower: S:L: value out of range 'K'`            |
| dp-walk-r  | Number above 45                | `dp-walk-r: S:L: value out of range 'K'`           |
| dp-walk-nr | Number above 91                | `dp-walk-nr: S:L: value out of range 'K'`          |
| walk tools | Number below 1                 | `<tool>: S:L: ERROR -- distance must be positive.` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-04).

## 7. Verification

| Method                                                                                                           | Applies to                                                                     |
| :--------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                                               | FR-01 … FR-11, FR-13, FR-15                                                    |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 01, 02, 04, 06, 07, 08, 09, and 10 have several steps) | FR-02 … FR-05, FR-08, FR-10 … FR-16                                            |
| Unit test (written by the implementer)                                                                           | FR-02, FR-06, FR-07, FR-09, NFR-06                                             |
| Measurement                                                                                                      | NFR-03                                                                         |
| Inspection / review / demonstration                                                                              | FR-03 (interactive timing), FR-11 (computation method), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                         | Verifies                                          |
| :--- | :------------------------------ | :------------------------------------------------ |
| 01   | `dp-fact facts.txt`             | FR-02 (sign, leading zeros, CRLF), FR-06 (0 … 20) |
| 02   | `dp-tower < three.txt`          | FR-01, FR-07, FR-08                               |
| 03   | `dp-tower --prompt < disks.txt` | FR-04, FR-08 (`There's nothing to move!`)         |
| 04   | `dp-walk-r dists.txt`           | FR-09, FR-10, FR-11                               |
| 05   | `dp-walk-nr - < dists.txt`      | FR-01, FR-10, FR-11                               |
| 06   | `dp-walk-nr far.txt`            | FR-02 (limit 91), FR-10                           |
| 07   | `dp-fact neg.txt`               | FR-05 (`value out of range`, answers kept)        |
| 08   | `dp-walk-r stop.txt`            | FR-05 (`ERROR -- distance must be positive.`)     |
| 09   | `dp-tower --help`               | FR-13                                             |
| 10   | `dp-walk-nr dists.txt extra`    | FR-15, FR-16                                      |

## 8. Traceability (URD → SRS)

| User requirement | System requirements            |
| :--------------- | :----------------------------- |
| UR-01            | FR-01, FR-02, FR-03            |
| UR-02            | FR-02, FR-06                   |
| UR-03            | FR-07, FR-08                   |
| UR-04            | FR-08                          |
| UR-05            | FR-09, FR-10                   |
| UR-06            | FR-11                          |
| UR-07            | FR-11, NFR-03, NFR-05          |
| UR-08            | FR-02, FR-05, CONV-33, CONV-34 |
| UR-09            | FR-01, CONV-26                 |
| UR-10            | FR-04, CONV-36                 |
| UR-11            | FR-03, NFR-02                  |
| UR-12            | FR-12, CONV-16                 |
| UR-13            | FR-02, NFR-02, CONV-37         |
| UR-14            | FR-13, FR-14                   |
| UR-15            | FR-15, FR-16                   |
| UR-16            | NFR-01, NFR-02, CONV-03        |
| UR-17            | FR-15, NFR-05, CLI-CONV        |
| UR-18            | NFR-03, NFR-07                 |
