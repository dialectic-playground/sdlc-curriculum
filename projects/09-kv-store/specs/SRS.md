# Software Requirements Specification (SRS) — dp-kv

| Field | Value |
| :-- | :-- |
| Document ID | SRS-09 |
| Project | `09-kv-store` — Local Key-Value Storage Engine (CLI + API) |
| Product | `dp-kv` (canonical name) |
| Version | 1.0.0 |
| Status | Approved (pre-written by the curriculum) |
| Parent document | `URD.md` (URD-09) |
| Incorporated by reference | `shared/CLI-CONVENTIONS.md` (CLI-CONV 1.0.0) |
| Structure | Adapted from ISO/IEC/IEEE 29148:2018 |

## 1. Introduction

### 1.1 Purpose
This SRS specifies the externally observable behavior of `dp-kv`. It is complete and precise
enough that independent implementations in any programming language produce **byte-identical**
command-line output and **byte-identical store files** for every invocation, and HTTP responses
whose status codes, headers named here, and bodies are identical. It is the authoritative source
for design (HLD/LLD), testing, and grading.

### 1.2 Scope
`dp-kv` keeps text values under keys in one local JSON file (the *store*). It offers commands to
set, get, delete, list, export, and import keys, and a `serve` command that exposes the same
store through a small HTTP/REST API on a local socket. Every change to the store is made under
an exclusive lock and written atomically and durably; readers take a shared lock.

### 1.3 Definitions

| Term | Definition |
| :-- | :-- |
| LF | The line-feed byte, `0x0A` |
| Store | The file at the store path PATH (FR-05) holding a dp-kv document (section 5) |
| Data | The set of key/value pairs held by a store |
| Lock file | The file whose name is PATH followed by `.lock` (string concatenation), used only for locking |
| Temporary file | The file whose name is PATH followed by `.tmp`, used only during a write (FR-21) |
| Key | A string satisfying FR-03 |
| Value | A string satisfying FR-04 |
| Byte-wise order | Ascending order of the UTF-8 encodings, compared byte by byte as unsigned numbers; a proper prefix sorts first (CONV-21). For keys, which are ASCII, this is ASCII order, so `Z` sorts before `a`. |
| Canonical document | The exact byte serialization of some data defined in section 5.1 |
| Valid document | A byte sequence that satisfies section 5.2 |
| Read-only command | `get`, `list`, `export` |
| Write command | `set`, `del`, `import` |
| Usage error | A CONV-13-style error: diagnostic, then the CONV-14 `Try` line, then exit status 2 |

### 1.4 References
- URD-09: `specs/URD.md`
- CLI-CONV: `shared/CLI-CONVENTIONS.md`
- User manual: `specs/user-manual.md` (contains the normative help text)
- RFC 8259 (JSON), RFC 3986 (URI), RFC 9110 (HTTP semantics), RFC 9112 (HTTP/1.1)
- POSIX `flock(2)`, `fsync(2)`, `rename(2)`; Win32 `LockFileEx`, `FlushFileBuffers`, `MoveFileExW`

### 1.5 Deviations from CLI-CONV
This SRS takes precedence over CLI-CONV for `dp-kv` in exactly these points:

1. **Command structure (refines CONV-07 … CONV-12).** The command line has two phases: global
   options, then a COMMAND word, then that command's options and operands (FR-01). Options and
   operands may be interleaved only *within* a phase; global options are not recognized after
   COMMAND, and command options are not recognized before it.
2. **Additional usage errors (extends CONV-13).** `missing command`, `unknown command '<word>'`,
   `invalid key '<key>'`, `value is not valid UTF-8`, and `value too long (maximum 65536 bytes)`
   are usage errors (exit status 2, followed by the CONV-14 line).
3. **Additional runtime reasons (extends CONV-16).** Besides the CONV-16 reasons, path
   diagnostics use `not a valid dp-kv store file` and `store is locked`. The diagnostics
   `key not found: <key>` and `<address>: cannot listen: <reason>` are not path diagnostics; the
   latter has its own fixed reason table (FR-23).
4. **Environment (CONV-06 clarification).** `dp-kv` reads the environment variable
   `DP_KV_STORE` (FR-05). It still ignores locale variables.
5. **Standard input (CONV-26).** Standard input is read only by `import -`.
6. **Informational standard-error line.** `serve` writes one non-error line,
   `dp-kv: listening on <url>`, to standard error (FR-22).
7. **Files created.** Besides the store, `dp-kv` creates the lock file (never removed) and,
   while writing, the temporary file (FR-20, FR-21).

## 2. Overall description

### 2.1 Product perspective
`dp-kv` is a standalone executable. Its interfaces are the command line, the environment
variable `DP_KV_STORE`, standard input (for `import -` only), standard output, standard error,
the exit status, the store file with its lock and temporary files, and — for `serve` only — a
TCP socket speaking HTTP/1.x. The store file format is itself an interface: files written by any
conforming implementation on any platform are byte-identical and interchangeable.

### 2.2 Product functions
1. Store, retrieve, and delete a value by key.
2. List keys in byte-wise order, optionally restricted to a prefix.
3. Export the store as a canonical document; import a document by merging or replacing.
4. Coordinate concurrent processes with shared/exclusive locks on a sidecar lock file.
5. Replace the store atomically and durably on every change.
6. Serve the store over a local HTTP/REST API.
7. Display help and version information; detect and report errors.

### 2.3 Constraints
- The tool MUST build and run on Linux, macOS, and Windows through the universal Makefile
  contract (`shared/templates/BASE-MAKEFILE`).
- The implementation language and toolchain are chosen by the implementing repository. This
  specification constrains only observable behavior and the locking/durability protocol
  (FR-20, FR-21, NFR-04, NFR-05), which other implementations must interoperate with.
- The store is held entirely in memory while a command runs.

### 2.4 Assumptions
- The store resides on a local file system that supports the platform locking primitive of
  NFR-04 and atomic rename within a directory.
- All processes that access a store follow the locking protocol of FR-20.
- The terminal or consumer accepts UTF-8.

## 3. External interface requirements

### 3.1 Command-line synopsis

