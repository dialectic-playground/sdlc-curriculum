<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-sales — User Manual](#dp-sales--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The accounts file](#the-accounts-file)
    - [The salesperson file](#the-salesperson-file)
    - [Fields](#fields)
    - [The report](#the-report)
    - [All or nothing](#all-or-nothing)
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

# dp-sales — User Manual

| Field         | Value                                                                        |
| :------------ | :--------------------------------------------------------------------------- |
| Product       | `dp-sales` 1.0.0                                                             |
| Project       | `42-sales-report` — Enterprise Sales Reporting & Relational Data Integration |
| Applies to    | Linux, macOS, Windows                                                        |
| Specification | `SRS.md` (SRS-42), `shared/CLI-CONVENTIONS.md`                               |

---

## NAME

**dp-sales** — print the sales report by salesperson from an accounts file and a salesperson file

## SYNOPSIS

```text
dp-sales [-a FILE | --accounts=FILE] [-s FILE | --salespeople=FILE]
dp-sales --help
dp-sales --version
```

## DESCRIPTION

`dp-sales` reads customer accounts from the file `sales.dat` and salespeople from the file
`sper.dat`, both in the current directory, and prints the sales report to standard output. Use
`-a` and `-s` to read other files; the name `-` means standard input (for one of the two files
only).

### The accounts file

Each line describes one account: its id, its name, its actual sales, and its projected sales.

```text
127 AceRecords 2762890.50 6780000.00
```

### The salesperson file

Each line describes one salesperson: name, sales coach, region, base salary, and bonus, then a
`#`, then the ids of the accounts the salesperson manages, in the order they should be listed
(possibly none).

```text
Johnsonbaugh Epp IL 98450.00 29324.18 # 127 812
```

### Fields

Fields are separated by spaces or tabs; blank lines are ignored, and files with Windows (CRLF)
line endings read the same as any other. One or more Ctrl-Z bytes at the very end of a file
(the end-of-file mark of old MS-DOS data files) are ignored. Names, coaches, and regions are
single words, printed exactly as written.

- **Ids** are whole numbers from 0 to 9223372036854775807. Leading zeros are allowed and do not
  matter: `0127` is the account 127.
- **Amounts** are written with digits and at most two decimals: `95679.10`, `95679.1`, and
  `95679` are valid; `+5`, `-5`, `5.`, `.5`, `1,000.00`, and `1432567.888` are not. The largest
  amount is 92233720368547758.07. Amounts are always printed exactly, with two decimals.

### The report

The salespeople are listed in order of name, comparing names byte by byte, so upper-case
letters come before lower-case ones (`Zimmer` before `deGroot`), whatever your locale.
Salespeople with the same name keep the order of the file. Each salesperson is followed by the
accounts listed for them, in the order listed. An account may be listed for several
salespeople; an account that is listed for nobody does not appear.

With the files of the textbook's example, the report begins:

```text
Sales report by salesperson:

        Salesperson:  Chessare
        Sales coach:  Cruz
        Sales region: TX
        Base salary and bonus:  102300.00  15671.90
        2 Account(s):

                Name:       PetRocks
                Id:         245
                Projected:  8130000.00
                Actual:     95679.10

```

The account lines are indented by 16 spaces, the salesperson lines by 8; the line
`2 Account(s): ` ends with a space, and every account, and every salesperson's heading, is
followed by an empty line.

### All or nothing

`dp-sales` checks both files completely before it prints anything. If a file cannot be read,
or a line has a missing, extra, or malformed field, an id that appears twice in the accounts
file, or a salesperson lists an account that does not exist, `dp-sales` reports the first
problem with its file and line number and prints no report at all.

## OPTIONS

**`-a FILE`, `--accounts=FILE`**
: Read the accounts from _FILE_ instead of `sales.dat`. `-` means standard input.

**`-s FILE`, `--salespeople=FILE`**
: Read the salespeople from _FILE_ instead of `sper.dat`. `-` means standard input.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-sales` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-ateam.dat`, `-a team.dat`,
  `--accounts=team.dat`, and `--accounts team.dat` are equivalent.
- Long options must be spelled out in full; `--acc` is not accepted.
- If an option is given more than once, the last one wins.
- `dp-sales` takes no operands: name the files with `-a` and `-s`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                      |
| :----- | :--------------------------------------------------------------------------- |
| 0      | Success: the report, help, or version was printed                            |
| 1      | A file could not be read, or contains an invalid line; no report was printed |
| 2      | Usage error: an invalid option or option value, or an operand                |

## DIAGNOSTICS

Problems with the data name the file (`-` for standard input) and the line number, and no report
is printed:

```text
$ dp-sales -s unknown.dat
dp-sales: unknown.dat:2: unknown account '999'
```

| Message                                 | Cause                                                                   | Fix                                              |
| :-------------------------------------- | :---------------------------------------------------------------------- | :----------------------------------------------- |
| `F:L: incomplete record`                | Line _L_ lacks a field                                                  | Complete the line                                |
| `F:L: unexpected field 'K'`             | An account line has more than four fields (perhaps a name with a space) | Remove the field, or join the name into one word |
| `F:L: invalid integer 'K'`              | An id _K_ is not a whole number                                         | Write the id in digits                           |
| `F:L: value out of range 'K'`           | An id is negative, or an amount is larger than 92233720368547758.07     | Correct the value                                |
| `F:L: invalid amount 'K'`               | An amount is not digits with at most two decimals                       | Write it like `1234.50`                          |
| `F:L: duplicate account id 'K'`         | Two accounts have the same id                                           | Give each account its own id                     |
| `F:L: expected '#' but found 'K'`       | The sixth field of a salesperson line is not `#`                        | Insert the `#` before the account ids            |
| `F:L: unknown account 'K'`              | A salesperson lists an id that no account has                           | Add the account, or correct the id               |
| `F:L: account listed twice 'K'`         | A salesperson lists the same account twice                              | Remove the repetition                            |
| `F:L: too many accounts (limit 100)`    | The accounts file has more than 100 accounts                            | Split the data                                   |
| `F:L: too many salespeople (limit 100)` | The salesperson file has more than 100 salespeople                      | Split the data                                   |
| `F: No such file or directory`          | _F_ does not exist                                                      | Check the spelling and the current directory     |
| `F: Permission denied`                  | You may not read _F_                                                    | Check the file's permissions                     |
| `F: Is a directory`                     | _F_ is a directory                                                      | Name a file instead                              |
| `F: Not a directory`                    | Part of the path _F_ is a file, not a directory                         | Correct the path                                 |
| `F: Input/output error`                 | Any other read failure                                                  | Check the device or file system                  |
| `write error`                           | The report could not be written (for example, the disk is full)         | Free space or redirect the output elsewhere      |

The accounts file is read and checked first; the salesperson file is read only if the accounts
file is valid.

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-sales sales.dat
dp-sales: extra operand 'sales.dat'
Try 'dp-sales --help' for more information.
```

| Message                                     | Cause                                                     | Fix                         |
| :------------------------------------------ | :-------------------------------------------------------- | :-------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                                 | Use `-a` or `-s`            |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                        | Spell the option in full    |
| `option requires an argument -- 'a'`        | `-a` or `-s` given without a file name                    | Supply a file name          |
| `option '--accounts' requires an argument`  | `--accounts` or `--salespeople` given without a file name | Supply a file name          |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…`                               | Remove the `=…`             |
| `invalid argument '' for '-a'`              | An empty file name                                        | Give a file name            |
| `invalid argument '-' for '-s'`             | Both files would be read from standard input              | Name a file for one of them |
| `extra operand 'F'`                         | A file was named without `-a` or `-s`                     | Use `-a F` or `-s F`        |

## EXAMPLES

Print the report from `sales.dat` and `sper.dat` and compare it with the textbook's sample:

```sh
dp-sales > sales.out && cmp sales.out sales.rpt && echo identical
```

Use another salesperson file with the same accounts:

```sh
dp-sales -s team.dat > team.rpt
```

Take the accounts from another program:

```sh
extract-accounts | dp-sales -a - -s sper.dat
```

A salesperson who manages no accounts:

```text
        Salesperson:  Kalin
        Sales coach:  Epp
        Sales region: IL
        Base salary and bonus:  75000.00  0.00
        0 Account(s):

```

## HELP OUTPUT

`dp-sales --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-sales [OPTION]...
Print the sales report by salesperson from an accounts file and a
salesperson file.

Each line of the accounts file (default sales.dat) describes one account:
  ID NAME ACTUAL PROJECTED
Each line of the salesperson file (default sper.dat) describes one
salesperson and lists the ids of the accounts the salesperson manages:
  NAME COACH REGION SALARY BONUS # ID...
Ids are whole numbers; amounts have at most two decimals.  Salespeople are
listed in order of name, each with the accounts in the order listed.  Both
files are checked completely before the report is written.

Options:
  -a, --accounts=FILE      read the accounts from FILE (default sales.dat);
                             - means standard input
  -s, --salespeople=FILE   read the salespeople from FILE (default sper.dat);
                             - means standard input
      --help               display this help and exit
      --version            output version information and exit
```

## VERSION OUTPUT

```text
dp-sales (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-sales` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Names are ordered byte by byte, and numbers are read and written with a `.` decimal point and no
digit grouping, whatever the locale.

## PLATFORM NOTES

- **Windows:** files are read as raw bytes: CRLF line endings are accepted, and Ctrl-Z bytes at
  the very end of a file are ignored, but a Ctrl-Z byte in the middle of a file is part of a
  field. The report uses LF line endings, not CRLF; some editors may also strip the trailing
  space of the `Account(s): ` lines when you save a report, so compare reports with `fc /b` or
  `cmp`, not after editing.
- **macOS / Linux:** `cat -A` shows the trailing spaces and line endings of a report.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-phone` (project 31), which sorts records and finds them by binary search; `dp-cars2`
(project 28), another sales report; `dp-films` (project 41), the other data-modeling project of
the same chapter; `join(1)`, `sort(1)`, `awk(1)`.
