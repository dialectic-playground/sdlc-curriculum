# dp-bfs-adj, dp-bfs-link — User Manual

| Field | Value |
| :-- | :-- |
| Products | `dp-bfs-adj` 1.0.0, `dp-bfs-link` 1.0.0 |
| Project | `47-bfs` — Graph Breadth-First Search: Adjacency Matrix vs. Adjacency List |
| Applies to | Linux, macOS, Windows |
| Specification | `SRS.md` (SRS-47), `shared/CLI-CONVENTIONS.md` |

---

## NAME

**dp-bfs-adj** — search a graph breadth-first using an adjacency matrix

**dp-bfs-link** — search a graph breadth-first using adjacency lists

## SYNOPSIS

```text
dp-bfs-adj  [-g FILE | --graph=FILE] [-s VERTEX | --start=VERTEX]
dp-bfs-link [-g FILE | --graph=FILE] [-s VERTEX | --start=VERTEX]
dp-bfs-adj  --help | --version
dp-bfs-link --help | --version
```

## DESCRIPTION

Both tools search a graph *breadth-first*: they visit the start vertex, then all of its
neighbors, then all the unvisited neighbors of those, and so on, and print one line for each
vertex at the moment it is first reached:

```text
Anger has been visited.
```

Each vertex reachable from the start is printed exactly once. Vertices that cannot be
reached from the start — because they lie in a separate part of the graph — are not printed.

The two tools differ only in how they store the graph, and therefore in the order in which
they look at a vertex's neighbors:

- **`dp-bfs-adj`** stores an *adjacency matrix*, a table with a row and a column per vertex.
  It looks at the neighbors of a vertex in **ascending order of vertex number**, as it scans
  the vertex's row from left to right.
- **`dp-bfs-link`** stores an *adjacency list* per vertex. The lists are built by reading the
  edges in order and inserting each new neighbor at the **head** of the list, so the tool
  looks at the neighbors of a vertex in the **reverse of the order in which its edges are
  listed**.

Both orders give a correct breadth-first search — every vertex one edge away from the start
is printed before every vertex two edges away, and so on — but within each distance the
orders can differ.

### The built-in graph

Without `-g`, both tools search the graph of the seven deadly sins, starting at Anger:

| Vertex | Name | Neighbors (`dp-bfs-adj` order) | Neighbors (`dp-bfs-link` order) |
| :-- | :-- | :-- | :-- |
| 0 | Anger | Lust, Envy, Gluttony | Gluttony, Envy, Lust |
| 1 | Lust | Anger, Envy, Pride | Pride, Envy, Anger |
| 2 | Envy | Anger, Lust, Pride | Pride, Lust, Anger |
| 3 | Gluttony | Anger, Sloth | Sloth, Anger |
| 4 | Pride | Lust, Envy, Covetousness | Covetousness, Envy, Lust |
| 5 | Sloth | Gluttony, Covetousness | Covetousness, Gluttony |
| 6 | Covetousness | Pride, Sloth | Sloth, Pride |

It is exactly the graph described by the file `sins.txt` shown below.

### Graph files

With `-g FILE`, the tools read the graph from *FILE* (`-` means standard input). A graph file
contains, separated by any spaces, tabs, or line breaks:

1. the number of vertices *n*, from 1 to 1000;
2. *n* names, one per vertex, numbered from 0 (a name is any word without spaces);
3. the number of edges *m*, from 0 to *n*(*n* − 1)/2;
4. *m* edges, each written as two vertex numbers.

Edges are undirected: `0 1` joins vertices 0 and 1 in both directions. An edge may not join
a vertex to itself, and the same two vertices may not be joined twice. The order of the edges
matters to `dp-bfs-link` only. This is the built-in graph as a file:

```text
7
Anger Lust Envy Gluttony Pride Sloth Covetousness
9
0 1
0 2
0 3
1 2
1 4
2 4
3 5
4 6
5 6
```

Numbers may have a sign and leading zeros. Files with Windows (CRLF) line endings read the
same as any other, and one or more Ctrl-Z bytes at the very end of a file (the end-of-file
mark of old MS-DOS files) are ignored. The whole file is checked before anything is printed:
if anything is wrong, the tools report the first problem and print no vertex at all.

## OPTIONS

Both tools have the same options.

**`-g FILE`, `--graph=FILE`**
: Read the graph from *FILE* instead of using the built-in graph. `-g -` reads standard input.

**`-s VERTEX`, `--start=VERTEX`**
: Start the search at vertex number *VERTEX* instead of 0. *VERTEX* is written with the
  digits `0`–`9` only and is at most 999; it must also be a vertex of the graph.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

Both tools follow the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- An option's value can be attached or separate: `-s4`, `-s 4`, `--start=4`, and
  `--start 4` are equivalent.
- Long options must be spelled out in full; `--sta` is not accepted.
- If an option is given more than once, the last one wins.
- The graph file is never given as a plain argument: `dp-bfs-adj sins.txt` is an error; write
  `dp-bfs-adj -g sins.txt`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning |
| :-- | :-- |
| 0 | Success: the search was printed, or help or version was printed |
| 1 | The graph file could not be read or is invalid, or the start vertex is not in the graph |
| 2 | Usage error: an invalid option or value, or an unexpected argument |

## DIAGNOSTICS

Every problem is reported on standard error as one line, and nothing is written to standard
output. Problems in a graph file name the file (`-` for standard input) and the line:

