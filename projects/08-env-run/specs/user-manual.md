# dp-env — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-env` 1.0.0 |
| Project | `08-env-run` — Environment Execution Wrapper |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-08), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-env** — run a command in a modified environment, or print the environment

## SYNOPSIS

```text
dp-env [OPTION]... [-] [NAME=VALUE]... [COMMAND [ARG]...]
dp-env --help
dp-env --version
```

## DESCRIPTION

`dp-env` builds an environment and then either runs *COMMAND* with it or, when no command is
given, prints it.

The environment is built in three steps:

1. Start from the environment `dp-env` itself received or, with `-i` (or a lone `-`), from an
   empty one.
2. Remove every variable named with `-u`.
3. Apply each *NAME*`=`*VALUE* assignment from left to right. An assignment adds the variable
   or replaces its value, and a later assignment to the same name wins. An empty *VALUE* sets
   the variable to the empty string; it does not remove it.

**Printing.** Without *COMMAND*, `dp-env` writes one `NAME=VALUE` entry per line, followed by
a line feed (LF), even on Windows. Entries are sorted by name in byte order, so upper-case
letters come before lower-case ones (`A`, `C`, `b`) whatever your locale. With `-0`, each
entry ends with a NUL byte instead, which keeps the output unambiguous when values contain line
feeds.

**Running a command.** With *COMMAND*, `dp-env` starts it directly, never through a shell,
and passes the *ARG*s unchanged. The command inherits `dp-env`'s standard input, output, and
error. `dp-env` waits for the command to finish and then exits with the command's exit
status, so `dp-env` can be put in front of any command without changing how scripts see its
result.

