<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-tromino — User Manual](#dp-tromino--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Coordinates](#coordinates)
    - [How the tiling is built](#how-the-tiling-is-built)
    - [Drawing the board](#drawing-the-board)
    - [Answers](#answers)
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

# dp-tromino — User Manual

| Field         | Value                                                       |
| :------------ | :---------------------------------------------------------- |
| Product       | `dp-tromino` 1.0.0                                          |
| Project       | `24-tromino` — Divide-and-Conquer Tromino Deficiency Tiling |
| Applies to    | Linux, macOS, Windows                                       |
| Specification | `SRS.md` (SRS-24), `shared/CLI-CONVENTIONS.md`              |

---

## NAME

**dp-tromino** — tile a deficient 2ᵏ × 2ᵏ board with L-shaped trominoes

## SYNOPSIS

```text
dp-tromino [-d | --draw] [-p | --prompt] [FILE]
dp-tromino --help
dp-tromino --version
```

## DESCRIPTION

`dp-tromino` reads answers from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`. Each round of answers is a board size — 2, 4, 8, 16, 32, or 64 — followed by the
x and y coordinates of the board's missing square. For each round, `dp-tromino` covers every
other square of the board with L-shaped trominoes and lists them:

```text
Tiling
------
2 2 LR
1 3 UL
3 3 UR
3 1 LR
1 1 LL
```

Rounds continue until a board size of **0** or the end of the input.

### Coordinates

Squares are numbered from 0. The x coordinate is the column, counted from the left; the y
coordinate is the row, counted **from the bottom**. So `0 0` is the lower-left square of every
board, and `3 3` is the upper-right square of a 4 × 4 board.

Each tromino covers three squares of a 2 × 2 block. The two numbers on its line are the
**center** of that block — the point where its four squares meet, counted in the same way, so a
block made of the squares `0 0`, `1 0`, `0 1`, and `1 1` has center `1 1`. The two letters say
in which corner of the block the tromino's arms meet, which is the corner opposite the square
it leaves out:

```text
  UL      UR      LR      LL
  ##      ##      .#      #.
  #.      .#      ##      ##
```

(`#` is covered, `.` is the square left out; the top row is the upper row.)

### How the tiling is built

`dp-tromino` uses the textbook's divide-and-conquer method. It places one tromino at the center
of the board, covering one square in each quarter that does not contain the missing square.
Now each quarter has exactly one square that must stay free, so each quarter is tiled the same
way, in the order upper left, upper right, lower right, lower left. A 2 × 2 board needs a
single tromino. Every tromino is listed before the trominoes of the quarters inside it, so the
first line is always the tromino at the center of the whole board. A board of size _n_ takes
(*n*² − 1) / 3 trominoes: 1, 5, 21, 85, 341, or 1365.

### Drawing the board

With `--draw`, each list is followed by a drawing of the board, top row first. Each square
shows the number of the tromino that covers it — its position in the list, counting from 1 —
and the missing square shows `X`. The numbers are right-aligned in columns as wide as the
largest number:

```text
Board
-----
2 2 3 3
2 X 1 3
5 1 1 4
5 5 4 4
```

### Answers

Answers are whole numbers written in decimal digits with an optional `+` or `-` sign; leading
zeros are allowed. They are separated by any mix of spaces, tabs, and line breaks, so a round
may be typed on one line (`4 1 2`) or several, and files with Windows (CRLF) line endings read
the same as any other. One or more Ctrl-Z bytes at the very end of the input (the end-of-file
mark of old MS-DOS files) are ignored.

A board size other than 0, 2, 4, 8, 16, 32, or 64, a coordinate outside the board, or anything
that is not a whole number is an error. `dp-tromino` reports the first such answer with its
line number and stops; the tilings already printed remain valid. After a size of 0, the rest of
the input is not read.

### Working interactively

`dp-tromino` prints each tiling as soon as you have typed the second coordinate and pressed
Enter or Space. End the session with a size of 0, or end the input with **Ctrl-D** on Linux and
macOS or **Ctrl-Z** followed by **Enter** in a Windows console. With `--prompt`,
`dp-tromino` asks for each answer:

```text
$ dp-tromino --prompt
Enter size of board (0 to quit): 2
Enter coordinates of missing square: 1 1
Tiling
------
1 1 LL
Enter size of board (0 to quit): 0
```

The prompts are written to standard error, so `dp-tromino --prompt > tiling.txt` saves only
the tilings.

## OPTIONS

**`-d`, `--draw`**
: After the list of each round, draw the board with every square numbered by the tromino that
covers it.

**`-p`, `--prompt`**
: Write `Enter size of board (0 to quit): ` to standard error before each board size is read,
and `Enter coordinates of missing square: ` before the two coordinates. A last size prompt
appears before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-tromino` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be combined: `-dp` is `-d -p`.
- Long options must be spelled out in full; `--dra` is not accepted.
- Options and the file name can be given in any order: `dp-tromino boards.txt -d` works.
- `--` ends option processing, so `dp-tromino -- -d` reads a file named `-d`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                         |
| :----- | :------------------------------------------------------------------------------------------------------------------------------ |
| 0      | Success: the session ended with a size of 0 or at the end of the input (an empty input is fine), or help or version was printed |
| 1      | The input could not be read, it contained an invalid answer, or it ended in the middle of a round                               |
| 2      | Usage error: an invalid option or more than one file                                                                            |

## DIAGNOSTICS

Problems with the answers name the input (`-` for standard input) and the line number.
Tilings printed before the problem are kept, and the exit status is 1:

```text
$ dp-tromino bad-size.txt
Tiling
------
2 2 LR
1 3 UL
3 3 UR
3 1 LR
1 1 LL
dp-tromino: bad-size.txt:3: invalid board size '6'
```

| Message                        | Cause                                                           | Fix                                                |
| :----------------------------- | :-------------------------------------------------------------- | :------------------------------------------------- |
| `S:L: invalid integer 'K'`     | Answer _K_ on line _L_ is not a whole number                    | Write the answer in digits only                    |
| `S:L: invalid board size 'K'`  | Board size _K_ is not 0, 2, 4, 8, 16, 32, or 64                 | Use a power of 2 from 2 to 64, or 0 to quit        |
| `S:L: value out of range 'K'`  | Coordinate _K_ is negative or not smaller than the board size   | Use coordinates from 0 to size − 1                 |
| `S:L: unexpected end of input` | The input ended after a board size, before both coordinates     | Complete the last round, or end the session with 0 |
| `F: No such file or directory` | _F_ does not exist                                              | Check the spelling and the current directory       |
| `F: Permission denied`         | You may not read _F_                                            | Check the file's permissions                       |
| `F: Is a directory`            | _F_ is a directory                                              | Name a file instead                                |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                 | Correct the path                                   |
| `F: Input/output error`        | Any other read failure                                          | Check the device or file system                    |
| `write error`                  | The output could not be written (for example, the disk is full) | Free space or redirect the output elsewhere        |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-tromino readme.txt boards.txt
dp-tromino: extra operand 'boards.txt'
Try 'dp-tromino --help' for more information.
```

| Message                                     | Cause                                                   | Fix                            |
| :------------------------------------------ | :------------------------------------------------------ | :----------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                               | Use `-d` or `-p`               |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                      | Spell the option in full       |
| `option '--draw' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                |
| `extra operand 'F'`                         | More than one file was named                            | Run `dp-tromino` once per file |

## EXAMPLES

The textbook's board, with its drawing:

```text
$ printf '4 1 2\n0\n' | dp-tromino --draw
Tiling
------
2 2 LR
1 3 UL
3 3 UR
3 1 LR
1 1 LL
Board
-----
2 2 3 3
2 X 1 3
5 1 1 4
5 5 4 4
```

Every way to tile a 2 × 2 board; the input ends without a 0:

```text
$ printf '2 0 0\n2 1 0\n2 0 1\n2 1 1\n' | dp-tromino
Tiling
------
1 1 UR
Tiling
------
1 1 UL
Tiling
------
1 1 LR
Tiling
------
1 1 LL
```

Check that a tiling of the largest board has 1365 trominoes (the list plus two heading lines):

```sh
printf '64 63 63\n' | dp-tromino | wc -l     # prints 1367
```

## HELP OUTPUT

`dp-tromino --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-tromino [OPTION]... [FILE]
Tile a 2^k-by-2^k board with one missing square using L-shaped trominoes.

Read whitespace-separated answers from FILE, or from standard input when FILE
is absent or -.  Each round gives a board size (2, 4, 8, 16, 32, or 64; 0 to
quit) and the x and y coordinates of the missing square (0 to size-1, with
0 0 the lower-left square).  For each tromino placed, in divide-and-conquer
order, a line gives the center of its 2-by-2 block and its orientation (UL,
UR, LR, or LL: the corner where its two arms meet).

Options:
  -d, --draw      after each tiling, draw the board with numbered trominoes
  -p, --prompt    write prompts to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-tromino (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-tromino` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Answer files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF. Writing a large drawing to a console window is slower
  than redirecting it to a file, but produces the same text.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing an answer).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-tower` and `dp-fact` (project 23), other classic recursions; `dp-koch` (project 51),
another self-similar recursive construction; `dp-perc` (project 32), which also prints a
square grid; `wc(1)`.
