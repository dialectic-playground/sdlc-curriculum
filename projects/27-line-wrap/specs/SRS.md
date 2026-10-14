# Software Requirements Specification (SRS) — dp-wrap

| Field | Value |
| :-- | :-- |
| Document ID | SRS-27 |
| Project | `27-line-wrap` — Greedy Word-Wrapping Text Formatter |
| Product | `dp-wrap` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-27) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-wrap`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-wrap` reads words as tokens from standard input or from one file. The line length is the
first token of the input, or is given with `-w`, `--width`. The words are written to standard
output greedily, separated by single spaces, so that no line is longer than the line length.
Lengths are counted in characters under a fixed UTF-8 rule, or in bytes. A word longer than the
line length is reported on standard error and written on a line of its own. A bad line length
and unreadable files are reported with fixed messages.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Input | The byte sequence read from standard input or from the FILE operand |
| Source | The name used for the input in diagnostics: the FILE operand exactly as given, or `-` when standard input is read (with or without the operand `-`) |
| Token, line number | As defined in CONV-32: a maximal run of bytes other than `0x20`, `0x09`, `0x0A`, `0x0B`, `0x0C`, `0x0D`, and the number of LF bytes before its first byte, plus 1 |
| Header | The first token of the input when `-w` is not given; it holds the line length (FR-03) |
| Word | Every token that is not the header, in input order |
| Character, character length, byte length | As defined in FR-04 |
| Measure | The length of a word used for placement: its character length, or its byte length when `-b` is given |
| *W* | The line length, an integer 1 ≤ *W* ≤ 9223372036854775807 (2⁶³−1) |
| Output line | A maximal run of output bytes containing no LF, together with the LF that ends it |
| Over-long word | A word whose measure is greater than *W* |

### 1.4 References
- URD-27: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- SRS-04 (`projects/04-wc/specs/SRS.md`) FR-06: the decoding rule that FR-04 restates
- SRS-29 (`projects/29-strlen/specs/SRS.md`) FR-05 and SRS-33 (`projects/33-reverse/specs/SRS.md`)
  FR-04: the same character rule, word for word
