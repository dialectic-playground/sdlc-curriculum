# dp-koch — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-koch` 1.0.0 |
| Project | `51-koch` — Recursive Fractal Geometry: The Koch Snowflake |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-51), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-koch** — draw the von Koch curve or snowflake as vertex coordinates or SVG

## SYNOPSIS

```text
dp-koch [-s] [-L LENGTH] [--svg] [-p] [FILE]
dp-koch -l LEVEL [-s] [-L LENGTH] [--svg]
dp-koch --help
dp-koch --version
```

## DESCRIPTION

`dp-koch` computes the von Koch curve: a straight segment (level 0) whose middle third is
replaced by the two sides of an equilateral triangle, giving four segments of one third the
length (level 1), and so on, each level replacing every segment again. A curve of level *k* has
4^*k* segments. With `--snowflake`, three curves are drawn on the sides of an equilateral
triangle, with the bumps pointing outward: 3 × 4^*k* segments.

The figure starts at the point (0, 0) and its base runs in the +x direction for *LENGTH* units
(729 by default); the y axis points up, and the bumps of a single curve rise above the x axis.
The snowflake's triangle lies below its first side.

### Two ways to choose the level

With `--level`, `dp-koch` draws one figure and reads no input:

```text
$ dp-koch --level 1
Koch curve, level 1: 4 segments
0.000000 0.000000
243.000000 0.000000
364.500000 210.444173
486.000000 0.000000
729.000000 0.000000
```

Without `--level`, `dp-koch` runs the textbook's dialog on *FILE*, or on standard input when
there is no *FILE* or *FILE* is `-`: it reads a level, draws the figure, and reads an answer —
`y` or `Y` to draw another (it then reads the next level), `n` or `N` to stop. The end of the
input in place of an answer also stops the dialog normally. Entries are separated by any mix of
spaces, tabs, and line breaks, so Windows (CRLF) files read the same as any other, and one or
more Ctrl-Z bytes at the very end of the input are ignored.

With `--prompt`, the dialog asks for each entry on standard error:

```text
$ dp-koch --prompt
Enter level (0-6): 0
Koch curve, level 0: 1 segment
0.000000 0.000000
729.000000 0.000000
Do another (y = yes, n = no)? n
```

The prompts are written to standard error, so `dp-koch --prompt > koch.txt` saves only the
figures. Each figure is written as soon as its level has been entered.

### Output formats

By default each figure is a heading line followed by one line per vertex, in drawing order:
the x and y coordinates, each with exactly six digits after the decimal point, separated by one
space. A coordinate that is zero, or that rounding errors have made a tiny bit negative, is
always written as `0.000000`, never `-0.000000`.

With `--svg`, each figure is written as an SVG document that a web browser can display. Its
`viewBox` encloses the figure with a margin of at least one unit, and the heading becomes the
document's title. Use `--svg` with `--level` to obtain one document per file; in the dialog,
each figure is a separate document.

### Exact and portable numbers

The coordinates are computed with a precisely defined sequence of double-precision
floating-point operations (SRS-51 FR-04), so every conforming implementation prints exactly the
same digits on every operating system. With the default length 729 = 3⁶, every segment of a
level-6 curve has length 1 and all x coordinates are exact.

## OPTIONS

**`-l LEVEL`, `--level=LEVEL`**
: Draw one figure of level *LEVEL* (a whole number from 0 to 6) and exit, without reading any
  input. No *FILE* may be given.

**`-s`, `--snowflake`**
: Draw the closed snowflake (three curves) instead of a single curve.

**`-L LENGTH`, `--length=LENGTH`**
: Make the base segment *LENGTH* units long, a whole number from 1 to 1000000 (default 729).
  For the snowflake, *LENGTH* is the side of the triangle.

**`--svg`**
: Write each figure as an SVG document instead of a list of coordinates.

**`-p`, `--prompt`**
: In the dialog, write `Enter level (0-6): ` before each level is read and
  `Do another (y = yes, n = no)? ` before each answer is read, to standard error. A last prompt
  appears even when the input ends there. Has no effect with `--level`.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-koch` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-l3`, `-l 3`, `--level=3`, and `--level 3`
  are equivalent.
- Short options can be combined: `-sl2` means `-s -l 2`.
- Long options must be spelled out in full; `--snow` is not accepted.
- If an option is given more than once, the last one wins.
- Options and the file name can be given in any order: `dialog.txt -p` works.
- `--` ends option processing, so `dp-koch -- -l` reads a dialog file named `-l`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the figure was drawn, or the dialog ended normally, or help or version was printed |
| 1 | The input could not be read, it contained an invalid entry, or it ended where a level was expected |
| 2 | Usage error: an invalid option or value, or an unexpected file name |

## DIAGNOSTICS

