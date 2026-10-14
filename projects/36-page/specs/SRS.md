# Software Requirements Specification (SRS) — dp-page

| Field | Value |
| :-- | :-- |
| Document ID | SRS-36 |
| Project | `36-page` — Stream Text Pagination Utility |
| Product | `dp-page` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-36) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-page`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-page` reads the concatenation of its inputs (standard input or the files named by its
operands) and copies it to standard output in pages. Each page consists of a header line, a
blank line, up to *L* input lines copied byte for byte (*L* = 52 by default), and a form feed.
It reports unreadable files with fixed messages and continues with the remaining operands.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| FF | The form-feed byte, `0x0C` |
| Stream | The concatenation, in operand order, of the bytes of every input that was opened and read successfully (FR-01) |
| Line | A maximal sequence of stream bytes that ends with an LF and contains no other LF (a *terminated line*), or the non-empty sequence of bytes after the last LF of the stream, or of the whole stream if it contains no LF (the *final unterminated line*). An empty stream has no lines. Every byte other than LF, including CR, NUL, FF, and `0x1A`, is an ordinary data byte |
| Page length *L* | The number of lines per page: 52, or the value of `-l`, `--lines` (FR-07) |
| Header | The bytes `Page     <N>` + LF + LF, where `<N>` is the page number (FR-04) |
| Decimal | The plain ASCII decimal representation of a positive integer: no sign, no leading zeros, no digit grouping (CONV-06) |

### 1.4 References
- URD-36: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §7.2 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-page` is a standalone executable in the tradition of the POSIX `pr` utility, much
simplified. Its interfaces are the command line, standard input and the files named by its
operands, standard output, standard error, and the exit status. It belongs to the curriculum's
applications-programming track (Projects 11–52) and adapts §7.2 of Johnsonbaugh & Kalin,
*Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read the inputs as one byte stream and divide it into lines.
2. Group the lines into pages of *L* lines; the last page may be shorter.
3. Write each page as a numbered header, a blank line, its lines copied byte for byte, and a
   form feed.
4. Write nothing for an empty stream, and never write a page without lines.
5. Report unreadable inputs and continue with the rest.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Input MUST be read and output written as raw bytes. Platform "text mode" I/O, newline
  translation, and character decoding MUST NOT be applied (NFR-02).

### 2.4 Assumptions
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.
- Inputs may be of any size, may contain any byte values, need not be valid UTF-8, and need
  not end with LF. Lines may be of any length.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §7.2 copies its standard input to its standard output in pages of
52 lines. Each page begins with `Page`, five spaces, and the page number, followed by a blank
line, and ends with a form feed; no page is started when the input is exhausted at a page
boundary. `dp-page` keeps:

- the page length of 52 lines, the header text and spacing (`Page`, five spaces, the number),
  the blank line after the header, and the form feed after each page;
- the absence of any separator after the form feed: the next page's header follows it
  directly, and the output ends with the last form feed;
- the rule that an input exhausted at the start of a page produces no further page, so an
  empty input produces no output and an input of an exact multiple of 52 lines produces no
  trailing empty page.

It changes or settles the following, for the reasons given:

- **The last line without a newline is copied as it is.** The section's description does not
  say what happens to a final line that lacks a newline. `dp-page` copies it without adding
  one and writes the form feed directly after its last byte (FR-05). Adding a newline would
  change the text, and with this rule the input can always be recovered exactly by deleting
  the headers and form feeds (FR-06).
- **Byte transparency.** Every byte other than LF is data (CONV-04): CR bytes are copied, so a
  CRLF file keeps its line endings, and NUL, form feed, and Ctrl-Z bytes inside the input are
  copied too. A form feed already present in the input does not start a new page and does not
  count as a line break.
- **Header spacing is fixed text.** The header is `Page`, exactly five spaces, and the page
  number, whatever the number of digits: `Page     9`, `Page     10`, `Page     100` (FR-04).
  The number is not padded to a column width.
- **Input sources.** Besides standard input, any number of FILE operands may be named; they
  are paginated as one continuous stream, as if concatenated first (FR-01). This keeps the
  tool usable in the same way as `dp-cat` (Project 02).
- **Page length option.** `-l`, `--lines` sets the number of lines per page for other paper
  sizes (FR-07). The default stays 52, so the default output is the textbook's.
- **No prompts.** The textbook program is a filter and shows no prompts, so `dp-page` has no
  `--prompt` option.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. Input bytes are copied as
required by CONV-04. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, processing continues after a failed operand (CONV-17), and the exit
statuses are those of CONV-18. Standard input is read as permitted by CONV-26.
Of section 10, none of CONV-32 … CONV-38 applies: the input is not read as tokens and contains
no numeric data (CONV-32 … CONV-34), no real number is written (CONV-35), there are no prompts
(CONV-36), and nothing is random (CONV-38). In particular the input is **not** *text data* in
the sense of CONV-37: a trailing run of `0x1A` bytes is copied like any other data, because
`dp-page` is a byte-transparent filter (FR-02). The option value of `-l`, `--lines` is
validated as a CONV-13 option value, not as data.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-page [-l N | --lines=N] [FILE]...
dp-page --help
dp-page --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-l` | `--lines` | N | 52 | Put *N* lines on each page (FR-07) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (attached and separate values such as `-l3`, `-l 3`, `--lines=3`,
`--lines 3`, `--`, repetition, and scan order) follows CONV-07 … CONV-12. If `-l` /
`--lines` is given more than once, the last occurrence wins (CONV-11); only that value is
validated.