```text
$ dp-bfs-link -g bad-edge.txt
dp-bfs-link: bad-edge.txt:6: value out of range '7'
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `S:L: invalid integer 'K'` | A count or vertex number *K* is not a whole number | Write it in digits |
| `S:L: value out of range 'K'` | The number of vertices is not 1–1000, the number of edges is too large, or a vertex number is not in 0 … *n* − 1 | Correct the number |
| `S:L: unexpected end of input` | The file ends before all the names or edges announced | Add the missing data, or correct the counts |
| `S:L: self-loop 'U V'` | An edge joins a vertex to itself | Remove the edge |
| `S:L: duplicate edge 'U V'` | The same two vertices are joined twice (in either order) | Remove one of the edges |
| `S:L: unexpected token 'K'` | Something follows the last edge | Remove it, or correct the edge count |
| `start vertex 'V' out of range 0-N` | The start vertex is not a vertex of the graph | Choose a vertex from 0 to *N* |
| `F: No such file or directory` | The graph file *F* does not exist | Check the spelling and the current directory |
| `F: Permission denied` | You may not read *F* | Check the permissions |
| `F: Is a directory` | *F* is a directory | Name a file instead |
| `F: Not a directory` | Part of the path *F* is a file, not a directory | Correct the path |
| `F: Input/output error` | Any other failure to read *F* | Check the device or file system |
| `write error` | The output could not be written | Free space or redirect the output elsewhere |

Usage errors are written to standard error as two lines, and nothing is read:

```text
$ dp-bfs-adj -s 1000
dp-bfs-adj: invalid argument '1000' for '-s'
Try 'dp-bfs-adj --help' for more information.
```

| Message | Cause | Fix |
| :-- | :-- | :-- |
| `invalid option -- 'x'` | Unknown short option `-x` | Use `-g` or `-s` |
| `unrecognized option '--xyz'` | Unknown or abbreviated long option | Spell the option in full |
| `option requires an argument -- 'g'` | `-g` or `-s` given without a value | Supply a value |
| `option '--graph' requires an argument` | `--graph` or `--start` given without a value | Supply a value |
| `option '--help' doesn't allow an argument` | `--help=…` or `--version=…` | Remove the `=…` |
| `invalid argument '' for '-g'` | An empty file name | Give a non-empty file name |
| `invalid argument 'V' for '-s'` | The start vertex is not a number from 0 to 999 | Use digits only, at most 999 |
| `extra operand 'F'` | A file name given without `-g` | Use `-g F` |

## EXAMPLES

The built-in graph, with each representation:

```text
$ dp-bfs-adj
Anger has been visited.
Lust has been visited.
Envy has been visited.
Gluttony has been visited.
Pride has been visited.
Sloth has been visited.
Covetousness has been visited.
$ dp-bfs-link
Anger has been visited.
Gluttony has been visited.
Envy has been visited.
Lust has been visited.
Sloth has been visited.
Pride has been visited.
Covetousness has been visited.
```

Start at Pride:

```text
$ dp-bfs-adj --start=4
Pride has been visited.
Lust has been visited.
Envy has been visited.
Covetousness has been visited.
Anger has been visited.
Sloth has been visited.
Gluttony has been visited.
```

A graph with two separate parts and an isolated vertex (`islands.txt`):

```text
$ cat islands.txt
5
Ada Babbage Church Dijkstra Euler
2
0 1
2 3
$ dp-bfs-adj -g islands.txt
Ada has been visited.
Babbage has been visited.
$ dp-bfs-link -g islands.txt -s 4
Euler has been visited.
```

Read a graph from a pipeline:

```sh
printf '3\nX Y Z\n2\n0 2\n0 1\n' | dp-bfs-link -g -
```

## HELP OUTPUT

`dp-bfs-adj --help` and `dp-bfs-link --help` print exactly the following texts (every line
ends in LF). The help texts are part of the specification (CONV-23).

`dp-bfs-adj --help`:

```text
Usage: dp-bfs-adj [OPTION]...
Search a graph breadth-first, using an adjacency matrix, and print each
vertex as it is visited.

Without --graph, search the built-in graph of the seven deadly sins.  The
neighbors of a vertex are examined in ascending order of vertex number.

Options:
  -g, --graph=FILE      read the graph from FILE; - means standard input
  -s, --start=VERTEX    start at vertex number VERTEX (0-999, default 0)
      --help            display this help and exit
      --version         output version information and exit
```

`dp-bfs-link --help`:

```text
Usage: dp-bfs-link [OPTION]...
Search a graph breadth-first, using adjacency lists, and print each vertex as
it is visited.

Without --graph, search the built-in graph of the seven deadly sins.  The
neighbors of a vertex are examined in the reverse of the order in which its
edges are listed.

Options:
  -g, --graph=FILE      read the graph from FILE; - means standard input
  -s, --start=VERTEX    start at vertex number VERTEX (0-999, default 0)
      --help            display this help and exit
      --version         output version information and exit
```

## VERSION OUTPUT

```text
dp-bfs-adj (dialectic-playground) 1.0.0
dp-bfs-link (dialectic-playground) 1.0.0
```

## ENVIRONMENT

Both tools ignore all environment variables, including locale settings (`LANG`, `LC_ALL`).
Numbers are always read and written with ASCII digits; names are printed exactly as their
bytes appear in the graph file.

## PLATFORM NOTES

- **Windows:** output uses LF line endings, not CRLF. Graph files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but
  a Ctrl-Z byte in the middle of a file is ordinary data (and usually an error). Use a
  UTF-8-capable console to see non-ASCII names correctly; redirected output is always the
  names' original bytes.
- **macOS / Linux:** nothing special; `-g -` reads a graph piped in from another command.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build both tools
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove them again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-astar` (project 48), an informed search for shortest routes; `dp-queue1` and
`dp-queue2` (project 45), the queue that breadth-first search uses; `dp-elephnt1` and
`dp-elephnt2` (project 43), linked lists; `tsort(1)`.
