<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-astar](#user-requirements-document-urd--dp-astar)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 A quick route](#41-a-quick-route)
    - [4.2 Asked for the city](#42-asked-for-the-city)
    - [4.3 A typo](#43-a-typo)
    - [4.4 Watching the search](#44-watching-the-search)
    - [4.5 Nowhere to go](#45-nowhere-to-go)
    - [4.6 A damaged data file](#46-a-damaged-data-file)
    - [4.7 Discovery and mistakes](#47-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-astar

| Field               | Value                                                      |
| :------------------ | :--------------------------------------------------------- |
| Document ID         | URD-48                                                     |
| Project             | `48-astar` — A* Heuristic Graph Search for European Cities |
| Product             | `dp-astar`                                                 |
| Version             | 1.0.0                                                      |
| Status              | Approved (pre-written by the curriculum)                   |
| Successor documents | `SRS.md` (SRS-48), `user-manual.md`                        |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-astar` need, in their own terms. It is the
starting point for the Software Requirements Specification (SRS-48), which turns each need
into precise, testable system behavior.

### 1.2 Product vision

`dp-astar` is a small route planner and a window into informed search. A user names a
European city, and the tool finds the shortest road route from it to Vienna, using a road
map and a table of straight-line estimates that come from the textbook's companion disk. It
prints the route and its length. A student can ask it to show every step of the search —
which city it expands, which routes it opens, improves, or reopens — and an instructor can
give it a different map to demonstrate a particular behavior.

### 1.3 Scope

In scope: reading the city table (`names.dat`) and the road-distance table (`distance.dat`),
or other files in the same formats; reading the start city from the command line or from
standard input, optionally with a prompt; searching for a route to Vienna or to another city
of the table; printing the route, its length, or the fact that there is none; optionally
printing the steps of the search; reporting every problem with the data files precisely;
help and version information.
Out of scope: changing the data, computing estimates, several start cities per run, other
search algorithms, configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder               | Description                                                         | Primary interest                                      |
| :--- | :------------------------ | :------------------------------------------------------------------ | :---------------------------------------------------- |
| SH-1 | Traveller (terminal user) | Asks for a route by hand, on Linux, macOS, or Windows               | The route and its length; forgiving city-name entry   |
| SH-2 | Student                   | Studies how A* explores the map                                     | A readable, complete trace of the search              |
| SH-3 | Instructor                | Prepares small maps that show reopening, ties, or unreachable goals | A documented data format; exact, explainable behavior |
| SH-4 | Script author             | Calls the tool from scripts                                         | Predictable output bytes and exit statuses            |
| SH-5 | Learner (assignee)        | Implements the tool in a language repository of their choice        | A complete, unambiguous specification                 |
| SH-6 | Grader / CI               | Runs automated acceptance tests on three operating systems          | Deterministic, byte-exact behavior                    |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                            | Priority | Source     |
| :---- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------- | :--------- |
| UR-01 | As a traveller, I want to name a start city and get the shortest road route from it to Vienna, with the cities in order and the total distance in kilometers.                               | M        | SH-1       |
| UR-02 | As a traveller, I want to type the city name in any mix of upper and lower case.                                                                                                            | M        | SH-1       |
| UR-03 | As a traveller, I want to be able to run the tool without arguments and be asked for the start city, as the textbook program does.                                                          | S        | SH-1       |
| UR-04 | As a traveller, I want to be told clearly when the city I typed is not on the map, and when there is no route at all.                                                                       | M        | SH-1, SH-4 |
| UR-05 | As a student, I want to see every step of the search: each city expanded, and each route opened, improved, or reopened, with its _g_ and _f_ values.                                        | S        | SH-2       |
| UR-06 | As a student, I want the search to follow the A* rules exactly, including reopening a city when a shorter route to it is found, so the trace matches what I work out by hand.               | M        | SH-2, SH-5 |
| UR-07 | As an instructor, I want to give the tool my own city table and distance table, and choose a goal other than Vienna.                                                                        | S        | SH-3       |
| UR-08 | As a traveller, I want the tool to read the textbook's data files exactly as they are, including their tabs, wrapped rows, and MS-DOS end-of-file padding.                                  | M        | SH-1       |
| UR-09 | As an instructor, I want every mistake in a data file to be reported with the file name, the line, and what is wrong, before any route is computed.                                         | M        | SH-3       |
| UR-10 | As a script author, I want missing or unreadable files reported clearly, with a non-zero exit status.                                                                                       | M        | SH-4       |
| UR-11 | As a terminal user, I want a built-in help screen and a version query.                                                                                                                      | M        | SH-1, SH-4 |
| UR-12 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before any file is read.                                                                 | M        | SH-4       |
| UR-13 | As a grader, I want identical output bytes on Linux, macOS, and Windows, from every implementation.                                                                                         | M        | SH-6       |
| UR-14 | As a learner, I want the tool to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                        | M        | SH-5       |
| UR-15 | As a grader, I want the tool to build, install, and uninstall with standard commands, regardless of its implementation language, and to answer quickly even for maps of hundreds of cities. | M        | SH-6       |

## 4. Usage scenarios

### 4.1 A quick route

In a directory holding `names.dat` and `distance.dat`, a traveller runs `dp-astar berlin` and
sees `Optimal path to Vienna:`, then `berlin -> prague -> vienna`, then
`Total distance: 404 kilometers`. (UR-01)

### 4.2 Asked for the city

The traveller runs `dp-astar --prompt`, sees `Enter start city:types `Lisbon`, and gets
the route `lisbon -> madrid -> genoa -> trieste -> vienna` of 1968 kilometers.
(UR-02, UR-03)

### 4.3 A typo

`dp-astar berln` reports `dp-astar: unknown start city 'berln'` and exits with status 1.
(UR-04)

### 4.4 Watching the search

A student runs `dp-astar --trace berlin` and sees Berlin expanded, its four neighbors opened,
Prague (the open city with the smallest _f_) expanded, Vienna opened, and Vienna selected,
followed by the route. With an instructor's small map, the trace shows a closed city being
reopened and the final route changing because of it. (UR-05, UR-06, UR-07)

### 4.5 Nowhere to go

In the textbook data Vienna has no outgoing roads, so `dp-astar --goal=lisbon vienna` prints
`No path from vienna to Lisbon.` (UR-04, UR-07)

### 4.6 A damaged data file

A distance table that is one entry short is reported as
`dp-astar: short.dat:57: unexpected end of input`, and no route is printed. (UR-09)

### 4.7 Discovery and mistakes

A user runs `dp-astar --help` to see the options. `dp-astar berlin prague` is rejected,
because only one start city can be given, and no file is read. (UR-11, UR-12)

## 5. Operational constraints

| ID   | Constraint                                                                                                                          |
| :--- | :---------------------------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher.                      |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets.                      |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                                       |
| UC-4 | Must behave identically whatever the user's locale or terminal settings, including when matching city names without regard to case. |

## 6. User acceptance criteria

The users will accept `dp-astar` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The help text exactly matches the one published in the user manual.

## 7. Glossary

| Term           | Meaning                                                                        |
| :------------- | :----------------------------------------------------------------------------- |
| City table     | The file of cities and estimates, `names.dat` by default                       |
| Distance table | The file of road distances, `distance.dat` by default; 1000 means no road      |
| Estimate (_h_) | The table's straight-line estimate of a city's distance to the goal            |
| _g_            | The length of the best route found so far from the start city to a city        |
| _f_            | _g_ + _h_, the estimated length of a complete route through a city             |
| OPEN           | The cities reached but not yet expanded                                        |
| CLOSED         | The cities already expanded                                                    |
| Reopening      | Moving a closed city back to OPEN because a shorter route to it has been found |
| Exit status    | The integer a process returns to its caller; 0 means success                   |
