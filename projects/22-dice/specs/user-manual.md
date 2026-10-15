<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-dice — User Manual](#dp-dice--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The rules](#the-rules)
    - [The transcript](#the-transcript)
    - [The dice](#the-dice)
    - [Responses](#responses)
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

# dp-dice — User Manual

| Field         | Value                                            |
| :------------ | :----------------------------------------------- |
| Product       | `dp-dice` 1.0.0                                  |
| Project       | `22-dice` — Roll Them Bones Dice Simulation Game |
| Applies to    | Linux, macOS, Windows                            |
| Specification | `SRS.md` (SRS-22), `shared/CLI-CONVENTIONS.md`   |

---

## NAME

**dp-dice** — play the dice game Roll Them Bones

## SYNOPSIS

```text
dp-dice [-p | --prompt] [--seed=SEED] [FILE]
dp-dice --help
dp-dice --version
```

## DESCRIPTION

`dp-dice` plays "Roll Them Bones" against the house. You start with a bankroll of $500.
Before each round you answer **1** to play or **0** to quit, and then you bet a whole number of
dollars. The responses are read from _FILE_, or from standard input when there is no _FILE_ or
_FILE_ is `-`.

### The rules

- A bet must be at least $1, at most the table limit of $250, and no more than your bankroll.
  A bet that breaks a rule is refused with the reason, and you are asked for the bet again.
- Two dice are rolled. If the first roll of the round is **7 or 11** (a _natural_), you win
  your bet at once.
- Any other first roll is your **mark**. The dice are rolled again until either the mark comes
  up again, and you win your bet, or a **7 or 11** comes up, and you lose it.
- If the mark is **2** (snake eyes) or **12** (box cars), making it pays **double**. Only the
  same number counts: with a mark of 2, a 12 is just another roll.
- The game ends when you quit or your bankroll reaches $0.

### The transcript

Every bet, roll, and outcome is written to standard output, followed by your bankroll:

```text
$ printf '1 100\n0\n' | dp-dice
Your bankroll is $500.
You bet $100.
Roll: 3 + 5 = 8
Your mark is 8.
Roll: 4 + 2 = 6
Roll: 2 + 6 = 8
You made your mark! You win $100.
Your bankroll is $600.
Congratulations! You leave the table with $600.
```

The other messages are `Natural! You win $W.`, `Your mark is M; it pays double.`,
`Out! You lose $W.`, the refusals `Bet refused: the minimum bet is $1.`,
`Bet refused: the table limit is $250.`, and `Bet refused: you only have $B.`, and, when the
money is gone, `You're broke! Better luck next time.`

### The dice

The dice come from the portable pseudo-random generator of the curriculum's conventions
(CONV-38), started from a _seed_. The same seed and the same responses always give the same
game, on every computer; the default seed is 1. Use `--seed` to play a different game.

### Responses

Responses are whole numbers separated by spaces, tabs, or line breaks, so `1 100` on one line
and `1` and `100` on two lines mean the same. Files with Windows (CRLF) line endings read the
same as any other, and Ctrl-Z bytes at the very end of a file are ignored. When a bet is refused,
the next response is the new bet. When the responses run out before a round, you quit; a file of
responses therefore needs no final `0`. Responses left over after you go broke are ignored.

A response that is not a whole number, or an answer to "Want to play?" other than 1 or 0, is
reported and ends the game without a banner. So does running out of responses when a bet is
expected.

### Working interactively

`dp-dice` writes the outcome of each response as soon as you type it. End the input with
**Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed by **Enter** in a Windows console, or
simply answer `0`. With `--prompt`, `dp-dice` asks for each response:

```text
$ dp-dice --prompt
Your bankroll is $500.
Want to play? (1: yes, 0: no) 1
Enter your bet: 300
Bet refused: the table limit is $250.
Enter your bet: 100
You bet $100.
Roll: 3 + 5 = 8
Your mark is 8.
Roll: 4 + 2 = 6
Roll: 2 + 6 = 8
You made your mark! You win $100.
Your bankroll is $600.
Want to play? (1: yes, 0: no) 0
Congratulations! You leave the table with $600.
```

The prompts are written to standard error, so `dp-dice --prompt > game.txt` saves only the
transcript.

## OPTIONS

**`-p`, `--prompt`**
: Write `Want to play? (1: yes, 0: no) ` to standard error before each answer is read, and
`Enter your bet: ` before each bet is read.

**`--seed=SEED`**
: Start the dice generator from _SEED_, a whole number from 0 to 4294967295 written in digits.
The default is 1.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-dice` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--se` is not accepted. `--seed 14` and
  `--seed=14` are the same; if `--seed` is given twice, the last one counts.
- Options and the file name can be given in any order: `dp-dice play.txt -p` works.
- `--` ends option processing, so `dp-dice -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                           |
| :----- | :---------------------------------------------------------------------------------------------------------------- |
| 0      | The game ended: you quit, the responses ran out before a round, or you went broke; or help or version was printed |
| 1      | A response was malformed, the responses ran out when a bet was expected, or the input could not be read           |
| 2      | Usage error: an invalid option, an invalid seed, or more than one file                                            |

## DIAGNOSTICS

Problems with the responses name the input (`-` for standard input) and the line number. The
transcript written before the problem is kept, and the exit status is 1:

```text
$ dp-dice badbet.txt
Your bankroll is $500.
dp-dice: badbet.txt:2: invalid integer '12.50'
```

| Message                        | Cause                                                                        | Fix                                          |
| :----------------------------- | :--------------------------------------------------------------------------- | :------------------------------------------- |
| `S:L: invalid integer 'K'`     | Response _K_ on line _L_ is not a whole number (or is far too large)         | Write the response in digits only            |
| `S:L: value out of range 'K'`  | The answer _K_ on line _L_ to "Want to play?" is a number other than 1 and 0 | Answer `1` or `0`                            |
| `S:L: unexpected end of input` | The responses ran out when a bet was expected                                | Give a bet after every `1`                   |
| `F: No such file or directory` | _F_ does not exist                                                           | Check the spelling and the current directory |
| `F: Permission denied`         | You may not read _F_                                                         | Check the file's permissions                 |
| `F: Is a directory`            | _F_ is a directory                                                           | Name a file instead                          |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                              | Correct the path                             |
| `F: Input/output error`        | Any other read failure                                                       | Check the device or file system              |
| `write error`                  | The transcript could not be written (for example, the disk is full)          | Free space or redirect the output elsewhere  |

A refused bet is not an error: the reason is part of the transcript and the game goes on.

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-dice --seed=abc
dp-dice: invalid argument 'abc' for '--seed'
Try 'dp-dice --help' for more information.
```

| Message                                       | Cause                                                   | Fix                                 |
| :-------------------------------------------- | :------------------------------------------------------ | :---------------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`                            |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full            |
| `option '--seed' requires an argument`        | `--seed` was the last argument                          | Give a seed: `--seed=14`            |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`                     |
| `invalid argument 'V' for '--seed'`           | The seed is not a number from 0 to 4294967295           | Give digits only, within that range |
| `extra operand 'F'`                           | More than one file was named                            | Name one file of responses          |

## EXAMPLES

A first roll of 7 wins at once:

```text
$ printf '1 100 0\n' | dp-dice --seed=6
Your bankroll is $500.
You bet $100.
Roll: 3 + 4 = 7
Natural! You win $100.
Your bankroll is $600.
Congratulations! You leave the table with $600.
```

Snake eyes, made again, pays double:

```text
$ printf '1 250 0\n' | dp-dice --seed=14
Your bankroll is $500.
You bet $250.
Roll: 1 + 1 = 2
Your mark is 2; it pays double.
Roll: 1 + 1 = 2
You made your mark! You win $500.
Your bankroll is $1000.
Congratulations! You leave the table with $1000.
```

Bet everything until broke (the third round is never played):

```text
$ printf '1 250\n1 250\n1 250\n' | dp-dice --seed=2
Your bankroll is $500.
You bet $250.
Roll: 3 + 6 = 9
Your mark is 9.
Roll: 4 + 3 = 7
Out! You lose $250.
Your bankroll is $250.
You bet $250.
Roll: 2 + 6 = 8
Your mark is 8.
Roll: 1 + 2 = 3
Roll: 5 + 6 = 11
Out! You lose $250.
Your bankroll is $0.
You're broke! Better luck next time.
```

Compare the final bankroll of one strategy over several seeds:

```sh
for seed in 1 2 3 4 5; do
    dp-dice --seed="$seed" strategy.txt | tail -n 1
done
```

## HELP OUTPUT

`dp-dice --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-dice [OPTION]... [FILE]
Play the dice game Roll Them Bones against the house.

With no FILE, or when FILE is -, read the player's responses from standard
input: before each round, 1 to play or 0 to quit, then the bet in whole
dollars.  The bankroll starts at $500; a bet must be from 1 to 250 and may not
exceed the bankroll.  A first roll of 7 or 11 wins at once; any other first
roll becomes the mark, which wins if it is rolled again (double for 2 and 12)
before a 7 or 11, which loses.  The game ends when the player quits or is
broke.

Options:
  -p, --prompt       write prompts to standard error before each read
      --seed=SEED    seed the dice with SEED, from 0 to 4294967295 (default 1)
      --help         display this help and exit
      --version      output version information and exit
```

## VERSION OUTPUT

```text
dp-dice (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-dice` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`). It
never uses the clock or the system's random-number generator, so a game depends only on the
seed and the responses.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte in the middle of a file is part of a response (and makes it invalid). Output uses
  LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a response).
- **All platforms:** the same seed and responses give the same game everywhere; the dice do not
  come from the C library's `rand()`, whose sequence differs between systems.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-perc` (project 32), another simulation driven by the CONV-38 generator; `dp-resistor`
(project 21), another keyboard dialog that reads its responses as tokens; `shuf(1)`.
