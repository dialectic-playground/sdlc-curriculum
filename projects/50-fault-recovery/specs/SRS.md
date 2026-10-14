# Software Requirements Specification (SRS) — dp-divide

| Field | Value |
| :-- | :-- |
| Document ID | SRS-50 |
| Project | `50-fault-recovery` — Structured Exception Handling & Fault Recovery |
| Product | `dp-divide` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-50) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-divide`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-divide` reads real numbers as tokens from standard input or from one file, two at a time.
For each pair it writes one line giving the dividend, the divisor, and the quotient, each
rounded to six decimal places. A pair whose divisor is zero, or whose quotient overflows, is a
fault: the tool writes two fixed recovery lines and ends with status 0. It can write a prompt
to standard error before each pair is read. It reports invalid numbers, an incomplete final
pair, and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| End-of-input line number | 1 plus the number of LF bytes in the whole input (CONV-32) |
| Number | The IEEE 754 binary64 value of a token that is a valid *real* (CONV-33); it is always finite |
| Pair | The (2*k* − 1)-th and 2*k*-th tokens of the input, for *k* = 1, 2, …: the dividend *a* and the divisor *b* |
| Quotient | *q* = *a* ⊘ *b*, the IEEE 754 binary64 division of *a* by *b* with rounding to nearest, ties to even |
| Fault | A pair for which the division routine raises a fault (FR-05) |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |
| `FIX(x, 6)` | *x* rounded to exactly 6 digits after the decimal point, as defined in CONV-35 |

