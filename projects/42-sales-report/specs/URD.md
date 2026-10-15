<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-sales](#user-requirements-document-urd--dp-sales)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The monthly report](#41-the-monthly-report)
    - [4.2 Another team](#42-another-team)
    - [4.3 A dangling reference](#43-a-dangling-reference)
    - [4.4 A duplicate id](#44-a-duplicate-id)
    - [4.5 A typo in an amount](#45-a-typo-in-an-amount)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-sales

| Field               | Value                                                                        |
| :------------------ | :--------------------------------------------------------------------------- |
| Document ID         | URD-42                                                                       |
| Project             | `42-sales-report` — Enterprise Sales Reporting & Relational Data Integration |
| Product             | `dp-sales`                                                                   |
| Version             | 1.0.0                                                                        |
| Status              | Approved (pre-written by the curriculum)                                     |
| Successor documents | `SRS.md` (SRS-42), `user-manual.md`                                          |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-sales` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-42), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

A sales manager keeps the customer accounts in one file and the sales staff, with the accounts
each of them manages, in another. `dp-sales` combines the two into one report: every
salesperson in alphabetical order, with coach, region, salary, and bonus, followed by each of
their accounts with its projected and actual sales. The report has exactly the layout of the
department's sample report, the amounts are exact to the cent, and a mistake in either file is
found and pointed out before any report is printed.

### 1.3 Scope

In scope: reading the accounts file (by default `sales.dat`) and the salesperson file (by
default `sper.dat`), or one of them from standard input; checking every record and every
account reference; printing the report to standard output; reading files written on Windows or
MS-DOS; help and version information.
Out of scope: changing either file, other report layouts, totals, more than 100 accounts or
salespeople, negative amounts, prompts, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                            | Primary interest                                                                                     |
| :--- | :----------------- | :------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------- |
| SH-1 | Sales manager      | Runs the report in the directory that holds the two files, on Linux, macOS, or Windows | The familiar layout, correct figures                                                                 |
| SH-2 | Data clerk         | Maintains the two files                                                                | Every mistake found and located: bad values, duplicate ids, references to accounts that do not exist |
| SH-3 | Script author      | Runs the report from scripts and pipelines                                             | Predictable output bytes and exit statuses; standard input as a file                                 |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                           | A complete, unambiguous specification                                                                |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                             | Deterministic, byte-exact behavior                                                                   |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                   | Priority | Source     |
| :---- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a sales manager, I want to run the tool with no arguments and get the report from `sales.dat` and `sper.dat` in the current directory.                          | M        | SH-1       |
| UR-02 | As a script author, I want to name either file, and to supply one of them on standard input.                                                                       | M        | SH-3       |
| UR-03 | As a sales manager, I want the report in exactly the layout of the sample report `sales.rpt`.                                                                      | M        | SH-1       |
| UR-04 | As a sales manager, I want the salespeople in alphabetical order of name, each followed by the accounts they manage, in the order the salesperson file lists them. | M        | SH-1       |
| UR-05 | As a sales manager, I want every amount printed exactly, to the cent, with two decimals.                                                                           | M        | SH-1       |
| UR-06 | As a data clerk, I want a record with a missing, extra, or malformed field to be reported with its file and line number.                                           | M        | SH-2       |
| UR-07 | As a data clerk, I want an account id that appears twice in the accounts file, and a salesperson's reference to an account that does not exist, to be reported.    | M        | SH-2       |
| UR-08 | As a sales manager, I want no report at all, rather than a partial or wrong one, when either file has a mistake or cannot be read.                                 | M        | SH-1       |
| UR-09 | As a data clerk, I want files written on Windows or MS-DOS (CRLF line endings, a Ctrl-Z end-of-file mark), with blank lines and tabs, to be read correctly.        | S        | SH-2       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query.                                                                                             | M        | SH-1, SH-3 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before anything is read.                                        | M        | SH-3       |
| UR-12 | As a grader, I want identical report bytes on Linux, macOS, and Windows.                                                                                           | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                               | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to finish instantly.          | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The monthly report

A manager runs `dp-sales` in the directory that holds `sales.dat` and `sper.dat`. The report
lists Chessare before Johnsonbaugh, each with two accounts, and is identical to `sales.rpt`.
The exit status is 0. (UR-01, UR-03, UR-04, UR-05)

### 4.2 Another team

A script runs `dp-sales -s team.dat > team.rpt`, using the same accounts with another
salesperson file. A salesperson who manages no accounts appears with `0 Account(s):an
account managed by two salespeople appears under both. (UR-02, UR-04)

### 4.3 A dangling reference

A salesperson's line lists the account `999`, which is not in the accounts file. The tool
reports `dp-sales: unknown.dat:2: unknown account '999'`, prints no report, and exits with
status 1. (UR-07, UR-08)

### 4.4 A duplicate id

Two accounts in `sales.dat` have the id 812 (one written `0812`). The tool reports the second
one with its line number and prints no report. (UR-07, UR-08)

### 4.5 A typo in an amount

An actual-sales figure reads `1432567.888`. The tool reports
`dp-sales: bad-amount.dat:4: invalid amount '1432567.888'`. (UR-05, UR-06)

### 4.6 Discovery and mistakes

A user runs `dp-sales --help` to see the options. `dp-sales sales.dat` is rejected, because
the files are named with `-a` and `-s`, and nothing is read. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                                                |
| :--- | :---------------------------------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher.                            |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets.                            |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                                             |
| UC-4 | Must behave identically whatever the user's locale or terminal settings; in particular, alphabetical order must not depend on the locale. |

## 6. User acceptance criteria

The users will accept `dp-sales` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term            | Meaning                                                                                          |
| :-------------- | :----------------------------------------------------------------------------------------------- |
| Account         | A customer account: id, name, actual sales, projected sales                                      |
| Salesperson     | A member of the sales staff: name, sales coach, region, base salary, bonus, and managed accounts |
| Account id      | The whole number that identifies an account; the key that links the two files                    |
| Unknown account | An id in the salesperson file that no account in the accounts file has                           |
| Amount          | A sum of money, in whole units and cents                                                         |
| Report          | The text the tool prints: a heading, then one block per salesperson                              |
| Exit status     | The integer a process returns to its caller; 0 means success                                     |
