# Software Requirements Specification (SRS) — dp-average, dp-chk-sort

| Field | Value |
| :-- | :-- |
| Document ID | SRS-17 |
| Project | `17-stream-filters` — Stream Filtering & Monotonicity Validation |
| Products | `dp-average`, `dp-chk-sort` (canonical names) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-17) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-average` and `dp-chk-sort`. It is
complete and precise enough that independent implementations in any programming language
produce **byte-identical** output for every invocation. It is the authoritative source for
design (HLD/LLD), testing, and grading.

### 1.2 Scope
Both tools read numbers as tokens from standard input or from one file. `dp-average` reads
real numbers until the end of the input and writes one line: the average of the numbers
greater than zero, or a message saying there were none. `dp-chk-sort` reads 64-bit integers
until the end of the input or until the first integer that is less than its predecessor,
writes one line saying whether the input is sorted, and also reports the answer through its
exit status, which this SRS defines in place of CONV-18 (§3.7). Both tools report invalid
numbers with their line numbers and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |
| binary64 operation | An IEEE 754 binary64 addition (⊕) or division (⊘), computed as if exactly and then rounded **once** to binary64, round to nearest, ties to even, with subnormal results kept |
| Positive value | A `dp-average` value *x* with *x* > 0 as a binary64 comparison; 0, −0, and negative values are not positive |
| Inversion | A `dp-chk-sort` value that is less than the value immediately before it |
| `FIX(x, 6)` | *x* written with exactly six digits after the decimal point, rounded from its exact binary64 value, with no negative zero (CONV-35) |

### 1.4 References
- URD-17: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help texts)
- IEEE 754-2019, *Standard for Floating-Point Arithmetic*
- POSIX `sort -c` (the exit-status protocol `dp-chk-sort` follows)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §3.1 (informative; see §2.5)
- SRS-15 (`projects/15-stats/specs/SRS.md`): `dp-stats`, whose reading of real numbers and
  overflow diagnostic `dp-average` shares

## 2. Overall description

### 2.1 Product perspective
`dp-average` and `dp-chk-sort` are standalone executables. Their interfaces are the command
line, standard input or the file named by the operand, standard output, standard error, and
the exit status. They belong to the curriculum's applications-programming track (Projects
11–52) and adapt the two programs of §3.1 of Johnsonbaugh & Kalin, *Applications Programming
in ANSI C*.

### 2.2 Product functions
1. `dp-average`: read and validate real numbers until the end of the input; sum the positive
   ones in input order; write their average, or `no positive numbers read`.
2. `dp-chk-sort`: read and validate integers until the end of the input or the first
   inversion; write `file is sorted` or `file is not sorted`; exit with 0 or 1 accordingly.
3. Both: accept CRLF input and a trailing Ctrl-Z marker; report invalid numbers and
   unreadable input files.
4. Both: display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The average MUST be computed with the binary64 operations of FR-04 in the order given.
  Wider intermediate precision, reassociation, and compensated summation MUST NOT be used.
- `dp-chk-sort` MUST compare integers exactly as 64-bit integers, never as floating-point
  values (two different integers above 2⁵³ can have the same binary64 value).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only tokens that match the tool's grammar are values.
- The number of positive values is below 2⁵³ in practice, so it converts to binary64 exactly;
  FR-04 nevertheless defines the conversion for every count.

### 2.5 Relationship to the textbook program (informative)
§3.1 presents two programs that read standard input until end-of-file. The first averages the
positive numbers it reads and prints `average = …`, or `no positive numbers read` when there
were none. The second reads integers and stops at the first one that is less than its
predecessor, printing `file is not sorted`; at end-of-file it prints `file is sorted`. Both
tools keep:

- the selection rule (only numbers greater than zero are averaged) and the non-decreasing
  order rule (equal neighbors are in order; an empty input and a single number are sorted);
- the result messages word for word, and the average with six digits after the decimal point
  (the textbook's default `%f` format);
- the short-circuit: `dp-chk-sort` stops reading at the first inversion.

They change the following, for the reasons given:

- **No leading blank line.** The section's description shows each result preceded by an empty
  line (`\naverage = …\n`). That line separated the answer from the numbers the user had just
  typed and echoed on the terminal; it carries no information, and in a redirected output file
  or a pipeline it is an empty first line that every consumer must skip. Following the
  curriculum's policy for output layout, both tools write the result line alone.
- **The answer of `dp-chk-sort` is also its exit status** (§3.7): 0 for sorted, 1 for not
  sorted, 2 for any failure, as POSIX `sort -c` does. A checker whose answer can be used only by
  parsing its output is awkward in scripts, and a failure (a missing file, a typo) must not be
  mistaken for either answer. This overrides CONV-18 for `dp-chk-sort` (§2.6).
- **What is read after an inversion is decided** (FR-08): nothing. The token that completes
  the first inversion is the last one validated; later bytes are not examined, so
  `1 3 8 4 junk` is reported as not sorted, not as an invalid integer. The textbook's early
  exit has the same effect, and it keeps the answer independent of how much unread data a
  pipe still holds.
- **Invalid input is diagnosed** (FR-06, FR-10). A token that is not a number stops the
  textbook programs' reading loops as if the input had ended, so a typo silently truncates
  the data: the average of the numbers before it, or "sorted" for a file whose later half was
  never checked. Both tools report the token with its line number and give no answer.
  Tokens that the C library would read as numbers but that are not numbers here, such as
  `inf`, `nan`, `0x10`, and (for `dp-chk-sort`) `12abc`, are invalid too (CONV-33).
- **Integers are 64-bit** (FR-07), with no silent wraparound, instead of the textbook's
  platform-dependent `int`.
- **The average is reproducible** (FR-04): the summation order and every rounding are fixed,
  and a sum that overflows is diagnosed instead of printing `inf`.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **No prompts.** Neither program in the section prompts: both are filters that consume a
  stream until end-of-file. The tools therefore have no `--prompt` option.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV with **one override**, for `dp-chk-sort` only: its exit statuses
are defined by §3.7 instead of CONV-18, so a runtime failure (CONV-16, CONV-17) and a data
diagnostic (CONV-34) exit with status **2**, not 1, and status 1 means "not sorted".
`dp-average` uses CONV-18 unchanged. From section 10, this SRS incorporates:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Both tools read their input as tokens, with line numbers. |
| CONV-33 | `dp-average` uses the *real* grammar, `dp-chk-sort` the *integer* grammar (−2⁶³ … 2⁶³−1), without further range restrictions. |
| CONV-34 | Data diagnostics: `invalid number` (`dp-average`), `invalid integer` (`dp-chk-sort`), and the further message `arithmetic overflow at '<token>'` (`dp-average`, FR-06, the same message as SRS-15). No answer has been written when one is reported. Exit status 1 for `dp-average`, 2 for `dp-chk-sort`. |
| CONV-35 | `FIX(x, 6)` for the average. |
| CONV-36 | Not applicable: neither tool has prompts (neither accepts `-p`). |
| CONV-37 | The input of both tools is *text data*. |
| CONV-38 | Not applicable: nothing is random. |

Option syntax follows CONV-07 … CONV-12, and diagnostics follow CONV-13 … CONV-16 (usage errors
exit with status 2 for both tools, as CONV-14 requires). Standard input is read as permitted by
CONV-26. The tools copy no input bytes to their output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-average [FILE]
dp-chk-sort [FILE]
dp-average --help | --version
dp-chk-sort --help | --version
```

