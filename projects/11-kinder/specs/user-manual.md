<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-kinder — User Manual](#dp-kinder--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
  - [OPTIONS](#options)
    - [Option syntax](#option-syntax)
  - [EXIT STATUS](#exit-status)
  - [DIAGNOSTICS](#diagnostics)
  - [EXAMPLES](#examples)
  - [HELP OUTPUT](#help-output)
  - [VERSION OUTPUT](#version-output)
  - [ENVIRONMENT](#environment)
  - [PLATFORM NOTES](#platform-notes)
  - [INSTALLATION](#installation)
  - [SEE ALSO](#see-also)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# dp-kinder — User Manual

| Field         | Value                                                   |
| :------------ | :------------------------------------------------------ |
| Product       | `dp-kinder` 1.0.0                                       |
| Project       | `11-kinder` — Console Output & Environment Verification |
| Applies to    | Linux, macOS, Windows                                   |
| Specification | `SRS.md` (SRS-11), `shared/CLI-CONVENTIONS.md`          |

---

## NAME

**dp-kinder** — print a kinder and gentler message to standard output

## SYNOPSIS

```text
dp-kinder
dp-kinder --help
dp-kinder --version
```

## DESCRIPTION

`dp-kinder` writes the line `ANSI--A kinder and gentler C!` to standard output and exits with
status 0. It is the first program of Johnsonbaugh & Kalin, _Applications Programming in ANSI
C_, and it serves the same purpose here: if it builds, installs, runs, and passes its tests on
your system, your toolchain is ready for the projects that follow.

The output is identical on every operating system: the message is followed by a single line
feed (LF), even on Windows.

`dp-kinder` takes no operands, never reads standard input, and never touches files or
environment variables. Any word on the command line other than `--help`, `--version`, or a
lone `--` is an error.

## OPTIONS

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-kinder` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--hel` is not accepted.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid: `dp-kinder oops --help` shows the
  help, but `dp-kinder -x --help` reports `-x`.
- `--` ends option processing. A lone `--` is accepted and changes nothing; anything after it
  is an operand, and therefore an error: `dp-kinder -- --help` reports `--help` as an extra
  operand.

## EXIT STATUS

| Status | Meaning                                                         |
| :----- | :-------------------------------------------------------------- |
| 0      | Success: the message, help, or version was printed              |
| 1      | The output could not be written (for example, the disk is full) |
| 2      | Usage error: an invalid option or an unexpected operand         |

## DIAGNOSTICS

Usage errors are written to standard error as two lines, and nothing is written to standard
output. For example:

```text
$ dp-kinder hello
dp-kinder: extra operand 'hello'
Try 'dp-kinder --help' for more information.
```

| Message                                     | Cause                                                               | Fix                                          |
| :------------------------------------------ | :------------------------------------------------------------------ | :------------------------------------------- |
| `invalid option -- 'x'`                     | A short option such as `-x`; `dp-kinder` has none                   | Remove it                                    |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option                                  | Use `--help` or `--version`, spelled in full |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…`                                         | Remove the `=…`                              |
| `extra operand 'foo'`                       | A word that is not an option, including `-` and anything after `--` | Remove it                                    |
| `write error`                               | The output could not be written                                     | Free space or redirect the output elsewhere  |

## EXAMPLES

Print the message:

```text
$ dp-kinder
ANSI--A kinder and gentler C!
```

Check an installation from a script:

```sh
if [ "$(dp-kinder)" = 'ANSI--A kinder and gentler C!' ]; then
    echo "toolchain OK"
fi
```

Show the version:

```text
$ dp-kinder --version
dp-kinder (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-kinder --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-kinder [OPTION]...
Print the message 'ANSI--A kinder and gentler C!' to standard output.

Options:
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-kinder (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-kinder` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).

## PLATFORM NOTES

- **Windows:** output uses LF line endings, not CRLF, so `dp-kinder > out.txt` produces a
  30-byte file. Check the exit status with `echo %ERRORLEVEL%` in `cmd.exe` or
  `$LASTEXITCODE` in PowerShell.
- **macOS / Linux:** check the exit status with `echo $?`. In bash, quote the expected message
  in single quotes when comparing it, because it contains `!`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-hello` (project 00), which prints a configurable greeting; `dp-echo` (project 01);
`echo(1)`, `printf(1)`.
