<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-sort-host, dp-sort-child](#user-requirements-document-urd--dp-sort-host-dp-sort-child)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Sorting a list](#41-sorting-a-list)
    - [4.2 Watching the conversation](#42-watching-the-conversation)
    - [4.3 Talking to the worker directly](#43-talking-to-the-worker-directly)
    - [4.4 Random data](#44-random-data)
    - [4.5 A typo](#45-a-typo)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-sort-host, dp-sort-child

| Field               | Value                                                              |
| :------------------ | :----------------------------------------------------------------- |
| Document ID         | URD-34                                                             |
| Project             | `34-parallel-sort` — Distributed Parallel Sorting & Stream Merging |
| Products            | `dp-sort-host`, `dp-sort-child`                                    |
| Version             | 1.0.0                                                              |
| Status              | Approved (pre-written by the curriculum)                           |
| Successor documents | `SRS.md` (SRS-34), `user-manual.md`                                |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-sort-host` and `dp-sort-child` need, in their own
terms. It is the starting point for the Software Requirements Specification (SRS-34), which
turns each need into precise, testable system behavior.

### 1.2 Product vision

`dp-sort-host` sorts a list of integers the way a small parallel computer would: a coordinator
keeps half of the work, hands the other half to a worker over a message channel, both sort at
the same time, and the coordinator merges the two sorted streams into one. The result is an
ordinary sorted list, but the user can also watch the conversation between host and worker,
message by message, and see exactly how the merge interleaves the two halves. The worker,
`dp-sort-child`, is a tool in its own right that speaks a simple, documented line protocol, so
it can be tried by hand, scripted, or reused.

### 1.3 Scope

In scope: reading integers from a file or standard input, or generating reproducible random
ones; splitting them between host and worker; concurrent sorting; merging; writing the sorted
list; an optional trace of messages and merge steps; the standalone worker; reporting invalid
data and unreadable files; help and version information.
Out of scope: more than one worker, workers on other machines, other sorting algorithms,
sorting anything but integers, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                              | Primary interest                                                                            |
| :--- | :----------------- | :----------------------------------------------------------------------- | :------------------------------------------------------------------------------------------ |
| SH-1 | Student            | Runs the tools to learn how message-passing concurrency and merging work | A visible, understandable exchange between host and worker                                  |
| SH-2 | Script author      | Sorts lists of integers in shell scripts and batch jobs                  | Correct sorted output, predictable bytes and exit statuses                                  |
| SH-3 | Integrator         | Reuses the worker in other pipelines or tests it on its own              | A fully documented protocol                                                                 |
| SH-4 | Learner (assignee) | Implements both tools in a language repository of their choice           | A complete, unambiguous specification of the protocol, the concurrency rules, and the merge |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems               | Deterministic, byte-exact behavior, even though the work is concurrent                      |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                       | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a script author, I want to give the tool a list of integers in a file or on standard input and get them back sorted, one per line.                                                  | M        | SH-2       |
| UR-02 | As a student, I want the work split between the host and a worker that sorts at the same time, half each, and the two results merged into one sorted list.                             | M        | SH-1       |
| UR-03 | As an integrator, I want the worker to be a separate tool with a documented line protocol, so I can run and test it on its own.                                                        | M        | SH-3       |
| UR-04 | As a student, I want to see, on request, every message exchanged with the worker and every step of the merge, in the same order every time.                                            | M        | SH-1       |
| UR-05 | As a student, I want to sort reproducible random data without preparing a file.                                                                                                        | S        | SH-1       |
| UR-06 | As a script author, I want the tool never to hang, lose, or duplicate a value, however the data is split.                                                                              | M        | SH-2       |
| UR-07 | As a script author, I want invalid data (a typo, a decimal point, a number too large, too many numbers) reported with its position and a non-zero exit status, and no partial result.  | M        | SH-2       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                 | M        | SH-2       |
| UR-09 | As a script author, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                         | S        | SH-2       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query for each tool.                                                                                                   | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                     | M        | SH-2       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                       | M        | SH-5       |
| UR-13 | As a learner, I want the tools to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                  | M        | SH-4       |
| UR-14 | As a grader, I want the tools to build, install, and uninstall with standard commands, regardless of their implementation language, and to sort tens of thousands of integers quickly. | M        | SH-5       |

## 4. Usage scenarios

### 4.1 Sorting a list

A script runs `dp-sort-host data.txt > sorted.txt`. The file `sorted.txt` holds the ten
integers of `data.txt` in non-decreasing order, one per line, and the exit status is 0.
(UR-01, UR-02)

### 4.2 Watching the conversation

A student runs `dp-sort-host --trace data.txt`. Standard error shows the host sending the
worker the size of its half and then its five numbers, and then the merge: each number the
worker sends back, and each number written, marked `from host` or `from child`. Running it
again gives exactly the same trace. (UR-02, UR-04)

### 4.3 Talking to the worker directly

An integrator types `dp-sort-child`, then `3`, `9`, `-1`, and `4`, each followed by Enter. As
soon as the third number is complete the worker answers `-1`, `4`, `9`, and exits without
waiting for more input. (UR-03)

### 4.4 Random data

A student runs `dp-sort-host --random=10 --trace` to see the algorithm on ten random numbers
without preparing a file; `--seed=42` gives a different, equally reproducible set. (UR-05)

### 4.5 A typo

A data file contains `4.5` on its third line. `dp-sort-host` reports
`bad.txt:3: invalid integer '4.5'`, writes nothing to standard output, and exits with status

1. (UR-07)

### 4.6 Discovery and mistakes

A user runs `dp-sort-host --help` and `dp-sort-child --help` to see the options, and
`dp-sort-host -r 5 data.txt` is rejected because random data and a file cannot be combined.
(UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                           |
| :--- | :------------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as native executables or language-runtime launchers.         |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets.       |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                        |
| UC-4 | Must behave identically whatever the user's locale or terminal settings, and whatever the number of processor cores. |

## 6. User acceptance criteria

The users will accept `dp-sort-host` and `dp-sort-child` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help texts exactly match those published in the user manual.

## 7. Glossary

| Term          | Meaning                                                                             |
| :------------ | :---------------------------------------------------------------------------------- |
| Host          | The coordinator, `dp-sort-host`: it splits the data, sorts its half, and merges     |
| Worker, child | The concurrent unit that sorts the other half; `dp-sort-child` as a standalone tool |
| Channel       | A one-way stream of messages between host and worker                                |
| Message       | One line holding one integer                                                        |
| Request       | What the host sends the worker: the number of values, then the values               |
| Reply         | What the worker sends back: the values, sorted                                      |
| Merge         | Combining two sorted lists into one sorted list in a single pass                    |
| Deadlock      | A state in which host and worker each wait for the other forever                    |
| Exit status   | The integer a process returns to its caller; 0 means success                        |
