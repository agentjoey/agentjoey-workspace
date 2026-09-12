#!/usr/bin/env python3
"""Validate this collection: marketplace <-> plugins <-> skills stay consistent.

Run it before pushing, or let CI run it:

    python3 scripts/validate.py          # errors only
    python3 scripts/validate.py -v       # also list what passed

Exit 0 = clean, 1 = at least one error. Warnings never fail the build.
No dependencies beyond the standard library, by design: this repo has no
package manager and should stay clone-and-go.
"""

from __future__ import annotations

import json
import os
import py_compile
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
PLUGINS_DIR = os.path.join(ROOT, "plugins")
TEMPLATES_DIR = os.path.join(ROOT, "templates")

# Claude Code truncates long skill descriptions; keep them well under the limit.
MAX_SKILL_DESCRIPTION = 1024
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

errors: list[str] = []
warnings: list[str] = []
passed: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def ok(msg: str) -> None:
    passed.append(msg)


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def read_json(path: str):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        err(f"{rel(path)}: missing")
    except ValueError as exc:
        err(f"{rel(path)}: invalid JSON — {exc}")
    return None


def frontmatter(path: str):
    """Parse flat `key: value` YAML frontmatter. Returns None if absent/broken."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError as exc:
        err(f"{rel(path)}: unreadable — {exc}")
        return None
    if not text.startswith("---\n"):
        err(f"{rel(path)}: missing YAML frontmatter (must start with ---)")
        return None
    end = text.find("\n---", 4)
    if end == -1:
        err(f"{rel(path)}: frontmatter is never closed")
        return None
    fields, key = {}, None
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        if line[0] not in " \t" and ":" in line:
            key, _, value = line.partition(":")
            key = key.strip()
            fields[key] = value.strip().strip('"\'')
        elif key:                                    # folded continuation line
            fields[key] = (fields[key] + " " + line.strip()).strip()
    return fields


def check_skill(plugin: str, skill_dir: str) -> None:
    name = os.path.basename(skill_dir)
    path = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(path):
        err(f"{rel(skill_dir)}: skill directory has no SKILL.md")
        return
    fm = frontmatter(path)
    if fm is None:
        return
    if fm.get("name") != name:
        err(f"{rel(path)}: frontmatter name '{fm.get('name')}' != directory name '{name}'")
    if not NAME_RE.match(name):
        err(f"{rel(skill_dir)}: skill name must be lowercase-with-hyphens")
    description = fm.get("description", "")
    if not description:
        err(f"{rel(path)}: frontmatter needs a description — it is what makes the skill trigger")
    elif len(description) > MAX_SKILL_DESCRIPTION:
        err(f"{rel(path)}: description is {len(description)} chars (max {MAX_SKILL_DESCRIPTION})")
    elif not re.search(r"\b(use|apply|run|read)\b", description, re.I):
        warn(f"{rel(path)}: description does not say when to use the skill "
             f"(\"Use when …\" triggers far more reliably)")
    else:
        ok(f"skill {plugin}/{name}")

    # Referenced helper scripts must at least exist and compile.
    scripts_dir = os.path.join(skill_dir, "scripts")
    if os.path.isdir(scripts_dir):
        for entry in sorted(os.listdir(scripts_dir)):
            script = os.path.join(scripts_dir, entry)
            if entry.endswith(".py"):
                try:
                    with tempfile.NamedTemporaryFile(suffix=".pyc", delete=True) as tmp:
                        py_compile.compile(script, cfile=tmp.name, doraise=True)
                    ok(f"script {rel(script)} compiles")
                except py_compile.PyCompileError as exc:
                    err(f"{rel(script)}: syntax error — {exc}")
            if entry.endswith((".py", ".sh")) and not os.access(script, os.X_OK):
                warn(f"{rel(script)}: not executable (chmod +x)")


def check_commands(plugin_dir: str) -> None:
    commands_dir = os.path.join(plugin_dir, "commands")
    if not os.path.isdir(commands_dir):
        return
    for entry in sorted(os.listdir(commands_dir)):
        if not entry.endswith(".md"):
            continue
        fm = frontmatter(os.path.join(commands_dir, entry))
        if fm is not None and not fm.get("description"):
            err(f"{rel(os.path.join(commands_dir, entry))}: command needs a description")


def check_plugin(entry: dict, seen: set) -> None:
    name = entry.get("name")
    source = entry.get("source", "")
    if not name:
        err("marketplace.json: a plugin entry has no name")
        return
    if not entry.get("description"):
        err(f"marketplace.json: '{name}' has no description")
    plugin_dir = os.path.normpath(os.path.join(ROOT, source.lstrip("./")))
    if not os.path.isdir(plugin_dir):
        err(f"marketplace.json: '{name}' points at missing directory {source}")
        return
    seen.add(os.path.basename(plugin_dir))
    if os.path.basename(plugin_dir) != name:
        err(f"marketplace.json: '{name}' lives in directory '{os.path.basename(plugin_dir)}'")

    manifest = read_json(os.path.join(plugin_dir, ".claude-plugin", "plugin.json"))
    if manifest is None:
        return
    if manifest.get("name") != name:
        err(f"{rel(plugin_dir)}/.claude-plugin/plugin.json: name '{manifest.get('name')}' "
            f"!= marketplace name '{name}'")
    for field in ("version", "description"):
        if not manifest.get(field):
            err(f"{rel(plugin_dir)}/.claude-plugin/plugin.json: missing {field}")
    if not os.path.isfile(os.path.join(plugin_dir, "README.md")):
        warn(f"{rel(plugin_dir)}: no README.md")

    skills_dir = os.path.join(plugin_dir, "skills")
    skill_dirs = (
        [os.path.join(skills_dir, d) for d in sorted(os.listdir(skills_dir))
         if os.path.isdir(os.path.join(skills_dir, d))]
        if os.path.isdir(skills_dir) else []
    )
    if not skill_dirs and not os.path.isdir(os.path.join(plugin_dir, "commands")):
        err(f"{rel(plugin_dir)}: plugin has neither skills/ nor commands/")
    for skill_dir in skill_dirs:
        check_skill(name, skill_dir)
    check_commands(plugin_dir)
    ok(f"plugin {name}")


def main() -> int:
    verbose = "-v" in sys.argv or "--verbose" in sys.argv

    market = read_json(MARKETPLACE)
    if market is None:
        print("cannot continue without a readable marketplace.json", file=sys.stderr)
        return 1
    for field in ("name", "owner", "plugins"):
        if field not in market:
            err(f"marketplace.json: missing '{field}'")

    seen: set = set()
    for entry in market.get("plugins", []):
        check_plugin(entry, seen)

    # Orphans: a plugin on disk that nobody can install.
    if os.path.isdir(PLUGINS_DIR):
        for entry in sorted(os.listdir(PLUGINS_DIR)):
            if os.path.isdir(os.path.join(PLUGINS_DIR, entry)) and entry not in seen:
                err(f"plugins/{entry}: on disk but not listed in marketplace.json")

    readme = ""
    if os.path.isfile(os.path.join(ROOT, "README.md")):
        readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for entry in market.get("plugins", []):
        if entry.get("name") and entry["name"] not in readme:
            warn(f"README.md does not mention '{entry['name']}'")

    if os.path.isdir(TEMPLATES_DIR) and "templates" in seen:
        err("templates/ must not be a marketplace entry")

    for line in (passed if verbose else []):
        print(f"  ok    {line}")
    for line in warnings:
        print(f"  warn  {line}")
    for line in errors:
        print(f"  ERROR {line}", file=sys.stderr)

    plugins = len(market.get("plugins", []))
    print(f"\n{plugins} plugin(s), {len(passed)} check(s) passed, "
          f"{len(warnings)} warning(s), {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