### 3.2 Options

Both tools accept only the standard options:

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| — | `--help` | none | — | Print the tool's help text and exit 0 |
| — | `--version` | none | — | Print the tool's version line and exit 0 |

Option syntax (`--`, repetition, and scan order) follows CONV-07 … CONV-12.

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
Exactly one result line (FR-05, FR-09) when the tool succeeds, and nothing else. On a data
error or an input failure, nothing. On a usage error, or when `--help` / `--version` is
handled, the output is as specified by FR-12 … FR-15 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing is written to standard error when the run succeeds,
including when `dp-chk-sort` finds the input not sorted.

### 3.7 Exit status

`dp-average` (CONV-18):

| Status | Condition |
| :-- | :-- |
| 0 | The whole input was read and the result line written (including `no positive numbers read`), or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-11), it contained an invalid number or the sum overflowed (FR-06), or standard output could not be written |
| 2 | Usage error (FR-14) |

`dp-chk-sort` (**overrides CONV-18**, like `sort -c`):

| Status | Condition |
| :-- | :-- |
| 0 | The input is sorted: `file is sorted` was written; or `--help` / `--version` was handled |
| 1 | The input is not sorted: `file is not sorted` was written |
| 2 | Trouble: a usage error (FR-14), an input that could not be opened or read (FR-11), an invalid integer (FR-10), or a failure to write standard output |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are the public fixture files in
`tests/fixtures/`: `numbers.txt` is `-5.0 0.0 10.0 20.0\n`; `nonpos.txt` is `-1.0 -10.0 0.0\n`;
`bad.txt` is `2.5 -1\n4.0\n\n1/2 3\n`; `sorted.txt` is `1 3 5 5 9 12\n`; `unsorted.txt` is
`1 3 8 4 10\n`; `stop.txt` is `1 3\n8 4 junk\n`; `badint.txt` is `1 2\n3 3.5 2\n`.

