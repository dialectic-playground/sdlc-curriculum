# Project 12 — Interactive Length Unit Conversion (`dp-convert`)

> Convert lengths in yards to feet and inches until a negative length says stop, the way a
> professional tool would: a sentinel-controlled loop that answers each length as soon as it
> is typed, exact 64-bit arithmetic with a stated limit, precise diagnostics for bad data and
> for a missing sentinel, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 12 is adapted from §1.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that asks for a length in yards, prints it in yards, feet, and inches, and repeats
until the user enters a negative number, when it prints `*** END OF PROGRAM ***`. The textbook
version assumes a well-behaved typist: it has no answer for a mistyped number, a length too
large for its integers, or an input that ends before the negative value arrives. This project
keeps its prompt, report, and banner word for word and turns it into a command-line tool that
works the same at the keyboard and in a pipeline. The engineering focus is the *sentinel
loop*: what ends it, what happens to input after it, and what happens when it never comes.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Lengths as whitespace-separated integer tokens (CONV-32, CONV-33), 0 … 256204778801521550 yards | Fractional lengths, other units, unit suffixes |
| Exact conversion: feet = yards × 3, inches = yards × 36 | Conversions in the other direction |
| A negative length as the sentinel; nothing after it is read | Continuing after the sentinel |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files, writing files |
| One block per length, flushed before the next length is read | Summary totals |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), including a missing sentinel; CONV-16 file errors | Recovering after an invalid length |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Write a sentinel-controlled loop that stops at the sentinel without reading further, so it
   ends at once at a keyboard and leaves the rest of a pipe untouched (FR-05).
2. Decide, specify, and test what a sentinel loop does when the input ends without the
   sentinel, instead of looping forever or failing silently (FR-07).
3. Implement a numeric grammar exactly (CONV-33) and an explicit overflow limit derived from
   the arithmetic, and prove both with boundary tests (FR-02, FR-03, FR-09).
4. Separate prompts (standard error) from results (standard output), so redirected output is
   identical with or without prompting (FR-08, CONV-36).
5. Keep an interactive dialog responsive on every platform by flushing each prompt and each
   result before blocking on input (NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`lengths.txt`, `mixed.txt`, `nosentinel.txt`, `bad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-convert`, with unit tests — including the boundary tests of the
   conversion that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-convert into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
