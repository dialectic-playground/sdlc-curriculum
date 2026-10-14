# Software Requirements Specification (SRS) — dp-matmult

| Field | Value |
| :-- | :-- |
| Document ID | SRS-30 |
| Project | `30-matmult` — Matrix Multiplication Engine |
| Product | `dp-matmult` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-30) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-matmult`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-matmult` reads, as integer tokens from standard input or from one file, a size *N*
(1 … 20) followed by two *N*×*N* matrices in row-major order. It writes the first matrix as
soon as it has been read, then the second, then their product, each under a heading. Every
term and partial sum of the product is checked for 64-bit overflow. It can write prompts to
standard error before each part of the input is read. It reports invalid data with line
numbers, overflow with the position of the product element, and unreadable files with fixed
messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| End-of-input line number | 1 plus the number of LF bytes in the whole input (CONV-32), after removal of a trailing Ctrl-Z run (FR-02) |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |
| *N* | The size: the value of the first token, 1 ≤ *N* ≤ 20 |
| *A*, *B* | The first and second matrix; *a*ᵢₖ is the element of *A* in row *i*, column *k* (1-based) |
| *C* | The product *A* × *B* (FR-06) |
| Int64 | The range −9223372036854775808 … 9223372036854775807 (−2⁶³ … 2⁶³−1) |
| Decimal | The plain ASCII decimal representation of an integer: a `-` for negative values, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-30: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §5.10 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-matmult` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §5.10 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read the size and the elements of two square matrices as integer tokens.
2. Write each matrix, under its heading, as soon as it has been read.
3. Compute the product exactly, detecting 64-bit overflow, and write it under its heading.
4. Optionally write prompts to standard error before each part of the input is read.
5. Report invalid data, overflow, and unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The product MUST be computed in integer arithmetic (FR-06). Binary floating point MUST NOT be
  used to compute or check it.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case, apart from the timing guaranteed by FR-05.
- The input may contain any bytes; only tokens that match the *integer* grammar are accepted.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §5.10 prompts for a size of at most 20, prompts for and reads the first
matrix by row, prints it under `Matrix m1:`, does the same for the second matrix
(`Matrix m2:`), and prints the product under `Product m3:`, computed with the triply nested
loop *c*ᵢⱼ = Σₖ *a*ᵢₖ × *b*ₖⱼ. `dp-matmult` keeps:

- the order of the dialog (size, first matrix, echo, second matrix, echo, product) and the
  three prompt texts `Input matrix size: `, `Input first matrix by row`, and
  `Input second matrix by row`;
- the three headings exactly, each on its own line, and one output line per matrix row;
- the size limit 1 … 20 and row-major reading, with rows and elements separated by any
  whitespace;
- the classic O(*N*³) algorithm and its summation order (ascending *k*).

It changes the following, for the reasons given:

- **No trailing space, no blank lines.** The textbook writes every element followed by a space,
  so each row ends in a space, and separates its output from the typed input with blank lines.
  Both exist only because of how the output was produced and how it sat next to keyboard
  echo. `dp-matmult` separates elements with exactly one space and ends every row with the last
  element (FR-04), and writes no blank lines, so redirected output is clean and easy to compare.
- **Checked 64-bit arithmetic.** The textbook uses the platform's `int`, whose size varies, and
  lets an oversized product wrap around (or worse: signed overflow is undefined in C). All
  values here are Int64, and FR-06 defines exactly which terms and partial sums are checked, in
  which order, so that every implementation rejects the same inputs; FR-09 reports the first
  offending element.
- **Invalid input is diagnosed.** A size outside 1 … 20, a token that is not an integer, or an
  input that ends early stops the textbook program in an unspecified way. `dp-matmult` reports
  it with its line number and exits with status 1 (FR-08).
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).
- **Prompts are optional and go to standard error.** The prompts are written only with `-p`,
  `--prompt` (FR-07), so that standard output holds only the report.
- **Values, not spellings.** Elements are echoed as their values (`+3` and `003` as `3`), so the
  echo shows what was understood.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (every token uses
the *integer* grammar; the size is further restricted to 1 … 20), CONV-34 (data diagnostics,
with the standard messages `invalid integer`, `value out of range`, and
`unexpected end of input` and the default consequences), CONV-36 (`-p`, `--prompt`), and
CONV-37 (the input is *text data*). The overflow diagnostic of FR-09 concerns no single token,
so it does not use the CONV-34 location format; it is an additional runtime error with exit
status 1. CONV-35 does not apply, because no real number is ever written, and CONV-38 does not
apply, because nothing is random. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. `dp-matmult` copies no input bytes to its output, so CONV-04 does not
apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-matmult [-p | --prompt] [FILE]
dp-matmult --help
dp-matmult --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | off | Write the prompts of FR-07 to standard error |
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
The report (FR-04, FR-05): up to three headed matrices. Nothing else. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-11 … FR-14 instead.

### 3.6 Standard error
Prompts (FR-07, only with `--prompt`) and diagnostics (section 6). Without `--prompt`, nothing
is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The product was written, or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-10), its data was invalid or incomplete (FR-08), the product overflowed (FR-09), or standard output could not be written |
| 2 | Usage error (FR-13) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the files named are the public fixtures in
`tests/fixtures/`: `readme.txt` is `2\n1 2\n3 4\n2 0\n1 2\n` (the section's example);
`identity.txt` holds a 3×3 matrix and the 3×3 identity with CRLF line endings, TABs, and
repeated spaces; `negative.txt` holds two 3×3 matrices with negative elements, a `+` sign, and
leading zeros; `bad.txt` is `2\n1 2\n3 4\n5 6\n7 x8\n`; `overflow.txt` is
`2\n3037000500 1\n0 1\n1 3037000500\n0 1\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the first prompt). More than one operand is a usage
error (FR-13).
*AC:* `dp-matmult readme.txt` and `dp-matmult < readme.txt` write the same report.
*(UR-05)*

