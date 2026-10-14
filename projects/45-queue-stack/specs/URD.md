# User Requirements Document (URD) — dp-queue1, dp-queue2, dp-stack1, dp-stack2

| Field | Value |
| :-- | :-- |
| Document ID | URD-45 |
| Project | `45-queue-stack` — Comparative Queue & Stack ADT Implementations |
| Products | `dp-queue1`, `dp-queue2`, `dp-stack1`, `dp-stack2` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-45), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-queue1`, `dp-queue2`, `dp-stack1`, and `dp-stack2`
need, in their own terms. It is the starting point for the Software Requirements Specification
(SRS-45), which turns each need into precise, testable system behavior.

### 1.2 Product vision
A bank lets customers wait in line: whoever arrives first is served first. A cafeteria stacks
its trays: the tray put on last is taken first. Four small tools model these two situations,
each in two ways — with a fixed table of 100 places and with a chain of linked records — and a
teller or cafeteria manager drives any of them with the same simple commands: add, take, show,
quit. Whichever tool of a kind is used, the results are the same, until the fixed table is full,
which the tool says plainly. Account balances are shown to the cent, exactly as entered.

### 1.3 Scope
In scope: a queue of customers (last name, first name, account number, balance) and a stack of
trays (color, id number); adding, removing, and showing records through numbered commands read
from the keyboard, a pipe, or a file; a capacity of 100 for the table-based tools and no fixed
capacity for the linked tools; optional prompts; reading files written on Windows or MS-DOS;
reporting malformed commands and unreadable files; help and version information.
Out of scope: changing a record that is already stored, searching, sorting, saving the queue or
stack between runs, interest or currency conversion, configuration files, and environment
variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Bank teller | Queues and serves customers at the keyboard on Linux, macOS, or Windows | Customers served in arrival order; balances shown exactly; clear questions |
| SH-2 | Cafeteria manager | Stacks and hands out trays | Trays handed out in reverse order of stacking |
| SH-3 | Script author | Feeds prepared command files to the tools and uses the output and exit status | Predictable output bytes and exit statuses |
| SH-4 | Instructor | Teaches abstract data types with the four tools | Two interchangeable implementations of each ADT behind one interface |
| SH-5 | Learner (assignee) | Implements the four tools in a language repository of their choice | A complete, unambiguous specification and a clear required structure |
| SH-6 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a bank teller, I want to add a customer — last name, first name, account number, and balance — to the end of the queue, and to remove the customer at the front, so customers are served in the order they arrived. | M | SH-1 |
| UR-02 | As a cafeteria manager, I want to put a tray — color and id number — on top of the stack and take the top tray off, so the last tray stacked is the first handed out. | M | SH-2 |
| UR-03 | As a teller or manager, I want to display the whole queue (front first) or stack (top first) at any time without changing it. | M | SH-1, SH-2 |
| UR-04 | As a teller or manager, I want a plain `QUEUE EMPTY` or `STACK EMPTY` when there is nothing to remove or display, and the session to continue. | M | SH-1, SH-2 |
| UR-05 | As a teller or manager using a table-based tool, I want a plain `QUEUE FULL` or `STACK FULL` when the 100 places are taken, and the session to continue with the contents unchanged. | M | SH-1, SH-2 |
| UR-06 | As an instructor, I want the table-based and the linked tool of each kind to give exactly the same results for the same commands, except that only the table-based tool can become full. | M | SH-4 |
| UR-07 | As a bank teller, I want balances entered with up to two decimal places and always shown with exactly two, to the cent, with no rounding errors. | M | SH-1 |
| UR-08 | As a teller or manager, I want to choose the operation by number — 1 add, 2 remove, 3 display, 0 quit — and to type records with their fields separated by spaces or line breaks as I like. | M | SH-1, SH-2 |
| UR-09 | As a teller or manager, I want the session to end when I choose 0 or when my input ends. | M | SH-1, SH-3 |
| UR-10 | As a teller or manager, I want an unknown command, a malformed account or id number, or a malformed balance reported with the line where it occurs, keeping the results already shown. | M | SH-1, SH-3 |
| UR-11 | As a teller or manager at the keyboard, I want to see the menu before each command and a reminder of the fields before each record, without these prompts mixing into output I redirect to a file. | S | SH-1, SH-2 |
| UR-12 | As a script author, I want to pipe commands into the tools or name a file of commands, and to read files written on Windows or MS-DOS correctly. | M | SH-3 |
| UR-13 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-3 |
| UR-14 | As a terminal user, I want a built-in help screen and a version query for each tool, and invalid usage rejected with a clear message and a distinct exit status. | M | SH-1, SH-3 |
| UR-15 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-6 |
| UR-16 | As a learner and grader, I want the tools to follow the curriculum's common CLI conventions and to build, install, and uninstall with standard commands in any language, handling long command sequences quickly. | M | SH-5, SH-6 |

## 4. Usage scenarios

### 4.1 Serving customers
A teller runs `dp-queue1 --prompt`, chooses `1` and enters `Smith Ann 1001 250.75`, then
`1` and `Jones Bob 1002 -12.5`. Choosing `3` shows `1: Smith, Ann; account 1001; balance
250.75` and `2: Jones, Bob; account 1002; balance -12.50`. Choosing `2` shows
`Removed: Smith, Ann; account 1001; balance 250.75`. Choosing `0` ends the session with exit
status 0. (UR-01, UR-03, UR-07, UR-08, UR-11)

### 4.2 Stacking trays
A manager runs `dp-stack2`, pushes a red, a green, and a blue tray, and pops one: the blue
tray is handed out first. (UR-02)

### 4.3 A full table
A script inserts 101 customers into `dp-queue1`. The 101st insertion prints `QUEUE FULL`, and
the queue still holds the first 100. The same commands given to `dp-queue2` insert all 101, and
apart from that one line the two outputs are the same. (UR-05, UR-06)

### 4.4 Wrapping around
A teller inserts 100 customers, serves 60, and inserts 60 more. The queue shows the 40
remaining original customers followed by the 60 new ones, in arrival order, in both queue
tools. (UR-01, UR-06)

### 4.5 Nothing to serve
Removing from an empty queue prints `QUEUE EMPTY`, and the session continues. (UR-04)

### 4.6 A slip
A command file holds `pop` where a command number belongs, on line 3. The results of the
earlier commands are printed, then the tool reports `bad-command.txt:3: invalid integer 'pop'`
and exits with status 1. (UR-10)

### 4.7 An old file
A command file copied from an MS-DOS machine has CRLF line endings and ends with Ctrl-Z bytes.
The tool reads it exactly like its LF version. (UR-12)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must work interactively: each result must appear before the tool waits for the next command. |

## 6. User acceptance criteria

The users will accept the four tools when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The four help texts exactly match the ones published in the user manual.
4. A design review confirms that each tool is the shared command driver bound to its own
   implementation of the queue or stack interface.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Queue | A first-in, first-out (FIFO) collection: records leave in the order they arrived |
| Stack | A last-in, first-out (LIFO) collection: the record added last leaves first |
| Front, rear | The oldest and the newest record of a queue |
| Top | The newest record of a stack |
| ADT | Abstract data type: a collection defined by its operations, independently of how it is stored |
| Circular array | A fixed table whose positions are reused from the start once the end is reached |
| Capacity | The number of records a table-based tool can hold: 100 |
| Balance | An amount of money with at most two decimal places, possibly negative |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
