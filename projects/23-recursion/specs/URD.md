# User Requirements Document (URD) — dp-fact, dp-tower, dp-walk-r, dp-walk-nr

| Field | Value |
| :-- | :-- |
| Document ID | URD-23 |
| Project | `23-recursion` — Recursion vs. Iteration Comparative Suite |
| Products | `dp-fact`, `dp-tower`, `dp-walk-r`, `dp-walk-nr` |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Successor documents | `SRS.md` (SRS-23), `user-manual.md` |

## 1. Introduction

### 1.1 Purpose
This document records what the users of `dp-fact`, `dp-tower`, `dp-walk-r`, and `dp-walk-nr`
need, in their own terms. It is the starting point for the Software Requirements Specification
(SRS-23), which turns each need into precise, testable system behavior.

### 1.2 Product vision
Four small tools answer three classic questions that are naturally stated recursively. How
large is *n*! ? Which moves carry a Tower of Hanoi of *n* disks from one peg to another? In how
many ways can a robot that takes steps of 1 and 2 meters walk a distance of *d* meters? The
robot question is answered twice, once by plain recursion (`dp-walk-r`) and once by iteration
(`dp-walk-nr`): the two tools always give the same answer, but one of them becomes slower and
slower as the distance grows while the other stays instant. A teacher can use the pair to show
the cost of recomputing the same sub-problems, and every tool gives exact answers right up to
the limit of 64-bit arithmetic and refuses, with a clear message, anything beyond it.

### 1.3 Scope
In scope: computing factorials, Tower of Hanoi move lists, and robot-walk counts for numbers
read from the keyboard, a pipe, or a file; optional prompts; reading data files written on
Windows or MS-DOS; reporting invalid numbers, numbers outside each tool's limits, and
unreadable files; help and version information.
Out of scope: numbers beyond the 64-bit range, arbitrary-precision results, other step sizes
or numbers of pegs, animated or graphical output, timing measurements in the output,
configuration files, and environment variables.

## 2. Stakeholders and user classes

| ID | Stakeholder | Description | Primary interest |
| :-- | :-- | :-- | :-- |
| SH-1 | Student | Types numbers at the keyboard on Linux, macOS, or Windows to explore recursion | Immediate, exact answers; clear prompts and messages |
| SH-2 | Teacher | Demonstrates recursion and compares the recursive and iterative walk tools in class | Identical answers from both walk tools; a visible difference in speed |
| SH-3 | Script author | Pipes lists of numbers through the tools and compares their outputs | Predictable output bytes and exit statuses |
| SH-4 | Learner (assignee) | Implements the four tools in a language repository of their choice | A complete, unambiguous specification, including the required recursive and iterative designs |
| SH-5 | Grader / CI | Runs automated acceptance tests on three operating systems | Deterministic, byte-exact behavior |

## 3. User requirements

Priorities use MoSCoW: **M** = Must, **S** = Should, **C** = Could.