```text
dp-kv [-s PATH | --store=PATH] set KEY VALUE
dp-kv [-s PATH | --store=PATH] get KEY
dp-kv [-s PATH | --store=PATH] del KEY
dp-kv [-s PATH | --store=PATH] list [-p PREFIX | --prefix=PREFIX]
dp-kv [-s PATH | --store=PATH] export
dp-kv [-s PATH | --store=PATH] import [-r | --replace] FILE
dp-kv [-s PATH | --store=PATH] serve [--host=ADDR] [--port=N]
dp-kv --help
dp-kv --version
```

### 3.2 Commands

| Command | Operands | Command options | Summary |
| :-- | :-- | :-- | :-- |
| `set` | KEY VALUE | — | Store VALUE under KEY (FR-06) |
| `get` | KEY | — | Print the value of KEY (FR-07) |
| `del` | KEY | — | Remove KEY (FR-08) |
| `list` | — | `-p`, `--prefix` | Print keys (FR-09) |
| `export` | — | — | Print the canonical document (FR-10) |
| `import` | FILE | `-r`, `--replace` | Merge or replace from a document (FR-11) |
| `serve` | — | `--host`, `--port` | Run the HTTP server (FR-22 … FR-33) |

Command words are case-sensitive and are not abbreviated.

### 3.3 Options

| Phase | Short | Long | Argument | Default | Description |
| :-- | :-- | :-- | :-- | :-- | :-- |
| global | `-s` | `--store` | PATH (required, non-empty) | see FR-05 | Use the store file PATH |
| global and command | — | `--help` | none | — | Print the help text and exit 0 (FR-12) |
| global and command | — | `--version` | none | — | Print the version line and exit 0 (FR-13) |
| `list` | `-p` | `--prefix` | PREFIX (required) | empty | Only keys that start with PREFIX |
| `import` | `-r` | `--replace` | none | merge | Replace the store contents instead of merging |
| `serve` | — | `--host` | ADDR (required) | `127.0.0.1` | IPv4 or IPv6 address to listen on |
| `serve` | — | `--port` | N (required) | `7700` | TCP port 0–65535; 0 lets the system choose |

Within a phase, option syntax (bundling, attached values, `--name=value`, `--`, repetition with
last-wins, and scan order) follows CONV-07 … CONV-12. For example, `-p user:` and `-puser:` are
equivalent, and `dp-kv -s a.json -s b.json list` uses `b.json`.

### 3.4 Operands
- KEY: a key (FR-03).
- VALUE: a value (FR-04). A VALUE that begins with `-` must follow a `--` terminator in the
  command phase (CONV-09), for example `dp-kv set -- k -5`.
- FILE: path of a document to import; `-` means standard input (CONV-10).

### 3.5 Environment

| Variable | Use |
| :-- | :-- |
| `DP_KV_STORE` | Store path when `--store` is not given and the variable is set to a non-empty value (FR-05) |

All other variables, including `LANG` and `LC_*`, are ignored (CONV-06).

### 3.6 Standard input
Read only by `import -`, which reads it to end of file (CONV-26).

### 3.7 Standard output

| Command | Standard output on success |
| :-- | :-- |
| `get` | The value's UTF-8 bytes followed by LF |
| `list` | Each selected key followed by LF, in byte-wise order; nothing if none is selected |
| `export` | The canonical document of the store's data (section 5.1) |
| `--help` / `--version` | The help text / version line |
| `set`, `del`, `import`, `serve` | Nothing |

Standard output is empty whenever the exit status is not 0.

### 3.8 Standard error
Diagnostics only (section 8), plus the single `listening` line written by `serve` (FR-22).

### 3.9 Files

| File | Created by | Content | Removed |
| :-- | :-- | :-- | :-- |
| PATH | First successful write command | Canonical document | Never by `dp-kv` |
| PATH`.lock` | Any command that accesses the store (FR-20) | Unspecified (normally empty) | Never |
| PATH`.tmp` | Write commands, during FR-21 | Next canonical document | Renamed to PATH, or deleted on failure |

### 3.10 Exit status

| Status | Condition |
| :-- | :-- |
| 0 | Success; `--help` / `--version` handled; `serve` stopped by a signal (FR-24) |
| 1 | Runtime failure: key not found, invalid store or import document, file error, lock timeout, cannot listen |
| 2 | Usage error |

## 4. Functional requirements

Each requirement gives an acceptance criterion (*AC*) and the user requirements it derives
from. Black-box test references use `P` for public and `H` for hidden tests.

**FR-01: Two-phase command line.**
Arguments are processed in two phases.
*Global phase:* tokens are scanned from the first argument per CONV-07 … CONV-12 with the global
options `-s`/`--store`, `--help`, and `--version`. The first operand ends the global phase and is
COMMAND. If `--` appears in the global phase, it is consumed and the token after it is COMMAND,
even if it begins with `-`.
*Command phase:* the tokens after COMMAND are scanned per CONV-07 … CONV-12 with that command's
options (section 3.3) plus `--help` and `--version`; options and operands may be interleaved, and
`--` ends option processing for this phase. Global options are not recognized in the command
phase (`dp-kv get k --store=x` reports `unrecognized option '--store=x'`), and an option of
another command is unrecognized (`dp-kv get --prefix=a k` reports
`unrecognized option '--prefix=a'`).
*AC:* `dp-kv --store=data.json list -p Z` lists `Zeta`; `dp-kv get alpha --store=data.json` is a
usage error (H09). *(UR-11, UR-17)*

**FR-02: Usage-check order.**
Usage errors are detected in the following order, and only the first one found is reported.
All of them are detected before any file is opened, any input is read, or any output is
written.
1. Global-phase scan (CONV-13 option errors; `--help`/`--version` end processing per CONV-12).
2. An empty `--store` value: `invalid argument '' for '<option>'` (`-s` or `--store` as
   written).
3. No COMMAND: `missing command`.
4. COMMAND is not one of the words in section 3.2: `unknown command '<COMMAND>'`.
5. Command-phase scan (CONV-13 option errors; `--help`/`--version` end processing).
6. Operand count: fewer operands than the command requires gives `missing operand`; more gives
   `extra operand '<first surplus operand>'`.
