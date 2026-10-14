# Project 20 — Modular Procedural Decomposition & Evaluation (`dp-bargraph2`, `dp-grade`)

> Rebuild the Project 16 bar graph from two reusable procedures without changing a single
> output byte, and write an interactive pass/fail grader whose borderline decisions are exact
> and identical on every processor, compiler, and operating system.

## Purpose

Project 20 is adapted from §4.1 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*,
the section that introduces functions. It has two tools. `dp-bargraph2` is `dp-bargraph`
(Project 16) refactored into a title-echoing procedure and a bar-drawing procedure: its
specification is "the same bytes as before", so the refactoring is checked by the same kind of
black-box tests, and its structure by design review. `dp-grade` is an answer-driven dialog that
reads two exam scores and a weight and decides pass or fail with a strict threshold of 7. A
naive floating-point implementation gets the borderline cases wrong — with a weight of 0.2,
scores of 7 and 7 average to 7.000000000000001 — so the specification fixes the weight's
precision and decides in integer arithmetic. The tool also has to work both at a keyboard,
with prompts on standard error, and on a prepared file.

## Operational scope

| In scope | Out of scope |
| :-- | :-- |
| `dp-bargraph2`: the exact behavior of `dp-bargraph` (Project 16) | Any change to the bar-graph format |
| A required decomposition into `echo_line`- and `print_stars`-style procedures | Prescribing a language or a module layout |
| `dp-grade`: rounds of answer, mid term, final, weight, read as tokens | Student names, more than two exams, letter grades other than P/F |
| Scores 0–10, weight 0–1 to the nearest 0.001, pass when the average exceeds 7 | Other scales and thresholds; printing the average |
| Exact integer decision rule (FR-11) | Binary floating-point comparison with 7.0 |
| `-p`, `--prompt` with the textbook's prompts on standard error (CONV-36) | Prompts on standard output |
| CRLF input, trailing Ctrl-Z (CONV-37); CONV-34 data diagnostics | Recovering after a data error |
| `--help`, `--version`, CONV-13 usage errors for both tools | Colors, line editing |

## Learning objectives

1. Refactor a working program into single-responsibility procedures while proving, with
   black-box tests, that its observable behavior is unchanged (FR-01, NFR-05).
2. Design a pure decision function and test it at and around its threshold (FR-11, NFR-06).
3. Recognize where binary floating point gives the wrong answer for decimal data, and replace
   it with a precisely specified exact computation (FR-10, FR-11, NFR-02).
4. Implement an incremental tokenizer that serves a keyboard dialog and a file equally,
   including prompts, flushing, and the end of input in the middle of a round (FR-07, FR-08,
   FR-13).
5. Share command-line handling between two tools of one project (NFR-05).

## What is provided

| Path | Contents |
| :-- | :-- |
| `specs/URD.md` | User requirements (UR-01 … UR-17) |
| `specs/SRS.md` | System requirements (FR-01 … FR-19, NFR-01 … NFR-08) |
| `specs/user-manual.md` | Complete user manual for both tools, including both normative help texts |
| `tests/fixtures/` | Input files shared by both suites: `bargraph.in` (from the textbook's companion disk), `edge.txt`, `readme-grades.txt`, `stop.txt`, `weights.txt`, `bad-score.txt`, `cut-record.txt` |
| `tests/public/` | 10 visible black-box tests with exact expected outputs |
| `tests/private/` | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/` | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the procedures that NFR-05 requires.
2. Implementations of `dp-bargraph2` and `dp-grade`, with unit tests — including every row of
   the grade table in FR-11.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-bargraph2 and dp-grade into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is *Verified*.
