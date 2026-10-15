<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 32 — Monte Carlo Forest Fire Percolation Simulation (`dp-perc`)](#project-32--monte-carlo-forest-fire-percolation-simulation-dp-perc)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 32 — Monte Carlo Forest Fire Percolation Simulation (`dp-perc`)

> Plant a random forest at a chosen density, set its top row on fire, let the fire spread
> downward, and show the forest before and after with statistics, the way a professional
> simulation tool would: a portable, seedable random number generator with a fully specified
> draw order, a bordered ASCII rendering, exact statistics, and byte-identical output on Linux,
> macOS, and Windows.

## Purpose

Project 32 is adapted from §5.12 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
a program that asks for a tree density, plants a 25×25 forest at random, ignites every tree in
the top row, spreads the fire to each tree that has a burning neighbor directly or diagonally
above it, prints the forest before and after the fire, reports statistics, and asks
`Again? (y/n)`. The textbook version draws from the C library's `rand()`, whose sequence differs
from one platform to the next, so no two systems show the same forest. This project keeps the
model and the dialog and turns it into a well-behaved, _reproducible_ command-line simulation.
The engineering focus is _deterministic Monte Carlo_: the generator, the seed, the exact order
in which random numbers are consumed, and how a random number becomes a tree are all part of
the specification, so the same seed gives the same forest in every implementation — and a
two-dimensional cellular automaton whose boundary columns are handled without stepping outside
the grid.

## Operational scope

| In scope                                                                                                                     | Out of scope                                         |
| :--------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- |
| Densities 1 … 100 (percent) as integer tokens and `y`/`n` answers (CONV-32, CONV-33)                                         | Fractional densities, other answers such as `yes`    |
| A square forest of side 25 by default, 1 … 78 with `-s`, `--size`                                                            | Rectangular forests, wind, sideways or upward spread |
| The ANSI C example generator with `--seed` (CONV-38), one draw per cell in row-major order                                   | The platform's own `rand()`, seeding from the clock  |
| Top-row ignition and downward spread to the three cells below a burning tree                                                 | Fire that burns out over time, animation             |
| Bordered ASCII grids before and after the fire; requested and actual density, trees at start, trees surviving                | Percolation-probability estimates over many runs     |
| Repeated simulations in one session, the generator continuing from one to the next                                           | Re-seeding between simulations                       |
| Standard input or one `FILE` operand (`-` is standard input); optional prompts on standard error (`-p`, `--prompt`, CONV-36) | Several input files, writing files                   |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37); data diagnostics (CONV-34), CONV-16 file errors               | Recovering after an invalid response                 |
| `--help`, `--version`, CONV-13 usage errors                                                                                  | Configuration files, environment variables           |

## Learning objectives

1. Implement a pseudo-random number generator exactly from its definition, and derive a
   Bernoulli trial from it with a specified formula, so that results are reproducible across
   languages and platforms (FR-05, CONV-38).
2. Implement a two-dimensional cellular-automaton update rule with neighbor checks that never
   read outside the grid at the edge columns (FR-06).
3. Render a grid as bordered ASCII art with exact bytes, including significant interior spaces
   (FR-07).
4. Compute a percentage of two integers and print it with a rounding rule that every language
   implements identically (FR-08, CONV-35).
5. Drive a repeated simulation from a stream of responses that works the same at a keyboard and
   in a pipe, with prompts kept out of the report (FR-03, FR-10).

## What is provided

| Path                   | Contents                                                                                                        |
| :--------------------- | :-------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                               |
| `specs/SRS.md`         | System requirements (FR-01 … FR-17, NFR-01 … NFR-08)                                                            |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                         |
| `tests/fixtures/`      | Response files shared by both suites (`once.txt`, `again.txt`, `full.txt`, `bad-density.txt`, `bad-answer.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                          |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                         |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                             |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-perc`, with unit tests — including the generator, planting, and
   fire-spreading tests that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-perc into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.