### 3.3 Operands
Zero or more FILE operands, processed in the order given. The operand `-` denotes standard
input (CONV-10). Every token after `--` is an operand, even if it begins with `-`. Operands are
used and echoed exactly as given (CONV-19).

### 3.4 Standard input
Read when no operand is given, and for each `-` operand. Read as raw bytes; no newline
translation of any kind is performed on any platform. Standard input is read until its end;
a later `-` operand contributes whatever bytes standard input still delivers, which for a file
or a pipe is nothing.

### 3.5 Standard output
The pages (FR-03 … FR-05). On a usage error, or when `--help` / `--version` is handled, the
output is as specified by FR-09 … FR-12 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing when every input is read successfully.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every input was read and paginated (including an empty stream), or `--help` / `--version` was handled |
| 1 | At least one input could not be opened or read (FR-08), or standard output could not be written |
| 2 | Usage error (FR-11) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, `\r` CR, `\f` FF, and the files are the public
fixtures in `tests/fixtures/`: `linesK.txt` (K = 50, 53, 104) consists of the K lines
`line 1\n` … `line K\n`; `poem.txt` is 208 bytes of ASCII text in seven LF-terminated lines,
the fifth of them empty; `noeol.txt` is `one\r\ntwo\r\nthree` (15 bytes, no final LF).

**FR-01: Inputs and the stream.**
If no operand is given, the tool MUST read standard input as if the single operand `-` had
been given. Otherwise each operand is one input, opened and read as raw bytes from its first
byte to its end, in command-line order. The stream is the concatenation of the bytes of all
inputs that were read, with nothing inserted between them: the inputs are paginated as one
continuous text, with continuous page numbers, and a file that does not end with LF continues
its last line into the first line of the next input. Inputs that cannot be opened or read
contribute no bytes (FR-08); bytes already copied from an input that fails while being read
remain part of the stream.
*AC:* `dp-page < lines50.txt` and `dp-page lines50.txt` write the same 404 bytes;
`dp-page --lines=4 poem.txt - noeol.txt < lines50.txt` paginates the 60 lines of the three
inputs as 15 pages of 4 lines, page 15 holding `line 50\n`, `one\r\n`, `two\r\n`, and `three`.
*(UR-06)*

**FR-02: Lines.**
The stream MUST be divided into lines as defined in section 1.3. Only LF ends a line. Every
other byte is copied unchanged and has no meaning to the tool: CR is not a line terminator
(CONV-04), a FF in the input neither ends a line nor starts a page, NUL is data, and `0x1A`
bytes are copied wherever they occur, including at the very end of the input (CONV-37 does not
apply). An empty line (a lone LF) is a line and counts toward the page length.
*AC:* `dp-page noeol.txt` → stdout `Page     1\n\none\r\ntwo\r\nthree\f` (28 bytes). A file
`x\0y\fz\n` + `0x1A` (7 bytes) → `Page     1\n\nx\0y\fz\n` + `0x1A` + `\f`; the input FF does
not start a page and the final `0x1A` byte is a one-byte line. *(UR-05)*

**FR-03: Page structure.**
The lines of the stream MUST be grouped, in order, into pages: page 1 holds lines 1 … *L*,
page 2 holds lines *L*+1 … 2*L*, and so on; the last page holds the remaining 1 … *L* lines.
Each page MUST be written as its header (FR-04), followed by its lines copied byte for byte,
followed by one FF. Nothing else is written: no byte follows the FF of a page except the header
of the next page, and the output ends with the FF of the last page.
*AC:* `dp-page lines53.txt` → `Page     1\n\nline 1\n` … `line 52\n\fPage     2\n\nline 53\n\f`
(441 bytes), exit 0. *(UR-01, UR-02, UR-03)*

