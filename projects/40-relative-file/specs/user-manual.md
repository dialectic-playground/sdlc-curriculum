<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-relfile — User Manual](#dp-relfile--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [How records are placed](#how-records-are-placed)
    - [Keys and data](#keys-and-data)
    - [Failed operations](#failed-operations)
    - [The file](#the-file)
  - [THE MENU DIALOG](#the-menu-dialog)
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

# dp-relfile — User Manual

| Field         | Value                                                                  |
| :------------ | :--------------------------------------------------------------------- |
| Product       | `dp-relfile` 1.0.0                                                     |
| Project       | `40-relative-file` — Direct-Access Hashed Relative File Storage Engine |
| Applies to    | Linux, macOS, Windows                                                  |
| Specification | `SRS.md` (SRS-40), `shared/CLI-CONVENTIONS.md`                         |

---

## NAME

**dp-relfile** — keep records in a hashed relative file of 100 fixed-size slots

## SYNOPSIS

```text
dp-relfile [-f FILE | --file=FILE] [-p | --prompt]
dp-relfile [-f FILE | --file=FILE] add KEY DATA
dp-relfile [-f FILE | --file=FILE] find KEY
dp-relfile [-f FILE | --file=FILE] remove KEY
dp-relfile [-f FILE | --file=FILE] slots
dp-relfile --help
dp-relfile --version
```

## DESCRIPTION

`dp-relfile` stores records in a _relative file_, `relative.dat` in the current directory
unless `-f` names another. Each record has a **key** of exactly four digits (`0000` to `9999`)
and up to 30 characters of **data**. If the file does not exist, `dp-relfile` creates it, with
room for 100 records.

Records are added, found, and removed one command at a time:

```text
$ dp-relfile add 1234 'Ada Lovelace'
Added 1234 in slot 70
$ dp-relfile find 1234
Found 1234 in slot 70: Ada Lovelace
$ dp-relfile remove 1234
Removed 1234 from slot 70
```

or, with no command, through the textbook's numbered menu (see **THE MENU DIALOG**).

### How records are placed

The file has 100 _slots_, numbered 0 to 99. A record's **home slot** is its key modulo 97: key
`1234` belongs in slot 70, because 1234 = 12 × 97 + 70. If the home slot is occupied by another
record (a _collision_), the record goes into the next slot, then the next, and so on, wrapping
from slot 99 back to slot 0. Finding a record follows the same path from the home slot until it
finds the key or reaches a slot that has never been used. Slots 97, 98, and 99 are never a home
slot; they are only reached this way.

Removing a record does not empty its slot: it marks the slot **deleted** (a _tombstone_), so
that searches for records stored further along the path keep going. A later add reuses the
first tombstone on its path, after checking that the key is not already stored further on.

Every message names the slot used, and `dp-relfile slots` lists every slot that is not free:

```text
$ dp-relfile slots
0 taken 0000 first
1 deleted 0097 second
2 taken 9700 third
```

Each line gives the slot, `taken` or `deleted`, the key, and the data (omitted when empty).

### Keys and data

A key is exactly four digits; leading zeros count (`0042` is a different key from `42`, which
is not a valid key at all). Data is at most 30 characters of printable ASCII — letters, digits,
spaces, and punctuation; no TABs and no accented letters. Trailing spaces are removed, because
the file pads every data field with spaces; leading spaces are kept. Data may be empty.

### Failed operations

Adding a key that is already stored, adding when all 100 slots are taken, and finding or
removing a key that is not stored are _failed operations_. Each is reported on standard error
and makes the exit status 1; nothing in the file changes.

### The file

The relative file is exactly 3500 bytes: 100 records of 35 bytes. Each record is one status
byte (`0` free, `1` taken, `2` deleted), the four key digits, and the data padded with spaces
to 30 bytes. A new file holds 100 records of `0` followed by 34 spaces. The record of slot _s_
starts at byte 35 × _s_, and `dp-relfile` reads and writes single records at those positions.
Before doing anything, `dp-relfile` checks the whole file and refuses to use one with the wrong
size or a damaged record; it never changes such a file.

## THE MENU DIALOG

With no command, `dp-relfile` reads its instructions from standard input, one per line, the
way the textbook program read them from the keyboard:

1. A choice: `1` add a record, `2` find a record, `3` remove a record, `0` exit.
2. The key (for every choice except `0`).
3. The data (for `1` only).

The dialog repeats until a choice of `0` or the end of the input. Spaces and TABs around a
choice or key are ignored; lines may end in CRLF. A failed operation is reported and the dialog
goes on; a line that is not a valid choice, key, or data stops it, with the line number:

```text
dp-relfile: -:11: invalid choice 'x'
```

With `-p` or `--prompt`, the menu and a prompt for each key and data are written to standard
error, so you can use the dialog at the keyboard:

```text
			1   -- add a record
			2   -- find a record
			3   -- remove a record
			0   -- exit the program

			Please pick a number:
```

The key prompt is `Enter key (4 digits):` and the data prompt is
`Enter data (up to 30 characters):`, each indented by three TABs and followed by three spaces.

## OPTIONS

**`-f FILE`, `--file=FILE`**
: Use the relative file _FILE_ instead of `relative.dat`. It is created if it does not exist.

**`-p`, `--prompt`**
: In the menu dialog, write the menu before each choice and a prompt before each key and data,
to standard error. It has no effect with a command.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-relfile` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-fdb.dat`, `-f db.dat`, `--file=db.dat`, and
  `--file db.dat` are equivalent.
- Options may come before or after the command: `dp-relfile find 1234 -f db.dat` works.
- Long options must be spelled out in full; `--fi` is not accepted.
- If `-f` is given more than once, the last one wins.
- Data with spaces must be quoted as one argument; data that begins with `-` must follow `--`:
  `dp-relfile add 0007 -- '-5 degrees'`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                             |
| :----- | :-------------------------------------------------------------------------------------------------- |
| 0      | Every operation succeeded, or help or version was printed                                           |
| 1      | An operation failed, the menu input was malformed, the file is damaged, or a file could not be used |
| 2      | Usage error: an invalid option, command, key, or data                                               |

## DIAGNOSTICS

Every problem is reported on standard error as one line.

| Message                                          | Cause                                                                              | Fix                                                                     |
| :----------------------------------------------- | :--------------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| `cannot add K: duplicate key`                    | A record with key _K_ is already stored                                            | Remove it first, or use another key                                     |
| `cannot add K: file is full`                     | All 100 slots are taken                                                            | Remove records you no longer need                                       |
| `cannot find K: no such record`                  | No record with key _K_ is stored                                                   | Check the key                                                           |
| `cannot remove K: no such record`                | No record with key _K_ is stored                                                   | Check the key                                                           |
| `F: not a relative file (size N, expected 3500)` | _F_ is not 3500 bytes long                                                         | Check that _F_ is the right file; restore it from a backup              |
| `F: slot S: invalid record`                      | Record _S_ of _F_ has an invalid status, key, or data                              | Restore _F_ from a backup                                               |
| `F: No such file or directory`                   | A directory in the path _F_ does not exist                                         | Create the directory or correct the path                                |
| `F: Permission denied`                           | You may not read or write _F_, or create it                                        | Check the permissions (`add`, `remove`, and the menu need write access) |
| `F: Is a directory`                              | _F_ is a directory                                                                 | Name a file instead                                                     |
| `F: Not a directory`                             | Part of the path _F_ is a file, not a directory                                    | Correct the path                                                        |
| `F: Input/output error`                          | Any other failure to use _F_                                                       | Check the device or file system                                         |
| `-:L: invalid choice 'C'`                        | Line _L_ of the menu input is not 0, 1, 2, or 3                                    | Correct the input                                                       |
| `-:L: invalid key 'K'`                           | Line _L_ of the menu input is not a 4-digit key                                    | Correct the input                                                       |
| `-:L: invalid character in data`                 | The data on line _L_ contains a TAB, a control character, or a non-ASCII character | Use printable ASCII only                                                |
| `-:L: data too long (maximum 30 characters)`     | The data on line _L_ is longer than 30 characters                                  | Shorten it                                                              |
| `-:L: unexpected end of input`                   | The menu input ended where a key or data was expected                              | Complete the input                                                      |
| `-: Input/output error`                          | Standard input could not be read                                                   | Check what feeds standard input                                         |
| `write error`                                    | The results could not be written to standard output                                | Free space or redirect the output elsewhere                             |

Usage errors are written to standard error as two lines; no file is created or changed:

```text
$ dp-relfile add 123 'too short'
dp-relfile: invalid key '123'
Try 'dp-relfile --help' for more information.
```

| Message                                       | Cause                                                                  | Fix                                                |
| :-------------------------------------------- | :--------------------------------------------------------------------- | :------------------------------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                                              | Use `-f` or `-p`                                   |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                                     | Spell the option in full                           |
| `option requires an argument -- 'f'`          | `-f` given without a file name                                         | Supply a file name                                 |
| `option '--file' requires an argument`        | `--file` given without a file name                                     | Supply a file name                                 |
| `option '--prompt' doesn't allow an argument` | `--prompt=…`, `--help=…`, or `--version=…`                             | Remove the `=…`                                    |
| `invalid argument '' for '-f'`                | An empty file name                                                     | Give a non-empty file name                         |
| `unknown command 'W'`                         | _W_ is not `add`, `find`, `remove`, or `slots`                         | Use one of the four commands                       |
| `missing operand`                             | The command lacks its key or data                                      | Supply them                                        |
| `extra operand 'X'`                           | The command was given too many arguments                               | Quote data that contains spaces                    |
| `invalid key 'K'`                             | _K_ is not exactly four digits                                         | Write the key with four digits, for example `0042` |
| `invalid character in data`                   | The data contains a TAB, a control character, or a non-ASCII character | Use printable ASCII only                           |
| `data too long (maximum 30 characters)`       | The data is longer than 30 characters                                  | Shorten it                                         |

## EXAMPLES

Watch collisions and wrap-around (the keys 0096, 0193, 0290, 0387, and 0484 all have home
slot 96):

```text
$ for k in 0096 0193 0290 0387 0484; do dp-relfile add $k "key $k"; done
Added 0096 in slot 96
Added 0193 in slot 97
Added 0290 in slot 98
Added 0387 in slot 99
Added 0484 in slot 0
```

Run a menu session from a file:

```text
$ cat session.txt
1
1234
Ada Lovelace
2
1234
0
$ dp-relfile < session.txt
Added 1234 in slot 70
Found 1234 in slot 70: Ada Lovelace
```

Use another file, and test for a record in a script:

```sh
if dp-relfile -f staff.dat find 0042 > /dev/null 2>&1; then
    echo "0042 is on file"
fi
```

## HELP OUTPUT

`dp-relfile --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-relfile [OPTION]... [COMMAND [ARG]...]
Keep records in a relative file: 100 slots of 35 bytes, addressed by hashing.

Each record has a key of exactly 4 digits and up to 30 characters of data
(printable ASCII; trailing spaces are not kept).  A key's home slot is the key
modulo 97; a collision moves on to the next slot, wrapping from 99 to 0.  A
removed record leaves a tombstone that a later add can reuse.  The file is
created, with 100 free slots, if it does not exist.

Commands:
  add KEY DATA    add a record
  find KEY        print the record with key KEY
  remove KEY      remove the record with key KEY
  slots           list every slot that is not free

With no COMMAND, run the menu dialog: read the choices (1 add, 2 find,
3 remove, 0 exit), keys, and data from standard input, one per line.

Options:
  -f, --file=FILE   use the relative file FILE (default relative.dat)
  -p, --prompt      in the menu dialog, write the menu and prompts to
                      standard error before each line is read
      --help        display this help and exit
      --version     output version information and exit
```

## VERSION OUTPUT

```text
dp-relfile (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-relfile` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Slot numbers are always written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** the relative file is binary and has exactly the same bytes as on Linux and
  macOS, so it can be copied between systems. Menu input may have CRLF line endings; end
  keyboard input with Ctrl-Z followed by Enter. Output uses LF line endings, not CRLF. Both `/`
  and `\` work as directory separators in file names.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line. A new relative file
  is created with the default permissions given by your `umask`.
- **All platforms:** `dp-relfile` does not lock the file. Do not run two copies on the same
  file at the same time.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-kv` (project 09), a key-value store with atomic writes and locking; `dp-size` (project 39),
which reads files in binary mode; `dp-phone` (project 31), which finds records by binary search
instead of hashing; `dp-elephnt1` (project 43), dynamic linked structures in memory; `dbm(3)`,
`od(1)`, `xxd(1)`.
