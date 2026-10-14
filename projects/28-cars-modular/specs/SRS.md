# Software Requirements Specification (SRS) — dp-cars2

| Field | Value |
| :-- | :-- |
| Document ID | SRS-28 |
| Project | `28-cars-modular` — Modular Car Sales Architecture & Reporting |
| Product | `dp-cars2` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-28) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-cars2`, and the decomposition its
design must follow (NFR-05). It is complete and precise enough that independent
implementations in any programming language produce **byte-identical** output, and
byte-identical totals files, for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-cars2` does everything `dp-cars1` (Project 26) does, with identical results: it reads the
opening stock of twelve car brands and then (brand, quantity) sales until a negative brand or
the end of the input, refuses impossible sales, and writes the `DAILY REPORT`. In addition, it
can save the day's totals to a file (`--save`) and can write the report from a file of totals
instead of from the sales (`--totals`). The report is produced by one independent component in
both cases.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number, end-of-input line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`; 1 plus the number of LF bytes before its first byte; 1 plus the number of LF bytes in the whole input |
| Brand | An integer *b* with 0 ≤ *b* ≤ 11. There are exactly 12 brands |
| Opening stock *S*<sub>*b*</sub> | The number of cars of brand *b* at the start of the day, 0 ≤ *S*<sub>*b*</sub> ≤ 999999 |
| Sales total *T*<sub>*b*</sub> | The number of cars of brand *b* sold during the day; in sales mode the sum of the quantities of the accepted sales of brand *b* |
| Totals | The 24 values *S*<sub>0</sub>, *T*<sub>0</sub>, …, *S*<sub>11</sub>, *T*<sub>11</sub> |
| Sales mode | The default mode: the input holds the opening stock and the sales (FR-04 … FR-06) |
| Totals mode | The mode selected by `-t`, `--totals`: the input holds the totals (FR-10) |
| Sale, sentinel, accepted sale, refused sale | As in sales mode: a brand token followed by a quantity token; a negative brand token, which ends the sales; a sale that passes the checks of FR-06; a sale that fails one of them |
| SAVE | The value of `-s`/`--save`, when given |
| Totals file | The file named by SAVE (FR-11), or a file with the same format read in totals mode |
| Report | The 14 lines of FR-07 |
| Report component | The design unit that produces the report from the totals (NFR-05) |
| Decimal | The plain ASCII decimal representation of an integer: a `-` for negative values only, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-28: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- SRS-26 (`projects/26-cars/specs/SRS.md`): the specification of `dp-cars1`, to which FR-01
  requires `dp-cars2`'s default behavior to be identical. FR-02 … FR-09 and FR-12 … FR-13 of
  this SRS restate SRS-26's requirements for sales mode, so that this SRS is complete on its
  own; they differ from SRS-26 only in the tool name and in the requirement numbers.
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §5.6 (and §5.3) (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-cars2` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, the totals file named by `--save`, standard output, standard
error, and the exit status. It belongs to the curriculum's applications-programming track
(Projects 11–52) and adapts §5.6 of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*:
the textbook's revision of the car-sales program of §5.3 (Project 26, `dp-cars1`), in which the
report is written by a separate function that is passed the two arrays.

### 2.2 Product functions
1. In sales mode, everything `dp-cars1` does, with byte-identical results (FR-01): read the
   opening stock and the sales, refuse impossible sales, write the daily report, and
   optionally prompt.
2. In totals mode, read the 24 totals and write the daily report from them.
3. Optionally save the totals the report was produced from to a totals file.
4. Report invalid tokens, incomplete or overlong input, unreadable input, and an unwritable
   totals file.
5. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior, and the decomposition of NFR-05.
- Stock and sales are counted in exact integer arithmetic. The percentage is computed in IEEE
  754 binary64 exactly as FR-08 prescribes.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-06 and FR-09.
- The current working directory is where a relative SAVE path is created.
- Nothing else writes the input or the totals file while the tool runs.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §5.6 is the program of §5.3 rewritten so that the daily report is
printed by a function that receives the stock array and the sales array as parameters; the
dialog and the report are unchanged. `dp-cars2` keeps:

- everything `dp-cars1` keeps from §5.3 (see SRS-26 §2.5), and every change `dp-cars1` makes
  to it, unchanged: the same dialog, prompts, refused sales, report layout, `n/a`, limits, and
  diagnostics (FR-01);
- the essential point of §5.6, the separation of the report from the dialog, as a design
  requirement (NFR-05): one component receives the two collections, may not modify them, and
  is the only place that knows the report's layout.

