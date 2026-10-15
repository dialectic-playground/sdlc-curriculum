<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 22 — Roll Them Bones Dice Simulation Game (`dp-dice`)](#project-22--roll-them-bones-dice-simulation-game-dp-dice)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 22 — Roll Them Bones Dice Simulation Game (`dp-dice`)

> Play a craps-like dice game against the house, the way a professional simulation would: a
> bankroll and a table limit enforced on every bet, a fully specified pseudo-random generator so
> every seed replays the same game on every platform, and a dialog that reads its responses
> from a keyboard, a pipe, or a file.

## Purpose

Project 22 is adapted from §4.7 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
the game "Roll Them Bones". The player starts with $500, bets up to the $250 table limit on each
round, wins at once with a first roll of 7 or 11, and otherwise rolls until the first roll (the
_mark_) comes up again, which wins — double if the mark was 2 or 12 — or a 7 or 11 comes up,
which loses. The textbook version depends on the C library's `rand()` and on a person at the
keyboard. This project keeps the rules, the stakes, and the flow of the game, and makes every
game reproducible: the dice come from the portable generator of CONV-38 with a `--seed`, and the
player's responses can come from a file. The engineering focus is a _finite state machine_
whose every transition is observable, _re-prompting_ for invalid bets in a way that stays
aligned when the responses are scripted, and _deterministic simulation_ — the same seed and
responses give the same bytes on Linux, macOS, and Windows.

## Operational scope

| In scope                                                                                 | Out of scope                                                 |
| :--------------------------------------------------------------------------------------- | :----------------------------------------------------------- |
| Bankroll $500, table limit $250, bets of 1 … min(bankroll, 250) whole dollars            | Other stakes, fractional bets, side bets                     |
| First roll 7 or 11 wins; 2 or 12 sets a double mark; the mark wins, 7 or 11 loses        | Real casino craps rules (come-out craps, odds bets)          |
| Responses (play? and bets) read as tokens (CONV-32) from standard input or one `FILE`    | Several input files                                          |
| Refused bets explained on standard output and asked for again                            | Negotiating the table limit                                  |
| The CONV-38 generator, `--seed` (default 1), two draws per roll in a stated order        | The platform's own random-number generator, time-based seeds |
| A transcript of every roll and outcome, the bankroll after every round, a closing banner | Statistics over many games                                   |
| Optional prompts on standard error (`-p`, `--prompt`, CONV-36)                           | Prompts on standard output                                   |
| CRLF input and a trailing Ctrl-Z end-of-file marker (CONV-37)                            | Other legacy encodings                                       |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                        | Recovering after an unreadable response                      |
| `--help`, `--version`, CONV-13 usage errors                                              | Configuration files, environment variables                   |

## Learning objectives

1. Model a game as a finite state machine — play question, bet, first roll, point rolls,
   settlement — and make every transition visible in the output (FR-04 … FR-09).
2. Implement a pseudo-random generator exactly, derive die faces from it in a stated order, and
   test chance-driven code deterministically by choosing seeds (FR-03, FR-14).
3. Enforce business constraints (minimum, table limit, bankroll) with a re-prompt loop that
   keeps scripted responses aligned (FR-06).
4. Distinguish a refused but well-formed response (a game event) from malformed input (a fatal
   data error), and define what happens when the responses run out (FR-10, FR-11).
5. Produce identical bytes on every platform from integer arithmetic only, so a seed is a
   portable replay of a game (NFR-02).

## What is provided

| Path                   | Contents                                                                                                               |
| :--------------------- | :--------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                                                      |
| `specs/SRS.md`         | System requirements (FR-01 … FR-19, NFR-01 … NFR-08)                                                                   |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                                |
| `tests/fixtures/`      | Response files shared by both suites (`play.txt`, `once.txt`, `double.txt`, `broke.txt`, `refusals.txt`, `badbet.txt`) |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                 |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                    |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-dice`, with unit tests — including the generator's known values and
   a scripted round for every outcome, as NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-dice into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.
