# dp-matmult — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-matmult` 1.0.0 |
| Project | `30-matmult` — Matrix Multiplication Engine |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-30), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-matmult** — multiply two square matrices of integers

## SYNOPSIS

```text
dp-matmult [-p | --prompt] [FILE]
dp-matmult --help
dp-matmult --version
```

## DESCRIPTION

`dp-matmult` reads a matrix size *N* and two *N*×*N* matrices from *FILE*, or from standard
input when there is no *FILE* or *FILE* is `-`. It prints the first matrix, the second matrix,
and their product, each under a heading:

```text
Matrix m1:
1 2
3 4
Matrix m2:
2 0
1 2
Product m3:
4 4
10 8
```

### Input

The input is a sequence of whole numbers separated by any mix of spaces, tabs, and line
breaks:

1. the size *N*, from 1 to 20;
2. the *N*×*N* elements of the first matrix, row by row (all of row 1, then all of row 2, …);
3. the *N*×*N* elements of the second matrix, in the same order.

How the numbers are spread over lines does not matter, so the conventional layout of one
matrix row per line is just a convenience. Elements may be negative and may have a `+` sign or
leading zeros; they are printed as plain numbers (`+1` as `1`, `005` as `5`). Each element may
be any whole number from −9223372036854775808 to 9223372036854775807. Anything after the last
element of the second matrix is ignored and not even read. Files with Windows (CRLF) line
endings read the same as any other, and one or more Ctrl-Z bytes at the very end of the input
(the end-of-file mark of old MS-DOS data files) are ignored.

### Output

Each matrix is printed as its heading followed by one line per row. The numbers in a row are
separated by one space; there is no space at the end of a line, no column alignment, and no
blank line between the matrices.

### The product

Element (*i*, *j*) of the product is row *i* of the first matrix multiplied element by element
with column *j* of the second, summed:
*c*ᵢⱼ = *a*ᵢ₁*b*₁ⱼ + *a*ᵢ₂*b*₂ⱼ + … + *a*ᵢₙ*b*ₙⱼ. The result is exact. If any product
*a*ᵢₖ*b*ₖⱼ, or the running total after adding it (added from left to right), falls outside
−9223372036854775808 … 9223372036854775807, `dp-matmult` reports an integer overflow and the
position of that product element, and prints no product. Because the running total is checked
at every step, an element can be reported even if its final value would have fitted; reordering
the rows and columns of the input can avoid that.

### Working interactively

`dp-matmult` prints the first matrix as soon as you have typed its last element, before you
type the second. End the input early with **Ctrl-D** on Linux and macOS, or **Ctrl-Z** followed
by **Enter** in a Windows console. With `--prompt`, `dp-matmult` asks for each part of the
input:

```text
$ dp-matmult --prompt
Input matrix size: 2
Input first matrix by row
1 2
3 4
Matrix m1:
1 2
3 4
Input second matrix by row
2 0
1 2
Matrix m2:
2 0
1 2
Product m3:
4 4
10 8
```

The prompts are written to standard error, so `dp-matmult --prompt > report.txt` saves only
the matrices.

## OPTIONS

**`-p`, `--prompt`**
: Write `Input matrix size: ` before the size is read, `Input first matrix by row` (and a line
  break) before the first matrix, and `Input second matrix by row` (and a line break) before
  the second matrix, all to standard error.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-matmult` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-matmult data.txt -p` works.
- `--` ends option processing, so `dp-matmult -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the product was printed, or help or version was printed |
| 1 | The input could not be read, it contained invalid or too little data, or the product overflowed |
| 2 | Usage error: an invalid option or more than one file |

## DIAGNOSTICS

Problems with the data name the input (`-` for standard input) and the line number. Matrices
printed before the problem are kept, and the exit status is 1:

```text
$ dp-matmult bad.txt
Matrix m1:
1 2
3 4
dp-matmult: bad.txt:5: invalid integer 'x8'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | Entry *K* on line *L* is not a whole number, or lies outside −9223372036854775808 … 9223372036854775807 | Write the number in digits only, without separators or decimals |
| `S:L: value out of range 'K'` | The size *K* is not between 1 and 20 | Give a size from 1 to 20 |
| `S:L: unexpected end of input` | The input ended before the size or before the last element of the second matrix; *L* is the last line | Supply all 2×*N*×*N* elements |
| `integer overflow in product row I, column J` | Computing product element (*I*, *J*) needs a number outside the 64-bit range | Use smaller elements |
| `F: No such file or directory` | *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the file's permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other read failure | Check the device or file system |
| `write error` | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-matmult readme.txt identity.txt
dp-matmult: extra operand 'identity.txt'
Try 'dp-matmult --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-p` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `extra operand 'F'` | More than one file was named | Run `dp-matmult` once per file |

## EXAMPLES

Multiply two 2×2 matrices given on one line:

```text
$ echo '2  1 2 3 4  2 0 1 2' | dp-matmult
Matrix m1:
1 2
3 4
Matrix m2:
2 0
1 2
Product m3:
4 4
10 8
```

Matrix multiplication is not commutative; swapping the matrices changes the product:

```text
$ echo '2  2 0 1 2  1 2 3 4' | dp-matmult
Matrix m1:
2 0
1 2
Matrix m2:
1 2
3 4
Product m3:
2 4
7 10
```

A product that does not fit in 64 bits is reported, not printed:

```text
$ dp-matmult overflow.txt
Matrix m1:
3037000500 1
0 1
Matrix m2:
1 3037000500
0 1
dp-matmult: integer overflow in product row 1, column 2
```

Use the exit status in a script:

```sh
if dp-matmult data.txt > product.txt; then
    echo "product computed"
fi
```

## HELP OUTPUT

`dp-matmult --help` prints exactly the following text (every line ends in LF). The help text
is part of the specification (CONV-23):

```text
Usage: dp-matmult [OPTION]... [FILE]
Multiply two square matrices of integers.

Read whitespace-separated integers from FILE, or from standard input when FILE
is absent or -: the size N (1-20), then the N*N elements of the first matrix
row by row, then the N*N elements of the second.  Print both matrices and
their product.  Elements and results are 64-bit signed integers; a product
that does not fit is reported as an error.

Options:
  -p, --prompt    write prompts to standard error before reading
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-matmult (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-matmult` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Data files are read as raw
  bytes: CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are
  ignored, but a Ctrl-Z byte in the middle of a file is an error, not an end-of-file mark.
  Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line (or twice after
  typing a number).
- **All platforms:** results are computed with 64-bit integers everywhere, so a product that
  fits on one system fits on all of them, and an overflow is reported on all of them.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-perc` (project 32), which also works on a square grid; `dp-taxes` (project 13), which
reads integer tokens the same way; `dp-wc` (project 04); `bc(1)`, `awk(1)`.