Problems with the dialog input name the input (`-` for standard input) and the line number.
Figures drawn before the problem are kept, and the exit status is 1:

```text
$ printf '1\ny\n7\n' > bad.txt
$ dp-koch bad.txt
Koch curve, level 1: 4 segments
0.000000 0.000000
243.000000 0.000000
364.500000 210.444173
486.000000 0.000000
729.000000 0.000000
dp-koch: bad.txt:3: value out of range '7'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | The level *K* on line *L* is not a whole number | Enter a level from 0 to 6 in digits |
| `S:L: value out of range 'K'` | The level *K* on line *L* is below 0 or above 6 | Enter a level from 0 to 6 |
| `S:L: invalid answer 'K'` | The answer *K* on line *L* is not `y`, `Y`, `n`, or `N` | Answer with a single `y` or `n` |
| `S:L: unexpected end of input` | The input ended where a level was expected (for example, an empty input, or `y` as the last entry) | Supply the level, or answer `n` |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The output could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-koch --level 9
dp-koch: invalid argument '9' for '--level'
Try 'dp-koch --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-l`, `-s`, `-L`, or `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'l'` | `-l` or `-L` given without a value | Supply a value |
| `option '--level' requires an argument` | `--level` or `--length` given without a value | Supply a value |
| `option '--svg' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `invalid argument '9' for '--level'` | Level not a whole number from 0 to 6 | Use 0 … 6 |
| `invalid argument '0' for '--length'` | Length not a whole number from 1 to 1000000 | Use 1 … 1000000 |
| `extra operand 'F'` | A file was named together with `--level`, or more than one file was named | Drop `--level` to run a dialog, or name one file |

## EXAMPLES

Draw the level-1 snowflake (a six-pointed star):

```text
$ dp-koch -s -l 1
Koch snowflake, level 1: 12 segments
0.000000 0.000000
243.000000 0.000000
364.500000 210.444173
486.000000 0.000000
729.000000 0.000000
607.500000 -210.444173
729.000000 -420.888346
486.000000 -420.888346
364.500000 -631.332519
243.000000 -420.888346
0.000000 -420.888346
121.500000 -210.444173
0.000000 0.000000
```

Write a picture of the level-4 snowflake and open it in a browser:

```sh
dp-koch --svg --snowflake --level 4 > snowflake.svg
```

The SVG document for the level-0 snowflake with side 1:

```text
$ dp-koch -s -l 0 -L 1 --svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 3 3">
<title>Koch snowflake, level 0: 3 segments</title>
<polyline fill="none" stroke="black" stroke-width="1" vector-effect="non-scaling-stroke" points="
0.000000,0.000000
1.000000,0.000000
0.500000,0.866025
0.000000,0.000000
"/>
</svg>
```

Run a dialog from a file:

```text
$ printf '0\ny\n2\nn\n' | dp-koch | head -5
Koch curve, level 0: 1 segment
0.000000 0.000000
729.000000 0.000000
Koch curve, level 2: 16 segments
0.000000 0.000000
```

Count the segments of each level in a script:

```sh
for k in 0 1 2 3 4 5 6; do
    dp-koch -l "$k" | head -1
done
```

## HELP OUTPUT

`dp-koch --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-koch [OPTION]... [FILE]
Draw the von Koch curve or snowflake as a list of vertex coordinates.

Reads a dialog from FILE (standard input with no FILE, or when FILE is -):
a level from 0 to 6, then, after each figure, an answer y or n to the
question whether to draw another.  With --level, draws one figure and
reads no input.  The curve starts at (0, 0) and runs in the +x direction.

Options:
  -l, --level=LEVEL    draw one figure of level LEVEL (0-6) and read no input
  -s, --snowflake      draw the closed snowflake (three curves), not one curve
  -L, --length=LENGTH  length of the base segment (1-1000000, default 729)
      --svg            write each figure as an SVG document
  -p, --prompt         write prompts to standard error before each read
      --help           display this help and exit
      --version        output version information and exit
```

## VERSION OUTPUT

```text
dp-koch (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-koch` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Dialog files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored. Output uses LF line endings, not CRLF; when you redirect SVG output to a file in
  PowerShell 5.1, use `cmd /c "dp-koch --svg -l 3 > koch.svg"` or `Out-File -Encoding ascii`,
  because PowerShell's `>` re-encodes the output as UTF-16.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line.
- **All platforms:** the coordinates are identical everywhere; implementations built with
  "fast math" compiler options, or on hardware that uses 80-bit intermediates, would not be
  conforming.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-tromino` (project 24), another four-way recursive decomposition; `dp-tower` (project 23),
recursion and its growth; `dp-ship` (project 52); `gnuplot(1)` for plotting the coordinate list.
