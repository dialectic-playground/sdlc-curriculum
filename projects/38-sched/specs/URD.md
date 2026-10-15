<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-sched](#user-requirements-document-urd--dp-sched)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 Booking the hall](#41-booking-the-hall)
    - [4.2 A tie](#42-a-tie)
    - [4.3 A typo](#43-a-typo)
    - [4.4 A pipeline](#44-a-pipeline)
    - [4.5 Discovery and mistakes](#45-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-sched

| Field               | Value                                            |
| :------------------ | :----------------------------------------------- |
| Document ID         | URD-38                                           |
| Project             | `38-sched` — Greedy Interval Activity Scheduling |
| Product             | `dp-sched`                                       |
| Version             | 1.0.0                                            |
| Status              | Approved (pre-written by the curriculum)         |
| Successor documents | `SRS.md` (SRS-38), `user-manual.md`              |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-sched` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-38), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-sched` books a single shared resource — a lecture hall, a machine, a court — among
competing requests. Each request is an activity with a start time and a finish time, one per
line of a fixed-width file. The tool picks as many activities as possible that do not overlap,
using the classic greedy rule (always take the compatible activity that finishes first), and
prints the chosen lines exactly as they appear in the file. The answer is always a largest
possible schedule, and the same file always gives the same schedule.

### 1.3 Scope

In scope: reading activities from a named file or standard input; checking that every line has
the fixed layout and sensible times; choosing a largest set of mutually compatible activities;
printing the chosen lines under a heading; reading files written on Windows or MS-DOS; help and
version information.
Out of scope: several resources, weighted or prioritized activities, times with fractions or
clock notation, listing the rejected activities, and interactive use.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                       | Primary interest                                                     |
| :--- | :----------------- | :-------------------------------------------------------------------------------- | :------------------------------------------------------------------- |
| SH-1 | Scheduler          | Prepares a file of requests and runs the tool by hand on Linux, macOS, or Windows | A correct, largest schedule; clear messages for mistakes in the file |
| SH-2 | Script author      | Calls the tool from scripts or pipelines                                          | Predictable output bytes and exit statuses                           |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice                      | A complete, unambiguous specification, including the tie rule        |
| SH-4 | Grader / CI        | Runs automated acceptance tests on three operating systems                        | Deterministic, byte-exact behavior                                   |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                    | Priority | Source     |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a scheduler, I want to name the file of activities on the command line, or read standard input instead.                                                                          | M        | SH-1, SH-2 |
| UR-02 | As a scheduler, I want each activity to be one line with its start time in columns 1–5 and its finish time in columns 6–10.                                                         | M        | SH-1       |
| UR-03 | As a scheduler, I want the tool to choose as many activities as possible that do not overlap, where an activity may start exactly when another finishes.                            | M        | SH-1       |
| UR-04 | As a scheduler, I want the chosen activities printed under the heading `Optimal schedule:`, in order of finish time, exactly as they are written in my file.                        | M        | SH-1       |
| UR-05 | As a script author, I want the same file always to produce the same schedule, even when several activities finish at the same time.                                                 | M        | SH-2, SH-4 |
| UR-06 | As a scheduler, I want a malformed line (wrong length, a missing or invalid time, a finish not after its start) to be reported with its line number, and no schedule to be printed. | M        | SH-1       |
| UR-07 | As a scheduler, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                               | S        | SH-1       |
| UR-08 | As a script author, I want every failure to give a clear message and a non-zero exit status.                                                                                        | M        | SH-2       |
| UR-09 | As a terminal user, I want a built-in help screen and a version query.                                                                                                              | M        | SH-1, SH-2 |
| UR-10 | As a script author, I want invalid usage, including a missing file name, rejected with a clear message and a distinct exit status, without any file being read.                     | M        | SH-2       |
| UR-11 | As a grader, I want identical output bytes on Linux, macOS, and Windows.                                                                                                            | M        | SH-4       |
| UR-12 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                | M        | SH-3       |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to handle large files quickly.                 | M        | SH-4       |

## 4. Usage scenarios

### 4.1 Booking the hall

A scheduler has nine requests in `sched.in` and runs `dp-sched sched.in`. The tool prints
`Optimal schedule:`, a blank line, and four of the lines — `
` `13  ` — exiwith status 0. No two of them overlap, and no
schedule has five. (UR-01 … UR-04)

### 4.2 A tie

Two requests, ``2 botnish6 and both fit after the request
` tool takes the one that comes first in the file, every time. (UR-05)

### 4.3 A typo

Line 3 of a file reads `tool reports`dp-sched: bad.in:3: invalid integer
'six'`, prints no schedule, and exits with status 1. (UR-06, UR-08)

### 4.4 A pipeline

A script runs `extract-requests | dp-sched - > plan.txt`. (UR-01)

### 4.5 Discovery and mistakes

A user runs `dp-sched --help` to see the format. `dp-sched` alone is rejected because the file
name is missing, and nothing is read. (UR-09, UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-sched` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term             | Meaning                                                                      |
| :--------------- | :--------------------------------------------------------------------------- |
| Activity         | A request for the resource from a start time until a finish time             |
| Compatible       | Two activities are compatible if one finishes no later than the other starts |
| Schedule         | A set of mutually compatible activities                                      |
| Optimal schedule | A schedule with as many activities as possible                               |
| Exit status      | The integer a process returns to its caller; 0 means success                 |