### 4.1 Requirements common to both tools

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. More than one operand is a
usage error (FR-14).
*AC:* `dp-average < numbers.txt`, `dp-average numbers.txt`, and `dp-average - < numbers.txt`
write the same line; likewise for `dp-chk-sort` and `unsorted.txt`. *(UR-06)*

**FR-02: Tokens.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order, one at a time, as each becomes complete. Line structure has no meaning:
values may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads
exactly like LF input. Neither tool keeps a token after processing it, so memory does not
depend on the input (NFR-03).
*AC:* a file `3 4\r\n` followed by one `0x1A` byte gives `average = 3.500000`; a file whose
tokens are `1`, `2`, `2` on CRLF lines followed by three `0x1A` bytes gives `file is sorted`.
*(UR-09, UR-15)*

### 4.2 dp-average

**FR-03: Values and selection.**
Every token MUST be a valid *real* (CONV-33); its value is the binary64 number nearest to the
token's decimal value. A sign, a missing integer or fraction part (`.5`, `3.`), an exponent in
either case, and leading zeros are allowed; the decimal separator is always `.`, whatever the
locale. A token too small for binary64 is valid and becomes zero or a subnormal number
(`1e-400` is 0); `-0` is negative zero. A value is **selected** if it is positive (*x* > 0);
every other value — zero, negative zero, a negative number, or a number that underflowed to
zero — is validated and then ignored. Every token is validated, whether or not its value is
selected.
*AC:* `dp-average < numbers.txt` selects 10.0 and 20.0; `dp-average nonpos.txt` selects
nothing; the tokens `1e-400 -0 0` select nothing; the token `4.9e-324` (the smallest subnormal)
is selected. *(UR-01)*

**FR-04: Sum and average.**
The tool keeps the sum *S* of the selected values and their count *c* (an exact integer).
Initially *S* = 0 and *c* = 0. For each selected value *x*, in input order, it MUST set
*S* = *S* ⊕ *x* and *c* = *c* + 1; so *S* = (…((0 ⊕ *x*₁) ⊕ *x*₂) …) ⊕ *x*_c, where
*x*₁ … *x*_c are the selected values. After the end of the input, if *c* ≥ 1, the average is
*a* = *S* ⊘ *ĉ*, where *ĉ* is *c* converted to binary64 (round to nearest, ties to even; exact
for *c* ≤ 2⁵³).
*AC:* the selected values 0.1 and 0.2 give *S* = 0.30000000000000004 and
*a* = 0.15000000000000002 (to 17 significant digits), printed as `0.150000`. *(UR-01, UR-10)*

