# User Requirements Document (URD) — dp-stats

| Field | Value |
| :-- | :-- |
| Document ID | URD-15 |
| Project | `15-stats` — Single-Pass Streaming Statistical Summary |
| Product | `dp-stats` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-15), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-stats` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-15), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-stats` summarizes a stream of measurements in one line of a shell pipeline: how many there
were, the largest and smallest, their sum and mean, and how widely they are spread (variance
and standard deviation). It looks at each number once and keeps nothing but a few running
totals, so a stream far larger than memory is no problem. Its answers are the same, to the
last printed digit, on every computer, and a typo in the data is reported instead of
silently corrupting the summary.

### 1.3 Scope
In scope: reading real numbers from the keyboard, a pipe, or a file until the end of the
input; printing the count, maximum, minimum, sum, mean, population variance, and standard
deviation; reading data files written on Windows or MS-DOS; reporting invalid numbers,
arithmetic overflow, and unreadable files; help and version information.
Out of scope: sample (N − 1) variance, medians, percentiles, histograms, several input files,
other output precisions, prompts, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Data analyst | Summarizes measurement files and pipeline output on Linux, macOS, or Windows | A complete, readable summary; helpful errors |
| SH-2 | Script author | Calls the tool from shell scripts and batch jobs | Predictable output bytes and exit statuses |
| SH-3 | Data engineer | Feeds very large streams through the tool | One pass, constant memory |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a data analyst, I want to give the tool any number of real numbers, in any mix of spaces and line breaks, and get one summary when the input ends. | M | SH-1 |
| UR-02 | As a data analyst, I want the summary to give the number of values, the maximum, the minimum, the sum, the mean, the population variance, and the standard deviation, each clearly labeled. | M | SH-1 |
| UR-03 | As a data engineer, I want the tool to read each number once and use the same small amount of memory however long the input is. | M | SH-3 |
| UR-04 | As a script author, I want to pipe numbers into the tool or name a file of numbers. | M | SH-2 |
| UR-05 | As a script author, I want every printed digit to be the same on every computer and in every implementation, so results can be compared and archived. | M | SH-2, SH-5 |
| UR-06 | As a data analyst, I want an input with no numbers at all to produce a clear one-line answer, not an error or a division by zero. | M | SH-1 |
| UR-07 | As a script author, I want an invalid number, or numbers too large to be summed, reported with their position and a non-zero exit status, and no misleading partial summary. | M | SH-2 |
| UR-08 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-2 |
| UR-09 | As a data analyst, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-10 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to process large inputs quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 A quick summary
An analyst runs `printf '10.0 20.0 30.0' | dp-stats` and sees seven lines: `3 data items read`,
the maximum 30, the minimum 10, the sum 60, the mean 20, the variance 66.666667, and the
standard deviation 8.164966, each real number with six decimals. The exit status is 0.
(UR-01, UR-02)

### 4.2 A huge stream
An engineer pipes 100 million readings from a sensor archive into `dp-stats`. The tool's
memory use stays flat while it runs, and the summary appears when the stream ends. (UR-03,
UR-04)

### 4.3 Comparing results
Two teams summarize the same file with implementations written in different languages, one on
Linux and one on Windows, and compare the reports with `diff`. They are identical, including
a standard deviation of exactly `0.000000` for a column of identical values. (UR-05, UR-12)

### 4.4 Nothing to summarize
A filter upstream produces no numbers. `dp-stats` prints `0 data items read` and exits with
status 0. (UR-06)

### 4.5 A typo
A data file contains `4,5` on its third line. The tool prints no summary, reports
`bad.txt:3: invalid number '4,5'`, and exits with status 1. (UR-07)

### 4.6 An old data file
A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. The tool
reads it exactly like a file with LF line endings. (UR-09)

### 4.7 Discovery and mistakes
A user runs `dp-stats --help` to see the options, and `dp-stats a.txt b.txt` is rejected
because the tool reads one file. (UR-10, UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings, including locales whose decimal separator is a comma. |
| UC-5 | Must not store the numbers it reads: memory use must not grow with the length of the input. |

## 6. User acceptance criteria

The users will accept `dp-stats` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Data item | One real number read from the input |
| Mean | The sum of the data items divided by their number |
| Population variance | The mean of the squares minus the square of the mean; it measures the spread of the data items around their mean |
| Standard deviation | The square root of the population variance |
| Single pass | Each data item is read once and then discarded; only running totals are kept |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
