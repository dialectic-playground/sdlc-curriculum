<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dialectic-playground/.github/main/assets/sdlc-curriculum/dist/logo-dark.svg">
    <img alt="dialectic playground / sdlc-curriculum" src="https://raw.githubusercontent.com/dialectic-playground/.github/main/assets/sdlc-curriculum/dist/logo.svg" height="96">
  </picture>
</p>

# SDLC Curriculum: System-Level Tooling and Applications Programming

Specification-driven curriculum: specs, black-box tests, and templates for fifty-three
cross-platform CLI projects.

📖 **Documentation:** <https://dialectic-playground.github.io/docs/> (curriculum index:
[Reference → Curriculum](https://dialectic-playground.github.io/docs/reference/curriculum/))

A **specification-driven** curriculum of fifty-three language-agnostic projects (sixty-five
CLI tools, one of which also serves an HTTP API), in two tracks:

- **System-level tooling (Projects 00–10).** It starts with Project 00, "Hello, World!", and
  works up through ten classic POSIX coreutils and shell built-ins to a key-value store with an
  HTTP API and a telemetry daemon.
- **Applications programming (Projects 11–52).** Forty-two projects adapted from the programs
  of R. Johnsonbaugh and M. Kalin, *Applications Programming in ANSI C* (3rd ed., Prentice
  Hall, 1996), from a first program and stream filters through recursion, arrays, files,
  data structures, graph search, and fault recovery. Each becomes a professional tool under
  the same conventions, with exact numeric formatting and reproducible randomness.

This repository contains **everything except the implementations**: requirements, user
manuals, black-box acceptance tests with exact expected outputs, white-box document templates,
the universal build contract, and the cross-platform CI template. Implementations are written
later, in **separate language repositories** (for example `dialectic-playground/py`, `…/rs`,
`…/go`), all of which are built and verified against this one shared specification.

## Philosophy

| Principle | What it means here |
| :-- | :-- |
| **Specification first** | Each project ships a complete URD, SRS, and user manual. Behavior is defined down to the byte, including error messages, exit statuses, and help text. |
| **Black-box acceptance** | Every project has 10 public and 10 hidden tests. Each compares stdout, stderr, and exit status byte-for-byte, whatever the implementation language. |
| **White-box ownership** | Implementers own the engineering lifecycle: a High-Level Design, a Low-Level Design, a Requirements Traceability Matrix, and a Master Test Plan, all from standard templates. |
| **Cross-platform by default** | Every tool must behave identically on **Linux, macOS, and Windows**, verified in GitHub Actions. |
| **One build interface** | The same `make` targets build, test, lint, format, install, and clean every implementation in every language. |
| **Code-quality governance** | The 20 engineering principles below apply to every implementation. |

## Repository layout

```text
sdlc-curriculum/
├── README.md                       # this file
├── curriculum.toml                 # project registry (slugs, titles, tool names)
├── shared/
│   ├── CLI-CONVENTIONS.md          # normative behavior shared by every tool (CONV-01…38)
│   ├── templates/
│   │   ├── HLD-TEMPLATE.md
│   │   ├── LLD-TEMPLATE.md
│   │   ├── RTM-TEMPLATE.md
│   │   ├── MASTER-TEST-PLAN-TEMPLATE.md
│   │   ├── DOCS-PLAN-TEMPLATE.md
│   │   ├── BASE-MAKEFILE           # universal polyglot build contract
│   │   ├── assignment/             # templates for each project's assignment/ workspace
│   │   └── language/               # skeleton for language repositories (root Makefile)
│   ├── ci/
│   │   └── cross-platform-ci.yml   # GitHub Actions template for implementation repos
│   └── tools/
│       ├── run-tests.py            # black-box test runner (stdlib Python, all OSes)
│       └── check-curriculum.py     # repository validator used by CI
├── projects/                       # the fifty-three projects (00–52), described below
├── reference/                      # maintainer-only models that generate/verify fixtures
├── tools/
│   ├── scaffold-project.py         # creates a project's assignment/ from the templates
│   ├── dp-run                      # shared container-first runner (copy of the .github original)
│   └── container.mk                # shared make integration, also used by BASE-MAKEFILE
├── Makefile, Containerfile         # container-first entry points: make check, the toolchain image
├── .devcontainer/                  # dev container using the same image
└── .github/workflows/ci.yml         # validates this repository in a container and on 3 OSes
```

## The projects

### System-level tooling (00–10)

| # | Project | Tool(s) | Inspiration | Functional scope | Cross-platform focus |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 00 | [`00-hello-world`](projects/00-hello-world/) | `dp-hello` | `echo "Hello, World!"` | Terminal output, option parsing, exit status | Binary execution, newline consistency |
| 01 | [`01-echo`](projects/01-echo/) | `dp-echo` | `echo` | Argument handling, `-n`/`-e`/`-E`, escapes | `\r\n` vs `\n` line endings |
| 02 | [`02-cat`](projects/02-cat/) | `dp-cat` | `cat` | Concatenation, stdin fallback, `-n`/`-b`, `-v` | File-descriptor management across filesystems |
| 03 | [`03-head-tail`](projects/03-head-tail/) | `dp-head`, `dp-tail` | `head`, `tail` | Byte/line slicing from either end, follow mode | Buffer seeking on multi-GB files in bounded memory |
| 04 | [`04-wc`](projects/04-wc/) | `dp-wc` | `wc` | Line/word/char/byte counts, totals, UTF-8 safety | Locale-independent counting |
| 05 | [`05-grep-lite`](projects/05-grep-lite/) | `dp-grep` | `grep` | Regex matching, `-n`, `-v`, `-r` | Regex-engine portability, path separators |
| 06 | [`06-find-lite`](projects/06-find-lite/) | `dp-find` | `find` | Traversal, name/size/time predicates, `-exec` | `MAX_PATH`, permission-denied states |
| 07 | [`07-diff-lite`](projects/07-diff-lite/) | `dp-diff` | `diff` | LCS/Myers comparison, normal and unified output | Deterministic formatting, newline normalization |
| 08 | [`08-env-run`](projects/08-env-run/) | `dp-env` | `env` / `nohup` | Subprocesses with modified environments, signals | Win32 process creation vs. fork/exec |
| 09 | [`09-kv-store`](projects/09-kv-store/) | `dp-kv` | SQLite / Redis subset | Atomic writes, locking, JSON, local REST API | `flock` vs. `LockFileEx` |
| 10 | [`10-sys-monitor`](projects/10-sys-monitor/) | `dp-sysmon` | `top` / `ps` | CPU, memory, disk, process telemetry; table/JSON | `/proc` vs. macOS APIs vs. PDH |

### Applications programming (11–52)

Each project adapts one section of Johnsonbaugh and Kalin, *Applications Programming in ANSI C*
(3rd ed., 1996); the Inspiration column gives the section. Where the original program read the
keyboard, the tool reads the same responses from standard input and can show the original
prompts on standard error (`--prompt`). Data files from the book's companion disk are included
as test fixtures where a program used them.

| # | Project | Tool(s) | Inspiration | Functional scope | Cross-platform focus |
| :-- | :-- | :-- | :-- | :-- | :-- |
| 11 | [`11-kinder`](projects/11-kinder/) | `dp-kinder` | §1.1 first program | Fixed-message output, CONV-12 scan order, operand rejection, exit status | Binary-mode console output (LF only, no BOM or code-page effects) |
| 12 | [`12-convert`](projects/12-convert/) | `dp-convert` | §1.2 yards to feet and inches | Sentinel-terminated yards → feet/inches with 64-bit limits and prompts | Interactive dialog flushing, Ctrl-D vs. Ctrl-Z, CRLF and trailing Ctrl-Z input |
| 13 | [`13-taxes`](projects/13-taxes/) | `dp-taxes` | §1.6 tax calculator (stream) | Income tokens to two-bracket tax records, exact integer arithmetic, prompts | Keyboard EOF (Ctrl-D vs. Ctrl-Z Enter), CRLF/Ctrl-Z data, per-record flushing |
| 14 | [`14-taxes-file`](projects/14-taxes-file/) | `dp-taxes-file` | §1.10 tax calculator (batch files) | `incomes.dat` → `out.dat` batch job, whole input validated before output | Binary-mode output files, create/truncate, portable error reasons |
| 15 | [`15-stats`](projects/15-stats/) | `dp-stats` | §2.5 statistical measures | Single-pass count, extremes, sum, mean, variance, standard deviation in constant memory | Reproducible binary64 arithmetic (no x87, FMA contraction, or flush-to-zero) |
| 16 | [`16-bargraph`](projects/16-bargraph/) | `dp-bargraph` | §2.8 bar graph | Title/value records to `*` bars (one per two units), located data errors | CRLF input and the trailing Ctrl-Z end-of-file marker, binary-mode reading |
| 17 | [`17-stream-filters`](projects/17-stream-filters/) | `dp-average`, `dp-chk-sort` | §3.1 average and sort check | Average of positive reals; non-decreasing check answered by exit status | Early termination across files, pipes, and consoles; reproducible digits |
| 18 | [`18-primes`](projects/18-primes/) | `dp-primes` | §3.2 primes by trial division | All primes ≤ n (n ≤ 10⁷) or just their count, with banner and prompt | Interactive input, raw TAB bytes, CR and trailing Ctrl-Z in input |
| 19 | [`19-calendar`](projects/19-calendar/) | `dp-calendar` | §3.6 annual calendar | 12-month calendar grid from day/leap codes or a Gregorian year | Exact space-only text grid, interactive re-prompting, Ctrl-Z marker |
| 20 | [`20-bargraph-grade`](projects/20-bargraph-grade/) | `dp-bargraph2`, `dp-grade` | §4.1 procedures: bar graph and grade | Procedural bar graph identical to 16; weighted pass/fail grader with exact threshold | Grades independent of binary floating point; interactive prompt/flush behavior |
| 21 | [`21-resistor`](projects/21-resistor/) | `dp-resistor` | §4.4 resistor color code | 3-band color codes decoded to ohms/kilo-ohms/mega-ohms with re-prompting | Locale-independent ASCII case folding; console EOF, CRLF, and Ctrl-Z handling |
| 22 | [`22-dice`](projects/22-dice/) | `dp-dice` | §4.7 Roll Them Bones dice game | Seeded dice game: bankroll, table limit, naturals, marks, double payouts | Reproducible randomness in exact 32-bit arithmetic, never platform `rand()` |
| 23 | [`23-recursion`](projects/23-recursion/) | `dp-fact`, `dp-tower`, `dp-walk-r`, `dp-walk-nr` | §4.8 factorial, Tower of Hanoi, robot walk | Recursive factorial, Hanoi moves, robot-walk counts by tree recursion vs. iteration | Integer width and call-stack depth (32-bit `long`, 1 MiB Windows stack) |
| 24 | [`24-tromino`](projects/24-tromino/) | `dp-tromino` | §4.9 tromino tiling | Divide-and-conquer L-tromino tiling of 2^k boards, with optional ASCII drawing | Bulk buffered output vs. interactive flushing on consoles, pipes, and files |
| 25 | [`25-max`](projects/25-max/) | `dp-max` | §4.10 variadic maximum | Maximum of one to four 64-bit integers via one variable-arity function | Exact 64-bit integer width (32-bit `long` on Windows, binary64 runtimes) |
| 26 | [`26-cars`](projects/26-cars/) | `dp-cars1` | §5.3 car sales tracker | Opening stock and sales for 12 brands, refused sales, fixed-width daily report | Interactive console dialog: flushed prompts, binary reads, Ctrl-D vs. Ctrl-Z |
| 27 | [`27-line-wrap`](projects/27-line-wrap/) | `dp-wrap` | §5.5 greedy line wrap | Greedy word wrapping to a line length, characters or bytes, over-long words reported | Locale-independent text measurement (UTF-8 characters, not code units) |
| 28 | [`28-cars-modular`](projects/28-cars-modular/) | `dp-cars2` | §5.6 report as a separate component | Byte-identical to 26, plus saving totals and reporting from saved totals | Portable saved-totals file (binary mode, LF only, portable error reasons) |
| 29 | [`29-strlen`](projects/29-strlen/) | `dp-strlen` | §5.8 string length | Length of each operand or input line by explicit scan, characters or bytes | UTF-16 vs. UTF-8 lengths, CRLF line endings |
| 30 | [`30-matmult`](projects/30-matmult/) | `dp-matmult` | §5.10 matrix multiplication | N×N integer matrices (N ≤ 20) echoed and multiplied, with overflow detection | Exact 64-bit integer width and defined-behavior overflow detection |
| 31 | [`31-phone`](projects/31-phone/) | `dp-phone` | §5.11 directory lookup | Fixed-width records, selection sort, binary-search lookups by last name | Byte-exact columns and unsigned byte comparison (no locale collation) |
| 32 | [`32-percolation`](projects/32-percolation/) | `dp-perc` | §5.12 forest-fire percolation | Seeded random forest, downward fire spread, bordered grids and statistics | Reproducible randomness from the specified ANSI C generator |
| 33 | [`33-reverse`](projects/33-reverse/) | `dp-reverse` | §6.5 in-place string reversal | Two-index in-place reversal of words or lines up to 100 characters | Character boundaries (UTF-16 code-unit reversal breaks emoji), line endings |
| 34 | [`34-parallel-sort`](projects/34-parallel-sort/) | `dp-sort-host`, `dp-sort-child` | §6.6 parallel host/child sort | Partitioned sort with a concurrent worker over a line protocol, then a merge | Threads vs. processes over pipes; deadlock-free ordering for any pipe size |
| 35 | [`35-sort-bench`](projects/35-sort-bench/) | `dp-sort-bench` | §6.10 sort timing harness | Selection sort vs. quicksort on seeded arrays: exact operation counts, opt-in timing | Portable random arrays; monotonic clocks on each OS for optional timings |
| 36 | [`36-page`](projects/36-page/) | `dp-page` | §7.2 text paginator | 52-line pages with `Page N` headers and form feeds, bytes copied verbatim | Binary transparency (CR, NUL, FF, Ctrl-Z copied as data), LF-only framing |
| 37 | [`37-calc`](projects/37-calc/) | `dp-calc` | §7.5 accumulator calculator | Left-to-right accumulator over operator/operand pairs with line rollback | Truncating division/remainder and overflow traps (−2⁶³ / −1) everywhere |
| 38 | [`38-sched`](projects/38-sched/) | `dp-sched` | §7.9 greedy activity selection | Fixed-width activities, stable sort by finish time, greedy selection | Deterministic ordering independent of library sort stability |
| 39 | [`39-size`](projects/39-size/) | `dp-size` | §8.3 file byte size | Byte size of named files (extension appended) by binary reading | Binary vs. text mode (CRLF translation and Ctrl-Z would change the count) |
| 40 | [`40-relative-file`](projects/40-relative-file/) | `dp-relfile` | §8.8 relative file with hashing | 100-slot hashed relative file: linear probing, tombstones, menu and subcommands | Binary random access at fixed offsets; byte-identical data file on every OS |
| 41 | [`41-films`](projects/41-films/) | `dp-films` | §9.2 nearest-neighbor film classifier | 1-nearest-neighbor hit/flop classifier over a validated sample set | Reproducible binary64 distances (no FMA, no x87), console end of input |
| 42 | [`42-sales-report`](projects/42-sales-report/) | `dp-sales` | §9.7 relational sales report | Accounts joined to salespeople by id; byte-exact `sales.rpt` report | Exact decimal money and byte-wise name order; trailing spaces preserved |
| 43 | [`43-linked-list`](projects/43-linked-list/) | `dp-elephnt1`, `dp-elephnt2` | §10.2 linked list of elephants | Static three-node list and a dialog-built list, one shared traversal | Interactive line input: binary reads, CRLF and Ctrl-Z, console EOF, flushed prompts |
| 44 | [`44-line-editor`](projects/44-line-editor/) | `dp-line-ed` | §10.3 line editor | Linked-buffer line editor: insert, delete, type, move, find, substitute, quit-and-write | Byte-exact file round trip in binary mode (CRLF kept, Ctrl-Z ignored) |
| 45 | [`45-queue-stack`](projects/45-queue-stack/) | `dp-queue1`, `dp-queue2`, `dp-stack1`, `dp-stack2` | §10.4 queue and stack ADTs | FIFO customers and LIFO trays on fixed arrays (100) vs. linked lists | Platform-independent capacity and storage; graceful out-of-memory handling |
| 46 | [`46-infix`](projects/46-infix/) | `dp-infix` | §10.5 infix to postfix | Shunting-yard conversion with precedence, parentheses, and located errors | Line-oriented input (LF/CRLF, missing final LF, Ctrl-Z); flushed dialog prompts |
| 47 | [`47-bfs`](projects/47-bfs/) | `dp-bfs-adj`, `dp-bfs-link` | §10.8 seven deadly sins BFS | BFS discovery order over a built-in or file graph: matrix vs. head-inserted lists | Visit order from data alone (no hashing or library ordering); binary graph files |
| 48 | [`48-astar`](projects/48-astar/) | `dp-astar` | §10.9 A* search to Vienna | A* route over the textbook's European road data with reopening and traces | Legacy MS-DOS data files (tabs, wrapped rows, Ctrl-Z); ASCII-only case folding |
| 49 | [`49-assert-sort`](projects/49-assert-sort/) | `dp-assert-sort` | §11.1 assertions and loop invariants | Selection sort with bounds assertion, invariant checks, trace, and fault injection | Assertions that behave identically everywhere (no abort dialogs, never compiled out) |
| 50 | [`50-fault-recovery`](projects/50-fault-recovery/) | `dp-divide` | §11.2 setjmp/longjmp fault recovery | Divides pairs of reals; zero divisor or overflow is caught and recovered | Floating-point faults found by explicit tests, not traps or FP-environment flags |
| 51 | [`51-koch`](projects/51-koch/) | `dp-koch` | §11.4 von Koch snowflake | Koch curve or snowflake (levels 0–6) as vertex coordinates or SVG | Reproducible binary64 geometry (fixed operation order, no FMA, no negative zero) |
| 52 | [`52-spacecraft`](projects/52-spacecraft/) | `dp-ship` | §11.5 C++ spacecraft class | Encapsulated spacecraft object: textbook scenario or a command script | `GEN` formatting independent of runtime float-to-text defaults (exponent digits) |

Every tool name starts with `dp-`, so installing a tool never shadows a real system utility.

### Inside each project

```text
projects/XX-slug/
├── README.md                   # purpose, operational scope, learning objectives
├── specs/
│   ├── URD.md                  # user requirements (UR-xx)
│   ├── SRS.md                  # software requirements (FR-xx, NFR-xx), exact diagnostics
│   └── user-manual.md          # complete user manual, including the normative --help text
├── tests/
│   ├── fixtures/               # input files shared by both suites (where needed)
│   ├── public/
│   │   ├── test-inputs.txt     # 10 visible invocations
│   │   ├── fixtures/           # input files for this suite only (where needed)
│   │   └── expected-outputs/   # <ID>.stdout, <ID>.stderr, <ID>.exit
│   └── private/
│       ├── hidden-inputs.txt   # 10 hidden invocations (grading / CI)
│       ├── fixtures/
│       └── expected-outputs/
└── assignment/                 # language-neutral workspace template for implementers
    ├── hld.md  lld.md  rtm.md  master-test-plan.md
    ├── Makefile                # extends BASE-MAKEFILE; language repos fill in the DP_* hooks
    └── src/README.md           # the implementation contract
```

## Global standards

### POSIX-style CLI conventions

[`shared/CLI-CONVENTIONS.md`](shared/CLI-CONVENTIONS.md) is part of every SRS. It defines:

- **Option syntax:** short options with bundling, long options with no abbreviations, `--`, and
  `-` as standard input.
- **Diagnostics:** the exact wording of every usage error and file error, using a fixed table
  of reasons instead of OS error strings.
- **Exit statuses:** 0 for success, 1 for a runtime failure, 2 for a usage error, unless a
  project's SRS overrides them.
- **Help and version:** `--help` and `--version`; the help text is normative.
- **Data, numbers, and dialogs** (Projects 11–52): whitespace-separated tokens with line
  numbers, exact integer and real grammars, located data diagnostics, correctly rounded number
  formatting (`FIX`, `GEN`), optional prompts on standard error (`--prompt`), the legacy
  Ctrl-Z end-of-file marker, and the ANSI C `rand()` generator with `--seed`.

### Cross-platform requirements

- Output is byte-identical on every OS. Every line terminator a tool generates is **LF only**,
  even on Windows, so standard streams are written in binary mode.
- Input data is binary-safe: CR bytes are data, preserved unless a project specifies otherwise.
- Arguments and output text are UTF-8, independent of locale.
- Paths a tool constructs use `/`, and directory traversal is in byte-wise sorted order.
- Every implementation must pass all black-box tests in CI on `ubuntu-latest`, `macos-latest`,
  and `windows-latest`.

## The universal Makefile contract

[`shared/templates/BASE-MAKEFILE`](shared/templates/BASE-MAKEFILE) is language-neutral. It
defines the targets every implementation must support. Each language repository plugs in its
toolchain's commands through **hook variables** in the project `Makefile`:

| Target | Purpose | Hook |
| :-- | :-- | :-- |
| `all` | Compile, build, or prepare the tools into `BIN_DIR` | `DP_BUILD` |
| `install` | Install the tools into `$(BINDIR)` (default `~/.local/bin`) | `DP_INSTALL` |
| `uninstall` | Remove the installed tools | `DP_UNINSTALL` |
| `test` / `check` | Language-native unit tests, then the public black-box suite | `DP_UNIT_TEST` (+ runner) |
| `lint` | Static analysis, linters, and type checkers | `DP_LINT` |
| `format` | The language's standard formatter | `DP_FORMAT` |
| `clean` | Remove build artifacts and compilation caches | `DP_CLEAN` |
| `distclean` | `clean`, plus virtualenvs, dependency caches, and local config | `DP_DISTCLEAN` |
| `test-blackbox` | Public black-box suite only (part of `test`) | *(provided)* |
| `test-hidden` / `grade` | Hidden suite, or both suites (CI and grading) | *(provided)* |
| `help` | Show the configuration and which hooks are defined | *(provided)* |

**Container-first.** `BASE-MAKEFILE` includes the curriculum's copy of `tools/container.mk`.
Every target runs in the language repository's toolchain container, built from the
`Containerfile` at the repository root: Podman, then Docker, then the local system. Override
the choice with `DP_RUNTIME=podman|docker|local`. The image needs the language toolchain,
`make`, and `python3` ≥ 3.11 for the black-box runner. `install`, `uninstall`, and `help` act on
the host, so they always run locally. Use `DP_RUNTIME=local` to build and test natively on your
own operating system. See
[Container-first development](https://dialectic-playground.github.io/docs/explanation/container-first-development/).

A hook that is left undefined makes its target fail with an explanation. It never succeeds
silently. `make help` shows which hooks are configured.

## Black-box tests

Each line of `test-inputs.txt` or `hidden-inputs.txt` is one invocation:

```text
<ID> [NAME=VALUE]... <tool> [ARG]... [< STDIN-FILE]
```

Arguments use POSIX shell quoting, but no shell is ever run. Consecutive lines with the same ID
are the steps of a single stateful test. `{PYTHON}` expands to a portable interpreter path, for
tests that need a child process. Each test runs in a fresh temporary copy of the fixtures
(`tests/fixtures/` merged with the suite's own `fixtures/`), with empty stdin and a minimal
environment.

```sh
python3 shared/tools/run-tests.py --bin-dir path/to/bin projects/02-cat/tests/public
```

**Hidden tests.** This repository is public, so `tests/private/` is hidden *by convention*.
Implementers design from the specifications and treat the public tests as the only tests they
have seen. CI runs both suites. If real secrecy is ever needed, move every `tests/private/`
directory into a private repository and have CI check it out using a token.

## Workflows

### Implementing the curriculum in a language repository

1. Create the repository from the organization's template repository (for example
   `dialectic-playground/rs`). Add this curriculum as a submodule pinned to a release tag,
   so specification changes arrive only when you choose to upgrade:

   ```sh
   git submodule add https://github.com/dialectic-playground/sdlc-curriculum
   git -C sdlc-curriculum checkout v1.6.0
   git add sdlc-curriculum && git commit -s -m "build: pin sdlc-curriculum to v1.6.0"
   ```

2. Lay the repository out as described in
   [`shared/templates/language/`](shared/templates/language/README.md): the root `Makefile`,
   and a copy of `projects/XX-slug/assignment/` as `XX-slug/` for every project (with
   `CURRICULUM_ROOT := ../sdlc-curriculum`). Base the `Containerfile` on the language's
   official image (pinned by digest), adding `make` and `python3`. To implement a project, set
   its `BIN_DIR` and `DP_*` hooks, then add it to `IMPLEMENTED` in the root `Makefile`.
3. Complete `hld.md` and `lld.md` **before** writing code (Principle 11). Then implement,
   write unit tests, and keep `rtm.md` and `master-test-plan.md` current.
4. Copy `shared/ci/cross-platform-ci.yml` to `.github/workflows/ci.yml` and add your native
   toolchain setup step. CI runs `make check`, so it needs no edits as projects are added.
5. A project is done when `make lint test test-hidden` passes in the container and natively on
   all three operating systems.

### Maintaining the curriculum

Container-first, like every repository: `make` targets and `tools/dp-run` run in the
toolchain image ([`Containerfile`](Containerfile): Python 3.12, `make`, `git`), using Podman,
then Docker, then the local system (`DP_RUNTIME` overrides the choice).

```sh
make check                                                  # everything CI checks
tools/dp-run python3 shared/tools/check-curriculum.py 04-wc # one project
make scaffold                                               # regenerate every assignment/
DP_RUNTIME=local make check                                 # natively, on your system
```

- **Changing a spec:** update the SRS and user manual first, then the model in `reference/`.
  Next, regenerate the fixtures with
  `run-tests.py --reference --update <suites>` and review the diff line by line.
- **The SRS is the authority.** `reference/` exists only to generate and verify the 1060
  fixtures and to show that every spec can be implemented on every OS. It is not a solution;
  see [`reference/README.md`](reference/README.md).
- **Adding a project:** add it to `curriculum.toml`, write the specs and tests following
  Project 00, add its reference model, scaffold its `assignment/`, and make
  `check-curriculum.py` pass.

## The 20 core engineering principles

Every implementation, in every language repository, must follow these principles:

1. **Follow Descriptive Naming Conventions:** Use descriptive names for variables, functions, and data types to make the code easy to understand.
2. **Use Comments Sparingly:** Comments should provide relevant and contextual information without being excessive in quantity.
3. **Keep Your Code DRY (Don’t Repeat Yourself):** Avoid code duplication by writing reusable functions and methods.
4. **Apply Unit Testing:** Use unit testing to ensure your code functions as intended.
5. **Maintain a Consistent Coding Style:** Adopt a consistent coding style throughout the project to facilitate collaboration and code readability.
6. **Handle Errors and Exceptions Appropriately:** Manage errors and exceptions properly to prevent crashes and unexpected issues.
7. **Document Your Code:** Provide clear documentation for public functions and data types using comments and standard documentation formats.
8. **Optimize Code Performance:** Write efficient and optimized code to ensure good performance.
9. **Exercise Caution with Security:** Validate and sanitize user inputs to prevent security vulnerabilities.
10. **Use Version Control:** Utilize version control systems to keep track of code revisions.
11. **Plan Before Programming:** Take the time to plan and design your solution before writing code. Good initial design saves time and effort later.
12. **Use Appropriate Data Structures:** Select the right data structures for the problem you’re solving. Don’t use a more complex structure than necessary.
13. **Keep Your Code Modular:** Divide your code into smaller modules or functions and focus on appropriate cohesion and coupling.
14. **Test in Different Scenarios:** Ensure your code is tested in various scenarios, including edge cases and error situations.
15. **Regularly Refactor Your Code:** Continuously review and improve your code to eliminate duplications, enhance efficiency, and keep it clean.
16. **Avoid the Use of Global Variables:** Minimize the use of global variables as they can make your code harder to understand and debug.
17. **Maintain a Record of Code Changes:** Document significant code changes, making it easier to understand its evolution.
18. **Follow the Single Responsibility Principle (SRP):** Each function or class should have a well-defined single responsibility.
19. **Consider Space and Time Efficiency:** In addition to time efficiency, also consider efficient memory usage in your code.
20. **Learn from Your Mistakes and Others:** Analyze past errors and other programmers’ code to learn and improve your skills.

## Versioning

Two version numbers are kept deliberately separate:

| Version | Where | Changes when |
| :-- | :-- | :-- |
| **Release** | Git tag `vMAJOR.MINOR.PATCH` ([releases](https://github.com/dialectic-playground/sdlc-curriculum/releases)) | Anything in the repository changes: specifications, tests, templates, or tooling |
| **Specification** | `spec_version` in `curriculum.toml`; printed by every tool's `--version` (CONV-02) | Specified tool behavior changes |

Release numbers follow these rules:

- **MAJOR:** specified behavior or test fixtures change in a way that can break a conforming
  implementation. `spec_version` changes too.
- **MINOR:** something is added (projects, tests, templates, or tooling) without breaking
  conforming implementations.
- **PATCH:** documentation or tooling fixes, with no change to specified behavior.

Language repositories pin a **release** tag. A new release that leaves `spec_version` unchanged
never requires implementation changes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for specification changes, fixtures, and new projects.
Organization-wide rules apply as well: squash merges, Conventional Commit pull request titles,
and DCO sign-off (see the
[organization CONTRIBUTING.md](https://github.com/dialectic-playground/.github/blob/main/CONTRIBUTING.md)).

## License

[MIT](LICENSE)
