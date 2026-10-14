# Software Requirements Specification (SRS) — dp-bargraph2, dp-grade

| Field | Value |
| :-- | :-- |
| Document ID | SRS-20 |
| Project | `20-bargraph-grade` — Modular Procedural Decomposition & Evaluation |
| Products | `dp-bargraph2`, `dp-grade` (canonical names) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-20) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-bargraph2` and `dp-grade`, and
the procedural decomposition each must have. It is complete and precise enough that
independent implementations in any programming language produce **byte-identical** output for
every invocation. It is the authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-bargraph2` draws the bar graph of Project 16 (`dp-bargraph`) — a title line, then one `*`
per two units of value — with the same input format, output, and diagnostics, but is built from
two named procedures. `dp-grade` runs an answer-driven loop: for each student it reads a
mid-term score, a final-exam score, and the weight of the mid term, and prints a pass/fail
grade; it reads its answers as tokens from a file or standard input, and can write the
textbook's prompts to standard error. Requirements that apply to one tool name it; all others
apply to both.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR | The bytes `0x0A` and `0x0D` |
| Whitespace byte | One of `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D` (CONV-32) |
| Input | The bytes of the FILE operand, or of standard input, with a trailing run of `0x1A` bytes ignored (CONV-37) |
| Source | The FILE operand exactly as given, or `-` for standard input (CONV-34) |
| Line, blank line, record, title, value, bar | As defined for `dp-bargraph2` in FR-02 … FR-05 (identical to SRS-16) |
| Token | A maximal run of non-whitespace bytes (CONV-32); used by `dp-grade` |
| Answer | The token that starts each round of `dp-grade`: 1 (compute a grade) or 0 (stop) |
| *m*, *f* | The mid-term and final-exam scores of one round (integers) |
| *w* | The mid-term weight of one round, as a binary64 value (CONV-33 *real*) |
| *W* | *w* in thousandths, an integer 0 … 1000 (FR-10) |
| *A* | The weighted average in thousandths of a point, an integer 0 … 10000 (FR-11) |
| Prompt | A byte string written to standard error before a read, only with `--prompt` (CONV-36) |

### 1.4 References
- URD-20: `specs/URD.md`
- SRS-16: `projects/16-bargraph/specs/SRS.md` (`dp-bargraph`)
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains both normative help texts)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §4.1

## 2. Overall description

### 2.1 Product perspective
`dp-bargraph2` and `dp-grade` are two standalone executables built from one project. Their
interfaces are the command line, the file named by the operand, standard input, standard
output, standard error, and the exit status. They belong to the applications-programming
track of the curriculum (Projects 11–52) and adapt the two programs of §4.1 of Johnsonbaugh &
Kalin, which introduces functions: the bar-graph program of §2.8 rewritten with procedures, and
a function that assigns a letter grade.

### 2.2 Product functions
1. `dp-bargraph2`: draw the bar graph of SRS-16 from a file or standard input, using a
   title-echoing procedure and a bar-drawing procedure.
2. `dp-grade`: repeatedly read an answer and, for answer 1, two scores and a weight; print
   `Grade is: P` or `Grade is: F` with an exactly specified threshold rule.
3. `dp-grade`: optionally write the textbook's prompts to standard error.
4. Both: report data errors with a line number; display help and version information; detect
   and report usage and file errors.

### 2.3 Constraints
- The tools MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior and, through NFR-05, the procedural structure
  of the code.

### 2.4 Assumptions
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- `dp-grade` may be used interactively, with standard input and standard error connected to a
  terminal.

### 2.5 Relationship to the textbook program (informative)
**Kept:** the bar graph of §2.8 and its decomposition into a procedure that echoes a title
line and reports the end of the input, and a procedure that prints ⌊size / 2⌋ asterisks and a
line feed; the grading loop, which continues while the answer is 1; the order of the three
values (mid term, final, weight); the formula *average* = *w* × *m* + (1 − *w*) × *f*; the
strict threshold (an average of exactly 7 fails); the output `Grade is: P` / `Grade is: F`; and
the two prompts, `Compute another grade (1 = Yes, 0 = No)? ` and
`Enter mid term, final, weight: `.

