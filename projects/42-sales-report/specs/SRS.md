# Software Requirements Specification (SRS) — dp-sales

| Field | Value |
| :-- | :-- |
| Document ID | SRS-42 |
| Project | `42-sales-report` — Enterprise Sales Reporting & Relational Data Integration |
| Product | `dp-sales` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-42) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-sales`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-sales` reads an accounts file (by default `sales.dat`) and a salesperson file (by default
`sper.dat`), each with one record per line. It validates every record, rejects duplicate
account ids, and resolves every account id listed for a salesperson to its account. Only when
both files are valid does it write the sales report to standard output: the salespeople in
byte-wise order of name, each with the accounts listed for them, in the exact layout of the
textbook's sample report `sales.rpt`. Amounts are exact decimals with at most two decimals.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| ACCOUNTS | The value of `-a`/`--accounts`, or `sales.dat` if neither is given |
| SALESPEOPLE | The value of `-s`/`--salespeople`, or `sper.dat` if neither is given |
| Input | The byte sequence read from a file, or from standard input when its name is `-` |
| Source | The name used for an input in diagnostics: ACCOUNTS or SALESPEOPLE exactly as given (so `-` for standard input) |
| Whitespace | The bytes `0x20` (space), `0x09` (TAB), `0x0B` (VT), `0x0C` (FF), and `0x0D` (CR): the CONV-32 set without LF, which ends lines |
| Line | A maximal byte sequence not containing LF, after CONV-37 has been applied: the input is split at every LF; the part after the last LF is a line too (it is empty when the input ends with LF, and then ignored as a blank line) |
| Line number | 1 plus the number of LF bytes before the line (CONV-32) |
| Field | A maximal run of non-whitespace bytes within a line. Fields are compared and echoed as bytes; no decoding is applied |
| Blank line | A line with no field. Blank lines are ignored |
| Record | A line with at least one field |
| Id | The value of a field that is a valid *integer* (CONV-33) with 0 ≤ value ≤ 9223372036854775807 (2⁶³−1) |
| Amount | The value of a field that matches the *amount* grammar `[0-9]+(\.[0-9]{1,2})?` (ASCII digits; no sign, no exponent, no grouping, at most two decimals) and whose exact decimal value, in hundredths, is at most 9223372036854775807, that is, at most 92233720368547758.07 |
| Text | Any field, used as it is: an account name, a salesperson name, a coach, or a region |
| Decimal | The plain ASCII decimal representation of a non-negative integer: no sign, no leading zeros (zero is `0`), no digit grouping (CONV-06) |
| MONEY(x) | For an amount *x* = *h* / 100 with *h* a whole number of hundredths: the decimal of ⌊*h* / 100⌋, a `.`, and the two digits of *h* mod 100 (with a leading `0` if below 10). `2762890.5` → `2762890.50`; `007` → `7.00`; `0` → `0.00`. MONEY(*x*) is the same string as `FIX(x, 2)` (CONV-35) of the exact decimal value |

