# Software Requirements Specification (SRS) — dp-taxes-file

| Field | Value |
| :-- | :-- |
| Document ID | SRS-14 |
| Project | `14-taxes-file` — Batch File-Based Progressive Income Tax Calculator |
| Product | `dp-taxes-file` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-14) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-taxes-file`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output, and byte-identical report files, for every invocation. It is the
authoritative source for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-taxes-file` reads incomes as integer tokens from an input file (by default `incomes.dat`)
or standard input, checks all of them, and then writes the report — two lines per income,
giving the income and the tax due under a two-bracket progressive rule — to an output file (by
default `out.dat`), replacing its contents, or to standard output. If the input cannot be read
or contains an invalid income, the output file is not created or changed.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| INPUT | The value of `-i`/`--input`, or `incomes.dat` if neither is given |
| OUTPUT | The value of `-o`/`--output`, or `out.dat` if neither is given |
| Input | The byte sequence read from the file INPUT, or from standard input when INPUT is `-` |
| Source | The name used for the input in diagnostics: INPUT exactly as given (so `-` for standard input) |
| Output file | The file named by OUTPUT, when OUTPUT is not `-` |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Income | The value *I* of a token that is a valid *integer* (CONV-33) with 0 ≤ *I* ≤ 9223372036854775807 (2⁶³−1) |
| Tax | The value *T* computed from an income by the tax rule (FR-03) |
| Record | The two report lines for one income (FR-04) |
| Report | The concatenation of the records of all incomes of the input, in input order; empty if the input has no tokens |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-14: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §1.10 (informative; see §2.5)
- SRS-13 (`projects/13-taxes/specs/SRS.md`): the stream variant, which specifies the same tax
  rule and record format word for word (FR-03, FR-04). It is cited for context only; this SRS
  is complete and normative on its own.

## 2. Overall description

### 2.1 Product perspective
`dp-taxes-file` is a standalone executable. Its interfaces are the command line, the input file
or standard input, the output file or standard output, standard error, and the exit status. It
belongs to the curriculum's applications-programming track (Projects 11–52) and adapts §1.10
of Johnsonbaugh & Kalin, *Applications Programming in ANSI C*. It is the batch counterpart of
`dp-taxes` (Project 13), which reads a stream interactively and writes to standard output.

### 2.2 Product functions
1. Read the input file (`incomes.dat` by default) or standard input.
2. Check every income in the input before any output is produced.
3. Compute the tax on each income exactly, under the two-bracket rule.
4. Write the report to the output file (`out.dat` by default), replacing its contents, or to
   standard output.
5. Report unreadable input, invalid incomes, and unwritable output.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- The tax MUST be computed in exact integer arithmetic (FR-03). Binary floating point MUST NOT
  be used to compute or round it.

### 2.4 Assumptions
- The current working directory is where the default files `incomes.dat` and `out.dat` are
  looked for and created; relative paths are relative to it.
- The input may contain any bytes; only tokens that match the *integer* grammar are incomes.
- Nothing else writes the input or output file while the tool runs.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §1.10 is the program of §1.6 changed to read its incomes from the file
`incomes.dat` and to write the same two lines per income to the file `out.dat`, which it
creates or truncates. `dp-taxes-file` keeps:

- the two-bracket rule, the threshold 6000 (inclusive in the upper bracket), and the two rates;
- the record wording and layout exactly: two lines per income, no blank lines, no header;
- the file names `incomes.dat` and `out.dat` as defaults in the current directory, and the
  replacement (not appending) of the output file; an empty input yields an empty output file;
- silence on success: nothing is written to standard output or standard error.

It changes the following, for the reasons given:

- **Exact arithmetic and negative incomes**, exactly as in `dp-taxes`: the textbook's
  floating-point multiplication is inexact for incomes above 2⁵³ (0.6 × 10000000000000003
  evaluates to 6000000000000002 in binary64, while the exact tax is 6000000000000001), so FR-03
  defines the exact result for every 64-bit income; negative incomes, for which the textbook
  would compute a negative tax, are rejected (FR-07).
