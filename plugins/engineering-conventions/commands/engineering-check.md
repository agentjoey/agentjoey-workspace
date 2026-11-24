---
description: Report the SHARED-ENGINEERING block version and drift across one or more repos.
argument-hint: "<repo dir> [<repo dir> ...] [--quiet]"
---

Check which repos carry the shared engineering conventions and whether they are
identical. Arguments: $ARGUMENTS

1. No directories given → use the current directory.
2. Run `python3 "$SKILL_DIR/scripts/engineering_block.py" check <dirs>` and print its
   output unchanged. It compares byte for byte, so `ok` means identical, not similar.
3. For every line that is not `ok`, say in one sentence what to run:
   - `MISSING` or `DRIFT` → `/adopt-engineering <dir>`
   - `DUP` → Recipe 3 in the skill (one real file, the other names symlinked)
   - `NO-CODEX` → Recipe 4 in the skill (the block must be reachable through
     `AGENTS.md`, or codex cannot see it)
4. Do not edit any file.
