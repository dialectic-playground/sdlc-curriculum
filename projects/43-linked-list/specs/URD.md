# User Requirements Document (URD) — dp-elephnt1, dp-elephnt2

| Field | Value |
| :-- | :-- |
| Document ID | URD-43 |
| Project | `43-linked-list` — Singly Linked List Foundations |
| Products | `dp-elephnt1`, `dp-elephnt2` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-43), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-elephnt1` and `dp-elephnt2` need, in their own
terms. It is the starting point for the Software Requirements Specification (SRS-43), which
turns each need into precise, testable system behavior.

### 1.2 Product vision
Two small programs demonstrate the linked list. `dp-elephnt1` shows the idea at its simplest:
three elephants, Edna, Elmer, and Eloise, each in a node that points to the next, printed by
following the links. `dp-elephnt2` lets a zookeeper type the names of any number of elephants,
answering after each one whether there is another, and then prints the herd in the order the
names were given. Typed at a keyboard or fed from a file, the dialog behaves the same way, and
a slip of the keyboard is reported clearly instead of printing a wrong list.

### 1.3 Scope
In scope: printing the fixed three-elephant list; building a list of any length from a dialog
of names and yes/no answers, read from the keyboard, a pipe, or a file; optional prompts;
reading files written on Windows or MS-DOS; reporting malformed dialogs and unreadable files;
help and version information.
Out of scope: editing, deleting, sorting, or searching the list; saving it to a file; names
spread over several lines; answers other than 0 and 1; configuration files and environment
variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Zookeeper | Types elephant names at the keyboard on Linux, macOS, or Windows | Clear questions; the herd printed in the order entered; helpful errors |
| SH-2 | Script author | Feeds prepared dialogs to `dp-elephnt2` and uses the output and exit status | Predictable output bytes and exit statuses |
| SH-3 | Instructor | Uses both tools to teach linked lists | Programs whose structure is a real linked list, with one shared traversal |
| SH-4 | Learner (assignee) | Implements both tools in a language repository of their choice | A complete, unambiguous specification and a clear required structure |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As an instructor, I want `dp-elephnt1` to print the three elephants Edna, Elmer, and Eloise, numbered in list order, without reading any input. | M | SH-3 |
| UR-02 | As a zookeeper, I want to enter one elephant name, then say whether I want to add another, and repeat until I say no. | M | SH-1 |
| UR-03 | As a zookeeper, I want each elephant printed as `Elephant number N is NAME.`, numbered from 1 in the order I entered them. | M | SH-1, SH-2 |
| UR-04 | As a zookeeper, I want names that contain spaces, such as `Babar the Elephant`, kept whole, while stray spaces before or after a name or an answer are ignored. | M | SH-1 |
| UR-05 | As a zookeeper, I want the list to end when I answer 0, or when I end the input instead of answering. | M | SH-1, SH-2 |
| UR-06 | As a zookeeper, I want an answer other than 0 or 1, a blank name, or a dialog that ends while a name is still expected reported with the line where it happened, and no list printed. | M | SH-1, SH-2 |
| UR-07 | As a zookeeper at the keyboard, I want to be asked for each name and each answer, the way the textbook program asked, without the questions appearing in output I redirect to a file. | S | SH-1 |
| UR-08 | As a script author, I want to pipe a dialog into `dp-elephnt2` or name a file holding it. | M | SH-2 |
| UR-09 | As a zookeeper, I want dialog files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-10 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-2 |
| UR-11 | As an instructor, I want both programs to store the elephants in a real linked list — nodes that refer to their successors, ended by an explicit end marker — and to print it with one shared traversal. | M | SH-3, SH-4 |
| UR-12 | As a terminal user, I want a built-in help screen and a version query for each tool. | M | SH-1, SH-2 |
| UR-13 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status. | M | SH-2 |
| UR-14 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-15 | As a learner and grader, I want the tools to follow the curriculum's common CLI conventions and to build, install, and uninstall with standard commands in any language, handling long dialogs quickly. | M | SH-4, SH-5 |

## 4. Usage scenarios

### 4.1 The fixed herd
An instructor runs `dp-elephnt1` and sees `Elephant number 1 is Edna.`, `Elephant number 2 is
Elmer.`, and `Elephant number 3 is Eloise.`. (UR-01, UR-03)

### 4.2 At the keyboard
A zookeeper runs `dp-elephnt2 --prompt`, sees `NAME:` indented by a tab, types `Dumbo`, is
asked `Add another? (1 == yes, 0 == no)`, types `1`, enters `Babar`, answers `0`, and sees
`Elephant number 1 is Dumbo.` and `Elephant number 2 is Babar.`. The exit status is 0.
(UR-02, UR-03, UR-07)

### 4.3 A prepared dialog
A script runs `dp-elephnt2 herd.txt > herd-list.txt`. The file holds only the numbered list.
A name typed as `  Jumbo  ` is listed as `Jumbo`, and `Babar the Elephant` is kept whole.
(UR-03, UR-04, UR-08)

### 4.4 Stopping early
A zookeeper enters a name and then ends the input (Ctrl-D, or Ctrl-Z and Enter on Windows)
instead of answering. The list is printed as if the answer had been 0. (UR-05)

### 4.5 A slip
In a dialog file, the answer on line 4 is `yes`. The tool prints no list and reports
`bad-answer.txt:4: invalid integer 'yes'`, exit status 1. A file that ends right after the
answer 1 is reported as `unexpected end of input`. (UR-06)

### 4.6 An old file
A dialog file copied from an MS-DOS machine has CRLF line endings and a final Ctrl-Z byte. The
tool reads it exactly like the LF version. (UR-09)

### 4.7 A code review
An instructor reviews an implementation and finds a node record with a name and a successor
link, a list builder that appends through a tail reference, and one traversal procedure called
by both programs. (UR-11)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as a native executable or a language-runtime launcher. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | `dp-elephnt2` must work interactively: each prompt must appear before the tool waits for the line it asks for. |

## 6. User acceptance criteria

The users will accept `dp-elephnt1` and `dp-elephnt2` when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. Both help texts exactly match the ones published in the user manual.
4. A design review confirms the linked structure of UR-11.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Node | One element of the list: an elephant's name and a link to the next node |
| Link, successor | The reference from a node to the node after it |
| End marker | The special link value (for example a null reference) that the last node holds instead of a successor |
| Head | The first node of the list |
| Traversal | Visiting every node by following the links from the head to the end marker |
| Dialog | The alternating sequence of names and answers that `dp-elephnt2` reads |
| Answer | `1` (add another elephant) or `0` (no more elephants) |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