**Changed, and why:**
- `dp-bargraph2` has every improvement SRS-16 §2.5 lists for `dp-bargraph`, so that the two
  tools stay interchangeable (FR-01).
- The prompts are written only with `--prompt`, and to standard error (CONV-36), so standard
  output holds only the grades and can be redirected or compared. Blank lines that only
  separated the textbook's output from the echo of the user's typing are not written.
- The textbook evaluated the average in binary floating point, where a weight such as 0.2 is
  not exact: 0.2 × 7 + (1 − 0.2) × 7 evaluates to 7.000000000000001 and would pass, although
  the intended average is exactly 7. `dp-grade` uses the weight to the nearest thousandth and
  decides in integer arithmetic (FR-10, FR-11), so every grade is the one the decimal numbers
  imply, on every platform.
- Scores are limited to 0 … 10 and the weight to 0 … 1 (FR-09); the textbook did not check
  them. The scale of 10 matches the threshold of 7.
- The textbook stopped at any answer other than 1; `dp-grade` accepts only 0 and 1, and treats
  the end of the input in place of an answer as 0 (FR-08). Malformed and missing values are
  reported with the line number (FR-14) instead of producing an arbitrary grade.
- Both tools accept a FILE operand in addition to standard input.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics CONV-13 …
CONV-16, and exit statuses CONV-18. Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | `dp-grade` reads its input as tokens. `dp-bargraph2` reads lines, using the whitespace-byte set and line numbers of CONV-32. |
| CONV-33 | Scores, answers, and bar values use the *integer* grammar; the weight uses the *real* grammar. Each is further range-restricted (FR-04, FR-08, FR-09). |
| CONV-34 | All data errors use its format and standard messages (FR-06, FR-14). |
| CONV-35 | `FIX(w, 3)` defines the weight's precision (FR-10). No real number is written. |
| CONV-36 | `dp-grade` has `-p`, `--prompt` with two prompts (FR-13). `dp-bargraph2` has no prompts. |
| CONV-37 | Applies to the input of both tools (FR-02, FR-07). |
| CONV-38 | Not applicable. |

