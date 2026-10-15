<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 30 — Matrix Multiplication Engine (`dp-matmult`)](#project-30--matrix-multiplication-engine-dp-matmult)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 30 — Matrix Multiplication Engine (`dp-matmult`)

> Read two square matrices of integers, print them, and print their product, the way a
> professional tool would: row-major input from the keyboard, a pipe, or a file; exact 64-bit
> arithmetic with every overflow detected instead of silently wrapped; precise diagnostics for
> bad data; and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 30 is adapted from §5.10 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that asks for a size _N_ (at most 20), reads two *N*×*N* matrices row by row, echoes
each one, and prints their product computed with the classic triply nested loop. The textbook
version stores the matrices in fixed two-dimensional arrays, trusts every number it is given,
and lets an oversized product wrap around without a word. This project keeps its dialog and its
report headings and turns it into a well-behaved command-line tool. The engineering focus is
_two-dimensional data in row-major order_ and _checked integer arithmetic_: every term and
every partial sum of every dot product is verified to fit in a 64-bit signed integer, in a
precisely specified order, so that independent implementations agree on exactly which inputs
are rejected.

## Operational scope

| In scope                                                                                               | Out of scope                                            |
| :----------------------------------------------------------------------------------------------------- | :------------------------------------------------------ |
| A size _N_ (1 … 20) and two *N*×*N* matrices as whitespace-separated integer tokens (CONV-32, CONV-33) | Non-square or rectangular matrices, sizes above 20      |
| 64-bit signed elements and results, with overflow in any term or partial sum reported                  | Arbitrary-precision results, real (fractional) elements |
| Both matrices echoed and the product printed under the textbook's headings                             | Column alignment, other matrix operations               |
| Standard input or one `FILE` operand (`-` is standard input)                                           | Several input files, writing files                      |
| The first matrix printed before the second is read (interactive use)                                   | Waiting for the whole input before answering            |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                                         | Prompts on standard output                              |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                                          | Other legacy encodings                                  |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                                      | Recovering after an invalid element                     |
| `--help`, `--version`, CONV-13 usage errors                                                            | Configuration files, environment variables              |

## Learning objectives

1. Represent a two-dimensional grid in memory, fill it from a row-major stream of tokens, and
   print it back row by row (FR-03, FR-04).
2. Implement the O(*N*³) matrix product as one function of two matrices and test its algebraic
   properties: the identity, the zero matrix, and non-commutativity (FR-06, NFR-06).
3. Detect signed 64-bit overflow in multiplication and addition _before_ it happens, with a
   specified evaluation order, instead of relying on wrap-around or undefined behavior
   (FR-06, FR-09).
4. Interleave reading and writing so that a keyboard user sees the first matrix before typing
   the second, while redirected output stays clean (FR-05, FR-07).
5. Read data written on any platform — CRLF line endings, a Ctrl-Z end-of-file byte — with the
   same result (NFR-02).

## What is provided

| Path                   | Contents                                                                                                    |
| :--------------------- | :---------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                           |
| `specs/SRS.md`         | System requirements (FR-01 … FR-14, NFR-01 … NFR-08)                                                        |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                     |
| `tests/fixtures/`      | Input files shared by both suites (`readme.txt`, `identity.txt`, `negative.txt`, `bad.txt`, `overflow.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                      |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                     |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                         |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-matmult`, with unit tests — including the overflow boundary tests of
   the multiplication function that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-matmult into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.