### 1.4 References
- URD-50: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- IEEE 754-2019, *Standard for Floating-Point Arithmetic* (binary64 division, rounding)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §11.2 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-divide` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §11.2 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*. Its companion in the same chapter,
`dp-assert-sort` (Project 49), treats the other side of defensive programming: stopping at a
violated assertion instead of recovering.

### 2.2 Product functions
1. Read numbers as real tokens, two at a time, until the end of the input.
2. Divide each pair in a division routine that raises a fault for a zero divisor or an
   overflowing quotient.
3. Write one result line per pair as soon as the pair has been read.
4. On a fault, transfer control to the recovery point, write the two recovery lines, and end
   with status 0.
5. Optionally write a prompt to standard error before each pair is read.
6. Report invalid numbers, an incomplete final pair, and unreadable input files.
7. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, apart from the design requirements of
  NFR-05.
- Numbers MUST be represented and divided as IEEE 754 binary64 values (FR-04).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-03.
- The input may contain any bytes; only tokens that match the *real* grammar are numbers.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §11.2 installs a handler for the arithmetic-fault signal and sets a
recovery point (a non-local jump buffer) before its loop. In the loop it prompts
`Two floats: `, reads two floats, and prints `a / b == q`, each with six decimal places. When a
division by zero raises the signal, the handler prints `Signal status == 8.` (8 being the
signal's number) and jumps back to the recovery point, which prints
`At jump point and about to exit...` and ends the program normally. `dp-divide` keeps:

- the result line exactly: `FIX(a, 6) / FIX(b, 6) == FIX(q, 6)`, one per pair (FR-04);
- the two recovery lines word for word, including the status 8, the full stop after it, and
  the three dots, written to standard output as the textbook program wrote them, and the
  normal exit status 0 after recovery (FR-06);
- the prompt text `Two floats: `, written once before each pair (FR-07);
- the structure: the fault is detected in the division routine and handled at a single
  recovery point outside the loop, reached by a non-local transfer of control (NFR-05).

It changes the following, for the reasons given:

- **Faults are defined by tests, not by traps.** IEEE 754 arithmetic, the default on every
  current platform, does not trap on a floating-point division by zero: it quietly produces an
  infinity or a NaN, so on most systems the textbook program would print `inf` instead of
  recovering. The tool therefore defines the faults by explicit tests of the operands and the
  result (FR-05): a divisor equal to zero (either sign, which also covers 0 ÷ 0, the only
  NaN-producing pair) and a quotient that overflows to an infinity. These are the cases in
  which IEEE 754 signals the *division-by-zero* and *overflow* exceptions for a division of
  finite numbers. A quotient that underflows is not a fault; it is rounded as usual, and
  `FIX` writes it as `0.000000` or a small multiple of 0.000001 (FR-04). The number 8 in the
  status line is now fixed text, not the platform's signal number (NFR-02).
- **Binary64 instead of single precision.** The textbook reads `float` values. The tool reads
  binary64 values (CONV-33), the curriculum's single real type, so results agree across
  languages that have no single-precision type.
- **No prompt on standard output, no echoed input.** The textbook's dialogue interleaves the
  prompt, the typed numbers, and the results on the terminal. Here prompts are optional and go
  to standard error (FR-07), so redirected output holds only results and recovery lines.
- **Input sources and the end of the input.** Besides standard input, one FILE operand may be
  named (FR-01). The end of the input at a pair boundary ends the run normally with status 0
  and without the recovery lines, which belong to a fault (FR-03). CRLF line endings and a
  trailing Ctrl-Z marker are accepted (FR-02).
- **Invalid input is diagnosed.** A token that is not a number, or a final pair with only one
  number, makes the textbook's reading loop misbehave or stop silently. `dp-divide` reports
  it with its line number and exits with status 1 (FR-08, FR-09).
- **Streaming is required.** Each result is written and flushed before more input is read
  (FR-03), so the tool answers immediately at a keyboard even when its output is a pipe.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
*real* grammar, with no further restriction), CONV-34 (data diagnostics, with the standard
messages `invalid number` and `unexpected end of input` and the default consequences), CONV-35
(every number is written as `FIX(x, 6)`), CONV-36 (`-p`, `--prompt`), and CONV-37 (the input
is *text data*). CONV-38 does not apply, because nothing is random. Option syntax follows
CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of
CONV-18: a recovered fault is a success (status 0), because recovering from it is the tool's
specified behavior. Standard input is read as permitted by CONV-26. `dp-divide` copies no input
bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-divide [-p | --prompt] [FILE]
dp-divide --help
dp-divide --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | off | Write the prompt `Two floats: ` to standard error before each pair is read (FR-07) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The result lines (FR-04), in input order, followed by the two recovery lines (FR-06) if a fault
occurred. Nothing else. On a usage error, or when `--help` / `--version` is handled, the output
is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error
Prompts (FR-07, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds, whether or not a fault occurred.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The input ended at a pair boundary (including an empty input), or a fault occurred and the tool recovered from it (FR-06), or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-10), it contained an invalid number (FR-08) or ended in the middle of a pair (FR-09), or standard output could not be written |
| 2 | Usage error (FR-13) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and `textbook.txt`, `pairs.txt`, `mixed.txt`,
`bad.txt`, and `odd.txt` are the public fixture files in `tests/fixtures/`: `textbook.txt` is
`10.0 2.0\n10.0 0.0\n`; `pairs.txt` is `12.0 4.0\n1 3\n-7.5 2\n2.5e3 -0.5\n`; `mixed.txt` is
`+1 8\r\n.5\t-.25\r\n\r\n1e-7 -10 22 7\n`; `bad.txt` is `6 3\n4 two\n1 1\n`; `odd.txt` is
`9 3\n\n5\n\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
*AC:* `dp-divide < pairs.txt`, `dp-divide pairs.txt`, and `dp-divide - < pairs.txt` write the
same lines. *(UR-01, UR-08)*

**FR-02: Tokens and numbers.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order and grouped into pairs. Each token MUST be a valid *real* (CONV-33); its
value is the IEEE 754 binary64 value nearest to the token's exact decimal value (ties to even),
and a token whose value would overflow to an infinity is invalid. A sign, a missing integer or
fraction part (`.5`, `5.`), and an exponent (`2.5e3`) are allowed; `-0` is negative zero. Line
structure has no meaning: the two numbers of a pair may share a line or not, several pairs may
share a line, and numbers may be separated by any mixture of space, TAB, VT, FF, CR, and LF.
A token that is not a valid *real* is handled by FR-08.
*AC:* `dp-divide mixed.txt` → the pairs (1, 8), (0.5, −0.25), (1e−7, −10), and (22, 7), exit 0.
*(UR-01, UR-09)*

