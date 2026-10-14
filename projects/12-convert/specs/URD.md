# User Requirements Document (URD) — dp-convert

| Field | Value |
| :-- | :-- |
| Document ID | URD-12 |
| Project | `12-convert` — Interactive Length Unit Conversion |
| Product | `dp-convert` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-12), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-convert` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-12), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-convert` converts lengths measured in whole yards into feet and inches. A user types one
length after another and sees each conversion at once; typing a negative length ends the
session with a closing banner. A script can feed the same lengths from a file or a pipe and get
the same report. The answers are exact for every length the tool accepts, and mistakes — a
mistyped number, a length too large, or an input that stops before the negative length — are
reported clearly instead of producing nonsense or hanging.

### 1.3 Scope
In scope: reading lengths from the keyboard, a pipe, or a file until a negative length;
converting and printing each one; optional prompts; reading data files written on Windows or
MS-DOS; reporting invalid lengths, a missing end marker, and unreadable files; help and version
information.
Out of scope: fractional lengths, other units or conversion directions, totals, writing files,
configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Interactive user | Types lengths by hand on Linux, macOS, or Windows | An immediate answer for each length; clear prompts; a clean way to stop |
| SH-2 | Script author | Pipes lists of lengths through the tool in shell scripts and batch jobs | Predictable output bytes and exit statuses; exact results |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As an interactive user, I want to enter any number of lengths in yards and see each one in yards, feet, and inches. | M | SH-1 |
| UR-02 | As a script author, I want the conversions to be exact (3 feet and 36 inches to the yard) for every length the tool accepts, and the largest accepted length to be documented. | M | SH-2 |
| UR-03 | As an interactive user, I want to end the session by entering a negative length, and to see `*** END OF PROGRAM ***` when I do. | M | SH-1 |
| UR-04 | As a script author, I want anything after the negative length to be left unread, so the end marker reliably ends the work. | S | SH-2 |
| UR-05 | As a script author, I want to pipe lengths into the tool or name a file of lengths, so I can process data I already have. | M | SH-2 |
| UR-06 | As an interactive user, I want to see each conversion as soon as I have typed the length, and the tool to exit as soon as I type the negative length. | M | SH-1 |
| UR-07 | As an interactive user, I want the tool to ask for each length when I request it, without the prompts appearing in the report I save. | S | SH-1 |
| UR-08 | As a script author, I want an input that ends without the negative length to be reported with a non-zero exit status, so a truncated file is noticed. | M | SH-2 |
| UR-09 | As a script author, I want an invalid length (a typo, a decimal point, a unit name, a number too large) reported with its position and a non-zero exit status, while the conversions already produced are kept. | M | SH-2 |
| UR-10 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-2 |
| UR-11 | As an interactive user, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-12 | As a terminal user, I want a built-in help screen and a version query, and invalid usage rejected with a clear message and a distinct exit status. | M | SH-1, SH-2 |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform; as a learner, I want the tool to follow the curriculum's common CLI conventions. | M | SH-3, SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large inputs quickly. | M | SH-4 |

## 4. Usage scenarios

### 4.1 At the keyboard
A user runs `dp-convert --prompt`, sees `Enter next length `, types `5` and Enter, and at once
sees `5 yd =`, `15 ft`, and `180 in`, followed by the next prompt. The user types `-1` and
Enter; the tool prints `*** END OF PROGRAM ***` and exits with status 0 without waiting for
more input. (UR-01, UR-03, UR-06, UR-07)

### 4.2 A batch in a pipeline
A script runs `dp-convert lengths.txt > lengths.out`, where the file ends with `-1`. The output
holds three lines per length and the banner, in input order, and nothing else. Notes written
after the `-1` in the file are ignored. (UR-02, UR-04, UR-05)

### 4.3 A truncated file
A file of lengths was cut short and has no negative length at the end. The tool prints the
conversions it could make, then reports `nosentinel.txt:3: unexpected end of input` and exits
with status 1. (UR-08)

### 4.4 A typo or an impossible length
A file contains `2.5` on its second line. The tool prints the conversion for the first length,
then reports `bad.txt:2: invalid integer '2.5'` and exits with status 1. A length of
256204778801521551 yards, whose inches would not fit in 64 bits, is reported as
`value out of range`. (UR-02, UR-09)

### 4.5 An old data file
A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The
tool reads it exactly like a file with LF line endings. (UR-11)

### 4.6 Discovery and mistakes
A user runs `dp-convert --help` to see the options, and `dp-convert a.txt b.txt` is rejected
because the tool reads one file. (UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: it must answer each length, and stop at the negative length, without waiting for the end of the input. |

## 6. User acceptance criteria

The users will accept `dp-convert` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Yard | The unit of input: 1 yard = 3 feet = 36 inches |
| Length | A whole, non-negative number of yards |
| Sentinel | A negative number that marks the end of the lengths; it is not converted |
| Block | The three report lines printed for one length |
| Banner | The line `*** END OF PROGRAM ***`, printed when the sentinel is read |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
