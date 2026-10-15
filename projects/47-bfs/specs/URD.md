<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [User Requirements Document (URD) — dp-bfs-adj, dp-bfs-link](#user-requirements-document-urd--dp-bfs-adj-dp-bfs-link)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Product vision](#12-product-vision)
    - [1.3 Scope](#13-scope)
  - [2. Stakeholders and user classes](#2-stakeholders-and-user-classes)
  - [3. User requirements](#3-user-requirements)
  - [4. Usage scenarios](#4-usage-scenarios)
    - [4.1 The textbook graph, two ways](#41-the-textbook-graph-two-ways)
    - [4.2 A graph of one's own](#42-a-graph-of-ones-own)
    - [4.3 Another start, another island](#43-another-start-another-island)
    - [4.4 A mistake in the file](#44-a-mistake-in-the-file)
    - [4.5 Discovery and mistakes](#45-discovery-and-mistakes)
  - [5. Operational constraints](#5-operational-constraints)
  - [6. User acceptance criteria](#6-user-acceptance-criteria)
  - [7. Glossary](#7-glossary)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# User Requirements Document (URD) — dp-bfs-adj, dp-bfs-link

| Field               | Value                                                                      |
| :------------------ | :------------------------------------------------------------------------- |
| Document ID         | URD-47                                                                     |
| Project             | `47-bfs` — Graph Breadth-First Search: Adjacency Matrix vs. Adjacency List |
| Products            | `dp-bfs-adj`, `dp-bfs-link`                                                |
| Version             | 1.0.0                                                                      |
| Status              | Approved (pre-written by the curriculum)                                   |
| Successor documents | `SRS.md` (SRS-47), `user-manual.md`                                        |

## 1. Introduction

### 1.1 Purpose

This document records what the users of `dp-bfs-adj` and `dp-bfs-link` need, in their own
terms. It is the starting point for the Software Requirements Specification (SRS-47), which
turns each need into precise, testable system behavior.

### 1.2 Product vision

`dp-bfs-adj` and `dp-bfs-link` are a matched pair of teaching tools. Each searches a graph
breadth-first from a start vertex and reports every vertex it reaches, in the order it reaches
it. They solve the same problem with two classic graph representations — a matrix of
yes/no entries, and a linked list of neighbors per vertex — and a user who runs both on the
same graph sees that both answers are correct breadth-first orders, yet not the same one.
Out of the box they search the textbook's graph of the seven deadly sins; a user can also
describe any other small graph in a plain text file.

### 1.3 Scope

In scope: the built-in seven-sins graph; graphs read from a file or standard input; choosing
the start vertex; printing each visited vertex once, in discovery order; precise reports of
mistakes in a graph file; files written on Windows or MS-DOS; help and version information.
Out of scope: directed or weighted graphs, other search orders, printing distances or paths,
listing the vertices that cannot be reached, interactive prompts, configuration files, and
environment variables.

## 2. Stakeholders and user classes

| ID   | Stakeholder        | Description                                                                               | Primary interest                                            |
| :--- | :----------------- | :---------------------------------------------------------------------------------------- | :---------------------------------------------------------- |
| SH-1 | Student            | Runs the tools by hand to watch breadth-first search at work, on Linux, macOS, or Windows | Readable output; the two representations side by side       |
| SH-2 | Instructor         | Prepares graph files to demonstrate cycles, disconnected parts, and neighbor order        | A simple, documented file format; exact, explainable orders |
| SH-3 | Script author      | Calls the tools from scripts or pipelines                                                 | Predictable output bytes and exit statuses                  |
| SH-4 | Learner (assignee) | Implements both tools in a language repository of their choice                            | A complete, unambiguous specification                       |
| SH-5 | Grader / CI        | Runs automated acceptance tests on three operating systems                                | Deterministic, byte-exact behavior                          |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID    | Requirement (user's perspective)                                                                                                                                                         | Priority | Source     |
| :---- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------- | :--------- |
| UR-01 | As a student, I want to run either tool with no arguments and see the seven deadly sins visited breadth-first from Anger.                                                                | M        | SH-1       |
| UR-02 | As a student, I want each visited vertex reported on its own line, as `<name> has been visited.`, in the order it is discovered, and each vertex reported at most once.                  | M        | SH-1       |
| UR-03 | As a student, I want one tool to use an adjacency matrix and the other adjacency lists, and the documented neighbor order of each to explain why their outputs differ.                   | M        | SH-1, SH-2 |
| UR-04 | As an instructor, I want to describe my own graph in a plain text file, or pipe it in, and have both tools search it.                                                                    | S        | SH-2, SH-3 |
| UR-05 | As an instructor, I want to choose the vertex the search starts from.                                                                                                                    | S        | SH-2       |
| UR-06 | As an instructor, I want a graph with several separate parts to be searched only within the part that contains the start vertex.                                                         | M        | SH-2       |
| UR-07 | As an instructor, I want every mistake in a graph file to be reported with the file name, the line, and what is wrong, and nothing else printed for that graph.                          | M        | SH-2       |
| UR-08 | As a script author, I want missing or unreadable files reported clearly, with a non-zero exit status.                                                                                    | M        | SH-3       |
| UR-09 | As an instructor, I want graph files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly.                                            | S        | SH-2       |
| UR-10 | As a terminal user, I want a built-in help screen and a version query for each tool.                                                                                                     | M        | SH-1, SH-3 |
| UR-11 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before any input is read.                                                             | M        | SH-3       |
| UR-12 | As a grader, I want identical output bytes on Linux, macOS, and Windows, from every implementation.                                                                                      | M        | SH-5       |
| UR-13 | As a learner, I want the tools to follow the curriculum's common CLI conventions, so what I learned in earlier projects carries over.                                                    | M        | SH-4       |
| UR-14 | As a grader, I want the tools to build, install, and uninstall with standard commands, regardless of their implementation language, and to handle graphs of up to 1000 vertices quickly. | M        | SH-5       |

## 4. Usage scenarios

### 4.1 The textbook graph, two ways

A student runs `dp-bfs-adj` and sees Anger, Lust, Envy, Gluttony, Pride, Sloth, and
Covetousness visited, one line each. `dp-bfs-link` visits Anger, Gluttony, Envy, Lust, Sloth,
Pride, and Covetousness. In both, Anger's three neighbors come before the two sins at
distance 2, and Covetousness comes last. (UR-01, UR-02, UR-03)

### 4.2 A graph of one's own

An instructor writes `order.txt` with six vertices and six edges, listing the edges of
vertex 0 in the order 0–3, 0–1, 0–2. `dp-bfs-adj -g order.txt` visits the neighbors of
vertex 0 as 1, 2, 3; `dp-bfs-link -g order.txt` visits them as 2, 1, 3, the reverse of the
order in which the file lists them. (UR-03, UR-04)

### 4.3 Another start, another island

`dp-bfs-adj --start=4` starts the search at Pride. With a graph of two separate pairs and an
isolated vertex, `dp-bfs-link -g islands.txt -s 4` reports only the isolated vertex.
(UR-05, UR-06)

### 4.4 A mistake in the file

A graph file of 7 vertices contains the edge `3 7`. The tool reports
`dp-bfs-link: bad-edge.txt:6: value out of range '7'`, prints no vertex, and exits with
status 1. (UR-07)

### 4.5 Discovery and mistakes

A user runs `dp-bfs-adj --help` to see the options. `dp-bfs-adj sins.txt` is rejected,
because the graph file is given with `-g`, and nothing is read. (UR-10, UR-11)

## 5. Operational constraints

| ID   | Constraint                                                                                                     |
| :--- | :------------------------------------------------------------------------------------------------------------- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files.                                  |
| UC-4 | Must behave identically whatever the user's locale or terminal settings.                                       |

## 6. User acceptance criteria

The users will accept `dp-bfs-adj` and `dp-bfs-link` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. Both help texts exactly match the ones published in the user manual.

## 7. Glossary

| Term                 | Meaning                                                                                                                                         |
| :------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------- |
| Graph                | A set of vertices, numbered from 0, each with a name, and a set of undirected edges, each joining two different vertices                        |
| Neighbor             | A vertex joined to a given vertex by an edge                                                                                                    |
| Breadth-first search | A search that visits the start vertex, then all its neighbors, then all their unvisited neighbors, and so on, using a first-in, first-out queue |
| Adjacency matrix     | A table with one row and one column per vertex, whose entry says whether the two vertices are neighbors                                         |
| Adjacency list       | For each vertex, a linked list of its neighbors                                                                                                 |
| Discovery order      | The order in which the search first reaches the vertices                                                                                        |
| Exit status          | The integer a process returns to its caller; 0 means success                                                                                    |
