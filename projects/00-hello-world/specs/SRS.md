# Software Requirements Specification (SRS) — dp-hello

| Field | Value |
| :-- | :-- |
| Document ID | SRS-00 |
| Project | `00-hello-world` — Standard Terminal Hello World |
| Product | `dp-hello` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-00) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-hello`. It is complete and
precise enough that independent implementations in any programming language produce
**byte-identical** output for every invocation. It is the authoritative source for design
(HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-hello` writes a greeting line to standard output. The greeting can be personalized and
repeated. The tool reads no input, takes no operands, and touches no files.

### 1.3 Definitions
| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Greeting line | The UTF-8 bytes of `Hello, ` + NAME + `!`, followed by LF |
| NAME | The greeted name: `World` by default, otherwise the value of `--name` |
| COUNT | The number of greeting lines to print: 1 by default, otherwise the value of `--count` |

### 1.4 References
- URD-00: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)

## 2. Overall description

### 2.1 Product perspective
`dp-hello` is a standalone executable. Its interfaces are the command line, standard output,
standard error, and the exit status. It is the first of the eleven curriculum tools and the one
that establishes the shared conventions in CLI-CONV.

### 2.2 Product functions
1. Print the greeting `Hello, World!`.
2. Greet a user-supplied name.
3. Repeat the greeting 1–1000 times.
4. Display help and version information.
5. Detect and report usage errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior.

### 2.4 Assumptions
- The terminal or consumer accepts UTF-8.
- Standard output may be a terminal, a pipe, or a file. Behavior is the same in every case.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-hello [-n NAME | --name=NAME] [-c COUNT | --count=COUNT]
dp-hello --help
dp-hello --version
```

### 3.2 Options

| Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- |
| `-n` | `--name` | NAME (required) | `World` | Greet NAME instead of `World` |
| `-c` | `--count` | COUNT (required) | `1` | Print the greeting COUNT times |
| — | `--help` | none | — | Print the help text and exit 0 |
| — | `--version` | none | — | Print the version line and exit 0 |

Option syntax (bundling, `--name=value`, `--`, repetition, and scan order) follows CONV-07 …
CONV-12. For example, `-c2 -nKen`, `-c 2 -n Ken`, and `--count=2 --name Ken` are equivalent.

### 3.3 Operands
`dp-hello` accepts **no operands**.

### 3.4 Standard input
Not read (CONV-26).

### 3.5 Standard output
Exactly COUNT greeting lines on success. Nothing on error.

### 3.6 Standard error
Diagnostics only (section 6). Nothing on success.

### 3.7 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | The greeting was printed, or `--help` / `--version` was handled |
| 2 | Usage error |

`dp-hello` never exits with status 1, because its only runtime failure mode is EPIPE
(CONV-25).

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirement it derives from.

**FR-01: Default greeting.**
With no options, the tool MUST write exactly `Hello, World!` + LF to standard output and exit
with status 0.
*AC:* `dp-hello` → stdout `Hello, World!\n`, stderr empty, exit 0. *(UR-01, UR-07)*

**FR-02: Named greeting.**
When `-n NAME`, `--name NAME`, `--name=NAME`, or `-nNAME` is given, the greeting line MUST be
`Hello, ` + NAME + `!` + LF. NAME is used verbatim: case, spaces, punctuation, and non-ASCII
characters are preserved and emitted as UTF-8 (CONV-05). NAME may begin with `-` when it is
attached (`--name=-x`, `-n-x`) or supplied as the next token (`--name -x`).
*AC:* `dp-hello --name 'Ada Lovelace'` → `Hello, Ada Lovelace!\n`. *(UR-02, UR-09)*

**FR-03: Empty name rejected.**
If NAME is the empty string, the tool MUST report the usage error
`dp-hello: invalid argument '' for '<option>'`, where `<option>` is `-n` or `--name`, as the user
wrote it (CONV-13, CONV-15).
*AC:* `dp-hello --name ''` → exit 2, stderr as specified, stdout empty. *(UR-06)*

**FR-04: Repetition.**
When `-c COUNT` or `--count COUNT` is given, the tool MUST write the greeting line exactly COUNT
times. COUNT MUST consist only of ASCII decimal digits (`0`–`9`, with no sign, spaces, or other
characters), and its value MUST be between **1 and 1000** inclusive. Leading zeros are allowed:
`007` means 7.
*AC:* `dp-hello --count 3` → three identical lines. *(UR-03)*

**FR-05: Invalid count rejected.**
If COUNT is empty, contains any character other than `0`–`9`, or has a value outside 1–1000,
the tool MUST report `dp-hello: invalid argument '<COUNT>' for '<option>'` (CONV-13) and exit
with status 2.
*AC:* `dp-hello --count 0`, `dp-hello -c abc`, and `dp-hello -c 1001` each exit 2 with that
diagnostic. *(UR-06)*

**FR-06: Option repetition.**
If `--name` or `--count` is given more than once, the last occurrence wins (CONV-11).
Validation (FR-03, FR-05) applies only to the winning value.
*AC:* `dp-hello -n A -n B` → `Hello, B!\n`. *(UR-10)*

**FR-07: Help.**
`--help` MUST write the help text from user-manual §"Help output" byte-for-byte to standard
output and exit 0, following the scan order in CONV-12.
*AC:* `dp-hello --help` matches the user manual exactly. `dp-hello --help extra -x` prints the
help and exits 0, because the scan reaches `--help` first. `dp-hello extra --help` also prints
the help: operand errors are detected only after the scan (CONV-12). *(UR-04)*

**FR-08: Version.**
`--version` MUST write `dp-hello (dialectic-playground) 1.0.0` + LF and exit 0 (CONV-02).
*AC:* exact match. *(UR-05)*

**FR-09: Operands rejected.**
Any operand, including tokens that follow `--`, MUST produce
`dp-hello: extra operand '<first operand>'` and exit status 2. Operands are checked after the
whole argument list has been scanned, so `--help` or `--version` anywhere in the list takes
precedence (CONV-12).
*AC:* `dp-hello extra` and `dp-hello -- -n` each exit 2 with that diagnostic. *(UR-06)*

**FR-10: Unknown and malformed options.**
Unknown options, missing option arguments, and arguments supplied to `--help` or `--version`
MUST be reported with the CONV-13 messages and exit status 2. Long options MUST NOT be
abbreviated (CONV-08): `--nam` is unrecognized.
*AC:* `dp-hello -x`, `dp-hello --nme Ada`, `dp-hello --name`, and `dp-hello --version=1` each
produce the CONV-13 message and exit 2. *(UR-06, UR-10)*

**FR-11: Error atomicity.**
When a usage error occurs, the tool MUST NOT write anything to standard output (CONV-12).
*AC:* stdout is empty in every exit-2 case. *(UR-06)*

## 5. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | Output MUST be byte-identical on Linux, macOS, and Windows, and every line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Performance | Wall-clock run time MUST be under 100 ms for a natively compiled build (under 300 ms for an interpreted runtime) on CI hardware, with peak memory under 32 MiB (above the runtime's baseline for managed or interpreted runtimes, CONV-31). | Measurement |
| NFR-03 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list (CONV-24). | Unit + black-box tests |
| NFR-04 | Maintainability | Option parsing, validation, greeting construction, and output MUST be separate units (Principles 13, 18). | Design review |
| NFR-05 | Testability | Greeting construction MUST be a pure function covered by unit tests. | Code review |
| NFR-06 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |
| NFR-07 | Security | The tool MUST read no files and no environment variables, and MUST run no subprocesses. | Inspection |

## 6. Diagnostics (complete list)

Each diagnostic is followed by `Try 'dp-hello --help' for more information.` and exit status 2.

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` | `dp-hello: invalid option -- 'x'` |
| Unknown long option token `T` | `dp-hello: unrecognized option 'T'` |
| `-n` / `-c` without an argument | `dp-hello: option requires an argument -- 'n'` (or `'c'`) |
| `--name` / `--count` without an argument | `dp-hello: option '--name' requires an argument` (or `'--count'`) |
| `--help=…` / `--version=…` | `dp-hello: option '--help' doesn't allow an argument` (or `'--version'`) |
| Empty NAME | `dp-hello: invalid argument '' for '-n'` (or `'--name'`) |
| Invalid COUNT `V` | `dp-hello: invalid argument 'V' for '-c'` (or `'--count'`) |
| Operand `X` | `dp-hello: extra operand 'X'` |