**FR-03: Pairs and streaming.**
Pairs MUST be processed one at a time, in input order. For each pair the tool (1) writes the
prompt if enabled (FR-07), (2) reads the dividend token, (3) reads the divisor token, and
(4) divides (FR-05) and writes either the result line (FR-04) or the recovery lines (FR-06).
Each token is validated (FR-08) as soon as it is complete, so an invalid dividend is reported
before the divisor is read. As soon as a pair's divisor is complete and valid, the tool MUST
write its line to standard output and flush standard output, before it waits for any further
input bytes. The tool MUST NOT wait for the end of the input before writing a line, and MUST
NOT read the input beyond what it needs to complete the current token, apart from ordinary
buffering of bytes that are already available. When the end of the input is reached where a
dividend would be read, the tool exits with status 0 and writes nothing more. An empty input,
or one that contains only whitespace and a trailing Ctrl-Z run, produces no output and exit
status 0.
*AC:* `dp-divide` with empty standard input → stdout and stderr empty, exit 0. At a terminal,
typing `10 2` and Enter shows `10.000000 / 2.000000 == 5.000000` before anything else is typed
(manual check). *(UR-01, UR-03)*

**FR-04: Result line.**
For a pair (*a*, *b*) that is not a fault, the tool MUST write exactly the line

```text
<A> / <B> == <Q>
```

where `<A>` = `FIX(a, 6)`, `<B>` = `FIX(b, 6)`, and `<Q>` = `FIX(q, 6)` (CONV-35), *q* being
the quotient (section 1.3): the correctly rounded binary64 result of one division of *a* by
*b*, with no extended intermediate precision and no other operation. The line ends with a
single LF; there is one space on each side of `/` and of `==`, and no leading or trailing
spaces. `FIX` is applied to the exact binary64 values, so a large value is written with all
its integer digits (for example 1.5 × 10³⁰⁸ is written with 309 digits before the decimal
point), a value whose magnitude is below 0.0000005 is written `0.000000`, and no minus sign is
written for a value that rounds to zero (negative zero, `-1e-7`). The numbers are written as
their values, not as their tokens were spelled.
*AC:* `dp-divide pairs.txt` → stdout
`12.000000 / 4.000000 == 3.000000\n1.000000 / 3.000000 == 0.333333\n-7.500000 / 2.000000 == -3.750000\n2500.000000 / -0.500000 == -5000.000000\n`,
stderr empty, exit 0; in `mixed.txt` the pair `1e-7 -10` gives
`0.000000 / -10.000000 == 0.000000`. *(UR-02, UR-12)*

**FR-05: Faults.**
The division of a pair MUST be performed by one division routine (NFR-05), which raises a
fault, instead of returning a quotient, in exactly these cases:

1. **Zero divisor:** *b* is zero, positive or negative (`0`, `0.0`, `-0`, `0e5`, and any token
   whose value rounds to zero, such as `1e-400`). This includes *a* = 0, which is the only pair
   of finite numbers whose quotient is NaN.
2. **Overflow:** *b* is not zero and the quotient *q* is +∞ or −∞, that is, the exact quotient's
   magnitude rounds to a value beyond the largest finite binary64 number
   (1.7976931348623157 × 10³⁰⁸).

No other pair is a fault. In particular a quotient that underflows (is subnormal or rounds to
zero) is an ordinary result, and a divisor that is written as `0.000000` by `FIX` but is not
zero (such as `1e-8`) is not a zero divisor. The faults MUST be detected by testing the
divisor and the quotient as stated, not by relying on a hardware trap, signal, or
floating-point exception flag (NFR-02).
*AC:* `textbook.txt` (divisor `0.0` in the second pair), the pairs `-1 -0` and `0 0`, and the
pair `-1e308 0.1` are faults; `1.5e300 1e-8` and `5e-324 2` are not. *(UR-04)*

**FR-06: Recovery.**
When the division routine raises a fault, control MUST pass to the recovery point (NFR-05),
which writes to standard output exactly the two lines

