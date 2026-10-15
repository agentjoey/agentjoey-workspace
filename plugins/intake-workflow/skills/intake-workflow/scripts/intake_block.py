#!/usr/bin/env python3
"""Render, check and apply the SHARED-INTAKE block in a repo's AGENTS.md.

    intake_block.py render --project P --linear-name N --linear-id P-AJ-18 [--formerly OLD] [--draining "P-AJ-12 Mairn MVP"]
    intake_block.py check  DIR [DIR ...] [--expect-project P] [--file NAME]
    intake_block.py apply  DIR --project P --linear-name N --linear-id P-AJ-18 [--formerly OLD] [--draining "P-AJ-12 Mairn MVP"]
                               [--file NAME ...] [--claude-pointer] [--dry-run]

`render` prints the block to stdout (use it when the repo is edited through an API
instead of a checkout). `check` reports each repo's block version and project lines and
exits 1 on a missing block, an older version, or a project mismatch. `apply` inserts or
replaces the block between its markers, leaving everything else untouched, so it is safe
to run again. Standard library only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "references", "shared-intake-block.md")
BEGIN_RE = re.compile(r"<!-- BEGIN SHARED-INTAKE v(\d+) -->")
BLOCK_RE = re.compile(r"<!-- BEGIN SHARED-INTAKE v\d+ -->.*?<!-- END SHARED-INTAKE -->\n?", re.S)
PROJECT_RE = re.compile(r"^- Project: `([^`]*)`", re.M)
LINEAR_RE = re.compile(r"^- Linear: team `AJ`, project `([^`]*)` \(([^)]*)\)", re.M)


def template_text() -> str:
    with open(TEMPLATE, encoding="utf-8") as fh:
        return fh.read()


def template_version() -> int:
    match = BEGIN_RE.search(template_text())
    if not match:
        sys.exit("template has no BEGIN SHARED-INTAKE marker")
    return int(match.group(1))


def render(project: str, linear_name: str, linear_id: str, formerly: str | None, draining: str | None = None) -> str:
    text = template_text()
    former = f" Formerly: `{formerly}`." if formerly else ""
    drain = ""
    if draining:
        drain_id, _, drain_name = draining.partition(" ")
        drain = f" Open work from before this flow still sits in project `{drain_name or drain_id}` ({drain_id}): read it for what to build, and create nothing new there."
    out = (
        text.replace("{{PROJECT}}", project)
        .replace("{{LINEAR_NAME}}", linear_name)
        .replace("{{LINEAR_ID}}", linear_id)
        .replace("{{FORMERLY}}", former)
        .replace("{{DRAINING}}", drain)
    )
    if "{{" in out:
        sys.exit("unfilled placeholder left in block")
    return out if out.endswith("\n") else out + "\n"


def agents_path(directory: str, name: str = "AGENTS.md") -> str:
    return os.path.join(directory, name)


def cmd_render(args: argparse.Namespace) -> int:
    sys.stdout.write(render(args.project, args.linear_name, args.linear_id, args.formerly, args.draining))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    current = template_version()
    bad = 0
    for directory in args.dirs:
        path = agents_path(directory, args.file)
        if not os.path.exists(path):
            print(f"MISSING   {directory}: no {args.file}")
            bad += 1
            continue
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        begin = BEGIN_RE.search(text)
        if not begin:
            print(f"MISSING   {directory}: no SHARED-INTAKE block in {args.file}")
            bad += 1
            continue
        version = int(begin.group(1))
        project = PROJECT_RE.search(text)
        linear = LINEAR_RE.search(text)
        name = project.group(1) if project else "?"
        linear_desc = f"{linear.group(1)} ({linear.group(2)})" if linear else "?"
        problems = []
        if version < current:
            problems.append(f"older than v{current}")
        if args.expect_project and name != args.expect_project:
            problems.append(f"project is {name!r}, expected {args.expect_project!r}")
        status = "DRIFT    " if problems else "ok       "
        bad += 1 if problems else 0
        extra = f"  <- {'; '.join(problems)}" if problems else ""
        print(f"{status} {directory}: v{version} project={name} linear={linear_desc}{extra}")
    return 1 if bad else 0


def cmd_apply(args: argparse.Namespace) -> int:
    block = render(args.project, args.linear_name, args.linear_id, args.formerly, args.draining)
    for name in args.file or ["AGENTS.md"]:
        path = agents_path(args.dir, name)
        existing = ""
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                existing = fh.read()
        if BLOCK_RE.search(existing):
            updated = BLOCK_RE.sub(lambda _m: block, existing, count=1)
            action = "replaced"
        else:
            sep = "" if not existing else ("\n" if existing.endswith("\n") else "\n\n")
            updated = existing + sep + ("\n" if existing else "") + block
            action = "inserted"
        if args.dry_run:
            print(f"[dry-run] would have {action} the block in {path}")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)
        print(f"{action} the block in {path}")
    if args.claude_pointer and not args.dry_run:
        claude = os.path.join(args.dir, "CLAUDE.md")
        text = ""
        if os.path.exists(claude):
            with open(claude, encoding="utf-8") as fh:
                text = fh.read()
        if "@AGENTS.md" not in text and "SHARED-INTAKE" not in text:
            with open(claude, "w", encoding="utf-8") as fh:
                fh.write("@AGENTS.md\n\n" + text if text else "@AGENTS.md\n")
            print(f"added @AGENTS.md to {claude}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    def project_args(p: argparse.ArgumentParser) -> None:
        p.add_argument("--project", required=True, help="value of Project in the Notion databases")
        p.add_argument("--linear-name", required=True, help="Linear project name")
        p.add_argument("--linear-id", required=True, help="Linear project id, e.g. P-AJ-18")
        p.add_argument("--formerly", help="previous name, kept for one version after a rename")
        p.add_argument("--draining", help='older Linear project still holding open issues, as "P-AJ-12 Mairn MVP"; remove it once that project is empty')

    p_render = sub.add_parser("render")
    project_args(p_render)
    p_render.set_defaults(func=cmd_render)

    p_check = sub.add_parser("check")
    p_check.add_argument("dirs", nargs="+")
    p_check.add_argument("--expect-project")
    p_check.add_argument("--file", default="AGENTS.md", help="file to inspect in each directory")
    p_check.set_defaults(func=cmd_check)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("dir")
    project_args(p_apply)
    p_apply.add_argument("--file", action="append", help="file to write (repeatable); default AGENTS.md")
    p_apply.add_argument("--claude-pointer", action="store_true", help="add '@AGENTS.md' to CLAUDE.md unless it already imports it or carries the block")
    p_apply.add_argument("--dry-run", action="store_true")
    p_apply.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