**FR-04: Header.**
The header of page *n* (*n* = 1, 2, …) MUST be exactly the bytes `Page`, five spaces (`0x20`),
the decimal of *n*, LF, and LF: a header line followed by an empty line. The number of spaces
is always five, whatever the number of digits of *n*; there are no leading or trailing spaces.
*AC:* page 1 begins `Page     1\n\n`; `dp-page -l 5 lines53.txt` writes eleven pages whose
headers include `\fPage     9\n\n`, `\fPage     10\n\n`, and `\fPage     11\n\n`. *(UR-02)*

**FR-05: End of the stream.**
The number of pages MUST be ⌈*k* / *L*⌉ for a stream of *k* lines. In particular:

- an empty stream (no bytes at all, for example an empty input or only empty files) MUST
  produce no output;
- when *k* is an exact multiple of *L*, the last page is full and is followed by nothing: no
  header of an empty page and no extra FF;
- when the last page holds fewer than *L* lines, it is written with the lines it has and
  closed with its FF;
- when the stream ends with a final unterminated line, that line is copied exactly as read,
  **without** adding an LF, and the page's FF follows its last byte directly. This holds also
  when that line is the *L*-th line of its page.

A header MUST be written only when the first byte of the page's first line exists; the tool
therefore never writes a header that is not followed by at least one line.
*AC:* `dp-page` with empty standard input → stdout and stderr empty, exit 0;
`dp-page lines104.txt` → exactly two pages, two headers and two FF bytes (854 bytes), the
output ending `line 104\n\f`; `dp-page < lines50.txt` → one page of 50 lines (404 bytes);
`dp-page -l 3 noeol.txt` → `Page     1\n\none\r\ntwo\r\nthree\f`, and `dp-page -l2 noeol.txt`
→ `Page     1\n\none\r\ntwo\r\n\fPage     2\n\nthree\f`. *(UR-04, UR-05)*

**FR-06: Byte transparency.**
For every stream, deleting from the output each header and each FF that the tool inserted
MUST yield the stream exactly, byte for byte. The tool MUST NOT change, add, or remove any
input byte, whatever its value, and MUST NOT expand tabs, trim spaces, or translate line
endings.
*AC:* for every public test that exits 0, removing the inserted headers and FF bytes from
stdout gives the concatenated inputs. *(UR-05)*

**FR-07: Page length.**
`-l N`, `--lines=N` sets the page length *L* to *N*. *N* MUST consist only of ASCII digits
(leading zeros are allowed) and its value MUST lie in 1 … 9223372036854775807; otherwise the
value is invalid and is reported as
`dp-page: invalid argument '<value>' for '<option>'` (CONV-13), where `<option>` is `-l` or
`--lines` as written. An empty value, a sign (`+3`, `-3`), spaces, and 0 are invalid. The
check is made after the whole argument list has been scanned (CONV-12) and only for the last
occurrence (CONV-11). Without the option, *L* = 52.
*AC:* `dp-page -l 3 poem.txt` → three pages of 3, 3, and 1 lines (247 bytes), the second page
holding the empty line; `dp-page -l 0 poem.txt` → `dp-page: invalid argument '0' for '-l'`
and the CONV-14 line, stdout empty, exit 2; `dp-page --lines=52 -l002 poem.txt` uses *L* = 2;
`dp-page --lines=9223372036854775807 poem.txt` writes one page. *(UR-07)*

**FR-08: Unreadable inputs.**
If a FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-page: <operand>: <reason>` with `<reason>` from the CONV-16 table, and
continue with the next operand (CONV-17). When standard input fails, `<operand>` is `-`. The
failed input contributes nothing further to the stream; output already written is kept, and
the page that is open (if any) stays open for the bytes of the following inputs. The exit
status is then 1.
*AC:* `dp-page missing.txt noeol.txt` → stderr
`dp-page: missing.txt: No such file or directory\n`, stdout as for `dp-page noeol.txt`,
exit 1; `dp-page subdir noeol.txt` where `subdir` is a directory →
`dp-page: subdir: Is a directory`, exit 1. *(UR-08)*

**FR-09: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-page --help` matches the user manual exactly; `dp-page extra --help` and
`dp-page --lines 0 --help` also print it. *(UR-09)*

**FR-10: Version.**
`--version` MUST write `dp-page (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-09)*

**FR-11: Usage errors.**
Unknown options, a missing value for `-l` / `--lines`, arguments supplied to options that
take none (`--help=…`, `--version=…`), and invalid page lengths (FR-07) MUST be reported with
the CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT
be abbreviated (CONV-08): `--line` is unrecognized.
*AC:* `dp-page -x --help` → `dp-page: invalid option -- 'x'`; `dp-page poem.txt -l` →
`dp-page: option requires an argument -- 'l'`; `dp-page --lines=` →
`dp-page: invalid argument '' for '--lines'`; `dp-page --help=x` →
`dp-page: option '--help' doesn't allow an argument`; each followed by the CONV-14 line,
exit 2. *(UR-10, UR-12)*