```text
Signal status == 8.
At jump point and about to exit...
```

(each ending with one LF), flushes standard output, and ends the run with exit status 0. No
result line is written for the faulty pair, and the tool reads no further input: tokens after
the faulty pair, valid or not, are ignored, and no further prompt is written. The recovery
lines are the same for both kinds of fault. Nothing is written to standard error (apart from
the prompts already written under FR-07).
*AC:* `dp-divide < textbook.txt` → stdout
`10.000000 / 2.000000 == 5.000000\nSignal status == 8.\nAt jump point and about to exit...\n`,
stderr empty, exit 0; for a file holding `0 0\nnot numbers\n` → stdout the two recovery lines,
exit 0. *(UR-04, UR-05)*

**FR-07: Prompts.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 12 bytes `Two floats: `
(ending with one space, no LF). With prompts enabled, the tool MUST write the prompt to
standard error, and flush standard error, immediately before it reads the dividend of each
pair: once before the first token, and once after each result line. No prompt is written
before a divisor, and none after the recovery lines. A prompt is therefore also written before
the attempt that reaches the end of the input (CONV-36): an input of *n* complete pairs without
a fault produces *n* + 1 prompts; an input whose *k*-th pair is a fault produces *k* prompts;
and a data diagnostic in the *k*-th pair (FR-08, FR-09) follows the *k*-th prompt directly on
the same line. Prompts never change standard output. No prompt is written if the input cannot
be opened.
*AC:* `dp-divide --prompt < textbook.txt` → stdout as in FR-06, stderr `Two floats: ` twice
with no LF, exit 0. `dp-divide -p` with empty standard input → stderr `Two floats: `, stdout
empty, exit 0. *(UR-06)*

**FR-08: Invalid numbers.**
If a token is not a valid *real* (CONV-33) — including `inf`, `nan`, `1,5`, `0x10`, and a
number that overflows such as `1e309` — the tool MUST write
`dp-divide: <source>:<line>: invalid number '<token>'`, where `<source>` is as defined in
section 1.3, `<line>` is the token's line number (CONV-32), and `<token>` is the token's exact
bytes (CONV-34). The tool then stops: it reads no further input, writes nothing more to
standard output, and exits with status 1. Lines already written for earlier pairs are kept
(CONV-34).
*AC:* `dp-divide bad.txt` → stdout `6.000000 / 3.000000 == 2.000000\n`, stderr
`dp-divide: bad.txt:2: invalid number 'two'\n`, exit 1. A token `1` followed by a `0x1A` byte
and an LF gives `invalid number` because that Ctrl-Z byte does not end the input. *(UR-07)*

