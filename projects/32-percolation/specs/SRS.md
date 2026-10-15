<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-perc](#software-requirements-specification-srs--dp-perc)
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

# Software Requirements Specification (SRS) — dp-perc

| Field                     | Value                                                             |
| :------------------------ | :---------------------------------------------------------------- |
| Document ID               | SRS-32                                                            |
| Project                   | `32-percolation` — Monte Carlo Forest Fire Percolation Simulation |
| Product                   | `dp-perc` (canonical name)                                        |
| Version                   | 1.0.0                                                             |
| Status                    | Approved (pre-written by the curriculum)                          |
| Parent document           | `URD.md` (URD-32)                                                 |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)                      |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018                              |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-perc`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope

`dp-perc` reads responses as tokens from standard input or from one file: a tree density, and
after each simulation an answer to `Again? (y/n)`. For each density it plants a square forest
using the CONV-38 generator, ignites the top row, spreads the fire downward, and writes the
forest before and after the fire as bordered ASCII grids, followed by four statistics lines. It
can write prompts to standard error before each response is read. It reports invalid responses
with line numbers and unreadable files with fixed messages.

### 1.3 Definitions

| Term                     | Definition                                                                                                                                                        |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                       | The line-feed byte, `0x0A`                                                                                                                                        |
| Input                    | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source                   | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number       | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| End-of-input line number | 1 plus the number of LF bytes in the whole input (CONV-32), after removal of a trailing Ctrl-Z run (FR-02)                                                        |
| _n_                      | The side of the forest: 25, or the value of `-s`, `--size` (1 … 78)                                                                                               |
| Cell (_r_, _c_)          | The cell in row _r_ and column _c_, both 1-based; row 1 is the top row, column 1 the leftmost                                                                     |
| Row-major order          | (1, 1), (1, 2), …, (1, _n_), (2, 1), …, (_n_, _n_)                                                                                                                |
| Density _D_              | The requested percentage, an integer 1 … 100                                                                                                                      |
| _T_, _S_                 | The number of trees at the start of a simulation, and the number of trees that are not burned at its end                                                          |
| Simulation               | Planting (FR-05), burning (FR-06), and writing the report (FR-09) for one density                                                                                 |
| Draw                     | One step of the CONV-38 generator, yielding _r_ in 0 … 32767                                                                                                      |
| Decimal                  | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                            |

### 1.4 References

- URD-32: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §5.12 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-perc` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §5.12 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Read a density, run one simulation, and ask whether to run another, until the answer is no
   or the input ends.
2. Plant each forest with the CONV-38 generator in a fixed draw order.
3. Ignite the top row and spread the fire downward.
4. Write each forest before and after the fire, and the statistics of the simulation.
5. Optionally write prompts to standard error before each response is read.
6. Report invalid responses and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Random numbers MUST come from the generator of CONV-38, implemented by the tool itself; the
  platform's or language's own random number facilities MUST NOT be used.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-09.
- The input may contain any bytes; only the tokens described in FR-04 are accepted.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §5.12 prompts for a density from 1 to 100, plants a 25×25 forest in
which each cell holds a tree when a random number from 1 to 100 does not exceed the density,
displays it inside a border, sets every tree of the top row burning, spreads the fire row by
row to every tree whose neighbor directly or diagonally above is burning, displays the result,
reports the requested density, the actual density, and the numbers of trees at the start and
surviving, and asks `Again? (y/n)`. `dp-perc` keeps:

- the model exactly: the side 25, the planting rule, top-row ignition, and the downward
  three-neighbor rule with the edge columns having only two upper neighbors;
- the symbols `T` (tree), space (no tree), and `*` (burned tree), and a bordered display;
- the four statistics, and the dialog: a density, a simulation, then `Again? (y/n)` with `y` or
  `Y` to continue and `n` or `N` to stop.

It changes the following, for the reasons given:

- **A specified generator.** The textbook draws from the C library's `rand()`, seeded so that
  every run differs; its sequence is not the same on any two platforms. `dp-perc` uses the
  CONV-38 generator, seeded once from `--seed` (default 1), with one draw per cell in
  row-major order and the derived value (_r_ mod 100) + 1 (FR-05), so every implementation
  plants the same forests. The generator is _not_ re-seeded between simulations: like the
  textbook's single seeding, it continues, so a session's later forests differ from its first.
- **Exact bytes for the display and the statistics.** The section does not fix the titles,
  border, or statistics wording. This SRS defines them (FR-07 … FR-09): titled grids framed by
  `+`, `-`, and `|`, one character per cell, and statistics lines whose real-valued density is
  written with `FIX(x, 2)` (CONV-35) from a single specified division.
- **Invalid responses are diagnosed.** A density outside 1 … 100, a token that is not an
  integer, or an answer other than `y`, `Y`, `n`, `N` is reported with its line number and
  ends the session with status 1 (FR-11), instead of being asked again: the tool reads a
  stream that may be a file, where asking again would loop or misalign the responses.
- **Input sources and prompts.** Besides standard input, one FILE operand may be named (FR-01).
  CRLF line endings and a trailing Ctrl-Z marker are accepted (FR-02). The prompts are written
  only with `-p`, `--prompt`, and only to standard error (FR-10). Blank lines that separated
  the textbook's output from typed responses are not written.
- **An optional forest size.** `-s`, `--size` (1 … 78; 78 keeps a bordered row within 80
  columns) makes small, readable examples and tests possible. The default remains 25.
- **README claim corrected.** The section's README states that a phase transition occurs near
  59% density. That value is the threshold of undirected four-neighbor site percolation. In
  this downward three-neighbor model the fire reaches the bottom row of a 25×25 forest in
  fewer than 20% of runs at density 40 and in every run at density 60 (measured with the
  reference model over 200 runs per density); the transition lies near 45–50%. No requirement
  depends on this observation.

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (a density uses the
_integer_ grammar, further restricted to 1 … 100), CONV-34 (data diagnostics, with the standard
messages `invalid integer`, `value out of range`, and `unexpected end of input`, plus the
additional message `invalid answer` in the same format, and the default consequences), CONV-35
(`FIX` for the actual density), CONV-36 (`-p`, `--prompt`), CONV-37 (the input is _text data_),
and CONV-38 (the generator and `--seed`, with the draw order and derived values of FR-05).
Option syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit
statuses are those of CONV-18. Standard input is read as permitted by CONV-26. `dp-perc` copies
no input bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-perc [-p | --prompt] [-s SIZE | --size=SIZE] [--seed=SEED] [FILE]
dp-perc --help
dp-perc --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                         |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-10 to standard error                        |
| `-s`  | `--size`    | SIZE     | 25      | The side _n_ of the forest, 1 … 78 (FR-13)                          |
| —     | `--seed`    | SEED     | 1       | The initial state of the generator, 0 … 4294967295 (FR-13, CONV-38) |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                      |
| —     | `--version` | none     | —       | Print the version line and exit 0                                   |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12: `-ps5`
means `-p -s 5`, `--size 5` and `--seed 7` take the next argument, and when `--size` or
`--seed` is repeated the last occurrence wins (CONV-11). `--seed` has no short form.

### 3.3 Operands

At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input

Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output

One report per simulation (FR-09), in order. Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-14 … FR-17 instead.

### 3.6 Standard error

