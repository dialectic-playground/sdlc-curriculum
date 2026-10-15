#!/usr/bin/env python3
"""Create a project's language-neutral ``assignment/`` workspace from the shared templates.

Usage::

    tools/scaffold-project.py [--force] [SLUG ...]     # default: every project in curriculum.toml

For each project this writes::

    projects/<slug>/assignment/
        Makefile             from shared/templates/assignment/Makefile.tmpl
        hld.md lld.md rtm.md master-test-plan.md
                             from shared/templates/*-TEMPLATE.md (header filled in)
        src/README.md        from shared/templates/assignment/src-README.md.tmpl

``{{NAME}}`` placeholders in the templates are substituted. Existing files are left untouched
unless ``--force`` is given.
"""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "shared" / "templates"
OUTPUTS = {
    "Makefile": TEMPLATES / "assignment" / "Makefile.tmpl",
    "hld.md": TEMPLATES / "HLD-TEMPLATE.md",
    "lld.md": TEMPLATES / "LLD-TEMPLATE.md",
    "rtm.md": TEMPLATES / "RTM-TEMPLATE.md",
    "master-test-plan.md": TEMPLATES / "MASTER-TEST-PLAN-TEMPLATE.md",
    "src/README.md": TEMPLATES / "assignment" / "src-README.md.tmpl",
}


def load_projects() -> list[dict[str, object]]:
    with open(ROOT / "curriculum.toml", "rb") as handle:
        return list(tomllib.load(handle)["project"])


def project_variables(project: dict[str, object]) -> dict[str, str]:
    return {
        "SLUG": str(project["slug"]),
        "TITLE": str(project["title"]),
        "TOOLS": " ".join(str(t) for t in project["tools"]),  # type: ignore
    }


def substitute(text: str, variables: dict[str, str]) -> str:
    for name, value in variables.items():
        text = text.replace("{{" + name + "}}", value)
    return text


def scaffold(project: dict[str, object], force: bool) -> list[str]:
    variables = project_variables(project)
    assignment = ROOT / "projects" / variables["SLUG"] / "assignment"
    reports = []
    for relative, template in OUTPUTS.items():
        target = assignment / relative
        if target.exists() and not force:
            reports.append(f"skip  {target.relative_to(ROOT).as_posix()}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        text = substitute(template.read_text(encoding="utf-8"), variables)
        target.write_bytes(text.encode("utf-8"))
        reports.append(f"wrote {target.relative_to(ROOT).as_posix()}")
    return reports


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Scaffold projects/<slug>/assignment/."
    )
    parser.add_argument("slugs", nargs="*", help="project slugs (default: all)")
    parser.add_argument("--force", action="store_true", help="overwrite existing files")
    args = parser.parse_args(argv)
    projects = {str(p["slug"]): p for p in load_projects()}
    unknown = [slug for slug in args.slugs if slug not in projects]
    if unknown:
        print(
            f"scaffold-project: unknown project(s): {', '.join(unknown)}",
            file=sys.stderr,
        )
        return 2
    for slug in args.slugs or list(projects):
        print("\n".join(scaffold(projects[slug], args.force)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
