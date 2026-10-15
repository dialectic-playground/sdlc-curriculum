<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-taxes-file](#user-requirements-document-urd--dp-taxes-file)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The nightly run](#41-the-nightly-run)
    - [4.2 Explicit files and pipelines](#42-explicit-files-and-pipelines)
    - [4.3 A typo in the data](#43-a-typo-in-the-data)
    - [4.4 A missing input](#44-a-missing-input)
    - [4.5 A report that cannot be written](#45-a-report-that-cannot-be-written)
    - [4.6 No incomes this time](#46-no-incomes-this-time)
    - [4.7 Discovery and mistakes](#47-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-taxes-file

| Field               | Value                                                                |
| :------------------ | :------------------------------------------------------------------- |
| Document ID         | URD-14                                                               |
| Project             | `14-taxes-file` — Batch File-Based Progressive Income Tax Calculator |
| Product             | `dp-taxes-file`                                                      |
| Version             | 1.0.0                                                                |
| Status              | Approved (pre-written by the curriculum)                             |
| Successor documents | `SRS.md` (SRS-14), `user-manual.md`                                  |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-taxes-file` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-14), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-taxes-file` is the batch version of the tax calculator `dp-taxes` (Project 13). An operator
drops a file of incomes, `incomes.dat`, into a working directory, runs the tool with no
arguments, and finds the tax report in `out.dat`. The rule is the same two-bracket rule, with
exact results. A bad input never destroys the previous report: if anything is wrong with the
input, the report file is left exactly as it was.

### 1.3 Scope

In scope: reading incomes from a file (by default `incomes.dat`) or standard input; writing the
tax report to a file (by default `out.dat`), replacing its contents, or to standard output;
reading data files written on Windows or MS-DOS; reporting invalid incomes and file problems;
help and version information.
Out of scope: interactive use and prompts (see `dp-taxes`, Project 13), several input files,
appending to or backing up the report, other tax schedules, negative incomes, configuration
files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                                    | Primary interest                                                               |
| :--- | :----------------- | :--------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------- |
| SH-1 | Batch operator     | Runs the tool in a working directory, by hand or from a scheduler, on Linux, macOS, or Windows | Fixed default file names; a report that is either complete or untouched        |
| SH-2 | Script author      | Calls the tool from scripts with explicit file names, or in a pipeline                         | Predictable output bytes and exit statuses; standard input and output as files |
| SH-3 | Auditor            | Checks that the published rule was applied                                                     | Exact, documented arithmetic with no rounding surprises                        |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                                   | A complete, unambiguous specification                                          |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                                     | Deterministic, byte-exact behavior that tests can observe                      |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                   | Priority | Source     |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a batch operator, I want to run the tool with no arguments and have it read `incomes.dat` and write `out.dat` in the current directory.                                         | M        | SH-1       |
| UR-02 | As a script author, I want to choose the input file and the report file, and to use standard input and standard output instead of files.                                           | M        | SH-2       |
| UR-03 | As an auditor, I want the tax to be 30% of an income below 6000 greenbacks and 60% of any other income, rounded down to a whole number of greenbacks, exactly, for every income.   | M        | SH-3       |
| UR-04 | As an auditor, I want the report to list each income with its tax, in input order, in the same format as `dp-taxes`.                                                               | M        | SH-3       |
| UR-05 | As a batch operator, I want the report file to be replaced completely by each successful run, and to be created even if there are no incomes.                                      | M        | SH-1       |
| UR-06 | As a batch operator, I want a bad input (an invalid income, or a missing or unreadable file) to leave the existing report file untouched, and to be told what was wrong and where. | M        | SH-1       |
| UR-07 | As a script author, I want every failure to give a clear message and a non-zero exit status.                                                                                       | M        | SH-2       |
| UR-08 | As a batch operator, I want to be told clearly when the report cannot be written, for example because the directory does not exist.                                                | M        | SH-1       |
| UR-09 | As a batch operator, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                    | S        | SH-1       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                             | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, without any file being touched.                                                 | M        | SH-2       |
| UR-12 | As a grader, I want identical report bytes on Linux, macOS, and Windows, whether the report goes to a file or to standard output.                                                  | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                               | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large files quickly.               | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The nightly run

An operator's directory holds `incomes.dat` with the incomes `4500`, `6000`, and `12000`. The
operator runs `dp-taxes-file`; nothing is printed, the exit status is 0, and `out.dat` holds
six lines, from `Income = 4500 greenbacks` to `Tax = 7200 greenbacks`. (UR-01, UR-03, UR-04)

### 4.2 Explicit files and pipelines

A script runs `dp-taxes-file -i 2026-q3.dat -o 2026-q3.rpt`, and another runs
`extract | dp-taxes-file -i - -o - | archive`. (UR-02)

### 4.3 A typo in the data

`incomes.dat` contains `12,000` on line 3. The tool reports
`dp-taxes-file: incomes.dat:3: invalid integer '12,000'` and exits with status 1. Yesterday's
`out.dat` is unchanged. (UR-06, UR-07)

### 4.4 A missing input

The operator runs the tool in the wrong directory. It reports
`dp-taxes-file: incomes.dat: No such file or directory`, exits with status 1, and creates no
`out.dat`. (UR-06, UR-07)

### 4.5 A report that cannot be written

`dp-taxes-file -o reports/out.dat` is run where `reports` does not exist. The tool reports
`dp-taxes-file: reports/out.dat: No such file or directory` and exits with status 1. (UR-08)

### 4.6 No incomes this time

`incomes.dat` is empty. The run succeeds and `out.dat` becomes an empty file. (UR-05)

### 4.7 Discovery and mistakes

A user runs `dp-taxes-file --help` to see the options. `dp-taxes-file incomes.dat` is rejected,
because file names are given with `-i` and `-o`, and no file is read or written. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must write the report with the same bytes on every platform; no text-mode newline conversion.                  |

## 6. User acceptance criteria

The users will accept `dp-taxes-file` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term        | Meaning                                                                              |
| :---------- | :----------------------------------------------------------------------------------- |
| Greenback   | The unit of currency of the textbook example; incomes and taxes are whole greenbacks |
| Income      | A whole, non-negative number of greenbacks                                           |
| Bracket     | The income range that decides the rate: below 6000 (30%) or 6000 and above (60%)     |
| Report      | The two lines per income that the tool writes, in input order                        |
| Report file | The file the report is written to: `out.dat` unless another is chosen                |
| Exit status | The integer a process returns to its caller; 0 means success                         |