It adds the following, for the reasons given:

- **`--totals`** (FR-10). The section's description asks that the report be "independently
  invokable", for example from a unit test, without user input. `--totals` makes that
  observable at the command line: the report component is fed from a second source, a file of
  totals, without the dialog being involved at all. This capability only makes sense because
  the report depends on nothing but the totals.
- **`--save`** (FR-11). It writes exactly the totals the report was produced from, in the
  format `--totals` reads, so a report can be reproduced later byte for byte (a round trip
  that the tests check).
- **Prompts** are those of `dp-cars1` in sales mode; totals mode has none, because a totals
  file is a saved record, not a keyboard dialog (FR-09).

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full. From section 10 it incorporates: CONV-32 (the input is
read as tokens; line numbers), CONV-33 (every token uses the *integer* grammar; opening stocks
are restricted to 0 … 999999 and, in totals mode, sales totals to 0 … *S*<sub>*b*</sub>),
CONV-34 (data diagnostics, with the standard messages `invalid integer`, `value out of range`,
and `unexpected end of input`, plus the three refused-sale messages of FR-06 and the message
`extra data` of FR-10), CONV-35 (`FIX(x, 6)` for the percentage), CONV-36 (`-p`, `--prompt`,
in sales mode), and CONV-37 (the input is *text data* in both modes). CONV-38 does not apply,
because nothing is random.

There is **one override**, the same as in SRS-26: the three refused-sale diagnostics of FR-06
use the CONV-34 format but do **not** end processing; the report is still written and the exit
status is 1, consistent with CONV-18. The exit-status table is CONV-18's. Option syntax follows
CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16 (CONV-16 is applied to the totals file
as well as the input), and standard input is read as permitted by CONV-26. `dp-cars2` copies no
input bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-cars2 [-p | --prompt] [-t | --totals] [-s FILE | --save=FILE] [FILE]
dp-cars2 --help
dp-cars2 --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | off | Write the prompts of FR-09 to standard error before each read (sales mode only) |
| `-s` | `--save` | FILE (required) | none | After the report, write the totals to FILE, replacing its contents (FR-11) |
| `-t` | `--totals` | none | off | Totals mode: read the 24 totals instead of the stock and the sales (FR-10) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling such as `-tp`, `-sFILE`, `--save FILE`, `--`, repetition, and scan
order) follows CONV-07 … CONV-12. Repeating a flag has the same effect as giving it once; if
`--save` is repeated, the last occurrence wins (CONV-11). SAVE may begin with `-` when it is
attached (`--save=-x`, `-s-x`) or supplied as the next token (`-s -x`). A SAVE that is empty or
exactly `-` is an invalid option value (FR-16).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-02). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The report (FR-07), written once, after the input has been consumed, and only if no error of
FR-12 or FR-13 occurred. Nothing else; in particular the totals are never written to standard
output. On a usage error, or when `--help` / `--version` is handled, the output is as specified
by FR-14 … FR-17 instead.

### 3.6 Standard error
Prompts (FR-09, only with `--prompt` in sales mode), refused-sale diagnostics (FR-06), and the
other diagnostics of section 6.

### 3.7 Files
- The input file is opened for reading only.
- The totals file SAVE is created if it does not exist, or truncated and rewritten if it does,
  only in step 4 of FR-11. No other file is created, and no file is deleted or renamed.