**Override:** CONV-04, for `dp-bargraph2` only, exactly as in SRS-16: one CR before a title's
LF is removed (FR-02).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-bargraph2 [FILE]
dp-grade [-p | --prompt] [FILE]
dp-bargraph2 --help | --version
dp-grade --help | --version
```

### 3.2 Options

| Short | Long | Argument | Tool | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | `dp-grade` | Write the prompts of FR-13 to standard error |
| — | `--help` | none | both | Print the help text and exit 0 |
| — | `--version` | none | both | Print the version line and exit 0 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands
Each tool accepts at most one FILE operand. With no operand, or with the operand `-`, it reads
standard input. Every token after `--` is an operand. The operand is used and echoed exactly as
given (CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (CONV-26), as raw bytes with no newline
translation on any platform. `dp-bargraph2` reads it to the end before writing; `dp-grade`
reads it incrementally (FR-07) and stops reading after the answer 0.

### 3.5 Standard output
`dp-bargraph2`: the bar graph (FR-05). `dp-grade`: one grade line per round (FR-12). Nothing on
a usage error or a file error.

### 3.6 Standard error
Diagnostics (section 6) and, for `dp-grade --prompt`, the prompts (FR-13).

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The whole input was processed (for `dp-grade`: the session ended with the answer 0 or at the end of the input), or `--help` / `--version` was handled |
| 1 | The input could not be read (FR-15), it contains a data error (FR-06, FR-14), or standard output could not be written |
| 2 | Usage error (FR-18) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `*×N` a run of N asterisks, and the named files are
the fixtures in `tests/fixtures/`.

### 4.1 dp-bargraph2

FR-02 … FR-06 restate SRS-16 FR-01 … FR-10 so that this document is self-contained.

**FR-01: Equivalence with dp-bargraph.**
For every argument list and every input, `dp-bargraph2` MUST write the same standard output,
the same standard error with `dp-bargraph` replaced by `dp-bargraph2`, and the same exit status
as `dp-bargraph` (SRS-16), apart from the help text (FR-16) and version line (FR-17), which
name `dp-bargraph2`.
*AC:* `dp-bargraph2 bargraph.in` writes exactly the textbook's five bars (46, 45, 37, 35, and 21
asterisks), as `dp-bargraph bargraph.in` does. *(UR-01)*

**FR-02: Input and lines (dp-bargraph2).**
The tool MUST read the FILE operand, or standard input when there is no operand or it is
`-`, as raw bytes. The input is *text data* (CONV-37): a run of `0x1A` bytes at its very end
is removed first. Each LF ends a line; if the last byte is not LF, the bytes after the last LF
form a final line; an empty input has no lines. From each line its LF and then one CR immediately before that LF (or, for a final line
without LF, one CR at the end of the input) are removed; any other CR is data. A line's number
is 1 plus the number of LF bytes before its first byte (CONV-32). A *blank line* is an empty
line or one consisting only of whitespace bytes.
*AC:* `bargraph.in` (final `0x1A`) draws five records; `crlf.txt` draws what its LF version
draws. *(UR-01, UR-03)*

**FR-03: Records and titles (dp-bargraph2).**
Every line after the last non-blank line is ignored. The remaining lines are taken in pairs: a
title line, then a value line. A title is the line content of FR-02 with no other change; it
MAY be empty and MAY contain any bytes, including leading and trailing spaces, bytes that are
not valid UTF-8, and `0x1A`.
*AC:* in `edge.txt`, `  Spaced  Title  ` keeps its spaces and an empty title gives an empty
line. *(UR-01)*

**FR-04: Values (dp-bargraph2).**
A value line, with all leading and trailing whitespace bytes removed, MUST be one token in the
*integer* grammar of CONV-33, with a value in **0 … 10000**.
*AC:* `edge.txt` accepts `+9`, `007`, and ` \t 13 \t`. *(UR-01)*

**FR-05: Output (dp-bargraph2).**
For each record, in order, the tool MUST write the title and LF, then ⌊*value* / 2⌋ asterisks
(`0x2A`) and LF, and nothing else. An input with no records produces no output and exit
status 0. A record MUST be written, and standard output flushed, as soon as its value line has
been read and validated, without waiting for the end of the input; the only lookahead allowed
is past blank lines (are they trailing?) and past a run of `0x1A` bytes (does it end the
input?).
*AC:* `dp-bargraph2 < edge.txt` → the title `Zero Value`, an empty bar, …, `Padded Value`,
`*×6`. *(UR-01)*

**FR-06: Data errors (dp-bargraph2).**
Each record is validated completely before any of it is written. At the first record that
cannot be drawn, the tool MUST write `dp-bargraph2: <source>:<line>: <message>` and exit with
status 1, having written the records before it in full and nothing of it or after it:

| Condition | `<line>` | `<message>` |
| :-- | :-- | :-- |
| The trimmed value line is not a valid *integer* | the value line's number | `invalid integer '<text>'` |
| The value is outside 0 … 10000 | the value line's number | `value out of range '<text>'` |
| The input ends after a title | the end-of-input line number (CONV-32) | `unexpected end of input` |

`<text>` is the value line without leading and trailing whitespace bytes (empty for a blank
value line).
*AC:* the hidden fixture `badvalue.txt` → `Superman\n*×35\n` and
`dp-bargraph2: badvalue.txt:4: invalid integer 'forty-two'`, exit 1. *(UR-02)*

### 4.2 dp-grade

**FR-07: Input and tokens (dp-grade).**
The input — the FILE operand, or standard input when there is no operand or it is `-` — is
opened before anything is written (in particular before the first prompt). It is *text data*
(CONV-37) and is read as tokens (CONV-32), so spaces, TABs, line breaks, and CRLF line endings
separate values equally. A token's line number follows CONV-32. The input MUST be
read incrementally: a token is complete, and MUST be processed, as soon as the whitespace byte
that follows it has been read, without waiting for further input; the only permitted lookahead
is a run of `0x1A` bytes, which is held back until the next byte shows whether it reaches the
end of the input. A `0x1A` byte that does not reach the end is ordinary data and belongs to a
token.
*AC:* `readme-grades.txt` holds one answer per line and three values per line; the hidden
fixture `eof-answer.txt`, with CRLF line endings and a final `0x1A`, is read like its LF
version. *(UR-04, UR-03)*

**FR-08: Session (dp-grade).**
The tool MUST run the following loop:

1. Write prompt P1 (FR-13). Read the next token. If the input has ended, end the session.
2. The token is the answer. It MUST be an *integer* (CONV-33) with the value 0 or 1.
3. If the answer is 0, end the session. The rest of the input is not read or validated.
4. If the answer is 1, write prompt P2, read and validate *m*, *f*, and *w* (FR-09), write the
   grade line (FR-12), and continue with step 1.

When the session ends, the tool exits with status 0. An end of the input in place of an answer
is therefore the same as the answer 0.
*AC:* `dp-grade -p stop.txt` (the single answer 0) → stdout empty, stderr P1, exit 0;
`readme-grades.txt` gives three grade lines. *(UR-04, UR-05)*

**FR-09: Scores and weight (dp-grade).**
In each round the three tokens after the answer are, in order: the mid-term score *m*, an
*integer* in **0 … 10**; the final-exam score *f*, an *integer* in **0 … 10**; and the mid-term
weight *w*, a *real* (CONV-33) with **0 ≤ *w* ≤ 1**, compared as a binary64 value (so `-0` is
accepted as 0, and `1.0004` is out of range). Each token MUST be validated as soon as it has
been read, before the next token is read.
*AC:* `bad-score.txt` → the mid term `11` on line 4 is out of range; the hidden fixtures reject
the weights `1.0004` and `-0.0001` as out of range, `nan` as an invalid number, and the score
`8.0` as an invalid integer. *(UR-06)*

**FR-10: Weight precision (dp-grade).**
The weight is used to the nearest thousandth: *W* is the integer number of thousandths given by
`FIX(w, 3)` (CONV-35), that is, *w* rounded to three decimal places from its exact binary64
value, an exact tie going to the even digit. A weight written with at most three decimal places
is therefore used exactly as written.
*AC:* `0.5` → *W* = 500; `0.105` → 105; `.3e0` → 300; `-0` → 0; `0.7004` → 700; `0.7005` → 701
(its binary64 value is slightly above 0.7005); `0.0625` → 62 (an exact tie). *(UR-07)*

**FR-11: Grade rule (dp-grade).**
The tool MUST compute, in exact integer arithmetic,

*A* = *W* × *m* + (1000 − *W*) × *f*,

the weighted average *w* × *m* + (1 − *w*) × *f* in thousandths of a point, and the grade MUST
be `P` if *A* > 7000 and `F` otherwise. An average of exactly 7 is a fail. The decision MUST
NOT be made by comparing a binary floating-point average with 7.0.

| *m* | *f* | weight | *W* | *A* | Grade |
| --: | --: | :-- | --: | --: | :-- |
| 8 | 6 | 0.5 | 500 | 7000 | F |
| 8 | 7 | 0.5 | 500 | 7500 | P |
| 10 | 5 | 0.8 | 800 | 9000 | P |
| 7 | 7 | 0.2 | 200 | 7000 | F |
| 0 | 10 | 0.3 | 300 | 7000 | F |
| 10 | 4 | 0.501 | 501 | 7006 | P |
| 10 | 0 | 0.7004 | 700 | 7000 | F |

*AC:* `dp-grade readme-grades.txt` → `Grade is: F\nGrade is: P\nGrade is: P\n`;
`dp-grade weights.txt` → four `F` lines, then two `P` lines. *(UR-07, UR-08)*

**FR-12: Output (dp-grade).**
For each completed round the tool MUST write `Grade is: ` followed by `P` or `F` and LF to
standard output, and nothing else is ever written there. The line MUST be written, and standard
output flushed, before the next token is read.
*AC:* `dp-grade readme-grades.txt` → three lines and nothing else. *(UR-05, UR-08)*

**FR-13: Prompts (dp-grade).**
With `-p` or `--prompt`, the tool MUST write these prompts to standard error, with no line
feed, and flush standard error before the read that follows (CONV-36):

| Prompt | Exact bytes | Written |
| :-- | :-- | :-- |
| P1 | `Compute another grade (1 = Yes, 0 = No)? ` (41 bytes, ending in a space) | Before every read of an answer, including the first and one that reaches the end of the input |
| P2 | `Enter mid term, final, weight: ` (31 bytes, ending in a space) | Once per round, after a valid answer 1 and before the mid-term score is read; not before *f* or *w* |

Without the flag, no prompt is written. Standard output is the same with and without it.
*AC:* `dp-grade --prompt < readme-grades.txt` → stdout as without `--prompt`; stderr is P1 P2
P1 P2 P1 P2 P1 concatenated. *(UR-09)*

**FR-14: Data errors (dp-grade).**
At the first invalid or missing token, the tool MUST write one CONV-34 diagnostic,
`dp-grade: <source>:<line>: <message>`, read no further input, write no grade for the current
round, and exit with status 1. Grade lines already written are kept.

| Condition | `<line>` | `<message>` |
| :-- | :-- | :-- |
| An answer or score is not a valid *integer* | the token's line | `invalid integer '<token>'` |
| An answer is not 0 or 1; a score is outside 0 … 10 | the token's line | `value out of range '<token>'` |
| The weight is not a valid *real* | the token's line | `invalid number '<token>'` |
| The weight is outside 0 … 1 | the token's line | `value out of range '<token>'` |
| The input ends after an answer 1 and before the weight | the end-of-input line number | `unexpected end of input` |

A prompt already written stays written, so with `--prompt` the diagnostic follows the last
prompt on the same line of standard error; P2 is not written when the answer is invalid.
*AC:* `bad-score.txt` → stdout `Grade is: P\n`, stderr
`dp-grade: bad-score.txt:4: value out of range '11'\n`, exit 1; `cut-record.txt` (`1\n8 6\n`) →
`dp-grade: cut-record.txt:3: unexpected end of input`, exit 1. *(UR-06)*

### 4.3 Both tools

**FR-15: File errors.**
If the FILE operand cannot be opened, or is a directory, the tool MUST write
`<tool>: <FILE>: <reason>` with the CONV-16 reason, write nothing to standard output (and, for
`dp-grade`, no prompt), and exit with status 1. If a read error occurs later, the output already
written is kept and the same diagnostic is written. A failure to read standard input is reported with `<FILE>` = `-`.
*AC:* `dp-grade missing.txt` → `dp-grade: missing.txt: No such file or directory`, exit 1.
*(UR-10)*

**FR-16: Help.**
`--help` MUST write the tool's help text from user-manual §"Help output" byte-for-byte to
standard output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-grade --help` and `dp-bargraph2 --help` match the user manual exactly;
`dp-grade a b --help` prints the help. *(UR-11)*

