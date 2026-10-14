---
description: Add or update the SHARED-INTAKE rule block in this repo's AGENTS.md.
argument-hint: "<Project> <Linear project name> <Linear project id> [formerly]"
---

Adopt the `intake-workflow` rules in the current repository. Arguments: $ARGUMENTS

1. Missing an argument → ask for it. The Project value must equal the option in the Notion Requests database; the Linear id (for example `P-AJ-18`) must belong to exactly one live project.
2. Run `python3 "$SKILL_DIR/scripts/intake_block.py" apply . --project "<P>" --linear-name "<N>" --linear-id <id> --claude-pointer` (add `--formerly "<old>"` after a rename). Use `--dry-run` first if `AGENTS.md` already holds a lot.
3. Run `intake_block.py check .` and show its line.
4. Show `git diff --stat`. Do not commit unless the Owner asks. Work on a branch or worktree, never on the default branch.
5. Remind the Owner of the two manual steps the script cannot do: add the `Project` option in both Notion databases, and confirm the Linear project name is unique among live projects.
