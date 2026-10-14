"""Reference implementation of dp-dice (projects/22-dice/specs/SRS.md).

The player's responses are read as tokens incrementally (CONV-32), so every message is
written, and standard output flushed, before the next response is read. The dice use the
CONV-38 generator: each roll draws the first die, then the second.
"""

from __future__ import annotations

from . import common
from .common import (PROMPT, AnsiRand, DataError, InputError, InputStream, Option,
                     UsageError, data_failure, file_failure, handle_action, open_input,
                     parse_args, parse_int_token, parse_seed, prompt, usage_failure)

TOOL = "dp-dice"
PLAY_PROMPT = "Want to play? (1: yes, 0: no) "
BET_PROMPT = "Enter your bet: "
NEST_EGG = 500
LIMIT = 250
HELP_TEXT = """\
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
"""

OPTIONS: list[Option] = [PROMPT, Option("seed", long="seed", takes_value=True)]


class Dice:
    def __init__(self, seed: int):
        self.rand = AnsiRand(seed)

    def roll(self) -> int:
        first = 1 + self.rand.next() % 6
        second = 1 + self.rand.next() % 6
        common.write(f"Roll: {first} + {second} = {first + second}\n")
        return first + second


def say(text: str) -> None:
    common.write(text + "\n")


def read_bet(tokens: InputStream, source: str, prompting: bool, bankroll: int) -> int:
    while True:
        common.out.flush()
        prompt(prompting, BET_PROMPT)
        bet = parse_int_token(tokens.require(source), source)
        if bet < 1:
            say("Bet refused: the minimum bet is $1.")
        elif bet > LIMIT:
            say(f"Bet refused: the table limit is ${LIMIT}.")
        elif bet > bankroll:
            say(f"Bet refused: you only have ${bankroll}.")
        else:
            return bet


def play_round(dice: Dice, bet: int) -> int:
    """Play one round; return the change to the bankroll."""
    mark = dice.roll()
    if mark in (7, 11):
        say(f"Natural! You win ${bet}.")
        return bet
    double = mark in (2, 12)
    say(f"Your mark is {mark}; it pays double." if double else f"Your mark is {mark}.")
    while True:
        total = dice.roll()
        if total == mark:
            payout = 2 * bet if double else bet
            say(f"You made your mark! You win ${payout}.")
            return payout
        if total in (7, 11):
            say(f"Out! You lose ${bet}.")
            return -bet


def game(tokens: InputStream, source: str, prompting: bool, dice: Dice) -> int:
    bankroll = NEST_EGG
    say(f"Your bankroll is ${bankroll}.")
    while True:
        common.out.flush()
        prompt(prompting, PLAY_PROMPT)
        token = tokens.token()
        if token is None or parse_int_token(token, source, 0, 1) == 0:
            break
        bet = read_bet(tokens, source, prompting, bankroll)
        say(f"You bet ${bet}.")
        bankroll += play_round(dice, bet)
        say(f"Your bankroll is ${bankroll}.")
        if bankroll == 0:
            say("You're broke! Better luck next time.")
            return 0
    say(f"Congratulations! You leave the table with ${bankroll}.")
    return 0


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
        seed = parse_seed(parsed)
    except UsageError as error:
        return usage_failure(TOOL, error)

    source = parsed.operands[0] if parsed.operands else "-"
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        return game(InputStream(handle), source, bool(parsed.values.get("prompt")),
                    Dice(seed))
    except DataError as error:
        common.out.flush()
        return data_failure(TOOL, error)
    except InputError as failure:
        common.out.flush()
        file_failure(TOOL, source, failure.error)
        return 1
    finally:
        if source != "-":
            handle.close()
