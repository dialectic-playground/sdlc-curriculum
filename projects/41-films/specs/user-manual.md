<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-films — User Manual](#dp-films--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The sample set](#the-sample-set)
    - [Films to classify](#films-to-classify)
    - [How a film is classified](#how-a-film-is-classified)
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

# dp-films — User Manual

| Field         | Value                                                   |
| :------------ | :------------------------------------------------------ |
| Product       | `dp-films` 1.0.0                                        |
| Project       | `41-films` — 1-Nearest Neighbor Film Success Classifier |
| Applies to    | Linux, macOS, Windows                                   |
| Specification | `SRS.md` (SRS-41), `shared/CLI-CONVENTIONS.md`          |

---

## NAME

**dp-films** — classify films as hits or flops by their nearest neighbor in a sample set

## SYNOPSIS

```text
dp-films [-s FILE | --sample=FILE] [-p | --prompt] [FILE]
dp-films --help
dp-films --version
```

## DESCRIPTION

`dp-films` forecasts whether a film will be a hit. It first reads a _sample set_ of films whose
outcome is known, from the file `films.dat` in the current directory (or the file named by
`-s`). Then it reads films to classify from _FILE_, or from standard input when there is no
_FILE_ or _FILE_ is `-`, until the end of the input, and prints one verdict for each:

```text
The film is a HIT!
The film is a flop.
```

### The sample set

Each film in the sample set is three values: the percentage of hits among the earlier films of
its director, the same percentage for the leading members of its cast, and `1` if the film was
a hit or `0` if it was a flop. Values are separated by any mix of spaces, tabs, and line
breaks; one film per line is customary but not required, and blank lines are ignored. The
sample set holds 1 to 100 films.

`dp-films` checks the whole sample set before it classifies anything. A value that is not a
number, a percentage below 0 or above 100, a code other than `0` or `1`, a film with a missing
value at the end, more than 100 films, or no films at all is reported with its line number, and
no film is classified.

### Films to classify

Each film to classify is two percentages: the director's, then the cast's. A percentage is a
decimal number from 0 to 100, with an optional sign, decimal point, and exponent: `75`, `75.0`,
`+75`, `7.5e1`, and `.5` are all valid. Digit grouping (`1,000`), a percent sign, `inf`, and
`nan` are not. Values are separated by any mix of spaces, tabs, and line breaks, so several
films may share a line.

### How a film is classified

The film gets the outcome of the _nearest_ film in the sample set. The distance between the
film (_d_, _c_) and a sample film (_D_, _C_) is measured by the squared Euclidean distance
(_d_ − _D_)² + (_c_ − _C_)². If several sample films are equally near, the one that comes first
in the sample set decides. With the textbook's `films.dat`, the film (50, 65) is at the same
distance, 125, from four sample films; the first of them, (40, 60), was a flop, so the verdict
is `The film is a flop.`.

The distance is computed in standard double-precision binary floating point, in exactly the
same way on every system. Because decimal fractions such as 0.1 are not exact in binary, two
distances that look equal on paper can differ in the last digit, and the nearer one wins.

### Working interactively

`dp-films` prints each verdict as soon as you have typed the second percentage of a film and
pressed Enter or Space. End the input with **Ctrl-D** on Linux and macOS, or **Ctrl-Z**
followed by **Enter** in a Windows console. With `--prompt`, `dp-films` asks for each value:

```text
$ dp-films --prompt
Enter the percentage of hits of the
director of the film to be classified or
generate EOF to terminate the program: 75.0
Enter the percentage of hits of the
leading members of the cast of the film
to be classified: 85.0
The film is a HIT!
Enter the percentage of hits of the
director of the film to be classified or
generate EOF to terminate the program: ^D
```

The prompts are written to standard error, so `dp-films --prompt > verdicts.txt` saves only the
verdicts.

One or more Ctrl-Z bytes at the very end of a file (the end-of-file mark of old MS-DOS data
files) are ignored, in the sample set and in the films to classify.

## OPTIONS

**`-s FILE`, `--sample=FILE`**
: Read the sample set from _FILE_ instead of `films.dat`. `-` means standard input; the films
to classify must then come from a _FILE_ operand, because standard input can be read only
once.

**`-p`, `--prompt`**
: Before each percentage is read, write a prompt to standard error. A last prompt appears
before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-films` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-sstudio.dat`, `-s studio.dat`,
  `--sample=studio.dat`, and `--sample studio.dat` are equivalent.
- Long options must be spelled out in full; `--samp` is not accepted.
- If `-s` is given more than once, the last one wins.
- Options and the file name can be given in any order: `dp-films queries.txt -p` works.
- `--` ends option processing, so `dp-films -- -p` reads films to classify from a file named
  `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                             |
| :----- | :-------------------------------------------------------------------------------------------------- |
| 0      | Success: every film was classified (no films at all is fine), or help or version was printed        |
| 1      | A file could not be read, the sample set is invalid, or a film to classify is invalid or incomplete |
| 2      | Usage error: an invalid option or option value, or more than one file                               |

## DIAGNOSTICS

Problems with the data name the file (`-` for standard input) and the line number. A problem in
the sample set stops the tool before anything is classified. A problem in the films to classify
stops it there; verdicts printed before the problem remain valid:

```text
$ dp-films bad-query.txt
The film is a HIT!
The film is a flop.
dp-films: bad-query.txt:3: invalid number 'seventy'
```

| Message                           | Cause                                                                    | Fix                                          |
| :-------------------------------- | :----------------------------------------------------------------------- | :------------------------------------------- |
| `S:L: too many films (limit 100)` | The sample set _S_ has more than 100 films; the 101st starts on line _L_ | Remove films                                 |
| `S:L: no films in the sample set` | The sample set is empty                                                  | Name the right file                          |
| `F:L: invalid number 'K'`         | A percentage _K_ is not a number                                         | Write it in plain decimal                    |
| `F:L: value out of range 'K'`     | A percentage is below 0 or above 100, or a code is not `0` or `1`        | Correct the value                            |
| `S:L: invalid integer 'K'`        | A code _K_ is not a whole number (for example `1.0`)                     | Write `0` or `1`                             |
| `F:L: unexpected end of input`    | The input ends in the middle of a film                                   | Add the missing value                        |
| `F: No such file or directory`    | _F_ does not exist                                                       | Check the spelling and the current directory |
| `F: Permission denied`            | You may not read _F_                                                     | Check the file's permissions                 |
| `F: Is a directory`               | _F_ is a directory                                                       | Name a file instead                          |
| `F: Not a directory`              | Part of the path _F_ is a file, not a directory                          | Correct the path                             |
| `F: Input/output error`           | Any other read failure                                                   | Check the device or file system              |
| `write error`                     | The verdicts could not be written (for example, the disk is full)        | Free space or redirect the output elsewhere  |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-films -s -
dp-films: invalid argument '-' for '-s'
Try 'dp-films --help' for more information.
```

| Message                                       | Cause                                                                        | Fix                          |
| :-------------------------------------------- | :--------------------------------------------------------------------------- | :--------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                                                    | Use `-s` or `-p`             |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                                           | Spell the option in full     |
| `option requires an argument -- 's'`          | `-s` given without a file name                                               | Supply a file name           |
| `option '--sample' requires an argument`      | `--sample` given without a file name                                         | Supply a file name           |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none                      | Remove the `=…`              |
| `invalid argument '' for '-s'`                | An empty file name                                                           | Give a file name             |
| `invalid argument '-' for '-s'`               | Both the sample set and the films to classify would come from standard input | Name a file for one of them  |
| `extra operand 'F'`                           | More than one file of films to classify was named                            | Run `dp-films` once per file |

## EXAMPLES

Classify the films of the textbook's example with the textbook's sample set:

```text
$ printf '75.0 85.0\n10.0 15.0\n90.0 70.0\n' | dp-films
The film is a HIT!
The film is a flop.
The film is a HIT!
```

Use another sample set and a file of films; the sample set below has a hit and a flop at the
same distance from (50, 50), and the first one decides:

```text
$ cat pair.dat
40 60 1
60 40 0
$ dp-films -s pair.dat center.txt
The film is a HIT!
The film is a HIT!
The film is a flop.
```

Read the sample set from a pipe and the films from a file:

```sh
gunzip -c films.dat.gz | dp-films -s - upcoming.txt > verdicts.txt
```

## HELP OUTPUT

`dp-films --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-films [OPTION]... [FILE]
Classify films as hits or flops by their nearest neighbor in a sample set.

The sample set (default films.dat) holds 1 to 100 films.  Each film is three
values: the percentage of hits of its director, the percentage of hits of the
leading members of its cast (each 0 to 100), and 1 for a hit or 0 for a flop.

Each film to classify is two percentages, director then cast, read from FILE,
or from standard input when there is no FILE or FILE is -, until the end of
the input.  It is a hit if the nearest film in the sample set is a hit; of
several equally near films, the first in the sample set decides.

Options:
  -s, --sample=FILE   read the sample set from FILE (default films.dat);
                        - means standard input
  -p, --prompt        write a prompt to standard error before each
                        percentage is read
      --help          display this help and exit
      --version       output version information and exit
```

## VERSION OUTPUT

```text
dp-films (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-films` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read with a `.` decimal point and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is part of a value and makes it invalid. Output uses LF
  line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a value).
- **All systems:** verdicts are identical everywhere, including for films that are equally near
  to two sample films; the distance is computed in the same binary floating-point arithmetic
  on every processor.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-stats` (project 15), which summarizes a stream of numbers; `dp-phone` (project 31), which
looks records up in a data file; `dp-sales` (project 42), the other data-modeling project of
the same chapter; `sort(1)`, `awk(1)`.