7. Option values, in this order: `--prefix` (FR-09), `--host`, `--port` (FR-22), each reported
   as `invalid argument '<value>' for '<option as written>'`.
8. KEY (FR-03): `invalid key '<KEY>'`.
9. VALUE (FR-04): `value is not valid UTF-8`, then `value too long (maximum 65536 bytes)`.

Each is followed by `Try 'dp-kv --help' for more information.` and exit status 2.
*AC:* `dp-kv` → `missing command`; `dp-kv --store=data.json frobnicate` → `unknown command
'frobnicate'` (P09); `dp-kv set onlykey` → `missing operand`; `dp-kv get a b` →
`extra operand 'b'`; `dp-kv --store= get a` → `invalid argument '' for '--store'` (H07).
*(UR-12, UR-17)*

**FR-03: Key rules.**
A key is a string of **1 to 256** characters, each from the set `A`–`Z`, `a`–`z`, `0`–`9`, `.`
(period), `_` (underscore), `:` (colon), and `-` (hyphen-minus). Keys are case-sensitive. A KEY
operand that is not a key is a usage error `invalid key '<KEY>'`, with KEY echoed exactly as
given (CONV-05, CONV-15).
*AC:* `dp-kv set 'bad key' value` → `dp-kv: invalid key 'bad key'`, exit 2 (P08); a 256-character
key is accepted and a 257-character key is rejected; `Zoë` is rejected; `-dash-` is accepted
after `--` (H08). *(UR-15, UR-12)*

**FR-04: Value rules.**
A value is any sequence of Unicode scalar values (any code point except the surrogates
U+D800–U+DFFF) whose UTF-8 encoding is at most **65536 bytes**. The empty string is a value.
Values may contain spaces, control characters, line breaks, and non-ASCII characters; they are
stored and printed exactly. On the command line, a VALUE operand whose bytes are not valid UTF-8
(POSIX), or which contains an unpaired UTF-16 surrogate (Windows), is a usage error
`value is not valid UTF-8`; a VALUE longer than 65536 bytes is a usage error
`value too long (maximum 65536 bytes)`.
*AC:* `dp-kv set empty ''` stores the empty string; `dp-kv set name 'Zoë Ångström'` followed by
`get name` prints the name exactly (H04, H08). *(UR-15)*

**FR-05: Store location.**
The store path PATH is the value of the last `--store`/`-s` option if one was given; otherwise
the value of the environment variable `DP_KV_STORE` if it is set and non-empty; otherwise the
literal relative path `kv.json`. PATH is used and echoed exactly as given (CONV-19); it is
resolved relative to the working directory. The lock file and temporary file names are formed
by appending `.lock` and `.tmp` to PATH as a string.
*AC:* with `DP_KV_STORE=env.json`, `dp-kv set colour blue` writes `env.json`; `--store=data.json`
overrides the variable; with the variable empty, `kv.json` is used (H06). *(UR-11)*

**FR-06: `set KEY VALUE`.**
Under an exclusive lock (FR-20), the tool loads the store (FR-15 … FR-18), sets KEY to VALUE
(adding or replacing), and writes the store (FR-21). It writes even if the value is unchanged.
Nothing is printed. If the store did not exist, it is created.
*AC:* on a new store, `set greeting 'Hello, World!'`, `get greeting`, and `export` print the
value and a one-key canonical document (P05); `set beta 'second value'` replaces `beta` (P06).
*(UR-01)*

**FR-07: `get KEY`.**
Under a shared lock, the tool loads the store and, if KEY is present, writes its value's UTF-8
bytes followed by one LF to standard output and exits 0. No other transformation is applied: a
value containing LF bytes prints on several lines, and a value that already ends in LF is
followed by a second LF. If KEY is absent, it reports `dp-kv: key not found: <KEY>` and exits 1.
*AC:* `dp-kv --store=data.json get alpha` → `first value\n` (P01); after `del beta`,
`get beta` → `dp-kv: key not found: beta`, exit 1 (P06). *(UR-02, UR-12)*

**FR-08: `del KEY`.**
Under an exclusive lock, the tool loads the store. If KEY is present, it removes it and writes
the store (FR-21); nothing is printed. If KEY is absent, it reports `dp-kv: key not found: <KEY>`,
exits 1, and does not write the store (a missing store therefore stays missing). Removing the
last key leaves a store whose data is empty; the file is not deleted.
*AC:* `del beta` then `get beta` → not found (P06); `del alpha` on a missing store → not found,
and the store is still missing (H01). *(UR-03, UR-12)*

**FR-09: `list [--prefix=PREFIX]`.**
PREFIX defaults to the empty string. A non-empty PREFIX MUST itself satisfy the key rules of
FR-03; otherwise it is a usage error `invalid argument '<PREFIX>' for '<option>'`. Under a shared
lock, the tool loads the store and writes every key that begins with PREFIX (case-sensitive,
character-by-character comparison), each followed by LF, in byte-wise order. If no key is
selected, nothing is written and the exit status is 0.
*AC:* `list` on `data.json` prints `Zeta`, `alpha`, `beta`, `config:theme`, `user:1001`,
`user:1002` in that order (P02); `list --prefix=user:` prints the last two (P03);
`list --prefix='user 1'` is a usage error (H09). *(UR-04)*

**FR-10: `export`.**
Under a shared lock, the tool loads the store and writes the canonical document (section 5.1) of
its data to standard output. If the store file is canonical, the output is byte-identical to it;
a valid but non-canonical store is exported in canonical form (the file itself is not
rewritten). A missing store exports the canonical empty document.
*AC:* `dp-kv --store=data.json export` is byte-identical to the fixture `data.json` (P04).
*(UR-05, UR-06)*

**FR-11: `import [--replace] FILE`.**
The tool reads FILE completely (standard input if FILE is `-`) *before* taking any lock. If
FILE cannot be read, it reports `dp-kv: <FILE>: <CONV-16 reason>`; if its bytes are not a valid
document (section 5.2), it reports `dp-kv: <FILE>: not a valid dp-kv store file`; in both cases
it exits 1 without touching the store. FILE is echoed as given; standard input is echoed as `-`.
Otherwise, under an exclusive lock, it loads the store (which MUST itself be valid or missing,
FR-17) and:
- **merge** (default): sets every key of the imported data to its imported value, adding new
  keys and replacing existing ones; keys not in FILE are kept;
