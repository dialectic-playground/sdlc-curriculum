<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

**Table of Contents** _generated with [DocToc](https://github.com/thlorenz/doctoc)_

- [Contributing to the SDLC curriculum](#contributing-to-the-sdlc-curriculum)
  - [Ground rules](#ground-rules)
  - [Changing a specification](#changing-a-specification)
  - [Adding or changing tests](#adding-or-changing-tests)
  - [Changing shared templates or tooling](#changing-shared-templates-or-tooling)
  - [Adding a project](#adding-a-project)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Contributing to the SDLC curriculum

This file adds curriculum-specific rules to the
[organization-wide contributing guide](https://github.com/dialectic-playground/.github/blob/main/CONTRIBUTING.md)
(Conventional Commit pull request titles, squash merges, DCO sign-off) and the
[Code of Conduct](https://github.com/dialectic-playground/.github/blob/main/CODE_OF_CONDUCT.md).

> **Implementations do not belong here.** This repository holds specifications, tests, and
> templates only. Implementations live in the language repositories.

## Ground rules

1. **The SRS is the authority.** When the SRS, the user manual, the fixtures, and the
   reference models disagree, the SRS wins. Fix the others to match it.
2. **Keep documents in step.** A behavior change touches, in this order: the SRS (and URD if
   the user need changed), then the user manual (including the normative help text), then
   the reference model in `reference/`, then the regenerated fixtures.
3. **Never hand-edit expected outputs.** Regenerate them from the reference model and review
   every changed byte.
4. **Stay language-neutral.** Specifications, manuals, and templates must not require or
   suggest a particular implementation language.

## Changing a specification

```sh
# 1. Edit specs/SRS.md and specs/user-manual.md (and specs/URD.md if needed)
# 2. Update the reference model: reference/dpref/<tool>.py
# 3. Regenerate the project's fixtures (in the toolchain container)
tools/dp-run python3 shared/tools/run-tests.py --reference --update \
    projects/<slug>/tests/public projects/<slug>/tests/private
# 4. Review the regenerated fixtures byte by byte
git diff projects/<slug>/tests/
# 5. Run every check CI runs (in the toolchain container; DP_RUNTIME=local for native)
make check
```

Use a scope in the pull request title, for example `fix(02-cat): correct -v notation for 0x7F`.
If the change can break a conforming implementation, mark it as breaking
(`feat(05-grep-lite)!: …`) and describe the migration in the pull request. It will ship in
the next MAJOR release (see [Versioning](README.md#versioning)).

## Adding or changing tests

- Every suite has exactly ten tests with IDs `01` … `10`. `check-curriculum.py` enforces this.
- Tests must be deterministic on Linux, macOS, and Windows. Follow the rules in
  [`shared/CLI-CONVENTIONS.md`](shared/CLI-CONVENTIONS.md) §9 and the fixture naming rules
  (lowercase ASCII, no symlinks, no empty directories, no names that differ only in case).
- Put fixtures shared by both suites in `tests/fixtures/`.

## Changing shared templates or tooling

- `shared/templates/` changes affect every project. After editing the assignment templates, run
  `make scaffold` and commit the regenerated `assignment/` files.
  CI's **Consistency** job checks that they match.
- `shared/ci/cross-platform-ci.yml` must use exactly the same SHA-pinned actions as
  `.github/workflows/ci.yml`. When Dependabot bumps an action, update the template in the same
  pull request. CI checks this too.

## Adding a project

1. Add it to `curriculum.toml`.
2. Write `README.md`, `specs/URD.md`, `specs/SRS.md`, and `specs/user-manual.md`, following
   Project 00 as the exemplar.
3. Add the reference model `reference/dpref/<tool>.py`, then the 10 + 10 tests and their
   fixtures.
4. Run `tools/dp-run python3 tools/scaffold-project.py <slug>`, then `make check`.
5. Add the project to the README's project table, and to the docs site's
   [curriculum reference](https://github.com/dialectic-playground/docs/blob/main/docs/reference/curriculum/index.md).
