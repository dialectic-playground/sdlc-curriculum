<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [dp-kv — User Manual](#dp-kv--user-manual)
  - [NAME](#name)
  - [SYNOPSIS](#synopsis)
  - [DESCRIPTION](#description)
    - [Commands](#commands)
    - [Safety](#safety)
  - [OPTIONS](#options)
    - [Global options (before COMMAND)](#global-options-before-command)
    - [Command options (after COMMAND)](#command-options-after-command)
    - [Option syntax](#option-syntax)
  - [STORE FILE FORMAT](#store-file-format)
  - [HTTP API](#http-api)
  - [EXIT STATUS](#exit-status)
  - [DIAGNOSTICS](#diagnostics)
  - [EXAMPLES](#examples)
  - [HELP OUTPUT](#help-output)
  - [VERSION OUTPUT](#version-output)
  - [ENVIRONMENT](#environment)
  - [FILES](#files)
  - [PLATFORM NOTES](#platform-notes)
  - [INSTALLATION](#installation)
  - [SEE ALSO](#see-also)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# dp-kv — User Manual

| Field         | Value                                                      |
| :------------ | :--------------------------------------------------------- |
| Product       | `dp-kv` 1.0.0                                              |
| Project       | `09-kv-store` — Local Key-Value Storage Engine (CLI + API) |
| Applies to    | Linux, macOS, Windows                                      |
| Specification | `SRS.md` (SRS-09), `shared/CLI-CONVENTIONS.md`             |

---

## NAME

**dp-kv** — store text values under keys in a local JSON file, or serve them over HTTP

## SYNOPSIS

```text
dp-kv [-s PATH | --store=PATH] set KEY VALUE
dp-kv [-s PATH | --store=PATH] get KEY
dp-kv [-s PATH | --store=PATH] del KEY
dp-kv [-s PATH | --store=PATH] list [-p PREFIX | --prefix=PREFIX]
dp-kv [-s PATH | --store=PATH] export
dp-kv [-s PATH | --store=PATH] import [-r | --replace] FILE
dp-kv [-s PATH | --store=PATH] serve [--host=ADDR] [--port=N]
dp-kv --help
dp-kv --version
```

## DESCRIPTION

`dp-kv` is a small key-value store kept in a single JSON file, the _store_. Each entry is a
_key_, such as `user:1001`, and a text _value_, such as `Ada Lovelace`.

The store is the file named by `--store`; if that option is not given, the file named by the
environment variable `DP_KV_STORE`; and otherwise `kv.json` in the current directory. A store
that does not exist yet behaves as an empty store, and is created by the first command that
changes it.

**Keys** are 1 to 256 characters long and may contain only the letters `A`–`Z` and `a`–`z`, the
digits `0`–`9`, and the four characters `.` `_` `:` `-`. Keys are case-sensitive: `Name` and
`name` are different keys. A colon is a convenient separator for groups of keys (`user:1001`,
`user:1002`), which `list --prefix` can select.

**Values** are any text, including spaces, line breaks, and non-ASCII characters such as `Zoë`,
up to 65536 bytes when encoded as UTF-8. Values are stored and printed exactly; the empty value
is allowed.

### Commands

**`set KEY VALUE`**
: Store _VALUE_ under _KEY_, replacing any previous value. Prints nothing.

**`get KEY`**
: Print the value stored under _KEY_, followed by a line feed. If _KEY_ is not in the store,
print `dp-kv: key not found: KEY` on standard error and exit with status 1.

**`del KEY`**
: Remove _KEY_ and its value. Prints nothing. If _KEY_ is not in the store, report
`key not found` and exit with status 1.

**`list [--prefix=PREFIX]`**
: Print every key, one per line, in byte order (uppercase letters before lowercase ones, as in
ASCII). With `--prefix`, print only the keys that start with _PREFIX_.

**`export`**
: Print the whole store as a canonical JSON document — exactly the bytes `dp-kv` writes to the
store file (see **STORE FILE FORMAT**). Redirect it to a file to make a backup.

**`import [--replace] FILE`**
: Read a store document from _FILE_ (or from standard input if _FILE_ is `-`) and _merge_ it
into the store: imported keys are added, existing keys with the same name are overwritten,
and other keys are kept. With `--replace`, the store's contents become exactly the imported
keys. _FILE_ may be any valid store document — an `export`, a store file, or hand-written JSON
in the same format — formatted in any way. If _FILE_ is invalid, nothing is changed.

**`serve [--host=ADDR] [--port=N]`**
: Serve the store over HTTP (see **HTTP API**) until interrupted with Ctrl+C (or SIGTERM).
On startup it prints one line on standard error, such as
`dp-kv: listening on http://127.0.0.1:7700`.

### Safety

Every change is _atomic_ and _durable_: `dp-kv` writes the new contents to a temporary file
next to the store (`PATH.tmp`), flushes it to disk, and then renames it over the store. A crash
or power failure therefore leaves either the old or the new store, never a damaged one.

Several `dp-kv` processes — command-line invocations and servers — can use the same store at the
same time. Each one locks the file `PATH.lock` next to the store: commands that only read share
the lock, and commands that change the store take it exclusively for the whole
read-modify-write, so no update is lost. If the lock is not available within 5 seconds, the
command gives up with `store is locked`. The `.lock` file is created automatically, is normally
empty, and should be left in place.

If the store file is damaged or is not a dp-kv store, `dp-kv` reports
`not a valid dp-kv store file` and refuses to overwrite it, so you can repair or recover it by
hand.

## OPTIONS

### Global options (before COMMAND)

**`-s PATH`, `--store=PATH`**
: Use the store file _PATH_. _PATH_ must not be empty.

**`--help`**
: Display the help text below and exit with status 0. It is also accepted after _COMMAND_.

**`--version`**
: Display the version line and exit with status 0. It is also accepted after _COMMAND_.

### Command options (after COMMAND)

**`-p PREFIX`, `--prefix=PREFIX`** (`list`)
: List only the keys that start with _PREFIX_. _PREFIX_ must be empty or follow the same rules
as a key.

**`-r`, `--replace`** (`import`)
: Replace the store's contents with the imported keys instead of merging.

**`--host=ADDR`** (`serve`)
: Listen on the IP address _ADDR_, written numerically (for example `127.0.0.1`, `::1`, or
`0.0.0.0`). Host names such as `localhost` are not accepted. The default `127.0.0.1` accepts
connections from this computer only.

**`--port=N`** (`serve`)
: Listen on TCP port _N_, from 0 to 65535 (default 7700). With `--port=0`, the system picks a
free port; the startup line shows which one.

### Option syntax

`dp-kv` follows the curriculum's common conventions (`shared/CLI-CONVENTIONS.md`), with one
addition: the command line has two parts.

- Global options (`--store`) go **before** the command word; command options (`--prefix`,
  `--replace`, `--host`, `--port`) go **after** it. `dp-kv get alpha --store=a.json` is an
  error; write `dp-kv --store=a.json get alpha`.
- After the command word, options and operands can be mixed: `dp-kv list -p user:` and
  `dp-kv list --prefix user:` are equivalent.
- A value that starts with `-` would be read as an option. Put `--` before it:
  `dp-kv set -- offset -5`.
- Long options must be spelled out in full. If an option is given twice, the last one wins.
- `--help` and `--version` take effect as soon as they are reached while reading the
  arguments from left to right, unless an earlier argument was invalid.

## STORE FILE FORMAT

The store is UTF-8 JSON in one exact layout, so that the same contents always produce the same
bytes on every operating system and in every implementation:

```text
{
  "format": "dp-kv",
  "version": 1,
  "data": {
    "alpha": "first value",
    "user:1001": "Ada Lovelace"
  }
}
```

Keys appear in byte order, indented by four spaces; every line ends with a line feed (LF), also
on Windows. In values, `"` and `\` are written as `\"` and `\\`, tab, line feed, carriage
return, backspace, and form feed as `\t`, `\n`, `\r`, `\b`, and `\f`, other control characters
as `\u` and four lowercase hexadecimal digits, and every other character — including non-ASCII
letters and emoji — as itself. An empty store has `"data": {}`.

`dp-kv` reads any valid JSON with exactly the members `format` (`"dp-kv"`), `version` (`1`), and
`data` (an object of keys and string values), however it is formatted. JSON extensions such as
comments or trailing commas, duplicate member names, and a leading byte-order mark make a file
invalid.

## HTTP API

`dp-kv serve` offers this API. Every response with a body is a single line of compact JSON
(`Content-Type: application/json; charset=utf-8`), and the server closes the connection after
each response.

| Method and path                           | Request body      | Success response                                                                    |
| :---------------------------------------- | :---------------- | :---------------------------------------------------------------------------------- |
| `GET /v1/health`                          | —                 | `200` `{"status":"ok"}`                                                             |
| `GET /v1/keys` or `GET /v1/keys?prefix=P` | —                 | `200` `{"keys":["a","b"]}`                                                          |
| `GET /v1/keys/KEY`                        | —                 | `200` `{"key":"KEY","value":"..."}`                                                 |
| `PUT /v1/keys/KEY`                        | `{"value":"..."}` | `201` (new key, with `Location`) or `200` (replaced), `{"key":"KEY","value":"..."}` |
| `DELETE /v1/keys/KEY`                     | —                 | `204`, no body                                                                      |

Errors have the body `{"error":{"code":"CODE","message":"MESSAGE"}}`:

| Status | Code                                  | Meaning                                                  |
| :----- | :------------------------------------ | :------------------------------------------------------- |
| 400    | `invalid_key`, `invalid_prefix`       | The key or prefix breaks the key rules                   |
| 400    | `invalid_json`, `invalid_body`        | The `PUT` body is not JSON, or not `{"value": "<text>"}` |
| 400    | `bad_request`                         | The request is not valid HTTP                            |
| 404    | `key_not_found`                       | The key is not in the store                              |
| 404    | `not_found`                           | Unknown path                                             |
| 405    | `method_not_allowed`                  | Unsupported method; see the `Allow` header               |
| 411    | `length_required`                     | A `PUT` without `Content-Length`                         |
| 413    | `payload_too_large`, `value_too_long` | Body over 524288 bytes, or value over 65536 bytes        |
| 500    | `store_error`                         | The store file is invalid or unreadable                  |
| 503    | `store_locked`                        | The store stayed locked for 5 seconds                    |

The API has no authentication. Do not use `--host=0.0.0.0` (or another non-loopback address)
on a network you do not trust.

## EXIT STATUS

| Status | Meaning                                                                                 |
| :----- | :-------------------------------------------------------------------------------------- |
| 0      | Success; `serve` was stopped with Ctrl+C or SIGTERM                                     |
| 1      | Key not found, invalid store or import file, file error, store locked, or cannot listen |
| 2      | Usage error: invalid option, command, operand, key, or value                            |

## DIAGNOSTICS

Errors are written to standard error, and nothing is written to standard output. Usage errors
add a second line pointing to `--help`:

```text
$ dp-kv fetch colour
dp-kv: unknown command 'fetch'
Try 'dp-kv --help' for more information.
```

| Message                                                 | Cause                                            | Fix                                                             |
| :------------------------------------------------------ | :----------------------------------------------- | :-------------------------------------------------------------- |
| `missing command`                                       | No command word                                  | Add `set`, `get`, `del`, `list`, `export`, `import`, or `serve` |
| `unknown command 'fetch'`                               | Misspelled command                               | Check the command list in `--help`                              |
| `missing operand` / `extra operand 'x'`                 | Wrong number of KEY/VALUE/FILE operands          | See SYNOPSIS; quote values containing spaces                    |
| `unrecognized option '--store=x'`                       | Option in the wrong part of the line, or unknown | Put `--store` before the command                                |
| `invalid argument '' for '--store'`                     | Empty store path                                 | Give a file name                                                |
| `invalid key 'bad key'`                                 | Key breaks the key rules                         | Use only `A-Z a-z 0-9 . _ : -`, at most 256 characters          |
| `value is not valid UTF-8`                              | Value bytes are not UTF-8 text                   | Convert the text to UTF-8                                       |
| `value too long (maximum 65536 bytes)`                  | Value exceeds 64 KiB                             | Store a shorter value                                           |
| `invalid argument 'user 1' for '--prefix'`              | Prefix breaks the key rules                      | Use key characters only                                         |
| `invalid argument 'localhost' for '--host'`             | Host name or malformed address                   | Use a numeric address such as `127.0.0.1`                       |
| `invalid argument '70000' for '--port'`                 | Port not a number from 0 to 65535                | Choose another port                                             |
| `key not found: colour`                                 | `get` or `del` of a key that is not stored       | Check `dp-kv list`                                              |
| `kv.json: not a valid dp-kv store file`                 | Store damaged or not a dp-kv file                | Restore it from an export, or fix it by hand                    |
| `backup.json: not a valid dp-kv store file`             | Import file invalid                              | Check the file's format; the store is unchanged                 |
| `kv.json: store is locked`                              | Another process held the lock for 5 seconds      | Retry; look for a stuck process                                 |
| `kv.json: Is a directory`                               | The store path names a directory                 | Choose a file name                                              |
| `kv.json: Permission denied`                            | No permission to read or replace the store       | Check file and directory permissions                            |
| `kv.json.lock: Permission denied`                       | The lock file cannot be created                  | Make the directory writable                                     |
| `127.0.0.1:7700: cannot listen: Address already in use` | Another program uses the port                    | Use `--port` with another port, or `--port=0`                   |

## EXAMPLES

Store and read values:

```text
$ dp-kv set editor vim
$ dp-kv set greeting 'Hello, World!'
$ dp-kv get greeting
Hello, World!
```

List keys, all or by prefix:

```text
$ dp-kv set user:1001 'Ada Lovelace'
$ dp-kv set user:1002 'Grace Hopper'
$ dp-kv list
editor
greeting
user:1001
user:1002
$ dp-kv list --prefix=user:
user:1001
user:1002
```

Delete a key and react to a missing key in a script:

```sh
dp-kv del editor
if ! value=$(dp-kv get editor 2>/dev/null); then
    echo "editor is not set"
fi
```

Use a store elsewhere, per command or per session:

```sh
dp-kv --store="$HOME/notes.json" set todo 'buy milk'
export DP_KV_STORE="$HOME/notes.json"
dp-kv get todo
```

Back up, restore, and combine stores:

```sh
dp-kv export > backup.json
dp-kv import --replace backup.json      # restore exactly
dp-kv --store=team.json import mine.json # merge my keys into the team store
dp-kv export | ssh host dp-kv import -   # copy to another machine
```

Serve the store and use it with `curl`:

```text
$ dp-kv serve --port=8080 &
dp-kv: listening on http://127.0.0.1:8080
$ curl -X PUT -d '{"value":"dark"}' http://127.0.0.1:8080/v1/keys/config:theme
{"key":"config:theme","value":"dark"}
$ curl 'http://127.0.0.1:8080/v1/keys?prefix=config:'
{"keys":["config:theme"]}
$ curl -i -X DELETE http://127.0.0.1:8080/v1/keys/config:theme
HTTP/1.0 204 No Content
...
$ kill %1
```

Show the version:

```text
$ dp-kv --version
dp-kv (dialectic-playground) 1.0.0
```

## HELP OUTPUT

`dp-kv --help` (and `dp-kv COMMAND --help`) prints exactly the following text (every line ends
in LF). The help text is part of the specification (CONV-23):

```text
Usage: dp-kv [--store=PATH] COMMAND [ARG]...
Store text values under keys in a local JSON file, or serve them over HTTP.

Commands:
  set KEY VALUE             store VALUE under KEY, replacing any previous value
  get KEY                   print the value stored under KEY
  del KEY                   remove KEY and its value
  list [--prefix=P]         print the keys in byte order, one per line
  export                    print the whole store as canonical JSON
  import [--replace] FILE   merge the store document FILE (- for stdin) in
  serve [--host=ADDR] [--port=N]
                            serve the store over HTTP until interrupted

The store is PATH if --store is given, else $DP_KV_STORE if it is set and not
empty, else kv.json. Keys are 1-256 characters from A-Z a-z 0-9 . _ : - and
values are UTF-8 text of at most 65536 bytes. Global options go before
COMMAND; command options go after it. Use -- before a VALUE that starts with -.

Global options:
  -s, --store=PATH          use the store file PATH
      --help                display this help and exit
      --version             output version information and exit

Command options:
  -p, --prefix=P            list: only keys that start with P
  -r, --replace             import: replace all contents instead of merging
      --host=ADDR           serve: IP address to listen on (default 127.0.0.1)
      --port=N              serve: TCP port, 0 for any free one (default 7700)
```

## VERSION OUTPUT

```text
dp-kv (dialectic-playground) 1.0.0
```

## ENVIRONMENT

**`DP_KV_STORE`**
: Store path used when `--store` is not given. An empty value is ignored.

All other environment variables, including locale settings (`LANG`, `LC_ALL`), are ignored.

## FILES

**`kv.json`**
: The default store, in the current directory.

**`PATH.lock`**
: Lock file next to the store _PATH_. Created on first use and never removed. Delete it only
when no `dp-kv` process is running.

**`PATH.tmp`**
: Temporary file used while a change is written. It exists only briefly; a leftover one from a
crash is harmless and is overwritten by the next change.

## PLATFORM NOTES

- **Locking.** On Linux and macOS, `dp-kv` locks `PATH.lock` with `flock(2)`, so you can
  coordinate your own scripts with it: `flock kv.json.lock -c '...'` (Linux `util-linux`)
  blocks `dp-kv` writers while the command runs. On Windows it uses `LockFileEx` on the first
  byte of `PATH.lock`. Locks are advisory: programs that ignore them, such as a text editor, can
  still change the store, so stop writers before editing it by hand.
- **Network drives.** Keep stores on a local disk. Locking and atomic rename are unreliable on
  many network file systems (NFS, SMB shares).
- **Windows:** output uses LF line endings, not CRLF, and redirected output is always UTF-8.
  Quote values with spaces in PowerShell with double quotes:
  `dp-kv set greeting "Hello, World!"`. Stop a server with Ctrl+C or Ctrl+Break. The first time
  a server listens on a non-loopback address, Windows Defender Firewall may ask for permission.
- **Path errors.** When a directory in `--store` is actually a file, Linux and macOS report
  `Not a directory`, while Windows reports `No such file or directory`.
- **macOS / Linux:** in shells such as bash or zsh, quote values that contain `!`, `$`, or
  spaces: `dp-kv set greeting 'Hello, World!'`.

## INSTALLATION

From an implementation's project directory (see the curriculum `README.md`):

```sh
make all          # build
make install      # install into ~/.local/bin (override with PREFIX=/some/prefix)
make uninstall    # remove it again
```

Make sure the install directory is on your `PATH`.

## SEE ALSO

`sqlite3(1)`, `redis-cli(1)`, `flock(1)`, `flock(2)`, `curl(1)`; `dp-hello` (project 00).
