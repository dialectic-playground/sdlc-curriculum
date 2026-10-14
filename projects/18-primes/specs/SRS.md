# Software Requirements Specification (SRS) — dp-primes

| Field | Value |
| :-- | :-- |
| Document ID | SRS-18 |
| Project | `18-primes` — Prime Number Generation via Trial Division |
| Product | `dp-primes` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-18) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-primes`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-primes` reads a bound *n* as the first integer token of standard input or of one file. It
writes a header line, a blank line, and every prime less than or equal to *n* in ascending
order, one per line; or, with `--count`, only the number of those primes. It can write a banner
and a prompt to standard error before *n* is read. It accepts every 64-bit *n* up to 10000000,
reports invalid bounds with their line numbers, and reports unreadable files with fixed
messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, TAB | The line-feed byte `0x0A`; the horizontal-tab byte `0x09` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Complete token | A token whose terminating whitespace byte has been read, or the last token of the input once the end of the input has been reached |
| Bound (*n*) | The value of the first token of the input, which MUST be a valid *integer* (CONV-33) with −2⁶³ ≤ *n* ≤ 10000000 (FR-02) |
| Prime | An integer *p* ≥ 2 that is not divisible by any integer *d* with 2 ≤ *d* < *p* |
| *P*(*n*) | The ascending sequence of all primes *p* with *p* ≤ *n*; empty when *n* < 2 |
| Decimal | The plain ASCII decimal representation of an integer: a `-` for a negative value, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-18: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §3.2 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-primes` is a standalone executable. Its interfaces are the command line, standard input or
the file named by its operand, standard output, standard error, and the exit status. It belongs
to the curriculum's applications-programming track (Projects 11–52) and adapts §3.2 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read the bound *n* as the first integer token of the input.
2. Compute every prime less than or equal to *n*.
3. Write a header and the primes in ascending order, or only their number.
4. Optionally write a banner and a prompt to standard error before *n* is read.
5. Report an invalid or missing bound and an unreadable input file.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Any algorithm that produces exactly *P*(*n*) is allowed (for example trial division by the
  integers or primes up to ⌊√*p*⌋, or the sieve of Eratosthenes), provided it meets NFR-03.
  Floating-point arithmetic MUST NOT decide whether a number is prime; if a square-root bound
  is used, it MUST be computed or checked in integer arithmetic (for example `d × d ≤ p`).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only the first token is examined.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §3.2 prints the banner `This program lists all primes <= n` (indented
by a TAB), prompts `Input n: `, reads an integer, prints the header `Primes <= n:` (indented by a
TAB and surrounded by blank lines), and then every prime up to *n*, one per line, found by
dividing each candidate *p* by every integer from 2 to *p* − 1. `dp-primes` keeps:

- the definition of the result: every prime 2 … *n*, ascending, one per line, nothing for
  *n* < 2 (including negative *n*);
- the header text with its leading TAB and the blank line between the header and the list;
- the banner and prompt texts, byte for byte, as an optional dialog (FR-06).

It changes the following, for the reasons given:

- **Dialog on standard error.** The banner and the prompt exist only to talk to a person at a
  keyboard. They are written to standard error, and only with `-p`, `--prompt` (FR-06), so a
  saved list holds only the results.
- **Blank lines before the header are dropped.** The textbook writes two blank lines between
  the echoed input and the header; they separated the results from the typed number on the
  screen and carry no information in a file. The output starts with the header (FR-04).
- **An explicit limit and a performance requirement.** The textbook's nested loop performs
  about *n*²/(2 ln *n*) divisions; for *n* = 10000000 that is several trillion, hours of work.
  `dp-primes` accepts *n* ≤ 10000000 and requires the whole list in under 2 s natively
  (NFR-03), which the textbook's algorithm cannot meet. A larger *n* is rejected (FR-07) rather
  than left to run for an unpredictable time or overflow a fixed-size integer.
- **Invalid input is diagnosed.** A token that is not an integer leaves the textbook's *n*
  undefined. `dp-primes` reports it with its line number, writes nothing to standard output, and
  exits with status 1 (FR-07); an empty input is reported as `unexpected end of input`.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02). Anything after the first token is
  ignored, as the textbook ignores the rest of the line.
- **Count-only mode.** `-c`, `--count` writes only the number of primes (FR-09), for scripts
  and for checking the limit without a 5 MB listing.
- **The header shows the value of *n*,** not its spelling: `+015` gives `Primes <= 15:`.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (the bound uses the
*integer* grammar, further restricted to at most 10000000), CONV-34 (data diagnostics, with the
standard messages `invalid integer`, `value out of range`, and `unexpected end of input` and the
default consequences), CONV-36 (`-p`, `--prompt`), and CONV-37 (the input is *text data*).
CONV-35 does not apply, because no real number is ever written, and CONV-38 does not apply,
because nothing is random. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. `dp-primes` copies no input bytes to its output, so CONV-04 does not
apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-primes [-c | --count] [-p | --prompt] [FILE]
dp-primes --help
dp-primes --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-c` | `--count` | none | off | Write only the number of primes ≤ *n* (FR-09) |
| `-p` | `--prompt` | none | off | Write the banner and the prompt `Input n: ` to standard error before *n* is read (FR-06) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling such as `-cp`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. Giving a flag more than once has the same effect as giving it once (CONV-11).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The report (FR-04) or the count (FR-09). Nothing else. Nothing is written to standard output
when the bound is missing or invalid. On a usage error, or when `--help` / `--version` is
handled, the output is as specified by FR-10 … FR-12 instead.