**FR-02: Tokens.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
read in order. Line structure has no meaning: tokens may be separated by any mixture of space,
TAB, VT, FF, CR, and LF, so a row may span several lines, several rows may share a line, and
CRLF input reads exactly like LF input. The input MUST be read incrementally: a token is
complete, and MUST be processed, as soon as the whitespace byte that follows it has been read;
the only permitted lookahead is a run of `0x1A` bytes, which is held back until the next byte
shows whether it reaches the end of the input. A `0x1A` byte that does not reach the end is
ordinary data and belongs to a token.
*AC:* `dp-matmult < identity.txt` writes the 3×3 matrix, the identity, and a product equal to
the first matrix, exit 0; the hidden fixture `ctrlz.txt` (the README example with CRLF line
endings and two final `0x1A` bytes) gives the same report as `readme.txt`. *(UR-01, UR-10)*

**FR-03: Input structure.**
The tokens are, in order:

1. the size *N*, an *integer* (CONV-33) with 1 ≤ *N* ≤ 20;
2. the *N*² elements of *A* in row-major order (*a*₁₁, *a*₁₂, …, *a*₁ₙ, *a*₂₁, …, *a*ₙₙ),
   each an *integer* (CONV-33), that is, any Int64 value;
3. the *N*² elements of *B* in the same order and with the same grammar.

Each token MUST be validated as soon as it is complete, before the next token is read. Once
the last element of *B* has been read, the tool reads no further input: anything after it is
neither read nor validated. A token that is invalid, out of range, or missing is handled by
FR-08.
*AC:* the hidden fixture `scalar.txt` (`1 -7 6 extra 1.5\n`) gives *N* = 1 and the product
`-42`, exit 0, although `extra` and `1.5` are not integers; `20` is accepted as a size (hidden
fixture `max20.txt`), `21` and `0` are `value out of range`. *(UR-01, UR-08)*

