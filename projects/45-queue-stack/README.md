<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 45 — Comparative Queue & Stack ADT Implementations (`dp-queue1`, `dp-queue2`, `dp-stack1`, `dp-stack2`)](#project-45--comparative-queue--stack-adt-implementations-dp-queue1-dp-queue2-dp-stack1-dp-stack2)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 45 — Comparative Queue & Stack ADT Implementations (`dp-queue1`, `dp-queue2`, `dp-stack1`, `dp-stack2`)

> Implement a FIFO queue of bank customers and a LIFO stack of cafeteria trays twice each — on
> a fixed array of 100 places and on a linked list — behind one command dialog, so that the
> array and linked tools are indistinguishable from the outside until the array is full, with
> exact money amounts and byte-identical output on Linux, macOS, and Windows.

## Purpose

Project 45 is adapted from §10.4 of Johnsonbaugh & Kalin, _Applications Programming in ANSI C_,
which implements the queue and the stack as abstract data types, each in two ways. Here they
become four tools that share one command dialog: `1` inserts (pushes) a record, `2` removes
(pops) one, `3` displays the contents, `0` quits. `dp-queue1` keeps its customers in a
circular array of exactly 100 places whose indices wrap around; `dp-queue2` keeps them in a
linked list with front and rear references; `dp-stack1` keeps its trays in an array of exactly
100 places; `dp-stack2` in a linked list whose top node links to the one below. The central
requirement is _substitutability_: for the same commands, the array tool and the linked tool of
a kind write the same bytes, until the array tool runs out of room and says `QUEUE FULL` or
`STACK FULL`. The tests check this with fixtures of more than 100 operations, including a
queue whose indices wrap around the end of the array. Balances are exact decimal amounts in
cents, never binary floating point.

## Operational scope

| In scope                                                                                        | Out of scope                                  |
| :---------------------------------------------------------------------------------------------- | :-------------------------------------------- |
| Queue of customers {last name, first name, account number, balance}; stack of trays {color, id} | Other record types, updating records in place |
| Circular array of capacity 100 (`dp-queue1`), array of capacity 100 (`dp-stack1`)               | Growing arrays, other capacities              |
| Linked queue with front and rear references (`dp-queue2`), linked stack (`dp-stack2`)           | Doubly linked lists, deques, priority queues  |
| Commands 1 insert/push, 2 remove/pop, 3 display, 0 quit, read as tokens (CONV-32)               | Command words, undo, searching                |
| `QUEUE FULL`, `QUEUE EMPTY`, `STACK FULL`, `STACK EMPTY` as results on standard output          | Treating them as tool failures                |
| Balances with at most two decimal places, kept exactly in cents                                 | Currencies, interest, binary floating point   |
| `-p`, `--prompt` with a menu prompt and a record prompt on standard error (CONV-36)             | Prompts on standard output                    |
| Standard input or one `FILE` operand; CRLF input and a trailing Ctrl-Z (CONV-37)                | Saving the queue or stack between runs        |
| Data diagnostics with line numbers (CONV-34), CONV-16 file errors                               | Recovering after a data error                 |
| ADT design requirements checked by design review; `--help`, `--version`, CONV-13 usage errors   | Configuration files, environment variables    |

## Learning objectives

1. Specify a queue and a stack as abstract data types and implement each twice, so that a
   single command driver works unchanged with either implementation (FR-12, NFR-05).
2. Manage a circular array correctly: indices that advance modulo 100, the distinction between
   empty and full, and order preserved across the wrap-around (FR-08 … FR-10, NFR-05).
3. Build linked queues and stacks with constant-time operations: insertion at the rear and
   removal at the front of a queue, push and pop at the top of a stack (NFR-05).
4. Prove substitutability with black-box tests that run two implementations on the same long
   command sequence, and explain the one place they are allowed to differ (FR-12).
5. Represent money exactly as an integer number of cents, with a precise input grammar and
   output format (FR-06).
6. Write an incremental command dialog that streams its results, prompts on standard error,
   and stops cleanly at the first malformed command (FR-03, FR-04, FR-13, FR-14).

## What is provided

| Path                   | Contents                                                                                                                                                     |
| :--------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-16)                                                                                                                            |
| `specs/SRS.md`         | System requirements (FR-01 … FR-19, NFR-01 … NFR-08)                                                                                                         |
| `specs/user-manual.md` | Complete user manual for the four tools, including the four normative help texts                                                                             |
| `tests/fixtures/`      | Input files shared by both suites: `customers.txt`, `trays.txt`, `full-queue.txt` and `full-stack.txt` (101 insertions each), `empty.txt`, `bad-command.txt` |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                                                                       |
| `tests/private/`       | 10 hidden black-box tests and their fixtures (used by grading/CI; unseen by convention)                                                                      |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                                                                          |

The textbook section has no companion data file; every fixture was written for this project.

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`, with the HLD showing
   the queue and stack interfaces, their four implementations, and the shared command driver
   that NFR-05 requires.
2. Implementations of `dp-queue1`, `dp-queue2`, `dp-stack1`, and `dp-stack2`, with unit tests —
   including the wrap-around and capacity tests and the array-versus-linked comparison that
   NFR-06 requires.
3. The project `Makefile` with every `DP_*` hook filled in for your toolchain, building and
   installing all four executables (see `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-queue1, dp-queue2, dp-stack1, and dp-stack2 into BIN_DIR
make test           # unit tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, `make lint` is clean, the design review confirms NFR-05, and every RTM row is
_Verified_.