### 3.6 Standard error
The banner and prompt (FR-06, only with `--prompt`) and diagnostics (section 6). Without
`--prompt`, nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | A valid bound was read and the report or count was written, or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-08), the bound was missing or invalid (FR-07), or standard output could not be written |
| 2 | Usage error (FR-12) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF and `\t` denotes TAB. The public fixture files in
`tests/fixtures/` are: `fifteen.txt` = `15\n`; `hundred.txt` = `100\n`; `one.txt` = `1\n`;
`negative.txt` = `-7\n`; `limit.txt` = `10000000\n`; `bad.txt` = `\n15.0\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the banner and prompt). More than one operand is a
usage error (FR-12).
*AC:* `dp-primes < fifteen.txt`, `dp-primes fifteen.txt`, and `dp-primes - < fifteen.txt` write
the same report. *(UR-01, UR-04)*

**FR-02: The bound.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32). The first
token is the bound: it MUST be a valid *integer* (CONV-33), and its value *n* MUST satisfy
*n* ≤ 10000000. Every 64-bit value up to that limit is accepted, including 0 and negative
values. A sign (`+15`, `-0`) and leading zeros (`015`) are allowed. Leading whitespace of any
kind (space, TAB, VT, FF, CR, LF) is skipped, so CRLF input reads exactly like LF input. Bytes
after the first token are not examined: they need not form valid tokens, and they cause no
diagnostic. A missing, invalid, or out-of-range bound is handled by FR-07.
*AC:* an input `  +0097 junk 5\r\n` gives the report for *n* = 97 with exit status 0; an input
`100\r\n` followed by two `0x1A` bytes gives the report for *n* = 100. *(UR-01, UR-10)*

**FR-03: The primes.**
The tool MUST compute *P*(*n*) (section 1.3) exactly: every integer *p* with 2 ≤ *p* ≤ *n* that
has no divisor *d* with 2 ≤ *d* < *p*, in ascending order, each exactly once. For *n* < 2,
*P*(*n*) is empty. The choice of algorithm is free (section 2.3), subject to NFR-03.
*AC:* *P*(15) = 2, 3, 5, 7, 11, 13; *P*(20) = 2, 3, 5, 7, 11, 13, 17, 19; *P*(2) = 2;
*P*(1), *P*(0), *P*(−7), and *P*(−9223372036854775808) are empty; *P*(100) has 25 elements,
the last being 97; *P*(10000000) has 664579 elements, the last being 9999991. *(UR-01, UR-03)*

**FR-04: Report format.**
Unless `--count` is given (FR-09), the tool MUST write to standard output exactly:

1. the header line: one TAB, then `Primes <= `, then the decimal of *n* (section 1.3), then
   `:`, then LF;
2. an empty line (a single LF);
3. for each prime *p* of *P*(*n*), in order, the decimal of *p* followed by LF.

There are no other bytes: no blank lines before the header or after the last prime, no
leading or trailing spaces, and no TAB other than the one that begins the header. When
*P*(*n*) is empty, the report is the header and the empty line only. The header shows the value
of *n*, not the token's spelling: `+015` and `15` both give `Primes <= 15:`, and `-0` gives
`Primes <= 0:`.
*AC:* `dp-primes < fifteen.txt` → stdout `\tPrimes <= 15:\n\n2\n3\n5\n7\n11\n13\n`, stderr
empty, exit 0; `dp-primes one.txt` → `\tPrimes <= 1:\n\n`; `dp-primes negative.txt` →
`\tPrimes <= -7:\n\n`. *(UR-01, UR-02, UR-03)*

**FR-05: Reading.**
The tool MUST read the input only as far as it needs to complete the first token (section
1.3), apart from ordinary buffering of bytes that are already available. As soon as the first
token is complete, the tool MUST validate it and write the report without waiting for the end
of the input, so a user who types `15` and Enter at a terminal sees the report at once. All
checks of FR-07 happen before anything is written to standard output.
*AC:* `dp-primes bad.txt` writes nothing to standard output. At a terminal, typing `15` and
Enter shows the report and ends the tool before anything else is typed (manual check).
*(UR-01, UR-08)*

**FR-06: Banner and prompt.**
`-p`, `--prompt` enables the tool's single prompt, which consists of the banner and the prompt
text. It is exactly the 46 bytes: one TAB, `This program lists all primes <= n`, LF, LF,
`Input n: ` (ending with one space, no LF). With prompts enabled, the tool MUST write it to
standard error, and flush standard error, once, after the input has been opened and
immediately before the first byte of the input is read. It is written even when the input turns
out to be empty (CONV-36); a diagnostic of FR-07 then follows it on the same line. Prompts
never change standard output. No prompt is written if the input cannot be opened, or on a
usage error.
*AC:* `dp-primes --prompt < fifteen.txt` → stdout as in FR-04, stderr
`\tThis program lists all primes <= n\n\nInput n: `, exit 0. *(UR-07)*

**FR-07: Missing or invalid bound.**
The tool MUST write one of the following diagnostics, write nothing to standard output, and
exit with status 1:

- the input contains no token (it is empty, or holds only whitespace and a trailing `0x1A`
  run): `dp-primes: <source>:<line>: unexpected end of input`, where `<line>` is the
  end-of-input line number (CONV-32);
- the first token is not a valid *integer* (CONV-33), including an integer outside
  −2⁶³ … 2⁶³−1: `dp-primes: <source>:<line>: invalid integer '<token>'`;
- the first token is a valid *integer* greater than 10000000:
  `dp-primes: <source>:<line>: value out of range '<token>'`.

`<source>` is as defined in section 1.3, `<line>` is the token's line number unless stated
otherwise, and `<token>` is the token's exact bytes (CONV-34).
*AC:* `dp-primes bad.txt` → stderr `dp-primes: bad.txt:2: invalid integer '15.0'\n`, stdout
empty, exit 1; `dp-primes` with empty standard input → `dp-primes: -:1: unexpected end of
input`; an input `10000001` → `value out of range '10000001'`; `9223372036854775808` →
`invalid integer`; a token `100` followed by a `0x1A` byte and an LF → `invalid integer
'100<0x1A>'`, because that Ctrl-Z byte does not end the input; an input of LF, LF, space, TAB,
LF, and one `0x1A` byte → `unexpected end of input` on line 4. *(UR-06, UR-08)*

**FR-08: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-primes: <source>: <reason>` with `<reason>` from the CONV-16 table, write
nothing to standard output, and exit with status 1. When standard input fails, `<source>` is
`-`.
*AC:* `dp-primes missing.txt` → stderr `dp-primes: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-primes subdir` where `subdir` is a directory →
`dp-primes: subdir: Is a directory`. *(UR-09)*

