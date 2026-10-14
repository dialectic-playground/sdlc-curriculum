# dp-sort-bench — User Manual

| Field | Value |
| :-- | :-- |
| Product | `dp-sort-bench` 1.0.0 |
| Project | `35-sort-bench` — Empirical Algorithm Runtime Benchmarking |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-35), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-sort-bench** — compare selection sort and quicksort on random arrays of growing size

## SYNOPSIS

```text
dp-sort-bench [-s LIST | --sizes=LIST] [--seed=SEED] [-t | --time]
dp-sort-bench --help
dp-sort-bench --version
```

## DESCRIPTION

`dp-sort-bench` generates an array of random integers from 0 to 32767 for each size in *LIST*
(by default 1000, 2000, and 4000), sorts one copy of it with **selection sort** and another
copy with **quicksort**, and reports for each sort how many comparisons and swaps it made and
whether its result is correctly sorted.

```text
Array size: 1000
	Algorithm: Selection Sort
		Comparisons = 499500
		Swaps = 990
		Sorted = yes
	Algorithm: Quicksort
		Comparisons = 11412
		Swaps = 5980
		Sorted = yes
```

The indented lines start with one or two TAB characters, and a blank line separates the sizes.

### What is counted

- A **comparison** is one check of whether one array element is smaller than another. Loop
  bookkeeping is not counted.
- A **swap** is one exchange of two elements at different positions.

Selection sort always makes *n*(*n* − 1)/2 comparisons, so doubling the size quadruples them.
Quicksort makes a small multiple of *n* log₂ *n* comparisons on random data, so doubling the
size only about doubles them. Because the counts do not depend on the computer, the report is the same
on every machine for the same sizes and seed.

### The algorithms

- **Selection sort:** for each position from the left, find the first smallest element of the
  rest of the array and exchange it into that position.
- **Quicksort:** move the middle element of the range to its left end as the pivot; scan the
  range once from left to right, gathering the elements smaller than the pivot just after it;
  put the pivot between the two parts; sort both parts the same way.

### Random arrays

The arrays come from the portable generator of the ANSI C standard (the same one every
curriculum tool uses), started from *SEED* (default 1). The sizes are processed in order and
each array takes the next numbers from the one generator, so `dp-sort-bench -s 1000` reports
the same first block as `dp-sort-bench`.

### Timing

With `--time`, each sort also reports its elapsed time, measured with the system's monotonic
clock, such as:

```text
	Algorithm: Selection Sort
		Time = 0.000731 seconds
		Comparisons = 499500
```

Times vary from run to run and from machine to machine; the other lines never change.

## OPTIONS

**`-s LIST`, `--sizes=LIST`**
: Benchmark the sizes in *LIST*, in order: whole numbers from 0 to 100000, separated by
  commas without spaces, for example `--sizes=10,20,40`. Sizes may repeat. The default is
  `1000,2000,4000`.

**`--seed=SEED`**
: Start the random-number generator from *SEED*, a whole number from 0 to 4294967295
  (digits only). The default is 1.

**`-t`, `--time`**
: Also report the elapsed time of each sort, in seconds with six decimals.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-sort-bench` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-s10`, `-s 10`, `--sizes=10`, and
  `--sizes 10` are equivalent.
- Long options must be spelled out in full; `--size` is not accepted.
- If an option is given more than once, the last one wins: `-s 5 -s 7` benchmarks size 7.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid. Note that `--sizes --help` gives
  `--help` to `--sizes` as its value, which is invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the report was written and every result was correctly sorted, or help or version was printed |
| 1 | A sort produced a wrong result (this indicates a defective implementation), or the output could not be written |
| 2 | Usage error: an invalid option or value, or an operand |

## DIAGNOSTICS

Usage errors are written to standard error as two lines; nothing is written to standard
output:

