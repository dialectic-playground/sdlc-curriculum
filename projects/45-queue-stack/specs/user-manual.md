<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-queue1, dp-queue2, dp-stack1, dp-stack2 — User Manual](#dp-queue1-dp-queue2-dp-stack1-dp-stack2--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Commands](#commands)
    - [Records](#records)
    - [Results](#results)
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

# dp-queue1, dp-queue2, dp-stack1, dp-stack2 — User Manual

| Field         | Value                                                                      |
| :------------ | :------------------------------------------------------------------------- |
| Products      | `dp-queue1` 1.0.0, `dp-queue2` 1.0.0, `dp-stack1` 1.0.0, `dp-stack2` 1.0.0 |
| Project       | `45-queue-stack` — Comparative Queue & Stack ADT Implementations           |
| Applies to    | Linux, macOS, Windows                                                      |
| Specification | `SRS.md` (SRS-45), `shared/CLI-CONVENTIONS.md`                             |

---

## NAME

**dp-queue1** — run a queue of bank customers stored in a circular array of 100 places

**dp-queue2** — run a queue of bank customers stored in a linked list

**dp-stack1** — run a stack of cafeteria trays stored in an array of 100 places

**dp-stack2** — run a stack of cafeteria trays stored in a linked list

## SYNOPSIS

```text
dp-queue1 [-p | --prompt] [FILE]
dp-queue2 [-p | --prompt] [FILE]
dp-stack1 [-p | --prompt] [FILE]
dp-stack2 [-p | --prompt] [FILE]
<tool> --help | --version
```

## DESCRIPTION

The four tools read numbered commands from _FILE_, or from standard input when _FILE_ is
absent or `-`, and apply them to a collection of records:

| Tool        | Holds           | Order               | Stored in        | Capacity |
| :---------- | :-------------- | :------------------ | :--------------- | :------- |
| `dp-queue1` | bank customers  | first in, first out | a circular array | 100      |
| `dp-queue2` | bank customers  | first in, first out | a linked list    | no limit |
| `dp-stack1` | cafeteria trays | last in, first out  | an array         | 100      |
| `dp-stack2` | cafeteria trays | last in, first out  | a linked list    | no limit |

The array and linked tools of each kind give exactly the same results for the same commands,
except that only the array tool can become full. You can switch between them freely.

### Commands

| Command      | Queue tools                                  | Stack tools                     |
| :----------- | :------------------------------------------- | :------------------------------ |
| `1` _record_ | insert the customer at the rear              | push the tray on top            |
| `2`          | remove the customer at the front and show it | pop the tray on top and show it |
| `3`          | display the queue, front first               | display the stack, top first    |
| `0`          | quit                                         | quit                            |

The end of the input also quits. Commands and the fields of a record are separated by any
spaces, tabs, or line breaks, so a record may be on the same line as its `1` or on lines of
its own. Files with Windows (CRLF) line endings read the same as any other, and one or more
Ctrl-Z bytes at the very end of the input are ignored.

### Records

A **customer** is four fields: last name, first name, account number, balance — for example
`1 Smith Ann 1001 250.75`. Names are single words (they cannot contain spaces). The account
number is a whole number from 0 to 9223372036854775807. The balance is an amount of money with
an optional sign and at most two decimal places: `250.75`, `-12.5`, `1000`, and `+0.05` are
valid; `12.345`, `.5`, and `1,000` are not. Its magnitude can be at most
999999999999999.99. Balances are kept exactly, to the cent, and always shown with two decimal
places.

A **tray** is two fields: color (a single word) and id number (a whole number from 0 to 9223372036854775807) — for example `1 red 7`.

### Results

Each result is printed as soon as its command has been read:

| Event                               | Output line                                                                             |
| :---------------------------------- | :-------------------------------------------------------------------------------------- |
| Customer removed                    | `Removed: Smith, Ann; account 1001; balance 250.75`                                     |
| Tray popped                         | `Popped: color red, id 7`                                                               |
| Display                             | one numbered line per record, for example `1: Smith, Ann; account 1001; balance 250.75` |
| Remove or display with nothing held | `QUEUE EMPTY` or `STACK EMPTY`                                                          |
| Insert into a full array tool       | `QUEUE FULL` or `STACK FULL` (the record is discarded)                                  |

An insertion that succeeds prints nothing. `QUEUE FULL`, `QUEUE EMPTY`, `STACK FULL`, and
`STACK EMPTY` are normal results: the session continues, and they do not change the exit
status.

### Prompts

With `-p` or `--prompt`, the tools ask for each command and each record on standard error:

| Tools | Before each command                                     | Before each record                                       |
| :---- | :------------------------------------------------------ | :------------------------------------------------------- |
| queue | `Enter 1 (insert), 2 (remove), 3 (display), 0 (quit): ` | `Enter last name, first name, account number, balance: ` |
| stack | `Enter 1 (push), 2 (pop), 3 (display), 0 (quit): `      | `Enter color, id: `                                      |

At a terminal:

```text
$ dp-stack1 --prompt
Enter 1 (push), 2 (pop), 3 (display), 0 (quit): 1
Enter color, id: red 1
Enter 1 (push), 2 (pop), 3 (display), 0 (quit): 1
Enter color, id: blue 2
Enter 1 (push), 2 (pop), 3 (display), 0 (quit): 2
Popped: color blue, id 2
Enter 1 (push), 2 (pop), 3 (display), 0 (quit): 0
```

The prompts never appear on standard output, so `dp-stack1 --prompt > log.txt` saves only the
results.

## OPTIONS

**`-p`, `--prompt`**
: Write the prompts shown above to standard error before each command and each record is read.
A last prompt appears before the end of the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

All four tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-queue1 commands.txt -p` works.
- `--` ends option processing, so `dp-queue2 -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                                                          |
| :----- | :------------------------------------------------------------------------------------------------------------------------------- |
| 0      | Success: the session ended with `0` or at the end of the input (full and empty results included), or help or version was printed |
| 1      | The input could not be read, it contained an invalid command or record, or memory ran out                                        |
| 2      | Usage error: an invalid option or more than one file                                                                             |

## DIAGNOSTICS

Errors in the input name the input (`-` for standard input) and the line. Results printed
before the error stand; nothing more is read:

```text
$ dp-stack1 bad-command.txt
1: color red, id 7
dp-stack1: bad-command.txt:3: invalid integer 'pop'
```

| Message                                 | Cause                                                                                               | Fix                                         |
| :-------------------------------------- | :-------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| `FILE:LINE: invalid integer 'TOKEN'`    | A command, account number, or tray id is not a whole number                                         | Write a whole number                        |
| `FILE:LINE: value out of range 'TOKEN'` | A command other than 0–3, a negative account number or id, or a balance of 1000000000000000 or more | Use a value in range                        |
| `FILE:LINE: invalid amount 'TOKEN'`     | A balance is not a number with at most two decimal places                                           | Write the balance like `250.75`             |
| `FILE:LINE: unexpected end of input`    | The input ends in the middle of a record                                                            | Complete the record                         |
| `FILE: No such file or directory`       | _FILE_ does not exist                                                                               | Check the name                              |
| `FILE: Is a directory`                  | _FILE_ is a directory                                                                               | Name a file                                 |
| `FILE: Permission denied`               | _FILE_ cannot be read                                                                               | Check its permissions                       |
| `out of memory`                         | `dp-queue2` or `dp-stack2` could not store another record                                           | Remove records, or use smaller inputs       |
| `write error`                           | The results could not be written (for example, the disk is full)                                    | Free space or redirect the output elsewhere |

With `--prompt`, the message follows the last prompt on the same line of standard error.

Usage errors are written to standard error as two lines; nothing is read and nothing is written
to standard output:

```text
$ dp-queue1 a b
dp-queue1: extra operand 'b'
Try 'dp-queue1 --help' for more information.
```

| Message                                       | Cause                                           | Fix                      |
| :-------------------------------------------- | :---------------------------------------------- | :----------------------- |
| `invalid option -- 'x'`                       | Unknown short option                            | Use `-p`                 |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option              | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | `=…` after `--prompt`, `--help`, or `--version` | Remove the `=…`          |
| `extra operand 'b'`                           | More than one _FILE_                            | Give one file            |

## EXAMPLES

Serve customers in arrival order (`customers.txt` inserts Smith, Jones, and Lee, displays,
removes two, displays, inserts Diaz, displays, and quits):

```text
$ dp-queue1 customers.txt
1: Smith, Ann; account 1001; balance 250.75
2: Jones, Bob; account 1002; balance -12.50
3: Lee, Kim; account 1003; balance 0.00
Removed: Smith, Ann; account 1001; balance 250.75
Removed: Jones, Bob; account 1002; balance -12.50
1: Lee, Kim; account 1003; balance 0.00
1: Lee, Kim; account 1003; balance 0.00
2: Diaz, Rosa; account 1004; balance 1000.00
```

Hand out trays, last in, first out:

```text
$ printf '1 red 1\n1 green 2\n1 blue 3\n2\n3\n' | dp-stack2
Popped: color blue, id 3
1: color green, id 2
2: color red, id 1
```

Nothing to remove:

```text
$ printf '2\n3\n' | dp-queue2
QUEUE EMPTY
QUEUE EMPTY
```

Compare the array and the linked queue on the same commands; the only difference appears when
the array is full:

```sh
dp-queue1 commands.txt > array.txt
dp-queue2 commands.txt > linked.txt
diff array.txt linked.txt
```

## HELP OUTPUT

`dp-queue1 --help`, `dp-queue2 --help`, `dp-stack1 --help`, and `dp-stack2 --help` print exactly
the following texts (every line ends in LF). The help texts are part of the specification
(CONV-23).

`dp-queue1 --help`:

```text
Usage: dp-queue1 [OPTION]... [FILE]
Run a queue of bank customers stored in a circular array of 100 places.

Read commands from FILE, or from standard input when FILE is absent or -.
1 inserts the customer whose last name, first name, account number, and
balance (at most 2 decimal places) follow; 2 removes the customer at the
front; 3 displays the queue from front to rear; 0 or the end of the input
quits.  Inserting into a full queue prints QUEUE FULL, and removing from an
empty one prints QUEUE EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

`dp-queue2 --help`:

```text
Usage: dp-queue2 [OPTION]... [FILE]
Run a queue of bank customers stored in a linked list of any length.

Read commands from FILE, or from standard input when FILE is absent or -.
1 inserts the customer whose last name, first name, account number, and
balance (at most 2 decimal places) follow; 2 removes the customer at the
front; 3 displays the queue from front to rear; 0 or the end of the input
quits.  Removing from an empty queue prints QUEUE EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

`dp-stack1 --help`:

```text
Usage: dp-stack1 [OPTION]... [FILE]
Run a stack of cafeteria trays stored in an array of 100 places.

Read commands from FILE, or from standard input when FILE is absent or -.
1 pushes the tray whose color and id follow; 2 pops the tray on top; 3
displays the stack from top to bottom; 0 or the end of the input quits.
Pushing onto a full stack prints STACK FULL, and popping an empty one prints
STACK EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

`dp-stack2 --help`:

```text
Usage: dp-stack2 [OPTION]... [FILE]
Run a stack of cafeteria trays stored in a linked list of any length.

Read commands from FILE, or from standard input when FILE is absent or -.
1 pushes the tray whose color and id follow; 2 pops the tray on top; 3
displays the stack from top to bottom; 0 or the end of the input quits.
Popping an empty stack prints STACK EMPTY.

Options:
  -p, --prompt     write prompts to standard error before reading
      --help       display this help and exit
      --version    output version information and exit
```

## VERSION OUTPUT

```text
dp-queue1 (dialectic-playground) 1.0.0
dp-queue2 (dialectic-playground) 1.0.0
dp-stack1 (dialectic-playground) 1.0.0
dp-stack2 (dialectic-playground) 1.0.0
```

(Each tool prints its own line.)

## ENVIRONMENT

The tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
Balances are always read and written with `.` as the decimal point and no digit grouping.

## PLATFORM NOTES

- **Windows:** input is read as bytes, so CRLF files and files ending in Ctrl-Z behave as on
  Linux and macOS, and output uses LF line endings. At the console, end the input by typing
  Ctrl+Z and then Enter; on Linux and macOS, type Ctrl+D at the start of a line. Either one, in
  place of a command, ends the session like `0`.
- **All platforms:** the array tools hold exactly 100 records everywhere, and account numbers
  and ids are 64-bit on every system. Balances are exact; they do not depend on the processor's
  floating-point unit.
- **Terminals:** prompts appear on standard error, so they stay visible when standard output is
  redirected to a file.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build the four tools
make install      # install them into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-elephnt1` and `dp-elephnt2` (project 43), which introduce linked lists; `dp-infix`
(project 46), which uses a stack to convert expressions; `dp-bfs-adj` and `dp-bfs-link`
(project 47), which use a queue for breadth-first search; `dp-kv` (project 09), which keeps
records between runs; `tac(1)`, `diff(1)`.