**Finding the command.** If *COMMAND* contains a path separator (`/`, or on Windows also `\`
or a drive prefix such as `C:`), it is used as a path. Otherwise `dp-env` searches the
directories in `PATH`. It uses the `PATH` of the new environment if that has one, and
otherwise its own `PATH`. So `dp-env -i PATH=/opt/tools/bin mytool` searches only
`/opt/tools/bin`, while `dp-env -i mytool` still finds `mytool` through your normal search
path. Empty `PATH` elements are skipped, and the current directory is never searched unless
`PATH` lists it explicitly. Use `./mytool` to run a program in the current directory.

**Where options end.** Options are recognized only before the first operand. Everything from
the first assignment or the command onwards belongs to the environment or to the command. For
example, in `dp-env FOO=1 ls -l`, the `-l` is passed to `ls`. `--` ends the options
explicitly.

**Signals.** While the command runs, `dp-env` stays in the foreground. On Linux and macOS,
when `dp-env` receives SIGINT, SIGTERM, or SIGHUP, it passes the signal on to the command and
keeps waiting. A supervisor that stops `dp-env` therefore stops the real program, and no
orphan is left behind. If `dp-env` was started with one of these signals ignored (for example,
under `nohup`), the signal stays ignored for both. On Windows, Ctrl+C and Ctrl+Break reach the
command directly through the console. `dp-env` ignores them and waits for the command to
finish.

An operand containing `=` before the command is always taken as an assignment, so `dp-env`
cannot run a program whose name contains `=`.

## OPTIONS

**`-i`, `--ignore-environment`**
: Start from an empty environment. Only variables assigned on the command line are set. A lone
  `-` as the first operand has the same effect.

**`-u NAME`, `--unset=NAME`**
: Remove the variable *NAME*. This option may be given several times, and every occurrence
  applies. Removing a variable that is not set is not an error. *NAME* must not be empty and
  must not contain `=`.

**`-C DIR`, `--chdir=DIR`**
: Run *COMMAND* with *DIR* as its working directory. The change happens before the command is
  looked up, so a relative command path such as `../tool` is relative to *DIR*. This option
  requires a *COMMAND*.

**`-0`, `--null`**
: When printing the environment, end each entry with a NUL byte instead of a line feed. This
  option cannot be combined with a *COMMAND*.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-env` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`), with the
differences below:

- An option's value can be attached or separate: `-uFOO`, `-u FOO`, `--unset=FOO`, and
  `--unset FOO` are equivalent. Flags can be combined: `-iu FOO`.
- Long options must be spelled out in full; `--unse` is not accepted.
- **Options end at the first operand.** `dp-env A=1 -i` runs a program called `-i`.
- A lone `-` as the first operand means `-i`, as in POSIX `env`.
- Unlike other curriculum tools, `-u` is cumulative. For `-C`, the last occurrence wins.
- `--help` and `--version` take effect when they appear among the options, unless an earlier
  option is malformed.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | The environment, help, or version was printed |
| 125 | `dp-env` itself failed: invalid usage, an invalid name, or a `-C` directory that cannot be entered |
| 126 | The command was found but could not be run (for example, no execute permission, or a directory) |
| 127 | The command was not found |
| *other* | The exit status of the command itself |
| 128 + *N* | Linux and macOS: the command was killed by signal *N* (for example, 143 for SIGTERM) |

A command may itself exit with 125, 126, or 127. When that matters, check standard error:
`dp-env` prints a diagnostic whenever it produces one of these statuses itself.

Usage errors exit with 125, not 2 as in the other curriculum tools. A wrapper must not
produce a status that the wrapped command could also produce in normal use.

## DIAGNOSTICS

Errors are written to standard error, and nothing is written to standard output. Usage errors
are followed by a hint line:

```text
$ dp-env --chdir
dp-env: option '--chdir' requires an argument
Try 'dp-env --help' for more information.
```

Errors about names, directories, and commands are a single line:

```text
$ dp-env pyhton script.py
dp-env: 'pyhton': No such file or directory
```

| Message | Cause | Status |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | 125 |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | 125 |
| `option requires an argument -- 'u'` | `-u` or `-C` without a value | 125 |
| `option '--unset' requires an argument` | `--unset` or `--chdir` without a value | 125 |
| `option '--null' doesn't allow an argument` | `--null=…`, `--ignore-environment=…`, `--help=…`, or `--version=…` | 125 |
| `cannot specify --null (-0) with command` | `-0` given together with a command | 125 |
| `must specify command with --chdir (-C)` | `-C` given without a command | 125 |
| `cannot unset 'A=B': Invalid argument` | `-u` name empty or containing `=` | 125 |
| `cannot set '=x': Invalid argument` | Assignment with an empty name | 125 |
| `cannot change directory to 'DIR': No such file or directory` | `-C` directory missing (other reasons: `Not a directory`, `Permission denied`, `Input/output error`) | 125 |
| `write error` | Standard output could not be written | 125 |
| `'cmd': Is a directory` | The command path names a directory | 126 |
| `'cmd': Permission denied` | The file is not executable or access is refused | 126 |
| `'cmd': Exec format error` | The file is not a valid program (a script needs a `#!` line) | 126 |
| `'cmd': No such file or directory` | The command does not exist, or not in any `PATH` directory | 127 |

## EXAMPLES

Run a command with one extra variable:

```text
$ dp-env GREETING=hello sh -c 'echo "$GREETING, world"'
hello, world
```

Print a clean, sorted environment:

```text
$ dp-env -i TZ=UTC LANG=C.UTF-8 lower=last
LANG=C.UTF-8
TZ=UTC
lower=last
```

Remove proxy settings for one build, and keep its exit status:

```sh
dp-env -u HTTP_PROXY -u HTTPS_PROXY make test
echo "make exited with $?"
```

Run a build in another directory:

```sh
dp-env -C build cmake --build .
```

Distinguish failures in a script:

```sh
dp-env "$tool" --check
case $? in
    0)   echo "check passed" ;;
    125) echo "dp-env usage problem" ;;
    126) echo "$tool is not executable" ;;
    127) echo "$tool not found" ;;
    *)   echo "check failed" ;;
esac
```

Parse the environment safely, even when values contain newlines:

```sh
dp-env -0 | while IFS= read -r -d '' entry; do printf '%s\n' "${entry%%=*}"; done
```

Show the version:

```text
$ dp-env --version
dp-env (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-env --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-env [OPTION]... [-] [NAME=VALUE]... [COMMAND [ARG]...]
Set each NAME to VALUE in the environment and run COMMAND.

Options are recognized only before the first operand. A lone '-' as the first
operand implies -i. Without COMMAND, print the resulting environment, one
NAME=VALUE entry per line, sorted by name.

Options:
  -i, --ignore-environment  start with an empty environment
  -u, --unset=NAME          remove variable NAME from the environment
  -C, --chdir=DIR           change the working directory to DIR before
                              running COMMAND
  -0, --null                end each printed entry with NUL, not newline
      --help                display this help and exit
      --version             output version information and exit

Exit status:
  125  dp-env itself failed
  126  COMMAND was found but could not be run
  127  COMMAND was not found
  otherwise, the exit status of COMMAND (128+N if killed by signal N)
```

## VERSION OUTPUT

```text
dp-env (dialectic-playground) 1.0.0
```

## ENVIRONMENT

| Variable | Use |
| :-- | :-- |
| `PATH` | Directories searched for *COMMAND* when it contains no path separator. The new environment's `PATH` is used if it has one, otherwise `dp-env`'s own. |
| `PATHEXT` | Windows only: file extensions tried when looking up *COMMAND* (default `.COM;.EXE;.BAT;.CMD`). Taken from the new environment if set there, otherwise from `dp-env`'s own. |

Apart from these lookups, `dp-env` does not interpret any variable. Locale variables such as
`LANG` and `LC_ALL` do not change `dp-env`'s behavior or messages, and they are passed on to the
command unchanged unless you remove or replace them.

## PLATFORM NOTES

- **Windows — variable names:** names are case-insensitive, as everywhere on Windows.
  `-u path` removes `Path`, and `dp-env path=C:\tools prog` replaces the existing `Path`
  entry with one spelled `path`. When printing, names appear with their spelling, and the
  sort is still byte-wise on that spelling. Windows' hidden per-drive entries (names starting
  with `=`, such as `=C:`) are not printed and cannot be changed.