**FR-05: Result line.**
After the end of the input, `dp-average` MUST write exactly one line to standard output:
`average = ` followed by `FIX(a, 6)` (CONV-35) and LF, if *c* ≥ 1; or
`no positive numbers read` + LF if *c* = 0 (including an empty input, or one that holds only
whitespace and a trailing Ctrl-Z run). There is no leading blank line, no leading or trailing
space, and nothing else; the exit status is 0.
*AC:* `dp-average < numbers.txt` → stdout `average = 15.000000\n`, stderr empty, exit 0;
`dp-average nonpos.txt` → stdout `no positive numbers read\n`, exit 0; `dp-average` with empty
standard input → `no positive numbers read\n`, exit 0; the single value `0.0078125` (an exact
tie) → `average = 0.007812`; the values `4.9e-324 -1` → `average = 0.000000`. *(UR-01, UR-02,
UR-10)*

**FR-06: Invalid numbers and overflow (`dp-average`).**
If a token is not a valid *real* (CONV-33) — including a token whose value overflows binary64,
such as `1e309`, and the spellings `inf`, `nan`, and `0x10` — the tool MUST write
`dp-average: <source>:<line>: invalid number '<token>'`. If a selected value makes *S*
infinite, the tool MUST write `dp-average: <source>:<line>: arithmetic overflow at '<token>'`.
In both messages `<source>` is as defined in section 1.3, `<line>` is the token's line number
(CONV-32), and `<token>` is the token's exact bytes (CONV-34). The tool then stops: it reads no
further input, writes **no result line**, and exits with status 1.
*AC:* `dp-average bad.txt` → stdout empty, stderr `dp-average: bad.txt:4: invalid number '1/2'\n`,
exit 1. The values `1e308` and `1e308` on lines 1 and 2 give
`arithmetic overflow at '1e308'` on line 2; `1e309` gives `invalid number`; a token `3`
followed directly by a `0x1A` byte and a space gives `invalid number '3␚'` (with the raw
`0x1A` byte), because that Ctrl-Z byte does not end the input. *(UR-07)*

### 4.3 dp-chk-sort

**FR-07: Integers.**
Every token that `dp-chk-sort` reads MUST be a valid *integer* (CONV-33): an optional sign and
decimal digits, with a value in −9223372036854775808 … 9223372036854775807 (−2⁶³ … 2⁶³−1).
Leading zeros and a sign are allowed, so `+5`, `05`, and `5` are equal, and `-0` equals `0`.
Values MUST be compared as exact integers.
*AC:* the tokens `-9223372036854775808 -1 +0 -0 05 +5 9223372036854775807` are sorted.
*(UR-03)*

**FR-08: Order check and short-circuit.**
The tool processes the tokens in order. For each token after the first, once the token is
complete (section 1.3) and valid (FR-07), it compares its value *v*_k with the value *v*_(k−1)
of the token before it. If *v*_k < *v*_(k−1) (an inversion), the tool MUST immediately decide
"not sorted" and stop: it MUST NOT validate any later token, MUST NOT read the input beyond
what it needed to complete the inverting token (apart from ordinary buffering of bytes that are
already available), and MUST NOT wait for more input. Equal neighbors are not an inversion. If
the end of the input is reached without an inversion, the input is sorted; in particular an
empty input (or one that holds only whitespace and a trailing Ctrl-Z run) and an input with one
integer are sorted. Tokens up to and including the inverting token are validated (FR-10).
*AC:* `dp-chk-sort sorted.txt` → sorted; `dp-chk-sort < unsorted.txt` → not sorted after
reading `4`; `dp-chk-sort stop.txt` → not sorted, although `junk` follows the inversion;
`1 2 3 2` without a final LF → not sorted; empty standard input and `42` → sorted. At a
terminal, typing `5 3` and Enter shows the answer at once and the tool exits without waiting
for end of input (manual check). *(UR-03, UR-04)*

**FR-09: Result line and exit status.**
When the answer is decided, `dp-chk-sort` MUST write exactly one line to standard output and
flush it: `file is sorted` + LF with exit status 0, or `file is not sorted` + LF with exit
status 1 (§3.7). There is no leading blank line, no leading or trailing space, and nothing
else; nothing is written to standard error.
*AC:* `dp-chk-sort sorted.txt` → stdout `file is sorted\n`, stderr empty, exit 0;
`dp-chk-sort < unsorted.txt` → stdout `file is not sorted\n`, stderr empty, exit 1.
*(UR-03, UR-05)*

