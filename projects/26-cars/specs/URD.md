<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-cars1](#user-requirements-document-urd--dp-cars1)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 A day at the dealership](#41-a-day-at-the-dealership)
    - [4.2 A mistyped sale](#42-a-mistyped-sale)
    - [4.3 An empty showroom](#43-an-empty-showroom)
    - [4.4 A batch file](#44-a-batch-file)
    - [4.5 A damaged file](#45-a-damaged-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-cars1

| Field               | Value                                                      |
| :------------------ | :--------------------------------------------------------- |
| Document ID         | URD-26                                                     |
| Project             | `26-cars` — Car Dealership Daily Sales & Inventory Tracker |
| Product             | `dp-cars1`                                                 |
| Version             | 1.0.0                                                      |
| Status              | Approved (pre-written by the curriculum)                   |
| Successor documents | `SRS.md` (SRS-26), `user-manual.md`                        |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-cars1` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-26), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-cars1` keeps one day's books for a car dealership that sells twelve brands, numbered 0 to 11. In the morning the sales manager enters how many cars of each brand are on the lot; during
the day each sale is entered as a brand and a number of cars; at closing time the tool prints
a `DAILY REPORT` that shows, for every brand, the stock at the start of the day, the cars sold,
the stock left, and the share of the stock that was sold. A slip of the finger — a brand that
does not exist, a negative number of cars, selling more cars than are on the lot — is pointed
out at once and kept out of the books, without losing the rest of the day's entries.

### 1.3 Scope

In scope: entering the opening stock and the sales from the keyboard, a pipe, or a file;
optional prompts; rejecting impossible sales; the daily report; reading data files written on
Windows or MS-DOS; reporting invalid entries and unreadable files; help and version
information.
Out of scope: a different number of brands, brand names, prices and revenue, several days or
carried-over stock, saving the day's totals or printing the report from saved totals (see
`dp-cars2`, Project 28), configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                     | Primary interest                                                            |
| :--- | :----------------- | :------------------------------------------------------------------------------ | :-------------------------------------------------------------------------- |
| SH-1 | Sales manager      | Types the opening stock and the day's sales by hand on Linux, macOS, or Windows | Clear prompts, immediate notice of a mistyped sale, a readable report       |
| SH-2 | Script author      | Feeds a day's entries from a file or a pipe in a batch job                      | Predictable report bytes and exit statuses                                  |
| SH-3 | Owner              | Reads the daily report to decide what to reorder                                | Correct ending stock and sales share for every brand; no impossible figures |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                    | A complete, unambiguous specification                                       |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                      | Deterministic, byte-exact behavior                                          |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                                                             | Priority | Source     |
| :---- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a sales manager, I want to enter the number of cars of each of the twelve brands on the lot at the start of the day, brand 0 first.                                                                                                                       | M        | SH-1       |
| UR-02 | As a sales manager, I want to enter each sale as a brand and a number of cars, as many sales as the day brings, with several sales of the same brand added together.                                                                                         | M        | SH-1       |
| UR-03 | As a sales manager, I want to close the day by entering a negative brand number, or simply by ending the input.                                                                                                                                              | M        | SH-1, SH-2 |
| UR-04 | As an owner, I want a daily report that lists every brand with its stock at the start of the day, the cars sold, the stock at the end of the day, and the percentage of the starting stock that was sold.                                                    | M        | SH-3       |
| UR-05 | As an owner, I want a sale of a brand that does not exist, of a negative number of cars, or of more cars than are left on the lot to be refused and pointed out, so the report never shows impossible figures, while the other sales of the day still count. | M        | SH-1, SH-3 |
| UR-06 | As an owner, I want a brand that had no cars at the start of the day to be shown sensibly in the report, not as a division error or a misleading percentage.                                                                                                 | M        | SH-3       |
| UR-07 | As a script author, I want an entry that is not a whole number, an impossible opening stock, or a day that ends in the middle of a sale reported with its position and a non-zero exit status, and no report printed from incomplete data.                   | M        | SH-2       |
| UR-08 | As a sales manager, I want the tool to tell me what to type next when I ask it to, without those prompts appearing in a report I save to a file.                                                                                                             | S        | SH-1       |
| UR-09 | As a script author, I want to pipe a day's entries into the tool or name a file of entries.                                                                                                                                                                  | M        | SH-2       |
| UR-10 | As a sales manager, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                                                                    | S        | SH-1       |
| UR-11 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                                                                                       | M        | SH-2       |
| UR-12 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                                                                       | M        | SH-1, SH-2 |
| UR-13 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                                                           | M        | SH-2       |
| UR-14 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform.                                                                                                                             | M        | SH-5       |
| UR-15 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                                                                                         | M        | SH-4       |
| UR-16 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to handle a day with very many sales quickly.                                                                           | M        | SH-5       |

## 4. Usage scenarios

### 4.1 A day at the dealership

The manager runs `dp-cars1 --prompt`. For each brand the tool asks `Cars in stock for brand: 0`,
`Cars in stock for brand: 1`, … and the manager types the counts. Then the tool asks
`Which brand was sold?nd `How many cars in sale?`freach sale. At closing time the
manager types `-1`, and the daily report appears. (UR-01, UR-02, UR-03, UR-04, UR-08)

### 4.2 A mistyped sale

The manager types brand `12` by mistake. After the number of cars is entered, the tool says
that there is no such brand and asks for the next sale; the sale is not counted. Later, the
manager tries to sell five cars of a brand that has only one left; that sale is refused too.
The report shows only the accepted sales, and the exit status tells a script that something
was refused. (UR-05)

### 4.3 An empty showroom

Brand 4 had no cars at the start of the day. Its line in the report shows 0, 0, and 0, and
`n/a` instead of a percentage. (UR-06)

### 4.4 A batch file

A script runs `dp-cars1 monday.txt > monday.rpt`. The file holds the twelve opening counts and
the sales, one pair per line, and ends without a sentinel. The report file contains the report
and nothing else. (UR-03, UR-09)

### 4.5 A damaged file

A file contains `2O` (with the letter O) as an opening count. The tool reports
`bad.txt:3: invalid integer '2O'`, prints no report, and exits with status 1. A file that ends
right after a brand number, before the number of cars, is reported as ending unexpectedly.
(UR-07)

### 4.6 Discovery and mistakes

A user runs `dp-cars1 --help` to see the input format, and `dp-cars1 a.txt b.txt` is rejected
because the tool reads one file. (UR-12, UR-13)

## 5. Operational constraints

| ID   | Constraint                                                                                                                                                    |
| :--- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher.                                                |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets.                                                |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                                                                 |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                                                                      |
| UC-5 | Must work interactively: each prompt must appear before the tool waits for the answer, and a refused sale must be reported before the next sale is asked for. |

## 6. User acceptance criteria

The users will accept `dp-cars1` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term          | Meaning                                                                                                     |
| :------------ | :---------------------------------------------------------------------------------------------------------- |
| Brand         | One of the twelve makes of car the dealership sells, identified by its number 0 … 11                        |
| Opening stock | The number of cars of a brand on the lot at the start of the day                                            |
| Sale          | One entry of a brand and a number of cars sold                                                              |
| Sentinel      | A negative brand number, which closes the day                                                               |
| Refused sale  | A sale that is reported and not counted: unknown brand, negative number of cars, or more cars than are left |
| Daily report  | The table printed at the end of the day, one line per brand                                                 |
| End of input  | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard                  |
| Exit status   | The integer a process returns to its caller; 0 means success                                                |