## 7. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01, FR-02, FR-04, FR-07, FR-08, FR-09, FR-10 |
| Black-box test (hidden, `tests/private/`, 10 cases; case 10 has two steps) | FR-02 … FR-07, FR-09, FR-10 |
| Unit test (written by the implementer) | FR-02 … FR-06, NFR-05 |
| Inspection / review | NFR-02, NFR-04, NFR-07 |

Public test map:

| Test | Command | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-hello` | FR-01 |
| 02 | `dp-hello --name Ada` | FR-02 |
| 03 | `dp-hello -n Grace` | FR-02 |
| 04 | `dp-hello --name=Linus` | FR-02, CONV-08 |
| 05 | `dp-hello --count 3` | FR-04 |
| 06 | `dp-hello -c2 -n Ken` | FR-04, CONV-07 |
| 07 | `dp-hello --help` | FR-07 |
| 08 | `dp-hello --version` | FR-08 |
| 09 | `dp-hello -x` | FR-10 |
| 10 | `dp-hello extra` | FR-09 |

## 8. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-01 |
| UR-02 | FR-02 |
| UR-03 | FR-04 |
| UR-04 | FR-07 |
| UR-05 | FR-08 |
| UR-06 | FR-03, FR-05, FR-09, FR-10, FR-11 |
| UR-07 | FR-01, §3.7 |
| UR-08 | NFR-01, CONV-03 |
| UR-09 | FR-02, CONV-05 |
| UR-10 | FR-06, FR-10, CLI-CONV |
| UR-11 | NFR-02 |
| UR-12 | NFR-06 |