- The Unicode Standard, Version 15.0, §3.9, Table 3-7 "Well-Formed UTF-8 Byte Sequences"
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §5.5 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-wrap` is a standalone executable in the tradition of `fmt` and `fold -s`. Its interfaces
are the command line, standard input or the file named by its operand, standard output,
standard error, and the exit status. It belongs to the curriculum's applications-programming
track (Projects 11–52) and adapts §5.5 of Johnsonbaugh & Kalin, *Applications Programming in
ANSI C*. It measures characters with the rule of `dp-wc -m` (Project 04), which `dp-strlen`
(Project 29) and `dp-reverse` (Project 33) also use.

### 2.2 Product functions
1. Read words as tokens until the end of the input.
2. Take the line length from the first token, or from `-w`, `--width`.
3. Measure each word in characters or in bytes.
4. Place the words greedily on lines separated by single spaces.
5. Report over-long words, and still write them; report a bad line length and unreadable files.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Character lengths MUST be computed from the byte-level rule of FR-04. Library facilities
  whose results depend on locale or platform (locale-aware classification, multibyte-conversion
  functions, display-width functions, text-mode file reading) MUST NOT determine any length
  (NFR-02).

### 2.4 Assumptions
- Standard input and standard output may each be a terminal, a pipe, or a file. Behavior is the
  same in every case.
- The input may be of any size, may contain any bytes, and need not be valid UTF-8 or end with
  LF.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §5.5 reads an integer line length, then reads words until end-of-file
and writes each one greedily: the first word of a line is written directly, a later word is
written after one space if the line, the space, and the word together fit in the line length,
and otherwise a new line is started with the word. A word longer than the line length makes
the program print `ERROR: word length exceeds line length`. `dp-wrap` keeps:

- the input order (line length first, then words) and the whitespace-delimited word reading;
- the greedy rule exactly, including its boundary: a word that brings the line to exactly the
  line length stays on it (FR-05);
- the single space between words, and the wording of the error message.

It changes the following, for the reasons given:

- **The error goes to standard error, and the word is still written.** The textbook prints the
  message into its standard output, in the middle of the formatted text, and then places the
  word as usual. `dp-wrap` writes a CONV-34 diagnostic that names the source, the line, and the
  word, still writes the word (on a line of its own, since it cannot share one), continues, and
  ends with exit status 1 (FR-07). The formatted text is therefore never interrupted, and no
  word is lost.
- **Lengths are in characters by default.** The textbook counts bytes, so `crème` is six long.
  `dp-wrap` counts characters with the rule of `dp-wc -m` (FR-04), so every curriculum tool
  measures text the same way; `-b`, `--bytes` restores byte counting.
- **The line length may be given as an option.** With `-w`, `--width` the first token is an
  ordinary word, so any text can be wrapped without editing it (FR-03).
- **The line length is validated.** The textbook reads it with a free-format numeric read and
  does not check it. `dp-wrap` requires a valid *integer* from 1 to 2⁶³−1 and reports every
  other header (FR-08); an input without a header is reported as ending early.
- **No fixed word buffer.** The textbook reads each word into a fixed-size array; a longer word
  overruns it. `dp-wrap` accepts words of any length (NFR-04), and its placement test cannot
  overflow even for the largest line length (FR-05).
- **The output ends cleanly.** The last output line ends with LF; an input without words
  produces no output at all (FR-06).
- **No prompts.** The textbook program prints no prompt, so `dp-wrap` has no `--prompt`.
- **Input sources.** Besides standard input, one FILE operand may be named (FR-01). CRLF line
  endings and a trailing Ctrl-Z marker are accepted (FR-02).

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV. Option syntax follows CONV-07 … CONV-12, diagnostics follow
CONV-13 … CONV-16, and the exit statuses are those of CONV-18. Standard input is read as
permitted by CONV-26. Of the conventions for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Applies: the input is read as tokens; diagnostics use token line numbers (FR-02). |
| CONV-33 | The header uses the *integer* grammar, further restricted to 1 … 2⁶³−1 (FR-03). |
| CONV-34 | Applies, with the standard messages `invalid integer`, `value out of range`, and `unexpected end of input` (FR-08), and one further message, `word length exceeds line length` (FR-07). |
| CONV-35 | Not applicable: no real numbers are written. |
| CONV-36 | Not applicable: the textbook program did not prompt, so there is no `--prompt`. |
| CONV-37 | Applies: the input is *text data* (FR-02). |
| CONV-38 | Not applicable: nothing is random. |

**Override of the CONV-34 consequence:** after an over-long word is reported, processing
continues; the exit status is 1 at the end (FR-07). A diagnostic about the header ends
processing as CONV-34 specifies.

**Override of CONV-04:** words are copied to standard output byte for byte, but the whitespace
between them is replaced by the single spaces and LFs of FR-06.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-wrap [-w WIDTH | --width=WIDTH] [-b | --bytes] [FILE]
dp-wrap --help
dp-wrap --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-w` | `--width` | WIDTH | the header | Use WIDTH as the line length *W*; the first token is then a word (FR-03) |
| `-b` | `--bytes` | none | off | Measure words by their byte length instead of their character length (FR-04) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

WIDTH MUST consist only of ASCII digits and denote a value from 1 to 9223372036854775807; any
other value (including the empty string, a sign, and `0`) is an invalid option value (CONV-13),
reported with the option as written (`-w` or `--width`). Option syntax (bundling such as
`-bw3`, `--`, repetition, and scan order) follows CONV-07 … CONV-12; if `-w` is repeated, the
last value is used, and only that value is validated (CONV-11).

### 3.3 Operands
At most one FILE operand. The operand `-` denotes standard input (CONV-10). Every token after
`--` is an operand, even if it begins with `-`. The operand is used and echoed exactly as given
(CONV-19).

### 3.4 Standard input
Read when no operand is given or the operand is `-` (FR-01). Read as raw bytes; no newline
translation of any kind is performed on any platform.

### 3.5 Standard output
The wrapped words (FR-05, FR-06). Nothing else. On a usage error, or when `--help` /
`--version` is handled, the output is as specified by FR-10 … FR-13 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing when the run succeeds.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Every word was placed and none was over-long (including an input without words), or `--help` / `--version` was handled |
| 1 | At least one over-long word was reported (FR-07), the header was missing or invalid (FR-08), the input could not be opened or read (FR-09), or standard output could not be written |
| 2 | Usage error (FR-12) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the files named are the public fixtures in
`tests/fixtures/`: `fox.txt` is `20\nThe quick brown fox jumps over the lazy dog\n`;
`words.txt` holds 18 words without a header, over four lines with a blank line, a run of spaces,
and a TAB; `utf8.txt` is the line `Zoë and Chloë ate crème brûlée in a café near the Straße 🙂`
and an LF, without a header; `long.txt` is
`10\nShort words, then supercalifragilistic,\nand short words again.\n`; `badwidth.txt` is
`twenty\nThe quick brown fox\n`.