### 3.8 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The report was written, no sale was refused, and the totals file (if requested) was written; or `--help` / `--version` was handled |
| 1 | The report was written but at least one sale was refused (FR-06) or the totals file could not be written (FR-11); or no report was written because the input could not be opened or read (FR-13) or its content was invalid, incomplete, or overlong (FR-12); or standard output could not be written |
| 2 | Usage error (FR-16) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\t` denotes TAB, and the following are public fixture
files in `tests/fixtures/`. `day.txt`, `rejected.txt`, and `cut.txt` are byte-for-byte the
files of the same names in Project 26 (described in SRS-26 §4); each begins with the line
`15 8 20 4 0 12 7 30 3 10 25 6\n`. `totals.tot` holds the totals of `day.txt`, one brand per
line with a TAB between the two values: `15\t5\n8\t0\n20\t5\n4\t4\n0\t0\n12\t0\n7\t2\n30\t10\n3\t1\n10\t0\n25\t1\n6\t0\n`.
`oversold.tot` is the same with spaces instead of TABs, except that line 4 is `4 5`.
`R` denotes the report of `day.txt`, given in full in FR-07.

**FR-01: Compatibility with dp-cars1.**
For every argument list made only of `-p`/`--prompt` (in any of the spellings CONV-07 …
CONV-11 allow), `--`, and operands — that is, every argument list that `dp-cars1` accepts,
other than `--help` and `--version` — and for every input, `dp-cars2` MUST produce the same
standard output bytes and the same exit status as `dp-cars1` (SRS-26), and the same standard
error bytes after each occurrence of the canonical name `dp-cars1` at the start of a
diagnostic line (including the CONV-14 line) is replaced by `dp-cars2`. This includes the
prompts, the refused-sale diagnostics and their timing, the report, and every error case.
FR-02 … FR-09, FR-12, and FR-13 restate the requirements this implies. A difference between
them and SRS-26 other than the tool name is a defect of this SRS.
*AC:* public tests 01, 02, 03, and 08 use the inputs and options of Project 26's public tests
01, 03, 04, and 06; their expected standard output and exit status are byte-identical to
Project 26's, and their expected standard error is identical after the name substitution.
Hidden test 09 does the same for three of Project 26's hidden cases. *(UR-01)*

**FR-02: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. This applies in both modes.
The input is opened before anything is written (in particular before the first prompt). More
than one operand is a usage error (FR-16).
*AC:* `dp-cars2 day.txt` → `R`, exit 0; `dp-cars2 -tp < totals.tot` → `R`, exit 0. *(UR-02)*

**FR-03: Tokens.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
consumed in order by FR-04 and FR-05 (sales mode) or FR-10 (totals mode). Every token that is
consumed MUST be a valid *integer* (CONV-33); a sign (`+5`, `-0`) and leading zeros (`007`) are
allowed, and the value is used, not the spelling. Line structure has no meaning: tokens may be
separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF
input. A token that is not a valid *integer* is handled by FR-12.
*AC:* `dp-cars2 --totals totals.tot` (TAB-separated) → `R`. *(UR-02, UR-10)*

**FR-04: Opening stock (sales mode).**
The first 12 tokens are the opening stock *S*<sub>0</sub> … *S*<sub>11</sub>, in brand order.
Each MUST be a valid *integer* with 0 ≤ *S*<sub>*b*</sub> ≤ 999999; a valid *integer* outside
that range is handled by FR-12 (`value out of range`). If the input ends before the twelfth
value has been read, FR-12 applies (`unexpected end of input`).
*(SRS-26 FR-03.)*
*AC:* as SRS-26 FR-03, with `dp-cars2` in the diagnostics. *(UR-02, UR-08)*

**FR-05: Sales phase (sales mode).**
After the opening stock, the tool MUST repeat the following steps until the sales phase ends:

1. Read the next token, the *brand token*. If the input has ended instead, the sales phase
   ends.
2. If the brand token's value is negative (the sentinel), the sales phase ends. The tool reads
   no further input: any bytes after the sentinel are ignored, whatever they contain.
3. Otherwise read the next token, the *quantity token*, whatever the brand's value (also when
   it is 12 or more). If the input has ended instead, FR-12 applies
   (`unexpected end of input`).
4. Apply the checks of FR-06. If the sale passes them, add the quantity to
   *T*<sub>*b*</sub>, where *b* is the brand token's value; otherwise the sale is refused.

The brand and the quantity may be any valid *integer* (−2⁶³ … 2⁶³−1). `-0` is brand 0, not the
sentinel. When the sales phase ends, the report is written (FR-07).
*(SRS-26 FR-04.)*
*AC:* `dp-cars2 day.txt` → `R`; `dp-cars2 cut.txt` → stdout empty, stderr
`dp-cars2: cut.txt:4: unexpected end of input\n`, exit 1. *(UR-02, UR-08)*

**FR-06: Refused sales (sales mode).**
A sale with brand value *b* (≥ 0) and quantity value *q* MUST be checked in this order, and
the first check that fails refuses the sale:

1. If *b* ≥ 12: `dp-cars2: <source>:<line>: no such brand '<token>'`, where `<line>` and
   `<token>` are those of the brand token.
2. If *q* < 0: `dp-cars2: <source>:<line>: negative quantity '<token>'`, where `<line>` and
   `<token>` are those of the quantity token.
3. If *q* > *S*<sub>*b*</sub> − *T*<sub>*b*</sub>:
   `dp-cars2: <source>:<line>: not enough cars in stock for brand <b> '<token>'`, where `<b>` is
   the decimal of *b* (its value, not its spelling), and `<line>` and `<token>` are those of
   the quantity token.

The comparison in check 3 MUST be exact for every *q* up to 2⁶³−1 (compare *q* with the
remaining stock; computing *T*<sub>*b*</sub> + *q* can overflow a 64-bit integer). A quantity
of 0 passes every check when *b* < 12 and changes nothing. `<source>` is as defined in section
1.3 and `<token>` is the token's exact bytes. The diagnostic MUST be written to standard error,
and standard error flushed, as soon as the quantity token has been read and before the next
read; the sales phase then continues with step 1 of FR-05. Each refused sale produces exactly
one diagnostic. A refused sale does not change any total. If at least one sale was refused,
the report is still written (and the totals saved, FR-11), and the exit status is 1.
*(SRS-26 FR-05.)*
*AC:* `dp-cars2 rejected.txt` → stderr
`dp-cars2: rejected.txt:3: no such brand '12'\n`,
`dp-cars2: rejected.txt:4: negative quantity '-2'\n`,
`dp-cars2: rejected.txt:6: not enough cars in stock for brand 3 '2'\n`,
`dp-cars2: rejected.txt:7: not enough cars in stock for brand 4 '1'\n`; stdout the report with
sales 8 for brand 1, 3 for brand 3, and 0 for every other brand; exit 1. *(UR-03)*

**FR-07: Report.**
When the totals are complete — at the end of the sales phase in sales mode, or after FR-10 in
totals mode — the tool MUST write exactly 14 lines to standard output, each ending with a
single LF:

1. `DAILY REPORT`
2. `Brand    Start    Sales      End      Sales %` (45 bytes: `Brand`, 4 spaces, `Start`,
   4 spaces, `Sales`, 6 spaces, `End`, 6 spaces, `Sales %`)
3. … 14. one line for each brand *b* = 0, 1, …, 11, in that order, made of five fields with no
   separators: the decimal of *b* right-aligned in 5 columns; the decimal of
   *S*<sub>*b*</sub> right-aligned in 9 columns; the decimal of *T*<sub>*b*</sub> in 9
   columns; the decimal of *S*<sub>*b*</sub> − *T*<sub>*b*</sub> in 9 columns; and the
   percentage field of FR-08 right-aligned in 13 columns.

"Right-aligned in *w* columns" means preceded by as many spaces (`0x20`) as are needed to make
the field *w* bytes long; with the limits of FR-04 and FR-10 no field is ever longer than its
width, so every brand line is exactly 45 bytes plus LF. There are no blank lines and no
trailing spaces. The report is written once, after all input has been consumed, and standard
output is flushed before the totals file is opened (FR-11) and before the tool exits. The
report depends only on the totals: the same totals give the same report in either mode.
*(SRS-26 FR-06.)*
*AC:* `dp-cars2 day.txt` → stdout `R`, which is exactly:

```text
DAILY REPORT
Brand    Start    Sales      End      Sales %
    0       15        5       10   33.333333%
    1        8        0        8    0.000000%
    2       20        5       15   25.000000%
    3        4        4        0  100.000000%
    4        0        0        0          n/a
    5       12        0       12    0.000000%
    6        7        2        5   28.571429%
    7       30       10       20   33.333333%
    8        3        1        2   33.333333%
    9       10        0       10    0.000000%
   10       25        1       24    4.000000%
   11        6        0        6    0.000000%