| ID | Requirement (user's perspective) | Priority | Source |
| :-- | :-- | :-- | :-- |
| UR-01 | As a student, I want to enter any number of whole numbers to a tool and get the answer to each one, until I signal the end of the input. | M | SH-1 |
| UR-02 | As a student, I want the exact factorial of every whole number whose factorial fits in 64-bit arithmetic, from 0! = 1 up to 20!. | M | SH-1 |
| UR-03 | As a student, I want the complete list of moves that solves the Tower of Hanoi for a given number of disks, one move per line, in the order they must be made, with each move obeying the rules of the puzzle. | M | SH-1 |
| UR-04 | As a student, I want a tower of zero disks answered with "There's nothing to move!". | M | SH-1 |
| UR-05 | As a student, I want the number of ways the robot can walk a given distance, as one sentence that repeats the distance. | M | SH-1 |
| UR-06 | As a teacher, I want the recursive and the iterative walk tools to give identical answers for every distance both accept, so the comparison is only about speed. | M | SH-2 |
| UR-07 | As a teacher, I want the recursive walk tool to really recompute its sub-problems, so its run time visibly grows with the distance, and the iterative tool to stay fast up to the largest distance whose count fits in 64 bits. | M | SH-2 |
| UR-08 | As a student, I want a number a tool cannot answer exactly — too large for 64-bit results, too many disks to list, a negative factorial, a distance that is not positive, or text that is not a whole number — rejected with its position and a non-zero exit status, while the answers already given are kept. | M | SH-1, SH-3 |
| UR-09 | As a script author, I want to pipe numbers into a tool or name a file of numbers. | M | SH-3 |
| UR-10 | As a student, I want each tool to ask for each number when I request it, without the questions appearing in output I save. | S | SH-1 |
| UR-11 | As a student, I want each answer as soon as I have typed the number, not only at the end. | M | SH-1 |
| UR-12 | As a script author, I want a missing or unreadable file reported clearly, with a non-zero exit status. | M | SH-3 |
| UR-13 | As a student, I want data files written on Windows or MS-DOS, with CRLF line endings or a Ctrl-Z end-of-file mark, to be read correctly. | S | SH-1 |
| UR-14 | As a user of any of the tools, I want a built-in help screen and a version query. | M | SH-1, SH-3 |
| UR-15 | As a script author, I want invalid usage rejected with a clear message and a distinct exit status, before anything is read. | M | SH-3 |
| UR-16 | As a grader, I want identical output bytes on Linux, macOS, and Windows, so one set of expected outputs verifies every platform. | M | SH-5 |
| UR-17 | As a learner, I want the tools to follow the curriculum's common CLI conventions, and the required recursive and iterative designs to be stated clearly, so they can be reviewed. | M | SH-4 |
| UR-18 | As a grader, I want the tools to build, install, and uninstall with standard commands, regardless of their implementation language, and to answer within stated times. | M | SH-5 |

## 4. Usage scenarios

### 4.1 Factorials at the keyboard
A student runs `dp-fact --prompt`, sees `Enter a nonnegative integer: `, types `5` and Enter,
and at once sees `5! = 120`, followed by the next prompt. After the last number the student
presses Ctrl-D (Ctrl-Z then Enter on Windows) and the tool exits with status 0. (UR-01, UR-02,
UR-10, UR-11)

### 4.2 A small tower
A student types `3` to `dp-tower` and sees seven lines, from
`Move top disk from peg A to peg B.` to `Move top disk from peg A to peg B.`, which carry the
three disks from peg A to peg B. Typing `0` prints `There's nothing to move!`. (UR-03, UR-04)

### 4.3 Recursion against iteration
A teacher runs `dp-walk-r dists.txt > r.txt` and `dp-walk-nr dists.txt > nr.txt` on the
distances 1 to 10 and shows that the two files are identical, the fifth line reading
`The robot can walk 5 meters in 8 ways.` The teacher then times both tools for the distance 40:
`dp-walk-nr` answers instantly, `dp-walk-r` takes clearly longer, and every 5 extra meters
multiply its run time by about 11. (UR-05, UR-06, UR-07)

### 4.4 The limits of 64 bits
A student asks `dp-walk-nr` for 91 meters and receives the exact count 7540113804746346429; for
92 meters, whose count does not fit in 64 bits, the tool reports
`value out of range '92'` and exits with status 1. Asking `dp-fact` for 21! is refused in the
same way. (UR-02, UR-08)

### 4.5 A distance that is not positive
A file of distances contains `0` on its second line. `dp-walk-r` answers the first distance,
then reports `stop.txt:2: ERROR -- distance must be positive.` and exits with status 1.
(UR-08)

### 4.6 Discovery and mistakes
A user runs `dp-tower --help` to see the options, and `dp-walk-nr a.txt b.txt` is rejected
because a tool reads one file. (UR-14, UR-15)

## 5. Operational constraints

| ID | Constraint |
| :-- | :-- |
| UC-1 | Must run on current Linux, macOS, and Windows releases, as native executables or language-runtime launchers. |
| UC-2 | Must be buildable, testable, installable, and removable through the curriculum's universal `Makefile` targets. |
| UC-3 | Must not require network access, elevated privileges, or configuration files. |
| UC-4 | Must behave identically whatever the user's locale or terminal settings. |
| UC-5 | Must give the same exact answers whatever the platform's native integer sizes and default call-stack size. |
| UC-6 | Must work interactively: a tool must not wait for the end of the input before answering. |

## 6. User acceptance criteria

The users will accept the four tools when all of the following hold:

1. Every scenario in section 4 behaves as described on Linux, macOS, and Windows.
2. All public and hidden black-box tests pass in CI on all three platforms.
3. The four help texts exactly match the ones published in the user manual.
4. A design review confirms the recursive and iterative structures required by SRS-23 NFR-05,
   and a measurement confirms the run times of SRS-23 NFR-03.

## 7. Glossary

| Term | Meaning |
| :-- | :-- |
| Factorial | *n*! = 1 × 2 × … × *n*, with 0! = 1 |
| Tower of Hanoi | A puzzle of disks of different sizes stacked on one of three pegs; the tower must be moved to another peg, one disk at a time, never placing a disk on a smaller one |
| Peg A, B, C | The pegs: the tower starts on A and must end on B; C is the spare |
| Move | Taking the top disk of one peg and placing it on another |
| Robot walk | A way of covering a distance in steps of 1 meter and 2 meters; the order of the steps matters |
| W(*d*) | The number of robot walks of *d* meters |
| Recursion | Solving a problem by solving smaller instances of the same problem |
| Iteration | Solving a problem with a loop that updates a fixed set of values |
| Prompt | A question a tool writes before reading a number, only when asked to with `--prompt` |
| End of input | The end of the file or pipe, or Ctrl-D (POSIX) / Ctrl-Z then Enter (Windows) at a keyboard |
| Exit status | The integer a process returns to its caller; 0 means success |
