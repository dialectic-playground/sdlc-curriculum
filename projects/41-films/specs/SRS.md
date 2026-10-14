# Software Requirements Specification (SRS) — dp-films

| Field | Value |
| :-- | :-- |
| Document ID | SRS-41 |
| Project | `41-films` — 1-Nearest Neighbor Film Success Classifier |
| Product | `dp-films` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-41) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-films`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-films` reads a sample set of 1 to 100 films, each given by a director percentage, a cast
percentage, and an outcome code, and validates all of it. It then reads queries — pairs of
percentages — from standard input or from one file until the end of the input, and for each
query writes one verdict line: the outcome of the sample film nearest to the query in squared
Euclidean distance, computed in IEEE 754 binary64 arithmetic, the first such film winning a
tie. It can write prompts to standard error before each value is read. It reports invalid
sample sets and queries with their line numbers and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| SAMPLE | The value of `-s`/`--sample`, or `films.dat` if neither is given |
| Sample input | The byte sequence read from the file SAMPLE, or from standard input when SAMPLE is `-` |
| Sample source | The name used for the sample input in diagnostics: SAMPLE exactly as given (so `-` for standard input) |
| Query input | The byte sequence read from the FILE operand, or from standard input when there is no operand or it is `-` |
| Query source | The name used for the query input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read |
| Token, line number, end-of-input line number | As defined in CONV-32 |
| Percentage | The value *v* of a token that is a valid *real* (CONV-33), that is, the binary64 value nearest to its decimal value, with 0 ≤ *v* ≤ 100. `-0` (negative zero) satisfies this and behaves as 0 in every computation. |
| Code | The value of a token that is a valid *integer* (CONV-33) equal to 0 or 1 |
| Film | A record of the sample set: a director percentage *D*, a cast percentage *C*, and a code *K* (1 = hit, 0 = flop) |
| Sample set | The films of the sample input, in input order, numbered 1, 2, … |
| Query | A director percentage *d* followed by a cast percentage *c* in the query input |
| Verdict | The line `The film is a HIT!` or `The film is a flop.`, followed by LF |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |

