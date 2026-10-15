<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-perc — User Manual](#dp-perc--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [A simulation](#a-simulation)
    - [Responses](#responses)
    - [Reproducible randomness](#reproducible-randomness)
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

# dp-perc — User Manual

| Field         | Value                                                             |
| :------------ | :---------------------------------------------------------------- |
| Product       | `dp-perc` 1.0.0                                                   |
| Project       | `32-percolation` — Monte Carlo Forest Fire Percolation Simulation |
| Applies to    | Linux, macOS, Windows                                             |
| Specification | `SRS.md` (SRS-32), `shared/CLI-CONVENTIONS.md`                    |

---

## NAME

**dp-perc** — simulate a forest fire spreading through a random forest

## SYNOPSIS

```text
dp-perc [-p | --prompt] [-s SIZE | --size=SIZE] [--seed=SEED] [FILE]
dp-perc --help
dp-perc --version
```

## DESCRIPTION

`dp-perc` plants a square forest at random, sets every tree in its top row on fire, lets the
fire spread downward, and prints the forest before and after the fire with some statistics.
It reads its responses from _FILE_, or from standard input when there is no _FILE_ or _FILE_
is `-`: first a tree density, then, after each simulation, an answer to `Again? (y/n)`.

### A simulation

1. **Planting.** Each cell of the forest (25×25 unless `--size` says otherwise) holds a tree
   with a probability equal to the density you asked for: at density 60, about 60% of the
   cells hold a tree.
2. **Ignition.** Every tree in the top row catches fire.
3. **Spreading.** Row by row, from the second row down, a tree catches fire if a burning tree
   stands directly above it or diagonally above it to the left or right. The fire never moves
   sideways or upward, and it cannot cross an empty cell.

The output of one simulation looks like this (`--size=8`, density 30):

```text
Forest before fire:
+--------+
|  TT TTT|
|T     T |
|       T|
|      TT|
| T      |
|T    T T|
|   T T T|
|TT      |
+--------+
Forest after fire:
+--------+
|  ** ***|
|T     * |
|       *|
|      **|
| T      |
|T    T T|
|   T T T|
|TT      |
+--------+
Requested density: 30%
Actual density: 29.69%
Trees at start: 19
Trees surviving: 10
```

`T` is a tree, `*` a burned tree, and a space is empty ground. The actual density is the
percentage of cells that received a tree, rounded to two decimals; it differs from the requested
density because the trees are planted at random.

### Responses

- A **density** is a whole number from 1 to 100 (a `+` sign and leading zeros are allowed).
- An **answer** is `y` or `Y` to run another simulation, or `n` or `N` to stop. Nothing else is
  accepted, not even `yes`.

Responses are separated by any mix of spaces, tabs, and line breaks. If the input ends where an
answer is expected, `dp-perc` stops as if you had answered `n`; if it ends where a density is
expected, that is an error. Files with Windows (CRLF) line endings read the same as any other,
and one or more Ctrl-Z bytes at the very end of the input are ignored.

### Reproducible randomness

`dp-perc` uses the portable random number generator given as an example in the ANSI C standard,
started from the seed given with `--seed` (1 by default). The same seed, size, and responses
always produce the same forests, on every system and in every implementation. The generator is
started once per run and continues from one simulation to the next, so the second forest of a
session is not the same as the first, even at the same density. Use a different seed to see
different forests.

For the curious: each cell, in reading order (left to right along the top row, then the next
row, and so on), takes the next random number _r_ from 0 to 32767 and holds a tree if
(_r_ mod 100) + 1 is at most the density.

### Working interactively

`dp-perc` prints each simulation as soon as you have typed the density. End the input with
**Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by **Enter** in a Windows console. With
`--prompt`, `dp-perc` asks for each response:

```text
$ dp-perc --prompt --size=8
Enter density (1-100): 30
Forest before fire:
...
Trees surviving: 10
Again? (y/n) n
```

The prompts are written to standard error, so `dp-perc --prompt > fire.txt` saves only the
simulations.

## OPTIONS

**`-p`, `--prompt`**
: Write `Enter density (1-100): ` before each density is read and `Again? (y/n) ` before each
answer is read, to standard error.

**`-s` _SIZE_, `--size=`_SIZE_**
: Use a forest of _SIZE_ by _SIZE_ cells, from 1 to 78 (default 25). The framed forest is
_SIZE_ + 2 columns wide, so 78 still fits an 80-column terminal.

**`--seed=`_SEED_**
: Start the random number generator from _SEED_, a whole number from 0 to 4294967295
(default 1).

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-perc` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--see` is not accepted.
- An option's value may be attached or separate: `-s8`, `-s 8`, `--size=8`, `--size 8`. Short
  options can be combined: `-ps8` means `-p -s 8`.
- If an option is given more than once, the last value counts.
- Options and the file name can be given in any order: `dp-perc responses.txt -s 8` works.
- `--` ends option processing, so `dp-perc -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                           |
| :----- | :---------------------------------------------------------------------------------------------------------------- |
| 0      | Success: the session ended with `n` or at the end of the input after a simulation, or help or version was printed |
| 1      | The input could not be read, or it contained an invalid or missing response                                       |
| 2      | Usage error: an invalid option, an invalid size or seed, or more than one file                                    |

## DIAGNOSTICS

Problems with the responses name the input (`-` for standard input) and the line number.
Simulations printed before the problem are kept, and the exit status is 1:

```text
$ dp-perc -s 5 bad-answer.txt
Forest before fire:
...
Trees surviving: 0
dp-perc: bad-answer.txt:2: invalid answer 'maybe'
```

| Message                        | Cause                                                              | Fix                                                       |
| :----------------------------- | :----------------------------------------------------------------- | :-------------------------------------------------------- |
| `S:L: invalid integer 'K'`     | The density _K_ on line _L_ is not a whole number                  | Write the density in digits only, without `%` or decimals |
| `S:L: value out of range 'K'`  | The density _K_ is not between 1 and 100                           | Give a density from 1 to 100                              |
| `S:L: invalid answer 'K'`      | The answer _K_ is not `y`, `Y`, `n`, or `N`                        | Answer with one of those letters                          |
| `S:L: unexpected end of input` | The input ended where a density was expected; _L_ is the last line | Supply a density at the start and after every `y`         |
| `F: No such file or directory` | _F_ does not exist                                                 | Check the spelling and the current directory              |
| `F: Permission denied`         | You may not read _F_                                               | Check the file's permissions                              |
| `F: Is a directory`            | _F_ is a directory                                                 | Name a file instead                                       |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                    | Correct the path                                          |
| `F: Input/output error`        | Any other read failure                                             | Check the device or file system                           |
| `write error`                  | The results could not be written (for example, the disk is full)   | Free space or redirect the output elsewhere               |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-perc --size=0 once.txt
dp-perc: invalid argument '0' for '--size'
Try 'dp-perc --help' for more information.
```

| Message                                       | Cause                                                   | Fix                                    |
| :-------------------------------------------- | :------------------------------------------------------ | :------------------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p` or `-s`                       |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full               |
| `option requires an argument -- 's'`          | `-s` was given without a size                           | Add the size                           |
| `option '--size' requires an argument`        | `--size` or `--seed` was the last argument              | Add the value                          |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                        |
| `invalid argument 'V' for '--size'`           | The size is not a whole number from 1 to 78             | Give a size from 1 to 78               |
| `invalid argument 'V' for '--seed'`           | The seed is not a whole number from 0 to 4294967295     | Give a seed in that range, digits only |
| `extra operand 'F'`                           | More than one file was named                            | Run `dp-perc` once per file            |

## EXAMPLES

One simulation of the standard 25×25 forest at density 60, then stop:

```sh
printf '60\nn\n' | dp-perc
```

Compare a sparse and a dense forest of side 8 in one session:

```sh
printf '30 y 80 n\n' | dp-perc --size=8
```

A full forest burns completely:

```text
$ printf '100 n\n' | dp-perc -s 3
Forest before fire:
+---+
|TTT|
|TTT|
|TTT|
+---+
Forest after fire:
+---+
|***|
|***|
|***|
+---+
Requested density: 100%
Actual density: 100.00%
Trees at start: 9
Trees surviving: 0
```

Count, for ten seeds, how many trees survive at density 50:

```sh
for seed in 1 2 3 4 5 6 7 8 9 10; do
    echo 50 | dp-perc --seed=$seed | grep 'Trees surviving'
done
```

## HELP OUTPUT

`dp-perc --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-perc [OPTION]... [FILE]
Simulate a forest fire spreading through a randomly planted square forest.

Read whitespace-separated responses from FILE, or from standard input when
FILE is absent or -: a tree density in percent (1-100), then after each
simulation an answer y or n to 'Again?'.  Each simulation plants the forest,
sets the top row on fire, lets the fire spread downward, and prints the forest
before and after the fire with statistics.

Options:
  -p, --prompt       write prompts to standard error before reading
  -s, --size=SIZE    use a SIZE by SIZE forest (1-78, default 25)
      --seed=SEED    seed the random number generator (0-4294967295,
                       default 1)
      --help         display this help and exit
      --version      output version information and exit
```

## VERSION OUTPUT

```text
dp-perc (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-perc` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`), and
never uses the clock: without `--seed`, every run uses seed 1.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Response files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a response).
- **All platforms:** the random numbers do not come from the system's own generator, so the
  same seed gives the same forests everywhere.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-dice` (project 22), which also simulates chance with the CONV-38 generator; `dp-matmult`
(project 30), which also works on a square grid; `dp-tromino` (project 24); `shuf(1)`.