**FR-04: Matrix format.**
A matrix is written as its heading line followed by *N* row lines. Row *i* consists of the
decimals (section 1.3) of the elements of row *i* in column order, separated by exactly one
space, with no leading space, **no trailing space**, and a single LF at the end. The headings
are exactly `Matrix m1:` for *A*, `Matrix m2:` for *B*, and `Product m3:` for *C*, each followed
by LF. No blank lines, padding, or column alignment are written. Elements are written as their
values, not as their tokens were spelled: `+1`, `005`, and `-0` are written as `1`, `5`, and
`0`.
*AC:* `dp-matmult readme.txt` → stdout
`Matrix m1:\n1 2\n3 4\nMatrix m2:\n2 0\n1 2\nProduct m3:\n4 4\n10 8\n`, stderr empty, exit 0.
*(UR-02, UR-03)*

**FR-05: Order of output.**
The tool MUST write *A* (FR-04) and flush standard output as soon as the last element of *A*
has been validated, before it reads any token of *B*. It MUST write *B* and flush as soon as
the last element of *B* has been validated. It then computes the whole product (FR-06), and
only if no overflow occurred writes *C* and flushes. *C* is never written in part.
*AC:* `dp-matmult bad.txt` writes *A* before reporting the invalid element of *B*;
`dp-matmult overflow.txt` writes *A* and *B* but no `Product m3:` heading. At a terminal, *A*
appears before the first element of *B* is typed (manual check). *(UR-06)*

**FR-06: Product and overflow rule.**
For every *i* and *j* in 1 … *N*, the tool MUST compute *c*ᵢⱼ as follows, in exact integer
arithmetic: start with the sum *s* = 0; for *k* = 1, 2, …, *N* in ascending order, form the term
*t*ₖ = *a*ᵢₖ × *b*ₖⱼ and set *s* ← *s* + *t*ₖ. The element *c*ᵢⱼ is the final *s*. The product
**overflows** at (*i*, *j*) if any term *t*ₖ, or any partial sum *s* after adding *t*ₖ, lies
outside Int64. This test MUST be applied to the mathematically exact values; an implementation
MUST detect overflow before or without relying on a wrapped result (signed wrap-around is not
a detection method in every language). Because the partial sums are checked in ascending *k*,
an element can overflow even when its final value would lie within Int64; such an element is
still reported. Product elements are computed in row-major order (*i* ascending, then *j*
ascending), and the first element that overflows is the one reported by FR-09.
*AC:* `dp-matmult readme.txt` → product rows `4 4` and `10 8`; the hidden fixture `limits.txt`
gives the product elements −9223372036854775808 and 9223372036854775807 exactly (no
overflow); in the hidden fixture `cancel.txt` the terms of *c*₁₁ are 2⁶², 2⁶², −2⁶²: the
partial sum 2⁶³ overflows although the final value 2⁶² would fit, while `ordered.txt`, with the
same terms in the order 2⁶², −2⁶², 2⁶², succeeds. *(UR-03, UR-04)*

**FR-07: Prompts.**
With `-p` or `--prompt`, the tool MUST write these prompts to standard error, and flush
standard error before the read that follows (CONV-36):

| Prompt | Exact bytes | Written |
| :-- | :-- | :-- |
| P1 | `Input matrix size: ` (19 bytes, ending in a space, no LF) | Once, before the size is read |
| P2 | `Input first matrix by row` + LF (26 bytes) | Once, after a valid size and before the first element of *A* is read |
| P3 | `Input second matrix by row` + LF (27 bytes) | Once, after *A* has been written to standard output, before the first element of *B* is read |

No prompt is written before the individual elements or rows. Without the flag, no prompt is
written. Standard output is the same with and without it. No prompt is written if the input
cannot be opened, and a prompt whose read fails is still written (CONV-36).
*AC:* `dp-matmult --prompt < readme.txt` → stdout as in FR-04; stderr
`Input matrix size: Input first matrix by row\nInput second matrix by row\n`, exit 0.
*(UR-07)*

