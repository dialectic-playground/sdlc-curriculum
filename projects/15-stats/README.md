# Project 15 — Single-Pass Streaming Statistical Summary (`dp-stats`)

> Read real numbers until the end of the input and report their count, extremes, sum, mean,
> variance, and standard deviation, the way a professional filter would: one pass, constant
> memory, a floating-point computation fixed down to the order of every operation, exact
> decimal formatting, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 15 is adapted from §2.5 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that reads numbers until end-of-file, keeps only a running count, minimum, maximum,
sum, and sum of squares, and then prints seven summary lines. The textbook version leaves the
result of a mistyped number, an empty input, and floating-point rounding to chance. This
project keeps its report word for word and turns it into a well-behaved command-line filter.
The engineering focus is *reproducible floating-point arithmetic*: the specification fixes the
binary64 operation order, the treatment of a variance that rounding has made slightly
negative, overflow, and the decimal rounding of every printed digit, so that independent
implementations in any language agree to the last digit.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Real numbers as whitespace-separated tokens until end of input (CONV-32, CONV-33) | Digit grouping, `inf`, `nan`, hexadecimal numbers |
| Count, maximum, minimum, sum, mean, population variance, standard deviation | Sample variance, median, percentiles, histograms |
| One pass in constant memory; the exact binary64 operation order of the SRS | Compensated or two-pass summation; arbitrary precision |
| Six digits after the decimal point, correctly rounded (`FIX(x, 6)`, CONV-35) | Other precisions or exponent notation |
| Standard input or one `FILE` operand (`-` is standard input) | Several input files |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), including arithmetic overflow; CONV-16 file errors | Recovering after an invalid number |
| `--help`, `--version`, CONV-13 usage errors | Prompts, configuration files, environment variables |

## Learning objectives

1. Design a single-pass, constant-memory accumulator over an unbounded stream, and derive
   every summary from five running values (FR-03, FR-04, NFR-03).
2. Implement a floating-point computation whose result is defined to the last bit: the order
   of additions, separately rounded products, and the clamping of a negative variance before
   the square root (FR-05).
3. Format real numbers by correct decimal rounding of their exact binary value rather than by
   "whatever the language prints" (FR-06, CONV-35).
4. Detect arithmetic overflow and invalid data and report them precisely instead of printing
   `inf` or `nan` (FR-08).
5. Keep floating-point results identical across compilers, CPUs, and operating systems:
   no extended precision, no fused multiply-add contraction, no locale-dependent parsing
   (NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-14) |
| `specs/SRS.md` | System requirements (FR-01 … FR-13, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`three.txt`, `data.txt`, `single.txt`, `same.txt`, `round.txt`, `bad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-stats`, with unit tests — including the operation-order and
   clamping tests of the summary function that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-stats into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