**FR-12: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any operand, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case; `dp-page -l 9223372036854775808 poem.txt` writes
nothing to stdout. *(UR-10)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line the tool generates (headers, help, diagnostics) MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: control characters and binary transparency | Inputs MUST be opened in binary mode on every platform, so that CR bytes reach the tool unchanged and a `0x1A` byte is never treated as end-of-file by the I/O layer (as Windows text-mode reads do). Standard output MUST be in binary mode, so that LF is not expanded to CRLF and the FF byte `0x0C` is written as exactly one byte; no console or terminal translation may be relied on. The form feed MUST be written as the byte `0x0C`, never as a terminal escape sequence. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Paginating a 100 MiB input MUST take under 2 s for a natively compiled build (under 20 s for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Memory MUST NOT grow with the size of the input or the length of a line: lines are copied in bounded chunks and never held whole. Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including lines of any length and page lengths up to 9223372036854775807 (no counter may overflow). A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, input opening and reading, the pagination state machine, header formatting, and output MUST be separate units. The pagination state (page number, lines on the current page, whether a page is open) MUST be held in one unit that receives bytes and does not know where they came from. | Design review |
| NFR-06 | Testability | The pagination unit MUST be a deterministic function of the byte stream and *L*, unit-tested with each acceptance case of FR-02 … FR-05 and with the stream split into reads at every byte position (the output MUST NOT depend on the split), including splits between a CR and its LF and between the last LF of a page and the next byte. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the files named by its operands or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-page --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-page: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-page: unrecognized option 'T'` |
| `-l` as the last argument | `dp-page: option requires an argument -- 'l'` |
| `--lines` as the last argument | `dp-page: option '--lines' requires an argument` |
| `--help=…`, `--version=…` | `dp-page: option '--help' doesn't allow an argument` (or `'--version'`) |
| Invalid page length `V` given with `-l` or `--lines` (FR-07) | `dp-page: invalid argument 'V' for '-l'` (or `'--lines'`) |

`dp-page` accepts any number of operands, so `missing operand` and `extra operand` never occur.

Runtime errors (exit status 1; the tool continues with the next operand):

| Trigger | Exact message |
| :-- | :-- |
| FILE `F` does not exist | `dp-page: F: No such file or directory` |
| FILE `F` cannot be opened or read because access is denied | `dp-page: F: Permission denied` |
| FILE `F` is a directory | `dp-page: F: Is a directory` |
| A component of FILE `F` is not a directory | `dp-page: F: Not a directory` |
| Any other open or read failure of FILE `F` | `dp-page: F: Input/output error` |
| Any of the above for standard input | the same message with `F` = `-` |
| Standard output cannot be written (other than a broken pipe) | `dp-page: write error` (the tool stops) |

There are no data diagnostics: every byte sequence is a valid input.

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-09, FR-11, FR-12 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 05 … 10 have several steps) | FR-01 … FR-12 |
| Unit test (written by the implementer) | FR-02 … FR-06, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-page < lines50.txt` | FR-01, FR-03, FR-04, FR-05 (partial last page) |
| 02 | `dp-page lines53.txt` | FR-03 (52 + 1 lines), FR-04 |
| 03 | `dp-page lines104.txt` | FR-05 (exact multiple: no empty page) |
| 04 | `dp-page` (empty standard input) | FR-05 (empty stream) |
| 05 | `dp-page -l 3 poem.txt` | FR-02 (empty line), FR-07 |
| 06 | `dp-page noeol.txt` | FR-02 (CR is data), FR-05 (no LF added), FR-06 |
| 07 | `dp-page --lines=4 poem.txt - noeol.txt < lines50.txt` | FR-01 (one stream, continuous numbers), FR-04 (two-digit pages), FR-07 |
| 08 | `dp-page missing.txt noeol.txt` | FR-08 (CONV-17) |
| 09 | `dp-page --help` | FR-09 |
| 10 | `dp-page -l 0 poem.txt` | FR-07, FR-11, FR-12 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-03, FR-05 |
| UR-02 | FR-03, FR-04 |
| UR-03 | FR-03 |
| UR-04 | FR-05 |
| UR-05 | FR-02, FR-05, FR-06, CONV-04 |
| UR-06 | FR-01, CONV-26 |
| UR-07 | FR-07 |
| UR-08 | FR-08, CONV-16, CONV-17 |
| UR-09 | FR-09, FR-10 |
| UR-10 | FR-11, FR-12 |
| UR-11 | NFR-01, NFR-02, CONV-03 |
| UR-12 | FR-11, CLI-CONV |
| UR-13 | NFR-03, NFR-07 |
