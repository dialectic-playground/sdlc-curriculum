# Project 18 — Prime Number Generation via Trial Division (`dp-primes`)

> List every prime up to a bound the user types, the way a professional tool would: an exact
> header and one prime per line, a stated upper limit with a performance guarantee at that
> limit, precise diagnostics for a mistyped bound, and byte-identical output on Linux, macOS,
> and Windows.

## Purpose

Project 18 is adapted from §3.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that asks for an integer *n* and prints every prime less than or equal to *n*, found
by trial division. The textbook version divides each candidate by every smaller integer, has no
answer for a mistyped number, and mixes its banner and prompt with its results. This project
keeps the report layout and turns the program into a well-behaved command-line tool. The
engineering focus is *algorithmic efficiency under a stated requirement*: the naive nested loop
is correct, but the tool must list the 664579 primes up to its limit of 10000000 within a
deadline, so the learner chooses and justifies a faster algorithm (trial division up to √*p*,
or a sieve) and proves it equivalent with tests.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| The bound *n* as the first integer token of standard input or one `FILE` (CONV-32, CONV-33) | Bounds given as options or several bounds per run |
| Every prime 2 … *n*, ascending, under the header `<TAB>Primes <= n:` | Primality of a single number, factorisation, ranges with a lower bound |
| Any 64-bit *n* ≤ 10000000; *n* < 2 lists no primes | *n* above 10000000 |
| A count-only mode (`-c`, `--count`) | Other output formats (columns, CSV) |
| Optional banner and prompt on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Recovering from an invalid bound |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Turn a mathematical definition (a prime has no divisor other than 1 and itself) into a
   correct algorithm, and test it at its edges: *n* < 2, *n* = 2, negative *n* (FR-03).
2. Measure an algorithm against a performance requirement and replace the naive O(*n*²) trial
   division with trial division up to √*p* or a sieve, without changing a single output byte
   (FR-03, NFR-03).
3. Choose and enforce an explicit input limit, and reject values beyond it with a precise,
   located diagnostic (FR-02, FR-07).
4. Separate a dialog (banner and prompt on standard error) from results (standard output), so
   redirected output is identical with or without prompting (FR-06, CONV-36).
5. Answer as soon as the bound has been typed, without waiting for the end of the input, while
   reading the same bytes on every platform (FR-05, NFR-02).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-13) |
| `specs/SRS.md` | System requirements (FR-01 … FR-12, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Input files shared by both suites (`fifteen.txt`, `hundred.txt`, `one.txt`, `negative.txt`, `limit.txt`, `bad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-primes`, with unit tests — including the comparison of your prime
   generator with a naive trial-division oracle that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-primes into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