- **replace** (`--replace`): makes the store's data exactly the imported data.

It then writes the store (FR-21), even if nothing changed. Nothing is printed.
*AC:* importing `import.json` into `data.json` replaces `beta` and adds `user:1003` (P07);
`import --replace - < import.json` leaves exactly the two imported keys (H03); a document with
`"version": 2`, a duplicate member name, or a 65537-byte value is rejected and the store is
unchanged (H05). *(UR-05, UR-13)*

**FR-12: Help.**
`--help`, whether reached in the global phase or the command phase, MUST write the help text
from user-manual §"Help output" byte-for-byte to standard output and exit 0, following the scan
order of CONV-12 within each phase. There is one help text for the whole tool.
*AC:* `dp-kv --help` (P10) and `dp-kv serve --help` (H10) print the help text and exit 0;
`dp-kv bogus --help` is `unknown command 'bogus'`, because COMMAND is reached first. *(UR-14)*

**FR-13: Version.**
`--version`, in either phase, MUST write `dp-kv (dialectic-playground) 1.0.0` + LF and exit 0
(CONV-02).
*AC:* `dp-kv get --version` → the version line (H10). *(UR-14)*

**FR-14: Canonical writes.**
Every time the tool writes the store, the file content MUST be exactly the canonical document
(section 5.1) of the new data, regardless of how the previous file was formatted.
*AC:* after `import` of a compact, unsorted document, `export` shows sorted, indented output, and
the store file has the same bytes (P07, H04). *(UR-06)*

**FR-15: Accepted store contents.**
When loading, the tool MUST accept any valid document (section 5.2), canonical or not, and MUST
treat any other content as invalid (FR-17).
*AC:* see FR-17. *(UR-06, UR-13)*

**FR-16: Missing store.**
If PATH does not exist, the store's data is empty. Read-only commands then succeed as for an
empty store and create no store file. If the lock file cannot be created because its directory
does not exist (or a path component is not a directory), a read-only command also treats the
store as empty. Write commands that change data create the store.
*AC:* on a missing store, `get alpha` → not found (1), `list` → nothing (0), `export` → the
canonical empty document (0); `--store=no-such-dir/kv.json list` → nothing (0); afterwards the
store file still does not exist (H01). *(UR-02, UR-04)*

**FR-17: Invalid store.**
If PATH exists, is not a directory, and its content is not a valid document, every command that
loads it (all commands except `serve`, `--help`, and `--version`) MUST report
`dp-kv: <PATH>: not a valid dp-kv store file` and exit 1. Write commands MUST NOT modify the
file in that case. An empty (0-byte) file is invalid.
*AC:* `get`, `set`, and `export` on `corrupt.json` each fail with that message, and `set` leaves
the file unchanged (H02). *(UR-13)*

**FR-18: File errors.**
File-system failures are reported as `dp-kv: <path>: <reason>` with a CONV-16 reason, exit 1:
- failing to open or create the lock file: `<path>` is PATH`.lock` (except the read-only case
  of FR-16);
- PATH is a directory: `dp-kv: <PATH>: Is a directory`;
- failing to read PATH, or any failure while writing the temporary file, flushing it, or
  renaming it over PATH (FR-21): `<path>` is PATH.

*AC:* `--store=sub get alpha`, where `sub` is a directory, → `dp-kv: sub: Is a directory`
(H02); `import nothere.json` → `dp-kv: nothere.json: No such file or directory` (H05).
*(UR-12)*

**FR-19: Failure atomicity.**
When a command exits with status 1 or 2, the store file MUST have the same content as before
the command, and standard output MUST be empty. A failed write leaves no temporary file behind
when it can be removed.
*AC:* after the failed imports of H05, `export` prints the original document. *(UR-07, UR-12)*

**FR-20: Locking protocol.**
Every command that loads the store first opens the lock file PATH`.lock` for reading and writing,
creating it if absent (permissions as created by the process, subject to the umask on POSIX),
and acquires on it:
- a **shared** lock for read-only commands and for HTTP `GET` requests;
- an **exclusive** lock for write commands and for HTTP `PUT` and `DELETE` requests.

The lock is acquired *before* PATH is opened and held until after PATH has been read and, for
writers, until after the rename of FR-21 has completed; then it is released and the lock file
is closed. The platform primitives are fixed by NFR-04 so that different implementations
exclude each other. If the lock cannot be acquired immediately, the tool MUST retry at intervals
of at most 50 ms; if it is still not acquired **5 seconds** after the first attempt, the command
fails with `dp-kv: <PATH>: store is locked` and exit 1 (HTTP: 503, FR-32). The lock file is never
deleted (deleting it would let two processes lock different files).
*AC:* integration tests IT-01, IT-02, IT-04 (section 9). *(UR-08)*

**FR-21: Atomic, durable replacement.**
To write the store, a writer holding the exclusive lock MUST:
1. create or truncate the temporary file PATH`.tmp` (same directory as PATH), write the complete
   canonical document to it, and flush it to stable storage (`fsync` on POSIX, `F_FULLFSYNC`
   SHOULD be used on macOS, `FlushFileBuffers` on Windows);
2. on POSIX, if PATH exists, give the temporary file the permission bits of PATH (SHOULD);
3. close it and atomically rename it over PATH (`rename` on POSIX; `MoveFileExW` with
   `MOVEFILE_REPLACE_EXISTING`, and SHOULD add `MOVEFILE_WRITE_THROUGH`, on Windows);
4. on POSIX, SHOULD `fsync` the directory containing PATH so the rename is durable.

PATH MUST never be opened for writing in place. If any step fails, the writer deletes the
temporary file if possible, leaves PATH untouched, and reports the error (FR-18). A temporary
file left by a crashed writer is simply overwritten by the next writer.
*AC:* integration test IT-03 (section 9). *(UR-07)*

