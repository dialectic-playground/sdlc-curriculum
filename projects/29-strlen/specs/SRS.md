# Software Requirements Specification (SRS) — dp-strlen

| Field | Value |
| :-- | :-- |
| Document ID | SRS-29 |
| Project | `29-strlen` — String Length from First Principles |
| Product | `dp-strlen` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-29) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-strlen`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-strlen` prints the length of each STRING operand or, when no operand is given, of each line
of standard input or of the file named with `-f`, `--file`. Lengths are counted in characters
under a fixed UTF-8 rule, or in bytes, by an explicit scan. Unreadable files are reported with
fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF, CR | The line-feed byte `0x0A`; the carriage-return byte `0x0D` |
| String mode | The mode used when at least one STRING operand is given (FR-01) |
| Line mode | The mode used when no STRING operand is given (FR-01) |
| Input | In line mode, the byte sequence read from standard input or from the file named by `-f` |
| Source | The name used for the input in diagnostics: the value of `-f` exactly as given, or `-` when standard input is read |
| Line | One of the byte sequences into which the input is divided by FR-04 |
| String | A STRING operand's bytes (FR-02), or a line |
| Character, character length, byte length | As defined in FR-05 |
| Length | The character length of a string, or its byte length when `-b` is given |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |

### 1.4 References
- URD-29: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- SRS-04 (`projects/04-wc/specs/SRS.md`) FR-06: the decoding rule that FR-05 restates
- SRS-27 (`projects/27-line-wrap/specs/SRS.md`) FR-04 and SRS-33
  (`projects/33-reverse/specs/SRS.md`) FR-04: the same character rule, word for word; SRS-33
  FR-03 divides lines by the same rule as FR-04
- The Unicode Standard, Version 15.0, §3.9, Table 3-7 "Well-Formed UTF-8 Byte Sequences"
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §5.8 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-strlen` is a standalone executable in the tradition of `expr length` and `wc -L`. Its
interfaces are the command line, standard input or the file named by `-f`, standard output,
standard error, and the exit status. It belongs to the curriculum's applications-programming
track (Projects 11–52) and adapts §5.8 of Johnsonbaugh & Kalin, *Applications Programming in
ANSI C*. It measures characters with the rule of `dp-wc -m` (Project 04), which `dp-wrap`
(Project 27) and `dp-reverse` (Project 33) also use.

### 2.2 Product functions
1. Measure each STRING operand.
2. Without operands, divide standard input or a file into lines and measure each line.
3. Count characters by a fixed UTF-8 rule, or bytes, by an explicit scan.
4. Write one decimal length per string, in order.
5. Report unreadable input files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior, and the design requirement of FR-06.
- Character lengths MUST be computed from the byte-level rule of FR-05. Library facilities
  whose results depend on locale or platform (locale-aware classification, multibyte-conversion
  functions, display-width functions, text-mode file reading) MUST NOT determine any length
  (NFR-02).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may be of any size, may contain any bytes (including NUL), and need not be valid
  UTF-8 or end with LF. Lines may be of any length.

### 2.5 Relationship to the textbook program (informative)
The textbook section of §5.8 presents a function that computes the length of a string by
starting at its first character and advancing, one character at a time, until it reaches the
terminating null character, counting the steps. Its test program measures a string and prints
the result. `dp-strlen` keeps:

- the algorithm: the length is the number of steps of a scan from the first byte to the end,
  never a stored or library-supplied length (FR-06);
- the results the section's description gives: the empty string has length 0, `a` has
  length 1, `hello world` has length 11, and `ANSI C` has length 6.

It changes the following, for the reasons given:

- **A command-line tool instead of a demonstration.** The tool measures every STRING operand,
  or every line of standard input or of a file (FR-01 … FR-04), and prints one number per
  string, so it is useful in scripts.
- **Characters by default.** The textbook counts bytes, so `Zoë` is 4 long. `dp-strlen` counts
  characters with the rule of `dp-wc -m` (FR-05), so every curriculum tool measures text the
  same way; `-b`, `--bytes` counts bytes as the textbook did. Both are defined for every byte
  sequence, valid UTF-8 or not.
- **The end of a string is not a NUL byte.** In line mode a string ends at an LF or at the end
  of the input, and a NUL byte inside a line is counted like any other byte (FR-04). The scan
  therefore stops at a known end rather than at a sentinel; the step-by-step counting is
  unchanged.
- **Line endings are normalized.** One CR before an LF, or at the very end of the input, is not
  part of the line, so a CRLF file gives the same lengths as an LF file, and a trailing Ctrl-Z
  run is ignored (FR-04). This deliberately differs from `dp-wc -L`, which counts a CR as a
  character: `dp-strlen` measures the text of a line, not its stored bytes.
- **No prompts.** The textbook program prints no prompt, so `dp-strlen` has no `--prompt`.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read only in
line mode (CONV-26). Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Not applicable: the input is line-oriented, not read as tokens (FR-04). |
| CONV-33 | Not applicable: no numbers are read. |
| CONV-34 | Not applicable: every byte sequence is a valid input, so there are no data diagnostics. |
| CONV-35 | Not applicable: no real numbers are written. |
| CONV-36 | Not applicable: the textbook program did not prompt, so there is no `--prompt`. |
| CONV-37 | Applies: the input of line mode is *text data* (FR-04). |
| CONV-38 | Not applicable: nothing is random. |

**Note on CONV-10:** STRING operands are strings, not files. The operand `-` is the one-byte
string `-` (length 1), not standard input; a file, including standard input, is named only with
`-f`.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-strlen [-b | --bytes] STRING...
dp-strlen [-b | --bytes] [-f FILE | --file=FILE]
dp-strlen --help
dp-strlen --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-f` | `--file` | FILE | standard input | In line mode, read the lines from FILE; the FILE `-` is standard input (FR-03) |
| `-b` | `--bytes` | none | off | Count bytes instead of characters (FR-05) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

