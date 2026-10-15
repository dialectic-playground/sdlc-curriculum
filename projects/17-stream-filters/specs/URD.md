<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-average, dp-chk-sort](#user-requirements-document-urd--dp-average-dp-chk-sort)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Averaging readings](#41-averaging-readings)
    - [4.2 A check in a script](#42-a-check-in-a-script)
    - [4.3 Stopping early](#43-stopping-early)
    - [4.4 A typo](#44-a-typo)
    - [4.5 An old data file](#45-an-old-data-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-average, dp-chk-sort

| Field               | Value                                                            |
| :------------------ | :--------------------------------------------------------------- |
| Document ID         | URD-17                                                           |
| Project             | `17-stream-filters` — Stream Filtering & Monotonicity Validation |
| Products            | `dp-average`, `dp-chk-sort`                                      |
| Version             | 1.0.0                                                            |
| Status              | Approved (pre-written by the curriculum)                         |
| Successor documents | `SRS.md` (SRS-17), `user-manual.md`                              |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-average` and `dp-chk-sort` need, in their own
terms. It is the starting point for the Software Requirements Specification (SRS-17), which
turns each need into precise, testable system behavior.

### 1.2 Product vision

Two small tools for the middle of a pipeline. `dp-average` answers "what is the average of the
positive values in this stream?", skipping zeros and negative values such as error codes or
placeholders. `dp-chk-sort` answers "is this stream of integers in order?" — in words for a
person and in its exit status for a script — and gives its answer as soon as it sees the first
number out of place, without reading the rest of a possibly enormous stream. Both report a
typo in the data clearly instead of guessing.

### 1.3 Scope

In scope: reading numbers from the keyboard, a pipe, or a file until the end of the input (or,
for `dp-chk-sort`, until the first number out of order); averaging the positive real numbers;
checking that integers are in non-decreasing order; answering through the exit status;
reading data files written on Windows or MS-DOS; reporting invalid numbers and unreadable
files; help and version information.
Out of scope: other statistics (see `dp-stats`, Project 15), other sort orders, locating or
counting inversions, sorting, several input files, prompts, configuration files, and
environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                   | Primary interest                                                     |
| :--- | :----------------- | :------------------------------------------------------------ | :------------------------------------------------------------------- |
| SH-1 | Terminal user      | Runs the tools by hand on Linux, macOS, or Windows            | A clear one-line answer; helpful errors                              |
| SH-2 | Script author      | Uses the tools in shell scripts, pipelines, and CI checks     | Predictable output bytes and exit statuses; an answer usable in `if` |
| SH-3 | Data engineer      | Checks or summarizes very large streams                       | Early answers, constant memory                                       |
| SH-4 | Learner (assignee) | Implements the tools in a language repository of their choice | A complete, unambiguous specification                                |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems    | Deterministic, byte-exact behavior                                   |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                            | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- | :--------- |
| UR-01 | As a terminal user, I want the average of the numbers greater than zero in a stream, with zeros and negative numbers ignored.                                                               | M        | SH-1       |
| UR-02 | As a terminal user, I want a clear message, not an error or a division by zero, when the stream contains no positive number.                                                                | M        | SH-1       |
| UR-03 | As a script author, I want to know whether a stream of integers is in non-decreasing order, where equal neighbors are in order and an empty or one-number stream is sorted.                 | M        | SH-2       |
| UR-04 | As a data engineer, I want the order check to answer as soon as it reads the first number out of order, without reading the rest of the stream.                                             | M        | SH-3       |
| UR-05 | As a script author, I want the order check's answer in its exit status as well as in words, with failures distinguishable from "not sorted", so I can write `if dp-chk-sort file; then …`.  | M        | SH-2       |
| UR-06 | As a script author, I want to pipe numbers into either tool or name a file of numbers.                                                                                                      | M        | SH-2       |
| UR-07 | As a script author, I want an invalid number reported with its position and a non-zero exit status, and no misleading answer.                                                               | M        | SH-2       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                      | M        | SH-2       |
| UR-09 | As a terminal user, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                              | S        | SH-1       |
| UR-10 | As a script author, I want the printed average to have the same digits on every computer and in every implementation.                                                                       | M        | SH-2, SH-5 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query for each tool.                                                                                                        | M        | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                          | M        | SH-2       |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                            | M        | SH-5       |
| UR-14 | As a learner, I want the tools to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                       | M        | SH-4       |
| UR-15 | As a grader, I want the tools to build, install, and uninstall with standard commands, regardless of their implementation language, and to process large inputs quickly in constant memory. | M        | SH-3, SH-5 |

## 4. Usage scenarios

### 4.1 Averaging readings

A user runs `printf -- '-5.0 0.0 10.0 20.0' | dp-average` and sees `average = 15.000000`: the
negative reading and the zero were ignored. With only `-1.0 -10.0 0.0` the answer is
`no positive numbers read`. Both runs exit with status 0. (UR-01, UR-02)

### 4.2 A check in a script

A CI job runs `if dp-chk-sort ids.txt; then echo ok; fi`. With `1 3 5 5 9 12` the tool prints
`file is sorted` and exits with status 0; with `1 3 8 4 10` it prints `file is not sorted` and
exits with status 1. (UR-03, UR-05)

### 4.3 Stopping early

An engineer pipes a 50 GB export into `dp-chk-sort`. The fifth number is smaller than the
fourth: the tool answers `file is not sorted` at once and exits; it does not read, or wait
for, the rest of the stream, and whatever follows the fifth number is never examined.
(UR-04)

### 4.4 A typo

A file of readings contains `1/2` on its fourth line. `dp-average` prints no average, reports
`bad.txt:4: invalid number '1/2'`, and exits with status 1. A file of integers that contains
`3.5` before any inversion makes `dp-chk-sort` report `invalid integer '3.5'` and exit with
status 2, which a script cannot mistake for "not sorted". (UR-05, UR-07)

### 4.5 An old data file

A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. Both
tools read it exactly like a file with LF line endings. (UR-09)

### 4.6 Discovery and mistakes

A user runs `dp-chk-sort --help` to see how the exit status is used, and `dp-average a.txt
b.txt` is rejected because each tool reads one file. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as native executables or language-runtime launchers.   |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must not store the numbers they read: memory use must not grow with the length of the input.                   |

## 6. User acceptance criteria

The users will accept `dp-average` and `dp-chk-sort` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help texts exactly match the ones published in the user manual.

## 7. Glossary

| Term                 | Meaning                                                                                           |
| :------------------- | :------------------------------------------------------------------------------------------------ |
| Positive number      | A number greater than zero; zero and negative numbers are not positive                            |
| Non-decreasing order | Every integer is greater than or equal to the one before it                                       |
| Inversion            | An integer that is less than the integer immediately before it                                    |
| Short-circuit        | Stopping as soon as the answer is known, without reading the rest of the input                    |
| End of input         | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard        |
| Exit status          | The integer a process returns to its caller; 0 means success, and for `dp-chk-sort` also "sorted" |