### 1.4 References
- URD-41: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- IEEE 754-2019, *Standard for Floating-Point Arithmetic* (binary64, round to nearest, ties to
  even)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §9.2 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-films` is a standalone executable. Its interfaces are the command line, the sample file or
standard input, the query file or standard input, standard output, standard error, and the
exit status. It belongs to the curriculum's applications-programming track (Projects 11–52) and
adapts §9.2 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read the sample set (`films.dat` by default) and validate all of it before any query.
2. Read queries until the end of the query input.
3. Classify each query by its nearest sample film, with a fixed tie-breaking rule.
4. Write one verdict per query as soon as the query has been read.
5. Optionally write prompts to standard error before each value is read.
6. Report invalid sample sets, invalid queries, and unreadable files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Distances MUST be computed in IEEE 754 binary64 arithmetic exactly as FR-05 prescribes.

### 2.4 Assumptions
- The current working directory is where the default sample file `films.dat` is looked for;
  relative paths are relative to it.
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-07.
- Nothing writes the sample file or the query file while the tool runs.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §9.2 asks at the keyboard for the name of the file that holds the
sample set, reads up to 100 films from it (director percentage, cast percentage, and code),
and then repeatedly asks for the two percentages of a film to classify, until end-of-file. For
each film it finds the sample film with the smallest squared Euclidean distance, keeping the
first one found when distances are equal, and prints `The film is a HIT!` or
`The film is a flop.`. `dp-films` keeps:

- the 1-nearest-neighbor rule, the squared Euclidean distance, and the tie-breaking rule (the
  first sample film at the minimum distance wins);
- the sample-set format (three whitespace-separated values per film; line structure has no
  meaning, so the two blank lines that begin `films.dat` are harmless), the limit of 100 films,
  and the codes 1 = hit and 0 = flop;
- the query order (director, then cast), reading until the end of the input, and the two
  verdict texts exactly;
- the two value prompts, word for word, as the optional prompts of FR-08.

It changes the following, for the reasons given:

- **The sample file is named by an option, not typed in.** The textbook's first keyboard
  response is a file name. Mixing a file name into the query stream would make query files and
  pipelines awkward, and the name could not be distinguished from a malformed percentage.
  `dp-films` takes the name from `-s`/`--sample`, with the textbook's file `films.dat` as the
  default, so the query input contains only percentages. The textbook's file-name prompt
  (`Enter name of file containing the sample set:`) therefore has no counterpart.
- **Prompts are optional and go to standard error** (CONV-36), so standard output holds only
  the verdicts. The blank lines the textbook printed before each prompt and each verdict only
  separated its output from the echo of the user's typing; they are not written.
- **The sample set is validated** (FR-02): a value that is not a number, a percentage outside
  0 … 100, a code other than 0 or 1, an incomplete last film, more than 100 films, and an empty
  sample set are diagnosed with line numbers. The textbook stopped reading silently at the
  first value it could not read, or after 100 films, and classified against an empty sample
  set without complaint.
- **Queries are validated** (FR-09), and a query whose cast percentage is missing is
  diagnosed instead of being classified with a stale value.
- **The arithmetic is specified exactly** (FR-05). The textbook used C's `float`, whose
  precision and evaluation depend on the compiler and processor. Two distances that are equal
  in decimal arithmetic can differ in binary floating point, which decides ties; binary64 with
  a fixed order of operations makes every verdict reproducible.
- **Input sources.** Queries may come from one FILE operand as well as standard input; CRLF line
  endings and a trailing Ctrl-Z marker are accepted in both inputs (FR-02, FR-04).
- **Streaming is required.** Each verdict is written and flushed before more input is read
  (FR-07), so the tool answers immediately at a keyboard even when its output is a pipe.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Of the conventions
for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Both inputs are read as tokens, with its line numbers (FR-02, FR-04). |
| CONV-33 | Percentages use the *real* grammar, restricted to 0 … 100; codes use the *integer* grammar, restricted to 0 and 1. |
| CONV-34 | All data errors use its format, with the standard messages and two further messages for the sample set (FR-02, FR-09). Verdicts already written are kept. |
| CONV-35 | Not applicable: no real number is written. |
| CONV-36 | `-p`, `--prompt` with the two prompts of FR-08. |
| CONV-37 | Both inputs are *text data*. |
| CONV-38 | Not applicable: nothing is random. |

Standard input is read as permitted by CONV-26. `dp-films` copies no input bytes to its output,
so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-films [-s FILE | --sample=FILE] [-p | --prompt] [FILE]
dp-films --help
dp-films --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-s` | `--sample` | FILE (required) | `films.dat` | Read the sample set from FILE; `-` is standard input (FR-01) |
| `-p` | `--prompt` | none | off | Write the prompts of FR-08 to standard error |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, `-sFILE`, `--sample FILE`, `--`, repetition, and scan order) follows
CONV-07 … CONV-12. If `-s` is repeated, the last occurrence wins; giving `-p` more than once has
the same effect as giving it once (CONV-11). FILE may begin with `-` when it is attached
(`--sample=-x`, `-s-x`) or supplied as the next token (`-s -x`).

### 3.3 Operands
At most one FILE operand, naming the query input. The operand `-` denotes standard input
(CONV-10). Every token after `--` is an operand, even if it begins with `-`. The operand is used
and echoed exactly as given (CONV-19).

### 3.4 Standard input
Read as the sample input when SAMPLE is `-`, or as the query input when there is no operand or
the operand is `-`; never both (FR-14). Read as raw bytes; no newline translation of any kind is
performed on any platform.

### 3.5 Standard output
The verdicts (FR-06), one per query, in query order. Nothing else. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-11 … FR-15 instead.

