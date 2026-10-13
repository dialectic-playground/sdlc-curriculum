# User Requirements Document (URD) — dp-echo

| Field | Value |
| :-- | :-- |
| Document ID | URD-01 |
| Project | `01-echo` — Stream Echo & Formatting |
| Product | `dp-echo` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-01), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-echo` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-01), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-echo` writes its arguments to standard output, the way the classic `echo` command does in
every shell. Shell scripts use `echo` constantly to emit text, build files, and pass data down
pipelines, yet the built-in `echo` behaves differently from shell to shell and from operating
system to operating system: some interpret backslashes and some do not, some accept `-n` and
some print it, and Windows tools tend to end lines with CRLF where Unix tools use LF. `dp-echo`
removes that uncertainty. It behaves the same way, byte for byte, on Linux, macOS, and Windows,
and it gives the user explicit control over the trailing newline and over escape sequences such
as tab and carriage return.

### 1.3 Scope
In scope: writing the arguments to standard output separated by spaces; suppressing the trailing
newline; optionally interpreting backslash escape sequences (including ones that produce control
characters, CR, and arbitrary byte values); stopping output early on request; help and version
information; predictable exit statuses.
Out of scope: reading standard input or files, formatted output with conversion specifiers (the
job of `printf`), colors or terminal control beyond what the user explicitly encodes, locale-
dependent behavior, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Terminal user | Runs the command by hand in a shell on Linux, macOS, or Windows | Output that looks exactly like what was typed |
| SH-2 | Script author | Uses the tool in shell scripts, Makefiles, and CI jobs to generate text and files | Identical bytes and exit statuses on every platform; no surprises with leading dashes |
| SH-3 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-4 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a terminal user, I want the tool to print its arguments separated by single spaces and followed by a newline, so I can display a message. | M | SH-1 |
| UR-02 | As a script author, I want to suppress the trailing newline, so I can build a line from several pieces or write a file that does not end in a newline. | M | SH-2 |
| UR-03 | As a script author, I want to opt in to backslash escape sequences (tab, newline, carriage return, and so on), so I can produce control characters without typing them literally. | M | SH-2 |
| UR-04 | As a script author, I want backslashes to be printed literally unless I opt in, so that paths such as `C:\temp` and other text containing backslashes are never altered by accident. | M | SH-2 |
| UR-05 | As a script author, I want to stop all further output from inside an argument, so I can end the output exactly where I choose, without the trailing newline. | S | SH-2 |
| UR-06 | As a script author, I want to emit any byte value by its octal or hexadecimal code, so I can produce bytes that cannot be typed. | S | SH-2 |
| UR-07 | As a script author, I want the newline the tool adds to be a single LF on every operating system, including Windows, so files generated on any platform are identical. | M | SH-2, SH-4 |
| UR-08 | As a script author, I want to produce Windows-style CRLF line endings deliberately when a file format or protocol requires them, so I control line endings instead of the platform. | M | SH-2 |
| UR-09 | As a script author, I want arguments that merely look like options (for example `--`, `-x`, or `-`) to be printed as text rather than rejected, because `echo` is used to print arbitrary data. | M | SH-2 |
| UR-10 | As a script author, I want the tool always to succeed (exit status 0) when its output was written, so I can chain it with `&&`, and to report failure when the output could not be written. | M | SH-2 |
| UR-11 | As a terminal user, I want text containing non-ASCII characters (for example `Zoë` or `日本語`) to be printed exactly as I typed it. | M | SH-1 |
| UR-12 | As a terminal user, I want a built-in help screen that lists every option and escape sequence, so I can use the tool without other documentation. | M | SH-1 |
| UR-13 | As a script author, I want to query the tool's version, so I can confirm which specification it implements. | M | SH-2 |
| UR-14 | As a learner, I want the tool to follow the curriculum's common CLI conventions except where `echo` traditionally differs, and I want every such difference to be stated explicitly. | M | SH-3 |
| UR-15 | As a script author, I want the tool to start and finish instantly, even with long arguments. | S | SH-2 |
| UR-16 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language. | M | SH-4 |

## 4. Usage scenarios

### 4.1 Printing a message
A user types `dp-echo Build finished` and sees `Build finished` on one line. The command exits
with status 0. (UR-01, UR-10)

### 4.2 Building a line in pieces
A script runs `dp-echo -n 'Progress: '` followed by `dp-echo done`. The terminal shows
`Progress: done` on a single line. (UR-02)

### 4.3 Tab-separated output
A script writes a header line with `dp-echo -e 'name\tsize'`. The output contains a real tab
character between the two words. Without `-e`, `dp-echo 'name\tsize'` prints the backslash and
the `t` unchanged. (UR-03, UR-04)

### 4.4 Line endings across platforms
A developer on Windows runs `dp-echo hello > a.txt` and a colleague on Linux runs the same
command. Both files contain exactly the six bytes `hello` + LF. When a network protocol
requires CRLF, the developer writes `dp-echo -ne 'HELO example\r\n'` and gets exactly that
CRLF, on every platform. (UR-07, UR-08)

### 4.5 Printing data that looks like options
A script prints a variable whose value happens to be `--` or `-x`. `dp-echo` prints the value as
text and exits 0; it never reports an "invalid option". (UR-09)

### 4.6 Stopping early
A script writes `dp-echo -e 'Continue? [y/N] \c'` to print a prompt that leaves the cursor on the
same line. (UR-05)

### 4.7 Discovery
A user runs `dp-echo --help` to see the options and escapes, and `dp-echo --version` to check the
version. (UR-12, UR-13)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must not depend on the platform's native line-ending convention; output bytes are fixed by the specification, not by the operating system. |

## 6. User acceptance criteria

The users will accept `dp-echo` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Argument | One word of the command line after the command name, as delivered by the shell |
| Escape sequence | A backslash followed by one or more characters that together stand for another byte, such as `\t` for a tab |
| LF | Line feed, byte `0x0A`; the Unix line terminator |
| CR | Carriage return, byte `0x0D` |
| CRLF | The two-byte sequence CR LF; the traditional Windows line terminator |
| Trailing newline | The LF that `dp-echo` writes after the last argument unless told not to |
| Exit status | The integer a process returns to its caller; 0 means success |