```

stderr empty, exit 0; `dp-cars2 --totals totals.tot` → the same `R`. *(UR-02, UR-05)*

**FR-08: Sales percentage.**
If *S*<sub>*b*</sub> > 0, the percentage field MUST be `FIX(P, 6)` (CONV-35) followed by `%`,
where *P* is the binary64 value of (100 × *T*<sub>*b*</sub>) / *S*<sub>*b*</sub> computed as
follows: 100 × *T*<sub>*b*</sub> is computed exactly (it is at most 99999900) and converted to
binary64 exactly, *S*<sub>*b*</sub> is converted to binary64 exactly, and the two are divided
once with IEEE 754 round-to-nearest-even. (Equivalently, *P* is the binary64 value nearest to
the exact quotient.) `FIX` then rounds the exact value of *P*, ties to even. Because
*T*<sub>*b*</sub> ≤ *S*<sub>*b*</sub>, the field is between `0.000000%` and `100.000000%`. If
*S*<sub>*b*</sub> = 0, the field MUST be the three bytes `n/a`.
*(SRS-26 FR-07.)*
*AC:* (*T*, *S*) = (5, 15) → `33.333333%`; (2, 7) → `28.571429%`; (2, 3) → `66.666667%`;
(1, 512) → `0.195312%`; (4, 4) → `100.000000%`; (0, 8) → `0.000000%`; (999999, 999999) →
`100.000000%`; (0, 0) → `n/a`. *(UR-03)*

**FR-09: Prompts (sales mode).**
`-p`, `--prompt` enables these prompts (CONV-36):

| Prompt | Bytes | Written |
| :-- | :-- | :-- |
| P1(*b*) | `Cars in stock for brand: ` followed by the decimal of *b* and one LF | immediately before the opening stock of brand *b* is read, for *b* = 0 … 11 |
| P2 | `Which brand was sold? ` (22 bytes, ending with one space, no LF) | immediately before each attempt to read a brand token (step 1 of FR-05) |
| P3 | `How many cars in sale? ` (23 bytes, ending with one space, no LF) | immediately before each attempt to read a quantity token (step 3 of FR-05) |

Each prompt is written to standard error, and standard error flushed, before the read it
belongs to; a prompt is written even if that read reaches the end of the input. So a day with
*n* sales (accepted or refused) produces P1(0) … P1(11), then *n* times P2 followed by P3,
then one final P2. No prompt is written after the sentinel, after an error of FR-12, or if the
input cannot be opened. A diagnostic that follows a prompt continues the same line of standard
error. Without the flag, no prompt is written. Prompts never change standard output.
*(SRS-26 FR-08.)* In totals mode, `-p` and `--prompt` are accepted and have **no effect**: no
prompt is ever written.
*AC:* `dp-cars2 --prompt < day.txt` → stdout `R`; stderr the twelve lines
`Cars in stock for brand: 0\n` … `Cars in stock for brand: 11\n`, then eight times
`Which brand was sold? How many cars in sale? `, then `Which brand was sold? `; exit 0.
`dp-cars2 -tp < totals.tot` → stdout `R`, stderr empty, exit 0. *(UR-09)*

**FR-10: Totals mode.**
With `-t` or `--totals`, the tool MUST read the whole input (FR-02, FR-03) and then interpret
its tokens, in order, as *S*<sub>0</sub>, *T*<sub>0</sub>, *S*<sub>1</sub>, *T*<sub>1</sub>,
…, *S*<sub>11</sub>, *T*<sub>11</sub>, checking each token before the next:

- each *S*<sub>*b*</sub> MUST be a valid *integer* with 0 ≤ *S*<sub>*b*</sub> ≤ 999999;
- each *T*<sub>*b*</sub> MUST be a valid *integer* with 0 ≤ *T*<sub>*b*</sub> ≤
  *S*<sub>*b*</sub>;
- the input MUST hold exactly 24 tokens.

A token that is not a valid *integer* gives `invalid integer`; a valid *integer* outside its
range gives `value out of range`; an input with fewer than 24 tokens gives
`unexpected end of input` (when the first missing value is reached); and a 25th token gives
`dp-cars2: <source>:<line>: extra data '<token>'`, with that token's line and bytes, once all
24 values have been checked. Each of these is handled by FR-12. If all checks pass, the tool
writes the report (FR-07) from these totals. Totals mode has no sales phase, no refused sales,
and no prompts (FR-09). Line structure has no meaning, so a totals file may hold one brand per
line (as FR-11 writes it), all 24 values on one line, or any other layout.
*AC:* `dp-cars2 --totals totals.tot` → `R`, exit 0. `dp-cars2 --totals oversold.tot` → stdout
empty, stderr `dp-cars2: oversold.tot:4: value out of range '5'\n`, exit 1. A totals file of 23
values on 12 lines gives `unexpected end of input` with line 13; one with a 13th line
`TOTAL 28` gives `extra data 'TOTAL'` with line 13; a sales total of `-1` and an opening stock
of `1000000` give `value out of range`. *(UR-05, UR-06)*

**FR-11: Saving the totals.**
With `-s FILE` or `--save=FILE`, after a successful run of either mode the tool MUST proceed in
this order:

1. Consume the input (sales mode: until the sales phase ends; totals mode: FR-10), and close
   it.
2. Write the report to standard output (FR-07).
3. Flush standard output.
4. Create the file SAVE if it does not exist, or truncate it to zero length if it does, and
   write to it, as raw bytes, exactly 12 lines: for *b* = 0 … 11, the decimal of
   *S*<sub>*b*</sub>, one space, the decimal of *T*<sub>*b*</sub>, and one LF. Then close it.

The totals saved are those the report was produced from: in sales mode, the opening stock and
the totals of the accepted sales (refused sales are not included, and a refused sale does not
prevent saving); in totals mode, the values read, written in decimal (`+15` is written `15`,
`05` is written `5`, `-0` is written `0`). The file is therefore valid input for totals mode,
and `dp-cars2 --totals SAVE` writes the same report again. Because the input is closed before
SAVE is opened, SAVE may name the input file itself.
If the run stops at an error of FR-12 or FR-13, no report is written and SAVE is neither
created nor modified. If SAVE cannot be created or opened for writing — a directory in it does
not exist, it is a directory, access is denied, or any other reason — the tool MUST write
`dp-cars2: <SAVE>: <reason>`, with SAVE exactly as given and `<reason>` from the CONV-16 table,
and exit with status 1; the report already written is kept. If writing or closing the file
fails, the message is `dp-cars2: <SAVE>: Input/output error`, exit 1, and the file's contents
are unspecified.
*AC:* `dp-cars2 --save day.tot day.txt` → `R`, exit 0, and a following `dp-cars2 -t day.tot`
→ `R`, exit 0. `dp-cars2 -s day.tot rejected.txt` → exit 1 with the refused-sale diagnostics,
and a following `dp-cars2 --totals day.tot` → the same report, exit 0.
`dp-cars2 -s day.tot cut.txt` → exit 1, and a following `dp-cars2 -t day.tot` reports
`dp-cars2: day.tot: No such file or directory`. `dp-cars2 -s subdir day.txt`, where `subdir`
is a directory → `R` on stdout, then stderr `dp-cars2: subdir: Is a directory\n`, exit 1;
`dp-cars2 -s nodir/day.tot day.txt` → `R`, then
`dp-cars2: nodir/day.tot: No such file or directory`, exit 1. *(UR-04, UR-05, UR-07)*

**FR-12: Invalid, incomplete, and overlong input.**
The tool MUST write one of the following diagnostics and stop: it reads no further input,
writes **no report**, does not open SAVE, and exits with status 1. Refused-sale diagnostics
already written (FR-06) are kept.

- A consumed token that is not a valid *integer* (CONV-33), including an integer outside
  −2⁶³ … 2⁶³−1: `dp-cars2: <source>:<line>: invalid integer '<token>'`.
- A valid *integer* outside its range — an opening stock outside 0 … 999999 (both modes), or a
  sales total outside 0 … *S*<sub>*b*</sub> (totals mode):
  `dp-cars2: <source>:<line>: value out of range '<token>'`.
- The input ends while a value is expected — an opening stock or a quantity in sales mode
  (FR-04, FR-05 step 3), any of the 24 totals in totals mode:
  `dp-cars2: <source>:<line>: unexpected end of input`, where `<line>` is the end-of-input
  line number.
- Totals mode only: a 25th token: `dp-cars2: <source>:<line>: extra data '<token>'`.

`<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32), and
`<token>` is the token's exact bytes (CONV-34). In sales mode this requirement is
SRS-26 FR-09 with the tool name changed.
*AC:* `dp-cars2 cut.txt` → `dp-cars2: cut.txt:4: unexpected end of input`, exit 1; in totals
mode, a token `x` on line 2 → `dp-cars2: badtok.tot:2: invalid integer 'x'`, exit 1. *(UR-06,
UR-08)*

