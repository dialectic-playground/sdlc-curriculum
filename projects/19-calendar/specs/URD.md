<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-calendar](#user-requirements-document-urd--dp-calendar)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the keyboard](#41-at-the-keyboard)
    - [4.2 A typo](#42-a-typo)
    - [4.3 By year](#43-by-year)
    - [4.4 A month that ends on a Saturday](#44-a-month-that-ends-on-a-saturday)
    - [4.5 Bad data](#45-bad-data)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-calendar

| Field               | Value                                               |
| :------------------ | :-------------------------------------------------- |
| Document ID         | URD-19                                              |
| Project             | `19-calendar` — Formatted Annual Calendar Generator |
| Product             | `dp-calendar`                                       |
| Version             | 1.0.0                                               |
| Status              | Approved (pre-written by the curriculum)            |
| Successor documents | `SRS.md` (SRS-19), `user-manual.md`                 |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-calendar` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-19), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-calendar` prints a calendar of the twelve months of a year. The user says on which weekday
January 1 falls and whether the year is a leap year; the tool does the rest. The result is a
neat grid that can be printed, pasted into a document, or compared byte for byte. A mistyped
weekday is reported and the user may simply try again, as in the original textbook program;
users who know only the year can ask for it directly.

### 1.3 Scope

In scope: reading the two codes from the keyboard, a pipe, or a file; asking again after an
invalid weekday; deriving the codes from a Gregorian year; printing the twelve-month calendar;
optional prompts; reading data files written on Windows or MS-DOS; reporting invalid codes and
unreadable files; help and version information.
Out of scope: other calendar systems, week numbers, holidays, localized names, several months
side by side, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder          | Description                                                               | Primary interest                                              |
| :--- | :------------------- | :------------------------------------------------------------------------ | :------------------------------------------------------------ |
| SH-1 | Office user          | Types the two codes by hand on Linux, macOS, or Windows                   | A clear prompt, a second chance after a typo, a neat calendar |
| SH-2 | Script author        | Generates calendars from a pipe or a file in shell scripts and batch jobs | Predictable output bytes and exit statuses                    |
| SH-3 | Printer / typesetter | Pastes the calendar into documents                                        | Exact columns, no trailing spaces, no stray blank lines       |
| SH-4 | Learner (assignee)   | Implements the tool in a language repository of their choice              | A complete, unambiguous specification                         |
| SH-5 | Grader / CI          | Runs automated acceptance tests on three operating systems                | Deterministic, byte-exact behavior                            |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                      | Priority | Source           |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------------- |
| UR-01 | As an office user, I want to give the weekday of January 1 (0 = Sunday … 6 = Saturday) and a leap-year code (1 = leap year, 0 = common year) and get a calendar of all twelve months.                 | M        | SH-1             |
| UR-02 | As a printer, I want every month to show its name, the weekday header `Sun  Mon  Tue  Wed  Thu  Fri  Sat`, and its days in the right columns, one week per line.                                      | M        | SH-3             |
| UR-03 | As a printer, I want no trailing spaces and no empty week lines, even when a month ends on a Saturday, and exactly one blank line between months.                                                     | M        | SH-3             |
| UR-04 | As an office user, I want February to have 29 days in a leap year and 28 otherwise, and each month to start on the weekday after the previous month's last day.                                       | M        | SH-1             |
| UR-05 | As an office user, I want an invalid weekday code to be reported and to be asked again, rather than to start over.                                                                                    | M        | SH-1             |
| UR-06 | As a script author, I want to pipe the codes into the tool or name a file that holds them.                                                                                                            | M        | SH-2             |
| UR-07 | As an office user, I want to ask for the calendar of a year such as 2024 without working out the codes myself.                                                                                        | S        | SH-1             |
| UR-08 | As an office user, I want the tool to ask for the codes when I request it, without the prompts appearing in the calendar I save.                                                                      | S        | SH-1             |
| UR-09 | As a script author, I want missing or malformed codes and an invalid leap-year code reported with their position and a non-zero exit status, with nothing written to the calendar.                    | M        | SH-2             |
| UR-10 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                                | M        | SH-2             |
| UR-11 | As an office user, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                              | S        | SH-1             |
| UR-12 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status, following the curriculum's common CLI conventions. | M        | SH-1, SH-2, SH-4 |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the tool to build, install, and uninstall with standard commands regardless of its implementation language.              | M        | SH-5             |

## 4. Usage scenarios

### 4.1 At the keyboard

A user runs `dp-calendar --prompt`, sees `Enter day and leap year codes:types `2 0` and
Enter, and at once sees the calendar of a common year that begins on a Tuesday, January to
December. (UR-01, UR-02, UR-04, UR-08)

### 4.2 A typo

The user types `9 0`. The tool reports `invalid day code '9'` and asks again; the user types
`2 0` and receives the calendar. The exit status is 0. (UR-05)

### 4.3 By year

A user runs `dp-calendar --year 2024` and receives the same calendar as from the codes `1 1`
(2024 begins on a Monday and is a leap year). (UR-07)

### 4.4 A month that ends on a Saturday

In the calendar of the codes `2 0`, August ends on Saturday the 31st. The line with 25 … 31 is
followed directly by the blank line before September, with no empty week line. (UR-03)

### 4.5 Bad data

A file holds `2` and then `zero`. The tool reports `bad.txt:2: invalid integer 'zero'`, writes
nothing to standard output, and exits with status 1. A file holding `2 2` is rejected because
the leap-year code must be 0 or 1. (UR-09)

### 4.6 Discovery and mistakes

A user runs `dp-calendar --help` to see the options, and `dp-calendar --year 0` is rejected as
a usage error. (UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale, time zone, clock, or terminal settings.                    |
| UC-5 | Must work interactively: it must not wait for the end of the input once valid codes are typed.                 |

## 6. User acceptance criteria

The users will accept `dp-calendar` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term           | Meaning                                                                                                              |
| :------------- | :------------------------------------------------------------------------------------------------------------------- |
| Day code       | The weekday of January 1: 0 = Sunday, 1 = Monday, 2 = Tuesday, 3 = Wednesday, 4 = Thursday, 5 = Friday, 6 = Saturday |
| Leap-year code | 1 for a leap year (February has 29 days), 0 for a common year (28 days)                                              |
| Pair           | One day code followed by one leap-year code, as typed in answer to one prompt                                        |
| Week line      | One line of a month's grid, holding the days of one week from Sunday to Saturday                                     |
| Gregorian year | A year of the calendar in civil use today, extended backwards to year 1                                              |
| End of input   | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard                           |
| Exit status    | The integer a process returns to its caller; 0 means success                                                         |
