<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-elephnt1, dp-elephnt2 — User Manual](#dp-elephnt1-dp-elephnt2--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [dp-elephnt1](#dp-elephnt1)
    - [dp-elephnt2](#dp-elephnt2)
    - [Prompts](#prompts)
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

# dp-elephnt1, dp-elephnt2 — User Manual

| Field         | Value                                             |
| :------------ | :------------------------------------------------ |
| Products      | `dp-elephnt1` 1.0.0, `dp-elephnt2` 1.0.0          |
| Project       | `43-linked-list` — Singly Linked List Foundations |
| Applies to    | Linux, macOS, Windows                             |
| Specification | `SRS.md` (SRS-43), `shared/CLI-CONVENTIONS.md`    |

---

## NAME

**dp-elephnt1** — print a linked list of three elephants

**dp-elephnt2** — build a linked list of elephant names from a dialog and print it

## SYNOPSIS

```text
dp-elephnt1
dp-elephnt2 [-p | --prompt] [FILE]
dp-elephnt1 --help | --version
dp-elephnt2 --help | --version
```

## DESCRIPTION

### dp-elephnt1

`dp-elephnt1` builds a list of three nodes — Edna, then Elmer, then Eloise — and prints it by
following the links from the first node to the last. It reads no input.

```text
$ dp-elephnt1
Elephant number 1 is Edna.
Elephant number 2 is Elmer.
Elephant number 3 is Eloise.
```

### dp-elephnt2

`dp-elephnt2` reads a dialog from _FILE_, or from standard input when _FILE_ is absent or `-`.
The dialog is a sequence of lines that alternate between a **name** and an **answer**:

1. A name: the whole line, so it may contain spaces (`Babar the Elephant`). Spaces, tabs, and a
   carriage return at the start or end of the line are ignored. A blank name is an error.
2. An answer: `1` to add another elephant, `0` to stop. Spaces around the answer are ignored,
   and `+1` or `01` are also accepted. Anything else is an error.

If the input ends where an answer is expected, the list ends there, as if you had answered
`0`. After the answer `0`, nothing more is read. When the dialog is over, `dp-elephnt2` prints
one line per elephant, in the order the names were entered:

```text
$ printf 'Dumbo\n1\nBabar\n0\n' | dp-elephnt2
Elephant number 1 is Dumbo.
Elephant number 2 is Babar.
```

Names are printed exactly as typed (apart from the ignored spaces around them), whatever
characters they contain. Files with Windows (CRLF) line endings read the same as any other, and
one or more Ctrl-Z bytes at the very end of the input (the end-of-file mark of old MS-DOS files)
are ignored. The list is printed only when the whole dialog was valid; after an error nothing is
printed.

### Prompts

With `-p` or `--prompt`, `dp-elephnt2` asks its questions on standard error, the way the
textbook program did: each question starts on a new line after a blank line, is indented by a
tab, and is followed by a tab.

| Prompt                                                      | Written before |
| :---------------------------------------------------------- | :------------- |
| _(blank line)_ `<TAB>NAME:<TAB>`                            | each name      |
| _(blank line)_ `<TAB>Add another? (1 == yes, 0 == no)<TAB>` | each answer    |

At a terminal (what you type is shown after each prompt; tabs are shown as spaces):

```text
$ dp-elephnt2 --prompt

        NAME:   Dumbo

        Add another? (1 == yes, 0 == no)        1

        NAME:   Babar

        Add another? (1 == yes, 0 == no)        0
Elephant number 1 is Dumbo.
Elephant number 2 is Babar.
```

The prompts never appear on standard output, so `dp-elephnt2 --prompt > herd.txt` saves only
the list.

## OPTIONS

**`-p`, `--prompt`** (dp-elephnt2 only)
: Write the prompts shown above to standard error before each name and each answer is read. A
prompt is written even if the input then turns out to have ended.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

Both tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-elephnt2 herd.txt -p` works.
- `--` ends option processing, so `dp-elephnt2 -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.
- `dp-elephnt1` takes no options other than `--help` and `--version`, and no operands.

## EXIT STATUS

| Status | Meaning                                                                                               |
| :----- | :---------------------------------------------------------------------------------------------------- |
| 0      | Success: the list was printed, or help or version was printed                                         |
| 1      | `dp-elephnt2`: the input could not be read, or the dialog contained an error                          |
| 2      | Usage error: an invalid option, an operand for `dp-elephnt1`, or more than one file for `dp-elephnt2` |

## DIAGNOSTICS

Errors in the dialog name the input (`-` for standard input) and the line. Nothing is printed
on standard output, and the exit status is 1:

```text
$ dp-elephnt2 bad-answer.txt
dp-elephnt2: bad-answer.txt:4: invalid integer 'yes'
```

| Message                                | Cause                                                                                               | Fix                                                |
| :------------------------------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------------- |
| `FILE:LINE: invalid integer 'TEXT'`    | The answer on line _LINE_ is not a whole number (or is blank)                                       | Answer `1` or `0`                                  |
| `FILE:LINE: value out of range 'TEXT'` | The answer is a whole number other than 0 and 1                                                     | Answer `1` or `0`                                  |
| `FILE:LINE: empty name`                | The name line is blank                                                                              | Type a name                                        |
| `FILE:LINE: unexpected end of input`   | The input ended where a name was expected (for example right after the answer 1, or an empty input) | Add the missing name, or answer `0` instead of `1` |
| `FILE: No such file or directory`      | _FILE_ does not exist                                                                               | Check the name                                     |
| `FILE: Is a directory`                 | _FILE_ is a directory                                                                               | Name a file                                        |
| `FILE: Permission denied`              | _FILE_ cannot be read                                                                               | Check its permissions                              |
| `write error`                          | The list could not be written (for example, the disk is full)                                       | Free space or redirect the output elsewhere        |

With `--prompt`, the message follows the last prompt on the same line of standard error.

Usage errors are written to standard error as two lines; nothing is read and nothing is written
to standard output:

```text
$ dp-elephnt1 extra
dp-elephnt1: extra operand 'extra'
Try 'dp-elephnt1 --help' for more information.
```

| Message                                       | Cause                                                              | Fix                      |
| :-------------------------------------------- | :----------------------------------------------------------------- | :----------------------- |
| `invalid option -- 'x'`                       | Unknown short option (`dp-elephnt1` has no `-p`)                   | Remove it                |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                                 | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | `=…` after `--prompt`, `--help`, or `--version`                    | Remove the `=…`          |
| `extra operand 'X'`                           | An operand for `dp-elephnt1`, or a second _FILE_ for `dp-elephnt2` | Remove it                |

## EXAMPLES

The dialog shown in the textbook, from a file (`readme.txt` holds `Dumbo`, `1`, `Babar`, `0`,
one per line):

```text
$ dp-elephnt2 readme.txt
Elephant number 1 is Dumbo.
Elephant number 2 is Babar.
```

Names with spaces, and answers written loosely. `herd.txt` holds eight lines: `Jumbo` with
two spaces before and after it, `1`, `Babar the Elephant`, `01` with a space before and after
it, `Horton` with a tab before and after it, `+1`, `Elmer`, and `0`:

```text
$ dp-elephnt2 herd.txt
Elephant number 1 is Jumbo.
Elephant number 2 is Babar the Elephant.
Elephant number 3 is Horton.
Elephant number 4 is Elmer.
```

End the list with the end of the input instead of `0`:

```text
$ printf 'Dumbo\n1\nBabar\n' | dp-elephnt2
Elephant number 1 is Dumbo.
Elephant number 2 is Babar.
```

Use the exit status in a script:

```sh
if dp-elephnt2 herd.txt > list.txt; then
    echo "herd listed"
fi
```

## HELP OUTPUT

`dp-elephnt1 --help` and `dp-elephnt2 --help` print exactly the following texts (every line ends
in LF). The help texts are part of the specification (CONV-23).

`dp-elephnt1 --help`:

```text
Usage: dp-elephnt1 [OPTION]...
Build a linked list of three elephants (Edna, Elmer, Eloise) and print it.

The three nodes are linked by hand and the list is printed by walking it from
its first node to its end, one line per elephant.  No input is read.

Options:
      --help       display this help and exit
      --version    output version information and exit
```

`dp-elephnt2 --help`:

```text
Usage: dp-elephnt2 [OPTION]... [FILE]
Build a linked list of elephant names from a dialog, then print the list.

Read the dialog from FILE, or from standard input when FILE is absent or -.
Lines alternate between a name and an answer: 1 adds another elephant, 0 (or
the end of the input) ends the list.  Spaces and tabs around a name or an
answer are ignored.  Then print 'Elephant number N is NAME.' for each name.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

## VERSION OUTPUT

```text
dp-elephnt1 (dialectic-playground) 1.0.0
dp-elephnt2 (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

Both tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
Names are handled as bytes and are never converted between character sets.

## PLATFORM NOTES

- **Windows:** input is read as bytes, so CRLF files and files ending in Ctrl-Z behave as on
  Linux and macOS, and output uses LF line endings. At the console, end the input by typing
  Ctrl+Z and then Enter; on Linux and macOS, type Ctrl+D at the start of a line. Either one, in
  place of an answer, ends the list. In Windows PowerShell 5.1, text piped into a native program
  is re-encoded before `dp-elephnt2` sees it, which can change names that are not plain ASCII;
  redirect from a file or use `cmd.exe` to pass names unchanged.
- **Terminals:** prompts appear on standard error, so they stay visible when standard output is
  redirected to a file.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build dp-elephnt1 and dp-elephnt2
make install      # install both into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-line-ed` (project 44), which keeps a text buffer in a linked list; `dp-queue1`,
`dp-queue2`, `dp-stack1`, and `dp-stack2` (project 45), which build queues and stacks from
arrays and linked lists; `dp-grade` (project 20), another answer-driven dialog; `nl(1)`.
