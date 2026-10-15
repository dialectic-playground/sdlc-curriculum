<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-env](#software-requirements-specification-srs--dp-env)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
    - [1.5 Deviations from CLI-CONV](#15-deviations-from-cli-conv)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
    - [7.1 Black-box tests](#71-black-box-tests)
    - [7.2 Integration tests](#72-integration-tests)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-env

| Field                     | Value                                        |
| :------------------------ | :------------------------------------------- |
| Document ID               | SRS-08                                       |
| Project                   | `08-env-run` — Environment Execution Wrapper |
| Product                   | `dp-env` (canonical name)                    |
| Version                   | 1.0.0                                        |
| Status                    | Approved (pre-written by the curriculum)     |
| Parent document           | `URD.md` (URD-08)                            |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018         |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-env`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
standard output and standard error, and identical exit statuses, for every invocation covered
by the black-box tests. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope

`dp-env` builds an environment from its own environment (or an empty one), command-line
removals, and command-line assignments. It then either prints that environment or runs a
command with it, optionally in another working directory. While the command runs, `dp-env`
waits for it, relays termination signals to it, and finally exits with a status derived from
the command's exit status.

### 1.3 Definitions

| Term                  | Definition                                                                                                                                                                                                                                                                          |
| :-------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                    | The line-feed byte, `0x0A`                                                                                                                                                                                                                                                          |
| NUL                   | The zero byte, `0x00`                                                                                                                                                                                                                                                               |
| Operand               | A command-line token that is not an option and not the `--` terminator (see FR-01)                                                                                                                                                                                                  |
| Assignment            | An operand of the form `NAME=VALUE`, recognized as described in FR-03                                                                                                                                                                                                               |
| Entry                 | One variable of an environment: a NAME and a VALUE, both text                                                                                                                                                                                                                       |
| Inherited environment | The environment `dp-env` itself received when it was started                                                                                                                                                                                                                        |
| Resulting environment | The environment built by FR-05; it is printed (FR-09) or given to the child (FR-13)                                                                                                                                                                                                 |
| COMMAND               | The first operand that follows the optional `-` (FR-02) and the assignments (FR-03)                                                                                                                                                                                                 |
| ARG                   | Every operand after COMMAND, passed to the child unchanged                                                                                                                                                                                                                          |
| Child                 | The process `dp-env` creates to run COMMAND                                                                                                                                                                                                                                         |
| Path separator        | `/` on POSIX. On Windows: `/`, `\`, or a colon as the second character (`C:prog`)                                                                                                                                                                                                   |
| List separator        | The character separating `PATH` elements: `:` on POSIX, `;` on Windows                                                                                                                                                                                                              |
| Name match            | On POSIX, two names match when they are identical byte sequences. On Windows, they match when they are equal ignoring case, compared ordinally after simple upper-casing of each character (for ASCII: `a`–`z` equals `A`–`Z`), which is how Windows itself compares variable names |
| Forwarded signal      | SIGINT, SIGTERM, or SIGHUP (POSIX only)                                                                                                                                                                                                                                             |

### 1.4 References

- URD-08: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- POSIX.1-2017, `env` utility, `exec` family, `waitpid`, signal concepts
- Microsoft Win32 documentation: `CreateProcessW`, environment blocks,
  `GetExitCodeProcess`, `SetConsoleCtrlHandler`

### 1.5 Deviations from CLI-CONV

CLI-CONV applies in full except where this table says otherwise. Each deviation keeps
`dp-env` compatible with the POSIX `env` utility or makes the child's exit status
unambiguous.

| CLI-CONV item                    | Override in this SRS                                                                                                                                                                     | Reason                                                                                                            |
| :------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------- |
| CONV-10 (interleaving)           | Options are recognized only **before the first operand**. The first operand ends option processing, and every later token is an operand, even if it starts with `-` (FR-01).             | Tokens after COMMAND belong to the command (`dp-env ls -l`).                                                      |
| CONV-10 (`-` means stdin)        | A lone `-` as the first operand means `-i` (FR-02). `dp-env` never reads standard input.                                                                                                 | POSIX `env -`.                                                                                                    |
| CONV-11 (last wins)              | `-u` is cumulative: every occurrence removes its own NAME (FR-05).                                                                                                                       | Removing several variables is the normal use.                                                                     |
| CONV-12 (scan order)             | The scan ends at the first operand, so `--help` or `--version` after an operand is an operand. The scan checks option _syntax_ only; values and operands are validated after it (FR-07). | Follows from the CONV-10 override.                                                                                |
| CONV-14, CONV-18 (exit status 2) | Usage errors print the CONV-13 message and the `Try` line, but exit with status **125** (§3.7).                                                                                          | Status 2 is a common command exit status; 125 cannot be confused with one that `dp-env` propagates in normal use. |
| CONV-16 (path diagnostics)       | Errors about `-C` and COMMAND use the formats in §6, and COMMAND diagnostics add the reason `Exec format error`.                                                                         | Names the failing step; matches POSIX `env`.                                                                      |
| CONV-17 (continue after errors)  | Any error stops `dp-env` before the environment is printed or the command is started.                                                                                                    | There is only one operation.                                                                                      |
| CONV-18 (exit statuses)          | Replaced by the table in §3.7.                                                                                                                                                           | `dp-env` propagates the child's exit status.                                                                      |

## 2. Overall description

### 2.1 Product perspective

`dp-env` is a standalone executable. Its interfaces are the command line, the inherited
environment, the working directory, standard output, standard error, the exit status, the
child process it creates, and (on POSIX) the signals it receives. The child inherits
`dp-env`'s standard input, standard output, and standard error.

### 2.2 Product functions

1. Build an environment from the inherited one (or an empty one), removals, and assignments.
2. Print that environment, sorted by name, with LF or NUL terminators.
3. Resolve a command name using the command search path.
4. Run the command directly, with the new environment and an optional working directory.
5. Relay termination signals to the child and wait for it to exit.
6. Report the child's exit status, or a distinct status for each way of failing.
7. Display help and version information, and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, plus the process-management obligations
  in §5 that make the observable behavior reliable.

### 2.4 Assumptions

- The terminal or consumer accepts UTF-8.
- On POSIX, environment variables and arguments are byte strings, interpreted as UTF-8 where
  they are compared or echoed (CONV-05). On Windows, they are UTF-16 and converted to and
  from UTF-8.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-env [OPTION]... [-] [NAME=VALUE]... [COMMAND [ARG]...]
dp-env --help
dp-env --version
```

### 3.2 Options

| Short | Long                   | Argument        | Default | Description                                                                           |
| :---- | :--------------------- | :-------------- | :------ | :------------------------------------------------------------------------------------ |
| `-i`  | `--ignore-environment` | none            | off     | Start from an empty environment instead of the inherited one                          |
| `-u`  | `--unset`              | NAME (required) | —       | Remove every entry whose name matches NAME. May be repeated; every occurrence applies |
| `-C`  | `--chdir`              | DIR (required)  | —       | Start COMMAND with DIR as its working directory. Requires COMMAND                     |
| `-0`  | `--null`               | none            | off     | When printing, end each entry with NUL instead of LF. Forbidden with COMMAND          |
| —     | `--help`               | none            | —       | Print the help text and exit 0                                                        |
| —     | `--version`            | none            | —       | Print the version line and exit 0                                                     |

Option syntax (bundling, attached and separate values, `--name=value`, the `--` terminator)
follows CONV-07 … CONV-09, with the scan limited as described in FR-01. For example,
`-iu X`, `-i -u X`, `-i --unset=X`, and `-iuX` are equivalent. `-C` given more than once:
the last occurrence wins (CONV-11).

### 3.3 Operands

In order: an optional lone `-` (FR-02), zero or more assignments (FR-03), then optionally
COMMAND followed by its ARGs. Operands that contain `=` and come after COMMAND are ARGs, not
assignments.

### 3.4 Standard input

Not read by `dp-env`. It is inherited, unread, by the child.

### 3.5 Standard output

Without COMMAND: the resulting environment (FR-09). With COMMAND: nothing from `dp-env`
itself. The child writes to the same standard output.

### 3.6 Standard error

Diagnostics only (§6). Nothing when `dp-env` succeeds. The child writes to the same standard
error.

### 3.7 Exit status

| Status    | Condition                                                                                                                                                                     |
| :-------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0         | Without COMMAND: the environment was printed. Also after `--help` / `--version`                                                                                               |
| 125       | `dp-env` itself failed: a usage error (CONV-13 messages and §6), an invalid `-u` NAME or assignment, a `-C` directory that cannot be entered, or a write error while printing |
| 126       | COMMAND was found but could not be started (FR-11, FR-12)                                                                                                                     |
| 127       | COMMAND was not found (FR-11, FR-12)                                                                                                                                          |
| _S_       | The child exited with exit status _S_ (FR-15). _S_ may be any value, including 125–127                                                                                        |
| 128 + _N_ | POSIX only: the child was terminated by signal _N_ (FR-15)                                                                                                                    |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
Unless stated otherwise, every failure in this section is reported with the diagnostic listed
in §6, writes nothing to standard output, and starts no process.

**FR-01: Option scanning.**
Arguments MUST be scanned from left to right with the syntax of CONV-07 … CONV-09 and the
options in §3.2. The scan MUST stop at the first token that is not an option: a token that does
not start with `-`, or that is exactly `-`. That token and every token after it are operands.
The token `--` also stops the scan; it is consumed, and every later token is an operand. If
the scan reaches `--help` or `--version`, the help or version output is printed and the tool
exits 0 (CONV-12), unless an earlier token was a usage error. Unknown options, missing option
values, and values attached to `--help`, `--version`, `--ignore-environment`, or `--null` are
usage errors with the CONV-13 messages, followed by the CONV-14 `Try` line, and exit status
**125**. Long options MUST NOT be abbreviated.
_AC:_ `dp-env -x` → stderr `dp-env: invalid option -- 'x'` and the `Try` line, exit 125.
`dp-env DP_X=1 -i` treats `-i` as COMMAND (→ FR-11, exit 127). `dp-env -u` → `dp-env: option
requires an argument -- 'u'`, exit 125. _(UR-06, UR-11, UR-16)_

**FR-02: Lone `-`.**
If the first operand is exactly `-`, it MUST be removed from the operands and the tool MUST
behave as if `-i` had been given. This applies whether or not the operand follows `--`. Only
the first operand is examined; a later `-` is an ordinary operand (for example, COMMAND `-`).
_AC:_ `dp-env - A=1 B= A=2` prints `A=2` LF `B=` LF and exits 0. _(UR-03)_

**FR-03: Assignments.**
Starting with the first operand (after any `-` removed by FR-02), each operand that contains
at least one `=` is an assignment. The first operand without `=` is COMMAND, and recognition
of assignments stops there. In an assignment, NAME is the text before the first `=` and VALUE
is everything after it; VALUE may be empty and may contain `=`. NAME MUST NOT be empty: an
assignment that starts with `=` is reported as `dp-env: cannot set '<operand>': Invalid
argument` (with the whole operand between the quotes) and exit status 125, without the `Try`
line. Any other NAME is accepted as given.
_AC:_ `dp-env -i b=3 C=x=y A=1` prints `A=1`, `C=x=y`, `b=3`, each followed by LF.
`dp-env -i =x` → `dp-env: cannot set '=x': Invalid argument`, exit 125. _(UR-01, UR-11)_

**FR-04: Removal names.**
Each `-u` value MUST be non-empty and MUST NOT contain `=`. Otherwise the tool reports
`dp-env: cannot unset '<NAME>': Invalid argument` and exits with status 125, without the
`Try` line. Removing a name that is not present is not an error.
_AC:_ `dp-env -u A=B -i` → `dp-env: cannot unset 'A=B': Invalid argument`, exit 125.
_(UR-02, UR-11)_

**FR-05: Building the resulting environment.**
The resulting environment MUST be built in this order:

1. Start with an empty environment if `-i` or a lone `-` was given; otherwise start with a copy
   of the inherited environment.
2. For each `-u` NAME, in command-line order, remove every entry whose name matches NAME.
3. For each assignment, in command-line order, remove every entry whose name matches NAME,
   then add the entry NAME=VALUE, spelled exactly as given. A later assignment to a matching
   name therefore wins.

An empty VALUE sets the variable to the empty string; it does not remove it. `dp-env` MUST NOT
add any variable of its own, and MUST NOT change any entry it was not asked to change. Locale
variables are passed through like any other variable (CONV-06 governs only `dp-env`'s own
behavior).
_AC:_ With `DP_X=old` inherited, `dp-env DP_X=new DP_Y=added CMD` gives the child
`DP_X=new` and `DP_Y=added`; with `DP_X=hello` inherited, `dp-env -u DP_X CMD` gives the child
no `DP_X`. _(UR-01, UR-02, UR-03)_

**FR-06: Option conflicts.**
After FR-03 has identified COMMAND: if `-0` was given and COMMAND is present, the tool MUST
report the usage error `dp-env: cannot specify --null (-0) with command`. If `-C` was given and
COMMAND is absent, it MUST report the usage error `dp-env: must specify command with --chdir
(-C)`. Both are followed by the `Try` line and exit status 125.
_AC:_ `dp-env -C subdir` → the `--chdir` message, the `Try` line, exit 125. `dp-env -0 CMD` →
the `--null` message, the `Try` line, exit 125. _(UR-11)_

**FR-07: Validation order and atomicity.**
Checks MUST be made in this order, and only the first failure is reported:

1. Option syntax, during the scan (FR-01), including `--help` / `--version` handling.
2. Each `-u` value, in command-line order (FR-04).
3. Each assignment, in command-line order (FR-03).
4. Option conflicts: first `-0` with COMMAND, then `-C` without COMMAND (FR-06).
5. Changing the working directory (FR-10).
6. Resolving COMMAND (FR-11).
7. Starting the child (FR-12).

Because validation of values follows the scan, `dp-env -u '' --help` prints the help text and
exits 0. No output is written and no process is started before checks 1–6 have passed.
_AC:_ `dp-env -u = =x` reports the `-u` error, not the assignment error. _(UR-11)_

**FR-08: Windows variable names.**
On Windows, every comparison of variable names (FR-04 removal, FR-05 replacement, the `PATH`
and `PATHEXT` lookups of FR-11) MUST use the Windows name match defined in §1.3. An entry
created by an assignment takes the spelling given in that assignment, replacing the previous
spelling: `dp-env Path=C:\bin` replaces the inherited `PATH` entry with one named `Path`.
Inherited entries keep the spelling reported by the operating system. Entries whose name
begins with `=` (the per-drive current-directory entries such as `=C:=C:\work`) are not part of
the environment as `dp-env` models it: they are never printed, and they cannot be named by
`-u` or by an assignment (FR-03, FR-04 reject such names). Whether they reach the child is
unspecified. On POSIX, names match only when they are identical, so `a` and `A` are different
variables.
_AC:_ On Windows with `Path` inherited, `dp-env -u PATH CMD` gives the child no `Path` entry.
_(UR-13)_

**FR-09: Printing the environment.**
When there is no COMMAND, the tool MUST write every entry of the resulting environment to
standard output as the UTF-8 bytes of NAME, `=`, and VALUE, followed by a terminator: LF by
default, NUL with `-0`. Entries MUST be sorted in ascending byte-wise order of the UTF-8
encoding of NAME (as spelled, case-sensitive, locale-independent). An empty resulting
environment produces no output. Values are written exactly as they are, including any LF they
contain; only `-0` makes such output unambiguous. The exit status is 0.
_AC:_ `dp-env -i` → empty stdout, exit 0. `dp-env -i -0 B=2 A=1` → stdout bytes
`A=1` NUL `B=2` NUL. _(UR-03, UR-04, UR-14, UR-15)_

**FR-10: Working directory.**
With `-C DIR`, the child MUST start with DIR as its working directory. DIR is interpreted
relative to `dp-env`'s own working directory. The change MUST take effect **before** command
resolution: a COMMAND that contains a path separator and is relative, and relative `PATH`
elements, are interpreted relative to DIR. If DIR cannot be used as a working directory, the
tool reports `dp-env: cannot change directory to '<DIR>': <reason>` and exits with status 125,
where `<reason>` comes from the CONV-16 table: `No such file or directory` if DIR does not
exist, `Not a directory` if DIR exists but is not a directory, `Permission denied` if access is
refused, and `Input/output error` otherwise. DIR is echoed exactly as given (CONV-19).
_AC:_ `dp-env -C subdir {PYTHON} ../child.py @cwd` prints `cwd=subdir`. `dp-env -C
no-such-dir CMD` → `dp-env: cannot change directory to 'no-such-dir': No such file or
directory`, exit 125. _(UR-05, UR-09)_

**FR-11: Command resolution.**
COMMAND MUST be resolved to a file as follows. The _candidates_ for a base path B are: on
POSIX, B alone. On Windows, B alone if the final component of B ends, ignoring case, with one
of the PATHEXT extensions; otherwise B followed by each PATHEXT extension in order. The
PATHEXT extensions are the non-empty `;`-separated elements of the resulting environment's
`PATHEXT` if it has one, otherwise of the inherited `PATHEXT`, otherwise of `.COM;.EXE;.BAT;.CMD`.
A candidate _exists_ when the file system reports an object at that path that is not a
directory. Any failure to query the path counts as "does not exist".

1. If COMMAND contains a path separator, it is used as a path. If that path names an existing
   directory, the result is exit status 126 with reason `Is a directory`. Otherwise the first
   existing candidate of COMMAND is selected. If none exists, the result is exit status 127
   with reason `No such file or directory`.
2. If COMMAND is empty, the result is exit status 127 with reason `No such file or directory`.
3. Otherwise COMMAND is searched for in the _search path_: the value of `PATH` in the
   resulting environment if it has such an entry, otherwise the inherited `PATH`, otherwise
   the empty string. The search path is split at the list separator; empty elements are
   skipped (they do **not** mean the current directory). For each element E, in order, the
   candidates of `E` + `/` + COMMAND are examined in order. The first candidate that exists
   and, on POSIX, is executable by the effective user is selected. If no candidate is selected,
   the result is exit status 126 with reason `Permission denied` if at least one candidate
   existed (POSIX: existed but was not executable), and otherwise exit status 127 with reason
   `No such file or directory`.

The current directory is never searched implicitly. On Windows, this means the
implementation MUST resolve the file itself and MUST NOT rely on the `CreateProcess` search,
which also looks in the current directory and the application directory. Failures are
reported as `dp-env: '<COMMAND>': <reason>`, with COMMAND exactly as given.
_AC:_ `dp-env dp-env-no-such-command` → `dp-env: 'dp-env-no-such-command': No such file or
directory`, exit 127. `dp-env ./subdir`, where `subdir` is a directory → `dp-env: './subdir':
Is a directory`, exit 126. _(UR-07, UR-09)_

**FR-12: Failure to start the selected file.**
If the operating system refuses to start the selected file, the tool MUST report
`dp-env: '<COMMAND>': <reason>` and exit as follows:

| Failure                                                                                            | Exit status | `<reason>`                  |
| :------------------------------------------------------------------------------------------------- | :---------- | :-------------------------- |
| ENOENT, `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND` (for example, a missing script interpreter) | 127         | `No such file or directory` |
| EACCES, EPERM, `ERROR_ACCESS_DENIED`                                                               | 126         | `Permission denied`         |
| ENOEXEC, `ERROR_BAD_EXE_FORMAT` (not a valid executable)                                           | 126         | `Exec format error`         |
| ENOTDIR                                                                                            | 126         | `Not a directory`           |
| EISDIR                                                                                             | 126         | `Is a directory`            |
| Any other failure, including failure to create the process                                         | 126         | `Input/output error`        |

`dp-env` MUST NOT retry a file that failed with ENOEXEC through a shell.
_AC:_ (POSIX, integration) `dp-env ./data.txt`, where `data.txt` is a regular file without
execute permission → `dp-env: './data.txt': Permission denied`, exit 126. _(UR-09)_

**FR-13: Running the command.**
The child MUST be started directly, without a shell, with:

- the selected file as the program;
- an argument vector consisting of COMMAND exactly as given (as `argv[0]`), followed by every
  ARG unchanged. On Windows, the command line MUST be built so that a child using the standard
  Microsoft C runtime rules (`CommandLineToArgvW`) recovers exactly COMMAND and the ARGs,
  including empty arguments and arguments containing spaces, quotes, and backslashes;
- exactly the resulting environment;
- the working directory from FR-10, or `dp-env`'s own;
- `dp-env`'s standard input, standard output, and standard error, and no other open files or
  handles of `dp-env`.

`dp-env` MUST then wait until the child has terminated. It writes nothing to standard output
or standard error while the child runs, or afterwards on success.
_AC:_ `DP_Y=1 dp-env -u DP_Y -- {PYTHON} child.py DP_Y` prints `DP_Y=<unset>`: `--` is
consumed and the child receives the remaining tokens. _(UR-01, UR-06)_

**FR-14: Signal forwarding (POSIX).**
On POSIX, `dp-env` MUST stay alive while the child runs, and relay each forwarded signal
(SIGINT, SIGTERM, SIGHUP) that it receives to the child with the same signal number:

1. Handlers for the forwarded signals MUST be installed before the child is created. A
   forwarded signal that arrives before the child exists MUST be delivered to the child as soon
   as it has been created.
2. After relaying a signal, `dp-env` MUST continue waiting. It MUST NOT terminate because of a
   forwarded signal, and it MUST NOT kill the child by any other means. If the child ignores or
   handles the signal, `dp-env` keeps waiting.
3. A forwarded signal whose disposition was "ignore" when `dp-env` started MUST remain
   ignored: it is not forwarded, and the child inherits the "ignore" disposition (this is how
   `nohup` composes with `dp-env`). The child MUST start with every other signal at the
   disposition `dp-env` inherited, and with an empty signal mask, so that `dp-env`'s own
   handlers never leak into the child.
4. Signals that the terminal sends to the whole foreground process group (Ctrl+C, for example)
   reach the child directly as well as through `dp-env`. An implementation MAY avoid relaying
   a signal that it can determine was sent by the terminal driver; otherwise the child may see
   such a signal twice.
5. Other signals keep their default effect on `dp-env`.

_AC:_ Integration tests IT-01 … IT-04 (§7.2). _(UR-10)_

**FR-15: Exit status propagation.**
When the child terminates, `dp-env` MUST exit as follows:

- The child exited normally with status _S_: `dp-env` exits with _S_. On POSIX _S_ is 0–255.
  On Windows, _S_ is the child's full 32-bit exit code (as returned by `GetExitCodeProcess`),
  and `dp-env` exits with the same 32-bit value, including values such as `0xC000013A` (the
  code of a process ended by Ctrl+C).
- POSIX only: the child was terminated by signal _N_: `dp-env` exits with status 128 + _N_
  (for example, 143 for SIGTERM and 137 for SIGKILL). `dp-env` does not re-raise the signal
  against itself and does not produce a core dump.

_AC:_ `dp-env {PYTHON} child.py @exit=3` exits 3. IT-02 and IT-05 (§7.2). _(UR-08)_

**FR-16: Console control events (Windows).**
On Windows, while the child runs, `dp-env` MUST NOT terminate because of a Ctrl+C or
Ctrl+Break console control event. The console delivers these events to every process attached
to it, including the child, so `dp-env` does not relay them; it keeps waiting and then exits
per FR-15. The mechanism `dp-env` uses to ignore the events MUST NOT be inherited by the child.
In particular, `SetConsoleCtrlHandler(NULL, TRUE)` MUST NOT be used, because the child would
inherit it and ignore Ctrl+C as well. A handler routine that returns `TRUE` is suitable.
_AC:_ Integration test IT-06 (§7.2). _(UR-10)_

**FR-17: Help.**
`--help` MUST write the help text from user-manual §"HELP OUTPUT" byte-for-byte to standard
output and exit 0, following FR-01.
_AC:_ `dp-env --help` matches the user manual exactly. _(UR-12)_

**FR-18: Version.**
`--version` MUST write `dp-env (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-12)_

**FR-19: Write errors.**
If writing the printed environment to standard output fails because the reader has gone away,
CONV-25 applies. Any other write failure MUST be reported as `dp-env: write error`, with exit
status 125.
_AC:_ Inspection. _(UR-09)_

## 5. Non-functional requirements

| ID     | Category                                | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Verification                 |
| :----- | :-------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------- |
| NFR-01 | Portability                             | Standard output and standard error MUST be byte-identical on Linux, macOS, and Windows for every black-box test, and every generated line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | CI black-box tests on 3 OSes |
| NFR-02 | Process creation (cross-platform focus) | On POSIX, the child MUST be created with `fork` + `execve`, `vfork` + `execve`, or `posix_spawn`, given an explicit program path, argument vector, and environment, and MUST be reaped with `waitpid`, retrying on `EINTR`. `dp-env` MUST NOT replace itself with the command through `exec` alone, because FR-14 and FR-15 require it to stay alive. On Windows, the child MUST be created with `CreateProcessW`, an explicit `lpApplicationName`, a `CREATE_UNICODE_ENVIRONMENT` block built from the resulting environment (entries SHOULD be sorted by name, ignoring case, as the Win32 documentation recommends), and handle inheritance limited to the three standard handles. The child MUST be waited for with `WaitForSingleObject`, its exit code read with `GetExitCodeProcess`, and both process and thread handles closed. | Code review, IT tests        |
| NFR-03 | Security                                | The command and its arguments MUST never be interpreted by a shell or by any other command interpreter in `dp-env`. Command resolution MUST NOT search the current directory implicitly (FR-11). `dp-env` MUST NOT log or print environment values except in FR-09.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      | Inspection, FR-11 tests      |
| NFR-04 | Performance                             | Time from `dp-env` starting to the child starting MUST be under 20 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, excluding the time to search a `PATH` on slow file systems. Printing an environment of 10,000 entries MUST take under 200 ms. Sorting MUST be O(_n_ log _n_) in the number of entries.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Measurement                  |
| NFR-05 | Memory                                  | Peak memory MUST stay under 32 MiB plus twice the total size of the resulting environment. `dp-env` MUST NOT buffer the child's output: the child writes directly to the inherited standard streams.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | Measurement, inspection      |
| NFR-06 | Resource hygiene                        | No file descriptor or handle other than the three standard streams may be inherited by the child (close-on-exec on POSIX, an explicit inheritance list or `bInheritHandles` with only standard handles on Windows). `dp-env` MUST NOT leave a zombie child: it reaps the child before exiting.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Integration test, inspection |
| NFR-07 | Signal safety                           | POSIX signal handlers MUST be async-signal-safe: they only record the signal or call `kill`. The time between installing handlers and creating the child MUST NOT lose a signal (FR-14 item 1).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Code review, IT-01 … IT-04   |
| NFR-08 | Robustness                              | The tool MUST NOT crash, panic, or print a stack trace for any argument list or environment content, including empty values, values containing `=` or LF, and very long values (CONV-24).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                | Unit + black-box tests       |
| NFR-09 | Maintainability                         | Argument scanning, environment construction, printing, command resolution, process creation, signal handling, and exit-status mapping MUST be separate units. Platform-specific code MUST be isolated behind one process-spawning interface.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Design review                |
| NFR-10 | Testability                             | Environment construction (FR-05, FR-08), command resolution (FR-11, with an injectable file-system query), and exit-status mapping (FR-15) MUST be unit-testable without starting processes.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Code review                  |
| NFR-11 | Build                                   | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | CI                           |

## 6. Diagnostics (complete list)

Usage errors (rows marked **U**) are followed by `Try 'dp-env --help' for more information.`
All other diagnostics are a single line. Text in angle brackets is replaced as described.

| Trigger                                                                        | Exact first line                                                        | U   | Exit |
| :----------------------------------------------------------------------------- | :---------------------------------------------------------------------- | :-- | :--- |
| Unknown short option `x`                                                       | `dp-env: invalid option -- 'x'`                                         | U   | 125  |
| Unknown long option token `T`                                                  | `dp-env: unrecognized option 'T'`                                       | U   | 125  |
| `-u` / `-C` without an argument                                                | `dp-env: option requires an argument -- 'u'` (or `'C'`)                 | U   | 125  |
| `--unset` / `--chdir` without an argument                                      | `dp-env: option '--unset' requires an argument` (or `'--chdir'`)        | U   | 125  |
| `--help=…`, `--version=…`, `--ignore-environment=…`, `--null=…`                | `dp-env: option '--<name>' doesn't allow an argument`                   | U   | 125  |
| `-0` together with COMMAND                                                     | `dp-env: cannot specify --null (-0) with command`                       | U   | 125  |
| `-C` without COMMAND                                                           | `dp-env: must specify command with --chdir (-C)`                        | U   | 125  |
| `-u` value `V` empty or containing `=`                                         | `dp-env: cannot unset 'V': Invalid argument`                            |     | 125  |
| Assignment operand `A` starting with `=`                                       | `dp-env: cannot set 'A': Invalid argument`                              |     | 125  |
| `-C DIR` cannot be entered                                                     | `dp-env: cannot change directory to 'DIR': <reason>` (reason per FR-10) |     | 125  |
| Writing the environment failed (not EPIPE)                                     | `dp-env: write error`                                                   |     | 125  |
| COMMAND names a directory (FR-11)                                              | `dp-env: 'COMMAND': Is a directory`                                     |     | 126  |
| COMMAND found only without execute permission, or start refused (FR-11, FR-12) | `dp-env: 'COMMAND': <reason>` (reason per FR-12)                        |     | 126  |
| COMMAND not found (FR-11, FR-12)                                               | `dp-env: 'COMMAND': No such file or directory`                          |     | 127  |

## 7. Verification

| Method                                              | Applies to                                               |
| :-------------------------------------------------- | :------------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases)  | FR-01, FR-03, FR-05, FR-09, FR-10, FR-11, FR-13, FR-15   |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-01 … FR-04, FR-06, FR-09 … FR-11, FR-13, FR-15, FR-17 |
| Integration test (written by the implementer, §7.2) | FR-12, FR-14, FR-15, FR-16, NFR-02, NFR-06, NFR-07       |
| Unit test (written by the implementer)              | FR-03 … FR-08, FR-11, FR-15, NFR-10                      |
| Inspection / review                                 | FR-19, NFR-02 … NFR-05, NFR-09                           |

### 7.1 Black-box tests

The child process in every test is `tests/fixtures/child.py`, run as
`{PYTHON} child.py WORD...`. For each WORD in order, it prints `NAME=<value>` (or
`NAME=<unset>` when the variable is missing) for a variable name, prints `cwd=<base name of its
working directory>` for `@cwd`, and sets its exit status to _N_ for `@exit=N`. The directory
`subdir` exists in every test's working directory. Tests use `-i` only when printing, because
a Python child on Windows cannot start without `SYSTEMROOT`. As a result, the printed output
never depends on the inherited environment or on FR-08.

Public test map:

| Test | Command                                                           | Verifies                                           |
| :--- | :---------------------------------------------------------------- | :------------------------------------------------- |
| 01   | `dp-env -i b=3 C=x=y A=1`                                         | FR-03, FR-05, FR-09 (byte-wise sort, `=` in VALUE) |
| 02   | `dp-env -i`                                                       | FR-09 (empty environment, empty output)            |
| 03   | `DP_X=hello dp-env -u DP_X {PYTHON} child.py DP_X`                | FR-05 (removal), FR-13                             |
| 04   | `DP_X=old dp-env DP_X=new DP_Y=added {PYTHON} child.py DP_X DP_Y` | FR-05 (override and addition), FR-13               |
| 05   | `dp-env -C subdir {PYTHON} ../child.py @cwd`                      | FR-10                                              |
| 06   | `dp-env {PYTHON} child.py @exit=3`                                | FR-15                                              |
| 07   | `dp-env dp-env-no-such-command`                                   | FR-11 (127)                                        |
| 08   | `dp-env -C no-such-dir {PYTHON} child.py`                         | FR-10 (125)                                        |
| 09   | `dp-env -x`                                                       | FR-01 (usage error, 125)                           |
| 10   | `DP_Y=1 dp-env -u DP_Y -- {PYTHON} child.py DP_Y`                 | FR-01 (`--`), FR-13                                |

### 7.2 Integration tests

Implementers MUST automate the following tests in their language repository. They involve
timing and signals, so they are not part of the byte-exact black-box suites. A _trap child_ is
a helper program that prints `ready` on standard output, flushes it, and then waits up to 10
seconds. If it receives SIGTERM, SIGINT, or SIGHUP, it prints `got <N>` and exits with
status 42. If the wait ends without a signal, it exits with status 1.

| ID    | Platform | Procedure                                                                                                                                                                                                                                                        | Expected result                                                                                             |
| :---- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| IT-01 | POSIX    | Start `dp-env TRAP-CHILD`, wait for `ready`, send SIGTERM to the `dp-env` process only (not the process group). Repeat with SIGINT and with SIGHUP.                                                                                                              | Child prints `got 15` (`got 2`, `got 1`), `dp-env` exits 42                                                 |
| IT-02 | POSIX    | Start `dp-env` running a child that sleeps 10 seconds with default signal dispositions, then send SIGTERM to `dp-env`.                                                                                                                                           | `dp-env` exits 143 within 1 second, and the child no longer exists                                          |
| IT-03 | POSIX    | As IT-01, but the child ignores SIGTERM and exits 0 by itself after 1 second.                                                                                                                                                                                    | `dp-env` survives the SIGTERM and exits 0 after the child exits                                             |
| IT-04 | POSIX    | Start `dp-env` with SIGINT set to "ignore" by its parent, running a child that reports whether SIGINT is ignored, then send SIGINT to `dp-env`.                                                                                                                  | Child reports SIGINT ignored, both processes survive the SIGINT, and `dp-env` exits with the child's status |
| IT-05 | POSIX    | `dp-env` running a child that sends SIGKILL to itself.                                                                                                                                                                                                           | `dp-env` exits 137                                                                                          |
| IT-06 | Windows  | Start `dp-env TRAP-CHILD` in a new process group (`CREATE_NEW_PROCESS_GROUP`) with a console, wait for `ready`, then call `GenerateConsoleCtrlEvent(CTRL_BREAK_EVENT, group)`. The Windows trap child handles Ctrl+Break by printing `got break` and exiting 42. | Child prints `got break`, `dp-env` exits 42                                                                 |
| IT-07 | POSIX    | `dp-env ./data.txt` where `data.txt` is a regular file without execute permission. Then `dp-env ./junk.bin`, where `junk.bin` is executable but holds random bytes.                                                                                              | `Permission denied` and exit 126. Then `Exec format error` and exit 126                                     |
| IT-08 | all      | A child that reports its open file descriptors (POSIX) or inheritable handles (Windows), run through `dp-env` while `dp-env` holds a file open.                                                                                                                  | Only the three standard streams are inherited                                                               |

## 8. Traceability (URD → SRS)

| User requirement | System requirements               |
| :--------------- | :-------------------------------- |
| UR-01            | FR-03, FR-05, FR-13               |
| UR-02            | FR-04, FR-05                      |
| UR-03            | FR-02, FR-05, FR-09               |
| UR-04            | FR-09                             |
| UR-05            | FR-10                             |
| UR-06            | FR-01, FR-13, NFR-03              |
| UR-07            | FR-11                             |
| UR-08            | FR-15                             |
| UR-09            | FR-10, FR-11, FR-12, FR-19, §3.7  |
| UR-10            | FR-14, FR-16, NFR-02, NFR-07      |
| UR-11            | FR-01, FR-03, FR-04, FR-06, FR-07 |
| UR-12            | FR-17, FR-18                      |
| UR-13            | FR-08                             |
| UR-14            | FR-09 (`-0`)                      |
| UR-15            | NFR-01, FR-09, CONV-03            |
| UR-16            | §1.5, CLI-CONV                    |
| UR-17            | NFR-04, NFR-05                    |
| UR-18            | NFR-11                            |
