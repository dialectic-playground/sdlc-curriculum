# User Requirements Document (URD) — dp-wc

| Field | Value |
| :-- | :-- |
| Document ID | URD-04 |
| Project | `04-wc` — Word, Line, and Byte Counter |
| Product | `dp-wc` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-04), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-wc` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-04), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-wc` counts the lines, words, characters, and bytes in files and in standard input, and
reports the length of the longest line. Unlike traditional `wc` implementations, whose word and
character counts change with the user's locale and whose column widths depend on file sizes,
`dp-wc` gives the same answer, in the same layout, for the same bytes on every operating system
and in every locale. Text in UTF-8, including text that contains damaged or truncated byte
sequences, is counted predictably.

### 1.3 Scope
In scope: counting lines, words, UTF-8 characters, and bytes; reporting the maximum line length;
choosing which counts to print; reading several files with a summary total; reading standard
input; reporting unreadable files without stopping; help and version information.
Out of scope: locale-dependent word or character rules, display-width (column) calculation for
wide or combining characters, tab expansion, reading a list of file names from a file, directory
traversal, and any form of output other than plain decimal columns.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Runs the command by hand on Linux, macOS, or Windows to size up files | Readable, aligned output; helpful errors |
| SH-2 | Script author | Uses the counts in shell scripts, build checks, and CI jobs | Exact, predictable output bytes and exit statuses |
| SH-3 | Data engineer | Measures large logs and multilingual text files | Correct character counts for UTF-8, constant memory on huge inputs |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to see the number of lines, words, and bytes in a file with no options, so I can size it up quickly. | M | SH-1 |
| UR-02 | As a script author, I want to ask for only the counts I need (lines, words, characters, bytes, or longest line), so I can parse the output easily. | M | SH-2 |
| UR-03 | As a script author, I want the counts always printed in the same column order, whatever order I give the options in, so my parsing never breaks. | M | SH-2 |
| UR-04 | As a data engineer, I want UTF-8 text counted in characters (code points), not just bytes, so multilingual text is measured correctly. | M | SH-3 |
| UR-05 | As a data engineer, I want files that contain invalid or truncated UTF-8 to be counted by a fixed, documented rule instead of failing or giving platform-dependent results. | M | SH-3 |
| UR-06 | As a script author, I want words and characters counted the same way in every locale, so results do not change between my laptop and the CI server. | M | SH-2, SH-5 |
| UR-07 | As a terminal user, I want to count several files at once and see a total line, so I can compare them and see the sum. | M | SH-1 |
| UR-08 | As a terminal user, I want the numbers in the output to line up in columns, so the report is easy to read. | S | SH-1 |
| UR-09 | As a script author, I want to pipe data into the tool and count it, so I can measure the output of other commands. | M | SH-2 |
| UR-10 | As a terminal user, I want a missing or unreadable file reported clearly, while the other files are still counted, and I want the exit status to show that something failed. | M | SH-1, SH-2 |
| UR-11 | As a terminal user, I want to know the length of the longest line, so I can check files against line-length rules. | S | SH-1 |
| UR-12 | As a data engineer, I want to count files far larger than memory, quickly. | M | SH-3 |
| UR-13 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-14 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-2 |
| UR-15 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-16 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-17 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-5 |

## 4. Usage scenarios

### 4.1 Sizing up a file
A user types `dp-wc notes.txt` and sees one line with three numbers — lines, words, and bytes —
followed by the file name. The command exits with status 0. (UR-01)

### 4.2 Counting lines in a pipeline
A script runs `some-command | dp-wc -l` and receives a single number followed by a line feed,
with no file name and no padding, which it can use directly. (UR-02, UR-09)

### 4.3 Multilingual text
A translator runs `dp-wc -m -c greeting.txt` on a file containing `Καλημέρα`. The character count
is smaller than the byte count, because each Greek letter is one character but two bytes. The
character count comes first, even if the options were typed as `-c -m`. (UR-03, UR-04)

### 4.4 A damaged file
A data engineer counts a log file that contains a few corrupted bytes. `dp-wc -m` does not fail;
each corrupted byte is counted as one character, so the result is the same on every machine.
(UR-05, UR-06)

### 4.5 Several files
A user runs `dp-wc chapter1.txt chapter2.txt`. Each file gets one line, and a final `total` line
gives the sums. All numbers are aligned in columns. (UR-07, UR-08)

### 4.6 A missing file
A user runs `dp-wc a.txt missing.txt b.txt`. The tool prints an error for `missing.txt`, counts
`a.txt` and `b.txt`, prints the total for those two, and exits with status 1. (UR-10)

### 4.7 Line-length check
A reviewer runs `dp-wc -L src.txt` to confirm that no line is longer than 100 characters.
(UR-11)

### 4.8 A large log
A data engineer counts a 20 GB log on a machine with 4 GB of memory. The tool finishes and uses
a small, fixed amount of memory. (UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must treat file contents as raw bytes; it must not depend on the platform's text-mode or newline conventions. |

## 6. User acceptance criteria

The users will accept `dp-wc` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Line | For counting purposes, one line feed (LF) byte; a final line without an LF is not counted as a line |
| Word | A maximal run of bytes that are not ASCII whitespace |
| Character | A Unicode code point encoded in UTF-8, or a single byte that is not part of a valid UTF-8 sequence |
| Byte | One octet of input |
| Total line | The summary line labelled `total` printed when more than one file is given |
| Exit status | The integer a process returns to its caller; 0 means success |