**FR-13: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-cars2: <source>: <reason>` with `<reason>` from the CONV-16 table,
write no report, not open SAVE, and exit with status 1. When standard input fails, `<source>`
is `-`.
*AC:* `dp-cars2 -t missing.tot` → stderr `dp-cars2: missing.tot: No such file or directory\n`,
stdout empty, exit 1. *(UR-08)*

**FR-14: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read, no prompt is written,
and no file is created.
*AC:* `dp-cars2 --help` matches the user manual exactly; `dp-cars2 extra --help` also prints
it. *(UR-11)*

**FR-15: Version.**
`--version` MUST write `dp-cars2 (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-11)*

**FR-16: Usage errors.**
Unknown options, missing option arguments, and arguments supplied to options that take none
(`--prompt=…`, `--totals=…`, `--help=…`, `--version=…`), MUST be reported with the CONV-13
messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be
abbreviated (CONV-08): `--tot` is unrecognized. A SAVE that is empty, or exactly `-` (the
totals are never written to standard output), MUST be reported as
`dp-cars2: invalid argument '<SAVE>' for '<option>'`, where `<option>` is `-s` or `--save` as
the user wrote it; only the winning occurrence of a repeated `--save` is checked (CONV-11). A
second operand MUST be reported as `dp-cars2: extra operand '<second operand>'`. Option values
and operands are checked after the whole argument list has been scanned (CONV-12), the option
value before the operands.
*AC:* `dp-cars2 -s '' day.txt` → `dp-cars2: invalid argument '' for '-s'`;
`dp-cars2 --save=- day.txt` → `dp-cars2: invalid argument '-' for '--save'`; `dp-cars2 -s` →
`dp-cars2: option requires an argument -- 's'`; `dp-cars2 --totals=1` →
`dp-cars2: option '--totals' doesn't allow an argument`; `dp-cars2 -x --help` →
`dp-cars2: invalid option -- 'x'`; each followed by the CONV-14 line, exit 2. *(UR-12, UR-14)*