**FR-09: Count mode.**
With `-c`, `--count`, the tool MUST write, instead of the report of FR-04, exactly one line:
the decimal of the number of elements of *P*(*n*), followed by LF. No header is written. Input,
prompt, and diagnostics are unchanged.
*AC:* `dp-primes --count limit.txt` → stdout `664579\n`, exit 0; `dp-primes -cp - < hundred.txt`
→ stdout `25\n` and the prompt of FR-06 on stderr; a bound of −9223372036854775808 → `0\n`.
*(UR-05, UR-06)*

**FR-10: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-primes --help` matches the user manual exactly; `dp-primes extra --help` also prints
it. *(UR-11)*

**FR-11: Version.**
`--version` MUST write `dp-primes (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-11)*

**FR-12: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--count=…`, `--prompt=…`,
`--help=…`, `--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14
line, with exit status 2. Long options MUST NOT be abbreviated (CONV-08): `--prom` is
unrecognized. A second operand MUST be reported as `dp-primes: extra operand '<second
operand>'`, after the whole argument list has been scanned (CONV-12). When a usage error
occurs, the tool MUST NOT open the operand, read standard input, write the prompt, or write
anything to standard output.
*AC:* `dp-primes fifteen.txt hundred.txt` → `dp-primes: extra operand 'hundred.txt'`;
`dp-primes -x --help` → `dp-primes: invalid option -- 'x'`; `dp-primes --count=yes` →
`dp-primes: option '--count' doesn't allow an argument`; each followed by the CONV-14 line,
stdout empty, exit 2. *(UR-11, UR-12)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: interactive input and line endings | The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer; only FR-02 decides what a trailing Ctrl-Z run means. At an interactive console the tool MUST answer as soon as the bound's line is entered (FR-05) and MUST NOT require the platform's end-of-input signal; that signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) given before any token MUST produce the `unexpected end of input` diagnostic, not a hang or a crash. Standard error MUST be flushed after the prompt, and standard output and standard error MUST be written in binary mode (CONV-03); the report contains a TAB, which MUST NOT be expanded. | CI black-box tests on 3 OSes; manual console check; code review |
| NFR-03 | Performance | For *n* = 10000000 (664579 primes, about 5 MiB of output), the tool MUST finish in under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with or without `--count`, with peak memory under 32 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). For *n* ≤ 1000, start-up and exit MUST take under 100 ms native (300 ms interpreted). Trial division by every integer below *p*, as in the textbook, does not meet this requirement. | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length, integers far outside the 64-bit range, and the extreme bound −2⁶³; no arithmetic on *n* (such as *n* + 1 or a square root) may overflow. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, reading the bound, validation, prime generation, report formatting, and I/O MUST be separate units. Prime generation MUST be one function from *n* to *P*(*n*) (or an equivalent stream) that does no I/O, and it is the only place where primality is decided. The limit 10000000 MUST appear in one named constant. | Design review |
| NFR-06 | Testability | The prime generator MUST be covered by unit tests that compare it with a naive trial-division oracle for every *n* from −5 to 2000, and that check the counts *π*(10ⁿ) = 4, 25, 168, 1229, 9592, 78498, 664579 for *n* = 1 … 7 and the bounds 2, 3, 4, and 10000000. The report formatter MUST be a pure function covered by unit tests. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. Memory use MUST be bounded by the limit on *n*, whatever the input. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-primes --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-primes: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-primes: unrecognized option 'T'` |
| `--count=…`, `--prompt=…`, `--help=…`, `--version=…` | `dp-primes: option '--count' doesn't allow an argument` (or `'--prompt'`, `'--help'`, `'--version'`) |
| A second operand `X` | `dp-primes: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one and writes nothing to standard
output):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-primes: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-primes: F: Permission denied` |
| FILE `F` is a directory | `dp-primes: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-primes: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-primes: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Source `S` contains no token; `L` is its end-of-input line number | `dp-primes: S:L: unexpected end of input` |
| The first token `K`, on line `L` of source `S`, is not a valid *integer* | `dp-primes: S:L: invalid integer 'K'` |
| The first token `K`, on line `L` of source `S`, is a valid *integer* above 10000000 | `dp-primes: S:L: value out of range 'K'` |
| Standard output cannot be written (other than a broken pipe) | `dp-primes: write error` |

When `--prompt` is given, a data diagnostic follows the prompt on the same line of standard
error (FR-06).

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-04, FR-06 … FR-10 |
| Black-box test (hidden, `tests/private/`, 10 cases; several have more than one step) | FR-02 … FR-04, FR-06 … FR-09, FR-11, FR-12 |
| Unit test (written by the implementer) | FR-02 … FR-04, FR-09, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-05 (interactive timing), NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-primes < fifteen.txt` | FR-01, FR-03, FR-04 |
| 02 | `dp-primes hundred.txt` | FR-01, FR-03, FR-04 |
| 03 | `dp-primes --prompt < fifteen.txt` | FR-06 |
| 04 | `dp-primes one.txt` | FR-03, FR-04 (empty list) |
| 05 | `dp-primes negative.txt` | FR-02, FR-04 (negative bound) |
| 06 | `dp-primes --count limit.txt` | FR-02 (the limit), FR-03, FR-09 |
| 07 | `dp-primes bad.txt` | FR-05, FR-07 (line number, nothing on stdout) |
| 08 | `dp-primes` (empty standard input) | FR-07 (unexpected end of input) |
| 09 | `dp-primes --help` | FR-10 |
| 10 | `dp-primes missing.txt` | FR-08 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-03, FR-04, FR-05 |
| UR-02 | FR-04 |
| UR-03 | FR-03, FR-04 |
| UR-04 | FR-01, CONV-26 |
| UR-05 | FR-09 |
| UR-06 | FR-07, FR-09, NFR-03 |
| UR-07 | FR-06, CONV-36 |
| UR-08 | FR-05, FR-07, CONV-33, CONV-34 |
| UR-09 | FR-08, CONV-16 |
| UR-10 | FR-02, NFR-02, CONV-37 |
| UR-11 | FR-10, FR-11, FR-12 |
| UR-12 | FR-12, NFR-01, NFR-02, CLI-CONV |
| UR-13 | NFR-07 |