**FR-17: Version.**
`--version` MUST write `<tool> (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* `dp-grade --version` → `dp-grade (dialectic-playground) 1.0.0\n`. *(UR-11)*

**FR-18: Usage errors.**
Unknown options, and an argument given to an option that takes none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. A second operand MUST be reported as `<tool>: extra operand '<second operand>'`;
operands are checked only after the whole argument list has been scanned (CONV-12).
`dp-bargraph2` has no `-p` option: `dp-bargraph2 -p` is an invalid option.
*AC:* `dp-grade a b` → `dp-grade: extra operand 'b'`; `dp-grade -x --help` →
`dp-grade: invalid option -- 'x'`; `dp-grade --prompt=1` →
`dp-grade: option '--prompt' doesn't allow an argument`; each exits 2. *(UR-12)*

**FR-19: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output MUST be byte-identical on Linux, macOS, and Windows, and every line the tools generate MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: platform-independent arithmetic and interactive I/O | `dp-grade` MUST decide every grade with the integer rule of FR-11, so no result can depend on extended-precision floating-point registers (for example x87), fused multiply-add contraction, compiler optimization level, or the decimal-to-binary rounding of the weight. Inputs MUST be read in binary mode on every platform, and only FR-02 and FR-07 may interpret CR and `0x1A`; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Prompts MUST reach a terminal before the program waits for input, and each output line before the next read, on every platform: standard error and standard output MUST be flushed explicitly where the platform buffers them. | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance | Each tool MUST start, process the public fixtures, and exit in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). `dp-grade` MUST process 100 000 rounds from a file in under 2 s native (20 s interpreted), and `dp-bargraph2` a 1 MiB input in under 1 s native (5 s interpreted); memory MUST NOT grow with the number of rounds or records. | Measurement |
| NFR-04 | Robustness | The tools MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24). Tokens and lines of any length MUST be handled; an integer outside the 64-bit range is `invalid integer`, never overflowed. A broken pipe on standard output ends a tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability: procedural decomposition | `dp-bargraph2` MUST be built from (a) one procedure that reads one title line, writes it with its LF, and reports to its caller whether the input was exhausted instead (the textbook's `echo_line`), and (b) one procedure that receives a value and writes its bar — ⌊value / 2⌋ asterisks and LF — and does nothing else (the textbook's `print_stars`); its main loop only sequences these procedures with the reading and validation of the value, and never writes titles or asterisks itself. In `dp-grade`, the grade decision MUST be one function that receives *m*, *f*, and the weight (as *W*, or as *w* converted inside the function by FR-10) and returns the letter `P` or `F`, with no input, output, or prompting; token reading, prompting, validation, and output are separate units. Command-line handling common to both tools MUST be shared rather than duplicated (Principles 3, 13, 18). | Design review |
| NFR-06 | Testability | The bar procedure, record validation, the weight conversion of FR-10, and the grade function MUST be pure or testable on in-memory streams, and covered by unit tests that include every row of the table in FR-11, the scores 0 and 10, and the weights 0, 1, 0.0005, and 0.9995. The `dp-grade` tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work for both tools: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tools MUST read only the FILE operand or standard input, and MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2) are each followed by `Try '<tool> --help' for more information.`,
where `<tool>` is `dp-bargraph2` or `dp-grade`.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (for `dp-bargraph2`, including `-p`) | `<tool>: invalid option -- 'x'` |
| Unknown long option token `T` | `<tool>: unrecognized option 'T'` |
| `--help=…` / `--version=…`; `--prompt=…` (dp-grade) | `<tool>: option '--help' doesn't allow an argument` (or `'--version'`, `'--prompt'`) |
| A second operand `X` | `<tool>: extra operand 'X'` |