Prompts (FR-10, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                   |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------ |
| 0      | The session ended with the answer `n` or `N`, or with the end of the input in place of an answer; or `--help` / `--version` was handled     |
| 1      | The input could not be opened or read (FR-12), it contained an invalid or missing response (FR-11), or standard output could not be written |
| 2      | Usage error (FR-16)                                                                                                                         |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the files named are the public fixtures in
`tests/fixtures/`: `once.txt` is `60\nn\n`; `again.txt` is `30\ny\n80\nn\n`; `full.txt` is
`100\nY\n1\nN\n`; `bad-density.txt` is `45\ny\n101\n`; `bad-answer.txt` is `50\nmaybe\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-16).
_AC:_ `dp-perc --size=8 again.txt` and `dp-perc --size=8 < again.txt` write the same reports.
_(UR-08)_

**FR-02: Tokens.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
read in order; responses may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so
CRLF input reads exactly like LF input. The input MUST be read incrementally: a token is
complete, and MUST be processed, as soon as the whitespace byte that follows it has been read;
the only permitted lookahead is a run of `0x1A` bytes, which is held back until the next byte
shows whether it reaches the end of the input. A `0x1A` byte that does not reach the end is
ordinary data and belongs to a token.
_AC:_ the hidden fixture `ctrlz.txt` (`70\r\nY\r\n20\r\nn\r\n` and a final `0x1A`) runs two
simulations and exits 0; in `midz.txt` (`70`, `0x1A`, CR, LF) the token made of `70` and the
`0x1A` byte is an `invalid integer`. _(UR-12)_

**FR-03: Session.**
The tool MUST run the following loop:

1. Write prompt P1 (FR-10). Read the next token; if the input has ended, report
   `unexpected end of input` (FR-11). The token is the density _D_ (FR-04).
2. Run one simulation with _D_ (FR-05, FR-06) and write its report (FR-09).
3. Write prompt P2. Read the next token. If the input has ended, or the token is `n` or `N`,
   end the session: the rest of the input is not read. If the token is `y` or `Y`, continue
   with step 1. Any other token is an invalid answer (FR-11).

When the session ends, the tool exits with status 0. A density is therefore required at the
start and after every `y`, and the end of the input in place of an answer is the same as `n`.
_AC:_ `dp-perc --size=8 again.txt` writes two reports (densities 30 and 80), exit 0; the hidden
fixture `eofanswer.txt` (`50\n`) writes one report, exit 0; `cutdensity.txt` (`50 y\n`) writes
one report, then `dp-perc: cutdensity.txt:2: unexpected end of input`, exit 1. _(UR-05)_

**FR-04: Responses.**
A density MUST be a valid _integer_ (CONV-33) with 1 ≤ _D_ ≤ 100; a sign and leading zeros are
allowed (`+050` is 50). An answer MUST be exactly one of the one-byte tokens `y`, `Y`, `n`,
`N`; longer tokens such as `yes` are invalid. Each token MUST be validated as soon as it is
complete, before anything else is read or written.
_AC:_ `full.txt` accepts `Y` and `N`; `bad-density.txt` rejects `101`; `bad-answer.txt` rejects
`maybe`; the hidden fixtures reject `0` (out of range), `50%` and `60.5` (invalid integer).
_(UR-01, UR-05, UR-10)_

**FR-05: Generator and planting.**
The tool MUST create exactly one CONV-38 generator per invocation, with the initial state set to
the seed (FR-13), before the first simulation. The generator MUST NOT be re-seeded or reset
between simulations: each simulation continues from the state the previous one left. To plant
a forest of side _n_ with density _D_, the tool MUST visit the *n*² cells in row-major order and
make exactly one draw per cell, yielding _r_; the cell holds a **tree** if
(_r_ mod 100) + 1 ≤ _D_, and is **empty** otherwise. A draw is made for every cell even when _D_ = 100 (where every cell
is a tree). No other draws are made. A simulation therefore consumes exactly *n*² draws.
_AC:_ with seed 1 the first twelve draws are 16838, 5758, 10113, 17515, 31051, 5627, 23010,
7419, 16212, 4086, 2749, 12767, so the derived values are 39, 59, 14, 16, 52, 28, 11, 20, 13,
87, 50, 68 and, at density 60, row 1 of the default 25×25 forest begins `TTTTTTTTT T ` (test
01); with seed 0 the first draws are 0, 21468, 9988, 22117, so `--seed=0 -s 4` at density 60
gives row 1 `T  T`; with `--size=8 again.txt` the second forest (density 80) is planted from
draws 65 … 128 of the sequence. _(UR-01, UR-06)_

**FR-06: Fire.**
After planting, the tool MUST burn the forest as follows. Every tree in row 1 becomes
**burned**. Then for _r_ = 2, 3, …, _n_ in order: a tree at (_r_, _c_) becomes burned if at
least one of the cells (*r*−1, *c*−1), (*r*−1, _c_), (*r*−1, _c_+1) that lies inside the forest
is burned. Row _r_ is decided only from the final state of row *r*−1, so the order of the cells
within a row does not matter. In column 1 only (*r*−1, 1) and (*r*−1, 2) are examined, in
column _n_ only (*r*−1, *n*−1) and (*r*−1, _n_); with _n_ = 1 only (*r*−1, 1). Empty cells never
burn, the fire never moves sideways or upward, and every tree that is not burned at the end
survives.
_AC:_ `full.txt` at density 100 burns every cell (_S_ = 0); at density 1 (seed 1, side 6) no
tree is planted and nothing burns; in test 01, the tree at (2, 13) survives because cells
(1, 12) … (1, 14) are empty, while (2, 12) burns from (1, 11). _(UR-02)_

**FR-07: Grid rendering.**
A forest of side _n_ MUST be written as _n_ + 2 lines:

1. the border: `+`, then _n_ `-` bytes, then `+`, then LF;
2. for each row from 1 to _n_: `|`, then one byte per cell from column 1 to _n_ — `T` for a
   tree, `*` for a burned tree, and a space (`0x20`) for an empty cell — then `|`, then LF;
3. the border again.

Each line is therefore exactly _n_ + 2 bytes plus LF. Spaces inside a row are significant; no
line has leading or trailing spaces outside the frame.
_AC:_ with `-s 6` and density 100 the grid before the fire is `+------+\n`, six lines
`|TTTTTT|\n`, and `+------+\n`. _(UR-03)_

**FR-08: Statistics.**
For a simulation with density _D_ on a forest of side _n_, with _T_ trees after planting and _S_
trees surviving, the tool MUST write these four lines:

```text
Requested density: <D>%
Actual density: <A>%
Trees at start: <T>
Trees surviving: <S>
```

where `<D>`, `<T>`, and `<S>` are decimals, and `<A>` is `FIX(x, 2)` (CONV-35) of the binary64
value _x_ = (100 × _T_) / (_n_ × _n_), computed as **one** binary64 division of the integers
100 × _T_ and _n_ × _n_ (both exactly representable). There is exactly one space after each
colon and none before `%` or at the end of a line.
_AC:_ 39 trees in an 8×8 forest give _x_ = 60.9375 and `Actual density: 60.94%`; 0 trees give
`0.00%`; a full forest gives `100.00%`; 18 trees in an 8×8 forest would give _x_ = 28.125, an
exact tie, written `28.12` (round half to even). _(UR-04)_

**FR-09: Report layout and timing.**
The report of one simulation MUST be, in this order and with no blank lines: the line
`Forest before fire:` + LF; the planted forest (FR-07); the line `Forest after fire:` + LF; the
burned forest (FR-07); the statistics (FR-08). Reports of successive simulations follow one
another directly. The whole report MUST be written, and standard output flushed, after the
density has been validated and before the next prompt is written or the next token is read.
_AC:_ `dp-perc -s 6 full.txt` writes two reports of 22 lines each, exit 0. At a
terminal, a report appears before the answer is typed (manual check). _(UR-03, UR-05)_

**FR-10: Prompts.**
With `-p` or `--prompt`, the tool MUST write these prompts to standard error, with no line
feed, and flush standard error before the read that follows (CONV-36):

| Prompt | Exact bytes                                             | Written                                                                                           |
| :----- | :------------------------------------------------------ | :------------------------------------------------------------------------------------------------ |
| P1     | `Enter density (1-100): ` (23 bytes, ending in a space) | Before every read of a density, including the first                                               |
| P2     | `Again? (y/n) ` (13 bytes, ending in a space)           | After every report, before the answer is read, including a read that reaches the end of the input |

Without the flag, no prompt is written. Standard output is the same with and without it. No
prompt is written if the input cannot be opened.
_AC:_ `dp-perc --prompt -s 8 < again.txt` → stdout as without `--prompt`; stderr is P1 P2 P1 P2
concatenated, exit 0. _(UR-09)_

**FR-11: Data errors.**
At the first invalid or missing response, the tool MUST write one CONV-34 diagnostic,
`dp-perc: <source>:<line>: <message>`, read no further input, and exit with status 1. Reports
already written are kept; no report is written for an invalid density.

| Condition                                                                   | `<line>`                     | `<message>`                    |
| :-------------------------------------------------------------------------- | :--------------------------- | :----------------------------- |
| A density is not a valid _integer_ (including a value outside −2⁶³ … 2⁶³−1) | the token's line             | `invalid integer '<token>'`    |
| A density is a valid _integer_ outside 1 … 100                              | the token's line             | `value out of range '<token>'` |
| An answer is not `y`, `Y`, `n`, or `N`                                      | the token's line             | `invalid answer '<token>'`     |
| The input ends where a density is required                                  | the end-of-input line number | `unexpected end of input`      |

`<token>` is the token's exact bytes (CONV-34). An empty input is therefore an error. With
`--prompt`, the diagnostic follows the last prompt on the same line of standard error.
_AC:_ `dp-perc -s 5 bad-density.txt` → one report, then stderr
`dp-perc: bad-density.txt:3: value out of range '101'\n`, exit 1; `dp-perc -s 5 bad-answer.txt`
→ one report, then `dp-perc: bad-answer.txt:2: invalid answer 'maybe'\n`, exit 1; `dp-perc`
with empty standard input → `dp-perc: -:1: unexpected end of input\n`, exit 1. _(UR-10)_

**FR-12: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-perc: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Reports already written are kept. When standard input fails, `<source>` is
`-`.
_AC:_ `dp-perc missing.txt` → stderr `dp-perc: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-perc subdir` where `subdir` is a directory →
`dp-perc: subdir: Is a directory`. _(UR-11)_

**FR-13: Option values.**
SIZE MUST consist only of ASCII digits and lie in 1 … 78. SEED MUST consist only of ASCII
digits and lie in 0 … 4294967295 (CONV-38); leading zeros are allowed in both. Any other value,
including an empty one, a sign, or spaces, is an invalid option value:
`dp-perc: invalid argument '<value>' for '<option>'`, where `<option>` is the option as written
(`-s`, `--size`, or `--seed`), followed by the CONV-14 line, exit 2. Option values are checked
after the whole argument list has been scanned (CONV-12), in this order: SIZE, then SEED, then
the number of operands; only the first error is reported.
_AC:_ `dp-perc --size=0 once.txt` → `dp-perc: invalid argument '0' for '--size'`, exit 2;
`--size=79`, `--seed=4294967296`, `--seed=-1`, `--seed=`, and `--seed=+5` are rejected likewise;
`--size=abc --seed=x` reports the size; `--size=1`, `-s78`, `--seed=0`, and
`--seed=4294967295` are accepted; `-ps5 --seed 7 --seed=3` uses side 5 and seed 3. _(UR-06, UR-07, UR-11)_

**FR-14: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
_AC:_ `dp-perc --help` matches the user manual exactly; `dp-perc extra --help` also prints it.
_(UR-13)_

**FR-15: Version.**
`--version` MUST write `dp-perc (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-13)_

**FR-16: Usage errors.**
Unknown options, a missing option argument, and arguments supplied to options that take none
(`--prompt=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--see` is
unrecognized. A second operand MUST be reported as `dp-perc: extra operand '<second operand>'`,
after the whole argument list has been scanned (CONV-12).
_AC:_ `dp-perc once.txt again.txt` → `dp-perc: extra operand 'again.txt'`; `dp-perc -x --help`
→ `dp-perc: invalid option -- 'x'`; `dp-perc --prompt=yes` →
`dp-perc: option '--prompt' doesn't allow an argument`; `dp-perc once.txt --size` →
`dp-perc: option '--size' requires an argument`; each followed by the CONV-14 line, exit 2.
_(UR-11, UR-13)_

**FR-17: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
_AC:_ stdout is empty in every exit-2 case. _(UR-11)_

## 5. Non-functional requirements

| ID     | Category                                      | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Verification                                                    |
| :----- | :-------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------- |
| NFR-01 | Portability                                   | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | CI black-box tests on 3 OSes                                    |
| NFR-02 | Cross-platform focus: reproducible randomness | The generator MUST be implemented by the tool with unsigned 32-bit arithmetic that wraps modulo 2³² (or an equivalent exact computation in a wider type), so that the product _S_ × 1103515245 can neither overflow a signed type nor be computed in floating point; the platform's `rand()`, `random()`, or any library generator MUST NOT be used, and nothing may depend on the clock, the process identifier, or the locale. The actual density MUST be computed by the single binary64 division of FR-08 and formatted by `FIX`, never by a library default. Inputs MUST be read in binary mode, so CR bytes reach the tokenizer and only FR-02 interprets `0x1A`; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output MUST be flushed after each report and standard error after each prompt. | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance                                   | One simulation of the largest forest (side 78) MUST complete, including start-up and exit, in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). A session of 1 000 simulations of side 25 MUST take under 2 s native (20 s interpreted); memory MUST NOT grow with the number of simulations.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Measurement                                                     |
| NFR-04 | Robustness                                    | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and every side 1 … 78 (no neighbor check may read outside the forest). A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | Unit + black-box tests                                          |
| NFR-05 | Maintainability                               | Option parsing, the incremental tokenizer, the generator, planting, burning, rendering, statistics, and the session loop MUST be separate units. The generator MUST be one unit whose state is passed to (or owned by) the planting unit, not a global hidden in it; planting MUST be a function of the side, the density, and the generator; burning MUST be a function of a planted forest with no input or output; one rendering procedure MUST write a forest under a given title and be used for both grids.                                                                                                                                                                                                                                                                                                                                                                                                                        | Design review                                                   |
| NFR-06 | Testability                                   | The generator MUST be unit-tested against the draw sequences of FR-05 for the seeds 0, 1, and 4294967295; planting against the derived-value rule at the densities 1, 60, and 100; burning with sides 1, 2, and 3, burned trees in the edge columns, and a forest in which the fire stops halfway; the statistics with the values of FR-08. The tokenizer MUST be unit-tested with the input split into reads at every byte position.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Code review                                                     |
| NFR-07 | Build                                         | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | CI                                                              |
| NFR-08 | Security                                      | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Inspection                                                      |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-perc --help' for more information.`

| Trigger                                            | Exact first line                                                                      |
| :------------------------------------------------- | :------------------------------------------------------------------------------------ |
| Unknown short option `x`                           | `dp-perc: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T`       | `dp-perc: unrecognized option 'T'`                                                    |
| `-s` as the last argument                          | `dp-perc: option requires an argument -- 's'`                                         |
| `--size` or `--seed` as the last argument          | `dp-perc: option '--size' requires an argument` (or `'--seed'`)                       |
| `--prompt=…`, `--help=…`, `--version=…`            | `dp-perc: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| Invalid SIZE `V` given with `O` (`-s` or `--size`) | `dp-perc: invalid argument 'V' for 'O'`                                               |
| Invalid SEED `V`                                   | `dp-perc: invalid argument 'V' for '--seed'`                                          |
| A second operand `X`                               | `dp-perc: extra operand 'X'`                                                          |

Runtime errors (exit status 1; the tool stops at the first one; earlier reports are kept):

| Trigger                                                                          | Exact message                           |
| :------------------------------------------------------------------------------- | :-------------------------------------- |
| FILE `F` does not exist                                                          | `dp-perc: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                       | `dp-perc: F: Permission denied`         |
| FILE `F` is a directory                                                          | `dp-perc: F: Is a directory`            |
| A component of FILE `F` is not a directory                                       | `dp-perc: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                       | `dp-perc: F: Input/output error`        |
| Any of the above for standard input                                              | the same message with `F` = `-`         |
| Density token `K` on line `L` of source `S` is not a valid _integer_             | `dp-perc: S:L: invalid integer 'K'`     |
| Density token `K` on line `L` of source `S` is outside 1 … 100                   | `dp-perc: S:L: value out of range 'K'`  |
| Answer token `K` on line `L` of source `S` is not `y`, `Y`, `n`, or `N`          | `dp-perc: S:L: invalid answer 'K'`      |
| Source `S` ends where a density is required; `L` is the end-of-input line number | `dp-perc: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)                     | `dp-perc: write error`                  |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-10).