FILE MUST NOT be empty; the empty string is an invalid option value (CONV-13), reported with the
option as written (`-f` or `--file`). Option syntax (bundling such as `-bf FILE`, `--`,
repetition, and scan order) follows CONV-07 … CONV-12; if `-f` is repeated, the last value is
used (CONV-11), and earlier values are neither validated nor opened.

### 3.3 Operands
Zero or more STRING operands, measured in the order given. Every token after `--` is an
operand, even if it begins with `-`. The operand `-` is an ordinary string (section 2.6). If
`-f` is given, no operand is allowed (FR-11).

### 3.4 Standard input
Read only in line mode, when `-f` is not given or its value is `-` (FR-03). Read as raw bytes;
no newline translation of any kind is performed on any platform. In string mode standard input
is never read.

### 3.5 Standard output
One length per string (FR-07). Nothing else. On a usage error, or when `--help` / `--version`
is handled, the output is as specified by FR-09 … FR-12 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every string was measured (including the case of an input with no lines), or `--help` / `--version` was handled |
| 1 | The input could not be opened or read (FR-08), or standard output could not be written |
| 2 | Usage error (FR-11) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\r` denotes CR, and the files named are the public
fixtures in `tests/fixtures/`: `lines.txt` is
`hello\n\nhello world\nANSI C\n  tabs\tand spaces  \n`; `crlf.txt` is the same text with every
LF preceded by CR; `utf8.txt` is the four lines `Zoë`, `日本語`, `🙂`, and `naïve café`, each
followed by LF.

**FR-01: Mode.**
If at least one STRING operand is given, the tool MUST work in string mode: it measures each
operand (FR-02) and reads no input. Otherwise it MUST work in line mode: it reads the input
(FR-03), divides it into lines (FR-04), and measures each line.
*AC:* `dp-strlen hello` → stdout `5\n`, exit 0, standard input not read; `dp-strlen < lines.txt`
measures the lines of `lines.txt`. *(UR-01, UR-02)*

**FR-02: String operands.**
The string of a STRING operand is the operand's UTF-8 encoding exactly as given (CONV-05): its
bytes on POSIX, or the UTF-8 conversion of its UTF-16 text on Windows. No escape sequences are
interpreted, and the empty operand is the empty string. Operands are measured in command-line
order; options may appear between them (CONV-10).
*AC:* `dp-strlen '' a 'hello world' 'ANSI C'` → `0\n1\n11\n6\n`; `dp-strlen -- -b -` →
`2\n1\n`. *(UR-01, UR-07)*

**FR-03: Input source.**
In line mode, if `-f` is not given or its value is `-`, the tool MUST read standard input.
Otherwise it MUST open the file named by the value of `-f` and read it as raw bytes.
*AC:* `dp-strlen < utf8.txt`, `dp-strlen -f utf8.txt`, `dp-strlen --file=utf8.txt`, and
`dp-strlen -f - < utf8.txt` write the same lengths. *(UR-02, UR-08)*

**FR-04: Lines.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is first removed. The remaining bytes are divided at each LF: every LF ends
one line, and the bytes after the last LF, if there are any, form one more line. A line does
not include its LF. If a line's last byte is CR, that one CR is removed from the line (so a CR
before an LF, or at the very end of the input, is not part of the line); every other CR is
part of the line. Every other byte, including NUL, TAB, `0x1A` followed by more data, and every byte
`0x80`–`0xFF`, is part of the line. Consequently: an empty input, or one made only of `0x1A`
bytes, has no lines; an input that ends with LF has no empty last line; each empty line in the
middle of the input is a line of length 0; and `\r` alone forms a line of length 0.
*(The division into lines is word for word the same as SRS-33 FR-03.)*
*AC:* `dp-strlen < lines.txt` → `5\n0\n11\n6\n19\n`; `dp-strlen -f crlf.txt` gives the same;
the hidden fixture `cr.txt` (`a\rb\r\r\nlast\r`) gives `4\n4\n`; `noeol.txt`
(`first\nsecond has no newline`) gives `5\n21\n`; an empty file gives no output; `\n\n\n`
gives `0\n0\n0\n`. *(UR-02, UR-06, UR-07)*

**FR-05: Characters and lengths.**
The *characters* of a byte sequence *b*[0] … *b*[*n*−1] are found by the following scan. Set
*p* = 0. While *p* < *n*: if the bytes starting at *b*[*p*] form a complete well-formed sequence
of length *k* — that is, *b*[*p*] … *b*[*p*+*k*−1] all exist in the sequence and match one row
of the table below — they are one character and *p* advances by *k*; otherwise the single byte
*b*[*p*] is one character and *p* advances by 1. The *character length* of the sequence is the
number of characters found; its *byte length* is *n*.

| Code points | Byte 1 | Byte 2 | Byte 3 | Byte 4 |
| :-- | :-- | :-- | :-- | :-- |
| U+0000..U+007F | `00`–`7F` | | | |
| U+0080..U+07FF | `C2`–`DF` | `80`–`BF` | | |
| U+0800..U+0FFF | `E0` | `A0`–`BF` | `80`–`BF` | |
| U+1000..U+CFFF | `E1`–`EC` | `80`–`BF` | `80`–`BF` | |
| U+D000..U+D7FF | `ED` | `80`–`9F` | `80`–`BF` | |
| U+E000..U+FFFF | `EE`–`EF` | `80`–`BF` | `80`–`BF` | |
| U+10000..U+3FFFF | `F0` | `90`–`BF` | `80`–`BF` | `80`–`BF` |
| U+40000..U+FFFFF | `F1`–`F3` | `80`–`BF` | `80`–`BF` | `80`–`BF` |
| U+100000..U+10FFFF | `F4` | `80`–`8F` | `80`–`BF` | `80`–`BF` |

This is the decoding rule of SRS-04 FR-06 (`dp-wc -m`), applied to one sequence. Consequences,
all normative: every valid UTF-8 code point counts 1; each byte of an invalid or truncated
sequence counts 1 (`E2 82 41` is three characters: two invalid bytes and `A`); overlong forms,
encoded surrogates, values above U+10FFFF, and lone continuation bytes count 1 per byte; a
sequence truncated by the end of the sequence counts 1 per byte present; a byte-order mark
(`EF BB BF`) is one ordinary character; NUL and every other control byte count 1. No display
width is involved: a TAB, a combining mark, and a wide East Asian character each count 1.
*(This requirement is word for word the same as SRS-27 FR-04 and SRS-33 FR-04.)*
In `dp-strlen`, each string is a separate sequence: a multibyte sequence never continues from
one line into the next (it cannot, since `0A` is never part of one). The *length* of a string
is its character length, or its byte length when `-b`, `--bytes` is given.
*AC:* `dp-strlen Zoë 日本語 🙂` → `3\n3\n1\n`; `dp-strlen -b Zoë 日本語 🙂` → `4\n9\n4\n`; the
hidden fixture `invalid.bin`, one invalid or unusual sequence per line, gives the character
lengths `3 2 3 3 4 2 2 4 3 5` and the byte lengths `3 2 3 3 4 2 2 6 9 5`. *(UR-03, UR-04, UR-05)*

**FR-06: Counting by explicit scan.**
Every length MUST be computed by one counting function that starts at the first byte of the
string, advances by one byte (byte length) or by one character as determined by FR-05
(character length), adds 1 to a counter at each step, and stops at the end of the string. The
length MUST NOT be taken from a stored length or size of a string, array, or buffer object, or
from any library function that returns a length, a character count, or decoded text; the
counting function itself determines where each character ends, from the table of FR-05. In line
mode the scan MAY be fed the input in pieces of any size, keeping its state (the count so far
and at most three bytes of an incomplete sequence) from one piece to the next; the end of a
line is the point where the scan stops. Reading the input in fixed-size blocks is permitted:
the block sizes the I/O layer returns are not string lengths.
*AC:* design review of the counting function; unit tests of NFR-06. *(UR-12)*

**FR-07: Output.**
For each string, in order (operands in command-line order; lines in input order), the tool
MUST write the decimal of its length followed by a single LF. Nothing else is written: no name,
no padding, no total. In line mode, the length of each line MUST be written and standard output
flushed as soon as the line's LF has been read, before the tool waits for more input, so the
tool can be used interactively; the length of a final line without LF is written at the end of
the input. An input with no lines produces no output.
*AC:* `dp-strlen --file=utf8.txt` → `3\n3\n1\n10\n`; `dp-strlen -f empty.txt` (hidden) → stdout
empty, exit 0. *(UR-01, UR-02)*

**FR-08: Unreadable input.**
If the file named by `-f` does not exist, cannot be opened, is a directory, or a read error
occurs, the tool MUST write `dp-strlen: <source>: <reason>` with `<reason>` from the CONV-16
table, and exit with status 1. Lengths already written for earlier lines are kept. When
standard input fails, `<source>` is `-`.
*AC:* `dp-strlen -f missing.txt` → stderr `dp-strlen: missing.txt: No such file or directory\n`,
stdout empty, exit 1; `dp-strlen -f subdir` where `subdir` is a directory →
`dp-strlen: subdir: Is a directory`. *(UR-08)*

**FR-09: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-strlen --help` matches the user manual exactly; `dp-strlen extra --help` also prints
it. *(UR-09)*