File errors (exit status 1):

| Trigger | Exact message |
| :-- | :-- |
| FILE does not exist | `<tool>: FILE: No such file or directory` |
| Access to FILE is denied | `<tool>: FILE: Permission denied` |
| FILE is a directory | `<tool>: FILE: Is a directory` |
| A component of FILE is not a directory | `<tool>: FILE: Not a directory` |
| Any other open or read failure | `<tool>: FILE: Input/output error` |
| Any of the above for standard input | the same message with `FILE` = `-` |

Output errors (exit status 1):

| Trigger | Exact message |
| :-- | :-- |
| Standard output cannot be written (other than a broken pipe, CONV-25) | `<tool>: write error` |

Data errors (exit status 1; earlier output kept):

| Tool | Trigger | Exact message |
| :-- | :-- | :-- |
| dp-bargraph2 | Value line is not one *integer* | `dp-bargraph2: SOURCE:LINE: invalid integer 'TEXT'` |
| dp-bargraph2 | Value outside 0 … 10000 | `dp-bargraph2: SOURCE:LINE: value out of range 'TEXT'` |
| dp-bargraph2 | Title with no value line | `dp-bargraph2: SOURCE:LINE: unexpected end of input` |
| dp-grade | Answer or score not an *integer* | `dp-grade: SOURCE:LINE: invalid integer 'TOKEN'` |
| dp-grade | Answer not 0 or 1; score outside 0 … 10; weight outside 0 … 1 | `dp-grade: SOURCE:LINE: value out of range 'TOKEN'` |
| dp-grade | Weight not a *real* | `dp-grade: SOURCE:LINE: invalid number 'TOKEN'` |
| dp-grade | Input ends inside a round | `dp-grade: SOURCE:LINE: unexpected end of input` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-05, FR-07 … FR-14, FR-16 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 01, 02, 05, 06, 07, 09, and 10 have several steps) | FR-01 … FR-04, FR-06 … FR-11, FR-13 … FR-19 |
| Unit test (written by the implementer) | FR-02 … FR-06, FR-09 … FR-11, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review / demonstration | FR-07 (interactive timing), NFR-02, NFR-05, NFR-08 |