**FR-01: Input source.**
If no operand is given, or the operand is `-`, the tool MUST read standard input. Otherwise it
MUST open the file named by the operand and read it as raw bytes. More than one operand is a
usage error (FR-12).
*AC:* `dp-wrap fox.txt` and `dp-wrap < fox.txt` write the same three lines. *(UR-08)*

**FR-02: Tokens.**
The input is *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the very
end of the input is ignored. The remaining input is divided into tokens (CONV-32), which are
processed in order. Line structure and the amount of whitespace between tokens have no meaning:
tokens may be separated by any mixture of space, TAB, VT, FF, CR, and LF, so CRLF input reads
exactly like LF input, and blank lines are not preserved. A `0x1A` byte that is followed by any
other byte is ordinary data and belongs to a token.
*AC:* the hidden fixture `dos.txt` (`12`, CRLF line endings, TABs, runs of spaces, a blank line,
and two trailing `0x1A` bytes) gives `Lorem ipsum\ndolor sit\namet,\nconsectetur\n`, exit 0.
*(UR-01, UR-09)*

**FR-03: Line length.**
If `-w`, `--width` is given, *W* is its value (section 3.2) and every token is a word. Otherwise
the first token is the header: it MUST be a valid *integer* (CONV-33) with a value from 1 to
9223372036854775807, and that value is *W*; every later token is a word. The header may share
its line with words (`1 a b c` is valid). The header is validated before anything is written;
if it is missing or invalid, FR-08 applies.
*AC:* `dp-wrap fox.txt` uses *W* = 20; `dp-wrap -w 10 words.txt` wraps all 18 words of
`words.txt` at 10. *(UR-03)*

**FR-04: Characters and lengths.**
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
*(This requirement is word for word the same as SRS-29 FR-05 and SRS-33 FR-04.)*
In `dp-wrap`, the *measure* of a word is its character length, or its byte length when `-b`,
`--bytes` is given. Every word has a measure of at least 1.
*AC:* `dp-wrap --width=12 utf8.txt` places `crème brûlée` (12 characters, 15 bytes) on one line;
`dp-wrap -b --width=12 utf8.txt` does not. With `-w 3`, the word `E2 82 41` (three characters)
fits on a line of its own without a diagnostic. *(UR-04, UR-05, UR-12)*

**FR-05: Greedy placement.**
Words MUST be placed one at a time, in input order, with the following rule. Let *L* be the
length of the current output line so far, in the same unit as the measure, and let *m* be the
measure of the next word.

1. If no word has been placed yet, the word starts the first output line, and *L* = *m*.
2. Otherwise, if *L* + 1 + *m* ≤ *W*, a single space (`0x20`) and the word are appended to the
   current line, and *L* = *L* + 1 + *m*.
3. Otherwise the current line is ended with an LF, the word starts a new line, and *L* = *m*.

A word whose measure brings *L* to exactly *W* stays on the current line, and the next word
then always starts a new line. An over-long word (FR-07) is placed by the same rule; since it
can never satisfy step 2, and nothing can be appended after it, it always occupies an output
line of its own. The comparison in step 2 MUST be computed without overflow for every *W* up to
2⁶³−1 and every *m*; with 64-bit signed integers, the equivalent test *m* < *W* − *L* is
suitable (*W* − *L* may be negative after an over-long word, and then the test fails, as
required).
*AC:* `dp-wrap fox.txt` → `The quick brown fox\njumps over the lazy\ndog\n` (19, 19, and 3
characters); the hidden fixture `exact.txt` (`5`, then `abcde ab cd e f g hijkl`) gives
`abcde\nab cd\ne f g\nhijkl\n`. *(UR-01, UR-02)*

**FR-06: Output format.**
Standard output MUST consist of the placed words exactly as their tokens' bytes, the single
spaces and LFs of FR-05, and, if at least one word was placed, one final LF that ends the last
output line. Nothing else is written: no leading or trailing spaces on any line, no blank
lines, no header. If the input contains no word (it is empty, or holds only whitespace, a
header, or a trailing Ctrl-Z run), standard output is empty. When every word fits (none is
over-long), every output line is at most *W* long, not counting its LF. The output depends only
on the input bytes, *W*, and `-b`; it MUST NOT depend on how the input is divided into reads.
*AC:* `dp-wrap -w 10 words.txt` →
`A greedy\nformatter\nputs as\nmany words\non each\nline as\nwill fit,\nthen\nstarts a\nnew line.\n`;
`dp-wrap -w 5` with an empty input, and the hidden fixture `header.txt` (`7\n\n`), write
nothing, exit 0. *(UR-01, UR-02)*