- **Windows — starting programs:** `dp-env` finds the program itself, trying each `PATHEXT`
  extension (`prog` finds `prog.exe`). Unlike `cmd.exe`, it never looks in the current
  directory unless `PATH` lists it. Batch files (`.bat`, `.cmd`) are started the way
  `CreateProcess` starts them. Arguments are quoted so that programs using the standard C
  runtime receive them exactly.
- **Windows — exit codes:** the full 32-bit exit code is passed through. A command ended by
  Ctrl+C typically exits with `0xC000013A` (3221225786), and `dp-env` exits with the same code.
- **Windows — clearing the environment:** many Windows programs, including most language
  runtimes, cannot start without `SYSTEMROOT`. When using `-i` to run a command, assign it
  back: `dp-env -i SYSTEMROOT=%SYSTEMROOT% prog`.
- **Linux / macOS — signals:** pressing Ctrl+C in a terminal sends SIGINT to every process in
  the foreground job, so the command receives it directly, and it may receive it a second
  time through `dp-env`. A signal sent to `dp-env` alone, for example with `kill`, reaches
  the command once.
- **Linux / macOS — scripts:** a script needs a `#!` line and execute permission. Without a
  `#!` line, `dp-env` reports `Exec format error` rather than running the script with a
  shell.
- **Compared with GNU/BSD `env`:** `dp-env` sorts printed output, always waits for the command
  instead of replacing itself with it, and does not offer `-S`/`--split-string`, `-v`, or the
  signal-blocking options.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`env(1)`, `nohup(1)`, `execve(2)`, `posix_spawn(3)`, `waitpid(2)`, `signal(7)`;
`CreateProcessW` and `SetConsoleCtrlHandler` in the Win32 documentation.