### 3.6 Standard error
Prompts (FR-08, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every query of the query input was classified (including an empty query input), or `--help` / `--version` was handled |
| 1 | A file could not be opened or read (FR-10), the sample set was invalid (FR-02), a query was invalid or incomplete (FR-09), or standard output could not be written |
| 2 | Usage error (FR-13, FR-14) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\r` CR, and `\t` TAB, and the following are public
fixture files in `tests/fixtures/`: `films.dat` is the textbook's sample set (two empty lines,
then 20 films, one per line: `10.0 20.0 0`, `10.0 30.0 0`, `20.0 50.0 0`, `20.0 60.0 1`,
`30.0 10.0 0`, `40.0 10.0 0`, `40.0 40.0 0`, `40.0 60.0 0`, `40.0 70.0 1`, `60.0 30.0 0`,
`60.0 60.0 1`, `60.0 70.0 0`, `70.0 30.0 0`, `70.0 60.0 1`, `70.0 70.0 1`, `70.0 90.0 1`,
`80.0 80.0 1`, `90.0 30.0 1`, `90.0 50.0 0`, `90.0 70.0 1`); `readme.txt` is
`75.0 85.0\n10.0 15.0\n90.0 70.0\n`; `queries.txt` is
`50 65\r\n65\t65\r\n+20 6e1\r\n0 0   100 100\r\n55.5 .5\r\n`; `pair.dat` is
`40 60 1\n60 40 0\n`; `center.txt` is `50 50\n45 55\n55 45\n`; `bad-query.txt` is
`75 85\n10 15\n90 seventy\n80 80\n`; `bad-code.dat` is `10 20 0\n20 60 1\n30 10 2\n`. `H` and `F`
denote the verdicts `The film is a HIT!\n` and `The film is a flop.\n`.

**FR-01: Sample-set source.**
If SAMPLE is `-`, the tool MUST read standard input to its end as the sample input. Otherwise it
MUST open the file SAMPLE (a path relative to the current directory unless absolute) and read it
to its end as raw bytes. Without `-s`/`--sample`, SAMPLE is `films.dat`. The whole sample input
is read and validated (FR-02) before the query input is opened, before any prompt is written,
and before any verdict is written.
*AC:* `dp-films < readme.txt` → stdout `H F H`, exit 0;
`dp-films -s - readme.txt < films.dat` → the same. *(UR-01)*

**FR-02: Sample-set format and validation.**
The sample input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the
very end of it is ignored. The rest is divided into tokens (CONV-32). Line structure has no
meaning: tokens may be separated by any mixture of space, TAB, VT, FF, CR, and LF. Tokens 1, 2,
and 3 form film 1, tokens 4, 5, and 6 form film 2, and so on: the first token of a film is its
director percentage *D*, the second its cast percentage *C*, and the third its code *K*. The
films are checked in input order, and within a film in the order *D*, *C*, *K*; the first
problem found is reported:

1. If the film would be the 101st, the tool MUST report `too many films (limit 100)` at the
   line of the film's first token, before the film's values are checked.
2. A *D* or *C* token that is not a valid *real* is reported as `invalid number '<token>'`;
   a valid *real* whose binary64 value lies outside 0 … 100 as `value out of range '<token>'`.
3. A *K* token that is not a valid *integer* (including `1.0`) is reported as
   `invalid integer '<token>'`; a valid *integer* other than 0 and 1 as
   `value out of range '<token>'`.
4. If the sample input ends after the first or second token of a film, the tool MUST report
   `unexpected end of input` at the end-of-input line number.
5. If the sample input contains no token at all, the tool MUST report
   `no films in the sample set` at the end-of-input line number.

Each problem is written as `dp-films: <sample source>:<line>: <message>` (CONV-34), with
`<line>` the line number of the offending token unless stated otherwise. The tool then exits
with status 1 without opening the query input, writing a prompt, or writing anything to
standard output. A percentage is compared with 0 and 100 after conversion to binary64: `1e2`
and `100.000` are valid, `100.5` is not.
*AC:* `dp-films -s bad-code.dat < readme.txt` → stdout empty, stderr
`dp-films: bad-code.dat:3: value out of range '2'\n`, exit 1. A sample set of 100 films is
accepted; one of 101 films whose 101st film starts on line 101 gives
`dp-films: over.dat:101: too many films (limit 100)`. An empty file `empty.dat` gives
`dp-films: empty.dat:1: no films in the sample set`; a file holding only `\n \r\n\t` and a
`0x1A` byte gives the same message at line 3. `10 20 0\n30 40\n` gives
`unexpected end of input` at line 3; `1.0` as a code gives `invalid integer '1.0'`.
*(UR-07, UR-09)*

**FR-03: Query source.**
If no operand is given, or the operand is `-`, the query input is standard input. Otherwise the
tool MUST open the file named by the operand and read it as raw bytes. The query input is
opened after the sample set has been validated (FR-01) and before the first prompt is written.
More than one operand is a usage error (FR-13).
*AC:* `dp-films readme.txt`, `dp-films - < readme.txt`, and `dp-films < readme.txt` write the
same verdicts; `dp-films -s missing.dat missing.txt` reports only `missing.dat`. *(UR-04)*

**FR-04: Queries.**
The query input is *text data* (CONV-37) and is divided into tokens (CONV-32); line structure
has no meaning. Tokens 1 and 2 form query 1, tokens 3 and 4 form query 2, and so on: the first
token of a query is its director percentage *d*, the second its cast percentage *c*. Each token
MUST be a percentage (section 1.3); otherwise FR-09 applies. Reaching the end of the query
input where a director percentage would be read ends the run normally with exit status 0; an
empty query input therefore produces no output. Reaching it where a cast percentage would be
read is an error (FR-09).
*AC:* `dp-films queries.txt` → stdout `F H H F H F`, exit 0 (the queries are (50, 65), (65, 65),
(20, 60), (0, 0), (100, 100), and (55.5, 0.5)). `dp-films` with empty standard input → stdout
and stderr empty, exit 0. *(UR-02, UR-04, UR-09)*

**FR-05: Nearest-neighbor rule.**
For a query (*d*, *c*) and the films (*D*ᵢ, *C*ᵢ, *K*ᵢ), *i* = 1 … *n*, of the sample set, the
tool MUST compute for each film, in IEEE 754 binary64 arithmetic with every operation rounded to
nearest, ties to even:

1. *a* = *d* − *D*ᵢ, then *b* = *c* − *C*ᵢ;
2. *s*ᵢ = (*a* × *a*) + (*b* × *b*), where each product is rounded to binary64 before the sum,
   and the sum is rounded to binary64.

The computation MUST NOT use a fused multiply-add, extended or reduced precision, or any
reordering, and MUST NOT take a square root (rounding the root could turn two different
values into a tie). The nearest film is the film *k* with the smallest *s*ₖ; if several films share the
smallest value, *k* is the one that comes first in the sample set. The query's code is *K*ₖ.
Equivalently: scan the films in order and replace the current best only when *s*ᵢ is strictly
smaller. Because the values are rounded, two distances that are equal in decimal arithmetic can
differ: for the query (0.2, 0) and the films (0.1, 0, 1) and (0.3, 0, 0), *s*₁ =
0.010000000000000002 and *s*₂ = 0.009999999999999995, so the code is 0. A query equal to a
sample film has distance 0 to it. All values lie in 0 … 100, so no result overflows or is NaN.
*AC:* (75, 85) → `H` (the films (70, 90, 1) and (80, 80, 1) are both at 50); (10, 15) → `F`
(nearest (10, 20, 0), at 25); (90, 70) → `H` (an exact match); (50, 65) → `F` (the films
(40, 60, 0), (40, 70, 1), (60, 60, 1), and (60, 70, 0) are all at 125, and (40, 60, 0) comes
first); with `pair.dat`, `center.txt` gives `H H F`, and with its two films swapped, the first
query gives `F`. *(UR-03, UR-12)*

**FR-06: Verdicts.**
For each query the tool MUST write exactly one verdict to standard output: `The film is a HIT!`
followed by LF if the query's code is 1, and `The film is a flop.` followed by LF if it is 0.
There are no blank lines, headers, summaries, or other spaces.
*AC:* `dp-films < readme.txt` → stdout
`The film is a HIT!\nThe film is a flop.\nThe film is a HIT!\n`. *(UR-02, UR-04)*

**FR-07: Streaming.**
Queries MUST be processed one at a time, in input order. As soon as the cast percentage's token
is complete (section 1.3) and valid, the tool MUST write the verdict and flush standard output
before it waits for any further input bytes. It MUST NOT wait for the end of the query input
before writing a verdict, and MUST NOT read the query input beyond what it needs to complete the
current token, apart from ordinary buffering of bytes that are already available.
*AC:* at a terminal, typing `75 85` and Enter shows `The film is a HIT!` before anything else is
typed (manual check). *(UR-05)*

**FR-08: Prompts.**
`-p`, `--prompt` enables two prompts. P1 is the 116 bytes

```text
Enter the percentage of hits of the
director of the film to be classified or
generate EOF to terminate the program: 
```

that is, three lines, the first two ending in LF, the third ending in `: ` (colon and one space)
with no LF. P2 is the 94 bytes

```text
Enter the percentage of hits of the
leading members of the cast of the film
to be classified: 
```

likewise ending in `: ` with no LF. With prompts enabled, the tool MUST write P1 to standard
error, and flush it, immediately before each attempt to read a director percentage, and P2
immediately before each attempt to read a cast percentage. A prompt is also written before the
attempt that reaches the end of the input (CONV-36): a query input with *n* complete valid
queries produces P1 *n* + 1 times and P2 *n* times, alternating P1, P2, P1, …, P1. A diagnostic
of FR-09 follows the last prompt directly, on the same line. No prompt is written when the
sample set or the query input cannot be read or the sample set is invalid. Prompts never change
standard output.
*AC:* `dp-films --prompt < readme.txt` → stdout as in FR-06; stderr P1 P2 P1 P2 P1 P2 P1, exit
0. `dp-films --prompt odd.txt`, where `odd.txt` is `75 85\n10\n` → stdout `H`, stderr
P1 P2 P1 P2 `dp-films: odd.txt:3: unexpected end of input\n`, exit 1. *(UR-06)*

**FR-09: Invalid queries.**
If a query token is not a valid *real*, the tool MUST write
`dp-films: <query source>:<line>: invalid number '<token>'`; if it is a valid *real* whose
binary64 value lies outside 0 … 100, `dp-films: <query source>:<line>: value out of range
'<token>'`, with `<line>` the token's line number. If the query input ends after a director
percentage, the tool MUST write `dp-films: <query source>:<line>: unexpected end of input`, with
`<line>` the end-of-input line number. `<token>` is the token's exact bytes (CONV-34). The tool
then stops: it reads no further input, writes no further verdict, and exits with status 1.
Verdicts already written for earlier queries are kept (CONV-34).
*AC:* `dp-films bad-query.txt` → stdout `H F`, stderr
`dp-films: bad-query.txt:3: invalid number 'seventy'\n`, exit 1. A query token `101` gives
`value out of range '101'`; `-0` and `1e2` are valid; a token `85` followed by a `0x1A` byte and
an LF gives `invalid number`, because that Ctrl-Z byte does not end the input. *(UR-08)*

**FR-10: Unreadable input.**
If SAMPLE or the FILE operand does not exist, cannot be opened, is a directory, or a read error
occurs, the tool MUST write `dp-films: <name>: <reason>`, where `<name>` is SAMPLE or the
operand exactly as given (`-` for standard input) and `<reason>` is from the CONV-16 table, and
exit with status 1. The sample input is read first, so its failure is the one reported when
both fail. Verdicts already written are kept.
*AC:* `dp-films -s missing.dat readme.txt` → stderr
`dp-films: missing.dat: No such file or directory\n`, stdout empty, exit 1;
`dp-films subdir`, where `subdir` is a directory → `dp-films: subdir: Is a directory`. *(UR-07,
UR-08)*

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-films --help` matches the user manual exactly; `dp-films extra --help` also prints it.
*(UR-10)*

**FR-12: Version.**
`--version` MUST write `dp-films (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-13: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--prompt=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages followed by
the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--samp`
is unrecognized. After the whole argument list has been scanned (CONV-12), the tool checks, in
this order: a second operand, reported as `dp-films: extra operand '<second operand>'`; then
the winning value of `-s`/`--sample` (CONV-11), which is invalid if it is empty or if FR-14
forbids it, reported as `dp-films: invalid argument '<value>' for '<option>'`, where
`<option>` is `-s` or `--sample` as the user wrote it.
*AC:* `dp-films readme.txt queries.txt` → `dp-films: extra operand 'queries.txt'`;
`dp-films -s ''` → `dp-films: invalid argument '' for '-s'`; `dp-films --sample` →
`dp-films: option '--sample' requires an argument`; `dp-films -x --help` →
`dp-films: invalid option -- 'x'`; `dp-films --prompt=1` →
`dp-films: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-14: Standard input used once.**
Standard input can supply the sample input or the query input, not both. If SAMPLE is `-` and
the query input is standard input (no operand, or the operand `-`), the tool MUST report
`dp-films: invalid argument '-' for '<option>'` as a usage error (FR-13).
*AC:* `dp-films -s -` and `dp-films -s - -` → `dp-films: invalid argument '-' for '-s'`, exit 2;
`dp-films --sample=- readme.txt < films.dat` is valid. *(UR-11)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any file, read standard input, write a prompt,
or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: reproducible floating-point arithmetic | Every verdict MUST be the same on every operating system, processor, compiler, and runtime. Decimal-to-binary conversion MUST be correctly rounded (CONV-33), not a hand-written digit loop that accumulates error. FR-05 MUST be evaluated in binary64 with each operation rounded separately: implementations MUST disable fused multiply-add contraction (for example C's `-ffp-contract=off` or the language's equivalent), MUST NOT use x87 80-bit intermediates or single precision, and MUST NOT let an optimizer reassociate the sum. Both inputs MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte never ends an input early at the I/O layer. At an interactive console the platform's end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the query input normally. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Classifying 100 000 queries against a sample set of 100 films MUST take under 1 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of queries; only the sample set and the token being read are held. Start-up and exit for an empty query input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and numbers whose magnitude overflows binary64. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, sample-set loading and validation, the incremental query tokenizer, the classifier, prompting, and output MUST be separate units. The classifier MUST be one function that receives the sample set and a query and returns the code, with no input, output, or prompting; it is the only place the distance is computed. The sample set MUST be held in a collection of film records (one record type with three fields), not in parallel arrays (Principles 12, 13, 18). | Design review |
| NFR-06 | Testability | The classifier MUST be a pure function covered by unit tests, including every acceptance value of FR-05, an exact match, a tie between a hit and a flop in both orders, the binary64 example of FR-05, and the corners (0, 0) and (100, 100). Sample-set validation MUST be unit-tested for every message of FR-02, including 100 and 101 films. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only SAMPLE, the FILE operand, or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-films --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-films: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-films: unrecognized option 'T'` |
| `-s` without an argument | `dp-films: option requires an argument -- 's'` |
| `--sample` without an argument | `dp-films: option '--sample' requires an argument` |
| `--prompt=…`, `--help=…`, `--version=…` | `dp-films: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X` | `dp-films: extra operand 'X'` |
| Empty SAMPLE | `dp-films: invalid argument '' for '-s'` (or `'--sample'`, as written) |
| SAMPLE `-` while the queries are read from standard input | `dp-films: invalid argument '-' for '-s'` (or `'--sample'`, as written) |

Runtime errors (exit status 1; the tool stops at the first one). `S` is the sample source and
`Q` the query source (section 1.3); `L` is a line number, `K` a token's exact bytes.

| Trigger | Exact message |
| :-- | :-- |
| File `F` (SAMPLE or the operand) does not exist | `dp-films: F: No such file or directory` |
| File `F` cannot be opened or read because access is denied | `dp-films: F: Permission denied` |
| File `F` is a directory | `dp-films: F: Is a directory` |
| A component of the path `F` is not a directory | `dp-films: F: Not a directory` |
| Any other open or read failure of `F` | `dp-films: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| A 101st film starts on line `L` of the sample set | `dp-films: S:L: too many films (limit 100)` |
| A sample percentage token `K` is not a valid *real* | `dp-films: S:L: invalid number 'K'` |
| A sample percentage token `K` lies outside 0 … 100 | `dp-films: S:L: value out of range 'K'` |
| A code token `K` is not a valid *integer* | `dp-films: S:L: invalid integer 'K'` |
| A code token `K` is an integer other than 0 and 1 | `dp-films: S:L: value out of range 'K'` |
| The sample set ends inside a film (`L` = end-of-input line) | `dp-films: S:L: unexpected end of input` |
| The sample set has no token (`L` = end-of-input line) | `dp-films: S:L: no films in the sample set` |
| A query token `K` is not a valid *real* | `dp-films: Q:L: invalid number 'K'` |
| A query token `K` lies outside 0 … 100 | `dp-films: Q:L: value out of range 'K'` |
| The query input ends after a director percentage (`L` = end-of-input line) | `dp-films: Q:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe) | `dp-films: write error` |