## 7. Verification

| Method                                                                                | Applies to                                         |
| :------------------------------------------------------------------------------------ | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)                                    | FR-01, FR-03 … FR-14, FR-16, FR-17                 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 09 have several steps) | FR-02 … FR-17                                      |
| Unit test (written by the implementer)                                                | FR-02, FR-05, FR-06, FR-08, NFR-06                 |
| Measurement                                                                           | NFR-03                                             |
| Inspection / review                                                                   | FR-09 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                                | Verifies                                                     |
| :--- | :------------------------------------- | :----------------------------------------------------------- |
| 01   | `dp-perc once.txt`                     | FR-03, FR-05 … FR-09 (default side 25, seed 1)               |
| 02   | `dp-perc --size=8 again.txt`           | FR-03, FR-05 (generator continues across simulations), FR-13 |
| 03   | `dp-perc --prompt -s 8 < again.txt`    | FR-01, FR-10                                                 |
| 04   | `dp-perc --seed=42 --size=10 once.txt` | FR-05, FR-13 (CONV-38 seed)                                  |
| 05   | `dp-perc -s 6 full.txt`                | FR-04 (`Y`, `N`), FR-05, FR-06 (densities 100 and 1), FR-08  |
| 06   | `dp-perc -s 5 bad-density.txt`         | FR-04, FR-11 (report kept)                                   |
| 07   | `dp-perc -s 5 bad-answer.txt`          | FR-04, FR-11 (`invalid answer`)                              |
| 08   | `dp-perc missing.txt`                  | FR-12                                                        |
| 09   | `dp-perc --help`                       | FR-14                                                        |
| 10   | `dp-perc --size=0 once.txt`            | FR-13, FR-17                                                 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                          |
| :--------------- | :------------------------------------------- |
| UR-01            | FR-03, FR-04, FR-05                          |
| UR-02            | FR-06                                        |
| UR-03            | FR-07, FR-09                                 |
| UR-04            | FR-08, CONV-35                               |
| UR-05            | FR-03, FR-04, FR-09                          |
| UR-06            | FR-05, FR-13, NFR-02, CONV-38                |
| UR-07            | FR-13                                        |
| UR-08            | FR-01, CONV-26                               |
| UR-09            | FR-10, CONV-36                               |
| UR-10            | FR-04, FR-11, CONV-33, CONV-34               |
| UR-11            | FR-12, FR-13, FR-16, FR-17, CONV-13, CONV-16 |
| UR-12            | FR-02, NFR-02, CONV-37                       |
| UR-13            | FR-14, FR-15, FR-16, CLI-CONV                |
| UR-14            | NFR-03, NFR-07                               |
