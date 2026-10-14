# User Requirements Document (URD) — dp-ship

| Field | Value |
| :-- | :-- |
| Document ID | URD-52 |
| Project | `52-spacecraft` — Object-Oriented Spacecraft Domain Modeling |
| Product | `dp-ship` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-52), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-ship` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-52), which turns each need into
precise, testable system behavior.

### 1.2 Product vision
`dp-ship` models spacecraft: each ship has a name, a mass, a velocity, a trip distance, and a
number of astronauts it holds. Run on its own, it replays the textbook's short mission — a
blank ship and the MightyMite, whose velocity is adjusted before its trip time is reported.
Given a script, it lets a mission planner create a fleet, speed ships up or slow them down
(never below a standstill), and ask how long each trip will take. Behind the tool is a small,
well-encapsulated object, the textbook's first example of object-oriented design.

### 1.3 Scope
In scope: the textbook scenario; command scripts from a file or a pipe that create ships with
default or given values, adjust velocities, and report basics and trip times; reporting
invalid script lines and unreadable files; help and version information.
Out of scope: changing a ship's name, mass, distance, or capacity after creation; deleting
ships; units other than kilograms, kilometers, and kilometers per hour; saving ships between
runs; interactive prompting; configuration files; and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Mission planner | Writes scripts describing ships and their velocity changes | Correct trip times; clear reports; helpful errors |
| SH-2 | Script author | Runs the tool from shell scripts and batch jobs | Predictable output bytes and exit statuses |
| SH-3 | Instructor | Uses the project to teach encapsulation and constructors | A design that hides the ship's data behind its operations |
| SH-4 | Learner (assignee) | Implements the tool in a language repository of their choice | A complete, unambiguous specification |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As an instructor, I want running the tool without arguments to replay the textbook's scenario and print its report. | M | SH-3 |
| UR-02 | As a mission planner, I want to create a ship either with default values (name `???`, everything zero) or with a given mass, velocity, distance, capacity, and name. | M | SH-1 |
| UR-03 | As a mission planner, I want to speed a ship up or slow it down by a given amount, with the velocity never dropping below zero, and to know the trip time as distance divided by velocity. | M | SH-1 |
| UR-04 | As a mission planner, I want to describe a mission as a script in a file or a pipe, one command per line, with comments and blank lines allowed. | M | SH-1, SH-2 |
| UR-05 | As a mission planner, I want each ship's basics and trip time reported in the textbook's wording, with numbers in a compact, documented format. | M | SH-1 |
| UR-06 | As a mission planner, I want a ship that is standing still to be reported as unable to make its trip, not given a nonsensical time. | M | SH-1 |
| UR-07 | As a script author, I want an invalid script line (an unknown command or ship, a missing or extra value, a negative mass) reported with its line number and a non-zero exit status, while the reports already produced are kept. | M | SH-2 |
| UR-08 | As a mission planner, I want scripts written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to work unchanged. | S | SH-1 |
| UR-09 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-2 |
| UR-10 | As a terminal user, I want a built-in help screen and a version query. | M | SH-1, SH-2 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-2 |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-13 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over. | M | SH-4 |
| UR-14 | As an instructor, I want the spacecraft implemented as one encapsulated object with constructors and operations, so the project teaches object-oriented design in any language. | M | SH-3 |
| UR-15 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to run long scripts quickly. | M | SH-5 |

## 4. Usage scenarios

### 4.1 The textbook mission
An instructor runs `dp-ship` and sees the basics of the default ship `???`, then those of
MightyMite before and after its velocity is raised from 63567 to 64567 km/h, and finally
`MightyMite requires 8.68848 hours for trip.` The tool exits with status 0. (UR-01, UR-02,
UR-03, UR-05)

### 4.2 Planning a fleet
A planner writes `fleet.txt` with a comment, the textbook's ships, and a probe, and runs
`dp-ship fleet.txt > plan.txt`. The file holds the requested reports in script order. A probe
with a distance of 1.2 billion kilometers is reported as `1.2e+09 kilometers`. (UR-04, UR-05)

### 4.3 Full stop
A planner slows MightyMite by 100000 km/h. Its velocity becomes 0, and the trip report reads
`MightyMite cannot make the trip at a velocity of 0.` (UR-03, UR-06)

### 4.4 A typo
A script's third line reads `adjust s1 fast`. The tool prints the reports of the first two
lines, then reports `bad.txt:3: invalid number 'fast'` and exits with status 1. (UR-07)

### 4.5 Discovery and mistakes
A user runs `dp-ship --help` to see the script commands, and `dp-ship a.txt b.txt` is rejected
because the tool runs one script. (UR-10, UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |

## 6. User acceptance criteria

The users will accept `dp-ship` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.
4. A design review confirms the object design of SRS-52 NFR-05.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Ship | A spacecraft with a name, a mass (kg), a velocity (km/h), a trip distance (km), and a capacity (astronauts) |
| Basics | The two-line description of a ship printed by the textbook program |
| Trip time | The distance divided by the velocity, in hours |
| Script | A text file of commands, one per line, that create, adjust, and report on ships |
| Encapsulation | Keeping an object's data private, so that it can be read or changed only through the object's own operations |
| Exit status | The integer a process returns to its caller; 0 means success |
