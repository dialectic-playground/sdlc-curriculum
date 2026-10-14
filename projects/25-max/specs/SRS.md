# Software Requirements Specification (SRS) — dp-max

| Field | Value |
| :-- | :-- |
| Document ID | SRS-25 |
| Project | `25-max` — Variadic Functions & Dynamic Arity Processing |
| Product | `dp-max` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-25) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-max`, and one design property of
its implementation (NFR-05). It is complete and precise enough that independent
implementations in any programming language produce **byte-identical** output for every
invocation. It is the authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-max` reads one to four integers as tokens from standard input or from one file until the
end of the input, validates the whole input, and writes one line giving the largest value. The
largest value is computed by a single function that accepts any number of arguments. The tool
can write a prompt to standard error before reading. It reports a missing, surplus, or invalid
value with its line number and unreadable files with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number, end-of-input line number | As defined in CONV-32 |
| Value | The value of a token that is a valid *integer* (CONV-33): −9223372036854775808 … 9223372036854775807 |
| Maximum | For values *v*₁ … *v*ₖ (*k* ≥ 1), the value *M* = *v*ᵢ for some *i* such that *v*ⱼ ≤ *M* for every *j* |
| Decimal | The plain ASCII decimal representation of an integer: a `-` for negative values, no `+`, no leading zeros (zero is `0`), no digit grouping (CONV-06, CONV-35) |
| Variadic function | A function whose callers may pass different numbers of arguments in different calls (NFR-05) |

### 1.4 References
- URD-25: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §4.10 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-max` is a standalone executable. Its interfaces are the command line, standard input or the
file named by its operand, standard output, standard error, and the exit status. It belongs to
the curriculum's applications-programming track (Projects 11–52) and adapts §4.10 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read the whole input and divide it into tokens.
2. Check that it holds one to four valid integers and nothing else.
3. Compute the maximum with one variadic function and write it in one line.
4. Optionally write a prompt to standard error before reading.
5. Report a missing, surplus, or invalid value, and unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains observable behavior, plus the design property of NFR-05, which is
  stated so that every language can meet it.

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may contain any bytes; only tokens that match the *integer* grammar are values.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §4.10 prints `Enter one to four integers` and `generate EOF when done`,
reads up to four integers until end-of-file, and passes them to a maximum function whose first
argument is the number of values that follow, so one function serves one, two, three, or four
arguments; it then prints a blank line and `Maximum integer = …`. `dp-max` keeps:

- the task, the limit of one to four values, and reading until the end of the input;
- the report wording exactly: `Maximum integer = ` followed by the value;
- the two prompt lines word for word (with `--prompt`, FR-06);
- the teaching point: the maximum is computed by **one function that accepts any number of
  arguments** (NFR-05). Whether the number of arguments is passed explicitly, as the textbook
  does, or is known to the function through the language's own mechanism, is a design choice.

It changes the following, for the reasons given:

- **The count is checked.** The textbook's behavior with no integer, or with more than four, is
  not defined by its description. An input without a value is `unexpected end of input`, and a
  fifth token is `too many values` (FR-03), so the tool never prints a maximum of values it did
  not read or silently ignores values it did.
- **Invalid input is diagnosed.** A token that is not an integer stops the textbook's reading
  in an unspecified way; `dp-max` reports it with its line number and exits with status 1
  (FR-07).
- **64-bit values everywhere.** The textbook reads C `int`s, whose size varies by platform
  (16 bits was common in 1996). Values are 64-bit signed integers on every platform (FR-02,
  NFR-02). The maximum MUST NOT start from a sentinel such as "the smallest `int`", which would
  be wrong whenever the sentinel's type is narrower than the values (NFR-05).
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02). The integers are not accepted as
  command-line operands: negative values would look like options (CONV-10), and a data
  diagnostic needs a source and a line number (CONV-34).
- **The prompt is optional and goes to standard error** (FR-06), and the blank line before the
  result, which only separated it from the echoed keyboard input, is dropped (FR-04).

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each value uses the
*integer* grammar, with no further restriction), CONV-34 (data diagnostics, with the standard
messages `invalid integer` and `unexpected end of input`, one further message,
`too many values`, and the default consequences), CONV-36 (`-p`, `--prompt`, with one
two-line prompt), and CONV-37 (the input is *text data*). CONV-35 does not apply, because no
real number is written (integers are written as in CONV-35's last paragraph), and CONV-38 does
not apply, because nothing is random. Option syntax follows CONV-07 … CONV-12, diagnostics
follow CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. `dp-max` copies no input bytes to its output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-max [-p | --prompt] [FILE]
dp-max --help
dp-max --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-p` | `--prompt` | none | off | Write the prompt of FR-06 to standard error before the input is read |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, `--`, repetition, and scan order) follows CONV-07 … CONV-12. Giving
`-p` more than once has the same effect as giving it once (CONV-11). A token such as `-5` is an
option cluster, not a value: `dp-max -5` is the usage error `invalid option -- '5'`.

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The result line (FR-04) when the input is valid. Nothing else. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-09 … FR-12 instead.

