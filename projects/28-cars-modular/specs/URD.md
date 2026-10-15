<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-cars2](#user-requirements-document-urd--dp-cars2)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 A drop-in replacement](#41-a-drop-in-replacement)
    - [4.2 Closing the day](#42-closing-the-day)
    - [4.3 A reprint](#43-a-reprint)
    - [4.4 A damaged totals file](#44-a-damaged-totals-file)
    - [4.5 Nowhere to save](#45-nowhere-to-save)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-cars2

| Field               | Value                                                          |
| :------------------ | :------------------------------------------------------------- |
| Document ID         | URD-28                                                         |
| Project             | `28-cars-modular` — Modular Car Sales Architecture & Reporting |
| Product             | `dp-cars2`                                                     |
| Version             | 1.0.0                                                          |
| Status              | Approved (pre-written by the curriculum)                       |
| Successor documents | `SRS.md` (SRS-28), `user-manual.md`                            |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-cars2` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-28), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-cars2` is the second release of the dealership's daily sales tool, `dp-cars1`
(Project 26). Its users must notice no difference: the same entries produce the same prompts,
the same messages, the same `DAILY REPORT`, and the same exit status. Inside, the report has
become an independent component that is handed the day's totals and prints them. That
component can now be fed from a second source: the day's totals, saved at closing time, can be
printed again later — or typed in from another system — without re-entering every sale.

### 1.3 Scope

In scope: everything `dp-cars1` does (the opening stock, the sales, refused sales, the daily
report, prompts, data files from Windows or MS-DOS, diagnostics, help and version); saving the
day's totals to a file; printing the report from a file of totals.
Out of scope: a different number of brands, brand names, prices and revenue, combining several
days, other report formats, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                     | Primary interest                                                                        |
| :--- | :----------------- | :------------------------------------------------------------------------------ | :-------------------------------------------------------------------------------------- |
| SH-1 | Sales manager      | Types the opening stock and the day's sales by hand on Linux, macOS, or Windows | The dialog and report they already know from `dp-cars1`                                 |
| SH-2 | Script author      | Runs `dp-cars1` today in batch jobs and wants to switch to `dp-cars2`           | Byte-identical output and exit statuses for existing inputs                             |
| SH-3 | Owner              | Reads the daily report, sometimes days later                                    | Reprinting a past day's report exactly, from a small saved file                         |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                    | A complete, unambiguous specification, and a clear design goal for the report component |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                      | Deterministic, byte-exact behavior                                                      |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                      | Priority | Source     |
| :---- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a script author, I want `dp-cars2` to produce exactly the same report, messages, and exit status as `dp-cars1` for the same input and options, so I can replace one with the other without changing anything else. | M        | SH-2       |
| UR-02 | As a sales manager, I want to enter the opening stock of the twelve brands and the day's sales, close the day with a negative brand or the end of the input, and get the daily report, as with `dp-cars1`.            | M        | SH-1       |
| UR-03 | As an owner, I want impossible sales (unknown brand, negative number of cars, more cars than are left) refused and pointed out, and a brand with no starting stock shown as `n/a`, as with `dp-cars1`.                | M        | SH-1, SH-3 |
| UR-04 | As an owner, I want to save the day's totals — each brand's starting stock and cars sold — to a small file at closing time.                                                                                           | M        | SH-3       |
| UR-05 | As an owner, I want to print the daily report again from a file of totals, identical to the report of the day it was saved from, without re-entering any sale.                                                        | M        | SH-3       |
| UR-06 | As an owner, I want a damaged or incomplete totals file — a missing value, an extra value, an impossible figure — reported with its position instead of printing a wrong report.                                      | M        | SH-3       |
| UR-07 | As an owner, I want a failure to save the totals reported clearly, with a non-zero exit status, while the report I just entered the day for is still printed.                                                         | M        | SH-3       |
| UR-08 | As a script author, I want invalid entries, an input that ends too early, and unreadable files reported with a position or a reason and a non-zero exit status, and no report printed from incomplete data.           | M        | SH-2       |
| UR-09 | As a sales manager, I want the tool to tell me what to type next when I ask it to, without those prompts appearing in a report I save.                                                                                | S        | SH-1       |
| UR-10 | As a sales manager, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly, and saved totals to be readable on every platform.                          | S        | SH-1, SH-3 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                                | M        | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                    | M        | SH-2       |
| UR-13 | As a grader, I want identical output bytes and identical saved files on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                            | M        | SH-5       |
| UR-14 | As a learner, I want the tool to follow the curriculum's common CLI conventions, and I want a clear statement of how the program must be divided into components.                                                     | M        | SH-4       |
| UR-15 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to handle a day with very many sales quickly.                                    | M        | SH-5       |

## 4. Usage scenarios

### 4.1 A drop-in replacement

A batch job that ran `dp-cars1 monday.txt > monday.rpt` now runs
`dp-cars2 monday.txt > monday.rpt`. The report file, the messages, and the exit status are the
same as before. (UR-01, UR-02, UR-03)

### 4.2 Closing the day

The manager runs `dp-cars2 --prompt --save monday.tot`, enters the day as usual, and types
`-1`. The report appears, and `monday.tot` now holds twelve short lines: each brand's starting
stock and cars sold. (UR-04, UR-09)

### 4.3 A reprint

On Friday the owner runs `dp-cars2 --totals monday.tot` and sees Monday's report again, byte
for byte. (UR-05)

### 4.4 A damaged totals file

A totals file claims that 5 cars of brand 3 were sold from a stock of 4. `dp-cars2 --totals`
reports the impossible figure with its line number and prints no report. A file with a
thirteenth line is reported as holding extra data. (UR-06)

### 4.5 Nowhere to save

The manager types `dp-cars2 --save reports/monday.tot`, but the directory `reports` does not
exist. The report is printed, then the tool says that `reports/monday.tot` could not be
created, and exits with status 1. (UR-07)

### 4.6 Discovery and mistakes

A user runs `dp-cars2 --help` to see the options, and `dp-cars2 --save ''` is rejected as an
invalid file name. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively, exactly like `dp-cars1`.                                                              |
| UC-6 | Must write no file other than the one named with `--save`.                                                     |

## 6. User acceptance criteria

The users will accept `dp-cars2` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms, including the
   tests whose expected outputs are those of `dp-cars1`.
3. The help text exactly matches the one published in the user manual.
4. A design review confirms that the report is produced by an independent component as the
   SRS requires.

## 7. Glossary

| Term             | Meaning                                                                                                     |
| :--------------- | :---------------------------------------------------------------------------------------------------------- |
| Brand            | One of the twelve makes of car the dealership sells, identified by its number 0 … 11                        |
| Opening stock    | The number of cars of a brand on the lot at the start of the day                                            |
| Sale             | One entry of a brand and a number of cars sold                                                              |
| Refused sale     | A sale that is reported and not counted: unknown brand, negative number of cars, or more cars than are left |
| Totals           | For each brand, its opening stock and the number of cars sold during the day                                |
| Totals file      | A text file holding the totals, as written by `--save` and read by `--totals`                               |
| Report component | The part of the program that receives the totals and prints the daily report                                |
| Daily report     | The table printed at the end of the day, one line per brand                                                 |
| Exit status      | The integer a process returns to its caller; 0 means success                                                |
