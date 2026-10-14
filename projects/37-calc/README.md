# Project 37 — Interactive Accumulator Calculator (`dp-calc`)

> Evaluate lines of operator-operand pairs strictly left to right on a running total, like a
> desk adding machine, the way a professional tool would: exact 64-bit integer arithmetic with
> every overflow and division by zero caught, a rejected line that leaves the total untouched,
> one answer per line as soon as it is typed, and byte-identical output on Linux, macOS, and
> Windows.

## Purpose

Project 37 is adapted from §7.5 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
an interactive calculator whose accumulator starts at 0 and to which each input line, such as
`+ 5 * 10`, applies its operations in order, without operator precedence, printing
`0 + 5 * 10 == 50`; the operator `!` ends the calculation. The textbook builds the program from
separate modules for input/output and for evaluation. This project keeps its dialog and report
word for word and turns it into a well-behaved command-line tool. The engineering focus is
*transactional evaluation*: a line is evaluated on a copy of the accumulator and committed only
if every step succeeds, so a typo, a division by zero, or an overflow halfway along a line
leaves the total exactly as it was — and every result an implementation could compute
differently (negative division, the most negative 64-bit value) is pinned down.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Lines of whitespace-separated operator-operand pairs, evaluated left to right on an accumulator that starts at 0 | Operator precedence, parentheses, unary operators |
| `+ - * / %` on 64-bit signed integers; `/` and `%` truncate toward zero | Real numbers, other bases, arbitrary precision |
| Overflow and division by zero detected; the line is rejected and the accumulator kept | Wrapping or saturating arithmetic |
| `!` ends the calculation with ` **** End of Calculation ****` | Undo, memory registers, variables |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files |
| One result per line, flushed before the next line is read | Batch summaries |
| Optional prompt (the accumulator) on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output, line editing |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Line diagnostics with line numbers (CONV-34), processing continues; CONV-16 file errors | Stopping at the first bad line |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Separate input/output from evaluation, so the evaluator is a pure function of the
   accumulator and a line that can be unit-tested without any I/O (NFR-05).
2. Implement a small line grammar exactly and reject everything else with a precise, located
   diagnostic (FR-03, FR-08).
3. Evaluate transactionally: work on a copy and commit only when the whole line succeeds
   (FR-04, FR-08).
4. Specify and implement integer arithmetic that every language agrees on: truncating
   division and remainder of negative numbers, overflow detection before it happens, and the
   corner cases of −2⁶³ (FR-05, FR-06).
5. Write a dialog that serves a keyboard and a pipe equally well: prompts on standard error,
   results on standard output, each answer flushed before the next line is read (FR-09,
   FR-10).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-17, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`session.txt`, `acs.txt`, `messy.txt`, `negative.txt`, `errors.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.
`session.txt` replays the example dialog of the section's description.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-calc`, with unit tests — including the arithmetic boundary tests
   that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-calc into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
