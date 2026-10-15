<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 34 — Distributed Parallel Sorting & Stream Merging (`dp-sort-host`, `dp-sort-child`)](#project-34--distributed-parallel-sorting--stream-merging-dp-sort-host-dp-sort-child)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 34 — Distributed Parallel Sorting & Stream Merging (`dp-sort-host`, `dp-sort-child`)

> Sort integers the way a small parallel machine does — a host keeps half, a concurrent
> worker sorts the other half behind a line protocol, and a pipelined two-way merge joins the
> streams — with deadlock freedom by design, a message trace that is deterministic although
> the work is concurrent, and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 34 is adapted from §6.6 of Johnsonbaugh & Kalin, _Applications Programming in ANSI
C_: a host program on a transputer network sends a child program the size and the elements
of half an array over a CSP channel, both halves are sorted with selection sort at the same
time, and the host merges its sorted half with the stream the child sends back. Transputer
channels exist on none of today's platforms, so this project specifies the channels as a
small line protocol and makes the worker a tool of its own, `dp-sort-child`, that can be run
and tested by hand. `dp-sort-host` may run that worker as a thread, a process, or the
`dp-sort-child` executable; the engineering focus is the part that does not change with the
choice — an ordering of sends, receives, and closes that cannot deadlock on any pipe size, a
merge whose every step is specified (including ties), and a `--trace` that turns a concurrent
computation into a byte-exact, testable record.

## Operational scope

| In scope                                                                     | Out of scope                                |
| :--------------------------------------------------------------------------- | :------------------------------------------ |
| Up to 100000 integer tokens from a file or standard input (CONV-32, CONV-33) | Real numbers, strings, keys with records    |
| Generated data with `-r`, `--random` and `--seed` (CONV-38)                  | Other distributions                         |
| Split ⌊_N_/2⌋ to the host, the rest to one concurrent worker                 | Several workers, workers on other machines  |
| A fully specified worker protocol; `dp-sort-child` serves it standalone      | Binary or framed protocols, network sockets |
| Worker as a thread, a process, or `dp-sort-child` (same observable bytes)    | Shared-memory parallel sorting              |
| Selection sort on both sides; linear two-way merge, host first on ties       | Other sorting algorithms                    |
| Deadlock-free ordering (FR-10); worker failure detected, never a hang        | Recovering from a failed worker             |
| Deterministic `--trace` of messages and merge steps on standard error        | Timing or profiling information             |
| CRLF input, trailing Ctrl-Z (CONV-37); CONV-34 data diagnostics              | Partial output on invalid data              |
| `--help`, `--version`, CONV-13 usage errors for both tools                   | Configuration files, environment variables  |

## Learning objectives

1. Partition a workload between a coordinator and a concurrent worker that communicate only
   through messages, with no shared state (FR-04, FR-09).
2. Design a line protocol precisely — exact bytes to send, tolerant parsing on receipt, and no
   reading past the end of a request — and implement it once for two tools (FR-05, FR-06,
   NFR-05).
3. Reason about deadlock: order writes, flushes, closes, and reads so that no pipe capacity
   and no scheduling can make host and worker wait for each other forever (FR-10, NFR-02).
4. Implement the pipelined two-way merge in linear time with a precise tie rule, consuming one
   stream lazily (FR-11).
5. Make a concurrent program testable byte for byte by tracing events whose order depends only
   on the data (FR-12).

## What is provided

| Path                   | Contents                                                                                        |
| :--------------------- | :---------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-14)                                                               |
| `specs/SRS.md`         | System requirements (FR-01 … FR-19, NFR-01 … NFR-08)                                            |
| `specs/user-manual.md` | Complete user manual for both tools, including both normative help texts                        |
| `tests/fixtures/`      | Input files shared by both suites: `data.txt`, `odd.txt`, `request.txt`, `bad.txt`, `short.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                          |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)         |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates             |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the worker module shared by both tools, the chosen kind of worker, and an argument that the
   design meets the ordering of FR-10.
2. Implementations of `dp-sort-host` and `dp-sort-child`, with unit tests — including the
   merge tests with an in-memory reply stream that NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-sort-host and dp-sort-child into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, and every RTM row is _Verified_.
