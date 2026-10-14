# User Requirements Document (URD) — dp-line-ed

| Field | Value |
| :-- | :-- |
| Document ID | URD-44 |
| Project | `44-line-editor` — Modal Line-Oriented Text Editor |
| Product | `dp-line-ed` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-44), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-line-ed` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-44), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-line-ed` is a small line editor in the tradition of `ed`. It holds a text file as a list of
lines with a *current line*, and obeys one-letter commands typed one per line: type lines, move
forward, insert, delete, find, substitute, and quit. Nothing is written to the file until the
user quits with `q`. Because the commands come from standard input, the same editor serves a
person at a keyboard and a script that applies a prepared sequence of edits. A mistyped command
is reported clearly and changes nothing, and the session goes on.

### 1.3 Scope
In scope: loading a file (or starting an empty buffer when the file does not exist); the
commands `i`, `d`, `t`, `m`, `f`, `s`, and `q`; writing the buffer back to the file on `q`; an
optional command prompt; preserving the bytes of lines that are not edited; reporting bad
commands, unreadable or unwritable files, and usage errors; help and version information.
Out of scope: undo, line addresses and marks, regular expressions, global substitution, several
buffers, backup files, file locking, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Edits files by hand on Linux, macOS, or Windows, for example over a slow or minimal terminal | Simple commands, immediate feedback, no lost work |
| SH-2 | Script author | Applies prepared edits to files from shell scripts or CI jobs | Predictable output bytes, file contents, and exit statuses |
| SH-3 | Maintainer of legacy files | Edits files that came from Windows or MS-DOS systems | Line endings and other bytes preserved exactly |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want to open a file by naming it, and to start with an empty buffer when the file does not exist yet, so I can edit existing files and create new ones. | M | SH-1 |
| UR-02 | As a terminal user, I want to display the current line, the first line, the last line, or the next few lines. | M | SH-1 |
| UR-03 | As a terminal user, I want to move the current line forward by a number of lines without ever falling off the end of the file. | M | SH-1 |
| UR-04 | As a terminal user, I want to insert any number of new lines after the current line. | M | SH-1 |
| UR-05 | As a terminal user, I want to delete one or more lines after the current line. | M | SH-1 |
| UR-06 | As a terminal user, I want to find the next line that contains a given text and make it the current line. | M | SH-1 |
| UR-07 | As a terminal user, I want to replace a piece of text in the current line, choosing a delimiter that does not occur in the text. | M | SH-1 |
| UR-08 | As a terminal user, I want the file written only when I quit with `q`, so I can abandon a session without changing the file. | M | SH-1, SH-2 |
| UR-09 | As a script author, I want to feed the editor a file of commands on standard input, so I can apply the same edits automatically. | M | SH-2 |
| UR-10 | As a terminal user, I want a mistyped or impossible command reported with its line number while the buffer stays unchanged and the session goes on; as a script author, I want the exit status to tell me afterwards that a command failed. | M | SH-1, SH-2 |
| UR-11 | As a maintainer of legacy files, I want the lines I do not edit written back exactly as they were, including CRLF line endings and any other bytes, and a Ctrl-Z end-of-file mark to be understood. | S | SH-3 |
| UR-12 | As a terminal user, I want a prompt that tells me the editor is waiting for a command, when I ask for it, without the prompts appearing in saved output. | S | SH-1 |
| UR-13 | As a terminal user, I want a built-in help screen that summarizes the commands, and a version query. | M | SH-1, SH-2 |
| UR-14 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, without touching the file. | M | SH-2 |
| UR-15 | As a grader, I want identical output bytes and file contents on Linux, macOS, and Windows, and the tool to follow the curriculum's common CLI conventions. | M | SH-4, SH-5 |
| UR-16 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to handle large files quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 A quick fix
A user runs `dp-line-ed --prompt notes.txt`, sees `*`, types `f 'teh'`, and sees the first line
containing `teh`. The user types `s 'teh' 'the'`, sees the corrected line, and types `q`. The
file now holds the correction, and the exit status is 0. (UR-01, UR-06, UR-07, UR-08, UR-12)

### 4.2 Adding a header to a new file
A user runs `dp-line-ed todo.txt` for a file that does not exist, types `i`, two lines of text,
and a line holding a single `.`, then `q`. The file `todo.txt` now holds the two lines.
(UR-01, UR-04, UR-08)

### 4.3 A scripted edit
A release script runs `dp-line-ed CHANGES.txt < bump.ed`, where `bump.ed` finds a line, deletes
the two lines after it, inserts new text, and ends with `q`. The script checks that the exit
status is 0. (UR-05, UR-09)

### 4.4 A typo
A user types `x` instead of `t`. The editor writes `dp-line-ed: -:4: unknown command 'x'`, the
buffer is unchanged, and the next prompt appears. When the user finally types `q`, the file is
written, and the exit status is 1, so a script would notice the mistake. (UR-10)

### 4.5 Changing one's mind
A user deletes the wrong lines and ends the input with Ctrl-D instead of typing `q`. The editor
reports that the input ended without `q` and leaves the file exactly as it was. (UR-08)

### 4.6 An old file
A file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte. After a
session that changes one word, every other line is written back byte for byte, still with its
CR, and the Ctrl-Z mark is dropped. (UR-11)

### 4.7 Discovery and mistakes on the command line
A user runs `dp-line-ed --help` to see the commands; `dp-line-ed` without a file name is
rejected with a usage error, and nothing is read. (UR-13, UR-14)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: each command's output must appear before the next command is read. |

## 6. User acceptance criteria

The users will accept `dp-line-ed` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Buffer | The lines being edited, held in memory until `q` writes them to the file |
| `[BOF]` | "Beginning of file": the position before the first line, which is never written to the file |
| Current line | The position most commands work from: `[BOF]` or one line of the buffer |
| Command | One line of standard input that starts with a command letter, such as `t e` or `d 3` |
| Insert mode | The state after `i`, in which input lines are added to the buffer until a line holding a single `.` |
| Delimiter | The punctuation character that encloses a pattern or replacement, such as `'` in `f 'cat'` |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
