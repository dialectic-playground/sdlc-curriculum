# User Requirements Document (URD) — dp-calc

| Field | Value |
| :-- | :-- |
| Document ID | URD-37 |
| Project | `37-calc` — Interactive Accumulator Calculator |
| Product | `dp-calc` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-37), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-calc` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-37), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-calc` works like a desk adding machine. It keeps a running total that starts at 0. The
user types a line such as `+ 5 * 10`; the machine applies each operation in the order typed —
add 5, then multiply by 10 — and shows the old total, the line, and the new total. A mistyped
line, a division by zero, or a result too large for the machine is reported and changes
nothing, so the user can simply type the line again. Typing `!` ends the calculation.

### 1.3 Scope
In scope: reading lines of operations from the keyboard, a pipe, or a file; addition,
subtraction, multiplication, whole-number division, and remainder on whole numbers; showing
each result at once; optionally showing the current total as a prompt; reporting bad lines
without losing the total; ending with `!`; reading files written on Windows or MS-DOS; help and
version information.
Out of scope: operator precedence and parentheses, fractions and decimals, numbers beyond the
64-bit range, memory registers, undo, line editing, configuration files, and environment
variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Clerk | Adds up figures at the keyboard on Linux, macOS, or Windows | An immediate answer for each line; mistakes that cost nothing |
| SH-2 | Script author | Feeds prepared lines through the tool in scripts and batch jobs | Predictable output bytes and exit statuses; exact results |
| SH-3 | Auditor | Checks a calculation tape afterwards | Every step of the calculation shown, with exact, documented arithmetic |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a clerk, I want a running total that starts at 0 and to which each line I type applies its operations, so I can build up a calculation step by step. | M | SH-1 |
| UR-02 | As a clerk, I want the operations of a line applied strictly in the order I typed them, like an adding machine, without operator precedence. | M | SH-1 |
| UR-03 | As an auditor, I want each accepted line shown with the total before it and the total after it, so the printout is a complete calculation tape. | M | SH-3 |
| UR-04 | As an auditor, I want addition, subtraction, multiplication, whole-number division, and remainder to give exact, documented results, including for negative numbers. | M | SH-3 |
| UR-05 | As a clerk, I want a mistyped line, a division by zero, or a result too large to hold reported with its line number, and the total left exactly as it was, so I can continue. | M | SH-1 |
| UR-06 | As a clerk, I want to end the calculation with `!` and see a closing message. | M | SH-1 |
| UR-07 | As a clerk, I want to see each result as soon as I have typed the line. | M | SH-1 |
| UR-08 | As a clerk, I want the current total shown as a prompt when I ask for it, without the prompts appearing in the tape I save. | S | SH-1 |
| UR-09 | As a script author, I want to pipe lines into the tool or name a file of lines, and to learn from the exit status whether any line was rejected. | M | SH-2 |
| UR-10 | As a clerk, I want files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly, and extra spaces or tabs between items to be accepted. | S | SH-1 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query; as a script author, I want invalid usage and unreadable files rejected with a clear message and a distinct exit status. | M | SH-1, SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process long inputs quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 At the desk
A clerk runs `dp-calc --prompt` and sees `0 `. The clerk types `+ 5 * 10` and Enter, and sees
`0 + 5 * 10 == 50`, then the prompt `50 `. After `- 20 / 3` the clerk sees
`50 - 20 / 3 == 10`. Typing `!` prints ` **** End of Calculation ****` and the tool exits
with status 0. (UR-01, UR-02, UR-03, UR-06, UR-07, UR-08)

### 4.2 A mistake costs nothing
With a total of 10, the clerk types `/ 0`. The tool reports a division by zero on that line;
the total is still 10, and the next line continues from 10. (UR-05)

### 4.3 A prepared tape
A script runs `dp-calc figures.txt > tape.txt`. The tape holds one line per accepted input
line; if any line was rejected, the exit status is 1 and standard error says which. (UR-03,
UR-09)

### 4.4 Negative numbers
An auditor checks that `- 7 / 2` from 0 gives `-3` and that `- 7 % 2` from 0 gives `-1`, as
documented. (UR-04)

### 4.5 An old data file
A file from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like a file with LF line endings. (UR-10)

### 4.6 Discovery and mistakes
A user runs `dp-calc --help` to see the options; `dp-calc a.txt b.txt` is rejected because the
tool reads one file. (UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: it must not wait for the end of the input before answering a line. |

## 6. User acceptance criteria

The users will accept `dp-calc` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Accumulator | The running total; it starts at 0 |
| Pair | An operator followed by a number, for example `* 10` |
| Accepted line | A line all of whose pairs could be applied; it updates the accumulator |
| Rejected line | A line with a mistake, a division by zero, or an overflow; it leaves the accumulator unchanged |
| Tape | The lines printed for accepted input lines, showing the total before and after |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
