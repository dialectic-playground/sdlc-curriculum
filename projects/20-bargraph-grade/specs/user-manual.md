# dp-bargraph2, dp-grade — User Manual

| Field | Value |
| :-- | :-- |
| Products | `dp-bargraph2` 1.0.0, `dp-grade` 1.0.0 |
| Project | `20-bargraph-grade` — Modular Procedural Decomposition & Evaluation |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-20), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-bargraph2** — draw a bar graph of titled values (procedural version of `dp-bargraph`)

**dp-grade** — assign a pass/fail grade from two weighted exam scores

## SYNOPSIS

```text
dp-bargraph2 [FILE]
dp-grade [-p | --prompt] [FILE]
dp-bargraph2 --help | --version
dp-grade --help | --version
```

## DESCRIPTION

### dp-bargraph2

`dp-bargraph2` behaves exactly like `dp-bargraph` (project 16): for the same arguments and
input it prints the same graph, the same diagnostics (with its own name), and exits with the
same status. It reads *records* from *FILE*, or from standard input when *FILE* is absent or
`-`. Each record is two lines, a **title** and a **value**; the tool prints the title, then a
bar of one `*` for every 2 units of the value, rounded down.

- Lines end with LF or CR LF. The last line needs no line ending.
- A title is printed exactly as written, including its spaces; it may be empty.
- A value is a whole number from 0 to 10000 on a line of its own; spaces and tabs around it,
  a leading `+`, and leading zeros are allowed.
- Blank lines at the end of the input, and a run of Ctrl-Z bytes (`0x1A`) at its very end, are
  ignored.

```text
$ dp-bargraph2 bargraph.in
Detective Comics
**********************************************
Action Comics
*********************************************
Marvel Comics
*************************************
Superman
***********************************
Whiz Comics
*********************
```

### dp-grade

`dp-grade` reads answers from *FILE*, or from standard input when *FILE* is absent or `-`.
Answers are separated by any mix of spaces, tabs, and line breaks. The session is a series of
rounds:

1. An answer: `1` to compute a grade, `0` to stop. The end of the input also stops.
2. After `1`: the **mid-term score** and the **final-exam score**, whole numbers from 0 to 10,
   and the **weight** of the mid term, a number from 0 to 1 (for example `0.5`, `.25`, or
   `1e-1`). The final exam gets the remaining weight.

For each round, `dp-grade` prints `Grade is: P` if the weighted average

*weight* × *mid term* + (1 − *weight*) × *final*

is greater than 7, and `Grade is: F` otherwise. An average of exactly 7 is a fail.

The weight is used to the nearest thousandth (0.001), and the average is then computed
exactly, so the grade is always the one the decimal numbers imply: with scores 7 and 7 and a
weight of 0.2 the average is exactly 7, a fail, on every computer. A weight with more than
three decimal places is rounded: `0.7004` is used as 0.700 and `0.7005` as 0.701.

After the answer `0`, the rest of the input is not read.

### Prompts

With `-p` or `--prompt`, `dp-grade` asks its questions on standard error:

- `Compute another grade (1 = Yes, 0 = No)? ` before every answer;
- `Enter mid term, final, weight: ` once per round, before the three values.

Each prompt ends with a space and no line feed, so you type on the same line. The grades on
standard output are the same with or without `--prompt`.

## OPTIONS

**`-p`, `--prompt`** (dp-grade only)
: Write the prompts described above to standard error before each read.

**`--help`**
: Display the tool's help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

Both tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be mixed: `dp-grade grades.txt -p` works.
- `--` ends option processing, so `dp-grade -- -grades.txt` reads a file named `-grades.txt`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the whole input was processed, or help or version was printed |
| 1 | The file could not be read, or the data contains an error |
| 2 | Usage error: an invalid option or more than one *FILE* |

## DIAGNOSTICS

Errors in the data name the input (`-` for standard input) and the line. Everything printed
before the error stands; nothing more is read:

