<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-primes](#user-requirements-document-urd--dp-primes)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the keyboard](#41-at-the-keyboard)
    - [4.2 Saving a list](#42-saving-a-list)
    - [4.3 Small and negative bounds](#43-small-and-negative-bounds)
    - [4.4 Counting](#44-counting)
    - [4.5 A typo](#45-a-typo)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-primes

| Field               | Value                                                    |
| :------------------ | :------------------------------------------------------- |
| Document ID         | URD-18                                                   |
| Project             | `18-primes` — Prime Number Generation via Trial Division |
| Product             | `dp-primes`                                              |
| Version             | 1.0.0                                                    |
| Status              | Approved (pre-written by the curriculum)                 |
| Successor documents | `SRS.md` (SRS-18), `user-manual.md`                      |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-primes` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-18), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-primes` lists every prime number up to a bound _n_. A student can type a number and see the
primes at once; a script can pipe in a bound and save the list, or ask only how many primes
there are. The list is exact, appears quickly even for bounds in the millions, and a mistyped
bound is reported clearly instead of producing nonsense.

### 1.3 Scope

In scope: reading the bound from the keyboard, a pipe, or a file; listing the primes up to it
in ascending order under a header; counting them; an optional banner and prompt; reading data
files written on Windows or MS-DOS; reporting invalid bounds and unreadable files; help and
version information.
Out of scope: testing or factoring a single number, lower bounds, bounds above 10000000, other
output formats, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                         | Primary interest                                                 |
| :--- | :----------------- | :------------------------------------------------------------------ | :--------------------------------------------------------------- |
| SH-1 | Student            | Types a bound by hand on Linux, macOS, or Windows to explore primes | A clear dialog and an immediate answer                           |
| SH-2 | Script author      | Pipes bounds into the tool and processes the list                   | Predictable output bytes and exit statuses; a count-only mode    |
| SH-3 | Instructor         | Uses the tool to discuss primes and algorithm efficiency            | Correct results at every edge, and fast results for large bounds |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice        | A complete, unambiguous specification                            |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems          | Deterministic, byte-exact behavior                               |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                             | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to enter a whole number _n_ and get every prime less than or equal to _n_, in ascending order, one per line.                                                            | M        | SH-1       |
| UR-02 | As a script author, I want the list to begin with a header that repeats _n_, so a saved list can be read without the input beside it.                                                        | M        | SH-2       |
| UR-03 | As an instructor, I want a bound below 2, including a negative bound, to give an empty list rather than an error.                                                                            | M        | SH-3       |
| UR-04 | As a script author, I want to pipe the bound into the tool or name a file that holds it.                                                                                                     | M        | SH-2       |
| UR-05 | As a script author, I want to ask only for the number of primes up to _n_.                                                                                                                   | S        | SH-2       |
| UR-06 | As an instructor, I want bounds up to ten million to be answered within a couple of seconds, and larger bounds to be refused clearly.                                                        | M        | SH-3       |
| UR-07 | As a student, I want the tool to greet me and ask for _n_ when I request it, without the greeting appearing in the list I save.                                                              | S        | SH-1       |
| UR-08 | As a script author, I want a missing or invalid bound (a typo, a decimal point, a number too large) reported with its position and a non-zero exit status, with nothing written to the list. | M        | SH-2       |
| UR-09 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                       | M        | SH-2       |
| UR-10 | As a student, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                          | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status.                                           | M        | SH-1, SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the curriculum's common CLI conventions, so one set of expected outputs verifies every platform.                | M        | SH-4, SH-5 |
| UR-13 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language.                                                             | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the keyboard

A student runs `dp-primes --prompt`, sees the banner `This program lists all primes <= n` and
the prompt `Input n:types `15`and Enter, and at once sees the header`Primes <= 15:`, a
blank line, and the primes 2, 3, 5, 7, 11, and 13. (UR-01, UR-02, UR-07)

### 4.2 Saving a list

A script runs `echo 100 | dp-primes > primes.txt`. The file holds the header, a blank line, and
the 25 primes up to 100, and nothing else. (UR-01, UR-02, UR-04)

### 4.3 Small and negative bounds

An instructor enters `1`, then `-7`. Each time the tool prints the header and an empty list,
and exits with status 0. (UR-03)

### 4.4 Counting

A script runs `echo 10000000 | dp-primes --count` and receives `664579` within two seconds.
`echo 10000001 | dp-primes` is refused with `value out of range '10000001'`. (UR-05, UR-06,
UR-08)

### 4.5 A typo

A file contains a blank line and then `15.0`. The tool reports `bad.txt:2: invalid integer
'15.0'`, writes nothing to standard output, and exits with status 1. (UR-08)

### 4.6 Discovery and mistakes

A user runs `dp-primes --help` to see the options, and `dp-primes a.txt b.txt` is rejected
because the tool reads one file. (UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must not wait for the end of the input once the bound is typed.                    |

## 6. User acceptance criteria

The users will accept `dp-primes` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term         | Meaning                                                                                    |
| :----------- | :----------------------------------------------------------------------------------------- |
| Prime        | An integer greater than 1 whose only positive divisors are 1 and itself                    |
| Bound (_n_)  | The whole number entered by the user; every listed prime is less than or equal to it       |
| Header       | The line `Primes <= n:` (indented by one TAB) that precedes the list                       |
| Banner       | The greeting `This program lists all primes <= n` shown before the prompt                  |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status  | The integer a process returns to its caller; 0 means success                               |
