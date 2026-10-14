# User Requirements Document (URD) — dp-divide

| Field | Value |
| :-- | :-- |
| Document ID | URD-50 |
| Project | `50-fault-recovery` — Structured Exception Handling & Fault Recovery |
| Product | `dp-divide` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-50), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-divide` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-50), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-divide` divides one number by another, pair after pair, and shows how a program survives a
fault it cannot compute around. When a pair cannot be divided — the divisor is zero, or the
quotient is too large to represent — the tool does not crash or print nonsense such as `inf`:
it reports the fault in the textbook's words, leaves through its recovery point, and ends
normally. Every result is printed with six digits after the decimal point, the same on every
operating system.

### 1.3 Scope
In scope: reading pairs of numbers from the keyboard, a pipe, or a file; printing each
quotient; recovering from a division fault; optional prompts; reading data files written on
Windows or MS-DOS; reporting invalid numbers, an incomplete last pair, and unreadable files;
help and version information.
Out of scope: other arithmetic, continuing after a fault, writing files, configuration files,
and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Student | Types pairs of numbers on Linux, macOS, or Windows to see fault recovery at work | An immediate answer for each pair; the recovery messages when a fault occurs |
| SH-2 | Instructor | Demonstrates exception handling and non-local control flow | Faults that are precisely defined and reproducible on every platform |
| SH-3 | Script author | Pipes pairs of numbers through the tool | Predictable output bytes and exit statuses; a clear difference between a recovered fault and bad data |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a student, I want to enter any number of pairs of numbers and see each first number divided by the second, until I signal the end of the input. | M | SH-1 |
| UR-02 | As a student, I want each result to show both numbers and the quotient, with six digits after the decimal point, as in the textbook. | M | SH-1 |
| UR-03 | As a student, I want to see each quotient as soon as I have typed its pair. | M | SH-1 |
| UR-04 | As an instructor, I want a zero divisor, and a quotient too large to represent, to be treated as a fault rather than printed as an infinite or undefined value. | M | SH-2 |
| UR-05 | As an instructor, I want the tool to recover from a fault exactly as the textbook program does: report the status, announce the recovery point, and end normally with exit status 0. | M | SH-2 |
| UR-06 | As a student, I want the tool to ask for each pair when I request it, without the prompts appearing in the output I save. | S | SH-1 |
| UR-07 | As a script author, I want an invalid number, or a last pair with only one number, reported with its position and a non-zero exit status, while the results already produced are kept. | M | SH-3 |
| UR-08 | As a script author, I want to pipe pairs into the tool or name a file of pairs, and a missing or unreadable file reported clearly. | M | SH-3 |
| UR-09 | As a student, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-10 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-3 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-3 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, whatever the platform's floating-point traps, signals, and number formatting. | M | SH-5 |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large inputs quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 The textbook's dialogue
A student runs `dp-divide --prompt`, sees `Two floats: `, types `10.0 2.0` and Enter, and at
once sees `10.000000 / 2.000000 == 5.000000`. At the next prompt the student types `10.0 0.0`;
the tool prints `Signal status == 8.` and `At jump point and about to exit...` and exits with
status 0. (UR-01, UR-02, UR-03, UR-04, UR-05, UR-06)

### 4.2 A batch in a pipeline
A script runs `extract-pairs | dp-divide > quotients.txt`. The file holds one line per pair,
in input order, and nothing else; the exit status is 0. (UR-01, UR-08)

### 4.3 Too large to represent
An instructor divides `-1e308` by `0.1`. The quotient would be −10³⁰⁹, beyond the largest
representable number, so the tool recovers from a fault instead of printing an infinity.
(UR-04, UR-05)

### 4.4 A typo and a missing number
A file holds `6 3` on line 1 and `4 two` on line 2. The tool prints the result for the first
pair, then reports `bad.txt:2: invalid number 'two'` and exits with status 1. A file whose last
pair has only one number is reported with `unexpected end of input`. (UR-07)

### 4.5 An old data file
A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like a file with LF line endings. (UR-09)

### 4.6 Discovery and mistakes
A user runs `dp-divide --help` to see the options, and `dp-divide a.txt b.txt` is rejected
because the tool reads one file. (UR-10, UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: it must not wait for the end of the input before answering. |

## 6. User acceptance criteria

The users will accept `dp-divide` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Pair | Two consecutive numbers of the input: the dividend and the divisor |
| Quotient | The dividend divided by the divisor |
| Fault | A pair that cannot be divided: a zero divisor, or a quotient too large to represent |
| Recovery point | The single place in the program to which control passes when a fault occurs, and where the run is ended in an orderly way |
| Recovery | Reporting the fault, leaving through the recovery point, and ending with exit status 0 |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
