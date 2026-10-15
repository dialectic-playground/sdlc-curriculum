<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Project 08 — Environment Execution Wrapper (`dp-env`)](#project-08--environment-execution-wrapper-dp-env)
  - [Purpose](#purpose)
  - [Operational scope](#operational-scope)
  - [Learning objectives](#learning-objectives)
  - [What is provided](#what-is-provided)
  - [What you deliver (in your language repository)](#what-you-deliver-in-your-language-repository)
  - [Quick start](#quick-start)
  - [Acceptance](#acceptance)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Project 08 — Environment Execution Wrapper (`dp-env`)

> Run a program with a precisely controlled environment and working directory, the way POSIX
> `env` does. Find it on the search path, start it without a shell, relay termination signals
> to it, and report its exit status faithfully on Linux, macOS, and Windows.

## Purpose

Every earlier project transforms bytes. Project 08 manages a **process**. `dp-env` builds an
environment (inherited or empty, with variables removed and assigned), then either prints it
or starts a command with it. It stays alive while the command runs, forwards termination
signals, and exits with the command's status. Getting this right means working directly with
the operating system's process primitives, which differ deeply between the two platform
families: `fork`/`exec`/`waitpid` and signal dispositions on Linux and macOS, and
`CreateProcessW`, Unicode environment blocks, 32-bit exit codes, and console control events
on Windows.

## Operational scope

| In scope                                                                                   | Out of scope                                            |
| :----------------------------------------------------------------------------------------- | :------------------------------------------------------ |
| Printing the resulting environment, sorted byte-wise by name (`-0` for NUL terminators)    | Running commands through a shell, `-S`/`--split-string` |
| `-i` / lone `-`, `-u NAME` (repeatable), `NAME=VALUE` assignments                          | Blocking, ignoring, or defaulting signals on request    |
| `-C DIR` working directory for the command                                                 | Detaching from the terminal (`nohup`), resource limits  |
| Command lookup via `PATH` (and `PATHEXT` on Windows), no implicit current-directory search | Changing `dp-env`'s own behavior from locale variables  |
| Exit statuses 125 / 126 / 127, child status propagation, 128+N for signal deaths           | Re-raising the child's signal against `dp-env`          |
| Forwarding SIGINT/SIGTERM/SIGHUP (POSIX); surviving Ctrl+C/Ctrl+Break (Windows)            | Process groups, job control, pseudo-terminals           |
| Case-insensitive variable names on Windows                                                 |                                                         |

## Learning objectives

1. Parse options that stop at the first operand, and define precisely where a wrapper's own
   arguments end and the wrapped command's begin.
2. Model an environment as data, including Windows' case-insensitive names, and give a child
   process exactly that environment.
3. Create processes with the native primitives (`fork`+`execve` or `posix_spawn`, and
   `CreateProcessW`), resolve commands without a shell, and classify start-up failures.
4. Handle signals correctly: async-signal-safe handlers, race-free installation, dispositions
   that are inherited across `exec` versus those that are not, and Windows console control
   events.
5. Propagate exit statuses faithfully, including signal deaths and 32-bit Windows exit codes.
6. Write integration tests for asynchronous behavior that byte-exact black-box tests cannot
   cover.

## What is provided

| Path                   | Contents                                                                                                    |
| :--------------------- | :---------------------------------------------------------------------------------------------------------- |
| `specs/URD.md`         | User requirements (UR-01 … UR-18)                                                                           |
| `specs/SRS.md`         | System requirements (FR-01 … FR-19, NFR-01 … NFR-11), integration tests IT-01 … IT-08                       |
| `specs/user-manual.md` | Complete user manual, including the normative help text                                                     |
| `tests/public/`        | 10 visible black-box tests with exact expected outputs                                                      |
| `tests/private/`       | 10 hidden black-box tests (used by grading/CI; unseen by convention)                                        |
| `tests/fixtures/`      | The portable child process `child.py` (run through `{PYTHON}`) and the `subdir` directory used by the tests |
| `assignment/`          | Language-neutral `Makefile` and blank HLD, LLD, RTM, and master-test-plan templates                         |

## What you deliver (in your language repository)

1. A completed `hld.md`, `lld.md`, `rtm.md`, and `master-test-plan.md`.
2. An implementation of `dp-env`, with unit tests for environment construction, command
   resolution, and exit-status mapping (SRS NFR-10).
3. Automated integration tests IT-01 … IT-08 (SRS §7.2) for the platforms they name.
4. The project `Makefile` with every `DP_*` hook filled in for your toolchain (see
   `assignment/src/README.md`).

## Quick start

```sh
make all            # build dp-env into BIN_DIR
make test           # unit + integration tests + 10 public black-box tests
make lint format    # static analysis and formatting
make test-hidden    # hidden suite (CI does this on Linux, macOS, and Windows)
```

The black-box tests start a Python interpreter as the child process (`{PYTHON}` in the test
files). They use `-i` only when printing, because a Python child on Windows cannot start
without `SYSTEMROOT`.

## Acceptance

The project is complete when `make test` and `make test-hidden` pass on all three operating
systems in CI, the integration tests pass on the platforms they name, `make lint` is clean,
and every RTM row is _Verified_.