**FR-10: Version.**
`--version` MUST write `dp-strlen (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-09)*

**FR-11: Usage errors.**
Unknown options, a missing FILE, an empty FILE, and arguments supplied to options that take
none (`--bytes=…`, `--help=…`, `--version=…`) MUST be reported with the CONV-13 messages
followed by the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated
(CONV-08): `--byte` is unrecognized. If `-f` is given together with one or more STRING
operands, the tool MUST report `dp-strlen: extra operand '<first operand>'`. Errors about FILE
values and operands are detected after the whole argument list has been scanned (CONV-12).
*AC:* `dp-strlen -f lines.txt extra` → `dp-strlen: extra operand 'extra'`; `dp-strlen -f ''` →
`dp-strlen: invalid argument '' for '-f'`; `dp-strlen --file` →
`dp-strlen: option '--file' requires an argument`; `dp-strlen --bytes=1 x` →
`dp-strlen: option '--bytes' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-10, UR-12)*

**FR-12: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any file, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-10)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: locale-independent lengths and line endings | Every length MUST be computed from the byte-level rule of FR-05. Results MUST NOT depend on locale variables (`LANG`, `LC_ALL`, `LC_CTYPE`, …), the platform's default encoding or wide-character size (for example 16-bit `wchar_t` on Windows, where a UTF-16 string length would count `🙂` as 2), the console code page, terminal display widths, or text-mode I/O. The input MUST be read in binary mode on every platform, so that only FR-04 decides what a CR or a `0x1A` byte means. On Windows, operands MUST be obtained as UTF-16 and converted to UTF-8 (CONV-05), not through the ANSI code page. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Measuring a 100 MiB input MUST take under 2 s for a natively compiled build (under 30 s for an interpreted runtime) on CI hardware. Memory MUST be bounded by a constant independent of the input size and of line lengths: lines MUST NOT be held in memory; the scan keeps only its counter and at most three pending bytes (FR-06), plus the pending CR and `0x1A` bytes needed to apply FR-04 at a line end or the end of the input. Peak memory MUST stay under 16 MiB for any input (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Start-up and exit MUST take under 100 ms native (300 ms interpreted). | Measurement; code review |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including NUL bytes and lines longer than any buffer. Lengths MUST use integers of at least 64 bits. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the line divider of FR-04, the counting function of FR-06, output formatting, and I/O MUST be separate units. The counting function MUST be the only place where the table of FR-05 is applied. | Design review |
| NFR-06 | Testability | The counting function MUST be a pure, I/O-free unit covered by unit tests: the empty string, `a`, `hello world`, `ANSI C`, every consequence listed in FR-05, a NUL byte, and each multibyte sequence fed in pieces split at every possible offset, compared with a single-piece run. The line divider MUST be unit-tested with CR, CRLF, a final line without LF, an empty input, and trailing `0x1A` runs. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by `-f` or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-strlen --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-strlen: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-strlen: unrecognized option 'T'` |
| `-f` as the last argument | `dp-strlen: option requires an argument -- 'f'` |
| `--file` as the last argument | `dp-strlen: option '--file' requires an argument` |
| Empty FILE given with `-f` or `--file` | `dp-strlen: invalid argument '' for '-f'` (or `'--file'`) |
| `--bytes=…`, `--help=…`, `--version=…` | `dp-strlen: option '--bytes' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| `-f` given together with STRING operands, the first being `X` | `dp-strlen: extra operand 'X'` |

