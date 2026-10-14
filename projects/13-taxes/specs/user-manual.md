# dp-taxes — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-taxes` 1.0.0 |
| Project | `13-taxes` — Stream-Based Progressive Income Tax Calculator |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-13), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-taxes** — compute the progressive income tax on a stream of incomes

## SYNOPSIS

```text
dp-taxes [-p | --prompt] [FILE]
dp-taxes --help
dp-taxes --version
```

## DESCRIPTION

`dp-taxes` reads incomes from *FILE*, or from standard input when there is no *FILE* or *FILE*
is `-`, until the end of the input. For each income it prints two lines: the income and the
tax due on it.

```text
Income = 5000 greenbacks
Tax = 1500 greenbacks
```

### The tax rule

- An income **below 6000** greenbacks is taxed at **30%**.
- An income of **6000 or more** is taxed at **60%** of the whole income.

The tax is rounded down to a whole number of greenbacks: 30% of 5999 is 1799.7, so the tax is
1799. The calculation is exact for every income `dp-taxes` accepts, up to
9223372036854775807; it never suffers from floating-point rounding.

### Incomes

Incomes are whole numbers from 0 to 9223372036854775807, written in decimal digits with an
optional `+` or `-` sign; leading zeros are allowed. They are separated by any mix of spaces,
tabs, and line breaks, so several incomes may share a line, and files with Windows (CRLF) line
endings read the same as any other. The income is printed as a plain number: `+4500` is printed
as `4500` and `007` as `7`.

Everything else is an error: a decimal point (`4500.50`), digit grouping (`12,000`), a currency
sign, a negative income, or a number larger than 9223372036854775807. `dp-taxes` reports the
first such entry with its line number and stops; the lines already printed for earlier incomes
remain valid.

One or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data
files) are ignored.

### Working interactively

`dp-taxes` prints each result as soon as you finish typing an income (press Enter or Space), so
it can be used at the keyboard. End the input with **Ctrl-D** on Linux and macOS, or
**Ctrl-Z** followed by **Enter** in a Windows console. With `--prompt`, `dp-taxes` asks for
each income:

```text
$ dp-taxes --prompt
Enter income: 5000
Income = 5000 greenbacks
Tax = 1500 greenbacks
Enter income: 6000
Income = 6000 greenbacks
Tax = 3600 greenbacks
Enter income: ^D
```

The prompts are written to standard error, so `dp-taxes --prompt > taxes.txt` saves only the
results.

## OPTIONS

**`-p`, `--prompt`**
: Before each income is read, write `Enter income: ` to standard error. A last prompt appears
  before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-taxes` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-taxes incomes.txt -p` works.
- `--` ends option processing, so `dp-taxes -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: every income was processed (an empty input is fine), or help or version was printed |
| 1 | The input could not be read, or it contained an invalid income |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Results
printed before the problem are kept, and the exit status is 1:

```text
$ dp-taxes bad.txt
Income = 4500 greenbacks
Tax = 1350 greenbacks
Income = 6000 greenbacks
Tax = 3600 greenbacks
dp-taxes: bad.txt:3: invalid integer '12,000'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | Entry *K* on line *L* is not a whole number, or is larger than 9223372036854775807 | Write the income in digits only, without separators or decimals |
| `S:L: value out of range 'K'` | Entry *K* on line *L* is negative | Enter a non-negative income |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-taxes incomes.txt mixed.txt
dp-taxes: extra operand 'mixed.txt'
Try 'dp-taxes --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-taxes` once per file |

## EXAMPLES

Compute the tax on three incomes:

```text
$ printf '5000\n6000\n10000\n' | dp-taxes
Income = 5000 greenbacks
Tax = 1500 greenbacks
Income = 6000 greenbacks
Tax = 3600 greenbacks
Income = 10000 greenbacks
Tax = 6000 greenbacks
```

Read a file in which incomes share lines and have signs or leading zeros:

```text
$ dp-taxes mixed.txt
Income = 0 greenbacks
Tax = 0 greenbacks
Income = 5999 greenbacks
Tax = 1799 greenbacks
Income = 6000 greenbacks
Tax = 3600 greenbacks
Income = 4500 greenbacks
Tax = 1350 greenbacks
Income = 7 greenbacks
Tax = 2 greenbacks
Income = 12345 greenbacks
Tax = 7407 greenbacks
Income = 1 greenbacks
Tax = 0 greenbacks
```

The largest income is computed exactly:

```text
$ echo 9223372036854775807 | dp-taxes
Income = 9223372036854775807 greenbacks
Tax = 5534023222112865484 greenbacks
```

Use the exit status in a script:

```sh
if dp-taxes incomes.txt > taxes.txt; then
    echo "all incomes processed"
fi
```

## HELP OUTPUT

`dp-taxes --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-taxes [OPTION]... [FILE]
Compute the progressive income tax for each income in FILE.

With no FILE, or when FILE is -, read standard input.  Incomes are whole
numbers from 0 to 9223372036854775807, separated by whitespace, and are read
until the end of the input.  An income below 6000 greenbacks is taxed at 30%,
any other income at 60%; the tax is rounded down to a whole number.

Options:
  -p, --prompt    write the prompt 'Enter income: ' to standard error before
                    each income is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-taxes (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-taxes` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF. In Windows PowerShell 5.1, text piped into a native
  program is re-encoded before `dp-taxes` sees it; for plain ASCII digits this does not change
  the result.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing an income).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-taxes-file` (project 14), which applies the same rule to a file of incomes and writes the
report to a file; `dp-wc` (project 04); `awk(1)`, `bc(1)`.