**FR-17: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, create or modify any file, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case, and no totals file is created. *(UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Standard output, standard error, and the bytes of the totals file MUST be identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: a portable saved-totals file | The totals file MUST be created and written in binary mode on every platform, so it never contains CR bytes, and a totals file written on any platform MUST be read back identically on every other (CRLF line endings and a trailing Ctrl-Z, as left by editors and old tools, are accepted by FR-03). Creating or truncating SAVE MUST work identically whether or not it exists, and the CONV-16 reason MUST be derived portably: opening a directory for writing fails with `EISDIR` on Linux and macOS but with "access denied" on Windows, and both MUST be reported as `Is a directory`; a missing parent directory (`ENOENT`, `ERROR_PATH_NOT_FOUND`) MUST be reported as `No such file or directory`. In sales mode, the interactive requirements of SRS-26 NFR-02 apply unchanged: binary-mode input, explicit flushing of each prompt and refused-sale diagnostic, no reading beyond the current token, and the platform's own end-of-input signal. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance | A day of 1 000 000 sales MUST be processed in under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31); memory MUST NOT grow with the number of sales. A totals input of any size MAY be held in memory while it is checked; for a 1 MiB totals input the tool MUST finish in under 1 s native (10 s interpreted). Start-up and exit for a short input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list, input bytes, or file-system condition (CONV-24), including tokens of any length, integers far outside the 64-bit range, and quantities near 2⁶³−1. A broken pipe on standard output ends the tool quietly (CONV-25). Every file the tool opens MUST be closed on every path, including failures. | Unit + black-box tests |
| NFR-05 | Maintainability: an independent report component | The design MUST contain one **report component** (the textbook's `print_report`) that: (a) receives exactly two indexed collections of 12 integers — the opening stocks and the sales totals, indexed by brand number — and nothing else (no input stream, source name, options, or mode); (b) treats both as read-only and MUST NOT modify them, using the language's means of expressing this where it has one (read-only parameters, immutable views, or copies); (c) performs no input, no prompting, and no diagnostics, and produces only the 14 report lines, either by writing them to an output it is given or by returning them; (d) is the only place where the report's title, heading, column widths, and `n/a` rule appear, using one percentage function for FR-08; (e) is invoked exactly once per successful run, by the sales-mode path and the totals-mode path alike, neither of which formats any part of the report itself. The sales dialog (opening stock, sales, the checks of FR-06, prompts) MUST be a separate component that produces the two collections and knows nothing of the report layout. The totals reader (FR-10) and the totals writer (FR-11) MUST be separate units that share one definition of the totals format. The number of brands (12) and the stock limit (999999) MUST each appear exactly once, as named constants. Option parsing and file handling are further separate units (Principles 3, 13, 16, 18). | Design review |
| NFR-06 | Testability | The report component MUST be covered by unit tests that call it directly with literal collections, with no input and no dialog — at least the totals of `R`, a brand with zero opening stock, the limits 0 and 999999, and (1, 512) — and that check that both collections are unchanged after the call. The sales dialog MUST be unit-tested without the report component, by checking the collections it produces. A round-trip test MUST show that writing any valid totals with the totals writer and reading them with the totals reader gives the same collections. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the input (the FILE operand or standard input), MUST create or modify only SAVE, and MUST NOT delete or rename any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-cars2 --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-cars2: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-cars2: unrecognized option 'T'` |
| `-s` without an argument | `dp-cars2: option requires an argument -- 's'` |
| `--save` without an argument | `dp-cars2: option '--save' requires an argument` |
| `--prompt=…`, `--totals=…`, `--help=…`, `--version=…` | `dp-cars2: option '--prompt' doesn't allow an argument` (or `'--totals'`, `'--help'`, `'--version'`) |
| SAVE `V` is empty or `-` | `dp-cars2: invalid argument 'V' for '-s'` (or `'--save'`, as written) |
| A second operand `X` | `dp-cars2: extra operand 'X'` |

Refused sales (sales mode; processing continues, the report is written, and the final exit
status is 1):

| Trigger | Exact message |
| :-- | :-- |
| Brand token `K` on line `L` of source `S` has a value of 12 or more | `dp-cars2: S:L: no such brand 'K'` |
| Quantity token `K` on line `L` of source `S` is negative | `dp-cars2: S:L: negative quantity 'K'` |
| Quantity token `K` on line `L` of source `S` exceeds the remaining stock of brand `B` | `dp-cars2: S:L: not enough cars in stock for brand B 'K'` |

Runtime errors before the report (exit status 1; the tool stops at the first one, writes no
report, and does not open SAVE):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-cars2: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-cars2: F: Permission denied` |
| FILE `F` is a directory | `dp-cars2: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-cars2: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-cars2: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *integer* | `dp-cars2: S:L: invalid integer 'K'` |
| Opening stock or (totals mode) sales total `K` on line `L` of source `S` is out of range | `dp-cars2: S:L: value out of range 'K'` |
| The input of source `S` ends, at end-of-input line `L`, where a value is expected | `dp-cars2: S:L: unexpected end of input` |
| Totals mode: a 25th token `K` on line `L` of source `S` | `dp-cars2: S:L: extra data 'K'` |

Runtime errors after the report (exit status 1; the report already written is kept):

| Trigger | Exact message |
| :-- | :-- |
| A directory in SAVE `G` does not exist | `dp-cars2: G: No such file or directory` |
| SAVE `G` cannot be created or opened because access is denied | `dp-cars2: G: Permission denied` |
| SAVE `G` is a directory | `dp-cars2: G: Is a directory` |
| A component of SAVE `G` is not a directory | `dp-cars2: G: Not a directory` |
| Any other failure to open, write, or close SAVE `G` | `dp-cars2: G: Input/output error` |
| Standard output cannot be written (other than a broken pipe) | `dp-cars2: write error` |

When `--prompt` is given in sales mode, a diagnostic follows the last prompt on the same line of
standard error (FR-09).

## 7. Verification

The black-box harness compares only standard output, standard error, and exit status, so tests
observe the totals file indirectly: a later step of the same test reads it with `--totals`. A
file that holds the expected totals then yields the expected report, a file that was never
created yields `No such file or directory`, and an untouched fixture yields its own report.
FR-01 is verified by tests whose inputs, options, and expected outputs are those of Project 26.

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases; case 05 has two steps) | FR-01 … FR-12, FR-14, FR-16 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 and 04 … 10 have several steps) | FR-01, FR-03 … FR-17 |
| Unit test (written by the implementer) | FR-03 … FR-08, FR-10, FR-11, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-06 and FR-09 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-cars2 day.txt` | FR-01 (= Project 26 test 01), FR-05, FR-07, FR-08 |
| 02 | `dp-cars2 --prompt < day.txt` | FR-01 (= Project 26 test 03), FR-09 |
| 03 | `dp-cars2 rejected.txt` | FR-01 (= Project 26 test 04), FR-06 |
| 04 | `dp-cars2 --totals totals.tot` | FR-03, FR-07 (same report as test 01), FR-10 |
| 05 | `dp-cars2 --save day.tot day.txt`, then `dp-cars2 -t day.tot` | FR-11 (round trip) |
| 06 | `dp-cars2 -tp < totals.tot` | FR-02, FR-09 (no prompts in totals mode) |
| 07 | `dp-cars2 --totals oversold.tot` | FR-10, FR-12 |
| 08 | `dp-cars2 cut.txt` | FR-01 (= Project 26 test 06), FR-12 |
| 09 | `dp-cars2 --help` | FR-14 |
| 10 | `dp-cars2 -s '' day.txt` | FR-16, FR-17 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01 |
| UR-02 | FR-02 … FR-05, FR-07 |
| UR-03 | FR-06, FR-08 |
| UR-04 | FR-11 |
| UR-05 | FR-07, FR-10, FR-11 |
| UR-06 | FR-10, FR-12 |
| UR-07 | FR-11 |
| UR-08 | FR-04, FR-05, FR-12, FR-13, CONV-34, CONV-16 |
| UR-09 | FR-09, CONV-36 |
| UR-10 | FR-03, NFR-02, CONV-37 |
| UR-11 | FR-14, FR-15 |
| UR-12 | FR-16, FR-17 |
| UR-13 | NFR-01, NFR-02, CONV-03 |
| UR-14 | FR-16, NFR-05, CLI-CONV |
| UR-15 | NFR-03, NFR-07 |