### 3.6 Standard error
The prompt (FR-06, only with `--prompt`) and diagnostics (section 6). Without `--prompt`,
nothing is written to standard error when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The input held one to four valid integers and the result was written, or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-08), it held no value, more than four tokens, or an invalid integer (FR-03, FR-07), or standard output could not be written |
| 2 | Usage error (FR-11) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are the public fixture files in
`tests/fixtures/`: `readme.txt` is `15 42 8\n`; `one.txt` is `42\n`; `four-negative.txt` is
`-10 -2\n-50 -4\n`; `five.txt` is `1 2 3 4\n5\n`; `bad.txt` is `10 2O\n` (the letter O).

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. The input is opened before
anything is written (in particular before the prompt). More than one operand is a usage error
(FR-11).
*AC:* `dp-max < readme.txt` and `dp-max readme.txt` write the same line. *(UR-03)*

**FR-02: Tokens and values.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32). Line
structure has no meaning: values may share a line or be spread over several, separated by any
mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF input. Each of
the first four tokens MUST be a valid *integer* (CONV-33); a sign (`+7`, `-0`) and leading
zeros (`007`) are allowed, and every value from −9223372036854775808 to 9223372036854775807 is
accepted. A token that is not a valid *integer* is handled by FR-07.
*AC:* `dp-max four-negative.txt` → `Maximum integer = -2\n`; an input `3\r\n-1\r\n` followed by
one `0x1A` byte → `Maximum integer = 3\n`; an input `3 `, a `0x1A` byte, ` 4\n` →
`invalid integer` on line 1, because that Ctrl-Z byte does not end the input. *(UR-01, UR-02,
UR-09)*

**FR-03: Number of values.**
The input MUST hold at least one and at most four tokens. The tokens are checked in this order,
and the first failure is reported (FR-07):

1. Tokens 1 to 4 (as many as exist), in input order, are each validated as an *integer*.
2. If a fifth token exists, whatever its content, the input has too many values; tokens after
   the fifth are never examined.
3. If there is no token at all (an empty input, or one holding only whitespace and a trailing
   Ctrl-Z run), the input ends where a value is required.

*AC:* `dp-max five.txt` → stderr `dp-max: five.txt:2: too many values '5'\n`, stdout empty,
exit 1; `dp-max` with empty standard input → stderr `dp-max: -:1: unexpected end of input\n`,
exit 1; `1 2 3 4 junk` → `too many values 'junk'`; `1 junk 3 4 5` → `invalid integer 'junk'`;
an input of three LF-terminated blank lines → `unexpected end of input` on line 4. *(UR-04)*

**FR-04: Maximum and result line.**
For the values *v*₁ … *v*ₖ (1 ≤ *k* ≤ 4) the tool MUST compute the maximum *M* (section 1.3)
exactly, and write exactly the line

```text
Maximum integer = <M>
```

where `<M>` is the decimal of *M* (section 1.3), with one space on each side of `=`, no leading
or trailing spaces, and a single LF. The value is written as its value, not as a token was
spelled: `+07`, `007`, and `-0` are 7, 7, and 0. Nothing else is written to standard output.
*AC:* `dp-max < readme.txt` → stdout `Maximum integer = 42\n`, stderr empty, exit 0;
`dp-max one.txt` → `Maximum integer = 42\n`; `7 7 7` → `7`;
`-9223372036854775808 9223372036854775807` → `9223372036854775807`;
`-9223372036854775808` alone → `-9223372036854775808`. *(UR-01, UR-02)*