**FR-09: Incomplete final pair.**
If the end of the input is reached after a valid dividend, where its divisor would be read, the
tool MUST write `dp-divide: <source>:<line>: unexpected end of input`, where `<line>` is the
end-of-input line number (section 1.3), and exit with status 1. Lines already written for
earlier pairs are kept; nothing is written for the incomplete pair.
*AC:* `dp-divide odd.txt` → stdout `9.000000 / 3.000000 == 3.000000\n`, stderr
`dp-divide: odd.txt:5: unexpected end of input\n`, exit 1. *(UR-07)*

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-divide: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. Lines already written are kept. When standard input fails, `<source>` is
`-`.
*AC:* `dp-divide missing.txt` → stderr `dp-divide: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-divide subdir` where `subdir` is a directory →
`dp-divide: subdir: Is a directory`. *(UR-08)*

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-divide --help` matches the user manual exactly; `dp-divide extra --help` also prints
it. *(UR-10)*

**FR-12: Version.**
`--version` MUST write `dp-divide (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--pro` is unrecognized. A
second operand MUST be reported as `dp-divide: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
*AC:* `dp-divide textbook.txt pairs.txt` → `dp-divide: extra operand 'pairs.txt'`;
`dp-divide -x --help` → `dp-divide: invalid option -- 'x'`; `dp-divide --prompt=yes` →
`dp-divide: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case; `dp-divide -p - extra < textbook.txt` writes no
prompt. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: floating-point faults and formatting | Faults MUST be detected by the explicit tests of FR-05 on every platform. The implementation MUST NOT depend on, enable, or install handlers for floating-point traps, signals (SIGFPE), Windows structured exceptions, or the floating-point environment's exception flags, whose availability and behavior differ between operating systems, processors, compilers, and language runtimes; the status `8` is fixed text. Division MUST be one IEEE 754 binary64 operation, rounded to nearest, without extended intermediate precision or fused operations. Reading MUST convert each token correctly rounded (CONV-33) and writing MUST implement `FIX` exactly (CONV-35), independently of the C library's or runtime's own conversion quality and of the locale's decimal separator. The input MUST be read in binary mode, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output and standard error MUST be written in binary mode (CONV-03), and standard output MUST be flushed after each line (FR-03) even when it is a pipe or a file. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance | Processing 1 000 000 pairs (about 20 MiB of input) MUST take under 3 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of pairs; only the pair being read is held. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, numbers with very large or very small exponents, and every kind of fault. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the incremental tokenizer, number validation, the division routine, result formatting, the recovery point, and I/O MUST be separate units. The division routine MUST be the only place that tests for faults, and MUST signal a fault by a **non-local transfer of control** to a single recovery point established by the driver before the first pair is read — an exception that the driver catches, an error value that every intermediate caller propagates without inspecting it (such as `Result` with `?`), or a non-local jump — rather than by a sentinel quotient (an infinity, NaN, or a special number) that the caller must recognize. The recovery point MUST be the only place that writes the recovery lines and decides the exit status after a fault. | Design review |
| NFR-06 | Testability | The division routine MUST be unit-tested for ordinary pairs, a zero divisor of each sign, 0 ÷ 0, an overflowing quotient of each sign, the largest finite quotient, and an underflowing quotient; the recovery path MUST be tested through the driver. The `FIX` formatter MUST be unit-tested with values that need 309 integer digits, values just below and above 0.0000005, exact ties, and negative values that round to zero. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-divide --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-divide: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-divide: unrecognized option 'T'` |
| `--prompt=…`, `--help=…`, `--version=…` | `dp-divide: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X` | `dp-divide: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-divide: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-divide: F: Permission denied` |
| FILE `F` is a directory | `dp-divide: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-divide: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-divide: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *real* | `dp-divide: S:L: invalid number 'K'` |
| Source `S` ends after a dividend; `L` is the end-of-input line number | `dp-divide: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe) | `dp-divide: write error` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error (FR-07).

A fault is not an error: the recovery lines of FR-06 are written to standard output, and the
exit status is 0.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03 and 05 … 10 have several steps) | FR-02 … FR-14 |
| Unit test (written by the implementer) | FR-02 … FR-06, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-03 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-divide < textbook.txt` | FR-01, FR-04, FR-05, FR-06 |
| 02 | `dp-divide pairs.txt` | FR-01, FR-03, FR-04 |
| 03 | `dp-divide --prompt < textbook.txt` | FR-07 |
| 04 | `dp-divide mixed.txt` | FR-02 (CRLF, TAB, signs, `.5`, exponents), FR-04 (rounding to zero) |
| 05 | `dp-divide bad.txt` | FR-08 (lines kept, CONV-34) |
| 06 | `dp-divide odd.txt` | FR-09 |
| 07 | `dp-divide` (empty standard input) | FR-03 |
| 08 | `dp-divide missing.txt` | FR-10 |
| 09 | `dp-divide --help` | FR-11 |
| 10 | `dp-divide textbook.txt pairs.txt` | FR-13, FR-14 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-03 |
| UR-02 | FR-04, CONV-35 |
| UR-03 | FR-03, NFR-02 |
| UR-04 | FR-05 |
| UR-05 | FR-06, NFR-05 |
| UR-06 | FR-07, CONV-36 |
| UR-07 | FR-08, FR-09, CONV-33, CONV-34 |
| UR-08 | FR-01, FR-10, CONV-16, CONV-26 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-11, FR-12 |
| UR-11 | FR-13, FR-14 |
| UR-12 | FR-04, FR-05, NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-13, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
