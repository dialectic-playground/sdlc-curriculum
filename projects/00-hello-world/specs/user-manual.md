<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-hello — User Manual](#dp-hello--user-manual)
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

# dp-hello — User Manual

| Field         | Value                                            |
| :------------ | :----------------------------------------------- |
| Product       | `dp-hello` 1.0.0                                 |
| Project       | `00-hello-world` — Standard Terminal Hello World |
| Applies to    | Linux, macOS, Windows                            |
| Specification | `SRS.md` (SRS-00), `shared/CLI-CONVENTIONS.md`   |

---

## NAME

**dp-hello** — print a greeting to standard output

## SYNOPSIS

```text
dp-hello [-n NAME | --name=NAME] [-c COUNT | --count=COUNT]
dp-hello --help
dp-hello --version
```

## DESCRIPTION

`dp-hello` writes the line `Hello, World!` to standard output. With `--name` it greets someone
else, and with `--count` it repeats the greeting.

Output is identical on every operating system: each greeting is followed by a single line feed
(LF), even on Windows. Names are printed exactly as typed, including spaces and non-ASCII
characters such as `Zoë`, and are encoded in UTF-8.

`dp-hello` reads no input, takes no operands, and never touches files or environment variables.

## OPTIONS

**`-n NAME`, `--name=NAME`**
: Greet _NAME_ instead of `World`. The name may contain any characters but must not be empty.
Quote names that contain spaces or shell metacharacters: `--name 'Ada Lovelace'`.

**`-c COUNT`, `--count=COUNT`**
: Print the greeting _COUNT_ times. _COUNT_ must be a whole number from 1 to 1000, written with
the digits `0`–`9` only (no sign, spaces, or decimal point). Leading zeros are allowed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-hello` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-nAda`, `-n Ada`, `--name=Ada`, and
  `--name Ada` are equivalent.
- Short options can be combined: `-c2 -nKen` works.
- Long options must be spelled out in full; `--nam` is not accepted.
- If an option is given more than once, the last one wins: `-n A -n B` greets `B`.
- `--` ends option processing. Since `dp-hello` accepts no operands, anything after `--` is an
  error.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                              |
| :----- | :------------------------------------------------------------------- |
| 0      | Success: the greeting, help, or version was printed                  |
| 2      | Usage error: invalid option, invalid value, or an unexpected operand |

## DIAGNOSTICS

Errors are written to standard error as two lines, and nothing is written to standard output.
For example:

```text
$ dp-hello --nme Ada
dp-hello: unrecognized option '--nme'
Try 'dp-hello --help' for more information.
```

| Message                                     | Cause                                       | Fix                                  |
| :------------------------------------------ | :------------------------------------------ | :----------------------------------- |
| `invalid option -- 'x'`                     | Unknown short option `-x`                   | Check the option letter (`-n`, `-c`) |
| `unrecognized option '--xyz'`               | Unknown or abbreviated long option          | Spell the option in full             |
| `option requires an argument -- 'n'`        | `-n` or `-c` given without a value          | Supply a value                       |
| `option '--name' requires an argument`      | `--name` or `--count` given without a value | Supply a value                       |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…`                 | Remove the `=…`                      |
| `invalid argument '' for '--name'`          | Empty name                                  | Give a non-empty name                |
| `invalid argument '0' for '--count'`        | Count not in 1–1000 or not all digits       | Use a whole number from 1 to 1000    |
| `extra operand 'foo'`                       | A word that is not an option                | Remove it, or use `--name foo`       |

## EXAMPLES

Print the classic greeting:

```text
$ dp-hello
Hello, World!
```

Greet someone by name:

```text
$ dp-hello --name Ada
Hello, Ada!
$ dp-hello -n 'Ada Lovelace'
Hello, Ada Lovelace!
```

Repeat the greeting:

```text
$ dp-hello -c 3 -n Grace
Hello, Grace!
Hello, Grace!
Hello, Grace!
```

Use the exit status in a script:

```sh
if dp-hello --count 2 > greetings.txt; then
    echo "wrote $(wc -l < greetings.txt) lines"
fi
```

Show the version:

```text
$ dp-hello --version
dp-hello (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-hello --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-hello [OPTION]...
Print a greeting to standard output.

Options:
  -n, --name=NAME     greet NAME instead of World
  -c, --count=COUNT   print the greeting COUNT times (1-1000, default 1)
      --help          display this help and exit
      --version       output version information and exit
```

## VERSION OUTPUT

```text
dp-hello (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-hello` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).

## PLATFORM NOTES

- **Windows:** output uses LF line endings, not CRLF. Use Windows Terminal or another
  UTF-8-capable console to see non-ASCII names correctly; redirected output is always UTF-8.
  In PowerShell, quote names that contain spaces: `dp-hello -n "Ada Lovelace"`.
- **macOS / Linux:** in shells such as bash or zsh, quote names that contain `!`, `$`, or spaces:
  `dp-hello -n 'Hi!'`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`echo(1)`, `printf(1)`; `dp-echo` (project 01).
