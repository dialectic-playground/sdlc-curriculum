<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-infix — User Manual](#dp-infix--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [The dialog](#the-dialog)
    - [Expressions](#expressions)
    - [Output](#output)
    - [Mistakes in an expression](#mistakes-in-an-expression)
    - [Working interactively](#working-interactively)
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

# dp-infix — User Manual

| Field         | Value                                                  |
| :------------ | :----------------------------------------------------- |
| Product       | `dp-infix` 1.0.0                                       |
| Project       | `46-infix` — Shunting-Yard Infix to Postfix Conversion |
| Applies to    | Linux, macOS, Windows                                  |
| Specification | `SRS.md` (SRS-46), `shared/CLI-CONVENTIONS.md`         |

---

## NAME

**dp-infix** — convert infix expressions to postfix notation

## SYNOPSIS

```text
dp-infix [-p | --prompt] [FILE]
dp-infix --help
dp-infix --version
```

## DESCRIPTION

`dp-infix` reads arithmetic expressions in the usual _infix_ notation, where each operator
stands between its operands, and rewrites each one in _postfix_ (reverse Polish) notation,
where each operator follows its operands and no parentheses are needed:

```text
Infix:   (A + B) * C - D / E
Postfix: A B + C * D E / -
```

It reads from _FILE_, or from standard input when there is no _FILE_ or _FILE_ is `-`.

### The dialog

After each expression, `dp-infix` asks whether you want to convert another one. The input
therefore alternates between an expression line and an answer line:

- `y` or `Y` asks for another expression;
- `n` or `N` ends the session, and so does the end of the input.

Blanks around an answer are ignored. Any other answer — `yes`, an empty line, a second
expression typed by mistake — is reported as an `invalid answer` and ends the run with exit
status 1, because the rest of the input would be read out of step.

A prepared file of exercises looks like this:

```text
(A + B) * C
y
A - B - C
n
```

### Expressions

- **Operands** are names or numbers made of ASCII letters and digits: `A`, `x1`, `rate`, `40`.
  A run of letters and digits is one operand, so `AB` is a single operand; write `A * B` for a
  product. Operands are copied to the output exactly as written (`007` stays `007`).
- **Operators** are `+`, `-`, `*`, `/`, and `%`. `*`, `/`, and `%` bind more tightly than `+`
  and `-`, and operators of equal precedence group from the left: `A - B - C` means
  `(A - B) - C` and becomes `A B - C -`.
- **Parentheses** `(` and `)` group as usual and never appear in the postfix form.
- Spaces and tabs between tokens are optional: `A+B*C` and `A + B * C` are the same.

Unary operators (`-A`), functions, and decimal points are not part of the notation.

### Output

For each valid expression, `dp-infix` writes two lines to standard output: `Infix:` and three
spaces, followed by the expression as you typed it (without leading or trailing blanks), and
`Postfix:` and one space, followed by the postfix tokens separated by single spaces. Nothing
else is ever written to standard output.

### Mistakes in an expression

A malformed expression is reported on standard error with its line number and the first
problem found, scanning from left to right; no output lines are written for it, and the dialog
goes on with the `Another?` question. When the session ends, the exit status is 1 if any
expression was rejected.

### Working interactively

Each conversion appears as soon as you press Enter. End the input with **Ctrl-D** on Linux and
macOS, or **Ctrl-Z** followed by **Enter** in a Windows console, at either question. With
`--prompt`, `dp-infix` asks for each line:

```text
$ dp-infix --prompt
Enter infix expression: A + B * C
Infix:   A + B * C
Postfix: A B C * +
Another? (y/n) y
Enter infix expression: (A + B
dp-infix: -:3: unmatched '('
Another? (y/n) n
```

The prompts are written to standard error, so `dp-infix --prompt > answers.txt` saves only the
results.

Files with Windows (CRLF) line endings, a last line without a line feed, and one or more Ctrl-Z
bytes at the very end (the end-of-file mark of old MS-DOS files) are all read correctly.

## OPTIONS

**`-p`, `--prompt`**
: Before each expression is read, write `Enter infix expression:o standard error, and
before each answer is read, write `Another? (y/n)A last prompt appears before the end of
the input is noticed.

**`--help`**
: Display the help text below and exit with status 0.

**`--version`**
: Display the version line and exit with status 0.

### Option syntax

`dp-infix` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`):

- Long options must be spelled out in full; `--prom` is not accepted.
- Options and the file name can be given in any order: `dp-infix sheet.txt -p` works.
- `--` ends option processing, so `dp-infix -- -p` reads a file named `-p`.
- `--help` and `--version` take effect as soon as they are reached while reading the arguments
  from left to right, unless an earlier argument was invalid.

## EXIT STATUS

| Status | Meaning                                                                                          |
| :----- | :----------------------------------------------------------------------------------------------- |
| 0      | Success: every expression was converted (an empty input is fine), or help or version was printed |
| 1      | An expression was rejected, an answer was invalid, or the input could not be read                |
| 2      | Usage error: an invalid option or more than one file                                             |

## DIAGNOSTICS

Problems with an expression name the input (`-` for standard input) and the line number. The
dialog continues after them:

```text
$ dp-infix errors.txt
dp-infix: errors.txt:1: unmatched '('
dp-infix: errors.txt:3: unexpected operator '*'
dp-infix: errors.txt:5: invalid character '$'
Infix:   A + B
Postfix: A B +
```

(Standard error and standard output are shown together here; the results go to standard
output.)

| Message                             | Cause                                                                                                                            | Fix                                                      |
| :---------------------------------- | :------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------- |
| `S:L: invalid character 'C'`        | A character that is not a letter, digit, operator, parenthesis, space, or tab; bytes outside printable ASCII are shown as `\xHH` | Remove it; write operands with letters and digits only   |
| `S:L: unexpected operand 'X'`       | Two operands in a row, as in `A B` or `2 x`                                                                                      | Put an operator between them                             |
| `S:L: unexpected operator 'O'`      | An operator with no operand before it, as in `-A`, `A * * B`, or `(+ A)`                                                         | Supply the missing operand; unary minus is not supported |
| `S:L: unexpected '('`               | A parenthesis directly after an operand, as in `A(B)`                                                                            | Write the operator: `A * (B)`                            |
| `S:L: unexpected ')'`               | A `)` with no operand before it, as in `()` or `(A +)`                                                                           | Supply the missing operand                               |
| `S:L: unmatched ')'`                | A `)` with no `(` to close                                                                                                       | Remove it or add the `(`                                 |
| `S:L: empty expression`             | The expression line is empty or holds only blanks                                                                                | Type an expression                                       |
| `S:L: unexpected end of expression` | The line ends after an operator or `(`                                                                                           | Complete the expression                                  |
| `S:L: unmatched '('`                | A `(` is never closed                                                                                                            | Add the `)`                                              |

Problems that end the run (exit status 1):

| Message                        | Cause                                                            | Fix                                                             |
| :----------------------------- | :--------------------------------------------------------------- | :-------------------------------------------------------------- |
| `S:L: invalid answer 'A'`      | The answer line is not `y`, `Y`, `n`, or `N`                     | Answer `y` or `n`; check that expressions and answers alternate |
| `F: No such file or directory` | _F_ does not exist                                               | Check the spelling and the current directory                    |
| `F: Permission denied`         | You may not read _F_                                             | Check the file's permissions                                    |
| `F: Is a directory`            | _F_ is a directory                                               | Name a file instead                                             |
| `F: Not a directory`           | Part of the path _F_ is a file, not a directory                  | Correct the path                                                |
| `F: Input/output error`        | Any other read failure                                           | Check the device or file system                                 |
| `write error`                  | The results could not be written (for example, the disk is full) | Free space or redirect the output elsewhere                     |

Usage errors are written to standard error as two lines; nothing is read and nothing is
written to standard output:

```text
$ dp-infix readme.txt mixed.txt
dp-infix: extra operand 'mixed.txt'
Try 'dp-infix --help' for more information.
```

| Message                                       | Cause                                                   | Fix                          |
| :-------------------------------------------- | :------------------------------------------------------ | :--------------------------- |
| `invalid option -- 'x'`                       | Unknown short option `-x`                               | Use `-p`                     |
| `unrecognized option '--xyz'`                 | Unknown or abbreviated long option                      | Spell the option in full     |
| `option '--prompt' doesn't allow an argument` | A value was given with `=` to an option that takes none | Remove the `=…`              |
| `extra operand 'F'`                           | More than one file was named                            | Run `dp-infix` once per file |

## EXAMPLES

Convert one expression:

```text
$ printf 'A + B * C\n' | dp-infix
Infix:   A + B * C
Postfix: A B C * +
```

Convert a sheet of exercises, answering `y` between expressions:

```text
$ printf '(A + B) * (C - D)\ny\nA - B - C\nn\n' | dp-infix
Infix:   (A + B) * (C - D)
Postfix: A B + C D - *
Infix:   A - B - C
Postfix: A B - C -
```

Names and numbers as operands:

```text
$ printf 'rate * (hours + 40) %% 7\n' | dp-infix
Infix:   rate * (hours + 40) % 7
Postfix: rate hours 40 + * 7 %
```

Check a file of expressions in a script:

```sh
if dp-infix sheet.txt > answers.txt; then
    echo "every expression converted"
fi
```

## HELP OUTPUT

`dp-infix --help` prints exactly the following text (every line ends in LF). The help text is
part of the specification (CONV-23):

```text
Usage: dp-infix [OPTION]... [FILE]
Convert infix expressions to postfix (reverse Polish) notation.

Read FILE, or standard input when FILE is absent or -.  Lines alternate
between an infix expression and the answer to 'Another? (y/n)': y or Y asks
for another expression; n, N, or the end of the input ends the session.
Operands are runs of letters and digits; the operators are + - * / % (all
left-associative, * / % before + -), and parentheses group.

Options:
  -p, --prompt    write the prompts to standard error before each read
      --help      display this help and exit
      --version   output version information and exit
```

## VERSION OUTPUT

```text
dp-infix (dialectic-playground) 1.0.0
```

## ENVIRONMENT

`dp-infix` ignores all environment variables, including locale settings (`LANG`, `LC_ALL`).

## PLATFORM NOTES

- **Windows:** end keyboard input with Ctrl-Z followed by Enter. Files are read as raw bytes:
  CRLF line endings are accepted, and Ctrl-Z bytes at the very end of a file are ignored, but a
  Ctrl-Z byte anywhere else is an invalid character. Output uses LF line endings, not CRLF.
- **macOS / Linux:** end keyboard input with Ctrl-D at the start of a line. In `printf`
  format strings, write `%` as `%%`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`dp-stack1`, `dp-stack2` (project 45), the stack abstract data type this conversion relies on;
`dp-calc` (project 37), an interactive calculator; `dc(1)`, which evaluates postfix
expressions; `bc(1)`.