**FR-22: `serve` options and startup.**
ADDR MUST be a numeric IPv4 address in dotted-decimal form (four decimal numbers 0–255 without
leading zeros) or a numeric IPv6 address in RFC 4291 text form, without a zone identifier (`%`);
host names, including `localhost`, are rejected. N MUST consist only of ASCII digits and have a
value from 0 to 65535 (leading zeros allowed). Invalid values are usage errors
`invalid argument '<value>' for '<option>'` (FR-02 step 7). The default is `127.0.0.1` port
`7700`; the server MUST NOT listen on any non-loopback address unless `--host` names one.
After the listening socket is bound and listening, and before serving any request, `serve`
writes exactly one line to standard error and flushes it:

```text
dp-kv: listening on http://<ADDR>:<PORT>
```

where `<ADDR>` is ADDR as given (enclosed in `[` `]` if it is an IPv6 address) and `<PORT>` is
the actual bound port in decimal (the system-chosen port when N is 0). `serve` does not read the
store at startup; store errors are reported per request (FR-32). Nothing is ever written to
standard output.
*AC:* `serve --port=65536` and `serve --host=localhost` are usage errors (H10); `serve --port=0`
prints a line with a non-zero port that accepts connections (IT-06). *(UR-09, UR-10)*

**FR-23: Listen failure.**
If the socket cannot be created, bound, or put into the listening state, `serve` reports
`dp-kv: <ADDR>:<N>: cannot listen: <reason>` (IPv6 ADDR in brackets; N as requested) and exits
1. `<reason>` is `Address already in use` (EADDRINUSE / WSAEADDRINUSE), `Permission denied`
(EACCES / WSAEACCES), or `Address not available` (any other failure).
*AC:* starting a second server on the port of a running one → `Address already in use`, exit 1
(IT-06). *(UR-12)*

**FR-24: Shutdown.**
`serve` runs until it receives SIGINT or SIGTERM (POSIX) or a Ctrl+C or Ctrl+Break console event
(Windows). It then stops accepting connections, closes the listening socket, and exits with
status 0 without writing anything further. Requests in progress either complete or are aborted;
in both cases the store remains valid (FR-21).
*AC:* SIGTERM / Ctrl+Break → exit 0 (IT-06). *(UR-09)*

**FR-25: HTTP message conventions.**
The server MUST implement section 6.2: response status line and headers, JSON bodies, and
connection handling.
*AC:* IT-05. *(UR-09)*

**FR-26: Routing and methods.**
The server MUST route requests per section 6.3, including `404 not_found` for unknown paths and
`405 method_not_allowed` with an `Allow` header for unsupported methods on known paths.
*AC:* IT-05. *(UR-09)*

**FR-27: `GET /v1/health`.**
MUST return `200` with body `{"status":"ok"}` without accessing the store.
*AC:* IT-05. *(UR-09)*

**FR-28: `GET /v1/keys`.**
MUST return `200` with body `{"keys":[...]}` listing, in byte-wise order, the keys that begin
with the `prefix` query parameter (section 6.3), under a shared lock; an invalid prefix gives
`400 invalid_prefix`.
*AC:* IT-05. *(UR-04, UR-09)*

**FR-29: `GET /v1/keys/{key}`.**
MUST return `200` with body `{"key":K,"value":V}` under a shared lock, or `404 key_not_found`.
*AC:* IT-05, IT-07. *(UR-02, UR-09)*

**FR-30: `PUT /v1/keys/{key}`.**
MUST validate the request body (section 6.3), set the key under an exclusive lock with FR-21
durability, and return `201` (key was absent; with a `Location` header) or `200` (key replaced),
with body `{"key":K,"value":V}`.
*AC:* IT-05, IT-07. *(UR-01, UR-09)*

**FR-31: `DELETE /v1/keys/{key}`.**
MUST remove the key under an exclusive lock and return `204` with no body, or `404
key_not_found` without writing the store.
*AC:* IT-05. *(UR-03, UR-09)*

**FR-32: HTTP errors and precedence.**
Error responses MUST use the JSON error shape, codes, statuses, and messages of section 6.4,
and the checks MUST be applied in the order given there.
*AC:* IT-05. *(UR-09, UR-12, UR-13)*

**FR-33: Request limits and logging.**
The server MUST reject request bodies declared larger than 524288 bytes without reading them
(`413 payload_too_large`), MUST close a connection on which no complete request arrives within
10 seconds of the last byte received, and MUST NOT write per-request log lines (standard error
carries only the FR-22 line).
*AC:* IT-05. *(UR-10)*

## 5. Store document format

### 5.1 Canonical document (written)
The canonical document of some data is the UTF-8 encoding (no byte-order mark) of the following
text, in which every line ends with a single LF, including the last:

```text
{
  "format": "dp-kv",
  "version": 1,
  "data": {
    "<key 1>": "<value 1>",
    "<key 2>": "<value 2>"
  }
}
```

Exact rules:
1. Line 1 is `{`. Line 2 is two spaces and `"format": "dp-kv",`. Line 3 is two spaces and
   `"version": 1,`.
2. If the data is empty, line 4 is two spaces and `"data": {}`, followed by the line `}`.
3. Otherwise line 4 is two spaces and `"data": {`, followed by one line per key in byte-wise key
   order: four spaces, the key as a JSON string, `: ` (colon, space), the value as a JSON string,
   and a `,` on every entry line except the last. Then the line `  }` (two spaces, `}`) and the
   line `}`.
4. A *JSON string* is `"`, the encoded characters, and `"`. Characters are encoded as follows,
   and in no other way:

| Character | Encoding |
| :-- | :-- |
| `"` (U+0022) | `\"` |
| `\` (U+005C) | `\\` |
| U+0008, U+000C, U+000A, U+000D, U+0009 | `\b`, `\f`, `\n`, `\r`, `\t` |
| Other U+0000 … U+001F | `\u` followed by 4 **lowercase** hexadecimal digits, e.g. `\u0007` |
| Every other character, including `/`, U+007F, non-ASCII, U+2028, U+2029 | Itself, as UTF-8 |

There is no other whitespace. Example (the public fixture `data.json`):

```text
{
  "format": "dp-kv",
  "version": 1,
  "data": {
    "Zeta": "uppercase sorts first",
    "alpha": "first value",
    "beta": "2",
    "config:theme": "dark",
    "user:1001": "Ada Lovelace",
    "user:1002": "Zoë Ångström"
  }
}
```

The canonical empty document is the five lines `{`, `  "format": "dp-kv",`, `  "version": 1,`,
`  "data": {}`, `}`.

### 5.2 Valid document (accepted)
A byte sequence is a valid document if and only if all of the following hold:
1. It is well-formed UTF-8. A leading byte-order mark makes it invalid.
2. Its text is exactly one JSON value per RFC 8259, optionally surrounded by JSON whitespace
   (space, tab, LF, CR). Non-standard extensions are invalid: comments, trailing commas,
   single-quoted strings, `NaN`, `Infinity`, unescaped control characters in strings.
3. No JSON object anywhere in it has two members with the same name.
4. The value is an object with exactly three members, in any order: `"format"`, whose value is
   the string `"dp-kv"`; `"version"`, whose value is the number written as the integer `1`
   (no fraction or exponent, so `1.0` and `1e0` are invalid); and `"data"`, whose value is an
   object.
5. Every member name of `data` is a key (FR-03), and every member value is a JSON string that
   decodes to a value (FR-04). An escaped unpaired surrogate such as `\ud800` makes the string
   invalid; escaped surrogate pairs such as `😀` denote one character.

The same rules apply to the store file (FR-15) and to imported files (FR-11).

## 6. HTTP interface (`serve`)

### 6.1 Overview
The server speaks HTTP/1.0 and HTTP/1.1 (RFC 9112) over TCP, without TLS and without
authentication. It MAY process requests concurrently; each request takes its own lock (FR-20)
so it is atomic with respect to the CLI and to other requests.

### 6.2 Message conventions
1. Every response carries `Content-Length`, and `Connection: close`; the server closes the
   connection after sending the response. Persistent connections and chunked responses are not
   used. The status line's HTTP version and reason phrase are not significant.
2. Every response that has a body carries `Content-Type: application/json; charset=utf-8`. The
   body is the *compact JSON* of the response object followed by one LF. Compact JSON has no
   whitespace outside strings, lists object members in the order shown in this section, and
   encodes strings exactly as in section 5.1 rule 4.
3. A `204` response, and every response to a `HEAD` request, has no body (the `HEAD` response
   still carries the `Content-Length` of the body it omits).
4. Requests are not required to send `Content-Type`; request bodies are decoded per FR-30
   regardless of it. Request bodies of methods other than `PUT` are ignored.
5. A request that is not well-formed HTTP/1.x (bad request line, unsupported HTTP version,
   oversized header) is answered with the status the HTTP parser chooses (400, 414, 431, or
   505) and the error body with code `bad_request`.

### 6.3 Resources
The request target is split at the first `?` into *path* and *query*. Routes are matched on the
path exactly as received (before percent-decoding):

| Path | Methods (`Allow` value) | Behavior |
| :-- | :-- | :-- |
| `/v1/health` | `GET` | `200`, `{"status":"ok"}` |
| `/v1/keys` | `GET` | `200`, `{"keys":["<key>",...]}` (empty list `[]` if none) |
| `/v1/keys/` followed by the key segment | `GET, PUT, DELETE` | See below |
| anything else | — | `404 not_found` |

- **Key segment.** Everything after `/v1/keys/` is percent-decoded once (`%XX` → byte; `+` is not
  special) and the bytes are decoded as UTF-8. If decoding fails, or the result is not a key
  (FR-03) — for example because it is empty or contains `/` — the response is
  `400 invalid_key`.
- **Prefix.** The query is decoded as `application/x-www-form-urlencoded`: split at `&`, each
  part split at the first `=` (a part without `=` has an empty value), `+` means space, and
  percent-escapes are decoded as UTF-8 (invalid sequences become U+FFFD). Only the parameter
  `prefix` is used; if it appears several times, the last occurrence wins; other parameters are
  ignored. A missing or empty `prefix` selects every key; a non-empty prefix that is not a key
  is `400 invalid_prefix`. The query is ignored on other routes.
- **GET key:** `200`, `{"key":"<key>","value":"<value>"}` or `404 key_not_found`.
- **PUT key:** the request MUST carry `Content-Length` consisting only of ASCII digits; the body
  is that many bytes and MUST be a valid JSON text (section 5.2 rules 1–3) whose value is an
  object with exactly one member, `"value"`, whose value is a JSON string that decodes to a
  value (FR-04). On success: `201` with header `Location: /v1/keys/<key>` if the key did not
  exist, `200` if it was replaced; body `{"key":"<key>","value":"<value>"}` in both cases.
- **DELETE key:** `204` with no body, or `404 key_not_found`.
- Any other method on a known path (including `HEAD`, `POST`, `PATCH`, `OPTIONS`, and unknown
  method names) is `405 method_not_allowed` with the `Allow` header of the table.

### 6.4 Errors
An error response body is `{"error":{"code":"<code>","message":"<message>"}}`:

| Status | Code | Message |
| :-- | :-- | :-- |
| 400 | `bad_request` | `malformed HTTP request` |
| 400 | `invalid_key` | `invalid key` |
| 400 | `invalid_prefix` | `invalid prefix` |
| 400 | `invalid_json` | `request body is not valid JSON` |
| 400 | `invalid_body` | `request body must be a JSON object with exactly one member, "value", whose value is a string` |
| 404 | `key_not_found` | `key not found: <key>` |
| 404 | `not_found` | `resource not found` |
| 405 | `method_not_allowed` | `method not allowed` |
| 411 | `length_required` | `Content-Length header required` |
| 413 | `payload_too_large` | `request body too large (maximum 524288 bytes)` |
| 413 | `value_too_long` | `value too long (maximum 65536 bytes)` |
| 500 | `store_error` | `<path>: <reason>` — the FR-17/FR-18 diagnostic without the `dp-kv: ` prefix |
| 503 | `store_locked` | `<PATH>: store is locked` |

The `invalid_body` message contains two `"` characters, encoded as `\"` in the body. Checks are
applied in this order, and the first failing check determines the response:
1. route (`404 not_found`); 2. method (`405`); 3. key segment (`400 invalid_key`) or, for
`/v1/keys`, prefix (`400 invalid_prefix`); 4. for `PUT`: missing or non-numeric
`Content-Length` (`411`), declared length above 524288 (`413 payload_too_large`, body not read),
body not valid JSON (`400 invalid_json`), body not an object with exactly one string member
`value`, or that string containing an unpaired surrogate (`400 invalid_body`), value longer than
65536 bytes (`413 value_too_long`); 5. lock timeout (`503`); 6. store errors (`500`); 7. key absent
for `GET`/`DELETE` (`404 key_not_found`).