**FR-05: Validation before output.**
The tool MUST read the whole input and complete every check of FR-03 before it writes the
result line. If any check fails, nothing is written to standard output.
*AC:* `dp-max bad.txt` and `dp-max five.txt` write nothing to standard output. *(UR-04, UR-05)*

**FR-06: Prompt.**
`-p`, `--prompt` enables the single prompt of this tool, which is the 50 bytes

```text
Enter one to four integers
generate EOF when done
```

(two lines, each ending with one LF). With the prompt enabled, the tool MUST write it to
standard error, and flush standard error, once, after the input has been opened and before the
input is read — also when the input turns out to be empty (CONV-36). A diagnostic of FR-07
therefore starts on the line after the prompt. The prompt never changes standard output. No
prompt is written if the input cannot be opened.
*AC:* `dp-max --prompt < readme.txt` → stdout `Maximum integer = 42\n`, stderr
`Enter one to four integers\ngenerate EOF when done\n`, exit 0; `dp-max -p missing.txt` →
stderr only the CONV-16 diagnostic. *(UR-07)*

**FR-07: Invalid data.**
If one of the first four tokens is not a valid *integer* (CONV-33), including an integer
outside −2⁶³ … 2⁶³−1, the tool MUST write `dp-max: <source>:<line>: invalid integer '<token>'`.
If a fifth token exists, it MUST write `dp-max: <source>:<line>: too many values '<token>'`. If
the input has no token, it MUST write `dp-max: <source>:<line>: unexpected end of input`.
`<source>` is as defined in section 1.3, `<line>` is the token's line number, or the
end-of-input line number for `unexpected end of input` (CONV-32), and `<token>` is the
token's exact bytes (CONV-34). The tool then exits with status 1 (FR-05).
*AC:* `dp-max bad.txt` → stderr `dp-max: bad.txt:1: invalid integer '2O'\n`, stdout empty,
exit 1; `9223372036854775808` and `-9223372036854775809` give `invalid integer`. *(UR-05)*

**FR-08: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-max: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. When standard input fails, `<source>` is `-`.
*AC:* `dp-max missing.txt` → stderr `dp-max: missing.txt: No such file or directory\n`, stdout
empty, exit 1; `dp-max subdir` where `subdir` is a directory → `dp-max: subdir: Is a directory`.
*(UR-08)*

**FR-09: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read and no prompt is
written.
*AC:* `dp-max --help` matches the user manual exactly; `dp-max a b --help` also prints it.
*(UR-10)*

**FR-10: Version.**
`--version` MUST write `dp-max (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-11: Usage errors.**
Unknown options, and arguments supplied to options that take none (`--prompt=…`, `--help=…`,
`--version=…`), MUST be reported with the CONV-13 messages followed by the CONV-14 line, with
exit status 2. Long options MUST NOT be abbreviated (CONV-08). A second operand MUST be
reported as `dp-max: extra operand '<second operand>'`, after the whole argument list has been
scanned (CONV-12).
*AC:* `dp-max readme.txt one.txt` → `dp-max: extra operand 'one.txt'`; `dp-max -x --help` →
`dp-max: invalid option -- 'x'`; `dp-max --prompt=1` →
`dp-max: option '--prompt' doesn't allow an argument`; `dp-max -5` →
`dp-max: invalid option -- '5'`; each followed by the CONV-14 line, exit 2. *(UR-11, UR-12)*

