# Project 51 — Recursive Fractal Geometry: The Koch Snowflake (`dp-koch`)

> Compute the von Koch curve and snowflake by multi-branch recursion and write every vertex as
> text or SVG, the way a professional tool would: a fully specified floating-point computation
> that prints the same digits in every language, the textbook's "do another?" dialog,
> precise diagnostics, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 51 is adapted from §11.4 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
a program that asks for a level from 0 to 6 and draws the von Koch snowflake on a DOS graphics
screen, tracking the drawing direction as one of six 60° codes, and then asks
`Do another (y = yes, n = no)? `. This project keeps the recursion, the direction codes, and the
dialog, and replaces the screen with output that can be tested byte for byte: a list of vertex
coordinates, or an SVG document. The engineering focus is *reproducible floating point*: the
SRS fixes every binary64 operation and its order, and CONV-35 fixes the rounding of the printed
digits, so an implementation in any language, on any platform and compiler, prints exactly the
same coordinates — including those that rounding errors push a hair below zero.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| Koch curve (4^k segments) or closed snowflake (3 × 4^k), levels 0 … 6 | Other fractals, levels above 6 |
| Base length 1 … 1000000 (`--length`, default 729), start (0, 0), direction +x | Other start points, orientations, or scaling to a window |
| Vertex list with `FIX(x, 6)` coordinates (CONV-35), or a fully specified SVG document | PNG, PostScript, colors, styling options |
| The textbook dialog from standard input or one `FILE` operand (`-` is standard input) | Several input files, writing files |
| One-shot mode (`--level`) that reads no input | Batch lists of levels on the command line |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Prompts on standard output |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37) | Other legacy encodings |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors | Recovering after invalid input |
| `--help`, `--version`, CONV-13 usage errors | Configuration files, environment variables |

## Learning objectives

1. Express a self-similar shape as a recursive function that calls itself four times per level,
   and verify the 4^k growth of its output (FR-03).
2. Compute geometry with trigonometric displacements in binary64, and make the result
   reproducible across languages by fixing every operation, its order, and its precision
   (FR-04, NFR-02).
3. Format real numbers by an exact rule rather than a library default, including the
   suppression of negative zero (FR-05, CONV-35).
4. Generate a well-formed vector-graphics document whose every byte is specified (FR-06).
5. Drive an interactive dialog from a token stream that works the same at a keyboard, in a
   pipe, and from a file, with prompts kept off standard output (FR-07, FR-08).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-15) |
| `specs/SRS.md` | System requirements (FR-01 … FR-14, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual, including the normative help text |
| `tests/fixtures/` | Dialog files shared by both suites (`two.txt`, `bad.txt`) |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-koch`, with unit tests — including the segment-count and closure
   tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-koch into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