**FR-08: Data errors.**
At the first invalid or missing token, the tool MUST write one CONV-34 diagnostic,
`dp-matmult: <source>:<line>: <message>`, read no further input, and exit with status 1.
Output already written (*A*, if it was complete) is kept; the matrix being read is not written.

| Condition | `<line>` | `<message>` |
| :-- | :-- | :-- |
| The size or an element is not a valid *integer* (including a value outside Int64) | the token's line | `invalid integer '<token>'` |
| The size is a valid *integer* outside 1 … 20 | the token's line | `value out of range '<token>'` |
| The input ends before the size or before the last element of *B* | the end-of-input line number | `unexpected end of input` |

`<token>` is the token's exact bytes (CONV-34). An empty input is therefore an error. With
`--prompt`, the diagnostic follows the last prompt written, on the same line of standard error.
*AC:* `dp-matmult bad.txt` → stdout `Matrix m1:\n1 2\n3 4\n`, stderr
`dp-matmult: bad.txt:5: invalid integer 'x8'\n`, exit 1; `dp-matmult -p` with empty standard
input → stderr `Input matrix size: dp-matmult: -:1: unexpected end of input\n`, exit 1;
`9223372036854775808` and `2.0` are `invalid integer`. *(UR-08)*

**FR-09: Overflow error.**
If the product overflows (FR-06), the tool MUST write
`dp-matmult: integer overflow in product row <i>, column <j>` to standard error, where
`<i>` and `<j>` are the decimals of the 1-based row and column of the first element that
overflows in row-major order, write no part of *C*, and exit with status 1. *A* and *B* remain
written (FR-05).
*AC:* `dp-matmult overflow.txt` → stdout
`Matrix m1:\n3037000500 1\n0 1\nMatrix m2:\n1 3037000500\n0 1\n`, stderr
`dp-matmult: integer overflow in product row 1, column 2\n`, exit 1 (*c*₁₁ = 3037000500 fits;
*c*₁₂ = 3037000500² + 1 does not). *(UR-04)*

**FR-10: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-matmult: <source>: <reason>` with `<reason>` from the CONV-16 table,
and exit with status 1. Output already written is kept. When standard input fails, `<source>`
is `-`.
*AC:* `dp-matmult missing.txt` → stderr `dp-matmult: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-matmult subdir` where `subdir` is a directory →
`dp-matmult: subdir: Is a directory`. *(UR-09)*

**FR-11: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-matmult --help` matches the user manual exactly; `dp-matmult extra --help` also
prints it. *(UR-11)*

**FR-12: Version.**
`--version` MUST write `dp-matmult (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match; `dp-matmult -p --version` also prints it. *(UR-11)*

**FR-13: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is unrecognized. A
second operand MUST be reported as `dp-matmult: extra operand '<second operand>'`, after the
whole argument list has been scanned (CONV-12).
*AC:* `dp-matmult readme.txt identity.txt` → `dp-matmult: extra operand 'identity.txt'`;
`dp-matmult -x --help` → `dp-matmult: invalid option -- 'x'`; `dp-matmult --prompt=yes` →
`dp-matmult: option '--prompt' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-12, UR-13)*