### 1.4 References
- URD-42: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`, in particular section 10 (CONV-32 … CONV-38)
- User manual: `specs/user-manual.md` (contains the normative help text)
- `tests/fixtures/sales.rpt`: the textbook's sample report, which FR-08 reproduces exactly
- R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C*, 3rd ed., Prentice Hall,
  1996, §9.7 (informative; see §2.5)

## 2. Overall description

### 2.1 Product perspective
`dp-sales` is a standalone executable. Its interfaces are the command line, the two input files
(one of which may be standard input), standard output, standard error, and the exit status. It
belongs to the curriculum's applications-programming track (Projects 11–52) and adapts §9.7 of
Johnsonbaugh & Kalin, *Applications Programming in ANSI C*.

### 2.2 Product functions
1. Read and validate the accounts file (`sales.dat` by default); reject duplicate ids.
2. Read and validate the salesperson file (`sper.dat` by default); resolve every listed account
   id to its account, rejecting unknown ids.
3. Order the salespeople by name.
4. Write the sales report to standard output, only after both files have been validated.
5. Report unreadable files and invalid records.
6. Display help and version information; detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.
- Amounts MUST be held and printed exactly (FR-04). Binary floating point MUST NOT be used to
  hold, convert, or round them.

### 2.4 Assumptions
- The current working directory is where the default files `sales.dat` and `sper.dat` are
  looked for; relative paths are relative to it.
- Names, coaches, and regions contain no whitespace (the textbook writes `AceRecords`, not
  `Ace Records`); they may contain any other bytes, which are copied to the report unchanged.
- Nothing writes the input files while the tool runs.

### 2.5 Relationship to the textbook program (informative)
The textbook program of §9.7 reads the accounts file `sales.dat` (id, name, actual sales,
projected sales) and the salesperson file `sper.dat` (name, coach, region, salary, bonus, `#`,
account ids), sorts the accounts by id with a quicksort that takes a comparison function, links
each salesperson to their accounts by binary search, sorts the salespeople by name with the
same quicksort, and prints the report of which `sales.rpt` is a sample. `dp-sales` keeps:

- the two record formats and the field order, including the `#` that introduces the account
  ids, and the file names `sales.dat` and `sper.dat` as defaults in the current directory;
- the report exactly as `sales.rpt` shows it: the heading, the indentation of 8 and 16 spaces,
  the labels and their alignment, the order Projected before Actual (although the file has
  actual sales first), the count line `N Account(s): ` with its trailing space, and every blank
  line, including the one that ends the report;
- money with two decimals, the salespeople in order of name, and the accounts of a salesperson
  in the order listed; the limits of 100 accounts and 100 salespeople;
- the design: accounts sorted by id and resolved by binary search, and one sort procedure
  parameterized by a comparison function, used for both sorts (NFR-05).

It changes the following, for the reasons given:

- **Exact decimal money.** The textbook holds amounts in binary floating point and prints them
  with `%.2f`. For the sample data that gives the right digits, but not in general: a value
  that is not exact in binary can round the wrong way when printed, and above about 2⁵³
  hundredths whole cents are lost. `dp-sales` reads amounts as exact decimals with at most two
  decimals and prints them exactly (FR-04), so the report always shows the digits in the file.
- **Validation before output** (FR-09). The textbook does not check its input; a malformed
  field, a duplicate id, or an id with no account leads to garbage or a crash. `dp-sales`
  reports the first problem with its file and line number (FR-10) and prints no report, so a
  report is never partial or silently wrong.
- **Line-oriented records** (FR-02). Each record is one line, so a salesperson's id list ends
  at the end of the line, and blank lines are ignored. CRLF line endings, tabs, and a trailing
  Ctrl-Z marker are accepted.
- **A stated order.** Names are compared byte by byte (FR-07), which does not depend on the
  locale; salespeople with equal names keep the order of the file, which a plain quicksort
  does not guarantee.
- **File names can be overridden**, and either file can be standard input (FR-01).
- **No prompts.** The textbook program is not interactive, so `dp-sales` has no `--prompt`.

The textbook did not supply its input files. The fixtures `sales.dat` and `sper.dat` were
written for this project from the accounts and salespeople in `sales.rpt`; public test 01 shows
that `dp-sales` reproduces `sales.rpt` from them byte for byte.

### 2.6 Relationship to CLI-CONV
This SRS incorporates CLI-CONV in full and makes **no overrides**. Option syntax follows
CONV-07 … CONV-12, diagnostics CONV-13 … CONV-16, and exit statuses CONV-18. Of the conventions
for Projects 11–52:

| Convention | Use in this SRS |
| :-- | :-- |
| CONV-32 | Both inputs are line-oriented (FR-02); fields are separated by the CONV-32 whitespace bytes other than LF, and line numbers follow CONV-32. |
| CONV-33 | Ids use the *integer* grammar, restricted to 0 … 2⁶³−1. Amounts use the *amount* grammar defined in section 1.3 instead of the *real* grammar, because they are exact decimals. |
| CONV-34 | All data errors use its format, with the standard messages `invalid integer` and `value out of range` and further messages of this SRS (FR-10). Because of FR-09, no report has been written when one is reported. |
| CONV-35 | MONEY(*x*) equals `FIX(x, 2)` of the exact decimal value; no binary floating-point value is ever formatted. |
| CONV-36 | Not applicable: the tool has no prompts (it does not accept `-p`). |
| CONV-37 | Both inputs are *text data*. |
| CONV-38 | Not applicable: nothing is random. |

Standard input is read only when ACCOUNTS or SALESPEOPLE is `-` (CONV-26). Text fields are
copied from the input to the report byte for byte (CONV-04).

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-sales [-a FILE | --accounts=FILE] [-s FILE | --salespeople=FILE]
dp-sales --help
dp-sales --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-a` | `--accounts` | FILE (required) | `sales.dat` | Read the accounts from FILE; `-` is standard input (FR-01) |
| `-s` | `--salespeople` | FILE (required) | `sper.dat` | Read the salespeople from FILE; `-` is standard input (FR-01) |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (`-aFILE`, `--accounts FILE`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. If an option is repeated, the last occurrence wins (CONV-11). FILE may begin with `-`
when it is attached (`--accounts=-x`, `-a-x`) or supplied as the next token (`-a -x`).

### 3.3 Operands
`dp-sales` accepts **no operands**. File names are given with `-a` and `-s`.

### 3.4 Standard input
Read only when ACCOUNTS or SALESPEOPLE is `-`; never for both (FR-14). Read as raw bytes; no
newline translation of any kind is performed on any platform.

### 3.5 Standard output
The report (FR-08) when both files are valid; otherwise nothing. On a usage error, or when
`--help` / `--version` is handled, the output is as specified by FR-12 … FR-15 instead.

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The report was written, or `--help` / `--version` was handled |
| 1 | A file could not be read (FR-11), a record was invalid (FR-10), or standard output could not be written |
| 2 | Usage error (FR-14) |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.
In acceptance criteria, `\n` denotes LF, and the following are public fixture files in
`tests/fixtures/`. `sales.rpt` is the textbook's sample report. `sales.dat` holds, one per line,
the accounts `812 TacosAndThings 1412987.50 2345000.00`, `245 PetRocks 95679.10 8130000.00`,
`127 AceRecords 2762890.50 6780000.00`, and `943 BusterBurger 1432567.88 4650000.00`.
`sper.dat` holds the lines `Johnsonbaugh Epp IL 98450.00 29324.18 # 127 812` and
`Chessare Cruz TX 102300.00 15671.90 # 245 943`. `team.dat` is a salesperson file for the same
accounts with six salespeople (two named `Chessare`, one named `deGroot`, one with no accounts,
account 812 listed for two salespeople, ids out of order, and the id `0127`). `mixed.dat` holds
the four accounts of `sales.dat` and one more, in another order, with CRLF line endings, tabs,
runs of spaces, blank lines, leading zeros, amounts with one or no decimals, and a final `0x1A`
byte instead of a last LF. `unknown.dat` is `sper.dat` with the id `999` added to line 2;
`dup.dat` is `sales.dat` with line 3 replaced by `0812 Other 1.00 2.00`; `bad-amount.dat` is
`sales.dat` with the actual sales of line 4 written `1432567.888`.

**FR-01: Inputs.**
The tool MUST read the accounts input from the file ACCOUNTS, or from standard input if
ACCOUNTS is `-`, and the salesperson input from the file SALESPEOPLE, or from standard input if
SALESPEOPLE is `-`; each to its end, as raw bytes. Without the options, ACCOUNTS is `sales.dat`
and SALESPEOPLE is `sper.dat`. Paths are relative to the current directory unless absolute.
The tool MUST proceed in this order and stop at the first failure: read the accounts input
(FR-11); validate it (FR-03); read the salesperson input (FR-11); validate it (FR-05); write the
report (FR-08). So the salesperson file is not even opened when the accounts file is
unreadable or invalid.
*AC:* `dp-sales` → stdout identical to `sales.rpt`, stderr empty, exit 0;
`dp-sales --accounts=- < sales.dat` → the same. *(UR-01, UR-02, UR-03)*

