# Software Requirements Specification (SRS) — dp-stats

| Field | Value |
| :-- | :-- |
| Document ID | SRS-15 |
| Project | `15-stats` — Single-Pass Streaming Statistical Summary |
| Product | `dp-stats` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-15) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-stats`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-stats` reads real numbers as tokens from standard input or from one file until the end of
the input, in a single pass and in constant memory. It then writes a seven-line report giving
the number of values, their maximum, minimum, sum, and mean, and their population variance and
standard deviation, computed in a binary64 operation order that this SRS fixes completely and
written with six digits after the decimal point. An input without numbers produces a one-line
report. Invalid numbers, arithmetic overflow, and unreadable files are reported with fixed
messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Data item | The value of a token that is a valid *real* (CONV-33): the IEEE 754 binary64 number nearest to the token's decimal value |
| *N* | The number of data items in the input |
| *x*₁ … *x*_N | The data items, in input order |
| binary64 operation | An IEEE 754 binary64 addition (⊕), subtraction (⊖), multiplication (⊗), division (⊘), or square root (√), each computed as if exactly and then rounded **once** to binary64, round to nearest, ties to even, with subnormal results kept (never flushed to zero) |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |
| `FIX(x, 6)` | *x* written with exactly six digits after the decimal point, rounded from its exact binary64 value, with no negative zero (CONV-35) |

