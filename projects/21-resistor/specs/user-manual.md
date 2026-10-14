# dp-resistor — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-resistor` 1.0.0 |
| Project | `21-resistor` — Resistor 3-Band Color Code Decoder |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-21), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-resistor** — decode the color bands of 3-band resistors

## SYNOPSIS

```text
dp-resistor [-p | --prompt] [FILE]
dp-resistor --help
dp-resistor --version
```

## DESCRIPTION

`dp-resistor` first writes a guide to the resistor color codes:

```text
Resistor color codes
Code  Color   Value
B     Black   0
N     Brown   1
R     Red     2
O     Orange  3
Y     Yellow  4
G     Green   5
E     Blue    6
V     Violet  7
A     Gray    8
W     White   9
```

It then reads the codes of resistors from *FILE*, or from standard input when there is no
*FILE* or *FILE* is `-`. For each resistor it reads the codes of its three bands and writes
the resistance:

```text
Resistance of Y V R = 4.700000 kilo-ohms
```

After each resistance it reads an answer: **1** to decode another resistor, **0** to stop.

### The codes

Each code is one letter from the guide, typed in upper or lower case, and the codes are
separated by spaces, tabs, or line breaks: `Y V R`, `y v r`, and the three letters on three
lines all mean the same. Three letters typed together (`YVR`) are not three codes. Files with
Windows (CRLF) line endings read the same as any other, and one or more Ctrl-Z bytes at the very
end of the input (the end-of-file mark of old MS-DOS files) are ignored.

### The resistance

The first two bands are the digits of a two-digit number and the third band is the power of
ten it is multiplied by: yellow (4), violet (7), red (2) is 47 × 10² = 4700 ohms. The
resistance is written with six decimals in the largest unit that keeps it at least 1:

| Resistance | Written as | Example |
| :-- | :-- | :-- |
| below 1000 ohms | ohms | `R R B` → `22.000000 ohms` |
| 1000 up to 999 999 ohms | kilo-ohms | `B N O` → `1.000000 kilo-ohms` |
| 1 000 000 ohms and above | mega-ohms | `N B E` → `10.000000 mega-ohms` |

The smallest resistance is `B B B`, `0.000000 ohms`; the largest is `W W W`,
`99000.000000 mega-ohms`. The values are exact.

### Mistakes

If a code is not a letter from the guide, `dp-resistor` says so on standard error and reads
three new codes; the resistance of the rejected codes is not written. When the session ends,
the exit status is 1 to show that something was rejected.

The answer after a resistance must be `1` or `0` (`+1` and `01` are accepted too). Anything else
is reported and ends the session, keeping the resistances already written.

### Ending the session

The session ends when you answer `0`, or when the input ends before the next resistor or in
place of an answer, so a file of codes needs no `0` at the end. If the input ends after only one
or two codes of a resistor, that is reported as an error.

### Working interactively

`dp-resistor` writes each resistance as soon as you finish typing its third code. End the input
with **Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by **Enter** in a Windows console, or
simply answer `0`. With `--prompt`, `dp-resistor` asks for each input:

```text
$ dp-resistor --prompt
Resistor color codes
Code  Color   Value
B     Black   0
…
W     White   9
Enter the three color codes: Y Q R
dp-resistor: -:1: invalid color code 'Q'
Enter the three color codes: y v r
Resistance of Y V R = 4.700000 kilo-ohms
Decode another resistor (1 = yes, 0 = no)? 0
```

The prompts are written to standard error, so `dp-resistor --prompt > values.txt` saves only the
guide and the resistances.

## OPTIONS

**`-p`, `--prompt`**
: Write `Enter the three color codes: ` to standard error before the codes of each resistor are
  read, and `Decode another resistor (1 = yes, 0 = no)? ` before each answer is read.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-resistor` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-resistor codes.txt -p` works.
- `--` ends option processing, so `dp-resistor -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the session ended normally and every code was valid (an empty input is fine), or help or version was printed |
| 1 | A code was rejected, an answer was invalid, the input ended in the middle of a resistor, or the input could not be read |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. An invalid
code does not stop the session; every other problem does, keeping what was already written:

```text
$ dp-resistor invalid.txt
Resistor color codes
…
W     White   9
Resistance of Y V R = 4.700000 kilo-ohms
dp-resistor: invalid.txt:1: invalid color code 'Q'
dp-resistor: invalid.txt:2: invalid color code 'YVR'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid color code 'K'` | Entry *K* on line *L* is not one of the letters in the guide (the session continues) | Type one letter per band, separated by spaces |
| `S:L: invalid integer 'K'` | The answer *K* on line *L* is not a whole number | Answer `1` or `0` |
| `S:L: value out of range 'K'` | The answer *K* on line *L* is a number other than 1 and 0 | Answer `1` or `0` |
| `S:L: unexpected end of input` | The input ended after only one or two codes of a resistor | Give all three codes |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The output could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-resistor codes.txt mixed.txt
dp-resistor: extra operand 'mixed.txt'
Try 'dp-resistor --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-resistor` once per file |

## EXAMPLES

Decode one resistor from a pipe (no answer is needed after the last one):

```text
$ echo 'Y V R' | dp-resistor
Resistor color codes
…
W     White   9
Resistance of Y V R = 4.700000 kilo-ohms
```

Decode a list of resistors, in lower case, several per line:

```text
$ printf 'b n o 1 n b e 1 r r b\n' | dp-resistor | tail -n 3
Resistance of B N O = 1.000000 kilo-ohms
Resistance of N B E = 10.000000 mega-ohms
Resistance of R R B = 22.000000 ohms
```

Keep only the resistances:

```sh
dp-resistor kit.txt | grep '^Resistance of' > values.txt
```

Use the exit status in a script:

```sh
if ! dp-resistor kit.txt > values.txt; then
    echo "some codes were rejected; see the messages above" >&2
fi
```

## HELP OUTPUT

`dp-resistor --help` prints exactly the following text (every line ends in LF). The help text
is part of the specification (CONV-23):

```text
Usage: dp-resistor [OPTION]... [FILE]
Decode the color codes of 3-band resistors into resistances.

With no FILE, or when FILE is -, read standard input.  The color guide is
written first.  Each resistor is then given as three codes separated by
whitespace, one letter per band, in either case: B black 0, N brown 1,
R red 2, O orange 3, Y yellow 4, G green 5, E blue 6, V violet 7, A gray 8,
W white 9.  After each resistance, answer 1 to decode another resistor or 0
to stop.  An invalid code is reported and the three codes are asked for again.

Options:
  -p, --prompt    write prompts to standard error before each read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-resistor (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-resistor` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Lower-case codes are recognized by plain ASCII rules, so the result is the same in every
language setting.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is part of a code (and makes it invalid), not an
  end-of-file mark. Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a code).

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-convert` (project 12), another interactive unit conversion; `dp-taxes` (project 13), which
reads its input the same way; `dp-calc` (project 37); `units(1)`, `bc(1)`.