**FR-07: Over-long words.**
For every over-long word, the tool MUST write
`dp-wrap: <source>:<line>: word length exceeds line length '<word>'` to standard error, where
`<source>` is as defined in section 1.3, `<line>` is the word's line number (CONV-32), and
`<word>` is the word's exact bytes (CONV-34). The word is still placed (FR-05) and written in
full, and processing continues with the next word. A diagnostic is written for each over-long
word, in input order. After the end of the input, the exit status is 1 if any word was
over-long. A word whose measure equals *W* is not over-long.
*AC:* `dp-wrap long.txt` → stdout
`Short\nwords,\nthen\nsupercalifragilistic,\nand short\nwords\nagain.\n`, stderr
`dp-wrap: long.txt:2: word length exceeds line length 'supercalifragilistic,'\n`, exit 1.
*(UR-06)*

**FR-08: Missing or invalid line length.**
Without `-w`: if the input contains no token, the tool MUST write
`dp-wrap: <source>:<line>: unexpected end of input`, with `<line>` the end-of-input line number
(CONV-32, counted after the trailing Ctrl-Z run is removed). If the header is not a valid
*integer* (CONV-33), including an integer outside −2⁶³ … 2⁶³−1, the tool MUST write
`dp-wrap: <source>:<line>: invalid integer '<token>'`; if it is a valid *integer* below 1, it
MUST write `dp-wrap: <source>:<line>: value out of range '<token>'`. In each case nothing is
written to standard output, and the exit status is 1.
*AC:* `dp-wrap badwidth.txt` → stdout empty, stderr
`dp-wrap: badwidth.txt:1: invalid integer 'twenty'\n`, exit 1. A header `0` or `-3` gives
`value out of range`; `9223372036854775808` gives `invalid integer`; an empty input gives
`dp-wrap: empty.txt:1: unexpected end of input`. *(UR-07)*

**FR-09: Unreadable input.**
If the FILE operand does not exist, cannot be opened, is a directory, or a read error occurs,
the tool MUST write `dp-wrap: <source>: <reason>` with `<reason>` from the CONV-16 table, and
exit with status 1. When standard input fails, `<source>` is `-`.
*AC:* `dp-wrap missing.txt` → stderr `dp-wrap: missing.txt: No such file or directory\n`, stdout
empty, exit 1; `dp-wrap subdir` where `subdir` is a directory → `dp-wrap: subdir: Is a
directory`. *(UR-08)*

**FR-10: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No input is read.
*AC:* `dp-wrap --help` matches the user manual exactly; `dp-wrap a b --help` also prints it.
*(UR-10)*

**FR-11: Version.**
`--version` MUST write `dp-wrap (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-10)*

**FR-12: Usage errors.**
Unknown options, a missing WIDTH, an invalid WIDTH (section 3.2), and arguments supplied to
options that take none (`--bytes=…`, `--help=…`, `--version=…`) MUST be reported with the
CONV-13 messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be
abbreviated (CONV-08): `--wid` is unrecognized. A second operand MUST be reported as
`dp-wrap: extra operand '<second operand>'`. Errors about WIDTH and operands are detected after
the whole argument list has been scanned (CONV-12).
*AC:* `dp-wrap -w 0 fox.txt` → `dp-wrap: invalid argument '0' for '-w'`;
`dp-wrap fox.txt --width` → `dp-wrap: option '--width' requires an argument`;
`dp-wrap fox.txt extra` → `dp-wrap: extra operand 'extra'`; each followed by the CONV-14 line,
exit 2. *(UR-11, UR-13)*

**FR-13: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open the operand, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: locale-independent text measurement | Every measure MUST be computed from the byte-level rule of FR-04. Results MUST NOT depend on locale variables (`LANG`, `LC_ALL`, `LC_CTYPE`, …), the platform's default encoding or wide-character size (for example 16-bit `wchar_t` on Windows), the console code page, terminal display widths, or text-mode I/O. The input MUST be read in binary mode on every platform, so CR bytes reach the tokenizer (where they are whitespace) and a `0x1A` byte is never treated as end-of-file by the I/O layer. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Wrapping a 100 MiB input MUST take under 5 s for a natively compiled build (under 60 s for an interpreted runtime) on CI hardware. Memory MUST be bounded by a constant plus the length of the longest word: the tool MUST NOT hold the whole input or the current output line, so words are written as they are placed. Peak memory MUST stay under 16 MiB for inputs whose words are at most 1 MiB long (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Start-up and exit for an empty input MUST take under 100 ms native (300 ms interpreted). | Measurement; code review |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including words of any length and headers far outside the 64-bit range. Lengths MUST use integers of at least 64 bits. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability | Option parsing, the tokenizer, the character scan of FR-04, the placement rule of FR-05, and I/O MUST be separate units. The placement rule MUST be one function of (*L*, *m*, *W*) that is the only place the fit test appears. | Design review |
| NFR-06 | Testability | The character scan and the placement rule MUST be pure functions covered by unit tests, including every consequence listed in FR-04, a word whose measure equals *W*, an over-long first word, an over-long word after other words, and *W* = 2⁶³−1 with *L* close to *W*. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only the file named by its operand or standard input, MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-wrap --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-wrap: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` | `dp-wrap: unrecognized option 'T'` |
| `-w` as the last argument | `dp-wrap: option requires an argument -- 'w'` |
| `--width` as the last argument | `dp-wrap: option '--width' requires an argument` |
| Invalid WIDTH `V` given with `-w` or `--width` | `dp-wrap: invalid argument 'V' for '-w'` (or `'--width'`) |
| `--bytes=…`, `--help=…`, `--version=…` | `dp-wrap: option '--bytes' doesn't allow an argument` (or `'--help'`, `'--version'`) |
| A second operand `X` | `dp-wrap: extra operand 'X'` |