When `--prompt` is given, a query diagnostic follows the last prompt on the same line of
standard error (FR-08).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-06, FR-08, FR-09, FR-11, FR-13, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 10 have several steps) | FR-01 … FR-06, FR-08 … FR-15 |
| Unit test (written by the implementer) | FR-02, FR-04, FR-05, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review / demonstration | FR-07 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-films < readme.txt` | FR-01 (default sample set), FR-04 … FR-06 (the README examples) |
| 02 | `dp-films queries.txt` | FR-03, FR-04 (CRLF, TAB, sign, exponent), FR-05 (tie: first wins) |
| 03 | `dp-films --prompt < readme.txt` | FR-08 |
| 04 | `dp-films -s pair.dat center.txt` | FR-01, FR-05 (tie between a hit and a flop) |
| 05 | `dp-films -s - readme.txt < films.dat` | FR-01, FR-14 (sample set from standard input) |
| 06 | `dp-films` (empty standard input) | FR-04 (empty query input) |
| 07 | `dp-films bad-query.txt` | FR-09 (verdicts kept, CONV-34) |
| 08 | `dp-films -s bad-code.dat < readme.txt` | FR-02 (validated before any query) |
| 09 | `dp-films --help` | FR-11 |
| 10 | `dp-films readme.txt queries.txt` | FR-13, FR-15 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01 |
| UR-02 | FR-04, FR-06 |
| UR-03 | FR-05 |
| UR-04 | FR-03, FR-04, FR-06, CONV-26 |
| UR-05 | FR-07, NFR-02 |
| UR-06 | FR-08, CONV-36 |
| UR-07 | FR-02, FR-10, CONV-34 |
| UR-08 | FR-09, FR-10, CONV-34 |
| UR-09 | FR-02, FR-04, NFR-02, CONV-37 |
| UR-10 | FR-11, FR-12 |
| UR-11 | FR-13, FR-14, FR-15 |
| UR-12 | FR-05, NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-13, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
