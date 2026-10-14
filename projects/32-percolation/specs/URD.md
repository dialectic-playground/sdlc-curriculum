# User Requirements Document (URD) — dp-perc

| Field | Value |
| :-- | :-- |
| Document ID | URD-32 |
| Project | `32-percolation` — Monte Carlo Forest Fire Percolation Simulation |
| Product | `dp-perc` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-32), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-perc` need, in their own terms. It is the starting
point for the Software Requirements Specification (SRS-32), which turns each need into precise,
testable system behavior.

### 1.2 Product vision
`dp-perc` lets a student explore percolation: how far a fire lit along one edge of a forest
spreads, depending on how densely the trees are planted. The student chooses a density, sees
the forest before and after the fire, reads a few statistics, and can try again at once with
another density. The same seed always produces the same forests, on every system, so a result
can be shared, discussed, and tested.

### 1.3 Scope
In scope: reading densities and yes/no answers from the keyboard, a pipe, or a file; planting
a random forest; simulating the fire; printing both forests and statistics; repeating on
request; choosing the seed and the forest size; optional prompts; reading response files
written on Windows or MS-DOS; reporting invalid responses and unreadable files; help and
version information.
Out of scope: other fire models (wind, sideways spread, burn-out over time), rectangular
forests, aggregated statistics over many runs, writing files, configuration files, and
environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Student | Runs simulations at the keyboard on Linux, macOS, or Windows to watch the effect of density | Readable pictures; quick repeats; clear prompts |
| SH-2 | Instructor | Prepares examples and exercises from chosen seeds | The same seed gives the same forest everywhere |
| SH-3 | Script author | Drives the tool with response files to collect statistics | Predictable output bytes and exit statuses |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a student, I want to choose a tree density from 1 to 100 percent and have a 25 by 25 forest planted at random with about that density. | M | SH-1 |
| UR-02 | As a student, I want every tree in the top row set on fire and the fire to spread down to any tree directly or diagonally below a burning tree. | M | SH-1 |
| UR-03 | As a student, I want to see the forest before and after the fire as framed pictures, with trees, burned trees, and empty ground clearly distinguished. | M | SH-1 |
| UR-04 | As a student, I want the requested density, the actual density, the number of trees at the start, and the number of trees that survived. | M | SH-1 |
| UR-05 | As a student, I want to be asked whether to run another simulation, and to continue with a new density as often as I like. | M | SH-1 |
| UR-06 | As an instructor, I want to choose a seed, and to get the same forests for the same seed and responses on every system and in every implementation. | M | SH-2, SH-5 |
| UR-07 | As an instructor, I want to use a smaller forest for examples that fit on a slide. | C | SH-2 |
| UR-08 | As a script author, I want to pipe responses into the tool or name a file of responses. | M | SH-3 |
| UR-09 | As a student, I want the tool to ask for each response when I request it, without the prompts appearing in the report I save. | S | SH-1 |
| UR-10 | As a script author, I want an invalid density or answer, or responses that end too early, reported with its position and a non-zero exit status, while the simulations already shown are kept. | M | SH-3 |
| UR-11 | As a script author, I want a missing or unreadable file, and invalid usage, reported clearly with distinct non-zero exit statuses. | M | SH-3 |
| UR-12 | As a student, I want response files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-13 | As a terminal user, I want a built-in help screen and a version query, and the tool to follow the curriculum's common CLI conventions. | M | SH-1, SH-4 |
| UR-14 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to answer quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 Exploring densities
A student runs `dp-perc --prompt`, sees `Enter density (1-100): `, types `30`, and sees the
framed forest before the fire, the forest after it, and the statistics; the fire died out near
the top. At `Again? (y/n) ` the student types `y`, then `80`, and this time the whole forest
burns. The answer `n` ends the session. (UR-01 … UR-05, UR-09)

### 4.2 A shared example
An instructor runs `dp-perc --seed=42 --size=10 responses.txt` and pastes the output into the
course notes. Every student who runs the same command, on any system and with any conforming
implementation, sees the same two forests. (UR-06, UR-07, UR-08)

### 4.3 A typo
A response file contains the density `101` after one simulation. The tool shows the first
simulation, reports `bad-density.txt:3: value out of range '101'`, and exits with status 1.
(UR-10)

### 4.4 An old response file
A response file copied from an MS-DOS machine has CRLF line endings and ends with a Ctrl-Z byte.
The tool reads it exactly like a file with LF line endings. (UR-12)

### 4.5 Discovery and mistakes
A user runs `dp-perc --help` to see the options; `dp-perc --size=0` is rejected as an invalid
argument. (UR-11, UR-13)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings, and must never depend on the clock. |
| UC-5 | Must work interactively: each simulation is shown before the next response is read. |

## 6. User acceptance criteria

The users will accept `dp-perc` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Forest | A square grid of cells, each holding a tree or empty ground |
| Density | The percentage of cells meant to hold a tree (requested), or that actually do (actual) |
| Burned tree | A tree reached by the fire |
| Surviving tree | A tree the fire did not reach |
| Percolation | The fire getting through the forest from the top row to the bottom row |
| Seed | The number that starts the random number generator; the same seed gives the same forests |
| Session | One run of the tool: one or more simulations, until the answer `n` or the end of the input |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
