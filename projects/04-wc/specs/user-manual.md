# dp-wc — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-wc` 1.0.0 |
| Project | `04-wc` — Word, Line, and Byte Counter |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-04), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-wc** — print line, word, character, and byte counts

## SYNOPSIS

```text
dp-wc [-l] [-w] [-m] [-c] [-L] [FILE]...
dp-wc --help
dp-wc --version
```

## DESCRIPTION

`dp-wc` reads each *FILE* and prints one line of counts for it, followed by the file name. When
more than one *FILE* is given, a final line labelled `total` gives the sums. With no *FILE*,
`dp-wc` reads standard input and prints the counts without a name. The *FILE* `-` also means
standard input, and is shown as `-`.

Five counts are available. Whatever order you give the options in, they are always printed in
this order:

1. **lines** — the number of line-feed (LF) characters. A last line without a line feed is not
   counted as a line, exactly as in traditional `wc`.
2. **words** — the number of runs of non-blank bytes. Only six ASCII bytes separate words:
   space, tab, LF, vertical tab, form feed, and carriage return (CR). Everything else, including
   every non-ASCII character, is part of a word.
3. **characters** — the number of UTF-8 characters (Unicode code points). A byte that is not
   part of a valid UTF-8 sequence counts as one character on its own.
4. **bytes** — the size of the input in bytes.
5. **maximum line length** — the number of characters in the longest line, not counting the line
   feed. Every character counts as 1, including tab and CR.

Without options, `dp-wc` prints lines, words, and bytes.

Counting is the same in every locale and on every operating system: `dp-wc` looks only at the
bytes of the input. Windows files with CRLF line endings are counted as they are stored: each
CR is a byte, a character, and a word separator, and it counts towards the line length.

### Output layout

Every number in the output is right-aligned to the same width: the number of digits of the
largest number printed anywhere in the output, including the total line. Numbers are separated
by one space, and the name follows after one more space. So a single count is printed with no
padding at all, which makes `dp-wc -l < file` convenient in scripts.

```text
$ dp-wc poem.txt utf8.txt
  5  15  93 poem.txt
  4   9  93 utf8.txt
  9  24 186 total
```

### Character counting in detail

`dp-wc` decodes UTF-8 strictly, following the Unicode Standard. Overlong encodings, encoded
surrogates, values above U+10FFFF, stray continuation bytes, and sequences cut short (by another
byte or by the end of the file) are invalid, and **each byte** of an invalid sequence counts as
one character. For example, the three bytes `E2 82 41` (a truncated euro sign followed by `A`)
count as three characters. A byte-order mark is counted as an ordinary character.

### Large files

`dp-wc` reads its input in fixed-size blocks and never holds a whole file in memory, so it can
count files of any size.

## OPTIONS

**`-l`, `--lines`**
: Print the line count (the number of LF bytes).

**`-w`, `--words`**
: Print the word count.

**`-m`, `--chars`**
: Print the character count.

**`-c`, `--bytes`**
: Print the byte count.

**`-L`, `--max-line-length`**
: Print the length of the longest line, in characters. In the `total` line this is the largest
  value of all the files, not the sum.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-wc` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Short options can be combined: `-lw` is the same as `-l -w`.
- Long options must be spelled out in full; `--char` is not accepted.
- Giving an option twice is the same as giving it once.
- Options and file names can be mixed: `dp-wc notes.txt -l` works.
- `--` ends option processing, so `dp-wc -- -l` counts a file named `-l`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: every input was counted, or help or version was printed |
| 1 | At least one file could not be read; the others were still counted |
| 2 | Usage error: an invalid option |

## DIAGNOSTICS

Problems with a file are reported on standard error. `dp-wc` then continues with the next file,
leaves the failed file out of the output and the total, and exits with status 1:

```text
$ dp-wc poem.txt missing.txt crlf.txt
dp-wc: missing.txt: No such file or directory
  5  15  93 poem.txt
  4   6  41 crlf.txt
  9  21 134 total
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name the files inside it instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |

Usage errors are written to standard error as two lines; nothing is counted and nothing is
written to standard output:

```text
$ dp-wc -lz poem.txt
dp-wc: invalid option -- 'z'
Try 'dp-wc --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'z'` | Unknown short option `-z` | Use `-l`, `-w`, `-m`, `-c`, or `-L` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--bytes' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |

## EXAMPLES

Count lines, words, and bytes in a file:

```text
$ dp-wc poem.txt
 5 15 93 poem.txt
```

Count the lines produced by another command (no name, no padding):

```text
$ printf 'hello world\n' | dp-wc -l
1
```

Compare characters and bytes in UTF-8 text (`greek.txt` holds the two lines `Kalimera` and
`Καλημέρα`; each Greek letter is one character but two bytes):

```text
$ dp-wc -m -c greek.txt
18 26 greek.txt
```

Show every count; the column order is fixed:

```text
$ dp-wc -L -c -m -w -l utf8.txt
 4  9 54 93 19 utf8.txt
```

Find the longest line (here, 37 characters):

```text
$ dp-wc -L poem.txt
37 poem.txt
```

Count standard input explicitly, alongside a file:

```text
$ dp-wc - poem.txt < poem.txt
  5  15  93 -
  5  15  93 poem.txt
 10  30 186 total
```

Use the exit status in a script:

```sh
if lines=$(dp-wc -l < report.txt); then
    echo "report has $lines lines"
fi
```

## HELP OUTPUT

`dp-wc --help` prints exactly the following text (every line ends in LF). The help text is part
of the specification (CONV-23):

```text
Usage: dp-wc [OPTION]... [FILE]...
Print line, word, character, and byte counts for each FILE, and a total line
if more than one FILE is given.

With no FILE, read standard input.  The FILE '-' also means standard input.
A word is a maximal run of bytes other than space, tab, LF, VT, FF, and CR.
Characters are UTF-8 code points; each byte of an invalid sequence counts as
one character.  Counts are printed in the order lines, words, characters,
bytes, maximum line length.  With no option, -l -w -c is assumed.

Options:
  -l, --lines             print the line (LF) counts
  -w, --words             print the word counts
  -m, --chars             print the character counts
  -c, --bytes             print the byte counts
  -L, --max-line-length   print the maximum line length in characters
      --help              display this help and exit
      --version           output version information and exit
```

## VERSION OUTPUT

```text
dp-wc (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-wc` ignores all environment variables. In particular, locale settings (`LANG`, `LC_ALL`,
`LC_CTYPE`) have no effect on how words and characters are counted.

## PLATFORM NOTES

- **Windows:** files are read as raw bytes. CRLF line endings are not converted, and Ctrl-Z
  does not end a file, so byte counts always equal the file size shown by the file system.
  Output uses LF line endings, not CRLF. Character counts do not depend on the console code page.
  In Windows PowerShell 5.1, text piped into a native program is re-encoded (using the
  console's output encoding, with CRLF line endings) before `dp-wc` sees it; pass the file name
  instead to count the bytes stored on disk.
- **macOS / Linux:** results do not depend on the locale, so `dp-wc` gives the same word and
  character counts under `LANG=C` and `LANG=en_US.UTF-8`, unlike the system `wc`.
- **Differences from the system `wc`:** the column width follows the rule in "Output layout"
  rather than file sizes; `-L` counts tabs as 1 and wide characters as 1 instead of measuring
  display columns; a file that cannot be read gets no output line; standard input given as `-`
  more than once is read only the first time (later `-` operands count as empty); file names
  are printed as given, without quoting.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`wc(1)`; `dp-cat` (project 02), `dp-head` and `dp-tail` (project 03).