### 1.4 References
- URD-15: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- IEEE 754-2019, *Standard for Floating-Point Arithmetic* (binary64 format and operations)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §2.5 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-stats` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §2.5 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read real numbers as tokens until the end of the input, each exactly once.
2. Keep five running values — count, maximum, minimum, sum, and sum of squares — and nothing
   else.
3. Derive the mean, population variance, and standard deviation in a fixed binary64 operation
   order.
4. Write a seven-line report, or a one-line report for an input without numbers.
5. Report invalid numbers, arithmetic overflow, and unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Every real-number computation MUST use binary64 operations exactly as FR-04 and FR-05 list
  them. Wider intermediate precision (for example x87 80-bit registers or a `long double`
  accumulator), fused multiply-add, reassociation, and compensated or pairwise summation MUST
  NOT be used, because each can change printed digits.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only tokens that match the *real* grammar are data items.
- *N* is below 2⁵³ in practice (an input of 2⁵³ numbers would exceed 16 PiB), so *N* converts
  to binary64 exactly; FR-05 nevertheless defines the conversion for every *N*.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §2.5 reads numbers from standard input until end-of-file, keeping only
the count, the maximum, the minimum, the sum, and the sum of squares, and then prints the
count, maximum, minimum, sum, mean, variance (the mean of the squares minus the square of the
mean), and standard deviation, or `0 data items read` when there were no numbers.
`dp-stats` keeps:

- the single pass and the five running values, so memory does not depend on the input length;
- the formulas, including the population (divide by *N*) variance computed as
  (sum of squares) / *N* − mean²;
- the report wording and layout exactly: seven lines in the textbook's order and with its
  labels, the count as a plain integer, and every real number with six digits after the
  decimal point (the textbook's default `%f` format). The label `data items` is kept for every
  count, including `1 data items read`, because scripts may match the line;
- the one-line report `0 data items read` for an input without numbers.

It changes the following, for the reasons given:

- **The arithmetic is fixed to the last bit** (FR-04, FR-05). The textbook leaves the order of
  operations, the precision of intermediates, and the rounding of printed digits to the
  compiler and library, so two correct builds can print different last digits. Because the
  variance formula subtracts two nearly equal quantities, rounding can make it slightly
  negative for identical values (three copies of 0.1 give −1.7 × 10⁻¹⁸), and the square root
  of a negative number is not a number; FR-05 clamps such a variance to zero before the square
  root, as the section's description advises.
- **Invalid input is diagnosed** (FR-08). A token that is not a number stops the textbook
  program's reading loop as if the input had ended, and it would report a summary of the
  numbers before it. `dp-stats` reports it with its line number, writes no report, and exits
  with status 1. Tokens that the C library would read as numbers but that are not numbers
  here, such as `inf`, `nan`, and hexadecimal floating constants, are invalid too (CONV-33).
- **Arithmetic overflow is diagnosed** (FR-08). With values beyond about 1.34 × 10¹⁵⁴, the
  textbook's sum of squares becomes infinite and its report prints `inf` or `nan`, which differ
  between C libraries. `dp-stats` reports the number that caused the overflow instead.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **No prompts.** The section's program shows no prompt: it is a filter that consumes a stream
  until end-of-file. `dp-stats` therefore has no `--prompt` option; a prompt before each of
  possibly millions of numbers would serve no one.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
*real* grammar), CONV-34 (data diagnostics, with the standard message `invalid number` and the
further message `arithmetic overflow at '<token>'` defined in FR-08; because the report is
written only after the whole input has been read, no output has been produced when either is
written), CONV-35 (`FIX(x, 6)` for every real number written), and CONV-37 (the input is *text
data*). CONV-36 does not apply, because the tool has no prompts (it does not accept `-p`), and
CONV-38 does not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12,
diagnostics follow CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard
input is read as permitted by CONV-26. `dp-stats` copies no input bytes to its output, so
CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-stats [FILE]
dp-stats --help
dp-stats --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (`--`, repetition, and scan order) follows CONV-07 … CONV-12.

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The report (FR-06 or FR-07), written once, after the whole input has been read. Nothing else.
On a data error or an input failure, nothing. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-10 … FR-13 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The whole input was read and the report written (including the report for an empty input), or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-09), it contained an invalid number or caused an arithmetic overflow (FR-08), or standard output could not be written |
| 2 | Usage error (FR-12) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n`, `\t`, and `\r` denote LF, TAB, and CR, and the following are the
public fixture files in `tests/fixtures/`: `three.txt` is `10.0 20.0 30.0\n`; `data.txt` is
`-5.0\t2.5e1  .5\r\n+3. -20.0\r\n\r\n  1.25E+1 -0.75\n`; `single.txt` is `42.0\n`; `same.txt` is
`0.1\n0.1\n0.1\n`; `round.txt` is `0.0078125 0.0234375\n`; `bad.txt` is `1.5 2.5\n3.5\n4,5 6\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. More than one operand is a
usage error (FR-12).
*AC:* `dp-stats < three.txt`, `dp-stats three.txt`, and `dp-stats - < three.txt` write the same
report. *(UR-01, UR-04)*

**FR-02: Tokens and data items.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order. Each token MUST be a valid *real* (CONV-33); its value, the binary64 number
nearest to the token's decimal value, is the next data item. A sign, a missing integer or
fraction part (`.5`, `3.`), an exponent in either case (`2.5e1`, `1.25E+1`), and leading zeros
are allowed. A token whose value is too small for binary64 is valid and becomes zero or a
subnormal number (`1e-400` is 0); `-0` is negative zero. Line structure has no meaning: data
items may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads
exactly like LF input. A token that is not a valid *real* is handled by FR-08. The conversion
MUST NOT depend on the locale: the decimal separator is always `.`.
*AC:* `dp-stats data.txt` reads the seven data items −5, 25, 0.5, 3, −20, 12.5, and −0.75, in
that order (see FR-06). *(UR-01, UR-09)*

**FR-03: Single pass in constant memory.**
The tool MUST read the input once, from beginning to end, and MUST process each data item as
soon as its token is complete. After a data item has been used to update the running values
of FR-04, it MUST NOT be kept. Apart from the token being read and ordinary I/O buffering, the
tool's memory use MUST NOT depend on the input (see NFR-03).
*AC:* processing 1 000 000 data items uses no more memory than processing 1 000 (measurement,
NFR-03). *(UR-03)*

**FR-04: Running values.**
The tool keeps five running values: the count *n*, the maximum *M*, the minimum *m*, the sum
*S*, and the sum of squares *Q*. For the first data item *x*₁ it MUST set *n* = 1, *M* = *x*₁,
*m* = *x*₁, *S* = *x*₁, and *Q* = *x*₁ ⊗ *x*₁. For each later data item *x*_k (k = 2 … *N*), in
input order, it MUST

1. set *M* = *x*_k if *x*_k > *M*, and set *m* = *x*_k if *x*_k < *m* (ordinary numeric
   comparisons of binary64 values);
2. set *S* = *S* ⊕ *x*_k;
3. set *Q* = *Q* ⊕ (*x*_k ⊗ *x*_k), where the product is rounded to binary64 before the
   addition (no fused multiply-add);
4. set *n* = *n* + 1 (an exact integer count).

So *S* = (…((*x*₁ ⊕ *x*₂) ⊕ *x*₃) …) ⊕ *x*_N, and *Q* is the same left-to-right sum of the
separately rounded squares. The overflow check of FR-08 follows these updates.
*(Informative: an implementation MAY instead start *S* and *Q* at zero and add every data item,
including the first; that changes at most the sign of a zero sum, which `FIX` never shows.)*
*AC:* for `same.txt`, *S* = 0.1 ⊕ 0.1 ⊕ 0.1 = 0.30000000000000004 (to 17 significant digits),
and the report shows `sum of all values read = 0.300000`. *(UR-02, UR-03, UR-05)*

**FR-05: Derived statistics.**
After the end of the input, if *N* ≥ 1, the tool MUST compute, in this order and with
binary64 operations:

1. *n̂* = *N* converted to binary64 (round to nearest, ties to even; exact for *N* ≤ 2⁵³);
2. mean *μ* = *S* ⊘ *n̂*;
3. *A* = *Q* ⊘ *n̂* and *B* = *μ* ⊗ *μ*;
4. variance *V* = *A* ⊖ *B*; if *V* < 0, then *V* = 0 (clamping);
5. standard deviation *D* = √*V*, the correctly rounded square root.

Neither *V* nor *D* is ever negative or not-a-number in the report. The clamping is required
because the subtraction can round below zero when every data item is equal.
*AC:* `dp-stats three.txt` → variance `66.666667`, standard deviation `8.164966`. For
`same.txt`, *A* ⊖ *B* = −1.734723475976807 × 10⁻¹⁸, so *V* = 0 and the report shows
`variance = 0.000000` and `standard deviation = 0.000000`. For the integers 1 … 1000,
*V* = 83333.25 exactly and the standard deviation is `288.674990`. *(UR-02, UR-05)*

**FR-06: Report format.**
If *N* ≥ 1, the report MUST be exactly these seven lines, in this order:

```text
<N> data items read
maximum value read = FIX(M, 6)
minimum value read = FIX(m, 6)
sum of all values read = FIX(S, 6)
mean = FIX(μ, 6)
variance = FIX(V, 6)
standard deviation = FIX(D, 6)
```

where `<N>` is the decimal of *N* (section 1.3) and `FIX(…, 6)` is replaced by the formatted
value (CONV-35): rounded from the exact binary64 value, an exact tie rounded to the even digit,
a `-` sign only for a negative value that does not round to zero, and as many integer digits
as the value needs (no exponent). Each line ends with a single LF; there are no other spaces
than the single spaces shown, no leading or trailing spaces, and no blank lines, header, or
units. The count line reads `data items` for every *N*, including 1.
*AC:* `dp-stats < three.txt` → stdout
`3 data items read\nmaximum value read = 30.000000\nminimum value read = 10.000000\nsum of all values read = 60.000000\nmean = 20.000000\nvariance = 66.666667\nstandard deviation = 8.164966\n`,
stderr empty, exit 0. `dp-stats data.txt` → `7 data items read`, maximum `25.000000`, minimum
`-20.000000`, sum `15.250000`, mean `2.178571`, variance `168.977041`, standard deviation
`12.999117`. `dp-stats round.txt` → maximum `0.023438` and minimum `0.007812` (exact ties
rounded to even), sum `0.031250`, mean `0.015625`, variance `0.000061`, standard deviation
`0.007812`. Data items −0.0000004, −0.0000001, and −0 give `0.000000` (never `-0.000000`) for
the maximum, minimum, sum, and mean. Data items −10¹⁵ and 10¹⁵ give
`variance = 1000000000000000019884624838656.000000`. *(UR-02, UR-05)*

**FR-07: Empty input.**
If the input contains no tokens (it is empty, or holds only whitespace and a trailing Ctrl-Z
run), the report MUST be exactly the line `0 data items read` + LF, and the exit status 0.
No mean, variance, or standard deviation is computed.
*AC:* `dp-stats` with empty standard input → stdout `0 data items read\n`, stderr empty,
exit 0. *(UR-06)*

**FR-08: Invalid numbers and arithmetic overflow.**
If a token is not a valid *real* (CONV-33) — including a token whose value overflows binary64,
such as `1e309`, and the spellings `inf`, `nan`, and `0x10` — the tool MUST write
`dp-stats: <source>:<line>: invalid number '<token>'`. If a token is a valid *real* *x*_k but,
after the updates of FR-04 for that data item, *x*_k ⊗ *x*_k, *S*, or *Q* is infinite, the tool
MUST write `dp-stats: <source>:<line>: arithmetic overflow at '<token>'`. In both messages
`<source>` is as defined in section 1.3, `<line>` is the token's line number (CONV-32), and
`<token>` is the token's exact bytes (CONV-34). The tool then stops: it reads no further input,
writes **no report**, and exits with status 1. Since the report is written only after the end
of the input, nothing has been written to standard output.
*(Informative: *S* cannot become infinite before *Q* does, and when *Q* is finite every value
of FR-05 is finite for any input of fewer than 2⁵⁰ data items, so no other check is needed.)*
*AC:* `dp-stats bad.txt` → stdout empty, stderr `dp-stats: bad.txt:3: invalid number '4,5'\n`,
exit 1. Data items `1e154`, `2.5`, `1e154` on lines 1 … 3 give
`arithmetic overflow at '1e154'` on line 3; a token `-2e154` gives `arithmetic overflow at
'-2e154'` on its own line, because its square overflows; `1e309` and `inf` give
`invalid number`; a token `2.0` followed by a `0x1A` byte and an LF gives
`invalid number '2.0␚'` (with the raw `0x1A` byte) because that Ctrl-Z byte does not end the
input. *(UR-07)*

**FR-09: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-stats: <source>: <reason>` with `<reason>` from the CONV-16 table, write
no report, and exit with status 1. When standard input fails, `<source>` is `-`.
*AC:* `dp-stats missing.txt` → stderr `dp-stats: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-stats subdir` where `subdir` is a directory →
`dp-stats: subdir: Is a directory`. *(UR-08)*