```text
$ dp-sort-bench -s 10,,20
dp-sort-bench: invalid argument '10,,20' for '-s'
Try 'dp-sort-bench --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-s` or `-t` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 's'` | `-s` given without a value | Supply a size list |
| `option '--sizes' requires an argument` | `--sizes` or `--seed` given without a value | Supply a value |
| `option '--time' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…` |
| `invalid argument 'L' for '--sizes'` | The size list *L* is empty, has an empty item, a sign or space, or a size above 100000 | Use sizes 0–100000 separated by single commas |
| `invalid argument 'S' for '--seed'` | *S* is not a whole number from 0 to 4294967295 | Use digits only, within the range |
| `extra operand 'X'` | `dp-sort-bench` takes no operands | Remove *X*, or use `--sizes` |

Runtime errors:

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `verification failed` | At least one sort reported `Sorted = no` | Fix the implementation of that sort |
| `write error` | The report could not be written (for example, the disk is full) | Free space or redirect the output elsewhere |

## EXAMPLES

Small arrays, quick to run and to follow by hand:

```text
$ dp-sort-bench --sizes=0,2,3
Array size: 0
	Algorithm: Selection Sort
		Comparisons = 0
		Swaps = 0
		Sorted = yes
	Algorithm: Quicksort
		Comparisons = 0
		Swaps = 0
		Sorted = yes

Array size: 2
	Algorithm: Selection Sort
		Comparisons = 1
		Swaps = 1
		Sorted = yes
	Algorithm: Quicksort
		Comparisons = 1
		Swaps = 1
		Sorted = yes

Array size: 3
	Algorithm: Selection Sort
		Comparisons = 3
		Swaps = 0
		Sorted = yes
	Algorithm: Quicksort
		Comparisons = 2
		Swaps = 2
		Sorted = yes
```

(With `--sizes=0,2,3` the array of size 3 happens to be sorted already: selection sort still
makes all its comparisons but no swap.)

Compare the growth of the comparison counts for the default sizes:

```text
$ dp-sort-bench | grep -e size -e Comparisons
Array size: 1000
		Comparisons = 499500
		Comparisons = 11412
Array size: 2000
		Comparisons = 1999000
		Comparisons = 26932
Array size: 4000
		Comparisons = 7998000
		Comparisons = 52726
```

A different random array:

```sh
dp-sort-bench --seed=7 --sizes=100
```

Measure the time on this machine (the times shown will differ):

```sh
dp-sort-bench --time --sizes=4000,8000,16000
```

## HELP OUTPUT

`dp-sort-bench --help` prints exactly the following text (every line ends in LF). The help text
is part of the specification (CONV-23):

```text
Usage: dp-sort-bench [OPTION]...
Compare selection sort and quicksort on random arrays of growing size.

For each size (default 1000,2000,4000) an array of pseudo-random integers
0-32767 is generated, and a copy of it is sorted by each algorithm.  The
report gives the number of comparisons and swaps each sort made and whether
its result is sorted.

Options:
  -s, --sizes=LIST   comma-separated array sizes, each 0-100000
                       (default 1000,2000,4000)
      --seed=SEED    seed the pseudo-random generator (0-4294967295, default 1)
  -t, --time         also report the elapsed time of each sort in seconds
      --help         display this help and exit
      --version      output version information and exit
```

## VERSION OUTPUT

```text
dp-sort-bench (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-sort-bench` ignores all environment variables, including locale settings (`LANG`,
`LC_ALL`). Numbers are always written with ASCII digits and no digit grouping.

## PLATFORM NOTES

- **All platforms:** the report without `--time` is identical everywhere. Elapsed times are
  measured with the platform's monotonic clock (`clock_gettime(CLOCK_MONOTONIC)` on Linux,
  `mach_absolute_time` on macOS, `QueryPerformanceCounter` on Windows, or the language
  runtime's equivalent), so changes to the system time never distort them. For steadier
  timings, close other programs and repeat the run.
- **Windows:** output uses LF line endings, not CRLF. The TAB characters display as tab stops
  in a console; in a file they are single `0x09` bytes.
- **Interpreted runtimes:** times include the runtime's own overhead and may vary more between
  runs; the counts are unaffected.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-sort-host` and `dp-sort-child` (project 34), which sort with selection sort in two
concurrent halves; `dp-phone` (project 31), which sorts with selection sort; `dp-sales`
(project 42), which sorts with quicksort; `sort(1)`, `time(1)`.