**FR-02: Lines and fields.**
Both inputs are *text data* (CONV-37): a run of one or more `0x1A` bytes that extends to the
very end of an input is ignored. Each input is then divided into lines and each line into
fields (section 1.3). Blank lines are ignored; every other line is one record. CR, TAB, VT, FF,
and space separate fields, so CRLF input reads exactly like LF input, and fields may be
separated by any run of them. The line number of a record is used in every diagnostic about
it.
*AC:* `dp-sales -a mixed.dat` → stdout identical to `sales.rpt` (the extra account is not
listed for anyone and so does not appear), exit 0. *(UR-09)*

**FR-03: Accounts file.**
Each record of the accounts input MUST consist of exactly four fields: ID, NAME, ACTUAL, and
PROJECTED, where ID is an id, NAME is text, and ACTUAL (the actual sales) and PROJECTED (the
projected sales) are amounts. Records are checked in input order, and the first problem found
is reported (FR-10). For each record, in this order:

1. If it would be the 101st account, report `too many accounts (limit 100)`, before its fields
   are checked.
2. The fields are checked from left to right: ID by the *integer* grammar and then the range of
   an id; NAME needs no check; ACTUAL and PROJECTED by FR-04. When the record ends where a
   required field would follow, report `incomplete record`.
3. A fifth field is reported as `unexpected field '<field>'`.
4. If an earlier record of the accounts input has an ID of the same *value*, report
   `duplicate account id '<field>'`, where `<field>` is this record's ID field as written.

Account names need not be unique. The accounts input may contain no record.
*AC:* `dp-sales -a dup.dat` → stdout empty, stderr
`dp-sales: dup.dat:3: duplicate account id '0812'\n`, exit 1. A record `127 AceRecords
2762890.50` gives `incomplete record`; one with a fifth field `extra` gives
`unexpected field 'extra'`; an id `-5` gives `value out of range '-5'`, and
`9223372036854775808` gives `invalid integer '9223372036854775808'`; a file of 100 accounts is
accepted, and in one of 101 accounts the 101st, on line 101, gives
`too many accounts (limit 100)`. *(UR-06, UR-07)*

**FR-04: Amounts.**
A field that must be an amount (ACTUAL, PROJECTED, SALARY, BONUS) MUST match the *amount*
grammar of section 1.3; otherwise the tool reports `invalid amount '<field>'`. If it matches but
its value exceeds 92233720368547758.07, the tool reports `value out of range '<field>'`. The
value is the exact decimal value of the field, which is a whole number of hundredths; leading
zeros are allowed. Amounts are printed as MONEY(*x*) (section 1.3), from that exact value, never
through binary floating point.
*AC:* `dp-sales -a bad-amount.dat` → stdout empty, stderr
`dp-sales: bad-amount.dat:4: invalid amount '1432567.888'\n`, exit 1. `+5` gives
`invalid amount '+5'`; `92233720368547758.07` is printed as `92233720368547758.07`;
`92233720368547758.08` gives `value out of range`; `60000.5` is printed `60000.50`, `75000`
`75000.00`, `01432567.88` `1432567.88`, and `0` `0.00`. *(UR-05, UR-06)*

**FR-05: Salesperson file.**
Each record of the salesperson input MUST consist of NAME, COACH, REGION, SALARY, BONUS, the
field `#` (the single byte `0x23`), and zero or more account ids, where NAME, COACH, and REGION
are text and SALARY and BONUS are amounts. Records are checked in input order, and the first
problem found is reported (FR-10). For each record, in this order:

1. If it would be the 101st salesperson, report `too many salespeople (limit 100)`, before its
   fields are checked.