**FR-10: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-stats --help` matches the user manual exactly; `dp-stats extra --help` also prints it.
*(UR-10)*

**FR-11: Version.**
`--version` MUST write `dp-stats (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-12: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--he` is unrecognized. A second
operand MUST be reported as `dp-stats: extra operand '<second operand>'`, after the whole
argument list has been scanned (CONV-12).
*AC:* `dp-stats data.txt three.txt` → `dp-stats: extra operand 'three.txt'`;
`dp-stats -x --help` → `dp-stats: invalid option -- 'x'`; `dp-stats --version=1` →
`dp-stats: option '--version' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-13: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: reproducible floating-point results | Every printed digit MUST be the same on every platform, compiler, and CPU. Decimal-to-binary conversion MUST be correctly rounded and locale-independent (a C-locale or hand-written parser, never one that honors a `,` decimal separator). Arithmetic MUST be binary64 with one rounding per operation: no x87 extended-precision intermediates, no fused multiply-add contraction (for example, compilers that contract `q + x*x` by default on some CPUs MUST be told not to), no fast-math reassociation, and no flush-to-zero of subnormals. The square root MUST be correctly rounded. `FIX` MUST be computed from the exact binary value (some older C runtimes print zeros or wrong digits beyond the 17th significant digit; such a formatter MUST NOT be used). The input MUST be read in binary mode, so CR bytes reach the tokenizer and a `0x1A` byte is never treated as end-of-file by the I/O layer; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. | CI black-box tests on 3 OSes; code review; unit tests |
| NFR-03 | Performance | Processing 1 000 000 data items (about 8 MiB of input) MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the number of data items; only the token being read is held. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, numbers that overflow or underflow binary64, and subnormal numbers. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the incremental tokenizer, number validation, the accumulator, the summary computation, report formatting, and I/O MUST be separate units. The accumulator MUST be one unit that receives one data item at a time and holds only the five running values of FR-04; the summary computation MUST be one function of those values that is the only place the formulas of FR-05 appear. | Design review |
| NFR-06 | Testability | The accumulator, the summary function, and `FIX` MUST be pure or testable in memory, and covered by unit tests that include every acceptance value of FR-04 … FR-06, the clamping case of three data items 0.1, the integers 1 … 1000, a single data item, negative zero, and both overflow cases of FR-08. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-stats --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-stats: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-stats: unrecognized option 'T'` |
| `--help=…`, `--version=…` | `dp-stats: option '--help' doesn't allow an argument` (or `'--version'`) |
| A second operand `X` | `dp-stats: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one and writes no report):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-stats: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-stats: F: Permission denied` |
| FILE `F` is a directory | `dp-stats: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-stats: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-stats: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` is not a valid *real* | `dp-stats: S:L: invalid number 'K'` |
| Data item `K` on line `L` of source `S` makes its square, the sum, or the sum of squares infinite | `dp-stats: S:L: arithmetic overflow at 'K'` |
| Standard output cannot be written (other than a broken pipe) | `dp-stats: write error` |

## 7. Verification

The test data are chosen so that the printed digits do not depend on the operation order:
for every valid fixture, a two-pass computation, Welford's update, exact rational arithmetic,
and a fused multiply-add variant print the same report as FR-04 and FR-05. The tests thus
check the formulas, clamping, and formatting without penalizing an implementation for a
rounding difference in the last binary digit; NFR-02 and NFR-06 require the exact order
nonetheless, and code review checks it.

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01, FR-02, FR-04 … FR-10, FR-12, FR-13 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 05, 06, 08, 09, and 10 have several steps) | FR-01, FR-02, FR-04 … FR-13 |
| Unit test (written by the implementer) | FR-02, FR-04 … FR-06, NFR-06 |
| Measurement | FR-03, NFR-03 |
| Inspection / review | FR-03, NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-stats < three.txt` | FR-01, FR-04 … FR-06 (the textbook's example) |
| 02 | `dp-stats data.txt` | FR-02 (CRLF, TAB, signs, exponents, `.5`, `3.`), FR-04 … FR-06 (negative values) |
| 03 | `dp-stats - < single.txt` | FR-01, FR-05 (*N* = 1), FR-06 (`1 data items read`) |
| 04 | `dp-stats` (empty standard input) | FR-07 |
| 05 | `dp-stats same.txt` | FR-05 (clamping a negative variance) |
| 06 | `dp-stats round.txt` | FR-06 (`FIX` ties to even) |
| 07 | `dp-stats bad.txt` | FR-08 (no report, CONV-34) |
| 08 | `dp-stats missing.txt` | FR-09 |
| 09 | `dp-stats --help` | FR-10 |
| 10 | `dp-stats data.txt three.txt` | FR-12, FR-13 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-06 |
| UR-02 | FR-04, FR-05, FR-06 |
| UR-03 | FR-03, FR-04, NFR-03 |
| UR-04 | FR-01, CONV-26 |
| UR-05 | FR-04, FR-05, FR-06, NFR-02, CONV-35 |
| UR-06 | FR-07 |
| UR-07 | FR-08, CONV-33, CONV-34 |
| UR-08 | FR-09, CONV-16 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-10, FR-11 |
| UR-11 | FR-12, FR-13 |
| UR-12 | NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-12, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
