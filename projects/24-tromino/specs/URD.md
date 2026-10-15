<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-tromino](#user-requirements-document-urd--dp-tromino)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The textbook's board](#41-the-textbooks-board)
    - [4.2 Seeing the tiling](#42-seeing-the-tiling)
    - [4.3 An answer key](#43-an-answer-key)
    - [4.4 A mistake](#44-a-mistake)
    - [4.5 An old answer file](#45-an-old-answer-file)
    - [4.6 Discovery and mistakes](#46-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-tromino

| Field               | Value                                                       |
| :------------------ | :---------------------------------------------------------- |
| Document ID         | URD-24                                                      |
| Project             | `24-tromino` — Divide-and-Conquer Tromino Deficiency Tiling |
| Product             | `dp-tromino`                                                |
| Version             | 1.0.0                                                       |
| Status              | Approved (pre-written by the curriculum)                    |
| Successor documents | `SRS.md` (SRS-24), `user-manual.md`                         |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-tromino` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-24), which turns each need into
precise, testable system behavior.

### 1.2 Product vision

A square board of 2ᵏ × 2ᵏ squares with one square removed can always be covered exactly by
L-shaped tiles of three squares (trominoes). `dp-tromino` shows how: given the board size and
the missing square, it lists every tromino of one such tiling — where it lies and which way it
points — in the order a divide-and-conquer algorithm places them, and on request draws the
tiled board. A student can check the theorem on any board up to 64 × 64, and a teacher can
compare a student's own program against the tool line by line.

### 1.3 Scope

In scope: reading board sizes and missing squares from the keyboard, a pipe, or a file, one
board after another, until the user enters 0 or the input ends; listing the trominoes of each
tiling; an optional drawing of each tiled board; optional prompts; reading data files written
on Windows or MS-DOS; reporting invalid answers and unreadable files; help and version
information.
Out of scope: rectangular boards, boards with more than one missing square, boards larger than
64 × 64, other tilings of the same board, graphical output, writing files, configuration
files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                     | Primary interest                                           |
| :--- | :----------------- | :-------------------------------------------------------------- | :--------------------------------------------------------- |
| SH-1 | Student            | Explores the tiling at the keyboard on Linux, macOS, or Windows | Clear prompts; a readable list and drawing; helpful errors |
| SH-2 | Teacher            | Uses the tool's output as the answer key for a tiling exercise  | One documented, reproducible tiling and listing order      |
| SH-3 | Script author      | Pipes board descriptions through the tool                       | Predictable output bytes and exit statuses                 |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice    | A complete, unambiguous specification                      |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems      | Deterministic, byte-exact behavior                         |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                       | Priority | Source     |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to give a board size and the position of the missing square and get a complete tiling of the rest of the board by trominoes, with no overlaps and no gaps.                                        | M        | SH-1       |
| UR-02 | As a student, I want to tile one board after another in the same session, and to stop by entering 0 or by ending the input.                                                                                            | M        | SH-1       |
| UR-03 | As a teacher, I want the trominoes listed in a fixed, documented order, each with a documented position and orientation, so any correct program produces exactly the same list.                                        | M        | SH-2       |
| UR-04 | As a teacher, I want the textbook's divide-and-conquer method used: a tromino at the center of the board first, then each quarter in turn.                                                                             | M        | SH-2       |
| UR-05 | As a student, I want to see a drawing of the tiled board in which I can tell the trominoes apart, when I ask for it.                                                                                                   | C        | SH-1       |
| UR-06 | As a student, I want the tool to ask for each answer when I request it, without the prompts appearing in the output I save.                                                                                            | S        | SH-1       |
| UR-07 | As a script author, I want to pipe the answers into the tool or name a file of answers.                                                                                                                                | M        | SH-3       |
| UR-08 | As a student, I want an invalid answer (a size that is not an allowed power of 2, a square outside the board, a typo) reported with its position and a non-zero exit status, while the tilings already shown are kept. | M        | SH-1, SH-3 |
| UR-09 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status.                                                                                                                 | M        | SH-3       |
| UR-10 | As a student, I want answer files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                             | S        | SH-1       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                                                 | M        | SH-1, SH-3 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status.                                                                                                                     | M        | SH-3       |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions.                                                                               | M        | SH-4, SH-5 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to tile the largest board quickly.                                                | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The textbook's board

A student runs `dp-tromino --prompt`, answers `Enter size of board (0 to quit):ith `4`and`Enter coordinates of missing square:ith `1 2`. The tool prints the heading `Tiling` and
five lines, starting with `2 2 LR` — the tromino placed at the center first. The student
answers the next size prompt with `0`, and the tool exits with status 0. (UR-01, UR-02, UR-03,
UR-04, UR-06)

### 4.2 Seeing the tiling

The student repeats the run with `--draw`. After the list, the tool draws the 4 × 4 board,
showing each square as the number of the tromino that covers it and the missing square as `X`.
(UR-05)

### 4.3 An answer key

A teacher keeps `printf '8\n5 6\n0\n' | dp-tromino > key.txt` as the reference answer and
compares each student's output with it. (UR-03, UR-07)

### 4.4 A mistake

A student answers the size question with `6`. The tool reports
`dp-tromino: -:1: invalid board size '6'` and exits with status 1. (UR-08)

### 4.5 An old answer file

A file of answers copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z
byte. The tool reads it exactly like a file with LF line endings. (UR-10)

### 4.6 Discovery and mistakes

A user runs `dp-tromino --help` to see the options, and `dp-tromino a.txt b.txt` is rejected
because the tool reads one file. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |
| UC-5 | Must work interactively: each tiling appears as soon as its missing square has been entered.                   |

## 6. User acceptance criteria

The users will accept `dp-tromino` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term            | Meaning                                                                                             |
| :-------------- | :-------------------------------------------------------------------------------------------------- |
| Board           | A square of _n_ × _n_ unit squares, where _n_ is a power of 2                                       |
| Deficient board | A board with exactly one square missing                                                             |
| Tromino         | An L-shaped tile made of three unit squares: a 2 × 2 block with one square left out                 |
| Orientation     | Which corner of its 2 × 2 block a tromino's two arms meet in: UL, UR, LR, or LL                     |
| Tiling          | A covering of every square of a deficient board except the missing one by non-overlapping trominoes |
| Round           | One board size followed by the coordinates of its missing square                                    |
| End of input    | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard          |
| Exit status     | The integer a process returns to its caller; 0 means success                                        |
