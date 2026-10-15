<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 52 — Object-Oriented Spacecraft Domain Modeling (`dp-ship`)](#project-52--object-oriented-spacecraft-domain-modeling-dp-ship)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 52 — Object-Oriented Spacecraft Domain Modeling (`dp-ship`)

> Model spacecraft as encapsulated objects and report their basics and trip times, the way a
> professional tool would: the textbook scenario by default, a fully specified command script
> for anything else, exact `%g`-style number formatting in every language, precise
> diagnostics, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 52 is adapted from §11.5 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_:
the book's first C++ example, a spacecraft class with private data, a default and a full
constructor, a velocity adjustment that never goes below zero, and a short scenario that prints
the ships' basics and a trip time. This project keeps the class, the scenario, and the report
wording, and turns the scenario into a tool: without arguments it replays the textbook, and
with a script it creates and adjusts any number of ships. The engineering focus is twofold: an
_object design_ requirement stated without reference to any language (encapsulation and
constructors, checked by design review), and _number formatting_ that does not depend on a
language's default conversion of floating-point values to text — the textbook's own trip time,
printed by C++ stream defaults, is reproduced here by an explicit rule (and corrected: the
section's description misquotes it).

## Operational scope

| In scope                                                                         | Out of scope                                                          |
| :------------------------------------------------------------------------------- | :-------------------------------------------------------------------- |
| The textbook scenario with no operand (FR-07)                                    | Other built-in scenarios                                              |
| Command scripts from one `FILE` operand (`-` is standard input)                  | Several scripts, interactive prompting                                |
| `new` (default or full construction), `adjust`, `print`, `trip`                  | Changing name, mass, distance, or capacity; deleting ships            |
| Velocity clamped at 0; trip time = distance / velocity, guarded at zero velocity | Units other than kg, km, km/h                                         |
| Numbers written as `GEN(x, 6)` (CONV-35)                                         | Other precisions, localized number formats                            |
| CRLF scripts, comments, and a trailing Ctrl-Z end-of-file marker (CONV-37)       | Other legacy encodings                                                |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                | Recovering after an invalid line                                      |
| `--help`, `--version`, CONV-13 usage errors                                      | Saving ships between runs, configuration files, environment variables |

## Learning objectives

1. Design a domain object that encapsulates its state, with default and full construction,
   a mutator that enforces an invariant (velocity ≥ 0), and a derived property (trip time)
   (FR-02 … FR-04, NFR-05).
2. Turn a fixed demonstration into a tool by mapping a small command language one to one onto
   an object's operations (FR-08, FR-09).
3. Format floating-point numbers by an exact, documented rule instead of a language default,
   and verify it at its boundaries: exponent switch, ties, subnormals, negative zero (FR-05,
   NFR-02).
4. Guard a derived computation against division by zero and overflow without producing
   infinities or NaNs in a report (FR-04, FR-06).
5. Validate a line-oriented script with a fixed order of checks, so every error is reported
   the same way by every implementation (FR-10).

## What is provided

| Path                   | Contents                                                                                |
| :--------------------- | :-------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-15)                                                       |
| `specs/SRS.md`         | System requirements (FR-01 … FR-15, NFR-01 … NFR-08)                                    |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                 |
| `tests/fixtures/`      | Scripts shared by both suites (`fleet.txt`, `clamp.txt`, `bad.txt`)                     |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                  |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention) |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates     |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md` — the HLD must show the
   spacecraft abstraction and how NFR-05's encapsulation is achieved in your language.
2. An implementation of `dp-ship`, with unit tests — including the spacecraft and `GEN` tests
   that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-ship into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, a design review confirms NFR-05, and every RTM row is
_Verified_.
