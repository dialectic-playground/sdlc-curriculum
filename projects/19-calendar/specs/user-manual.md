<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-calendar — User Manual](#dp-calendar--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Trying again after a wrong day code](#trying-again-after-a-wrong-day-code)
    - [Working interactively](#working-interactively)
    - [Calendar of a given year](#calendar-of-a-given-year)
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

# dp-calendar — User Manual

| Field         | Value                                               |
| :------------ | :-------------------------------------------------- |
| Product       | `dp-calendar` 1.0.0                                 |
| Project       | `19-calendar` — Formatted Annual Calendar Generator |
| Applies to    | Linux, macOS, Windows                               |
| Specification | `SRS.md` (SRS-19), `shared/CLI-CONVENTIONS.md`      |

---

## NAME

**dp-calendar** — print a calendar of the twelve months of a year

## SYNOPSIS

```text
dp-calendar [-p | --prompt] [FILE]
dp-calendar [-p | --prompt] (-y YEAR | --year=YEAR)
dp-calendar --help
dp-calendar --version
```

## DESCRIPTION

`dp-calendar` reads two codes from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`, and prints a calendar of the twelve months of the year they describe:

- the **day code**, the weekday of January 1: `0` Sunday, `1` Monday, `2` Tuesday,
  `3` Wednesday, `4` Thursday, `5` Friday, `6` Saturday;
- the **leap year code**: `1` for a leap year (February has 29 days), `0` for a common year.

The two codes are whole numbers separated by spaces, tabs, or line breaks. Each month is
printed as its name, a blank line, a header of weekday names, and one line per week, with each
day under its weekday; one blank line separates consecutive months:

```text
$ echo 2 0 | dp-calendar
January

Sun  Mon  Tue  Wed  Thu  Fri  Sat
            1    2    3    4    5
  6    7    8    9   10   11   12
 13   14   15   16   17   18   19
 20   21   22   23   24   25   26
 27   28   29   30   31

February

Sun  Mon  Tue  Wed  Thu  Fri  Sat
                      1    2    3
...
```

Every day number is right-aligned under the last letter of its weekday's name. Lines never end
with spaces, and a month that ends on a Saturday is followed directly by the blank line before
the next month.

### Trying again after a wrong day code

If the day code is not between 0 and 6, `dp-calendar` reports it (`invalid day code '9'`),
discards the pair, and reads the next two codes, just as the original textbook program asked
again. When the next pair is valid, the calendar is printed and the exit status is 0. The same
happens when the codes come from a file: a file holding `9 0` on its first line and `2 0` on its
second prints the calendar for `2 0`.

Every other mistake ends the run with status 1 and nothing on standard output: an entry that is
not a whole number (`zero`, `2.5`), a leap year code other than 0 or 1, or an input that ends
before a valid pair. Anything after the first valid pair is ignored.

One or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data
files) are ignored, and files with Windows (CRLF) line endings read like any other.

### Working interactively

With `--prompt`, `dp-calendar` asks for the codes before each pair it reads:

```text
$ dp-calendar --prompt
Enter day and leap year codes: 9 0
dp-calendar: -:1: invalid day code '9'
Enter day and leap year codes: 2 0
January

Sun  Mon  Tue  Wed  Thu  Fri  Sat
            1    2    3    4    5
...
```

The prompts and messages are written to standard error, so `dp-calendar --prompt > cal.txt`
saves only the calendar.

### Calendar of a given year

`--year=YEAR` works out both codes for a year of the Gregorian calendar between 1 and 9999 and
prints the same calendar as the codes would; nothing is read. For example, 2024 began on a
Monday and is a leap year, so `dp-calendar --year 2024` prints exactly what `echo 1 1 |
dp-calendar` prints. The calendar does not show the year. Years before the Gregorian reform of
1582 are computed as if the Gregorian calendar had always been in use.

## OPTIONS

**`-p`, `--prompt`**
: Before each pair of codes is read, write `Enter day and leap year codes:o standard error.
A last prompt appears before the end of the input is noticed. It has no effect with `--year`.

**`-y` _YEAR_, `--year=`_YEAR_**
: Print the calendar of the Gregorian year _YEAR_ instead of reading codes. _YEAR_ is written
in digits only (no sign) and lies between 1 and 9999. No _FILE_ may be given.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-calendar` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value may be attached or separate: `-y2024`, `-y 2024`, `--year=2024`, and
  `--year 2024` are the same. If `--year` is given twice, the last value counts.
- Long options must be spelled out in full; `--yea` is not accepted.
- Options and the file name can be given in any order: `dp-calendar codes.txt -p` works.
- `--` ends option processing, so `dp-calendar -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                     |
| :----- | :---------------------------------------------------------------------------------------------------------- |
| 0      | Success: the calendar was printed (also after wrong day codes were skipped), or help or version was printed |
| 1      | The input could not be read, or it ended or contained an invalid entry before a valid pair of codes         |
| 2      | Usage error: an invalid option, an invalid year, or too many operands                                       |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number:

```text
$ dp-calendar bad.txt
dp-calendar: bad.txt:2: invalid integer 'zero'
```

| Message                        | Cause                                                                                                                                    | Fix                                          |
| :----------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------- |
| `S:L: invalid day code 'K'`    | The day code _K_ on line _L_ is not between 0 and 6. The pair is skipped and the next one is read; this alone does not make the run fail | Enter a day code from 0 to 6                 |
| `S:L: unexpected end of input` | The input ends before a valid pair of codes; _L_ is the last line                                                                        | Supply both codes                            |
| `S:L: invalid integer 'K'`     | Entry _K_ on line _L_ is not a whole number                                                                                              | Write the codes in digits only               |
| `S:L: value out of range 'K'`  | The leap year code _K_ on line _L_ is neither 0 nor 1                                                                                    | Enter 1 for a leap year, 0 otherwise         |
| `F: No such file or directory` | _F_ does not exist                                                                                                                       | Check the spelling and the current directory |
| `F: Permission denied`         | You may not read _F_                                                                                                                     | Check the file's permissions                 |
| `F: Is a directory`            | _F_ is a directory                                                                                                                       | Name a file instead                          |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                                                                                          | Correct the path                             |
| `F: Input/output error`        | Any other read failure                                                                                                                   | Check the device or file system              |
| `write error`                  | The calendar could not be written (for example, the disk is full)                                                                        | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-calendar --year 0
dp-calendar: invalid argument '0' for '--year'
Try 'dp-calendar --help' for more information.
```

| Message                                       | Cause                                                                    | Fix                                        |
| :-------------------------------------------- | :----------------------------------------------------------------------- | :----------------------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                                                | Use `-p` or `-y`                           |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                                       | Spell the option in full                   |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none                  | Remove the `=…`                            |
| `option requires an argument -- 'y'`          | `-y` (or `--year`) was given without a year                              | Add the year                               |
| `invalid argument 'V' for '--year'`           | The year _V_ is not a number from 1 to 9999 in plain digits              | Use a year from 1 to 9999                  |
| `extra operand 'F'`                           | A file was named together with `--year`, or more than one file was named | Use either codes or `--year`, and one file |

## EXAMPLES

The calendar of a leap year that begins on a Saturday (2000):

```sh
printf '6 1\n' | dp-calendar
dp-calendar --year 2000          # the same bytes
```

Only February of 2024:

```sh
dp-calendar --year 2024 | sed -n '/^February$/,/^$/p'
```

Check that the codes and the year give the same calendar:

```sh
echo 0 1 | dp-calendar > a.txt
dp-calendar --year 2012 > b.txt
cmp a.txt b.txt && echo identical
```

## HELP OUTPUT

`dp-calendar --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-calendar [OPTION]... [FILE]
  or:  dp-calendar [OPTION]... --year=YEAR
Print a calendar of the twelve months of a year.

With no FILE, or when FILE is -, read standard input.  The input holds two
whole numbers: the day code of January 1 (0 = Sunday, 1 = Monday, ...,
6 = Saturday) and the leap year code (1 = leap year, 0 = common year).  A pair
whose day code is not 0 to 6 is reported and skipped, and the next pair is
read.  With --year, the codes are derived from a Gregorian year instead.

Options:
  -p, --prompt      write the prompt 'Enter day and leap year codes: ' to
                      standard error before each pair of codes is read
  -y, --year=YEAR   print the calendar of the Gregorian year YEAR (1 to 9999)
                      instead of reading codes
      --help        display this help and exit
      --version     output version information and exit
```

## VERSION OUTPUT

```text
dp-calendar (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-calendar` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`)
and the time zone (`TZ`). Month and weekday names are always in English, and the tool never
looks at the system clock.

## PLATFORM NOTES

- **Windows:** the calendar ends its lines with LF, not CRLF; programs such as Notepad on
  current Windows versions display it correctly. Use a fixed-width font, because the columns are
  made of spaces. Data files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z
  bytes at the very end of a file are ignored, but a Ctrl-Z byte directly after a code and
  before more input makes the entry invalid. Pressing Ctrl-Z then Enter instead of typing the
  codes ends the input and is reported as `unexpected end of input`.
- **macOS / Linux:** pressing Ctrl-D instead of typing the codes ends the input and is reported
  as `unexpected end of input`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-primes` (project 18), another program from the same chapter of the textbook;
`dp-head` (project 03), to show only the first months; `cal(1)`, `ncal(1)`, `date(1)`.