Fixtures (`tests/fixtures/`): `bargraph.in` is the textbook's data file, byte for byte (five
records and a final `0x1A`); `edge.txt` is the bar-graph edge-case file of Project 16;
`readme-grades.txt` holds the three rounds 8 6 0.5, 8 7 0.5, and 10 5 0.8, then the answer 0;
`stop.txt` holds only the answer 0; `weights.txt` holds rounds whose weights (0.2, 0.3, 0.7,
0.105, 0.501, 0.499) are not exact in binary floating point; `bad-score.txt` has a valid round,
then a mid term of 11 on line 4; `cut-record.txt` ends after two of the three values.

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-bargraph2 bargraph.in` | FR-01 … FR-05 (textbook data, Ctrl-Z) |
| 02 | `dp-bargraph2 < edge.txt` | FR-03 … FR-05 |
| 03 | `dp-grade readme-grades.txt` | FR-07, FR-08, FR-11, FR-12 |
| 04 | `dp-grade --prompt < readme-grades.txt` | FR-13 |
| 05 | `dp-grade -p stop.txt` | FR-08, FR-13 |
| 06 | `dp-grade weights.txt` | FR-10, FR-11 |
| 07 | `dp-grade bad-score.txt` | FR-09, FR-14 |
| 08 | `dp-grade cut-record.txt` | FR-14 |
| 09 | `dp-grade --help` | FR-16 |
| 10 | `dp-bargraph2 --help` | FR-16 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01 … FR-05 |
| UR-02 | FR-06 |
| UR-03 | FR-02, FR-07, NFR-02 |
| UR-04 | FR-07, FR-08 |
| UR-05 | FR-08, FR-12 |
| UR-06 | FR-09, FR-14 |
| UR-07 | FR-10, FR-11, NFR-02 |
| UR-08 | FR-11, FR-12 |
| UR-09 | FR-13 |
| UR-10 | FR-15 |
| UR-11 | FR-16, FR-17 |
| UR-12 | FR-18, FR-19 |
| UR-13 | NFR-01, CONV-03 |
| UR-14 | FR-18, CLI-CONV |
| UR-15 | NFR-05, NFR-06 |
| UR-16 | NFR-03 |
| UR-17 | NFR-07 |
