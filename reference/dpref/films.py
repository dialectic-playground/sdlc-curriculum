"""Reference implementation of dp-films (projects/41-films/specs/SRS.md).

The sample set is read and validated completely before the first query is read. Queries are
tokenized incrementally (CONV-32), so each classification is written, and standard output
flushed, as soon as the cast percentage's token is complete: the tool works interactively.
"""

from __future__ import annotations

from . import common
from .common import (PROMPT, DataError, InputError, InputStream, Option, Token, UsageError,
                     data_failure, end_line, file_failure, handle_action, invalid_argument,
                     open_input, parse_args, parse_int_token, parse_real_token, prompt,
                     read_all, strip_eof_marker, tokenize, unexpected_end, usage_failure)

TOOL = "dp-films"
DEFAULT_SAMPLE = "films.dat"
MAX_FILMS = 100
PROMPT_DIRECTOR = ("Enter the percentage of hits of the\n"
                   "director of the film to be classified or\n"
                   "generate EOF to terminate the program: ")
PROMPT_CAST = ("Enter the percentage of hits of the\n"
               "leading members of the cast of the film\n"
               "to be classified: ")
HIT = b"The film is a HIT!\n"
FLOP = b"The film is a flop.\n"
HELP_TEXT = """\
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
"""

OPTIONS = [Option("sample", short="s", long="sample", takes_value=True), PROMPT]


def percentage(token: Token, source: str) -> float:
    value = parse_real_token(token, source)
    if not 0.0 <= value <= 100.0:
        raise DataError(source, token.line, b"value out of range '" + token.text + b"'")
    return value


def load_sample(data: bytes, source: str) -> list[tuple[float, float, int]]:
    tokens = tokenize(data)
    films: list[tuple[float, float, int]] = []
    for start in range(0, len(tokens), 3):
        if len(films) == MAX_FILMS:
            raise DataError(source, tokens[start].line, f"too many films (limit {MAX_FILMS})")
        record = tokens[start:start + 3]
        director = percentage(record[0], source)
        if len(record) < 2:
            raise unexpected_end(source, data)
        cast = percentage(record[1], source)
        if len(record) < 3:
            raise unexpected_end(source, data)
        code = parse_int_token(record[2], source, 0, 1)
        films.append((director, cast, code))
    if not films:
        raise DataError(source, end_line(data), "no films in the sample set")
    return films


def classify(films: list[tuple[float, float, int]], director: float, cast: float) -> int:
    best_code = films[0][2]
    best = None
    for film_director, film_cast, code in films:
        dd = director - film_director
        dc = cast - film_cast
        distance = dd * dd + dc * dc  # binary64, each operation rounded, no fusion
        if best is None or distance < best:
            best, best_code = distance, code
    return best_code


def main(argv: list[str]) -> int:
    try:
        parsed = parse_args(argv, OPTIONS)
        if handle_action(TOOL, parsed, HELP_TEXT):
            return 0
        if len(parsed.operands) > 1:
            raise UsageError(f"extra operand '{parsed.operands[1]}'")
        sample = str(parsed.values.get("sample", DEFAULT_SAMPLE))
        source = parsed.operands[0] if parsed.operands else "-"
        if sample == "" or (sample == "-" and source == "-"):
            raise invalid_argument(sample, parsed.spelled["sample"])
    except UsageError as error:
        return usage_failure(TOOL, error)

    try:
        data = strip_eof_marker(read_all(sample))
    except OSError as error:
        file_failure(TOOL, sample, error)
        return 1
    try:
        films = load_sample(data, sample)
    except DataError as error:
        return data_failure(TOOL, error)

    prompting = bool(parsed.values.get("prompt"))
    try:
        handle = open_input(source)
    except OSError as error:
        file_failure(TOOL, source, error)
        return 1
    try:
        stream = InputStream(handle)
        while True:
            prompt(prompting, PROMPT_DIRECTOR)
            token = stream.token()
            if token is None:
                return 0
            director = percentage(token, source)
            prompt(prompting, PROMPT_CAST)
            cast = percentage(stream.require(source), source)
            common.write(HIT if classify(films, director, cast) == 1 else FLOP)
            common.out.flush()
    except DataError as error:
        return data_failure(TOOL, error)
    except InputError as error:
        file_failure(TOOL, source, error.error)
        return 1
    finally:
        if source != "-":
            handle.close()
