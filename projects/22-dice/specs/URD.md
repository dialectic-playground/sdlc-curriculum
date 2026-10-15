<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-dice](#user-requirements-document-urd--dp-dice)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 A night at the table](#41-a-night-at-the-table)
    - [4.2 Too big a bet](#42-too-big-a-bet)
    - [4.3 Snake eyes](#43-snake-eyes)
    - [4.4 Broke](#44-broke)
    - [4.5 A classroom replay](#45-a-classroom-replay)
    - [4.6 A broken script](#46-a-broken-script)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-dice

| Field               | Value                                            |
| :------------------ | :----------------------------------------------- |
| Document ID         | URD-22                                           |
| Project             | `22-dice` — Roll Them Bones Dice Simulation Game |
| Product             | `dp-dice`                                        |
| Version             | 1.0.0                                            |
| Status              | Approved (pre-written by the curriculum)         |
| Successor documents | `SRS.md` (SRS-22), `user-manual.md`              |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-dice` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-22), which turns each need into precise,
testable system behavior.

### 1.2 Product vision

`dp-dice` lets a player gamble play money on "Roll Them Bones", a simple dice game, against the
house. The player starts with $500 and, round after round, decides whether to play and how much
to bet. The tool rolls the dice, tells the player what happened, and keeps the bankroll until
the player walks away or goes broke. Because the dice come from a documented generator with a
seed, any game can be replayed exactly — by a teacher demonstrating the rules, a student
testing a strategy, or a grader checking an implementation.

### 1.3 Scope

In scope: the bankroll, the table limit, betting, the rules for winning and losing a round, a
transcript of every roll, the closing banner, a seed for the dice, optional prompts, reading the
player's responses from the keyboard, a pipe, or a file, including files written on Windows or
MS-DOS; reporting malformed responses and unreadable files; help and version information.
Out of scope: other games and stakes, saving a game, statistics over many games, configuration
files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                    | Primary interest                           |
| :--- | :----------------- | :------------------------------------------------------------- | :----------------------------------------- |
| SH-1 | Player             | Plays at a terminal on Linux, macOS, or Windows                | Clear rules, clear messages, fair dice     |
| SH-2 | Instructor         | Demonstrates the rules and probability with reproducible games | The same game every time for the same seed |
| SH-3 | Script author      | Feeds betting strategies to the tool from files                | Predictable output bytes and exit statuses |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice   | A complete, unambiguous specification      |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems     | Deterministic, byte-exact behavior         |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                                                               | Priority | Source     |
| :---- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a player, I want to start with a bankroll of $500 and decide before each round whether to play or quit.                                                                                                                     | M        | SH-1       |
| UR-02 | As a player, I want to bet a whole number of dollars on each round, at least $1, at most the table limit of $250, and never more than I have.                                                                                  | M        | SH-1       |
| UR-03 | As a player, I want a bet that breaks a rule refused with the reason, and to be asked for the bet again.                                                                                                                       | M        | SH-1       |
| UR-04 | As a player, I want the round decided by the rules of Roll Them Bones: a first roll of 7 or 11 wins; otherwise the first roll is my mark, which wins if it comes up again before a 7 or 11, and pays double if it is 2 or 12.  | M        | SH-1, SH-2 |
| UR-05 | As a player, I want to see every roll of the dice and the outcome, and my bankroll after every round.                                                                                                                          | M        | SH-1       |
| UR-06 | As a player, I want the game to end when I quit or go broke, with a closing message that fits.                                                                                                                                 | M        | SH-1       |
| UR-07 | As an instructor, I want to choose a seed so that the same seed and the same responses replay the same game on any computer, and the game without a seed to be the same every time too.                                        | M        | SH-2, SH-5 |
| UR-08 | As a script author, I want to pipe the responses in or name a file of responses, and get a transcript that reads well without the input beside it.                                                                             | M        | SH-3       |
| UR-09 | As a player, I want to see the outcome of each response as soon as I give it, and to be prompted when I ask for it, without the prompts appearing in a saved transcript.                                                       | S        | SH-1       |
| UR-10 | As a script author, I want a malformed response (not a whole number, an answer other than 1 or 0), responses that run out in the middle of a bet, or an unreadable file reported with its position and a non-zero exit status. | M        | SH-3       |
| UR-11 | As a player, I want response files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                                                                    | S        | SH-1       |
| UR-12 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status.                                                                             | M        | SH-1, SH-3 |
| UR-13 | As a learner and grader, I want the tool to follow the curriculum's common CLI conventions and to produce identical output bytes on Linux, macOS, and Windows.                                                                 | M        | SH-4, SH-5 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to play long scripted games quickly.                                                      | M        | SH-5       |

## 4. Usage scenarios

### 4.1 A night at the table

A player runs `dp-dice --prompt`, sees `Your bankroll is $500.` and
`Want to play? (1: yes, 0: no)answers `1`, and at `Enter your bet:`tps `100`. The tool
shows each roll — the first roll 8 is the mark, then 6, then 8 — announces
`You made your mark! You win $100.`and`Your bankroll is $600.`, and asks again. The player
answers `0`and sees`Congratulations! You leave the table with $600.` (UR-01, UR-02, UR-04,
UR-05, UR-06, UR-09)

### 4.2 Too big a bet

With $150 left, the player bets 200. The tool answers `Bet refused: you only have $150.` and
asks for the bet again; a bet of 300 would be refused because of the table limit, and a bet of
0 because the minimum is $1. (UR-02, UR-03)

### 4.3 Snake eyes

The first roll is 1 + 1 = 2. The tool announces `Your mark is 2; it pays double.`; when 2 comes
up again before 7 or 11, the player's bet of $250 wins $500. (UR-04)

### 4.4 Broke

A player who bets everything twice and loses twice sees `Your bankroll is $0.` and
`You're broke! Better luck next time.`, and the game ends even if more responses follow.
(UR-06)

### 4.5 A classroom replay

An instructor runs `dp-dice --seed=14 strategy.txt` on a Linux laptop, and the students run the
same command on macOS and Windows; every transcript is identical. (UR-07, UR-08, UR-13)

### 4.6 A broken script

A response file contains the bet `12.50`. The tool reports `invalid integer '12.50'` with the
line number and exits with status 1, keeping the transcript so far. (UR-10)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings, and must not depend on the clock.     |
| UC-5 | Must work interactively: it must answer each response before the next one is typed.                            |

## 6. User acceptance criteria

The users will accept `dp-dice` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term                 | Meaning                                                                                    |
| :------------------- | :----------------------------------------------------------------------------------------- |
| Bankroll             | The player's money, in whole dollars; it starts at $500                                    |
| Table limit          | The largest bet the house accepts, $250                                                    |
| Round                | One bet and the rolls that decide it                                                       |
| Roll                 | One throw of two six-sided dice; its value is the sum of the faces, 2 … 12                 |
| Natural              | A first roll of 7 or 11, which wins at once                                                |
| Mark                 | The value of a round's first roll when it is not a natural; rolling it again wins          |
| Snake eyes, box cars | A roll of 2 and a roll of 12; as a mark, they pay double                                   |
| Seed                 | The number that starts the generator, so the same seed gives the same dice                 |
| Response             | An answer to "Want to play?" or a bet, typed or read from a file                           |
| End of input         | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status          | The integer a process returns to its caller; 0 means success                               |
