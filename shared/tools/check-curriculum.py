#!/usr/bin/env python3
"""Validate the curriculum repository (maintainer and CI tool).

Checks, for every project in curriculum.toml (or those named on the command line):

1. **Structure**: every required document, suite, and assignment file exists.
2. **Suites**: each suite defines exactly ten tests with IDs 01-10, invokes only the
   project's own tools, and has stdout/stderr/exit files for every test and no orphans.
3. **Help text**: the HELP OUTPUT section of specs/user-manual.md contains, verbatim, the
   ``--help`` output of each tool's reference model.
4. **Fixtures**: every public and hidden test passes against the reference models
   (``run-tests.py --reference``), which proves the fixtures are consistent on this OS.

Usage::

    check-curriculum.py [--structure-only] [SLUG ...]

Exit status: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import argparse
import re
import shlex
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "shared" / "tools" / "run-tests.py"
REFERENCE = ROOT / "reference" / "run.py"
REQUIRED_FILES = (
    "README.md",
    "specs/URD.md",
    "specs/SRS.md",
    "specs/user-manual.md",
    "tests/public/test-inputs.txt",
    "tests/private/hidden-inputs.txt",
    "assignment/Makefile",
    "assignment/hld.md",
    "assignment/lld.md",
    "assignment/rtm.md",
    "assignment/master-test-plan.md",
    "assignment/src/README.md",
)
SUITES = {"public": "test-inputs.txt", "private": "hidden-inputs.txt"}
EXPECTED_IDS = [f"{n:02d}" for n in range(1, 11)]
HELP_BLOCK = re.compile(r"```text\n(Usage: .*?)```", re.DOTALL)


def load_projects() -> list[dict[str, Any]]:
    with open(ROOT / "curriculum.toml", "rb") as handle:
        return list(tomllib.load(handle)["project"])


def test_ids_and_tools(inputs: Path) -> tuple[list[str], set[str]]:
    """Return the ordered unique test IDs and the tool names a suite invokes."""
    ids: list[str] = []
    tools: set[str] = set()
    for line in inputs.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        tokens = shlex.split(line)
        if tokens[0] not in ids:
            ids.append(tokens[0])
        rest = tokens[1:]
        while rest and "=" in rest[0] and rest[0].split("=", 1)[0].isidentifier():
            rest.pop(0)
        if rest:
            tools.add(rest[0])
    return ids, tools


def check_structure(project_dir: Path, tools: list[str]) -> list[str]:
    problems = [
        f"missing {name}"
        for name in REQUIRED_FILES
        if not (project_dir / name).is_file()
    ]
    for suite, inputs_name in SUITES.items():
        suite_dir = project_dir / "tests" / suite
        inputs = suite_dir / inputs_name
        if not inputs.is_file():
            continue
        ids, used_tools = test_ids_and_tools(inputs)
        if ids != EXPECTED_IDS:
            problems.append(f"{suite}: test IDs must be 01..10 in order, found {ids}")
        foreign = sorted(used_tools - set(tools))
        if foreign:
            problems.append(f"{suite}: invokes tools outside this project: {foreign}")
        expected_dir = suite_dir / "expected-outputs"
        wanted = {f"{i}.{kind}" for i in ids for kind in ("stdout", "stderr", "exit")}
        present = (
            {p.name for p in expected_dir.glob("*")} if expected_dir.is_dir() else set()
        )
        problems += [
            f"{suite}: missing expected-outputs/{n}" for n in sorted(wanted - present)
        ]
        problems += [
            f"{suite}: orphan expected-outputs/{n}" for n in sorted(present - wanted)
        ]
    return problems


def reference_help(tool: str) -> str | None:
    completed = subprocess.run(
        [sys.executable, str(REFERENCE), tool, "--help"],
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.decode("utf-8")


def check_help_text(project_dir: Path, tools: list[str]) -> list[str]:
    manual = (project_dir / "specs" / "user-manual.md").read_text(encoding="utf-8")
    _, _, help_section = manual.partition("## HELP OUTPUT")
    help_section = help_section.split("\n## ", 1)[0]
    blocks = HELP_BLOCK.findall(help_section)
    problems = []
    for tool in tools:
        actual = reference_help(tool)
        if actual is None:
            problems.append(f"reference model for {tool} is missing or failed --help")
        elif actual not in blocks:
            problems.append(
                f"user-manual HELP OUTPUT does not match `{tool} --help` verbatim"
            )
    return problems


def check_fixtures(project_dir: Path) -> list[str]:
    suites = [str(project_dir / "tests" / suite) for suite in SUITES]
    completed = subprocess.run(
        [sys.executable, str(RUNNER), "--reference", "-q", *suites],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode == 0:
        return []
    failing = [line.strip() for line in completed.stdout.splitlines() if "FAIL" in line]
    detail = failing or [completed.stderr.strip() or completed.stdout.strip()[-500:]]
    return ["fixtures do not match the reference: " + "; ".join(detail)]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Validate the curriculum repository.")
    parser.add_argument("slugs", nargs="*", help="projects to check (default: all)")
    parser.add_argument(
        "--structure-only",
        action="store_true",
        help="skip help-text and fixture verification",
    )
    args = parser.parse_args(argv)

    projects = {str(p["slug"]): p for p in load_projects()}
    unknown = [slug for slug in args.slugs if slug not in projects]
    if unknown:
        print(
            f"check-curriculum: unknown project(s): {', '.join(unknown)}",
            file=sys.stderr,
        )
        return 1

    failed = False
    for slug in args.slugs or list(projects):
        project_dir = ROOT / "projects" / slug
        tools = [str(t) for t in projects[slug]["tools"]]
        problems = check_structure(project_dir, tools)
        if not args.structure_only and not problems:
            problems += check_help_text(project_dir, tools)
            problems += check_fixtures(project_dir)
        status = "ok" if not problems else "FAIL"
        print(f"{status:4}  {slug}")
        for problem in problems:
            print(f"      - {problem}")
        failed = failed or bool(problems)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
