#!/usr/bin/env python3
"""Render, check and apply the SHARED-ENGINEERING block in a repo's AGENTS.md.

    engineering_block.py render
    engineering_block.py check DIR [DIR ...] [--file NAME ...] [--quiet]
    engineering_block.py apply DIR [--file NAME ...] [--claude-pointer] [--dry-run]

The block takes no parameters: every repo carries the same text, so `render` just
prints the canonical source and `check` can compare byte for byte. That is the one
thing the intake block cannot do, and it is what turns "the blocks look similar"
into "the blocks are identical".

`check` looks in AGENTS.md, CLAUDE.md and GEMINI.md, resolving symlinks so that the
diskwatch pattern (AGENTS.md and GEMINI.md both pointing at CLAUDE.md) counts as one
file. It exits 1 on any of:

    MISSING    no agent file in the repo carries the block
    DRIFT      the block is there but its text differs from the canonical source
    DUP        two distinct real files carry the block, so some harnesses load it twice
    NO-CODEX   the block is there but not reachable through AGENTS.md

NO-CODEX matters because codex reads AGENTS.md and nothing else: a block that lives
only in CLAUDE.md is invisible to it. Standard library only.
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "references", "shared-engineering-block.md")
AGENT_FILES = ("AGENTS.md", "CLAUDE.md", "GEMINI.md")
BEGIN_RE = re.compile(r"<!-- BEGIN SHARED-ENGINEERING v(\d+) -->")
BLOCK_RE = re.compile(
    r"<!-- BEGIN SHARED-ENGINEERING v\d+ -->.*?<!-- END SHARED-ENGINEERING -->\n?", re.S
)


def template_text() -> str:
    with open(TEMPLATE, encoding="utf-8") as fh:
        text = fh.read()
    return text if text.endswith("\n") else text + "\n"


def template_version() -> int:
    match = BEGIN_RE.search(template_text())
    if not match:
        sys.exit("canonical source has no BEGIN SHARED-ENGINEERING marker")
    return int(match.group(1))


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def extract(text: str) -> str | None:
    match = BLOCK_RE.search(text)
    if not match:
        return None
    block = match.group(0)
    return block if block.endswith("\n") else block + "\n"


def cmd_render(_args: argparse.Namespace) -> int:
    sys.stdout.write(template_text())
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    canonical = template_text()
    current = template_version()
    names = args.file or list(AGENT_FILES)
    bad = 0

    for directory in args.dirs:
        # real path -> (block text, version, names that reach it)
        carriers: dict[str, tuple[str, int, list[str]]] = {}
        agents_real = None
        for name in names:
            path = os.path.join(directory, name)
            if not os.path.exists(path):
                continue
            real = os.path.realpath(path)
            if name == "AGENTS.md":
                agents_real = real
            if real in carriers:
                carriers[real][2].append(name)
                continue
            block = extract(read(path))
            if block is None:
                continue
            version = int(BEGIN_RE.search(block).group(1))
            carriers[real] = (block, version, [name])

        if not carriers:
            print(f"MISSING  {directory}: no SHARED-ENGINEERING block in {', '.join(names)}")
            bad += 1
            continue

        problems = []
        versions = sorted({v for _b, v, _n in carriers.values()})
        for block, version, where in carriers.values():
            if version < current:
                problems.append(f"{'/'.join(where)} is v{version}, canonical is v{current}")
            elif block != canonical:
                problems.append(f"{'/'.join(where)} text differs from canonical v{current}")
        if len(carriers) > 1:
            where = " and ".join("/".join(n) for _b, _v, n in carriers.values())
            problems.append(f"block is in two separate files ({where}); harnesses that read both load it twice")
        if agents_real is None or agents_real not in carriers:
            problems.append("not reachable through AGENTS.md, so codex cannot see it")

        reached = ", ".join(
            "=".join(n) if len(n) > 1 else n[0] for _b, _v, n in carriers.values()
        )
        label = f"v{versions[0]}" if len(versions) == 1 else "v" + "/v".join(str(v) for v in versions)
        if problems:
            tag = "DUP     " if len(carriers) > 1 else ("DRIFT   " if versions[0] < current or any("differs" in p for p in problems) else "NO-CODEX")
            bad += 1
            print(f"{tag} {directory}: {label} in {reached}")
            for problem in problems:
                print(f"         <- {problem}")
        elif not args.quiet:
            print(f"ok       {directory}: {label} in {reached}")

    return 1 if bad else 0


def cmd_apply(args: argparse.Namespace) -> int:
    block = template_text()
    for name in args.file or ["AGENTS.md"]:
        path = os.path.join(args.dir, name)
        existing = read(path) if os.path.exists(path) else ""
        if BLOCK_RE.search(existing):
            if extract(existing) == block:
                print(f"already current in {path}")
                continue
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
        text = read(claude) if os.path.exists(claude) else ""
        if os.path.islink(claude):
            print(f"left {claude} alone: it is a symlink")
        elif "@AGENTS.md" in text or "SHARED-ENGINEERING" in text:
            print(f"left {claude} alone: it already reaches AGENTS.md or carries the block")
        else:
            with open(claude, "w", encoding="utf-8") as fh:
                fh.write("@AGENTS.md\n\n" + text if text else "@AGENTS.md\n")
            print(f"added @AGENTS.md to {claude}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_render = sub.add_parser("render")
    p_render.set_defaults(func=cmd_render)

    p_check = sub.add_parser("check")
    p_check.add_argument("dirs", nargs="+")
    p_check.add_argument("--file", action="append", help=f"file to inspect (repeatable); default {', '.join(AGENT_FILES)}")
    p_check.add_argument("--quiet", action="store_true", help="print only the repos with problems")
    p_check.set_defaults(func=cmd_check)

    p_apply = sub.add_parser("apply")
    p_apply.add_argument("dir")
    p_apply.add_argument("--file", action="append", help="file to write (repeatable); default AGENTS.md")
    p_apply.add_argument("--claude-pointer", action="store_true", help="add '@AGENTS.md' to CLAUDE.md unless it already reaches it, carries the block, or is a symlink")
    p_apply.add_argument("--dry-run", action="store_true")
    p_apply.set_defaults(func=cmd_apply)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
