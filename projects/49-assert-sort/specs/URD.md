<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-assert-sort](#user-requirements-document-urd--dp-assert-sort)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The textbook's array](#41-the-textbooks-array)
    - [4.2 Watching the invariant](#42-watching-the-invariant)
    - [4.3 An off-by-one bug](#43-an-off-by-one-bug)
    - [4.4 A bug that only shows later](#44-a-bug-that-only-shows-later)
    - [4.5 A harmless fault](#45-a-harmless-fault)
    - [4.6 A typo and an old file](#46-a-typo-and-an-old-file)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-assert-sort

| Field               | Value                                                                           |
| :------------------ | :------------------------------------------------------------------------------ |
| Document ID         | URD-49                                                                          |
| Project             | `49-assert-sort` — Formal Program Verification via Assertions & Loop Invariants |
| Product             | `dp-assert-sort`                                                                |
| Version             | 1.0.0                                                                           |
| Status              | Approved (pre-written by the curriculum)                                        |
| Successor documents | `SRS.md` (SRS-49), `user-manual.md`                                             |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-assert-sort` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-49), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-assert-sort` sorts a list of whole numbers with selection sort and checks, while it runs,
that the algorithm is doing what its proof says it does: after every pass the index it used is
inside the array, and the part of the array already processed is sorted and no larger than
anything still to come. A student can watch every check pass, or deliberately break one step
of the algorithm and see exactly which check catches it, in which pass, and why. A script gets
either correctly sorted numbers or a failure — never a wrong answer.

### 1.3 Scope

In scope: reading integers from the keyboard, a pipe, or a file; sorting them by selection
sort with the bounds assertion and the loop invariant checked after every pass; printing the
sorted numbers; an optional trace of the checks; injecting a chosen fault; reading data files
written on Windows or MS-DOS; reporting invalid numbers, failed assertions, and unreadable
files; help and version information.
Out of scope: other sorting algorithms, other kinds of data, writing files, random faults,
configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                        | Primary interest                                                           |
| :--- | :----------------- | :----------------------------------------------------------------- | :------------------------------------------------------------------------- |
| SH-1 | Student            | Studies loop invariants and assertions on Linux, macOS, or Windows | Seeing each check hold, and seeing a broken step caught                    |
| SH-2 | Instructor         | Uses the tool to demonstrate program verification                  | Faults that are exactly reproducible; diagnostics that explain the failure |
| SH-3 | Script author      | Sorts lists of integers in shell scripts                           | Predictable output bytes and exit statuses; no wrong results               |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice       | A complete, unambiguous specification                                      |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems         | Deterministic, byte-exact behavior                                         |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                             | Priority | Source     |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a script author, I want to give the tool a list of whole numbers and get them back in ascending order, one per line.                                                      | M        | SH-3       |
| UR-02 | As a student, I want the numbers sorted by selection sort exactly as the textbook describes it, so that I can follow the algorithm pass by pass.                             | M        | SH-1       |
| UR-03 | As an instructor, I want every pass to check that the index of the minimum lies inside the array and that the loop invariant holds, on the actual data.                      | M        | SH-2       |
| UR-04 | As a student, I want to see, when I ask for it, each invariant check that held, with the array as it stood, without changing the sorted output.                              | S        | SH-1       |
| UR-05 | As an instructor, I want to break one precisely defined step of the algorithm, in every pass or in one chosen pass, and get the same result every time.                      | M        | SH-2       |
| UR-06 | As a student, I want a failed check to tell me which assertion failed, in which pass, and which elements violate it.                                                         | M        | SH-1       |
| UR-07 | As a script author, I want a failed check to produce no sorted output and a non-zero exit status, so a wrong result is never mistaken for a right one.                       | M        | SH-3       |
| UR-08 | As a script author, I want to pipe numbers into the tool or name a file of numbers.                                                                                          | M        | SH-3       |
| UR-09 | As a script author, I want an invalid number reported with its position and a non-zero exit status, and a missing or unreadable file reported clearly.                       | M        | SH-3       |
| UR-10 | As a student, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                     | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status.                           | M        | SH-1, SH-3 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and a tool that follows the curriculum's common CLI conventions.                                    | M        | SH-5, SH-4 |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to sort a few thousand numbers quickly. | M        | SH-5       |
| UR-14 | As an instructor, I want the checks to be part of every build of the tool, not something a release configuration can switch off.                                             | M        | SH-2       |

## 4. Usage scenarios

### 4.1 The textbook's array

A student runs `echo 5 4 3 2 1 | dp-assert-sort` and sees `1` to `5`, one per line. Every
check held, and the exit status is 0. (UR-01, UR-02, UR-03)

### 4.2 Watching the invariant

The student adds `--trace` and sees, on standard error, one line per pass — for example
`pass 0: min_ind = 4 in bounds; a = 1 4 3 2 5; sorted(a, 0, 5) holds` — while the sorted
numbers on standard output are unchanged. (UR-04)

### 4.3 An off-by-one bug

The instructor runs `dp-assert-sort --fault=off-by-one textbook.txt`. In pass 0 the faulty
index is 5 in an array of 5 elements, and the tool reports
`assertion failed in pass 0: min_ind >= 0 && min_ind < n (min_ind = 5, n = 5)`, prints no
numbers, and exits with status 1. (UR-05, UR-06, UR-07)

### 4.4 A bug that only shows later

With `--fault=search-from-next`, passes 0 and 1 happen to produce correct results; in pass 2
the invariant check reports `sorted(a, 2, 5) (a[3] = 3 < a[2] = 4)`. (UR-05, UR-06)

### 4.5 A harmless fault

With `--fault=skip-swap:3` the swap of the last pass is omitted, but the minimum is already in
place, so every check holds and the numbers are sorted correctly: the checks report wrong
data, not wrong code. (UR-05)

### 4.6 A typo and an old file

A file contains `0x9` on line 3; the tool reports `bad.txt:3: invalid integer '0x9'` and sorts
nothing. A file from an MS-DOS machine with CRLF line endings and a final Ctrl-Z byte is read
exactly like any other. (UR-09, UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-assert-sort` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term           | Meaning                                                                                                                         |
| :------------- | :------------------------------------------------------------------------------------------------------------------------------ |
| Selection sort | Sorting by repeatedly finding the smallest remaining element and swapping it into the next position                             |
| Pass           | One step of selection sort that places one element; passes are numbered from 0                                                  |
| Assertion      | A condition the program checks while it runs; if it is false, the program reports it and stops                                  |
| Loop invariant | A condition that holds after every pass of a loop; for this tool, "a[0..i] is sorted and no later element is smaller than a[i]" |
| Fault          | A deliberate, precisely defined error injected into one step of the algorithm                                                   |
| Trace          | The optional lines that show each invariant check that held                                                                     |
| Exit status    | The integer a process returns to its caller; 0 means success                                                                    |
