# reference/ — maintainer fixture tooling (not an assignment solution)

> **This is not a language implementation of the curriculum.** Implementations live in
> separate language repositories. This directory exists for one purpose: to **generate and
> verify the expected-output fixtures** in `projects/*/tests/`, so that every one of the 220
> black-box tests is proven consistent with its SRS on Linux, macOS, and Windows.

## Why it exists

The test suites compare output byte-for-byte. Hand-written fixtures drift from the specs
through typos, a forgotten trailing newline, or a misremembered error message. An executable
model of each SRS, run in CI on all three operating systems, catches these mistakes and shows
that every specification can actually be implemented portably.

## Rules

- Standard-library Python ≥ 3.11 only. No third-party packages.
- Each tool is a module `dpref/<name>.py` exposing `main(argv) -> int`. Tool `dp-foo-bar` maps
  to module `dpref.foo_bar`. Shared CLI-CONV behavior (option parsing, diagnostics, byte
  output) lives in `dpref/common.py`.
- **When the reference and the SRS disagree, the SRS wins**: fix the reference, regenerate the
  fixtures, and review the diff.
- Learners implementing a project should design from `specs/`, not from this code.

## Usage (maintainers)

```bash
# Run a reference tool by name
python3 reference/run.py dp-hello --name Ada

# Verify every fixture of every project (what CI does)
python3 shared/tools/check-curriculum.py

# Regenerate one project's fixtures after a deliberate spec change, then review `git diff`
python3 shared/tools/run-tests.py --reference --update \
    projects/00-hello-world/tests/public projects/00-hello-world/tests/private
```
