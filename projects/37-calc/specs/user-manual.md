# dp-calc — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-calc` 1.0.0 |
| Project | `37-calc` — Interactive Accumulator Calculator |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-37), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-calc** — left-to-right accumulator calculator

## SYNOPSIS

```text
dp-calc [-p | --prompt] [FILE]
dp-calc --help
dp-calc --version
```

## DESCRIPTION

`dp-calc` works like a desk adding machine. It keeps a running total, the *accumulator*, which
starts at 0. It reads lines from *FILE*, or from standard input when there is no *FILE* or
*FILE* is `-`. Each line holds one or more *pairs* of an operator and a whole number, such as
`+ 5 * 10`, and the pairs are applied to the accumulator one after another, from left to
right. For each line, `dp-calc` prints the old total, the line, `==`, and the new total:

```text
0 + 5 * 10 == 50
```

There is no operator precedence: `+ 5 * 10` means "add 5, then multiply by 10", so starting
from 0 the result is 50, not 0 + 50.

### Operators

| Operator | Meaning |
| :-- | :-- |
| `+ n` | add *n* |
| `- n` | subtract *n* |
| `* n` | multiply by *n* |
| `/ n` | divide by *n*, discarding any remainder (the quotient is truncated toward zero) |
| `% n` | replace the total by the remainder of dividing it by *n* (it has the sign of the total) |
| `!` | end the calculation |

Operators and numbers are separated by spaces or tabs: write `+ 5`, not `+5`. Numbers are whole
numbers from −9223372036854775808 to 9223372036854775807, written in decimal digits with an
optional `+` or `-` sign, so `- -5` subtracts minus five. Leading zeros are allowed.

Division and remainder follow one rule for negative numbers: the quotient is rounded toward
zero, and the remainder is what is left over. Starting from 0:

```text
$ printf -- '- 7 / 2\n- 4 %% 2\n+ 8 %% -3\n' | dp-calc
0 - 7 / 2 == -3
-3 - 4 % 2 == -1
-1 + 8 % -3 == 1
```

### Mistakes cost nothing

A line is applied to the total only if *all* of its pairs can be applied. If a line contains
a mistake — an unknown operator, an operator without a number, something that is not a whole
number — or if it divides by zero or produces a result outside the range above, `dp-calc`
reports the first problem with the line number, prints no result, and leaves the total exactly
as it was, even if some pairs of the line had already been worked out. It then reads the next
line. Lines that are empty or contain only spaces are ignored.

### The tape

The printed line repeats the operators and numbers exactly as you typed them, separated by
single spaces; extra spaces and tabs are not reproduced. Every printed line therefore shows one
complete step of the calculation, and the output can be saved as a calculation tape.

### Ending the calculation

Type `!` to end the calculation. `dp-calc` prints

```text
 **** End of Calculation ****
```

(with one leading space) and exits; nothing after the `!` is read. If a line has pairs before
the `!`, such as `* 3 !`, they are applied and their result is printed first. At the end of the
input (Ctrl-D, or the end of a file), the calculation also ends, but without the closing
message.

### Working interactively

`dp-calc` answers each line as soon as you press Enter. With `--prompt`, it shows the current
total, followed by a space, before each line:

```text
$ dp-calc --prompt
0 + 5 * 10
0 + 5 * 10 == 50
50 / 0
dp-calc: -:2: division by zero
50 - 20 / 3
50 - 20 / 3 == 10
10 !
 **** End of Calculation ****
```

The prompts are written to standard error, so `dp-calc --prompt > tape.txt` saves only the
results. A file with Windows (CRLF) line endings reads the same as any other, and one or more
Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS files) are
ignored.

## OPTIONS

**`-p`, `--prompt`**
: Before each line is read, write the current total and a space to standard error. A last
  prompt appears before the end of the input is noticed; none follows `!`.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-calc` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-calc tape.in -p` works.
- `--` ends option processing, so `dp-calc -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the calculation ended at `!` or at the end of the input and every line was accepted (an empty input is fine), or help or version was printed |
| 1 | At least one line was rejected, or the input could not be read |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

A rejected line is reported with the input's name (`-` for standard input) and the line
number. The total is kept, the calculation continues, and the exit status will be 1:

```text
$ dp-calc errors.txt
0 + 10 == 10
dp-calc: errors.txt:2: invalid operator '?'
dp-calc: errors.txt:3: division by zero
dp-calc: errors.txt:4: invalid integer 'x'
dp-calc: errors.txt:5: missing operand after '-'
10 - 3 == 7
 **** End of Calculation ****
```

(Results go to standard output and messages to standard error; a terminal shows them in the
order they occur.)

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid operator 'K'` | *K* stands where an operator is expected, but is not one of `+ - * / % !` (for example `+5` without a space) | Separate the operator from its number |
| `S:L: missing operand after 'O'` | The line ends with the operator *O* | Add the number |
| `S:L: invalid integer 'K'` | *K* is not a whole number, or is outside −9223372036854775808 … 9223372036854775807 | Write the number in digits only |
| `S:L: division by zero` | `/ 0` or `% 0` | Divide by a non-zero number |
| `S:L: integer overflow` | A step of the line gives a result outside −9223372036854775808 … 9223372036854775807 | Use smaller numbers |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-calc session.txt acs.txt
dp-calc: extra operand 'acs.txt'
Try 'dp-calc --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-calc` once per file |

## EXAMPLES

The example of the textbook, from a file:

```text
$ printf '+ 5 * 10\n- 20 / 3\n!\n' > session.txt
$ dp-calc session.txt
0 + 5 * 10 == 50
50 - 20 / 3 == 10
 **** End of Calculation ****
```

Extra spaces, tabs, and blank lines do not matter, and numbers are echoed as typed:

```text
$ printf '  +   007\t*  3\n\n- +21 + 0\n' | dp-calc
0 + 007 * 3 == 21
21 - +21 + 0 == 0
```

The full 64-bit range is available, and leaving it is an error, not a wrap-around:

```text
$ printf '+ 9223372036854775807\n+ 1\n' | dp-calc
0 + 9223372036854775807 == 9223372036854775807
dp-calc: -:2: integer overflow
```

Use the exit status in a script:

```sh
if dp-calc figures.txt > tape.txt; then
    echo "every line accepted"
fi
```

## HELP OUTPUT

`dp-calc --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-calc [OPTION]... [FILE]
Evaluate lines of operator-operand pairs left to right on an accumulator.

With no FILE, or when FILE is -, read standard input.  The accumulator starts
at 0.  Each line holds pairs such as '+ 10 * 3', separated by whitespace; the
operators are + - * / % and the operands are whole numbers.  Each pair is
applied in turn, without precedence, and a valid line prints
'OLD LINE == NEW'.  Division truncates toward zero.  A line with an error is
reported and leaves the accumulator unchanged.  The operator ! ends the
calculation.

Options:
  -p, --prompt    write the accumulator and a space to standard error before
                    each line is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-calc (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-calc` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but
  a Ctrl-Z byte in the middle of a file is data (and makes the token it touches invalid).
  Output uses LF line endings, not CRLF. In batch files, write `%%` for the operator `%`.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line. In `printf`
  format strings, write `%%` for the operator `%`; in interactive `bash`, quote `!` to avoid
  history expansion.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-infix` (project 46), which converts expressions with operator precedence to postfix;
`dp-taxes` (project 13), another line-at-a-time interactive calculation; `bc(1)`, `dc(1)`,
`expr(1)`.
