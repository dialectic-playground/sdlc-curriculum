<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-resistor](#user-requirements-document-urd--dp-resistor)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 At the bench](#41-at-the-bench)
    - [4.2 A typo](#42-a-typo)
    - [4.3 A checklist](#43-a-checklist)
    - [4.4 The extremes](#44-the-extremes)
    - [4.5 A bad answer](#45-a-bad-answer)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-resistor

| Field               | Value                                              |
| :------------------ | :------------------------------------------------- |
| Document ID         | URD-21                                             |
| Project             | `21-resistor` — Resistor 3-Band Color Code Decoder |
| Product             | `dp-resistor`                                      |
| Version             | 1.0.0                                              |
| Status              | Approved (pre-written by the curriculum)           |
| Successor documents | `SRS.md` (SRS-21), `user-manual.md`                |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-resistor` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-21), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

`dp-resistor` tells a technician the resistance of a 3-band resistor from the colors of its
bands. It shows a guide to the ten colors and their one-letter codes, then reads the codes of
one resistor after another and answers each with the resistance in ohms, kilo-ohms, or
mega-ohms. A mistyped code is pointed out and the codes are asked for again; a script can feed
a whole list of resistors from a file and get the same answers.

### 1.3 Scope

In scope: the color guide; decoding the three bands of a resistor; choosing the unit by
magnitude; deciding after each resistor whether to decode another; optional prompts; reading
responses from the keyboard, a pipe, or a file, including files written on Windows or MS-DOS;
reporting invalid codes, invalid answers, and unreadable files; help and version information.
Out of scope: resistors with four or more bands, tolerance, color names typed in full,
configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                                   | Primary interest                                                                |
| :--- | :----------------- | :-------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------ |
| SH-1 | Technician         | Reads band colors off resistors and types the codes at a terminal on Linux, macOS, or Windows | A guide to the codes; an immediate, correct answer; forgiving handling of typos |
| SH-2 | Script author      | Feeds lists of codes to the tool from files or pipes                                          | Predictable output bytes and exit statuses                                      |
| SH-3 | Instructor         | Uses the tool to check students' color-code readings                                          | Exact values in the conventional units                                          |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice                                  | A complete, unambiguous specification                                           |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                                    | Deterministic, byte-exact behavior                                              |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                                                      | Priority | Source     |
| :---- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a technician, I want to see a guide to the ten band colors, their one-letter codes, and their digit values before I start.                                                                                                                         | M        | SH-1       |
| UR-02 | As a technician, I want to type the codes of a resistor's three bands and get its resistance: the first two bands are digits and the third is the power of ten.                                                                                       | M        | SH-1, SH-3 |
| UR-03 | As an instructor, I want the resistance shown in ohms below 1000 ohms, in kilo-ohms below one million ohms, and in mega-ohms above that, always with six decimals.                                                                                    | M        | SH-3       |
| UR-04 | As a technician, I want to decode as many resistors as I like, answering after each one whether to decode another.                                                                                                                                    | M        | SH-1       |
| UR-05 | As a technician, I want a mistyped code pointed out and the codes asked for again, without losing the session.                                                                                                                                        | M        | SH-1       |
| UR-06 | As a technician, I want the codes accepted in lower case as well as upper case.                                                                                                                                                                       | S        | SH-1       |
| UR-07 | As a script author, I want each answer to repeat the codes it belongs to, and to pipe the codes in or name a file of codes.                                                                                                                           | M        | SH-2       |
| UR-08 | As a technician, I want to see each resistance as soon as I have typed its three codes, and to be prompted for input when I ask for it, without the prompts appearing in a saved report.                                                              | S        | SH-1       |
| UR-09 | As a script author, I want a nonsensical answer, an input that stops in the middle of a resistor, or an unreadable file reported with its position and a non-zero exit status, and I want to know from the exit status whether any code was rejected. | M        | SH-2       |
| UR-10 | As a technician, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                                                                | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status.                                                                                                    | M        | SH-1, SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, whatever the locale, so one set of expected outputs verifies every platform.                                                                                                 | M        | SH-5       |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                                                                                  | M        | SH-4       |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process long lists quickly.                                                                                   | M        | SH-5       |

## 4. Usage scenarios

### 4.1 At the bench

A technician runs `dp-resistor --prompt`, reads the color guide, sees
`Enter the three color codes:types `Y V R`and Enter, and at once sees`Resistance of Y V R = 4.700000 kilo-ohms`, followed by
`Decode another resistor (1 = yes, 0 = no)?After answering `0` the tool exits with
status 0. (UR-01, UR-02, UR-03, UR-04, UR-08)

### 4.2 A typo

The technician types `Y Q R`. The tool reports that `Q` is not a color code and asks for the
three codes again; the technician types `y v r` and gets the resistance. At the end, the exit
status is 1, because a code was rejected. (UR-05, UR-06, UR-09)

### 4.3 A checklist

An instructor keeps a file with the codes of every resistor in a kit, each followed by `1`,
and runs `dp-resistor kit.txt > values.txt`. The file holds the color guide and one line per
resistor, each naming the codes; the last resistor needs no answer after it. (UR-03, UR-07)

### 4.4 The extremes

`B B B` is `0.000000 ohms`; `B N O` is exactly one kilo-ohm, `1.000000 kilo-ohms`; `W W W` is
`99000.000000 mega-ohms`. (UR-03)

### 4.5 A bad answer

A file answers `yes` instead of `1`. The tool reports `invalid integer 'yes'` with the line
number and exits with status 1, keeping the resistances already written. (UR-09)

### 4.6 Discovery and mistakes

A user runs `dp-resistor --help` to see the codes and options, and `dp-resistor a.txt b.txt` is
rejected because the tool reads one file. (UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: it must answer each resistor before the next one is typed.                            |

## 6. User acceptance criteria

The users will accept `dp-resistor` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term                    | Meaning                                                                                    |
| :---------------------- | :----------------------------------------------------------------------------------------- |
| Band                    | One of the three colored rings on a resistor: two digits, then the power of ten            |
| Color code              | The one-letter abbreviation of a band color, such as `R` for red and `E` for blue          |
| Color guide             | The table of the ten colors, their codes, and their digit values                           |
| Ohm, kilo-ohm, mega-ohm | The unit of resistance, a thousand ohms, and a million ohms                                |
| Answer                  | The `1` (decode another) or `0` (stop) typed after each resistance                         |
| End of input            | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status             | The integer a process returns to its caller; 0 means success                               |