Runtime errors (exit status 1):

| Trigger | Exact message | Effect |
| :-- | :-- | :-- |
| FILE `F` does not exist | `dp-wrap: F: No such file or directory` | stops |
| FILE `F` cannot be opened or read because access is denied | `dp-wrap: F: Permission denied` | stops |
| FILE `F` is a directory | `dp-wrap: F: Is a directory` | stops |
| A component of FILE `F` is not a directory | `dp-wrap: F: Not a directory` | stops |
| Any other open or read failure of FILE `F` | `dp-wrap: F: Input/output error` | stops |
| Any of the above for standard input | the same message with `F` = `-` | stops |
| No token in source `S` (without `-w`) | `dp-wrap: S:L: unexpected end of input` (`L` = end-of-input line number) | stops; nothing written |
| Header `K` on line `L` is not a valid *integer* | `dp-wrap: S:L: invalid integer 'K'` | stops; nothing written |
| Header `K` on line `L` is a valid *integer* below 1 | `dp-wrap: S:L: value out of range 'K'` | stops; nothing written |
| Word `K` on line `L` is over-long | `dp-wrap: S:L: word length exceeds line length 'K'` | continues; word still written |
| Standard output cannot be written (other than a broken pipe) | `dp-wrap: write error` | stops |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01, FR-03 … FR-10, FR-12, FR-13 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02, 04, 05, and 07 … 10 have several steps) | FR-02 … FR-13 |
| Unit test (written by the implementer) | FR-04, FR-05, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-wrap fox.txt` | FR-01, FR-03, FR-05, FR-06 |
| 02 | `dp-wrap < fox.txt` | FR-01 |
| 03 | `dp-wrap -w 10 words.txt` | FR-02 (whitespace collapsed), FR-03, FR-05 (exact fit), FR-06 |
| 04 | `dp-wrap --width=12 utf8.txt` | FR-04 (characters), FR-05 |
| 05 | `dp-wrap -b --width=12 utf8.txt` | FR-04 (bytes), FR-05 |
| 06 | `dp-wrap long.txt` | FR-07 |
| 07 | `dp-wrap badwidth.txt` | FR-08 |
| 08 | `dp-wrap missing.txt` | FR-09 |
| 09 | `dp-wrap --help` | FR-10 |
| 10 | `dp-wrap -w 0 fox.txt` | FR-12, FR-13 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-02, FR-05, FR-06 |
| UR-02 | FR-05, FR-06 |
| UR-03 | FR-03 |
| UR-04 | FR-04, NFR-02 |
| UR-05 | FR-04 |
| UR-06 | FR-05, FR-07 |
| UR-07 | FR-08, CONV-33, CONV-34 |
| UR-08 | FR-01, FR-09, CONV-16, CONV-26 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-10, FR-11 |
| UR-11 | FR-12, FR-13 |
| UR-12 | FR-04, NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-12, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
