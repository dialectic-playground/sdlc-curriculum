# User Requirements Document (URD) — dp-bargraph

| Field | Value |
| :-- | :-- |
| Document ID | URD-16 |
| Project | `16-bargraph` — ASCII Comic Book Bar Graph Generator |
| Product | `dp-bargraph` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-16), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-bargraph` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-16), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-bargraph` turns a short list of named values — in the textbook, the prices of famous comic
books — into a bar graph that can be read in any terminal: each name on its own line, with a
bar of asterisks beneath it. It reads the same data file on every operating system, whether
the file was written with Unix or Windows line endings or still carries the Ctrl-Z marker of
an MS-DOS editor, and it says exactly which line is wrong when the data is not what it expects.

### 1.3 Scope
In scope: reading alternating title and value lines from a file or standard input; drawing one
bar per record at a fixed scale of one asterisk per two units; tolerating CRLF line endings,
a trailing Ctrl-Z, and trailing blank lines; reporting malformed data with a line number; help
and version information.
Out of scope: other scales, vertical bars, labels on the bars, colors, sorting or totals,
values that are negative or not whole numbers, and reading several files.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Draws a quick graph of a small data file by hand on Linux, macOS, or Windows | A readable graph; clear errors |
| SH-2 | Script author | Generates the data with another program and pipes it into the tool | Predictable output bytes and exit statuses |
| SH-3 | Data keeper | Maintains old data files, some written on MS-DOS or Windows | Old and new files read the same way |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want each title in my data printed with a bar beneath it whose length shows its value, so I can compare the values at a glance. | M | SH-1 |
| UR-02 | As a script author, I want to give the tool a file name or pipe the data into it, so it fits into my scripts. | M | SH-2 |
| UR-03 | As a data keeper, I want files with Windows (CRLF) line endings to give exactly the same graph as files with Unix (LF) line endings. | M | SH-3 |
| UR-04 | As a data keeper, I want the Ctrl-Z end-of-file marker that old MS-DOS files carry to be ignored, so the textbook's data file works unchanged. | M | SH-3 |
| UR-05 | As a terminal user, I want blank lines at the end of my file to be ignored, and an empty file to produce an empty graph, not an error. | S | SH-1 |
| UR-06 | As a terminal user, I want titles printed exactly as I wrote them, including spaces and accented letters. | M | SH-1 |
| UR-07 | As a script author, I want a value to be a whole number on a line of its own, and anything else rejected, so mistakes in my data are never drawn as a wrong bar. | M | SH-2 |
| UR-08 | As a script author, I want the graph to contain nothing but the titles and the bars, so I can process it further. | M | SH-2 |
| UR-09 | As a terminal user, I want a bad or missing value reported with the file name and line number, after the bars of the records before it. | M | SH-1 |
| UR-10 | As a terminal user, I want a missing or unreadable file reported clearly, with an exit status that shows the failure. | M | SH-1, SH-2 |
| UR-11 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before anything is read. | M | SH-2 |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-14 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-15 | As a terminal user, I want the graph to appear instantly. | S | SH-1 |
| UR-16 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-5 |

## 4. Usage scenarios

### 4.1 The textbook's data
A user runs `dp-bargraph bargraph.in`. Five comic-book titles appear, each followed by a bar:
46 asterisks for *Detective Comics* (valued at 92), down to 21 for *Whiz Comics* (42). The
Ctrl-Z byte at the end of the file is ignored. (UR-01, UR-04)

### 4.2 In a pipeline
A script produces title and value lines and pipes them into `dp-bargraph > graph.txt`. The
file holds only titles and bars. (UR-02, UR-08)

### 4.3 A file from Windows
A user graphs a file saved by a Windows editor with CRLF line endings and a few blank lines at
the end. The graph is the same as for the Unix version of the file. (UR-03, UR-05)

### 4.4 A typing mistake
A user's file contains `forty-two` where a number belongs, on line 4. The tool draws the bar
for the first record, then reports `dp-bargraph: prices.txt:4: invalid integer 'forty-two'`
and exits with status 1. (UR-07, UR-09)

### 4.5 A mistake on the command line
A user types `dp-bargraph prices.txt more.txt`. The tool explains that only one file is
accepted, points to `--help`, and exits with status 2 without reading anything. (UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must read data files as bytes; it must not depend on the platform's text-mode or newline conventions. |

## 6. User acceptance criteria

The users will accept `dp-bargraph` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Record | A title line followed by a value line |
| Title | The text that names a record, printed above its bar |
| Value | The whole number on a record's second line |
| Bar | A line of asterisks, one for every two units of the value |
| CRLF | The two-byte line ending (carriage return, line feed) used by Windows |
| Ctrl-Z | The byte `0x1A`, which MS-DOS programs wrote at the end of text files |
| Exit status | The integer a process returns to its caller; 0 means success |
