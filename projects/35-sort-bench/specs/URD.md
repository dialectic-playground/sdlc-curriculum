<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-sort-bench](#user-requirements-document-urd--dp-sort-bench)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The textbook experiment](#41-the-textbook-experiment)
    - [4.2 A quick experiment](#42-a-quick-experiment)
    - [4.3 The same numbers everywhere](#43-the-same-numbers-everywhere)
    - [4.4 Real time](#44-real-time)
    - [4.5 Discovery and mistakes](#45-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-sort-bench

| Field               | Value                                                      |
| :------------------ | :--------------------------------------------------------- |
| Document ID         | URD-35                                                     |
| Project             | `35-sort-bench` — Empirical Algorithm Runtime Benchmarking |
| Product             | `dp-sort-bench`                                            |
| Version             | 1.0.0                                                      |
| Status              | Approved (pre-written by the curriculum)                   |
| Successor documents | `SRS.md` (SRS-35), `user-manual.md`                        |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-sort-bench` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-35), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-sort-bench` lets a student _see_ the difference between a quadratic and an _N_ log _N_
sorting algorithm. It sorts the same random arrays of growing size with selection sort and with
quicksort and reports how much work each did: the number of comparisons and swaps, which are
the same on every computer, and — when asked — the time each sort took on this computer.
Doubling the array size quadruples the work of selection sort but only about doubles that of
quicksort, and the report makes that visible in a form that can be checked exactly.

### 1.3 Scope

In scope: generating reproducible random arrays of chosen sizes, sorting copies of each with
the two algorithms, counting their comparisons and swaps, checking that the results are sorted,
optionally timing each sort, help and version information, and clear usage errors.
Out of scope: reading arrays from files, other algorithms, repeated runs and statistics over
timings, charts, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                  | Primary interest                                                        |
| :--- | :----------------- | :--------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| SH-1 | Student            | Runs the benchmark by hand to compare algorithms on Linux, macOS, or Windows | A clear report that shows the growth of each algorithm                  |
| SH-2 | Instructor         | Uses the report in class and in exercises                                    | The same numbers on every student's machine; real timings on demand     |
| SH-3 | Script author      | Runs the tool from scripts and CI jobs                                       | Predictable output bytes and exit statuses                              |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                 | A complete, unambiguous specification of both algorithms and the counts |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                   | Deterministic, byte-exact behavior                                      |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                    | Priority | Source     |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to run the benchmark with no arguments and see the results for arrays of 1000, 2000, and 4000 elements, as in the textbook.                                    | M        | SH-1       |
| UR-02 | As a student, I want to choose the array sizes myself, so I can explore smaller or larger arrays.                                                                                   | M        | SH-1       |
| UR-03 | As an instructor, I want both algorithms to sort copies of the same random array, and the arrays to be reproducible from a seed I choose, so the comparison is fair and repeatable. | M        | SH-2       |
| UR-04 | As a learner, I want the two algorithms specified step by step, so my implementation does exactly the work the specification describes.                                             | M        | SH-4       |
| UR-05 | As an instructor, I want the default report to be identical on every machine, so students can compare their results with mine.                                                      | M        | SH-2       |
| UR-06 | As a student, I want to see the number of comparisons and swaps each sort made, so I can relate the work to *n*² and _n_ log _n_.                                                   | M        | SH-1       |
| UR-07 | As a student, I want the tool to confirm that each sort's result is correctly sorted, so a fast but wrong sort is never mistaken for a good one.                                    | M        | SH-1       |
| UR-08 | As a student, I want to see, when I ask for it, how long each sort took, measured with an accurate clock.                                                                           | S        | SH-1       |
| UR-09 | As a terminal user, I want a built-in help screen and a version query.                                                                                                              | M        | SH-1, SH-3 |
| UR-10 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                  | M        | SH-3       |
| UR-11 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                    | M        | SH-5       |
| UR-12 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                | M        | SH-4       |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to finish the default benchmark quickly.       | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The textbook experiment

A student runs `dp-sort-bench`. For each of the sizes 1000, 2000, and 4000 the report shows
selection sort's comparisons growing from 499500 to 1999000 to 7998000 — four times as many
each time — while quicksort's grow only about twice. Every result is marked `Sorted = yes`.
(UR-01, UR-03, UR-06, UR-07)

### 4.2 A quick experiment

The student runs `dp-sort-bench --sizes=10,20,40` and gets the same kind of report at once,
small enough to follow the algorithms by hand. (UR-02, UR-04)

### 4.3 The same numbers everywhere

The instructor runs `dp-sort-bench --seed=7 -s 100` on Linux, a student on Windows; both
reports are byte for byte the same. (UR-03, UR-05, UR-11)

### 4.4 Real time

The student runs `dp-sort-bench --time` and sees, in addition, a `Time = … seconds` line for
each sort, measured on this machine. (UR-08)

### 4.5 Discovery and mistakes

A user runs `dp-sort-bench --help` to see the options. `dp-sort-bench --sizes=10,,20` is
rejected with a message naming the invalid list, and nothing is sorted. (UR-09, UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-sort-bench` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term            | Meaning                                                                                    |
| :-------------- | :----------------------------------------------------------------------------------------- |
| Selection sort  | A quadratic sort that repeatedly moves the smallest remaining element to the front         |
| Quicksort       | A divide-and-conquer sort that partitions around a pivot element; _n_ log _n_ on average   |
| Comparison      | One check of the order of two array elements                                               |
| Swap            | One exchange of two array elements at different positions                                  |
| Seed            | The number that determines the sequence of random arrays                                   |
| Monotonic clock | A clock that only moves forward at a steady rate, unaffected by changes to the time of day |
| Exit status     | The integer a process returns to its caller; 0 means success                               |