**FR-10: Invalid integers (`dp-chk-sort`).**
If a token that is validated (FR-08) is not a valid *integer* (CONV-33) — including `3.5`,
`1e3`, `12abc`, and integers outside the 64-bit range — the tool MUST write
`dp-chk-sort: <source>:<line>: invalid integer '<token>'`, with `<source>`, `<line>`, and
`<token>` as in FR-06. It then stops: it reads no further input, writes **no result line**,
and exits with status **2** (§3.7).
*AC:* `dp-chk-sort badint.txt` → stdout empty, stderr
`dp-chk-sort: badint.txt:2: invalid integer '3.5'\n`, exit 2 (the inversion `2` after `3.5` is
never reached); `9223372036854775808` → `invalid integer`, exit 2; a token `2` followed directly
by a `0x1A` byte and a space → `invalid integer '2␚'`, exit 2. *(UR-05, UR-07)*

### 4.4 Common requirements (continued)

**FR-11: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs
before the answer is decided, the tool MUST write `<tool>: <source>: <reason>` with `<reason>`
from the CONV-16 table, write no result line, and exit with status 1 (`dp-average`) or 2
(`dp-chk-sort`). When standard input fails, `<source>` is `-`.
*AC:* `dp-chk-sort missing.txt` → stderr `dp-chk-sort: missing.txt: No such file or
directory\n`, stdout empty, exit 2; `dp-average missing.txt` → the same message for
`dp-average`, exit 1; `dp-average subdir` where `subdir` is a directory →
`dp-average: subdir: Is a directory`, exit 1. *(UR-05, UR-08)*

**FR-12: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-average --help` and `dp-chk-sort --help` match the user manual exactly;
`dp-average extra --help` also prints the help. *(UR-11)*

**FR-13: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF, where `<tool>` is
`dp-average` or `dp-chk-sort`, and exit 0 (CONV-02).
*AC:* exact match for each tool. *(UR-11)*

**FR-14: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08). A second operand MUST be
reported as `<tool>: extra operand '<second operand>'`, after the whole argument list has been
scanned (CONV-12).
*AC:* `dp-average numbers.txt nonpos.txt` → `dp-average: extra operand 'nonpos.txt'`;
`dp-chk-sort -x --help` → `dp-chk-sort: invalid option -- 'x'`; `dp-chk-sort --help=1` →
`dp-chk-sort: option '--help' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-12, UR-14)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every usage-error case. *(UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: early termination and end of input | `dp-chk-sort` MUST stop reading and exit at the first inversion on every platform, whether its input is a file, a pipe, or a console; when it exits before a pipe's writer has finished, the writer receives the platform's broken-pipe condition (SIGPIPE or EPIPE on POSIX, `ERROR_NO_DATA` or `ERROR_BROKEN_PIPE` on Windows), and `dp-chk-sort`'s own answer and exit status MUST NOT depend on it. Inputs MUST be read in binary mode, so CR bytes reach the tokenizer and a `0x1A` byte is never treated as end-of-file by the I/O layer; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. The result line MUST be flushed before exit. `dp-average`'s digits MUST NOT depend on the platform: decimal conversion correctly rounded and locale-independent, binary64 arithmetic without extended precision, and `FIX` computed from the exact binary value. | CI black-box tests on 3 OSes; manual pipe and console check; code review |
| NFR-03 | Performance | Each tool MUST process 1 000 000 values (about 8 MiB of input) in under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of values; only the token being read is held. When the first inversion is near the start of a large input, `dp-chk-sort` MUST finish in under 100 ms native (300 ms interpreted), however large the rest of the input. | Measurement |
| NFR-04 | Robustness | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and reals that overflow or underflow binary64. A broken pipe on standard output ends a tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the incremental tokenizer, number validation, the selection-and-sum logic of `dp-average`, the order check of `dp-chk-sort`, result formatting, and I/O MUST be separate units. The order check MUST be one unit that consumes values one at a time and reports as soon as the answer is known; the mapping from outcomes to exit statuses (§3.7) MUST appear in one place. Command-line handling and tokenizing common to both tools MUST be shared rather than duplicated. | Design review |
| NFR-06 | Testability | The selection-and-sum logic, the order check, and `FIX` MUST be pure or testable on in-memory streams, and covered by unit tests that include every acceptance value of FR-03 … FR-10, the empty input, a single value, equal neighbors, and the 64-bit extremes. A short-circuit test MUST show that the order check requests no token after the inverting one (for example, with a token source that fails if asked for more). The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tools MUST read only the file named by the operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2 for both tools). Each is followed by
`Try '<tool> --help' for more information.`, where `<tool>` is `dp-average` or `dp-chk-sort`.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `<tool>: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `<tool>: unrecognized option 'T'` |
| `--help=…`, `--version=…` | `<tool>: option '--help' doesn't allow an argument` (or `'--version'`) |
| A second operand `X` | `<tool>: extra operand 'X'` |

