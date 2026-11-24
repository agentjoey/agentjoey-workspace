---
description: Add or update the SHARED-ENGINEERING block in this repo's AGENTS.md.
argument-hint: "[repo dir] [--dry-run]"
---

Adopt the shared engineering conventions in a repository. Arguments: $ARGUMENTS

1. No directory given → use the current directory.
2. Run `python3 "$SKILL_DIR/scripts/engineering_block.py" check <dir>` first and show
   its line. If it already says `ok`, stop and say so — there is nothing to do.
3. If the file already holds a lot, or `check` reported `DUP` or `NO-CODEX`, run
   `apply <dir> --dry-run` and show what it would do before writing.
4. Run `python3 "$SKILL_DIR/scripts/engineering_block.py" apply <dir> --claude-pointer`.
   The block goes in `AGENTS.md` because codex reads nothing else. Never paste the block
   from another repo.
5. Re-run `check <dir>` and show the line. It must say `ok`.
6. Show `git diff --stat`. Do not commit unless the Owner asks. Work on a branch or
   worktree, never on the default branch.
7. If `check` still reports `DUP` or `NO-CODEX`, do not try to fix it by editing the
   block — read Recipe 3 or 4 in the skill and say which one applies.