2. The fields are checked from left to right: NAME, COACH, and REGION need no check; SALARY and
   BONUS by FR-04. When the record ends before the sixth field, report `incomplete record`.
3. If the sixth field is not `#`, report `expected '#' but found '<field>'`.
4. Each further field, from left to right, MUST be an id (`invalid integer '<field>'` or
   `value out of range '<field>'` otherwise); MUST be the id of an account of the accounts
   input (`unknown account '<field>'` otherwise); and MUST NOT have the same value as an
   earlier id of the same record (`account listed twice '<field>'` otherwise).

An id is matched by its value, so `0127` denotes the account 127. One account may be listed for
several salespeople. Salesperson names need not be unique. The salesperson input may contain no
record.
*AC:* `dp-sales -s unknown.dat` → stdout empty, stderr
`dp-sales: unknown.dat:2: unknown account '999'\n`, exit 1. A record without the `#`, whose
sixth field is `245`, gives `expected '#' but found '245'`; the ids `245 943 0245` give
`account listed twice '0245'`; a record that ends after SALARY gives `incomplete record`.
*(UR-06, UR-07)*

**FR-06: Linking.**
Each id of a salesperson record denotes the account of the accounts input whose ID has the same
value; FR-03 guarantees that there is at most one. The report shows that account's NAME, ID,
PROJECTED, and ACTUAL.
*AC:* in test 01, Chessare's ids 245 and 943 show PetRocks and BusterBurger with their amounts.
*(UR-04)*

**FR-07: Order.**
The salespeople MUST appear in ascending order of NAME, compared byte by byte as unsigned
values; a name that is a prefix of another comes first. The comparison MUST NOT depend on the
locale: `Zimmer` precedes `deGroot`, because `Z` (`0x5A`) is less than `d` (`0x64`).
Salespeople with equal names MUST appear in the order of their records in the salesperson
input. The accounts of a salesperson MUST appear in the order of their ids in the record, not
sorted.
*AC:* `dp-sales -s team.dat` → the salespeople `Adams`, `Chessare` (coach Cruz, from line 4),
`Chessare` (coach Lee, from line 6), `Johnsonbaugh`, `Kalin`, `deGroot`; Johnsonbaugh's
accounts are TacosAndThings (812), then AceRecords (127), as listed. *(UR-04)*

**FR-08: Report format.**
The report MUST be exactly the following lines, each ending in a single LF. `·` stands for one
space (`0x20`) in this table; `<N>` is the decimal of the number of ids in the salesperson's
record, `<ID>` the decimal of the account's id (its value, so `0127` is written `127`), and
`<NAME>`, `<COACH>`, `<REGION>`, and the account `<NAME>` are the fields' exact bytes.

| Line | Content |
| :-- | :-- |
| Heading | `Sales report by salesperson:` |
| (blank) | empty |
| For each salesperson, in FR-07 order: | |
| 1 | 8 × `·`, `Salesperson:··<NAME>` |
| 2 | 8 × `·`, `Sales·coach:··<COACH>` |
| 3 | 8 × `·`, `Sales·region:·<REGION>` |
| 4 | 8 × `·`, `Base·salary·and·bonus:··`, MONEY(SALARY), `··`, MONEY(BONUS) |
| 5 | 8 × `·`, `<N>·Account(s):·` (ending in one space) |
| 6 | empty |
| then for each of the salesperson's accounts, in FR-07 order: | |
| 1 | 16 × `·`, `Name:·······<NAME>` (7 spaces after the colon) |
| 2 | 16 × `·`, `Id:·········<ID>` (9 spaces) |
| 3 | 16 × `·`, `Projected:··`, MONEY(PROJECTED) (2 spaces) |
| 4 | 16 × `·`, `Actual:·····`, MONEY(ACTUAL) (5 spaces) |
| 5 | empty |