**FR-12: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, write the
prompt, or write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: integer width | Values MUST be held, compared, and written as 64-bit signed integers on every platform, whatever the width of the language's native types: C and C++ `long` has 32 bits on Windows and 64 bits on Linux and macOS, `int` may have 16 or 32, and some runtimes represent numbers as binary64, which is exact only up to 2⁵³. Parsing MUST reject values outside −2⁶³ … 2⁶³−1 instead of wrapping or saturating (as C's `atoi` or `strtol` into a 32-bit `long` would), and MUST be locale-independent. The input MUST be read in binary mode, so CR bytes reach the tokenizer and a `0x1A` byte is never treated as end-of-file by the I/O layer; at an interactive console the platform's own end-of-input signal (Ctrl-D on POSIX terminals, Ctrl-Z followed by Enter in a Windows console) MUST end the input normally. | CI black-box tests on 3 OSes; code review; manual console check |
| NFR-03 | Performance | Any input of up to 1 MiB MUST be processed in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 8 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including tokens of any length and integers far outside the 64-bit range. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability: one variadic maximum function | The maximum MUST be computed by **one function that accepts any number of integer arguments (one or more)**, using the language's own mechanism for variable-arity calls — for example a variadic parameter list, rest or "varargs" parameters, a parameter pack, or a macro that expands to one call — or, in a language that has no such mechanism, a single parameter holding a sequence whose length is not fixed. The function MUST return the maximum and do nothing else: no input, output, parsing, or prompting. It MUST NOT limit the number of arguments to four, or to any other number; the limit of four belongs to the driver (FR-03), which MUST call the function exactly once, with all the values read. The function MUST start from its first argument, not from a sentinel value. There MUST NOT be separate functions or code paths for one, two, three, and four values. | Design review |
| NFR-06 | Testability | The maximum function MUST be covered by unit tests that call it with 1, 2, 3, 4, and 10 arguments, with all values equal, with the maximum in the first and in the last position, with only negative values, and with −2⁶³ and 2⁶³−1. The token validation MUST be unit-tested with each acceptance value of FR-02, FR-03, and FR-07. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-max --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (including a digit, as in `-5`) | `dp-max: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-max: unrecognized option 'T'` |
| `--prompt=…`, `--help=…`, `--version=…` | `dp-max: option '--prompt' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X` | `dp-max: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-max: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-max: F: Permission denied` |
| FILE `F` is a directory | `dp-max: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-max: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-max: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| One of the first four tokens, `K` on line `L` of source `S`, is not a valid *integer* | `dp-max: S:L: invalid integer 'K'` |
| A fifth token `K` exists, on line `L` | `dp-max: S:L: too many values 'K'` |
| The input holds no token (end-of-input line `L`) | `dp-max: S:L: unexpected end of input` |
| Standard output cannot be written (other than a broken pipe) | `dp-max: write error` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-07, FR-09, FR-11, FR-12 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 05 and 07 … 10 have several steps) | FR-01 … FR-12 |
| Unit test (written by the implementer) | FR-02 … FR-04, NFR-06 |
| Measurement | NFR-03 |
| Design review | NFR-05 |
| Inspection / review | NFR-02, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-max < readme.txt` | FR-01, FR-04 |
| 02 | `dp-max readme.txt` | FR-01 |
| 03 | `dp-max one.txt` | FR-03 (one value), FR-04 |
| 04 | `dp-max four-negative.txt` | FR-02 (values on two lines), FR-03 (four values), FR-04 (all negative) |
| 05 | `dp-max --prompt < readme.txt` | FR-06 |
| 06 | `dp-max` (empty standard input) | FR-03, FR-07 (`unexpected end of input`) |
| 07 | `dp-max five.txt` | FR-03, FR-05, FR-07 (`too many values`) |
| 08 | `dp-max bad.txt` | FR-05, FR-07 (`invalid integer`) |
| 09 | `dp-max --help` | FR-09 |
| 10 | `dp-max readme.txt one.txt` | FR-11, FR-12 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-02, FR-03, FR-04 |
| UR-02 | FR-02, FR-04, NFR-02, NFR-05 |
| UR-03 | FR-01, CONV-26 |
| UR-04 | FR-03, FR-05, CONV-34 |
| UR-05 | FR-05, FR-07, CONV-33, CONV-34 |
| UR-06 | NFR-05, NFR-06 |
| UR-07 | FR-06, CONV-36 |
| UR-08 | FR-08, CONV-16 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-09, FR-10 |
| UR-11 | FR-11, FR-12 |
| UR-12 | NFR-01, NFR-02, FR-11, CLI-CONV |
| UR-13 | NFR-03, NFR-07 |
