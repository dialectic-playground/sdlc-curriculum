<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-taxes](#user-requirements-document-urd--dp-taxes)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the counter](#41-at-the-counter)
    - [4.2 A batch in a pipeline](#42-a-batch-in-a-pipeline)
    - [4.3 A large income](#43-a-large-income)
    - [4.4 A typo](#44-a-typo)
    - [4.5 An old data file](#45-an-old-data-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-taxes

| Field               | Value                                                       |
| :------------------ | :---------------------------------------------------------- |
| Document ID         | URD-13                                                      |
| Project             | `13-taxes` — Stream-Based Progressive Income Tax Calculator |
| Product             | `dp-taxes`                                                  |
| Version             | 1.0.0                                                       |
| Status              | Approved (pre-written by the curriculum)                    |
| Successor documents | `SRS.md` (SRS-13), `user-manual.md`                         |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-taxes` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-13), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-taxes` computes the income tax due under a simple two-bracket rule: incomes below 6000
greenbacks are taxed at 30%, all others at 60%. A clerk can type incomes one after another and
see each tax immediately; a script can pipe in thousands of incomes and get the same report.
The answers are exact for every income, however large, and a mistyped income is reported
clearly instead of producing nonsense.

### 1.3 Scope

In scope: reading incomes from the keyboard, a pipe, or a file until the end of the input;
computing and printing the tax on each; optional prompts; reading data files written on
Windows or MS-DOS; reporting invalid incomes and unreadable files; help and version
information.
Out of scope: other tax schedules, fractional amounts, negative incomes, totals or other
summaries, writing files (see `dp-taxes-file`, Project 14), configuration files, and
environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                             | Primary interest                                                   |
| :--- | :----------------- | :---------------------------------------------------------------------- | :----------------------------------------------------------------- |
| SH-1 | Tax clerk          | Types incomes by hand on Linux, macOS, or Windows                       | An immediate answer for each income; clear prompts; helpful errors |
| SH-2 | Script author      | Pipes lists of incomes through the tool in shell scripts and batch jobs | Predictable output bytes and exit statuses; exact results          |
| SH-3 | Auditor            | Checks that the published rule was applied                              | Exact, documented arithmetic with no rounding surprises            |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice            | A complete, unambiguous specification                              |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems              | Deterministic, byte-exact behavior                                 |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                  | Priority | Source     |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a tax clerk, I want to enter any number of incomes and get the tax on each one, until I signal the end of the input.                                                                                           | M        | SH-1       |
| UR-02 | As an auditor, I want the tax to be 30% of an income below 6000 greenbacks and 60% of any other income, rounded down to a whole number of greenbacks, exactly, for every income.                                  | M        | SH-3       |
| UR-03 | As a script author, I want each result to repeat the income it belongs to, so the report can be read without the input beside it.                                                                                 | M        | SH-2       |
| UR-04 | As a script author, I want to pipe incomes into the tool or name a file of incomes, so I can process data I already have.                                                                                         | M        | SH-2       |
| UR-05 | As a tax clerk, I want to see each tax as soon as I have typed the income, not only at the end.                                                                                                                   | M        | SH-1       |
| UR-06 | As a tax clerk, I want the tool to ask for each income when I request it, without the prompts appearing in the report I save.                                                                                     | S        | SH-1       |
| UR-07 | As a script author, I want an invalid income (a typo, a decimal point, a negative amount, a number too large) reported with its position and a non-zero exit status, while the results already produced are kept. | M        | SH-2       |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                                            | M        | SH-2       |
| UR-09 | As a tax clerk, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                        | S        | SH-1       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                            | M        | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                | M        | SH-2       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                                                  | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                                              | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large inputs quickly.                                             | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the counter

A clerk runs `dp-taxes --prompt`, sees `Enter income:types `5000`and Enter, and at once
sees`Income = 5000 greenbacks`and`Tax = 1500 greenbacks`, followed by the next prompt. After
the last income the clerk presses Ctrl-D (Ctrl-Z then Enter on Windows) and the tool exits with
status 0. (UR-01, UR-02, UR-03, UR-05, UR-06)

### 4.2 A batch in a pipeline

A script runs `extract-incomes | dp-taxes > taxes.txt`. The file holds two lines per income,
in input order, and nothing else. (UR-03, UR-04)

### 4.3 A large income

An auditor enters `9223372036854775807` and receives the exact tax `5534023222112865484`, not
an approximation. (UR-02)

### 4.4 A typo

A data file contains `12,000` on its third line. The tool prints the results for the first two
incomes, then reports `bad.txt:3: invalid integer '12,000'` and exits with status 1. (UR-07)

### 4.5 An old data file

A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like a file with LF line endings. (UR-09)

### 4.6 Discovery and mistakes

A user runs `dp-taxes --help` to see the options, and `dp-taxes a.txt b.txt` is rejected
because the tool reads one file. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must not wait for the end of the input before answering.                           |

## 6. User acceptance criteria

The users will accept `dp-taxes` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term         | Meaning                                                                                    |
| :----------- | :----------------------------------------------------------------------------------------- |
| Greenback    | The unit of currency of the textbook example; incomes and taxes are whole greenbacks       |
| Income       | A whole, non-negative number of greenbacks                                                 |
| Bracket      | The income range that decides the rate: below 6000 (30%) or 6000 and above (60%)           |
| Record       | The two report lines printed for one income                                                |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status  | The integer a process returns to its caller; 0 means success                               |