Runtime errors (exit status 1; the tool stops at the first one):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-strlen: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-strlen: F: Permission denied` |
| FILE `F` is a directory | `dp-strlen: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-strlen: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-strlen: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Standard output cannot be written (other than a broken pipe) | `dp-strlen: write error` |

There are no data diagnostics: every byte sequence has a length.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-05, FR-07 … FR-09, FR-11, FR-12 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 10 have several steps) | FR-02 … FR-05, FR-07 … FR-12, NFR-03 (a line longer than 64 KiB) |
| Unit test (written by the implementer) | FR-04 … FR-06, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | FR-06, NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-strlen hello` | FR-01, FR-07 |
| 02 | `dp-strlen '' a 'hello world' 'ANSI C'` | FR-02 (empty string, spaces), FR-07 |
| 03 | `dp-strlen Zoë 日本語 🙂` | FR-05 (characters) |
| 04 | `dp-strlen -b Zoë 日本語 🙂` | FR-05 (bytes) |
| 05 | `dp-strlen < lines.txt` | FR-01, FR-03, FR-04 (empty line, TAB) |
| 06 | `dp-strlen --file=utf8.txt` | FR-03, FR-05 |
| 07 | `dp-strlen -f crlf.txt` | FR-04 (CR before LF) |
| 08 | `dp-strlen -f missing.txt` | FR-08 |
| 09 | `dp-strlen --help` | FR-09 |
| 10 | `dp-strlen -f lines.txt extra` | FR-11, FR-12 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01, FR-02, FR-07 |
| UR-02 | FR-01, FR-03, FR-04, FR-07, CONV-26 |
| UR-03 | FR-05, NFR-02 |
| UR-04 | FR-05 |
| UR-05 | FR-05 |
| UR-06 | FR-04, NFR-02, CONV-37 |
| UR-07 | FR-02, FR-04 |
| UR-08 | FR-03, FR-08, CONV-16 |
| UR-09 | FR-09, FR-10 |
| UR-10 | FR-11, FR-12 |
| UR-11 | NFR-01, NFR-02, CONV-03, CONV-05 |
| UR-12 | FR-06, FR-11, CLI-CONV |
| UR-13 | NFR-03, NFR-07 |
