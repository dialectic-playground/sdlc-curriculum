# Language repository skeleton

The standard layout for a repository that implements the curriculum in one language (for
example `dialectic-playground/rs`). Every language repository uses it, so they all build,
test, and run CI the same way.

```text
<language-repo>/                 # created from dialectic-playground/repo-template
├── Makefile                     # from this directory: check, toolchain, projects, roundtrip
├── Containerfile                # official toolchain image (digest-pinned) + make + python3
├── .devcontainer/               # same image, for editors
├── tools/dp-run, container.mk   # shared container tooling (from repo-template)
├── sdlc-curriculum/             # git submodule, pinned to a release tag
├── 00-hello-world/ … 10-sys-monitor/
│                                # each a copy of projects/<slug>/assignment/ with
│                                # CURRICULUM_ROOT := ../sdlc-curriculum
└── .github/workflows/ci.yml     # from shared/ci/cross-platform-ci.yml
```

## Root Makefile

| Target | Runs |
| :-- | :-- |
| `make check` | `check-repository` (standard files, submodule, a workspace for every project, no `TEMPLATE:` markers) + `toolchain` + `projects` |
| `make toolchain` | Prints each tool's version and fails unless it is on the repository's release line, so the container image and the native CI toolchains stay in step |
| `make projects` | `make all lint test test-hidden` in every project listed in `IMPLEMENTED` |
| `make roundtrip` | `make install` / `make uninstall` for every implemented project (on the host) |

`IMPLEMENTED` starts empty. Add a project's directory to it once its implementation builds
and passes its tests. CI picks it up automatically: the workflow only runs `make check` and
`make check roundtrip`, so it never needs editing.

## Containerfile

Start from the language's official image, pinned by its multi-architecture index digest. Add
only `make`, `python3` (≥ 3.11, for the black-box runner), and anything else the toolchain
lacks. Point tool caches that the image places in read-only system locations (for example
`CARGO_HOME`, `GOPATH`, `GEM_HOME`) at `/dp-cache`, and end with `ENV DP_IN_CONTAINER=1`.

## Setting one up

Follow [Add a repository](https://dialectic-playground.github.io/docs/how-to/add-a-repository/)
and [Set up a language repository](https://dialectic-playground.github.io/docs/how-to/set-up-a-language-repository/).