There are no other lines, spaces, or tab characters: in particular the report ends with the
empty line that follows the last account (or the last salesperson's line 6), and a salesperson
with no accounts is followed directly by the next salesperson. An empty salesperson input gives
a report of only the heading and the empty line. The values of an account's lines start in the
same column, 12 bytes after the indentation.
*AC:* `dp-sales` → stdout byte-identical to `sales.rpt`; `dp-sales -s team.dat` shows
Kalin's block with `0 Account(s): ` followed by one empty line and then the block of
`deGroot`; `dp-sales -a empty.dat -s empty.dat`, where both files are empty →
`Sales report by salesperson:\n\n`. *(UR-03)*

**FR-09: Validation before output.**
The tool MUST NOT write anything to standard output until both inputs have been read and
validated completely (FR-01). If any input cannot be read or contains an invalid record, the
standard output of the run is empty.
*AC:* in tests 05 … 08, stdout is empty. *(UR-08)*

**FR-10: Data diagnostics.**
A problem found by FR-03 … FR-05 MUST be reported as `dp-sales: <source>:<line>: <message>`
(CONV-34), where `<source>` is the source of the input that holds the record (section 1.3),
`<line>` the record's line number, and `<message>` one of the messages of FR-03 … FR-05.
`<field>` is inserted as its exact bytes (CONV-15). Only the first problem is reported, and the
tool exits with status 1 without writing a report.
*AC:* as in FR-03 … FR-05; with standard input, the source is `-`
(`dp-sales: -:3: …`). *(UR-06, UR-07, UR-08)*

**FR-11: Unreadable input.**
If ACCOUNTS or SALESPEOPLE does not exist, cannot be opened, is a directory, or a read error
occurs, the tool MUST write `dp-sales: <name>: <reason>`, where `<name>` is the option value
exactly as given (`-` for standard input) and `<reason>` is from the CONV-16 table, and exit with
status 1 without writing a report. Because of the order of FR-01, an unreadable or invalid
accounts input is reported even if the salesperson input is unreadable too.
*AC:* `dp-sales -a missing.dat` → stderr `dp-sales: missing.dat: No such file or directory\n`,
stdout empty, exit 1; `dp-sales -a subdir`, where `subdir` is a directory →
`dp-sales: subdir: Is a directory`; `dp-sales -a dup.dat -s missing.dat` reports only the
duplicate id. *(UR-08)*

**FR-12: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12. No file is read.
*AC:* `dp-sales --help` matches the user manual exactly; `dp-sales extra --help` also prints it.
*(UR-10)*

**FR-13: Version.**
`--version` MUST write `dp-sales (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match; `dp-sales --accounts=nowhere.dat --version` also prints it and exits 0.
*(UR-10)*

**FR-14: Usage errors.**
Unknown options (including `-p` and `--prompt`, which this tool does not have), missing option
arguments, and arguments supplied to `--help` or `--version` MUST be reported with the CONV-13
messages followed by the CONV-14 line, with exit status 2. Long options MUST NOT be abbreviated
(CONV-08): `--acc` is unrecognized. After the whole argument list has been scanned (CONV-12),
the tool checks, in this order: an operand, reported as `dp-sales: extra operand '<first
operand>'`; the winning value of `-a`/`--accounts` and then of `-s`/`--salespeople`
(CONV-11), each invalid if empty; and finally, if both values are `-`, the salespeople value,
because standard input can be read only once. An invalid value is reported as
`dp-sales: invalid argument '<value>' for '<option>'`, where `<option>` is the option as the
user wrote it.
*AC:* `dp-sales sales.dat` → `dp-sales: extra operand 'sales.dat'`; `dp-sales -a ''` →
`dp-sales: invalid argument '' for '-a'`; `dp-sales -a - -s -` →
`dp-sales: invalid argument '-' for '-s'`; `dp-sales --salespeople` →
`dp-sales: option '--salespeople' requires an argument`; `dp-sales -p` →
`dp-sales: invalid option -- 'p'`; each followed by the CONV-14 line, exit 2. *(UR-11, UR-13)*

**FR-15: Error atomicity for usage errors.**
When a usage error occurs, the tool MUST NOT open any file, read standard input, or write
anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-11)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output and diagnostics MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Cross-platform focus: exact money and locale-independent collation | Amounts MUST be parsed and printed as exact decimals (for example as a 64-bit count of hundredths), never through a binary floating-point type or a `%.2f`-style conversion of one, so the digits are the same on every platform and for every value up to 92233720368547758.07. Names MUST be compared as unsigned bytes, never with a locale-aware collation (`strcoll`, `localeCompare`, ICU, or a case-insensitive comparison), which orders `deGroot` differently on different systems. Inputs MUST be read in binary mode, so CR bytes reach the field splitter and a `0x1A` byte never ends an input early at the I/O layer; the report MUST be written with LF line endings and with its trailing spaces intact on every platform. | CI black-box tests on 3 OSes; code review |
| NFR-03 | Performance | Any valid input of up to 100 accounts and 100 salespeople, with up to 100 ids each, MUST produce its report in under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 16 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). Inputs of up to 10 MiB (for example with many blank lines or long fields) MUST be processed in under 1 s native (10 s interpreted); memory MAY grow linearly with the size of the inputs, because both are validated before any output (FR-09). | Measurement |
| NFR-04 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list or input bytes (CONV-24), including fields of any length, integers and amounts far outside the 64-bit range, and lines of any length. A broken pipe on standard output ends the tool quietly (CONV-25). | Unit + black-box tests |
| NFR-05 | Maintainability: records, keys, and a parameterized sort | Accounts and salespeople MUST each be held in one record type; a salesperson MUST refer to its accounts by reference or index into the account collection, not by copies of their fields. Both orderings MUST be produced by **one** sort procedure that receives the collection and a comparison function (the textbook's quicksort), called once with a comparison of ids and once with a comparison of names; ties between equal names MUST be broken by input position, by the comparison or by a stable sort. Account ids MUST be resolved by binary search in the accounts sorted by id, not by a linear scan or a hash table. Option parsing, line splitting, record validation, linking, sorting, money formatting, and report formatting MUST be separate units (Principles 3, 12, 13, 18). | Design review |
| NFR-06 | Testability | Money parsing and MONEY(*x*), the comparison functions, the sort, the binary search, and the report formatter MUST be pure functions covered by unit tests, including every acceptance value of FR-04, the sort with equal names, a name that is a prefix of another, the binary search for the first, last, and a missing id, and the report for a salesperson with no accounts. | Code review |
| NFR-07 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-08 | Security | The tool MUST read only ACCOUNTS and SALESPEOPLE (or standard input), MUST NOT create or modify any file, read environment variables, or run subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Usage errors (exit status 2). Each is followed by `Try 'dp-sales --help' for more information.`

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (including `-p`) | `dp-sales: invalid option -- 'x'` |
| Unknown or abbreviated long option token `T` (including `--prompt`) | `dp-sales: unrecognized option 'T'` |
| `-a` / `-s` without an argument | `dp-sales: option requires an argument -- 'a'` (or `'s'`) |
| `--accounts` / `--salespeople` without an argument | `dp-sales: option '--accounts' requires an argument` (or `'--salespeople'`) |
| `--help=…` / `--version=…` | `dp-sales: option '--help' doesn't allow an argument` (or `'--version'`) |
| Operand `X` | `dp-sales: extra operand 'X'` |
| Empty FILE for `-a`, `--accounts`, `-s`, or `--salespeople` | `dp-sales: invalid argument '' for '-a'` (or the option as written) |
| Both ACCOUNTS and SALESPEOPLE are `-` | `dp-sales: invalid argument '-' for '-s'` (or `'--salespeople'`, as written) |

Runtime errors (exit status 1; the tool stops at the first one and writes no report). `F` is
ACCOUNTS or SALESPEOPLE as given, `A` the accounts source, `P` the salesperson source, `L` a
record's line number, and `K` a field's exact bytes.

| Trigger | Exact message |
| :-- | :-- |
| `F` does not exist | `dp-sales: F: No such file or directory` |
| `F` cannot be opened or read because access is denied | `dp-sales: F: Permission denied` |
| `F` is a directory | `dp-sales: F: Is a directory` |
| A component of the path `F` is not a directory | `dp-sales: F: Not a directory` |
| Any other open or read failure of `F` (including standard input, `F` = `-`) | `dp-sales: F: Input/output error` |
| A 101st account | `dp-sales: A:L: too many accounts (limit 100)` |
| A 101st salesperson | `dp-sales: P:L: too many salespeople (limit 100)` |
| A record ends before a required field (either file) | `dp-sales: A:L: incomplete record` (or `P:L:`) |
| An account record has a fifth field `K` | `dp-sales: A:L: unexpected field 'K'` |
| An id field `K` is not a valid *integer* (either file) | `dp-sales: A:L: invalid integer 'K'` (or `P:L:`) |
| An id field `K` is a valid *integer* below 0 (either file) | `dp-sales: A:L: value out of range 'K'` (or `P:L:`) |
| An amount field `K` does not match the *amount* grammar (either file) | `dp-sales: A:L: invalid amount 'K'` (or `P:L:`) |
| An amount field `K` exceeds 92233720368547758.07 (either file) | `dp-sales: A:L: value out of range 'K'` (or `P:L:`) |
| An account id `K` has the value of an earlier account's id | `dp-sales: A:L: duplicate account id 'K'` |
| The sixth field `K` of a salesperson record is not `#` | `dp-sales: P:L: expected '#' but found 'K'` |
| A listed id `K` matches no account | `dp-sales: P:L: unknown account 'K'` |
| A listed id `K` has the value of an earlier id of the same record | `dp-sales: P:L: account listed twice 'K'` |
| Standard output cannot be written (other than a broken pipe) | `dp-sales: write error` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-12, FR-14, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases; cases 02 … 10 have several steps) | FR-01 … FR-15 |
| Unit test (written by the implementer) | FR-03 … FR-08, NFR-06 |
| Measurement | NFR-03 |
| Inspection / review | NFR-02, NFR-05, NFR-08 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-sales` | FR-01 (default files), FR-03 … FR-08 (stdout identical to `sales.rpt`) |
| 02 | `dp-sales --accounts=- < sales.dat` | FR-01 (standard input) |
| 03 | `dp-sales -s team.dat` | FR-04 (money), FR-05, FR-07 (byte order, equal names, listed order), FR-08 (no accounts) |
| 04 | `dp-sales -a mixed.dat` | FR-02 (CRLF, tabs, blank lines, Ctrl-Z), FR-04 (leading zeros) |
| 05 | `dp-sales -s unknown.dat` | FR-05, FR-09, FR-10 |
| 06 | `dp-sales -a dup.dat` | FR-03 (duplicate id by value), FR-09, FR-10 |
| 07 | `dp-sales -a bad-amount.dat` | FR-04, FR-10 |
| 08 | `dp-sales -a missing.dat` | FR-11 |
| 09 | `dp-sales --help` | FR-12 |
| 10 | `dp-sales sales.dat` | FR-14, FR-15 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01 |
| UR-02 | FR-01, FR-14, CONV-26 |
| UR-03 | FR-08 |
| UR-04 | FR-05, FR-06, FR-07 |
| UR-05 | FR-04, NFR-02 |
| UR-06 | FR-03, FR-04, FR-05, FR-10, CONV-34 |
| UR-07 | FR-03, FR-05, FR-10 |
| UR-08 | FR-01, FR-09, FR-10, FR-11, CONV-16 |
| UR-09 | FR-02, NFR-02, CONV-37 |
| UR-10 | FR-12, FR-13 |
| UR-11 | FR-14, FR-15 |
| UR-12 | FR-07, FR-08, NFR-01, NFR-02, CONV-03 |
| UR-13 | FR-14, CLI-CONV |
| UR-14 | NFR-03, NFR-07 |
