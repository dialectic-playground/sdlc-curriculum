<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 24 — Divide-and-Conquer Tromino Deficiency Tiling (`dp-tromino`)](#project-24--divide-and-conquer-tromino-deficiency-tiling-dp-tromino)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 24 — Divide-and-Conquer Tromino Deficiency Tiling (`dp-tromino`)

> Tile a 2ᵏ × 2ᵏ board that has one square missing with L-shaped trominoes, the way a
> professional tool would: a fully specified coordinate system and recursion order, so that
> every implementation lists the same trominoes in the same order, an optional numbered
> drawing of the board, precise diagnostics for bad answers, and byte-identical output on
> Linux, macOS, and Windows.

## Purpose

Project 24 is adapted from §4.9 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that asks for the size of a board (a power of 2, or 0 to quit) and the coordinates of
its missing square, and prints, for every tromino it places, the tromino's position and
orientation. The algorithm is the classic divide-and-conquer proof of Golomb's theorem: place
one tromino at the center so that each quarter of the board has exactly one square that is
missing or already covered, then tile the four quarters the same way. The textbook leaves the
coordinate system, the meaning of the orientation codes, and the treatment of bad answers to
the reader; this project fixes all three, so that the order of the output — a pre-order walk
of a four-way recursion tree — is part of the specification and can be tested byte for byte.

## Operational scope

| In scope                                                                                         | Out of scope                                |
| :----------------------------------------------------------------------------------------------- | :------------------------------------------ |
| Rounds of board size, x, y as whitespace-separated integer tokens (CONV-32, CONV-33)             | Rectangular boards, several missing squares |
| Board sizes 2, 4, 8, 16, 32, 64; size 0 quits; the end of the input also ends the session        | Boards larger than 64 × 64                  |
| One line per tromino (center of its 2 × 2 block and orientation), in a specified recursion order | Other tilings of the same board             |
| Optional numbered ASCII drawing of each tiled board (`-d`, `--draw`)                             | Graphics, colors, Unicode box drawing       |
| Standard input or one `FILE` operand (`-` is standard input)                                     | Several input files, writing files          |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                                   | Prompts on standard output                  |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                                    | Other legacy encodings                      |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                                | Recovering after an invalid answer          |
| `--help`, `--version`, CONV-13 usage errors                                                      | Configuration files, environment variables  |

## Learning objectives

1. Design a recursive divide-and-conquer algorithm whose base case and recursive step are the
   same rule, and argue its correctness by induction on the board size (FR-04).
2. Make a recursion's _visiting order_ part of an interface contract, so that independent
   implementations produce identical output (FR-04, FR-05).
3. Pin down a geometric coordinate system — origin, axis directions, what a coordinate names —
   precisely enough that a drawing and a list agree (FR-04, FR-06).
4. Read a multi-value dialog as a token stream that works the same at a keyboard and in a
   pipe, with prompts kept off standard output (FR-02, FR-07).
5. Write bulk output efficiently while still flushing at the points an interactive user needs
   (NFR-02, NFR-03).

## What is provided

| Path                   | Contents                                                                                                        |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                               |
| `specs/SRS.md`         | System requirements (FR-01 … FR-14, NFR-01 … NFR-08)                                                            |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                         |
| `tests/fixtures/`      | Input files shared by both suites (`readme.txt`, `boards.txt`, `corners.txt`, `bad-size.txt`, `bad-square.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                          |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                         |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                             |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-tromino`, with unit tests — including the exhaustive tiling check
   that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-tromino into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.