**FR-14: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write a
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: integer width and overflow semantics | Every element, term, and sum MUST be held in a type of exactly 64 bits (or wider), never in a type whose width depends on the platform or compiler (C's `int` and `long` differ between Windows and POSIX). Overflow MUST be detected by a method that is defined behavior in the implementation language on every platform (for example checked-arithmetic primitives, a pre-test against the Int64 limits, or a wider intermediate type), never by inspecting a wrapped result where wrapping is undefined or optimizable. Inputs MUST be read in binary mode, so CR bytes reach the tokenizer and only FR-02 interprets `0x1A`; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. Standard output MUST be flushed after each matrix (FR-05) and standard error after each prompt, even when they are pipes. | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance | A 20×20 input (the largest allowed) MUST be processed in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, including start-up and exit, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range, and products whose exact value needs more than 128 bits. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the incremental tokenizer, reading one matrix, printing one matrix, and multiplication MUST be separate units. One procedure MUST read a matrix of a given size and be used for both *A* and *B*; one procedure MUST print a matrix under a given heading and be used for all three; the product MUST be one function of two matrices that performs no input or output (the textbook's `store`, `print`, and `mult`). | Design review |
| NFR-06 | Testability | The multiplication function MUST be unit-tested with the identity and zero matrices, *N* = 1, a pair with *A* × *B* ≠ *B* × *A*, the products that reach exactly −2⁶³ and 2⁶³−1, a term that overflows, a partial sum that overflows positively and one that overflows negatively, and the ascending-*k* case of FR-06. The tokenizer MUST be unit-tested with the input split into reads at every byte position. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-matmult --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-matmult: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-matmult: unrecognized option 'T'` |
| `--prompt=…`, `--help=…`, `--version=…` | `dp-matmult: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X` | `dp-matmult: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one; earlier output is kept):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-matmult: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-matmult: F: Permission denied` |
| FILE `F` is a directory | `dp-matmult: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-matmult: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-matmult: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Token `K` on line `L` of source `S` (size or element) is not a valid *integer* | `dp-matmult: S:L: invalid integer 'K'` |
| Size token `K` on line `L` of source `S` is outside 1 … 20 | `dp-matmult: S:L: value out of range 'K'` |
| Source `S` ends before the size or the last element of *B*; `L` is the end-of-input line number | `dp-matmult: S:L: unexpected end of input` |
| Product element in row `I`, column `J` overflows (FR-06) | `dp-matmult: integer overflow in product row I, column J` |
| Standard output cannot be written (other than a broken pipe) | `dp-matmult: write error` |

When `--prompt` is given, a data diagnostic follows the last prompt on the same line of
standard error, or starts a new line when that prompt was P2 or P3 (which end in LF) (FR-07).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-11, FR-13, FR-14 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03 and 05 … 10 have several steps) | FR-02 … FR-14 |
| Unit test (written by the implementer) | FR-02, FR-03, FR-06, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-05 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-matmult readme.txt` | FR-01, FR-03, FR-04, FR-06 (the section's example) |
| 02 | `dp-matmult < identity.txt` | FR-01, FR-02 (CRLF, TAB), FR-06 (identity) |
| 03 | `dp-matmult --prompt < readme.txt` | FR-07 |
| 04 | `dp-matmult negative.txt` | FR-04 (signs, leading zeros), FR-06 (negative values) |
| 05 | `dp-matmult -p` (empty standard input) | FR-07, FR-08 (unexpected end of input) |
| 06 | `dp-matmult bad.txt` | FR-05, FR-08 (output kept) |
| 07 | `dp-matmult overflow.txt` | FR-05, FR-06, FR-09 |
| 08 | `dp-matmult missing.txt` | FR-10 |
| 09 | `dp-matmult --help` | FR-11 |
| 10 | `dp-matmult readme.txt identity.txt` | FR-13, FR-14 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-02, FR-03 |
| UR-02 | FR-04 |
| UR-03 | FR-04, FR-06 |
| UR-04 | FR-06, FR-09, NFR-02 |
| UR-05 | FR-01, CONV-26 |
| UR-06 | FR-05, NFR-02 |
| UR-07 | FR-07, CONV-36 |
| UR-08 | FR-03, FR-08, CONV-33, CONV-34 |
| UR-09 | FR-10, CONV-16 |
| UR-10 | FR-02, NFR-02, CONV-37 |
| UR-11 | FR-11, FR-12 |
| UR-12 | FR-13, FR-14 |
| UR-13 | NFR-01, FR-13, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
