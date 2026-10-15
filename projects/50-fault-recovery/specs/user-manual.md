<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-divide — User Manual](#dp-divide--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Faults and recovery](#faults-and-recovery)
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

# dp-divide — User Manual

| Field         | Value                                                                |
| :------------ | :------------------------------------------------------------------- |
| Product       | `dp-divide` 1.0.0                                                    |
| Project       | `50-fault-recovery` — Structured Exception Handling & Fault Recovery |
| Applies to    | Linux, macOS, Windows                                                |
| Specification | `SRS.md` (SRS-50), `shared/CLI-CONVENTIONS.md`                       |

---

## NAME

**dp-divide** — divide pairs of numbers, recovering from an arithmetic fault

## SYNOPSIS

```text
dp-divide [-p | --prompt] [FILE]
dp-divide --help
dp-divide --version
```

## DESCRIPTION

`dp-divide` reads numbers from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`, two at a time. For each pair _a b_ it prints one line with _a_, _b_, and _a_
divided by _b_, each with six digits after the decimal point:

```text
12.000000 / 4.000000 == 3.000000
```

It stops normally, with exit status 0, at the end of the input.

### Faults and recovery

Some pairs cannot be divided:

- the divisor is **zero** — `0`, `0.0`, or `-0` (this includes `0 0`); or
- the quotient is **too large** to represent (its magnitude would exceed about
  1.8 × 10³⁰⁸), for example `-1e308 0.1`.

Such a pair is a _fault_. Instead of printing an infinite or undefined result, `dp-divide`
recovers: it prints these two lines on standard output, ignores the rest of the input, and
exits with status **0**:

```text
Signal status == 8.
At jump point and about to exit...
```

The wording comes from the textbook program, which recovered from the arithmetic-fault signal
(signal number 8) by jumping back to a recovery point. A recovered fault is not an error; it is
how the tool is meant to end when a pair cannot be divided.

A quotient that is merely very _small_ is not a fault: it is printed as `0.000000` (or a few
millionths). Likewise a divisor such as `1e-8` is printed as `0.000000` but is not zero, so it
is divided normally.

### Numbers

Numbers are written in decimal, with an optional `+` or `-` sign, an optional fraction
(`2.5`, `.5`, `5.`), and an optional exponent (`2.5e3`, `1E-7`). They are separated by any mix
of spaces, tabs, and line breaks: the two numbers of a pair may be on one line or on separate
lines, and several pairs may share a line. Files with Windows (CRLF) line endings read the same
as any other. Numbers are stored in IEEE 754 double precision, and the results are printed
exactly from the stored values, the same on every system.

Everything else is an error: digit grouping (`1,5`), hexadecimal, `inf`, `nan`, words, or a
number too large to store (`1e309`). `dp-divide` reports the first such entry with its line
number and stops, with exit status 1; the lines already printed remain valid. If the input ends
after the first number of a pair, that is reported too.

One or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS data
files) are ignored.

### Working interactively

`dp-divide` prints each result as soon as you finish typing a pair (press Enter or Space), so
it can be used at the keyboard. End the input with **Ctrl-D** on Linux and macOS, or
**Ctrl-Z** followed by **Enter** in a Windows console. With `--prompt`, `dp-divide` asks for
each pair, as the textbook program did:

```text
$ dp-divide --prompt
Two floats: 10.0 2.0
10.000000 / 2.000000 == 5.000000
Two floats: 10.0 0.0
Signal status == 8.
At jump point and about to exit...
```

The prompts are written to standard error, so `dp-divide --prompt > results.txt` saves only the
results and the recovery lines.

## OPTIONS

**`-p`, `--prompt`**
: Before each pair is read, write `Two floats:o standard error. A last prompt appears
before the end of the input is noticed; no prompt follows a fault.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-divide` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--pro` is not accepted.
- Options and the file name can be given in any order: `dp-divide pairs.txt -p` works.
- `--` ends option processing, so `dp-divide -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                                      |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Success: every pair was divided (an empty input is fine), or a fault occurred and the tool recovered from it, or help or version was printed |
| 1      | The input could not be read, it contained an invalid number, or its last pair was incomplete                                                 |
| 2      | Usage error: an invalid option or more than one file                                                                                         |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Results
printed before the problem are kept, and the exit status is 1:

```text
$ dp-divide bad.txt
6.000000 / 3.000000 == 2.000000
dp-divide: bad.txt:2: invalid number 'two'
```

| Message                        | Cause                                                                  | Fix                                                                        |
| :----------------------------- | :--------------------------------------------------------------------- | :------------------------------------------------------------------------- |
| `S:L: invalid number 'K'`      | Entry _K_ on line _L_ is not a number, or is too large to store        | Write the number in decimal digits, with an optional fraction and exponent |
| `S:L: unexpected end of input` | The input ended after the first number of a pair; _L_ is the last line | Add the missing divisor or remove the extra number                         |
| `F: No such file or directory` | _F_ does not exist                                                     | Check the spelling and the current directory                               |
| `F: Permission denied`         | You may not read _F_                                                   | Check the file's permissions                                               |
| `F: Is a directory`            | _F_ is a directory                                                     | Name a file instead                                                        |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                        | Correct the path                                                           |
| `F: Input/output error`        | Any other read failure                                                 | Check the device or file system                                            |
| `write error`                  | The results could not be written (for example, the disk is full)       | Free space or redirect the output elsewhere                                |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-divide textbook.txt pairs.txt
dp-divide: extra operand 'pairs.txt'
Try 'dp-divide --help' for more information.
```

| Message                                       | Cause                                                   | Fix                           |
| :-------------------------------------------- | :------------------------------------------------------ | :---------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`                      |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full      |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`               |
| `extra operand 'F'`                           | More than one file was named                            | Run `dp-divide` once per file |

## EXAMPLES

The textbook's dialogue, from a file:

```text
$ dp-divide textbook.txt
10.000000 / 2.000000 == 5.000000
Signal status == 8.
At jump point and about to exit...
```

Several pairs, with signs, fractions, and exponents:

```text
$ printf '12.0 4.0\n1 3\n-7.5 2\n2.5e3 -0.5\n' | dp-divide
12.000000 / 4.000000 == 3.000000
1.000000 / 3.000000 == 0.333333
-7.500000 / 2.000000 == -3.750000
2500.000000 / -0.500000 == -5000.000000
```

An incomplete last pair:

```text
$ dp-divide odd.txt
9.000000 / 3.000000 == 3.000000
dp-divide: odd.txt:5: unexpected end of input
```

Tell a recovered fault from a data error in a script:

```sh
if dp-divide pairs.txt > results.txt; then
    if grep -q '^At jump point' results.txt; then
        echo "stopped at a fault"
    fi
else
    echo "bad input"
fi
```

## HELP OUTPUT

`dp-divide --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-divide [OPTION]... [FILE]
Divide pairs of numbers, recovering from an arithmetic fault.

With no FILE, or when FILE is -, read standard input.  The input is a list of
real numbers separated by whitespace, taken two at a time.  For each pair
a b the line 'a / b == q' is written, with six digits after the decimal
point.  A zero divisor, or a quotient too large to represent, is a fault: the
tool writes 'Signal status == 8.' and 'At jump point and about to exit...',
ignores the rest of the input, and exits with status 0.

Options:
  -p, --prompt    write the prompt 'Two floats: ' to standard error before
                    each pair is read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-divide (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-divide` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and a `.` decimal point, never a comma.

## PLATFORM NOTES

- **All platforms:** a fault is detected by checking the divisor and the quotient, not by a
  hardware trap or signal, so the recovery lines and the exit status are the same everywhere,
  and the `8` in `Signal status == 8.` does not depend on the system's signal numbers.
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

`dp-assert-sort` (project 49), which stops at a violated assertion instead of recovering;
`dp-convert` (project 12) and `dp-stats` (project 15), other tools that read real numbers;
`dp-calc` (project 37); `bc(1)`, `awk(1)`.