- **The whole input is checked first** (FR-06). The textbook opens both files at the start and
  writes each record as it reads each income, so a missing input or a bad income can leave
  `out.dat` truncated or half-written. Here the input is read and validated completely before
  the output file is opened; a missing input or an invalid income leaves the output file
  exactly as it was. The cost is that the incomes (or the input) are held in memory, which
  NFR-03 bounds; the section's description suggests streaming, which is incompatible with this
  guarantee when the input is standard input.
- **File names can be overridden**, and `-` selects standard input or standard output
  (FR-01, FR-05). This makes the tool usable in pipelines, and makes the report observable by
  black-box tests, which compare only standard output, standard error, and the exit status.
- **Failures are diagnosed** with the CONV-16 and CONV-34 messages and exit status 1 (FR-07 …
  FR-09); the textbook program does not check whether its files could be opened.
- **Data files** with CRLF line endings and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. From section 10 it
incorporates: CONV-32 (the input is read as tokens; line numbers), CONV-33 (each token uses the
*integer* grammar, further restricted to 0 … 2⁶³−1), CONV-34 (data diagnostics, with the
standard messages `invalid integer` and `value out of range`; because of FR-06, no report has
been produced when one is written), and CONV-37 (the input is *text data*). CONV-35 does not
apply, because no real number is ever written; CONV-36 does not apply, because the tool has no
prompts (it does not accept `-p`); CONV-38 does not apply, because nothing is random. Option
syntax follows CONV-07 … CONV-12, diagnostics follow CONV-13 … CONV-16 (CONV-16 is applied to
the output file as well as the input), and the exit statuses are those of CONV-18. Standard
input is read only when INPUT is `-` (CONV-26). `dp-taxes-file` copies no input bytes to its
output, so CONV-04 does not apply.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-taxes-file [-i FILE | --input=FILE] [-o FILE | --output=FILE]
dp-taxes-file --help
dp-taxes-file --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-i` | `--input` | FILE (required) | `incomes.dat` | Read the incomes from FILE; `-` is standard input (FR-01) |
| `-o` | `--output` | FILE (required) | `out.dat` | Write the report to FILE, replacing its contents; `-` is standard output (FR-05) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (`-iFILE`, `--input FILE`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. If an option is repeated, the last occurrence wins (CONV-11). FILE may begin with `-`
when it is attached (`--input=-x`, `-i-x`) or supplied as the next token (`-i -x`). An empty
FILE is an invalid option value (FR-12).

### 3.3 Operands
`dp-taxes-file` accepts **no operands**. File names are given with `-i` and `-o`.

### 3.4 Standard input
Read only when INPUT is `-` (FR-01). Read as raw bytes; no newline translation of any kind is
performed on any platform.

### 3.5 Standard output
The report when OUTPUT is `-` (FR-05); otherwise nothing. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-10 … FR-13 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success.

### 3.7 Files
- The input file INPUT is opened for reading only; it is never modified (unless it is also the
  output file, FR-06).
- The output file OUTPUT is created if it does not exist, or truncated and rewritten if it does,
  only in step 4 of FR-06. No other file is created, and no file is deleted or renamed.

### 3.8 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The report was written completely (including an empty report), or `--help` / `--version` was handled |
| 1 | The input could not be read (FR-08), it contained an invalid income (FR-07), or the output could not be opened or written (FR-09) |
| 2 | Usage error (FR-12) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are public fixture files in
`tests/fixtures/`: `incomes.dat` is `4500\n6000\n12000\n`; `more.dat` is
`0 5999\t6000\r\n+4500   007\r\n\r\n  12345 1\n`; `bad.dat` is `4500\n6000\n12,000\n9000\n`;
`prev.dat` is `100\n`; `empty.dat` is empty. `R` denotes the report of `incomes.dat`:
`Income = 4500 greenbacks\nTax = 1350 greenbacks\nIncome = 6000 greenbacks\nTax = 3600 greenbacks\nIncome = 12000 greenbacks\nTax = 7200 greenbacks\n`.

**FR-01: Input.**
If INPUT is `-`, the tool MUST read standard input to its end. Otherwise it MUST open the file
INPUT (a path relative to the current directory unless absolute) and read it to its end as raw
bytes. Without `-i`/`--input`, INPUT is `incomes.dat`.
*AC:* `dp-taxes-file -o -` → stdout `R`, exit 0; `dp-taxes-file -i - -o - < incomes.dat` →
the same. *(UR-01, UR-02)*

**FR-02: Tokens and incomes.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order. Each token MUST be a valid *integer* (CONV-33) whose value lies in
0 … 9223372036854775807; that value is the income. A sign (`+5`, `-0`) and leading zeros
(`007`) are allowed. Line structure has no meaning: incomes may be separated by any mixture of
space, TAB, VT, FF, CR, and LF, so CRLF input reads exactly like LF input. A token that is not a
valid *integer*, or whose value lies outside that range, is handled by FR-07.
*AC:* `dp-taxes-file --input=more.dat --output=-` writes records for the incomes 0, 5999, 6000,
4500, 7, 12345, and 1, in that order, exit 0. *(UR-03, UR-09)*

**FR-03: Tax rule.**
For an income *I* (0 ≤ *I* ≤ 2⁶³−1) the tax *T* MUST be

- *T* = ⌊*I* × 30 / 100⌋ if *I* < 6000 (lower bracket), and
- *T* = ⌊*I* × 60 / 100⌋ if *I* ≥ 6000 (upper bracket),

where ⌊*x*⌋ is the largest integer not greater than *x*. *T* MUST be the exact mathematical
value; since *I* ≥ 0, rounding down is the same as truncation toward zero. The computation
MUST use integer arithmetic only. It MUST NOT overflow: the product *I* × 60 exceeds 2⁶³−1 for
*I* > 153722867280912930, so an implementation that uses 64-bit integers MUST rearrange the
computation, for example as *T* = *r* × *q* + ⌊*r* × *m* / 100⌋ with *r* the rate (30 or 60),
*q* = ⌊*I* / 100⌋, and *m* = *I* − 100 × *q*. The result always satisfies 0 ≤ *T* ≤ *I*.
*(This requirement is word for word the same as SRS-13 FR-03.)*
*AC:* 0 → 0; 1 → 0; 7 → 2; 4500 → 1350; 5000 → 1500; 5995 → 1798; 5999 → 1799; 6000 → 3600;
6009 → 3605; 10000 → 6000; 10000000000000003 → 6000000000000001;
9223372036854775807 → 5534023222112865484. *(UR-03)*

**FR-04: Record format.**
The record for an income *I* with tax *T* MUST be exactly the two lines

```text
Income = <I> greenbacks
Tax = <T> greenbacks
```

where `<I>` and `<T>` are the decimals of *I* and *T* (section 1.3), each line ends with a
single LF, and there are no other spaces: one space on each side of `=` and one before
`greenbacks`, no leading or trailing spaces. The income is written as its value, not as the
token was spelled: `+4500`, `007`, and `-0` are written as `4500`, `7`, and `0`. Records follow
one another with no blank lines, header, or summary.
*(This requirement is word for word the same as SRS-13 FR-04.)*
*AC:* the report of `incomes.dat` is `R`. *(UR-04)*

**FR-05: Output.**
If OUTPUT is `-`, the tool MUST write the report to standard output. Otherwise it MUST create
the file OUTPUT if it does not exist, or truncate it to zero length if it does, write the report
to it as raw bytes (LF line endings on every platform, NFR-02), and close it; the file then
contains exactly the report. Nothing is written to standard output in that case. Without
`-o`/`--output`, OUTPUT is `out.dat`. An empty report produces an empty output file (or no
standard output) and exit status 0.
*AC:* `dp-taxes-file` → stdout and stderr empty, exit 0, and `out.dat` exists and begins with
the token `Income` (a later `dp-taxes-file -i out.dat -o -` reports
`dp-taxes-file: out.dat:1: invalid integer 'Income'`). After `dp-taxes-file -i empty.dat -o
prev.dat`, `dp-taxes-file -i prev.dat -o -` writes nothing and exits 0, whereas before it wrote
the record for 100. *(UR-01, UR-02, UR-05)*

**FR-06: Order of operations.**
After a successful scan of the arguments, the tool MUST proceed in exactly this order and stop
at the first failure:

1. Read the whole input (FR-01). A failure is handled by FR-08.
2. Check every token (FR-02), in input order. The first invalid token is handled by FR-07.
3. Compute the report (FR-03, FR-04).
4. Only now, if OUTPUT is not `-`, open (create or truncate) the output file. A failure is
   handled by FR-09.
5. Write the report to the output file or standard output, and close the output file.

Consequently a failure in steps 1 or 2 MUST leave the output file exactly as it was — not
created if it did not exist, not truncated or modified if it did — and MUST write nothing to
standard output. Because the input has been read completely before the output file is opened,
INPUT and OUTPUT may name the same file: the file is replaced by the report of its previous
contents. After a failure in step 5, the contents of the output file are unspecified (it may be
partially written); the tool does not delete it.
*AC:* `dp-taxes-file -i bad.dat -o prev.dat` → exit 1, and a later
`dp-taxes-file -i prev.dat -o -` still writes the record for 100; `dp-taxes-file -i bad.dat -o -`
→ stdout empty; `dp-taxes-file -i missing.dat` → exit 1, and a later `dp-taxes-file -i out.dat`
reports that `out.dat` does not exist. With `self.dat` containing `7000\n`,
`dp-taxes-file -i self.dat -o self.dat` → exit 0, and `self.dat` then begins with `Income`.
*(UR-06)*

**FR-07: Invalid incomes.**
If a token is not a valid *integer* (CONV-33), including an integer outside −2⁶³ … 2⁶³−1, the
tool MUST write `dp-taxes-file: <source>:<line>: invalid integer '<token>'`. If it is a valid
*integer* below 0, the tool MUST write
`dp-taxes-file: <source>:<line>: value out of range '<token>'`. `<source>` is as defined in
section 1.3, `<line>` is the token's line number (CONV-32), and `<token>` is the token's exact
bytes (CONV-34). Only the first invalid token is reported. The tool then exits with status 1
without producing any output (FR-06).
*AC:* `dp-taxes-file -i bad.dat -o -` → stdout empty, stderr
`dp-taxes-file: bad.dat:3: invalid integer '12,000'\n`, exit 1. A token `-1` gives
`value out of range '-1'`; `9223372036854775808` gives `invalid integer`; with standard input,
the source is `-` (`dp-taxes-file: -:3: …`). *(UR-06, UR-07)*

**FR-08: Unreadable input.**
If INPUT does not exist, cannot be opened, is a directory, or a read error occurs, the tool MUST
write `dp-taxes-file: <source>: <reason>` with `<reason>` from the CONV-16 table, and exit with
status 1 without opening the output file (FR-06).
*AC:* `dp-taxes-file -i missing.dat` → stderr
`dp-taxes-file: missing.dat: No such file or directory\n`, stdout empty, exit 1, and no
`out.dat` is created. `dp-taxes-file -i subdir -o nodir/out.dat`, where `subdir` is a
directory and `nodir` does not exist, reports only `dp-taxes-file: subdir: Is a directory`.
*(UR-06, UR-07)*

**FR-09: Unwritable output.**
If the output file cannot be created or opened for writing — because a directory in OUTPUT does
not exist, OUTPUT is a directory, access is denied, or any other reason — the tool MUST write
`dp-taxes-file: <output>: <reason>`, where `<output>` is OUTPUT exactly as given and `<reason>`
is from the CONV-16 table, and exit with status 1. If writing or closing the output file fails,
the tool MUST write `dp-taxes-file: <output>: Input/output error` and exit with status 1. If
standard output cannot be written (OUTPUT is `-`), the tool MUST write
`dp-taxes-file: write error` and exit with status 1, except that a broken pipe ends the tool
quietly (CONV-25).
*AC:* `dp-taxes-file -o subdir` → `dp-taxes-file: subdir: Is a directory`, exit 1;
`dp-taxes-file -o nodir/out.dat` → `dp-taxes-file: nodir/out.dat: No such file or directory`,
exit 1. *(UR-07, UR-08)*

**FR-10: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No file is read or written.
*AC:* `dp-taxes-file --help` matches the user manual exactly; `dp-taxes-file extra --help` also
prints it. *(UR-10)*

**FR-11: Version.**
`--version` MUST write `dp-taxes-file (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match; `dp-taxes-file -i missing.dat --version` also prints it and exits 0. *(UR-10)*

**FR-12: Usage errors.**
Unknown options (including `-p` and `--prompt`, which this tool does not have), missing option
arguments, and arguments supplied to `--help` or `--version`, MUST be reported with the CONV-13
messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated
(CONV-08): `--in` is unrecognized. An empty FILE value MUST be reported as
`dp-taxes-file: invalid argument '' for '<option>'`, where `<option>` is `-i`, `--input`,
`-o`, or `--output` as the user wrote it; only the winning occurrence of a repeated option is
checked (CONV-11). Any operand MUST be reported as `dp-taxes-file: extra operand '<first
operand>'`. Option values and operands are checked after the whole argument list has been
scanned (CONV-12).
*AC:* `dp-taxes-file incomes.dat` → `dp-taxes-file: extra operand 'incomes.dat'`;
`dp-taxes-file -i ''` → `dp-taxes-file: invalid argument '' for '-i'`; `dp-taxes-file --input`
→ `dp-taxes-file: option '--input' requires an argument`; `dp-taxes-file --prompt --help` →
`dp-taxes-file: unrecognized option '--prompt'`; each followed by the CONV-14 line, exit 2.
*(UR-11, UR-13)*

**FR-13: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT read standard input or any file, MUST NOT create,
truncate, or modify any file, and MUST NOT write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case, and `out.dat` is not created. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Standard output, standard error, and the bytes of the output file MUST be identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: file creation and binary-mode writing | The input file and the output file MUST be opened in binary mode on every platform: no CRLF is ever written to the output file, and a `0x1A` byte never ends the input early at the I/O layer (only FR-02 interprets a trailing Ctrl-Z run). Creating or truncating the output file MUST work identically whether or not it exists, and the CONV-16 reason MUST be derived portably: for example, opening a directory for writing fails with `EISDIR` on Linux and macOS but with "access denied" on Windows, and both MUST be reported as `Is a directory`; a missing parent directory (`ENOENT`, `ERROR_PATH_NOT_FOUND`) MUST be reported as `No such file or directory`. Paths are used exactly as given; `/` MUST work as a separator on every platform. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Processing an input of 1 000 000 incomes (about 7 MiB) MUST take under 1 s for a natively compiled build (under 10 s for an interpreted runtime) on CI hardware, with peak memory under 128 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MAY grow linearly with the size of the input, because the whole input is checked before any output is written (FR-06). Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list, input bytes, or file-system condition (CONV-24), including tokens of any length and integers far outside the 64-bit range. | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, input reading, income validation, the tax rule, report formatting, and output-file handling MUST be separate units. The tax rule MUST be one function of the income that is the only place the threshold and the two rates appear. Every file the tool opens MUST be closed on every path, including failures. | Design review |
| NFR-06 | Testability | The tax function and the report formatter MUST be pure functions covered by unit tests, including every acceptance value of FR-03, the incomes 5999, 6000, 153722867280912930, 153722867280912931, and 2⁶³−1. The order of operations of FR-06 MUST be covered by integration tests that inspect the output file's bytes directly: after a successful run (including an empty input and INPUT equal to OUTPUT), after a data error, after a missing input, and with a pre-existing output file. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only INPUT (or standard input), MUST create or modify only OUTPUT, MUST NOT delete or rename any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-taxes-file --help' for more
information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-taxes-file: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-taxes-file: unrecognized option 'T'` |
| `-i` / `-o` without an argument | `dp-taxes-file: option requires an argument -- 'i'` (or `'o'`) |
| `--input` / `--output` without an argument | `dp-taxes-file: option '--input' requires an argument` (or `'--output'`) |
| `--help=…` / `--version=…` | `dp-taxes-file: option '--help' doesn't allow an argument` (or `'--version'`) |
| Empty FILE for `-i`, `--input`, `-o`, or `--output` | `dp-taxes-file: invalid argument '' for '-i'` (or the option as written) |
| Operand `X` | `dp-taxes-file: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| INPUT `F` does not exist | `dp-taxes-file: F: No such file or directory` |
| INPUT `F` cannot be opened or read because access is denied | `dp-taxes-file: F: Permission denied` |
| INPUT `F` is a directory | `dp-taxes-file: F: Is a directory` |
| A component of INPUT `F` is not a directory | `dp-taxes-file: F: Not a directory` |
| Any other open or read failure of INPUT `F` (including standard input, `F` = `-`) | `dp-taxes-file: F: Input/output error` |
| Token `K` on line `L` of source `S` is not a valid *integer* | `dp-taxes-file: S:L: invalid integer 'K'` |
| Token `K` on line `L` of source `S` is a valid *integer* below 0 | `dp-taxes-file: S:L: value out of range 'K'` |
| A directory in OUTPUT `G` does not exist | `dp-taxes-file: G: No such file or directory` |
| OUTPUT `G` cannot be created or opened because access is denied | `dp-taxes-file: G: Permission denied` |
| OUTPUT `G` is a directory | `dp-taxes-file: G: Is a directory` |
| A component of OUTPUT `G` is not a directory | `dp-taxes-file: G: Not a directory` |
| Any other failure to open, write, or close OUTPUT `G` | `dp-taxes-file: G: Input/output error` |
| Standard output cannot be written (OUTPUT is `-`; other than a broken pipe) | `dp-taxes-file: write error` |

## 7. Verification

The black-box harness compares only standard output, standard error, and exit status, so tests
observe the output file indirectly: with `-o -`, the report itself is compared; in multi-step
tests, a later step reads the file an earlier step wrote with `-i FILE -o -`. A file that holds
a report is then reported as `FILE:1: invalid integer 'Income'`, a missing file as
`No such file or directory`, an empty file as no output and exit 0, and an untouched fixture of
incomes by its records.

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases; cases 02, 05, 06, and 07 have several steps) | FR-01 … FR-08, FR-10, FR-12, FR-13 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 03 … 10 have several steps) | FR-01 … FR-13 |
| Unit test (written by the implementer) | FR-02 … FR-04, NFR-06 |
| Integration test (written by the implementer, inspecting file bytes) | FR-05, FR-06, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command(s) | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-taxes-file -o -` | FR-01 (default input), FR-03, FR-04, FR-05 |
| 02 | `dp-taxes-file`; `dp-taxes-file -i out.dat -o -` | FR-01, FR-05 (default output file created), FR-07 |
| 03 | `dp-taxes-file --input=more.dat --output=-` | FR-02 (CRLF, TAB, sign, leading zeros), FR-03 (boundaries) |
| 04 | `dp-taxes-file -i - -o - < incomes.dat` | FR-01, FR-05 (standard input and output) |
| 05 | `dp-taxes-file -i prev.dat -o -`; `dp-taxes-file -i empty.dat -o prev.dat`; `dp-taxes-file -i prev.dat -o -` | FR-05 (existing file truncated; empty report) |
| 06 | `dp-taxes-file -i bad.dat -o prev.dat`; `dp-taxes-file -i prev.dat -o -` | FR-06 (output untouched after a data error), FR-07 |
| 07 | `dp-taxes-file -i missing.dat`; `dp-taxes-file -i out.dat` | FR-06, FR-08 (no output file created) |
| 08 | `dp-taxes-file -i bad.dat -o -` | FR-06 (nothing written), FR-07 |
| 09 | `dp-taxes-file --help` | FR-10 |
| 10 | `dp-taxes-file incomes.dat` | FR-12, FR-13 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-05 |
| UR-02 | FR-01, FR-05, CONV-26 |
| UR-03 | FR-02, FR-03 |
| UR-04 | FR-04 |
| UR-05 | FR-05 |
| UR-06 | FR-06, FR-07, FR-08 |
| UR-07 | FR-07, FR-08, FR-09, CONV-16, CONV-34 |
| UR-08 | FR-09, NFR-02 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-10, FR-11 |
| UR-11 | FR-12, FR-13 |
| UR-12 | NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-12, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