## 7. Non-functional requirements

| ID | Category | Requirement | Verification |
| :-- | :-- | :-- | :-- |
| NFR-01 | Portability | CLI output and store files MUST be byte-identical on Linux, macOS, and Windows, and every generated line MUST end in LF only (CONV-03). | CI black-box tests on 3 OSes |
| NFR-02 | Performance | With a store of 10,000 keys of 100-byte values, every CLI command except `serve` MUST complete in under 200 ms (natively compiled) or 500 ms (interpreted runtime) on CI hardware, and an HTTP request MUST be answered in under 100 ms. Peak memory MUST stay under 32 MiB plus 4 times the store file size. | Measurement (IT-08) |
| NFR-03 | Durability | After a write command exits 0, or an HTTP write returns 2xx, the new contents MUST survive a process crash or power loss (FR-21 flush and rename). At every instant PATH MUST name either the complete previous document or the complete new one. | Integration test IT-03 |
| NFR-04 | Concurrency (cross-platform focus) | Locks MUST use these primitives so that all implementations interoperate. **POSIX (Linux, macOS):** `flock(2)` on the lock file's descriptor, `LOCK_SH` or `LOCK_EX`, polled with `LOCK_NB`, released with `LOCK_UN` or by closing. `fcntl(2)` record locks (`F_SETLK`, `lockf`) MUST NOT be used: they do not exclude `flock` locks and are dropped when the process closes *any* descriptor of the file. **Windows:** `LockFileEx` on the lock file's handle covering offset 0, length 1 byte (`nNumberOfBytesToLockLow` = 1, `High` = 0), with `LOCKFILE_EXCLUSIVE_LOCK` for exclusive locks and without it for shared locks, polled with `LOCKFILE_FAIL_IMMEDIATELY`, released with `UnlockFileEx` or by closing the handle. With 8 concurrent writer processes, no update may be lost and no reader may observe a partially written store. | Integration tests IT-01, IT-02, IT-04 |
| NFR-05 | Portability (Windows file semantics) | Because Windows cannot rename over a file that another process holds open without `FILE_SHARE_DELETE`, the store MUST be opened only while the lock is held, and closed before the lock is released; the writer's rename happens while it holds the exclusive lock, so no conforming reader has PATH open. | Integration test IT-02 on Windows |
| NFR-06 | Security | `serve` MUST bind to `127.0.0.1` unless `--host` is given. It MUST NOT serve files, follow paths from requests, or run programs. On POSIX it SHOULD set `SO_REUSEADDR`; on Windows it MUST NOT set `SO_REUSEADDR` (which there allows another process to steal the port) and SHOULD set `SO_EXCLUSIVEADDRUSE`. Request bodies and idle connections are bounded (FR-33). | Inspection, IT-06 |
| NFR-07 | Robustness | The tool MUST NOT crash, panic, or print a stack trace for any argument list, store content, import file, or HTTP request (CONV-24). A failing HTTP request MUST NOT stop the server. | Unit, black-box, and integration tests |
| NFR-08 | Maintainability | The storage engine (document codec, key/value rules, locking, atomic write) MUST be one unit used by both the CLI and the HTTP front end; argument parsing, command logic, and HTTP routing MUST be separate units (Principles 13, 18). | Design review |
| NFR-09 | Testability | The document encoder and validator MUST be pure functions with unit tests covering every rule of section 5; the locking and atomic-write code MUST be covered by the integration tests of section 9. | Code review |
| NFR-10 | Build | Every BASE-MAKEFILE target MUST work: `all install uninstall test check lint format clean distclean`. | CI |

## 8. Diagnostics (complete list)

All diagnostics go to standard error as one line starting `dp-kv: `.

**Usage errors** — each is followed by `Try 'dp-kv --help' for more information.` and exit
status 2:

| Trigger | Exact first line |
| :-- | :-- |
| Unknown short option `x` (either phase) | `dp-kv: invalid option -- 'x'` |
| Unknown long option token `T` (either phase, including a global option after COMMAND) | `dp-kv: unrecognized option 'T'` |
| `-s` / `-p` without an argument | `dp-kv: option requires an argument -- 's'` (or `'p'`) |
| `--store` / `--prefix` / `--host` / `--port` without an argument | `dp-kv: option '--store' requires an argument` (or the other name) |
| `--help=…` / `--version=…` / `--replace=…` | `dp-kv: option '--help' doesn't allow an argument` (or the other name) |
| Empty PATH | `dp-kv: invalid argument '' for '--store'` (or `'-s'`) |
| No COMMAND | `dp-kv: missing command` |
| Unknown COMMAND `W` | `dp-kv: unknown command 'W'` |
| Too few operands | `dp-kv: missing operand` |
| Surplus operand `X` | `dp-kv: extra operand 'X'` |
| Invalid PREFIX `P` | `dp-kv: invalid argument 'P' for '--prefix'` (or `'-p'`) |
| Invalid ADDR `A` | `dp-kv: invalid argument 'A' for '--host'` |
| Invalid port `N` | `dp-kv: invalid argument 'N' for '--port'` |
| Invalid KEY `K` | `dp-kv: invalid key 'K'` |
| VALUE not valid UTF-8 | `dp-kv: value is not valid UTF-8` |
| VALUE longer than 65536 bytes | `dp-kv: value too long (maximum 65536 bytes)` |

**Runtime errors** — exit status 1, no `Try` line:

