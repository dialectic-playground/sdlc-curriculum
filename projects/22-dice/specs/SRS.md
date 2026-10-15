<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Software Requirements Specification (SRS) — dp-dice](#software-requirements-specification-srs--dp-dice)
  - [1. Introduction](#1-introduction)
    - [1.1 Purpose](#11-purpose)
    - [1.2 Scope](#12-scope)
    - [1.3 Definitions](#13-definitions)
    - [1.4 References](#14-references)
  - [2. Overall description](#2-overall-description)
    - [2.1 Product perspective](#21-product-perspective)
    - [2.2 Product functions](#22-product-functions)
    - [2.3 Constraints](#23-constraints)
    - [2.4 Assumptions](#24-assumptions)
    - [2.5 Relationship to the textbook program (informative)](#25-relationship-to-the-textbook-program-informative)
    - [2.6 Relationship to CLI-CONV](#26-relationship-to-cli-conv)
  - [3. External interface requirements](#3-external-interface-requirements)
    - [3.1 Command-line synopsis](#31-command-line-synopsis)
    - [3.2 Options](#32-options)
    - [3.3 Operands](#33-operands)
    - [3.4 Standard input](#34-standard-input)
    - [3.5 Standard output](#35-standard-output)
    - [3.6 Standard error](#36-standard-error)
    - [3.7 Exit status](#37-exit-status)
  - [4. Functional requirements](#4-functional-requirements)
  - [5. Non-functional requirements](#5-non-functional-requirements)
  - [6. Diagnostics (complete list)](#6-diagnostics-complete-list)
  - [7. Verification](#7-verification)
  - [8. Traceability (URD → SRS)](#8-traceability-urd-%E2%86%92-srs)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Software Requirements Specification (SRS) — dp-dice

| Field                     | Value                                            |
| :------------------------ | :----------------------------------------------- |
| Document ID               | SRS-22                                           |
| Project                   | `22-dice` — Roll Them Bones Dice Simulation Game |
| Product                   | `dp-dice` (canonical name)                       |
| Version                   | 1.0.0                                            |
| Status                    | Approved (pre-written by the curriculum)         |
| Parent document           | `URD.md` (URD-22)                                |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0)     |
| Structure                 | Adapted from ISO/IEC/IEEE 29148:2018             |

## 1. Introduction

### 1.1 Purpose

This SRS specifies the externally observable behavior of `dp-dice`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
output for every invocation. It is the authoritative source for design (HLD/LLD), testing, and
grading.

### 1.2 Scope

`dp-dice` plays the dice game "Roll Them Bones" with one player. It reads the player's
responses — whether to play a round, and the bet — as tokens from standard input or from one
file, rolls two dice per throw with the portable pseudo-random generator of CONV-38, writes a
transcript of every bet, roll, and outcome and the bankroll after every round, and ends with a
banner when the player quits or is broke. Bets that break the rules are refused and asked for
again; malformed responses, responses that run out during a bet, and unreadable files end the
run with fixed diagnostics. Prompts can be written to standard error.

### 1.3 Definitions

| Term                     | Definition                                                                                                                                                        |
| :----------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| LF                       | The line-feed byte, `0x0A`                                                                                                                                        |
| Input                    | The byte sequence read from standard input or from the FILE operand                                                                                               |
| Source                   | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`)               |
| Token, line number       | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| End-of-input line number | As defined in CONV-32: 1 plus the number of LF bytes in the whole input                                                                                           |
| Bankroll                 | The player's money _B_, an integer number of dollars; _B_ = 500 at the start                                                                                      |
| Table limit              | The constant 250                                                                                                                                                  |
| Play answer              | The token read before each round, which decides whether the round is played (FR-05)                                                                               |
| Bet                      | The integer _W_ staked on a round once it has been accepted (FR-06)                                                                                               |
| Draw                     | One step of the CONV-38 generator, yielding _r_ in 0 … 32767                                                                                                      |
| Roll                     | Two dice thrown together: two draws, giving the faces _a_ and _b_ and the value _a_ + _b_ (FR-03)                                                                 |
| Mark                     | The value of a round's first roll when it is neither 7 nor 11 (FR-07)                                                                                             |
| Double mark              | A mark of 2 or 12 (FR-07)                                                                                                                                         |
| Round                    | One accepted bet and the rolls that settle it (FR-07, FR-08)                                                                                                      |
| Complete token           | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached                                |
| Decimal                  | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06)                            |

### 1.4 References

- URD-22: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, _Applications Programming in ANSI C_, 3rd ed., Prentice Hall,
  1996, §4.7 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective

`dp-dice` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §4.7 of
Johnsonbaugh & Kalin, _Applications Programming in ANSI C_.

### 2.2 Product functions

1. Keep the player's bankroll, starting at $500.
2. Read a play answer before each round and a bet for each round played, as tokens.
3. Refuse bets below $1, above the table limit, or above the bankroll, and ask again.
4. Roll two dice per throw with the CONV-38 generator and settle each round by the rules.
5. Write a transcript of every bet, roll, and outcome, and the bankroll after every round.
6. End the game when the player quits or is broke, with a closing banner.
7. Optionally write prompts to standard error before each read.
8. Report malformed responses, responses that run out during a bet, and unreadable input files.
9. Display help and version information; detect and report usage errors.

### 2.3 Constraints

- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The dice MUST come from the generator of CONV-38 exactly as FR-03 specifies; the platform's
  own random-number generator, the clock, and any other source of entropy MUST NOT be used.
- All money is computed in integer arithmetic.

### 2.4 Assumptions

- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-12.
- The input may contain any bytes; only tokens that match the _integer_ grammar are valid
  responses.

### 2.5 Relationship to the textbook program (informative)

The textbook program of §4.7 gives the player a nest egg of $500 and a table limit of $250,
asks before each round whether to play (`1: yes, 0: no`), reads and checks the bet, rolls two
dice, wins on a first roll of 7 or 11, otherwise rolls until the first roll (the mark) recurs —
paying double if the mark was 2 (snake eyes) or 12 (box cars) — or a 7 or 11 loses, and ends
with a banner that congratulates a player who quits or consoles one who is broke. `dp-dice`
keeps:

- the stakes (500, 250), the bet constraint 1 ≤ bet ≤ min(bankroll, 250), and the settlement
  rules, including the double payout on a recurring 2 or 12;
- the play question in the textbook's words, `Want to play? (1: yes, 0: no)`;
- the flow: play question, bet, rolls, settlement, bankroll, repeated until the player quits or
  is broke, then a congratulating or consoling banner.

It changes the following, for the reasons given:

- **A portable, seeded generator.** The textbook uses the C library's `rand()`, whose sequence
  differs between platforms. `dp-dice` uses the generator of CONV-38 with `--seed` (default 1,
  as in C when `srand` is never called), and FR-03 fixes the face derivation and the draw order,
  so a seed and a response file replay the same game everywhere.
- **The mark of 2 or 12.** The section's README describes the double payout in two ways ("if
  the mark is matched later" and "repeating 2 or 12"). This SRS reads both as the same rule: a
  first roll of 2 or 12 is the mark like any other, and only that same value wins (a first roll
  of 2 followed by 12 does not), as the README's step-by-step outline shows.
- **Messages.** The README does not give the textbook's message texts except the play question.
  The transcript messages of FR-04 … FR-10 are written in the same voice, and every roll is
  shown with both faces so the transcript can be checked by hand.
- **Refused bets.** The textbook warns and asks again. `dp-dice` writes the reason on standard
  output, as part of the transcript, and reads the next token as the new bet (FR-06). A refused
  bet is a game event, not an error: it does not change the exit status. A bet below $1 is also
  refused, which the README requires but does not show.
- **Malformed responses are fatal.** A token that is not an integer would stop a C `scanf` loop
  in an unspecified way (often forever). `dp-dice` reports it with its line number and exits
  with status 1, as it does for a play answer other than 0 or 1 (FR-11).
- **End of input is defined.** At the play question it means the player quits; in place of a
  bet it is an error (FR-10, FR-11). A response file therefore needs no final `0`.
- **Output layout.** The bankroll is shown at the start and after every round; lines that only
  separated output from echoed keyboard input are dropped, and the accepted bet is echoed
  (`You bet $100.`) so redirected output reads sensibly without the input.
- **Prompts are optional and go to standard error** (FR-13), and every message is flushed
  before the next response is read (FR-12).

### 2.6 Relationship to CLI-CONV

This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (play answers and
bets use the _integer_ grammar; play answers are further restricted to 0 … 1), CONV-34 (data
diagnostics, with the standard messages `invalid integer`, `value out of range`, and
`unexpected end of input` and the default consequences), CONV-36 (`-p`, `--prompt`), CONV-37
(the input is _text data_), and CONV-38 (the generator and `--seed`, with the derived quantities
and draw order of FR-03). CONV-35 does not apply, because no real number is ever written. A bet
outside 1 … min(bankroll, 250) is not a data diagnostic: it is a refusal written to standard
output (FR-06). Option syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16,
and the exit statuses are those of CONV-18. Standard input is read as permitted by CONV-26.
`dp-dice` copies no input bytes to its output except the bytes of a token quoted in a
diagnostic, so CONV-04 does not otherwise apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-dice [-p | --prompt] [--seed=SEED] [FILE]
dp-dice --help
dp-dice --version
```

### 3.2 Options

| Short | Long        | Argument | Default | Description                                                   |
| :---- | :---------- | :------- | :------ | :------------------------------------------------------------ |
| `-p`  | `--prompt`  | none     | off     | Write the prompts of FR-13 to standard error before each read |
| —     | `--seed`    | SEED     | 1       | The initial state of the generator (FR-14, CONV-38)           |
| —     | `--help`    | none     | —       | Print the help text and exit 0                                |
| —     | `--version` | none     | —       | Print the version line and exit 0                             |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12.
`--seed` accepts `--seed=SEED` and `--seed SEED` (CONV-08); if it is repeated, the last value
wins (CONV-11). Giving `-p` more than once has the same effect as giving it once.

### 3.3 Operands

At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input

Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output

The transcript (FR-04 … FR-10), in order. Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-16 … FR-19 instead.

### 3.6 Standard error

Prompts (FR-13, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition                                                                                                                                                     |
| :----- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0      | The game ended normally (FR-10): the player quit, the input ended at a play question, or the player is broke; or `--help` / `--version` was handled           |
| 1      | A response was malformed or the input ended in place of a bet (FR-11), the input could not be opened or read (FR-15), or standard output could not be written |
| 2      | Usage error (FR-18)                                                                                                                                           |

## 4. Functional requirements

Each requirement gives an acceptance criterion (_AC_) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following public fixture files in
`tests/fixtures/` are used: `play.txt` is `1 100\n1 100\n1 100\n0\n`; `once.txt` is
`1\n100\n0\n`; `double.txt` is `1\n250\n0\n`; `broke.txt` is `1 250\n1 250\n1 250\n`;
`refusals.txt` is `1\n300\n0\n250\n1\n-5\n100\n1\n200\n150\n1\n`; `badbet.txt` is `1\n12.50\n`.
Each message line below ends with a single LF and has no leading or trailing spaces; `<B>`,
`<W>`, and the other placeholders are decimals (section 1.3).

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written. More than one operand is a usage error (FR-18).
_AC:_ `dp-dice < play.txt`, `dp-dice play.txt`, and `dp-dice - < play.txt` write the same
transcript. _(UR-08)_

**FR-02: Tokens.**
The input is _text data_ (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which the
game consumes one at a time, in order, as play answers (FR-05) and bets (FR-06). Line structure
has no meaning: tokens may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so a
play answer and a bet may share a line and CRLF input reads exactly like LF input. Tokens after
the one that ends the game (FR-10) are neither read as responses nor validated.
_AC:_ an input `1\r\n100\r\n0\r\n` followed by one `0x1A` byte gives the same transcript as
`once.txt` with the default seed, exit 0. _(UR-08, UR-11)_

**FR-03: Generator and dice.**
The tool MUST use the generator of CONV-38, with its initial state set to the seed (FR-14)
once, before the game begins; the state carries over from roll to roll and from round to round.
Each roll consists of exactly two draws, *r*₁ then *r*₂, and the faces are _a_ = 1 + (*r*₁ mod 6)
for the first die and _b_ = 1 + (*r*₂ mod 6) for the second; the value of the roll is _a_ + _b_.
No other draws are made: the generator is not advanced by play answers, refused bets, or
anything but a roll.
_AC:_ with the default seed 1 the first four draws are 16838, 5758, 10113, and 17515, so the
first two rolls are 3 + 5 = 8 and 4 + 2 = 6; with seed 14 the first two rolls are 1 + 1 = 2 and
1 + 1 = 2; with seed 0 the first roll is 1 + 1 = 2; with seed 4294967295 the first roll is
6 + 6 = 12. _(UR-04, UR-07)_

**FR-04: Game flow.**
After the input has been opened, the tool MUST write `Your bankroll is $500.` and then repeat,
until the game ends (FR-10):

1. Read a play answer (FR-05). If it is 0, or the input has ended, the player quits (FR-10).
2. Read a bet (FR-06) and write `You bet $<W>.`.
3. Play the round (FR-07, FR-08) and update the bankroll (FR-09).
4. Write `Your bankroll is $<B>.` with the new bankroll. If _B_ = 0, the player is broke
   (FR-10).

_AC:_ `dp-dice < play.txt` → stdout begins
`Your bankroll is $500.\nYou bet $100.\nRoll: 3 + 5 = 8\nYour mark is 8.\nRoll: 4 + 2 = 6\nRoll: 2 + 6 = 8\nYou made your mark! You win $100.\nYour bankroll is $600.\n`
and ends `Your bankroll is $800.\nCongratulations! You leave the table with $800.\n`, stderr
empty, exit 0. _(UR-01, UR-05)_

**FR-05: Play answer.**
The play answer MUST be a valid _integer_ (CONV-33) whose value is 0 or 1; signs and leading
zeros are allowed. The value 1 plays a round; 0 quits. Any other token is handled by FR-11.
_AC:_ `dp-dice` with the input `2\n` → stdout `Your bankroll is $500.\n`, stderr
`dp-dice: -:1: value out of range '2'\n`, exit 1. _(UR-01)_

**FR-06: Bet.**
The bet MUST be read as one token that is a valid _integer_ (CONV-33); any other token is
handled by FR-11. The value _W_ is then checked against these rules, in this order, and the
first rule it breaks decides the refusal message:

| Rule      | Refusal message                         |
| :-------- | :-------------------------------------- |
| _W_ ≥ 1   | `Bet refused: the minimum bet is $1.`   |
| _W_ ≤ 250 | `Bet refused: the table limit is $250.` |
| _W_ ≤ _B_ | `Bet refused: you only have $<B>.`      |

A refused bet MUST be answered with its refusal message on standard output, after which the
tool reads the next token as a new bet (writing the bet prompt again when prompts are enabled,
FR-13). This repeats until a bet is accepted. A refusal does not end the game, consume a draw,
or change the bankroll or the exit status. A bet equal to the bankroll, or to the table limit,
is accepted.
_AC:_ `dp-dice --seed=5 refusals.txt` → stdout
`Your bankroll is $500.\nBet refused: the table limit is $250.\nBet refused: the minimum bet is $1.\nYou bet $250.\n`
…, later `Your bankroll is $250.\nBet refused: the minimum bet is $1.\nYou bet $100.\n` … and
`Your bankroll is $150.\nBet refused: you only have $150.\nYou bet $150.\n` …, exit 0 (the
token `0` on line 3 is read as a bet, not as a play answer). _(UR-02, UR-03)_

**FR-07: First roll.**
Each round MUST begin with one roll, written as `Roll: <a> + <b> = <a+b>` (FR-03). Then:

- if the value is 7 or 11, the round is won at once: write `Natural! You win $<W>.`; the round
  ends with a gain of _W_;
- if the value is 2 or 12, it becomes a double mark: write `Your mark is <m>; it pays double.`;
- otherwise it becomes the mark: write `Your mark is <m>.`.

_AC:_ seed 6 with `once.txt` → `Roll: 3 + 4 = 7\nNatural! You win $100.\n`; seed 4 →
`Roll: 6 + 5 = 11\nNatural! You win $100.\n`; seed 14 with `double.txt` →
`Roll: 1 + 1 = 2\nYour mark is 2; it pays double.\n`. _(UR-04, UR-05)_

**FR-08: Point rolls.**
After a mark has been set, the tool MUST roll again, writing each roll as in FR-07, until a
roll settles the round:

- a roll equal to the mark wins: write `You made your mark! You win $<P>.`, where _P_ = 2 × _W_
  for a double mark and _P_ = _W_ otherwise; the round ends with a gain of _P_;
- otherwise a roll of 7 or 11 loses: write `Out! You lose $<W>.`; the round ends with a loss
  of _W_;
- any other roll writes nothing more, and the tool rolls again.

Only the mark's own value wins: with a mark of 2, a roll of 12 neither wins nor loses. The
round always ends, because the generator's sequence is periodic and contains every roll value.
_AC:_ seed 14 with `double.txt` → `…Roll: 1 + 1 = 2\nYou made your mark! You win $500.\nYour bankroll is $1000.\n`;
seed 68 → mark 12, rolls 10 and 5, then 12, win $500; seed 2 with `broke.txt` →
`Roll: 3 + 6 = 9\nYour mark is 9.\nRoll: 4 + 3 = 7\nOut! You lose $250.\n`; seed 8 with
`once.txt` → mark 8, then 5, then `Roll: 5 + 6 = 11\nOut! You lose $100.\n`; seed 0 with
`once.txt` → mark 2 (double), then `Roll: 5 + 2 = 7\nOut! You lose $100.\n`. _(UR-04, UR-05)_

**FR-09: Bankroll.**
At the end of a round the bankroll MUST be updated exactly: _B_ ← _B_ + gain or _B_ ← _B_ −
loss. Because an accepted bet never exceeds _B_, the bankroll never becomes negative; because
it grows by at most 500 per round and each round consumes at least two input bytes, it cannot
exceed 2⁶³−1 for any input shorter than 2⁵⁴ bytes, so 64-bit signed integers suffice.
_AC:_ seed 14 with `double.txt` and a bet of 250 → `Your bankroll is $1000.`; seed 2 with
`broke.txt` → `Your bankroll is $250.` after the first round and `Your bankroll is $0.` after
the second. _(UR-01, UR-05)_

**FR-10: End of the game.**
The game ends normally in exactly these cases:

- **Quit.** The play answer is 0, or the input ends where a play answer is expected. The tool
  writes `Congratulations! You leave the table with $<B>.` and exits with status 0.
- **Broke.** The bankroll is 0 after a round (FR-04 step 4). The tool writes
  `You're broke! Better luck next time.` and exits with status 0, without reading any further
  input (remaining responses are ignored).

_AC:_ `dp-dice` with empty standard input → stdout
`Your bankroll is $500.\nCongratulations! You leave the table with $500.\n`, stderr empty,
exit 0; `dp-dice --seed=2 < broke.txt` → stdout ends
`Out! You lose $250.\nYour bankroll is $0.\nYou're broke! Better luck next time.\n`, exit 0,
although a third round was requested. _(UR-06)_

**FR-11: Malformed responses.**
The tool MUST write a CONV-34 diagnostic and end the run with exit status 1, writing no banner
and nothing more to standard output (output already written is kept), when:

| Condition                                                                                            | Message                                                  |
| :--------------------------------------------------------------------------------------------------- | :------------------------------------------------------- |
| A play answer or a bet is not a valid _integer_ (CONV-33), including an integer outside −2⁶³ … 2⁶³−1 | `dp-dice: <source>:<line>: invalid integer '<token>'`    |
| A play answer is a valid _integer_ other than 0 and 1                                                | `dp-dice: <source>:<line>: value out of range '<token>'` |
| The input ends where a bet is expected (including after a refused bet)                               | `dp-dice: <source>:<line>: unexpected end of input`      |

`<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32) or, for
the end of the input, the end-of-input line number, and `<token>` is the token's exact bytes,
without escaping. A valid _integer_ bet is never a data error, however large or small: it is
refused by FR-06.
_AC:_ `dp-dice badbet.txt` → stdout `Your bankroll is $500.\n`, stderr
`dp-dice: badbet.txt:2: invalid integer '12.50'\n`, exit 1; the input `1\n` → stderr
`dp-dice: -:2: unexpected end of input\n`, exit 1; a bet `9223372036854775807` is refused by the
table limit, while `9223372036854775808` gives `invalid integer`. _(UR-10)_

**FR-12: Streaming.**
The tool MUST NOT wait for the end of the input before writing. It MUST write every message
that follows from a response, and flush standard output, before it waits for the next
response, and it MUST NOT read the input beyond what it needs to complete the current token,
apart from ordinary buffering of bytes that are already available.
_AC:_ At a terminal, typing `1`, Enter, `100`, Enter shows the whole round and the new bankroll
before anything else is typed (manual check). _(UR-09)_

**FR-13: Prompts.**
`-p`, `--prompt` enables the two prompts of this tool:

| Prompt      | Exact bytes (no LF)                                            | Written                                                                                  |
| :---------- | :------------------------------------------------------------- | :--------------------------------------------------------------------------------------- |
| Play prompt | `Want to play? (1: yes, 0: no)30 bytes, ending with one space) | Before each play answer is read, including the attempt that reaches the end of the input |
| Bet prompt  | `Enter your bet:16 bytes, ending with one space)               | Before each bet is read, including every new bet after a refusal                         |

With prompts enabled, the tool MUST write each prompt to standard error, and flush it,
immediately before the read it belongs to (CONV-36). A prompt is written even if the read
reaches the end of the input. A diagnostic that follows a prompt continues the same line of
standard error. Prompts never change standard output. No prompt is written if the input cannot
be opened, and none after the game has ended.
_AC:_ `dp-dice --prompt --seed=8 < once.txt` → stdout as without `--prompt`, stderr
`Want to play? (1: yes, 0: no) Enter your bet: Want to play? (1: yes, 0: no)ith no LF,
exit 0; `dp-dice -p`with the input`1\n`→ stderr`Want to play? (1: yes, 0: no) Enter your bet: dp-dice: -:2: unexpected end of input\n`.
_(UR-09)_

**FR-14: Seed.**
`--seed=SEED` sets the generator's initial state (CONV-38). SEED MUST consist only of ASCII
digits (leading zeros allowed) and lie in 0 … 4294967295; otherwise — including an empty value,
a sign, or a larger number — it is an invalid option value, reported as
`dp-dice: invalid argument '<SEED>' for '--seed'` (CONV-13) after the whole argument list has
been scanned (CONV-12). Without `--seed`, the seed is 1.
_AC:_ `dp-dice --seed=abc` → `dp-dice: invalid argument 'abc' for '--seed'` and the CONV-14
line, exit 2; `--seed=4294967296`, `--seed=`, and `--seed=-1` are rejected the same way;
`--seed=4294967295` is accepted; `--seed=1 --seed=14` plays with seed 14. _(UR-07)_

**FR-15: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-dice: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. If the input cannot be opened, nothing is written to standard output.
Output already written is kept. When standard input fails, `<source>` is `-`.
_AC:_ `dp-dice missing.txt` → stderr `dp-dice: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-dice subdir` where `subdir` is a directory →
`dp-dice: subdir: Is a directory`. _(UR-10)_

**FR-16: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and nothing else is
written.
_AC:_ `dp-dice --help` matches the user manual exactly; `dp-dice --seed=abc --help` also prints
it, because option values are checked only after the scan. _(UR-12)_

**FR-17: Version.**
`--version` MUST write `dp-dice (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
_AC:_ exact match. _(UR-12)_

**FR-18: Usage errors.**
Unknown options, a missing SEED (`--seed` as the last argument), and arguments supplied to
options that take none (`--prompt=…`, `--help=…`, `--version=…`), MUST be reported with the
CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be
abbreviated (CONV-08): `--se` is unrecognized. A second operand MUST be reported as
`dp-dice: extra operand '<second operand>'`, and an invalid SEED as in FR-14, after the whole
argument list has been scanned (CONV-12); when both occur, the extra operand is reported.
_AC:_ `dp-dice -x --help` → `dp-dice: invalid option -- 'x'`; `dp-dice --prompt=1` →
`dp-dice: option '--prompt' doesn't allow an argument`; `dp-dice --seed` →
`dp-dice: option '--seed' requires an argument`; `dp-dice -p - extra` →
`dp-dice: extra operand 'extra'`; each followed by the CONV-14 line, exit 2. _(UR-12, UR-13)_

**FR-19: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output.
_AC:_ stdout is empty in every exit-2 case; `dp-dice -p - extra < play.txt` writes no prompt.
_(UR-12)_

## 5. Non-functional requirements

| ID     | Category                                             | Requirement                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Verification                                          |
| :----- | :--------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------------------------------------------------- |
| NFR-01 | Portability                                          | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | CI black-box tests on 3 OSes                          |
| NFR-02 | Cross-platform focus: reproducible pseudo-randomness | The generator MUST be implemented exactly as CONV-38 states, in unsigned 32-bit modular arithmetic (or wider arithmetic reduced modulo 2³² after every step), on every platform and in every language; the C library's `rand()`, a language's built-in random module, the clock, and process identifiers MUST NOT be used, because their sequences differ between platforms and runs. Implementations in languages without unsigned 32-bit integers MUST avoid signed overflow and floating-point arithmetic in the generator. The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03), and standard output MUST be flushed as FR-12 requires even when it is a pipe or a file. | CI black-box tests on 3 OSes; unit tests; code review |
| NFR-03 | Performance                                          | Playing 100 000 rounds from a response file MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of rounds. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Measurement                                           |
| NFR-04 | Robustness                                           | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Unit + black-box tests                                |
| NFR-05 | Maintainability                                      | Option parsing, the incremental tokenizer, the generator, the dice, the round state machine, bet validation, and I/O MUST be separate units. The generator MUST be a unit with an explicit state, created from the seed (no global state). The constants 500, 250, 7, 11, 2, and 12 MUST each be defined once, by name.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Design review                                         |
| NFR-06 | Testability                                          | The generator MUST be unit-tested against the known draws of FR-03; the round MUST be testable with a scripted sequence of rolls, independent of the generator, and unit tests MUST cover a natural 7 and 11, a mark won and lost by 7 and by 11, a double mark won and lost, and a mark of 2 followed by 12. Bet validation MUST be a pure function tested at 0, 1, 250, 251, the bankroll, and the bankroll + 1.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    | Code review                                           |
| NFR-07 | Build                                                | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | CI                                                    |
| NFR-08 | Security                                             | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Inspection                                            |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-dice --help' for more information.`

| Trigger                                                   | Exact first line                                                                      |
| :-------------------------------------------------------- | :------------------------------------------------------------------------------------ |
| Unknown short option `x`                                  | `dp-dice: invalid option -- 'x'`                                                      |
| Unknown or abbreviated long option token `T`              | `dp-dice: unrecognized option 'T'`                                                    |
| `--seed` without a value                                  | `dp-dice: option '--seed' requires an argument`                                       |
| `--prompt=…`, `--help=…`, `--version=…`                   | `dp-dice: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X`                                      | `dp-dice: extra operand 'X'`                                                          |
| SEED value `V` that is not 0 … 4294967295 in ASCII digits | `dp-dice: invalid argument 'V' for '--seed'`                                          |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger                                                                                   | Exact message                           |
| :---------------------------------------------------------------------------------------- | :-------------------------------------- |
| FILE `F` does not exist                                                                   | `dp-dice: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied                                | `dp-dice: F: Permission denied`         |
| FILE `F` is a directory                                                                   | `dp-dice: F: Is a directory`            |
| A component of FILE `F` is not a directory                                                | `dp-dice: F: Not a directory`           |
| Any other open or read failure of FILE `F`                                                | `dp-dice: F: Input/output error`        |
| Any of the above for standard input                                                       | the same message with `F` = `-`         |
| Play answer or bet token `K` on line `L` of source `S` is not a valid _integer_           | `dp-dice: S:L: invalid integer 'K'`     |
| Play answer token `K` on line `L` of source `S` is a valid _integer_ other than 0 and 1   | `dp-dice: S:L: value out of range 'K'`  |
| The input of source `S` ends where a bet is expected; `L` is the end-of-input line number | `dp-dice: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe)                              | `dp-dice: write error`                  |

Refused bets (FR-06) are not diagnostics: they are written to standard output and do not change
the exit status. When `--prompt` is given, a data diagnostic follows the last prompt on the same
line of standard error (FR-13).

## 7. Verification

| Method                                                                                                | Applies to                                         |
| :---------------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| Black-box test (public, `tests/public/`, 10 cases; cases 02 and 03 have two steps)                    | FR-01 … FR-11, FR-13, FR-14, FR-16, FR-18, FR-19   |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 03, 05, and 07 … 10 have several steps) | FR-02 … FR-19                                      |
| Unit test (written by the implementer)                                                                | FR-03, FR-06 … FR-09, NFR-06                       |
| Measurement                                                                                           | NFR-03                                             |
| Inspection / review                                                                                   | FR-12 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command                                                            | Verifies                                                                      |
| :--- | :----------------------------------------------------------------- | :---------------------------------------------------------------------------- |
| 01   | `dp-dice < play.txt`                                               | FR-01, FR-03 (default seed), FR-04, FR-08 (mark won), FR-09, FR-10 (quit)     |
| 02   | `dp-dice --seed=6 < once.txt`; `dp-dice --seed=4 < once.txt`       | FR-07 (natural 7, natural 11), FR-14                                          |
| 03   | `dp-dice --seed=14 < double.txt`; `dp-dice --seed 68 < double.txt` | FR-07, FR-08 (double mark 2 and 12 won, payout 2 × bet)                       |
| 04   | `dp-dice --seed=2 < broke.txt`                                     | FR-08 (lost by 7 and by 11), FR-09, FR-10 (broke, remaining input ignored)    |
| 05   | `dp-dice --prompt --seed=8 < once.txt`                             | FR-13, FR-08 (lost by 11)                                                     |
| 06   | `dp-dice --seed=5 refusals.txt`                                    | FR-06 (all three refusals, re-prompt alignment, bet equal to bankroll), FR-10 |
| 07   | `dp-dice` (empty standard input)                                   | FR-04, FR-10 (end of input at the play question)                              |
| 08   | `dp-dice badbet.txt`                                               | FR-11 (output kept, CONV-34)                                                  |
| 09   | `dp-dice --help`                                                   | FR-16                                                                         |
| 10   | `dp-dice --seed=abc`                                               | FR-14, FR-18, FR-19                                                           |

## 8. Traceability (URD → SRS)

| User requirement | System requirements                     |
| :--------------- | :-------------------------------------- |
| UR-01            | FR-04, FR-05, FR-09                     |
| UR-02            | FR-06                                   |
| UR-03            | FR-06, FR-13                            |
| UR-04            | FR-03, FR-07, FR-08                     |
| UR-05            | FR-04, FR-07, FR-08, FR-09              |
| UR-06            | FR-10                                   |
| UR-07            | FR-03, FR-14, NFR-02, CONV-38           |
| UR-08            | FR-01, FR-02, FR-04, CONV-26            |
| UR-09            | FR-12, FR-13, CONV-36                   |
| UR-10            | FR-11, FR-15, CONV-16, CONV-33, CONV-34 |
| UR-11            | FR-02, NFR-02, CONV-37                  |
| UR-12            | FR-16, FR-17, FR-18, FR-19              |
| UR-13            | NFR-01, NFR-02, CONV-03, CLI-CONV       |
| UR-14            | NFR-03, NFR-07                          |
