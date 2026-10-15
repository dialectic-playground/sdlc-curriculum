<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-env](#user-requirements-document-urd--dp-env)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 One-off setting](#41-one-off-setting)
    - [4.2 Hermetic build](#42-hermetic-build)
    - [4.3 Inspecting a clean environment](#43-inspecting-a-clean-environment)
    - [4.4 Running elsewhere](#44-running-elsewhere)
    - [4.5 A typo in the command](#45-a-typo-in-the-command)
    - [4.6 Cancelling a job](#46-cancelling-a-job)
    - [4.7 Windows](#47-windows)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-env

| Field               | Value                                        |
| :------------------ | :------------------------------------------- |
| Document ID         | URD-08                                       |
| Project             | `08-env-run` — Environment Execution Wrapper |
| Product             | `dp-env`                                     |
| Version             | 1.0.0                                        |
| Status              | Approved (pre-written by the curriculum)     |
| Successor documents | `SRS.md` (SRS-08), `user-manual.md`          |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-env` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-08), which turns each need into precise,
testable system behavior.

### 1.2 Product vision

`dp-env` runs another program with a controlled set of environment variables, in the spirit of
the POSIX `env` utility. A user can start from the current environment or from an empty one,
remove variables, add or override variables, and choose the working directory the program
starts in. Without a program to run, `dp-env` shows the environment it would have passed on.
`dp-env` stays in the foreground while the program runs: it relays termination requests to
the program and then reports the program's exit status as its own. Script authors can
therefore put `dp-env` in front of any command without changing how that command's success or
failure is detected.

The project teaches how processes are created on two very different families of operating
system: `fork`/`exec`/`wait` and signals on Linux and macOS, and `CreateProcess`, environment
blocks, exit codes, and console control events on Windows.

### 1.3 Scope

In scope: printing an environment; clearing, removing, setting, and overriding variables;
running a command directly (without a shell), with a search of the command search path;
changing the child's working directory; propagating the child's exit status; distinguishing
"`dp-env` failed", "command could not be run", and "command not found"; relaying termination
signals to the child.
Out of scope: running commands through a shell, splitting a single argument into several
(GNU `env -S`), blocking or ignoring signals on request, running commands detached from the
terminal (`nohup`), and resource limits.

## 2. Stakeholders and user classes

| ID   | Stakeholder                 | Description                                                                              | Primary interest                                  |
| :--- | :-------------------------- | :--------------------------------------------------------------------------------------- | :------------------------------------------------ |
| SH-1 | Terminal user               | Runs commands by hand on Linux, macOS, or Windows, sometimes with one-off settings       | Simple syntax, clear errors                       |
| SH-2 | Script author / CI engineer | Runs build and test commands with a controlled environment                               | Reproducible environments, faithful exit statuses |
| SH-3 | Process supervisor          | Starts `dp-env` and may later ask it to stop (for example, a CI runner cancelling a job) | Termination requests reach the real program       |
| SH-4 | Learner (assignee)          | Implements the tool in a language repository of their choice                             | A complete, unambiguous specification             |
| SH-5 | Grader / CI                 | Runs automated acceptance tests on three operating systems                               | Deterministic, byte-exact behavior                |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                               | Priority | Source |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :----- |
| UR-01 | As a script author, I want to run a command with extra or changed environment variables given on the command line, so I don't have to modify my own environment.                               | M        | SH-2   |
| UR-02 | As a script author, I want to remove specific variables before running a command, so it cannot be influenced by them.                                                                          | M        | SH-2   |
| UR-03 | As a script author, I want to start from an empty environment and add only what I list, so the result is fully reproducible.                                                                   | M        | SH-2   |
| UR-04 | As a terminal user, I want to see the environment `dp-env` would pass on, in a stable order, so I can inspect and compare it.                                                                  | M        | SH-1   |
| UR-05 | As a script author, I want to choose the working directory the command starts in, without a separate `cd`.                                                                                     | S        | SH-2   |
| UR-06 | As a script author, I want the command run directly, never through a shell, so arguments are passed exactly as given and nothing in them is interpreted.                                       | M        | SH-2   |
| UR-07 | As a terminal user, I want commands found through my command search path, just as the shell finds them.                                                                                        | M        | SH-1   |
| UR-08 | As a script author, I want `dp-env` to exit with the command's own exit status, so wrapping a command does not hide its success or failure.                                                    | M        | SH-2   |
| UR-09 | As a script author, I want distinct exit statuses for "`dp-env` failed", "the command exists but cannot be run", and "the command does not exist", so my scripts can react to each.            | M        | SH-2   |
| UR-10 | As a process supervisor, I want a termination request sent to `dp-env` to reach the command, and `dp-env` to keep waiting until the command has exited, so no orphaned process is left behind. | M        | SH-3   |
| UR-11 | As a script author, I want mistakes on the command line to be rejected with a clear message before anything runs.                                                                              | M        | SH-2   |
| UR-12 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                         | M        | SH-1   |
| UR-13 | As a terminal user on Windows, I want variable names to behave case-insensitively, as they do everywhere else on Windows.                                                                      | M        | SH-1   |
| UR-14 | As a script author, I want to print the environment in a form that is safe to parse even when values contain newlines.                                                                         | C        | SH-2   |
| UR-15 | As a grader, I want identical output bytes and exit statuses on Linux, macOS, and Windows for the same test.                                                                                   | M        | SH-5   |
| UR-16 | As a learner, I want the tool to follow the curriculum's common CLI conventions wherever its purpose allows, with every deviation stated explicitly.                                           | M        | SH-4   |
| UR-17 | As a terminal user, I want `dp-env` to add no noticeable delay when starting a command.                                                                                                        | S        | SH-1   |
| UR-18 | As a grader, I want the tool to install and uninstall with standard commands, regardless of its implementation language.                                                                       | M        | SH-5   |

## 4. Usage scenarios

### 4.1 One-off setting

A user runs `dp-env LOG_LEVEL=debug ./server --port 8080`. The server starts with
`LOG_LEVEL` set to `debug` and receives `--port` and `8080` as its arguments. The user's own
shell environment is unchanged afterwards. (UR-01, UR-06)

### 4.2 Hermetic build

A CI job runs `dp-env -u HTTP_PROXY -u HTTPS_PROXY make test`, so that proxy settings on the
build agent cannot affect the tests. When `make test` fails with status 2, the job sees exit
status 2 from `dp-env`. (UR-02, UR-07, UR-08)

### 4.3 Inspecting a clean environment

A user runs `dp-env -i LANG=C.UTF-8 TZ=UTC` and sees exactly two lines, `LANG=C.UTF-8` and
`TZ=UTC`, in sorted order. (UR-03, UR-04)

### 4.4 Running elsewhere

A user runs `dp-env -C build cmake --build .`. The build runs inside `build`, while the
user's shell stays in its current directory. If `build` does not exist, `dp-env` explains
that it cannot change into it, exits with status 125, and runs nothing. (UR-05, UR-09)

### 4.5 A typo in the command

A user types `dp-env FOO=1 pyhton script.py`. `dp-env` reports that `pyhton` does not exist
and exits with status 127, which the user's script recognizes as "command not found".
(UR-09)

### 4.6 Cancelling a job

A CI runner cancels a job by sending a termination signal to `dp-env`, which is running a long
test suite. `dp-env` passes the signal on to the test suite, waits for it to shut down, and
exits with the status that reflects how the suite ended. (UR-10)

### 4.7 Windows

On Windows, a user runs `dp-env -u path report.exe`. Because Windows variable names are
case-insensitive, `-u path` removes the variable named `Path`, and `report.exe` starts without
it. `dp-env` still finds `report.exe` through the user's own search path. (UR-07, UR-13)

## 5. Operational constraints

| ID   | Constraint                                                                                                                                                        |
| :--- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher.                                                    |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets.                                                    |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                                                                     |
| UC-4 | Must never pass the command or its arguments through a shell.                                                                                                     |
| UC-5 | Must behave identically whatever the user's locale or terminal settings, and must pass locale variables on to the command unchanged unless the user removes them. |

## 6. User acceptance criteria

The users will accept `dp-env` when all of the following hold:

1. Every scenario in section 4 behaves as described on the platforms it names (all three when
   none is named).
2. All public and hidden black-box tests pass in CI on Linux, macOS, and Windows.
3. The signal-forwarding integration tests described in SRS-08 §7.2 pass on Linux and macOS,
   and the console-event test passes on Windows.
4. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term                  | Meaning                                                                                                                     |
| :-------------------- | :-------------------------------------------------------------------------------------------------------------------------- |
| Environment           | The set of named text variables (`NAME=VALUE`) a process receives when it starts                                            |
| Environment variable  | One `NAME=VALUE` entry of an environment                                                                                    |
| Command               | The program `dp-env` starts, together with its arguments                                                                    |
| Child                 | The process running the command                                                                                             |
| Command search path   | The directories listed in the `PATH` variable, searched in order for a command name                                         |
| Exit status           | The integer a process returns to its caller; 0 means success                                                                |
| Signal                | A POSIX asynchronous notification sent to a process, such as SIGTERM (terminate) or SIGINT (interrupt, usually from Ctrl+C) |
| Console control event | The Windows counterpart of terminal signals: Ctrl+C, Ctrl+Break, and console close notifications                            |
| Usage error           | An invalid combination of command-line arguments                                                                            |