| Trigger | Exact line |
| :-- | :-- |
| `get` / `del` of an absent KEY | `dp-kv: key not found: <KEY>` |
| Store content invalid | `dp-kv: <PATH>: not a valid dp-kv store file` |
| Import document invalid | `dp-kv: <FILE>: not a valid dp-kv store file` |
| Lock not acquired within 5 s | `dp-kv: <PATH>: store is locked` |
| PATH is a directory | `dp-kv: <PATH>: Is a directory` |
| Store read or write failure | `dp-kv: <PATH>: <CONV-16 reason>` |
| Lock file cannot be opened or created | `dp-kv: <PATH>.lock: <CONV-16 reason>` |
| Import FILE cannot be read | `dp-kv: <FILE>: <CONV-16 reason>` |
| `serve` cannot listen | `dp-kv: <ADDR>:<N>: cannot listen: <reason>` (FR-23) |

**Informational** — not an error:

| Trigger | Exact line |
| :-- | :-- |
| `serve` is listening | `dp-kv: listening on http://<ADDR>:<PORT>` (FR-22) |

## 9. Verification

| Method | Applies to |
| :-- | :-- |
| Black-box test (public, `tests/public/`, 10 cases) | FR-01 … FR-12, FR-14, FR-15 |
| Black-box test (hidden, `tests/private/`, 10 cases) | FR-01 … FR-19, FR-22 (usage part) |
| Integration test (written by the implementer; see below) | FR-20, FR-21, FR-22 … FR-33, NFR-02 … NFR-06 |
| Unit test (written by the implementer) | FR-03, FR-04, FR-09, section 5, NFR-09 |
| Inspection / review | NFR-06, NFR-08 |

The black-box harness runs one process per step and cannot hold locks, interrupt writes, or
talk to a server, so the following **integration tests** are mandatory deliverables of the
implementation's master test plan. Each MUST run on Linux, macOS, and Windows in CI:

| ID | Integration test | Verifies |
| :-- | :-- | :-- |
| IT-01 | Start 8 processes at once, each running 25 `set` commands on distinct keys of one store; afterwards `list` shows all 200 keys and the file is canonical. | FR-20, NFR-04 |
| IT-02 | While 4 processes repeatedly `set`, 4 processes repeatedly `export` (and issue HTTP `GET /v1/keys`); every output is a valid canonical document / response, and no command fails. | FR-20, NFR-04, NFR-05 |
| IT-03 | Repeatedly start a writer on a large store and kill it (SIGKILL / `TerminateProcess`) at random moments; after each kill the store is valid and equals either the old or the new data; a stale PATH`.tmp` does not prevent the next write. | FR-19, FR-21, NFR-03 |
| IT-04 | A helper process holds an exclusive lock on PATH`.lock` using the NFR-04 primitive: `get` and `set` each fail after about 5 s with `store is locked`, exit 1. Holding a shared lock instead: `get` succeeds, `set` fails. Releasing the lock within 5 s lets a waiting `set` succeed. | FR-20, NFR-04 |
| IT-05 | Exercise every row of sections 6.3 and 6.4 (including the precedence order, `HEAD`, an unknown method, a 524289-byte declared body, and a store file made invalid while serving), checking status, `Content-Type`, `Content-Length`, `Allow`, `Location`, and exact bodies. | FR-25 … FR-33 |
| IT-06 | `serve --port=0` prints the listening line with the real port; a second `serve` on that port fails with `Address already in use`; SIGTERM (POSIX) / Ctrl+Break (Windows) stops the server with exit 0; the default bind address is `127.0.0.1`. | FR-22, FR-23, FR-24, NFR-06 |
| IT-07 | With a server running, a value written by HTTP `PUT` is read by CLI `get`, and a CLI `set` is seen by HTTP `GET`. | FR-20, FR-29, FR-30 |
| IT-08 | Time each command against a 10,000-key store and record peak memory. | NFR-02 |

Public test map (fixtures: `tests/fixtures/data.json` is the canonical document shown in
section 5.1; `tests/fixtures/import.json` is a compact, unsorted document with keys `user:1003`
and `beta`):

| Test | Command(s) | Verifies |
| :-- | :-- | :-- |
| 01 | `dp-kv --store=data.json get alpha` | FR-07 |
| 02 | `dp-kv --store=data.json list` | FR-09 (byte-wise order) |
| 03 | `dp-kv --store=data.json list --prefix=user:` | FR-09 |
| 04 | `dp-kv --store=data.json export` | FR-10, section 5.1 |
| 05 | `set greeting 'Hello, World!'`; `get greeting`; `export` on new `new.json` | FR-06, FR-14, FR-16 |
| 06 | `set beta 'second value'`; `get beta`; `del beta`; `get beta` | FR-06, FR-07, FR-08 |
| 07 | `import import.json`; `export` | FR-11 (merge), FR-14, FR-15 |
| 08 | `dp-kv --store=data.json set 'bad key' value` | FR-03, FR-02 |
| 09 | `dp-kv --store=data.json frobnicate` | FR-02 |
| 10 | `dp-kv --help` | FR-12 |

## 10. Traceability (URD → SRS)

| User requirement | System requirements |
| :-- | :-- |
| UR-01 | FR-06, FR-30 |
| UR-02 | FR-07, FR-16, FR-29 |
| UR-03 | FR-08, FR-31 |
| UR-04 | FR-09, FR-16, FR-28 |
| UR-05 | FR-10, FR-11 |
| UR-06 | FR-10, FR-14, FR-15, section 5, NFR-01 |
| UR-07 | FR-19, FR-21, NFR-03 |
| UR-08 | FR-20, NFR-04, NFR-05 |
| UR-09 | FR-22, FR-24 … FR-31, section 6 |
| UR-10 | FR-22, FR-33, NFR-06 |
| UR-11 | FR-01, FR-05 |
| UR-12 | FR-02, FR-03, FR-07, FR-08, FR-18, FR-19, FR-23, FR-32, section 8 |
| UR-13 | FR-11, FR-15, FR-17, FR-32 |
| UR-14 | FR-12, FR-13 |
| UR-15 | FR-03, FR-04 |
| UR-16 | NFR-01, CONV-03 |
| UR-17 | FR-01, FR-02, CLI-CONV, section 1.5 |
| UR-18 | NFR-02 |
| UR-19 | NFR-10 |