Runtime errors (exit status 1 for `dp-average`, 2 for `dp-chk-sort`; the tool stops at the first
one and writes no result line):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `<tool>: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `<tool>: F: Permission denied` |
| FILE `F` is a directory | `<tool>: F: Is a directory` |
| A component of FILE `F` is not a directory | `<tool>: F: Not a directory` |
| Any other open or read failure of FILE `F` | `<tool>: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| `dp-average`: token `K` on line `L` of source `S` is not a valid *real* | `dp-average: S:L: invalid number 'K'` |
| `dp-average`: selected value `K` on line `L` of source `S` makes the sum infinite | `dp-average: S:L: arithmetic overflow at 'K'` |
| `dp-chk-sort`: token `K` on line `L` of source `S`, read before any inversion, is not a valid *integer* | `dp-chk-sort: S:L: invalid integer 'K'` |
| Standard output cannot be written (other than a broken pipe) | `<tool>: write error` |

`file is not sorted` is an answer, not a diagnostic: it is written to standard output, and
nothing is written to standard error.

## 7. Verification

The `dp-average` test data are chosen so that the printed digits do not depend on the
summation order or on compensated summation; FR-04 requires the exact order nonetheless, and
code review checks it.

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01, FR-03, FR-05 … FR-12, FR-14, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases; every case has several steps) | FR-01 … FR-15 |
| Unit test (written by the implementer) | FR-02 … FR-10, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-08 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-average < numbers.txt` | FR-01, FR-03 … FR-05 (the textbook's example) |
| 02 | `dp-average nonpos.txt` | FR-03, FR-05 (`no positive numbers read`) |
| 03 | `dp-average bad.txt` | FR-06 (no result line, CONV-34) |
| 04 | `dp-average --help` | FR-12 |
| 05 | `dp-chk-sort sorted.txt` | FR-07 … FR-09 (equal neighbors, exit 0) |
| 06 | `dp-chk-sort < unsorted.txt` | FR-01, FR-08, FR-09 (exit 1) |
| 07 | `dp-chk-sort stop.txt` | FR-08 (nothing after the inversion is validated) |
| 08 | `dp-chk-sort badint.txt` | FR-10 (exit 2) |
| 09 | `dp-chk-sort --help` | FR-12 |
| 10 | `dp-chk-sort missing.txt` | FR-11 (exit 2) |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-03, FR-04, FR-05 |
| UR-02 | FR-05 |
| UR-03 | FR-07, FR-08, FR-09 |
| UR-04 | FR-08, NFR-02, NFR-03 |
| UR-05 | FR-09, FR-10, FR-11, §3.7 |
| UR-06 | FR-01, CONV-26 |
| UR-07 | FR-06, FR-10, CONV-33, CONV-34 |
| UR-08 | FR-11, CONV-16 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-04, FR-05, NFR-02, CONV-35 |
| UR-11 | FR-12, FR-13 |
| UR-12 | FR-14, FR-15 |
| UR-13 | NFR-01, NFR-02, CONV-03 |
| UR-14 | FR-14, CLI-CONV |
| UR-15 | FR-02, NFR-03, NFR-07 |
