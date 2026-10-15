<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-cars2 — User Manual](#dp-cars2--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Refused sales](#refused-sales)
    - [Saving and reprinting the day's totals](#saving-and-reprinting-the-days-totals)
    - [Numbers](#numbers)
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

# dp-cars2 — User Manual

| Field         | Value                                                          |
| :------------ | :------------------------------------------------------------- |
| Product       | `dp-cars2` 1.0.0                                               |
| Project       | `28-cars-modular` — Modular Car Sales Architecture & Reporting |
| Applies to    | Linux, macOS, Windows                                          |
| Specification | `SRS.md` (SRS-28), `shared/CLI-CONVENTIONS.md`                 |

---

## NAME

**dp-cars2** — record one day of car sales for 12 brands, print the daily report, and save or
reprint the day's totals

## SYNOPSIS

```text
dp-cars2 [-p | --prompt] [-t | --totals] [-s FILE | --save=FILE] [FILE]
dp-cars2 --help
dp-cars2 --version
```

## DESCRIPTION

`dp-cars2` is the second release of `dp-cars1` (project 26). Without `--totals` and `--save`
it behaves **exactly** like `dp-cars1`: the same input gives the same report, the same messages
(with `dp-cars2` in place of `dp-cars1`), the same prompts, and the same exit status. It reads
whole numbers from _FILE_, or from standard input when there is no _FILE_ or _FILE_ is `-`:

1. **The opening stock**: twelve numbers, the cars of brand 0, 1, …, 11 on the lot at the start
   of the day. Each is between 0 and 999999.
2. **The sales**: pairs of numbers, a brand and the number of cars sold in that sale. Several
   sales of the same brand are added together.
3. **The end of the day**: a negative brand number (for example `-1`), or simply the end of the
   input. Anything after a negative brand is not read.

Then it prints the daily report:

```text
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
    1        8        0        8    0.000000%
    2       20        5       15   25.000000%
    3        4        4        0  100.000000%
    4        0        0        0          n/a
    5       12        0       12    0.000000%
    6        7        2        5   28.571429%
    7       30       10       20   33.333333%
    8        3        1        2   33.333333%
    9       10        0       10    0.000000%
   10       25        1       24    4.000000%
   11        6        0        6    0.000000%
```

For each brand the report shows the stock at the start of the day, the cars sold, the stock
left at the end of the day, and the cars sold as a percentage of the starting stock, with six
decimals; a brand that had no cars at the start of the day shows `n/a`.

### Refused sales

A sale is refused, with a message on standard error, when the brand is 12 or more
(`no such brand`), the number of cars is negative (`negative quantity`), or it would sell more
cars of the brand than are left (`not enough cars in stock for brand B`). `dp-cars2` then goes
on with the next sale; the report shows only accepted sales, and the exit status is 1. A sale
is always two numbers, even after an unknown brand.

### Saving and reprinting the day's totals

The report depends only on the day's **totals**: each brand's opening stock and the number of
cars it sold. `--save FILE` writes them to _FILE_ after the report, one brand per line:

```text
$ dp-cars2 --save monday.tot day.txt > monday.rpt
$ cat monday.tot
15 5
8 0
20 5
4 4
0 0
12 0
7 2
30 10
3 1
10 0
25 1
6 0
```

`--totals` reads such a file instead of the stock and the sales, and prints the same report
again, byte for byte:

```text
$ dp-cars2 --totals monday.tot
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
...
```

A totals input holds exactly 24 numbers: for brand 0, 1, …, 11 in turn, its opening stock
(0 … 999999) and its cars sold (0 up to its opening stock). The layout does not matter — one
brand per line, all on one line, separated by tabs — so totals can also be typed or produced
by another program. A missing number, a 25th entry (`extra data`), or an impossible figure is
reported and no report is printed.

The totals saved are those the report shows: refused sales are not included, and a refused
sale does not prevent saving. If the input is invalid or incomplete, no report is printed and
_FILE_ is left exactly as it was. If _FILE_ cannot be written, the report has already been
printed; `dp-cars2` says why the file could not be written and exits with status 1. _FILE_ may
be the same file as the input.

### Numbers

Numbers are written in decimal digits with an optional `+` or `-` sign; leading zeros are
allowed (`007` is 7, and `-0` is brand 0, not the end of the day). They are separated by any
mix of spaces, tabs, and line breaks. Files with Windows (CRLF) line endings read the same as
any other, and Ctrl-Z bytes at the very end of the input are ignored. Anything else is an
error, reported with its line number; `dp-cars2` then stops without printing a report.

### Working interactively

`dp-cars2` reads each number as soon as you finish typing it and points out a refused sale at
once. With `--prompt` it asks for each number exactly as `dp-cars1` does:
`Cars in stock for brand: B` (and a line break) before each opening stock,
`Which brand was sold? ` before each brand, and `How many cars in sale? ` before each number of
cars. The prompts are written to standard error, so they never appear in a saved report.
`--totals` reads a saved file, not a dialog, so it never prompts, even with `--prompt`.

End the day with a negative brand, or with **Ctrl-D** on Linux and macOS (**Ctrl-Z** followed
by **Enter** in a Windows console).

## OPTIONS

**`-p`, `--prompt`**
: Write a prompt to standard error before each number is read. Ignored with `--totals`.

**`-s FILE`, `--save=FILE`**
: After the report, write the day's totals to _FILE_, replacing its contents. _FILE_ must not
be empty or `-`.

**`-t`, `--totals`**
: Read the day's totals (24 numbers) instead of the opening stock and the sales.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-cars2` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be combined (`-tp`) and take their value attached or separately
  (`-smonday.tot`, `-s monday.tot`); long options take `--save=FILE` or `--save FILE`.
- Long options must be spelled out in full; `--tot` is not accepted.
- Options and the file name can be given in any order. If `--save` is given twice, the last one
  counts.
- `--` ends option processing, so `dp-cars2 -- -t` reads a file named `-t`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                                                                          |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Success: the report was printed, every sale was accepted, and the totals were saved if requested; or help or version was printed                                                 |
| 1      | The report was printed but a sale was refused or the totals file could not be written; or no report was printed because the input could not be read or was invalid or incomplete |
| 2      | Usage error: an invalid option or option value, or more than one file                                                                                                            |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Refused
sales do not stop `dp-cars2`; every other data problem stops it before the report:

```text
$ dp-cars2 --totals oversold.tot
dp-cars2: oversold.tot:4: value out of range '5'
```

| Message                                         | Cause                                                                                                                                  | Fix                                          |
| :---------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------- |
| `S:L: no such brand 'K'`                        | The sale on line _L_ names brand _K_, which is 12 or more (refused)                                                                    | Enter a brand from 0 to 11                   |
| `S:L: negative quantity 'K'`                    | The sale on line _L_ sells _K_ cars, a negative number (refused)                                                                       | Enter the number of cars sold                |
| `S:L: not enough cars in stock for brand B 'K'` | Selling _K_ more cars of brand _B_ would sell more than were on the lot (refused)                                                      | Check the sale and the opening stock         |
| `S:L: invalid integer 'K'`                      | Entry _K_ on line _L_ is not a whole number, or is far too large                                                                       | Write numbers in digits only                 |
| `S:L: value out of range 'K'`                   | An opening stock is negative or more than 999999, or (with `--totals`) a brand's cars sold are negative or more than its opening stock | Correct the figure                           |
| `S:L: unexpected end of input`                  | The input ended where a number was expected                                                                                            | Complete the input                           |
| `S:L: extra data 'K'`                           | With `--totals`, the input holds more than 24 numbers                                                                                  | Remove the extra entries                     |
| `F: No such file or directory`                  | The input _F_, or a directory in the totals file name _F_, does not exist                                                              | Check the spelling and the current directory |
| `F: Permission denied`                          | You may not read the input _F_, or write the totals file _F_                                                                           | Check the permissions                        |
| `F: Is a directory`                             | _F_ is a directory                                                                                                                     | Name a file instead                          |
| `F: Not a directory`                            | Part of the path _F_ is a file, not a directory                                                                                        | Correct the path                             |
| `F: Input/output error`                         | Any other read or write failure                                                                                                        | Check the device or file system              |
| `write error`                                   | The report could not be written (for example, the disk is full)                                                                        | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read, no file is written,
and nothing is written to standard output:

```text
$ dp-cars2 -s '' day.txt
dp-cars2: invalid argument '' for '-s'
Try 'dp-cars2 --help' for more information.
```

| Message                                       | Cause                                                   | Fix                          |
| :-------------------------------------------- | :------------------------------------------------------ | :--------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`, `-s`, or `-t`      |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full     |
| `option requires an argument -- 's'`          | `-s` is the last argument                               | Give the totals file name    |
| `option '--save' requires an argument`        | `--save` is the last argument                           | Give the totals file name    |
| `option '--totals' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`              |
| `invalid argument 'V' for '--save'`           | The totals file name is empty or `-`                    | Name a file                  |
| `extra operand 'F'`                           | More than one input file was named                      | Run `dp-cars2` once per file |

## EXAMPLES

Replace `dp-cars1` in an existing job; nothing else changes:

```sh
dp-cars2 monday.txt > monday.rpt
```

Close the day at the keyboard and keep the totals:

```sh
dp-cars2 --prompt --save "$(date +%F).tot"
```

Reprint a past day's report:

```text
$ dp-cars2 -t 2026-10-12.tot | head -3
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
```

Normalize a hand-written totals file in place (the report goes to the null device):

```sh
dp-cars2 --totals --save typed.tot typed.tot > /dev/null
```

## HELP OUTPUT

`dp-cars2 --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-cars2 [OPTION]... [FILE]
Record one day of car sales for 12 brands and print the daily report.

Read whitespace-separated whole numbers from FILE, or from standard input when
FILE is absent or -: first the opening stock of brands 0 to 11 (0-999999
each), then each sale as a brand and a quantity, until a negative brand or the
end of the input.  A sale of an unknown brand, of a negative quantity, or of
more cars than are left in stock is reported and not recorded.

With --totals, read the day's totals instead: for each brand from 0 to 11, its
opening stock and the number of cars sold, as written by --save.

Options:
  -p, --prompt       write prompts to standard error before reading (ignored
                       with --totals)
  -s, --save=FILE    after the report, write the day's totals to FILE
  -t, --totals       read the day's totals instead of the stock and the sales
      --help         display this help and exit
      --version      output version information and exit
```

## VERSION OUTPUT

```text
dp-cars2 (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-cars2` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` as the decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is an error. The report and the totals file use LF line
  endings, not CRLF, so a totals file saved on Windows reads the same on Linux and macOS, and
  the other way round. Use `NUL` instead of `/dev/null` in the example above.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a number).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-cars1` (project 26), the original single-unit program whose behavior `dp-cars2` reproduces;
`dp-taxes-file` (project 14), which also replaces an output file only after its input has been
checked; `dp-sales` (project 42), a multi-file sales report; `awk(1)`.
