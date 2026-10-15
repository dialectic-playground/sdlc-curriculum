<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-fact, dp-tower, dp-walk-r, dp-walk-nr — User Manual](#dp-fact-dp-tower-dp-walk-r-dp-walk-nr--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [dp-fact](#dp-fact)
    - [dp-tower](#dp-tower)
    - [dp-walk-r and dp-walk-nr](#dp-walk-r-and-dp-walk-nr)
    - [Errors in the input](#errors-in-the-input)
    - [Working interactively](#working-interactively)
  - [OPTIONS](#options)
    - [Option syntax](#option-syntax)
  - [EXIT STATUS](#exit-status)
  - [DIAGNOSTICS](#diagnostics)
  - [EXAMPLES](#examples)
  - [HELP OUTPUT](#help-output)
  - [VERSION OUTPUT](#version-output)
  - [ENVIRONMENT](#environment)
  - [PLATFORM NOTES](#platform-notes)
  - [INSTALLATION](#installation)
  - [SEE ALSO](#see-also)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# dp-fact, dp-tower, dp-walk-r, dp-walk-nr — User Manual

| Field         | Value                                                                    |
| :------------ | :----------------------------------------------------------------------- |
| Products      | `dp-fact` 1.0.0, `dp-tower` 1.0.0, `dp-walk-r` 1.0.0, `dp-walk-nr` 1.0.0 |
| Project       | `23-recursion` — Recursion vs. Iteration Comparative Suite               |
| Applies to    | Linux, macOS, Windows                                                    |
| Specification | `SRS.md` (SRS-23), `shared/CLI-CONVENTIONS.md`                           |

---

## NAME

**dp-fact** — print factorials, computed by recursion

**dp-tower** — print the moves that solve the Tower of Hanoi

**dp-walk-r** — count robot walks by plain recursion

**dp-walk-nr** — count robot walks by iteration

## SYNOPSIS

```text
dp-fact [-p | --prompt] [FILE]
dp-tower [-p | --prompt] [FILE]
dp-walk-r [-p | --prompt] [FILE]
dp-walk-nr [-p | --prompt] [FILE]
<tool> --help | --version
```

## DESCRIPTION

Each tool reads whole numbers from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`, until the end of the input, and answers each number as soon as it has been read.
Numbers are written in decimal digits with an optional `+` or `-` sign; leading zeros are
allowed. They are separated by any mix of spaces, tabs, and line breaks, so several numbers may
share a line, and files with Windows (CRLF) line endings read the same as any other. A number
is printed as a plain number: `+7` is printed as `7` and `010` as `10`. One or more Ctrl-Z
bytes at the very end of the input (the end-of-file mark of old MS-DOS data files) are ignored.

### dp-fact

For each number _n_ from 0 to 20, `dp-fact` prints _n_!, the product 1 × 2 × … × _n_, with
0! = 1:

```text
5! = 120
```

20! = 2432902008176640000 is the largest factorial that fits in a 64-bit integer, so 21 and
larger numbers are refused, as are negative numbers.

### dp-tower

The Tower of Hanoi is a stack of _n_ disks of different sizes on peg A. `dp-tower` prints the
moves that carry the whole stack to peg B, using peg C as the spare, moving one disk at a time
and never placing a disk on a smaller one. For three disks:

```text
Move top disk from peg A to peg B.
Move top disk from peg A to peg C.
Move top disk from peg B to peg C.
Move top disk from peg A to peg B.
Move top disk from peg C to peg A.
Move top disk from peg C to peg B.
Move top disk from peg A to peg B.
```

_n_ disks take 2ⁿ − 1 moves, so the list doubles with every disk. `dp-tower` accepts at most 20
disks (1 048 575 moves, about 35 MiB of output). For 0 disks, or a negative number, it prints
`There's nothing to move!`. The move lists of several numbers follow one another directly.

### dp-walk-r and dp-walk-nr

A robot walks in steps of 1 meter and 2 meters. The number of different ways it can walk _d_
meters is W(_d_): W(1) = 1, W(2) = 2, and each further meter adds the two counts before it,
W(_d_) = W(_d_ − 1) + W(_d_ − 2). For example, 4 meters can be walked as 1+1+1+1, 1+1+2, 1+2+1,
2+1+1, or 2+2, so W(4) = 5. Both tools print one sentence per distance:

```text
The robot can walk 4 meters in 5 ways.
```

The words are never made singular: a distance of 1 prints `1 meters in 1 ways`.

The two tools always give the same answers. They differ in how they compute them:

- `dp-walk-r` applies the definition literally: to count the walks of _d_ meters it counts the
  walks of _d_ − 1 and of _d_ − 2 meters from scratch, and so on down to 1 and 2 meters. The
  same counts are recomputed again and again, and the work grows by a factor of about 1.6 per
  meter (about 11 per 5 meters). It accepts distances from 1 to 45.
- `dp-walk-nr` starts from 1 and 2 meters and works upward with a loop, keeping only the last
  two counts, so its work grows only in proportion to the distance. It accepts distances from 1
  to 91; W(91) = 7540113804746346429 is the largest count that fits in a 64-bit integer.

Time the two tools on the same distance to see the difference; the outputs themselves never
include timings.

### Errors in the input

A tool stops at the first number it cannot answer, reports it with its line number, and exits
with status 1; the answers already printed remain valid. Text that is not a whole number, and a
number larger than the tool's limit, are errors for every tool. A negative number is an error
for `dp-fact`; a distance of 0 or less is reported by the walk tools with the message
`ERROR -- distance must be positive.`

### Working interactively

Each answer appears as soon as you finish typing a number (press Enter or Space). End the input
with **Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by **Enter** in a Windows console.
With `--prompt`, a tool asks for each number on standard error:

| Tool                      | Prompt                          |
| :------------------------ | :------------------------------ |
| `dp-fact`                 | `Enter a nonnegative integer: ` |
| `dp-tower`                | `Enter number of disks: `       |
| `dp-walk-r`, `dp-walk-nr` | `Enter distance: `              |

```text
$ dp-walk-nr --prompt
Enter distance: 5
The robot can walk 5 meters in 8 ways.
Enter distance: 40
The robot can walk 40 meters in 165580141 ways.
Enter distance: ^D
```

The prompts are written to standard error, so `dp-fact --prompt > facts.txt` saves only the
answers.

## OPTIONS

All four tools have the same options.

**`-p`, `--prompt`**
: Before each number is read, write the tool's prompt to standard error. A last prompt appears
before the end of the input is noticed.

**`--help`**
: Display the tool's help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

The tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-fact numbers.txt -p` works.
- `--` ends option processing, so `dp-fact -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                     |
| :----- | :------------------------------------------------------------------------------------------ |
| 0      | Success: every number was answered (an empty input is fine), or help or version was printed |
| 1      | The input could not be read, or it contained a number the tool cannot answer                |
| 2      | Usage error: an invalid option or more than one file                                        |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Answers
printed before the problem are kept, and the exit status is 1:

```text
$ printf '3\n0\n4\n' | dp-walk-r
The robot can walk 3 meters in 3 ways.
dp-walk-r: -:2: ERROR -- distance must be positive.
```

| Message                                    | Cause                                                                                                       | Fix                                                                              |
| :----------------------------------------- | :---------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------- |
| `S:L: invalid integer 'K'`                 | Entry _K_ on line _L_ is not a whole number, or is larger than 9223372036854775807                          | Write the number in digits only, without separators or decimals                  |
| `S:L: value out of range 'K'`              | `dp-fact`: _K_ is negative or above 20; `dp-tower`: above 20; `dp-walk-r`: above 45; `dp-walk-nr`: above 91 | Use a number within the tool's limits (for distances 46 to 91, use `dp-walk-nr`) |
| `S:L: ERROR -- distance must be positive.` | A walk tool was given a distance of 0 or less                                                               | Enter a distance of at least 1                                                   |
| `F: No such file or directory`             | _F_ does not exist                                                                                          | Check the spelling and the current directory                                     |
| `F: Permission denied`                     | You may not read _F_                                                                                        | Check the file's permissions                                                     |
| `F: Is a directory`                        | _F_ is a directory                                                                                          | Name a file instead                                                              |
| `F: Not a directory`                       | Part of the path _F_ is a file, not a directory                                                             | Correct the path                                                                 |
| `F: Input/output error`                    | Any other read failure                                                                                      | Check the device or file system                                                  |
| `write error`                              | The answers could not be written (for example, the disk is full)                                            | Free space or redirect the output elsewhere                                      |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-walk-nr dists.txt extra
dp-walk-nr: extra operand 'extra'
Try 'dp-walk-nr --help' for more information.
```

| Message                                       | Cause                                                   | Fix                        |
| :-------------------------------------------- | :------------------------------------------------------ | :------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`                   |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full   |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`            |
| `extra operand 'F'`                           | More than one file was named                            | Run the tool once per file |

## EXAMPLES

Several factorials at once:

```text
$ echo 0 5 10 20 | dp-fact
0! = 1
5! = 120
10! = 3628800
20! = 2432902008176640000
```

Count the moves for 10 disks:

```text
$ echo 10 | dp-tower | wc -l
1023
```

Check that the recursive and iterative walk tools agree on the distances 1 to 30:

```sh
seq 30 > d.txt
dp-walk-r d.txt > r.txt && dp-walk-nr d.txt > nr.txt && cmp r.txt nr.txt
```

Compare their speed (the times depend on the computer):

```sh
time (echo 40 | dp-walk-r)
time (echo 40 | dp-walk-nr)
```

The largest distance whose count fits in 64 bits:

```text
$ echo 91 | dp-walk-nr
The robot can walk 91 meters in 7540113804746346429 ways.
```

## HELP OUTPUT

The four tools' `--help` options print exactly the following texts (every line ends in LF).
The help texts are part of the specification (CONV-23).

`dp-fact --help`:

```text
Usage: dp-fact [OPTION]... [FILE]
Print the factorial of each number in FILE, computed by recursion.

With no FILE, or when FILE is -, read standard input.  Numbers are whole
numbers from 0 to 20, separated by whitespace, and are read until the end of
the input.  For each number N the line 'N! = VALUE' is printed.

Options:
  -p, --prompt    write the prompt 'Enter a nonnegative integer: ' to standard
                    error before each number is read
      --help      display this help and exit
      --version   output version information and exit
```

`dp-tower --help`:

```text
Usage: dp-tower [OPTION]... [FILE]
Print the moves that solve the Tower of Hanoi, computed by recursion.

With no FILE, or when FILE is -, read standard input.  For each number of
disks N in FILE (a whole number, at most 20), print the 2^N-1 moves that carry
a tower of N disks from peg A to peg B, using peg C as the spare, one move per
line.  For a number below 1, print "There's nothing to move!".

Options:
  -p, --prompt    write the prompt 'Enter number of disks: ' to standard error
                    before each number is read
      --help      display this help and exit
      --version   output version information and exit
```

`dp-walk-r --help`:

```text
Usage: dp-walk-r [OPTION]... [FILE]
Count the ways a robot can walk a distance in steps of 1 and 2 meters, by
plain recursion.

With no FILE, or when FILE is -, read standard input.  Distances are whole
numbers from 1 to 45, separated by whitespace.  The count is computed from
W(1) = 1, W(2) = 2, W(d) = W(d-1) + W(d-2) by recursion that remembers no
earlier result, so its run time grows exponentially with the distance; see
dp-walk-nr for distances up to 91.

Options:
  -p, --prompt    write the prompt 'Enter distance: ' to standard error before
                    each distance is read
      --help      display this help and exit
      --version   output version information and exit
```

`dp-walk-nr --help`:

```text
Usage: dp-walk-nr [OPTION]... [FILE]
Count the ways a robot can walk a distance in steps of 1 and 2 meters, by
iteration.

With no FILE, or when FILE is -, read standard input.  Distances are whole
numbers from 1 to 91, separated by whitespace.  The count is computed from
W(1) = 1, W(2) = 2, W(d) = W(d-1) + W(d-2) by a loop that keeps only the last
two counts, so its run time grows linearly with the distance.

Options:
  -p, --prompt    write the prompt 'Enter distance: ' to standard error before
                    each distance is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-fact (dialectic-playground) 1.0.0
dp-tower (dialectic-playground) 1.0.0
dp-walk-r (dialectic-playground) 1.0.0
dp-walk-nr (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

The tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a number).
- **All platforms:** answers are exact and identical everywhere, whatever the size of the
  platform's native integers or its default stack size.
- **Large towers:** 20 disks produce about 35 MiB of output; redirect it to a file or a pipe
  rather than a terminal.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build dp-fact, dp-tower, dp-walk-r, and dp-walk-nr
make install      # install all four into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-tromino` (project 24), another recursive divide-and-conquer program;
`dp-sort-bench` (project 35), which also compares algorithms by measurement; `dp-taxes`
(project 13), which reads numbers the same way; `factor(1)`, `seq(1)`, `time(1)`.