```text
$ dp-grade bad-score.txt
Grade is: P
dp-grade: bad-score.txt:4: value out of range '11'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `FILE:LINE: invalid integer 'TOKEN'` | dp-grade: an answer or score is not a whole number; dp-bargraph2: a value line is not a single whole number | Write a whole number |
| `FILE:LINE: value out of range 'TOKEN'` | dp-grade: an answer other than 0 or 1, a score outside 0–10, or a weight outside 0–1; dp-bargraph2: a value outside 0–10000 | Use a value in range |
| `FILE:LINE: invalid number 'TOKEN'` | dp-grade: the weight is not a number | Write the weight like `0.5` |
| `FILE:LINE: unexpected end of input` | dp-grade: the input ends in the middle of a round; dp-bargraph2: it ends after a title | Complete the round or record |
| `FILE: No such file or directory` | *FILE* does not exist | Check the name |
| `FILE: Is a directory` | *FILE* is a directory | Name a file |
| `FILE: Permission denied` | *FILE* cannot be read | Check its permissions |

Usage errors are written to standard error as two lines; nothing is read and nothing is written
to standard output:

```text
$ dp-grade --prompt=yes
dp-grade: option '--prompt' doesn't allow an argument
Try 'dp-grade --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option (`dp-bargraph2` has no `-p`) | Remove it |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | `=…` after `--prompt`, `--help`, or `--version` | Remove the `=…` |
| `extra operand 'b'` | More than one *FILE* | Give one file |

## EXAMPLES

Grade the textbook's examples from a file (`readme-grades.txt` holds `1`, `8 6 0.5`, `1`,
`8 7 0.5`, `1`, `10 5 0.8`, `0`, one per line):

```text
$ dp-grade readme-grades.txt
Grade is: F
Grade is: P
Grade is: P
```

Grade at the keyboard (what you type is shown after each prompt):

```text
$ dp-grade -p
Compute another grade (1 = Yes, 0 = No)? 1
Enter mid term, final, weight: 7 7 0.2
Grade is: F
Compute another grade (1 = Yes, 0 = No)? 0
```

Keep only the grades when prompting:

```sh
dp-grade --prompt > results.txt
```

Check that the two bar-graph tools agree:

```sh
dp-bargraph prices.txt > a.txt; dp-bargraph2 prices.txt > b.txt; cmp a.txt b.txt
```

## HELP OUTPUT

`dp-bargraph2 --help` and `dp-grade --help` print exactly the following texts (every line ends
in LF). The help texts are part of the specification (CONV-23).

`dp-bargraph2 --help`:

```text
Usage: dp-bargraph2 [OPTION]... [FILE]
Draw a bar graph: for each record, print its title, then a bar of one '*' for
every 2 units of its value.

With no FILE, or when FILE is -, read standard input.  Lines alternate between
a title and a value; a value is a whole number from 0 to 10000 on a line of
its own.  Blank lines after the last record are ignored.

Options:
      --help       display this help and exit
      --version    output version information and exit
```

`dp-grade --help`:

```text
Usage: dp-grade [OPTION]... [FILE]
Assign a pass/fail grade from a mid-term score, a final-exam score, and the
weight of the mid term.

Read whitespace-separated answers from FILE, or from standard input when FILE
is absent or -.  Each round starts with 1 (compute a grade) or 0 (stop); after
1 come the mid-term and final scores (whole numbers 0-10) and the mid-term
weight (0-1, used to the nearest 0.001).  The grade is P when
weight*midterm + (1-weight)*final exceeds 7, and F otherwise.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

## VERSION OUTPUT

```text
dp-bargraph2 (dialectic-playground) 1.0.0
dp-grade (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

Both tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
`dp-grade` always reads a decimal point as `.`, whatever the locale.

## PLATFORM NOTES

- **Windows:** input is read as bytes, so CRLF files and files ending in Ctrl-Z behave as on
  Linux and macOS, and output uses LF line endings. At the console, end the input by typing
  Ctrl+Z and then Enter; on Linux and macOS, type Ctrl+D.
- **All platforms:** grades do not depend on the processor's floating-point unit or on compiler
  settings, because the decision is made in integer arithmetic.
- **Terminals:** prompts appear on standard error, so they stay visible when standard output is
  redirected to a file.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build dp-bargraph2 and dp-grade
make install      # install both into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-bargraph` (project 16); `dp-convert` (project 12), which also adapts an interactive
textbook program; `dp-stats` (project 15); `bc(1)`.
