<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-cars1 — User Manual](#dp-cars1--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Refused sales](#refused-sales)
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

# dp-cars1 — User Manual

| Field         | Value                                                      |
| :------------ | :--------------------------------------------------------- |
| Product       | `dp-cars1` 1.0.0                                           |
| Project       | `26-cars` — Car Dealership Daily Sales & Inventory Tracker |
| Applies to    | Linux, macOS, Windows                                      |
| Specification | `SRS.md` (SRS-26), `shared/CLI-CONVENTIONS.md`             |

---

## NAME

**dp-cars1** — record one day of car sales for 12 brands and print the daily report

## SYNOPSIS

```text
dp-cars1 [-p | --prompt] [FILE]
dp-cars1 --help
dp-cars1 --version
```

## DESCRIPTION

`dp-cars1` keeps one day's books for a dealership that sells twelve brands of car, numbered 0
to 11. It reads whole numbers from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`:

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
left at the end of the day (_Start_ − _Sales_), and the cars sold as a percentage of the
starting stock, with six decimals. A brand that had no cars at the start of the day shows
`n/a`, because no percentage of nothing can be sold.

### Refused sales

`dp-cars1` never records a sale that cannot have happened. A sale is refused, with a message
on standard error, when

- the brand is 12 or more (`no such brand`);
- the number of cars is negative (`negative quantity`);
- it would sell more cars of the brand than are left on the lot
  (`not enough cars in stock for brand B`).

After a refused sale, `dp-cars1` simply goes on with the next sale; the report shows only the
sales that were accepted. If any sale was refused, the exit status is 1, so a script can tell.
A sale is always two numbers: even after an unknown brand the number of cars is read, so the
rest of the input stays in step.

### Numbers

Numbers are written in decimal digits with an optional `+` or `-` sign; leading zeros are
allowed (`007` is 7, and `-0` is brand 0, not the end of the day). They are separated by any
mix of spaces, tabs, and line breaks, so the opening stock may share one line, and the two
numbers of a sale may even be on different lines. Files with Windows (CRLF) line endings read
the same as any other, and one or more Ctrl-Z bytes at the very end of the input (the
end-of-file mark of old MS-DOS data files) are ignored.

Anything else — a letter, a decimal point, digit grouping — is an error. So is an opening stock
outside 0 … 999999, and an input that ends in the middle of the opening stock or between a
brand and its number of cars. `dp-cars1` reports the problem with its line number and stops
**without** printing a report, because the day's figures would be incomplete.

### Working interactively

`dp-cars1` reads each number as soon as you finish typing it (press Enter or Space), and points
out a refused sale at once. With `--prompt` it tells you what to type:

```text
$ dp-cars1 --prompt
Cars in stock for brand: 0
15
Cars in stock for brand: 1
8
...
Cars in stock for brand: 11
6
Which brand was sold? 12
How many cars in sale? 1
dp-cars1: -:13: no such brand '12'
Which brand was sold? 0
How many cars in sale? 3
Which brand was sold? -1
DAILY REPORT
...
```

End the day with a negative brand, or with **Ctrl-D** on Linux and macOS (**Ctrl-Z** followed
by **Enter** in a Windows console). The prompts are written to standard error, so
`dp-cars1 --prompt > today.rpt` saves only the report.

## OPTIONS

**`-p`, `--prompt`**
: Write a prompt to standard error before each number is read: `Cars in stock for brand: B`
and a line break before each opening stock, `Which brand was sold? ` before each brand, and
`How many cars in sale? ` before each number of cars.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-cars1` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-cars1 day.txt -p` works.
- `--` ends option processing, so `dp-cars1 -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                                                                 |
| :----- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Success: the report was printed and every sale was accepted, or help or version was printed                                                                             |
| 1      | The report was printed but at least one sale was refused; or no report was printed because the input could not be read, contained an invalid number, or ended too early |
| 2      | Usage error: an invalid option or more than one file                                                                                                                    |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. A refused
sale does not stop `dp-cars1`:

```text
$ dp-cars1 rejected.txt
dp-cars1: rejected.txt:3: no such brand '12'
dp-cars1: rejected.txt:4: negative quantity '-2'
dp-cars1: rejected.txt:6: not enough cars in stock for brand 3 '2'
dp-cars1: rejected.txt:7: not enough cars in stock for brand 4 '1'
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        0       15    0.000000%
    1        8        8        0  100.000000%
...
```

(The messages are on standard error and the report on standard output; the exit status is 1.)
Every other problem stops `dp-cars1` before the report:

```text
$ dp-cars1 cut.txt
dp-cars1: cut.txt:4: unexpected end of input
```

| Message                                         | Cause                                                                                 | Fix                                          |
| :---------------------------------------------- | :------------------------------------------------------------------------------------ | :------------------------------------------- |
| `S:L: no such brand 'K'`                        | The sale on line _L_ names brand _K_, which is 12 or more (refused)                   | Enter a brand from 0 to 11                   |
| `S:L: negative quantity 'K'`                    | The sale on line _L_ sells _K_ cars, a negative number (refused)                      | Enter the number of cars sold                |
| `S:L: not enough cars in stock for brand B 'K'` | Selling _K_ more cars of brand _B_ would sell more than were on the lot (refused)     | Check the sale and the opening stock         |
| `S:L: invalid integer 'K'`                      | Entry _K_ on line _L_ is not a whole number, or is far too large                      | Write numbers in digits only                 |
| `S:L: value out of range 'K'`                   | The opening stock _K_ on line _L_ is negative or more than 999999                     | Enter a count from 0 to 999999               |
| `S:L: unexpected end of input`                  | The input ended during the opening stock, or after a brand without its number of cars | Complete the input                           |
| `F: No such file or directory`                  | _F_ does not exist                                                                    | Check the spelling and the current directory |
| `F: Permission denied`                          | You may not read _F_                                                                  | Check the file's permissions                 |
| `F: Is a directory`                             | _F_ is a directory                                                                    | Name a file instead                          |
| `F: Not a directory`                            | Part of the path _F_ is a file, not a directory                                       | Correct the path                             |
| `F: Input/output error`                         | Any other read failure                                                                | Check the device or file system              |
| `write error`                                   | The report could not be written (for example, the disk is full)                       | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-cars1 day.txt rejected.txt
dp-cars1: extra operand 'rejected.txt'
Try 'dp-cars1 --help' for more information.
```

| Message                                       | Cause                                                   | Fix                          |
| :-------------------------------------------- | :------------------------------------------------------ | :--------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`                     |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full     |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`              |
| `extra operand 'F'`                           | More than one file was named                            | Run `dp-cars1` once per file |

## EXAMPLES

A day's entries in a file, closed by `-1`:

```text
$ cat day.txt
15 8 20 4 0 12 7 30 3 10 25 6
0 3
2 5
3 4
7 10
0 2
10 1
6 2
8 1
-1
Anything after the sentinel is never read.
$ dp-cars1 day.txt > today.rpt
$ head -3 today.rpt
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
```

Use the exit status to find out whether any sale was refused:

```sh
if dp-cars1 monday.txt > monday.rpt; then
    echo "all sales recorded"
else
    echo "check the messages above" >&2
fi
```

## HELP OUTPUT

`dp-cars1 --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-cars1 [OPTION]... [FILE]
Record one day of car sales for 12 brands and print the daily report.

Read whitespace-separated whole numbers from FILE, or from standard input when
FILE is absent or -: first the opening stock of brands 0 to 11 (0-999999
each), then each sale as a brand and a quantity, until a negative brand or the
end of the input.  A sale of an unknown brand, of a negative quantity, or of
more cars than are left in stock is reported and not recorded.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

## VERSION OUTPUT

```text
dp-cars1 (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-cars1` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits, a `.` as the decimal point, and no digit
grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF.
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

`dp-cars2` (project 28), the same program with the report as a separate component, which can
also save the day's totals and print the report from saved totals; `dp-stats` (project 15) and
`dp-sales` (project 42), other report-producing tools of the curriculum; `awk(1)`.
