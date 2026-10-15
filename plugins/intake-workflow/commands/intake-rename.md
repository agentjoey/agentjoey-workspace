---
description: Rename a project in the intake flow (Linear, Notion option, repo blocks) and find repos still on the old name.
argument-hint: "<old name> <new name> [repo dirs...]"
---

Rename a project. Arguments: $ARGUMENTS

1. Confirm in Linear that the project already carries the new name; its id is unchanged. If it does not, rename it (the id stays).
2. Tell the Owner to rename the `Project` option from `<old>` to `<new>` in the Notion **UI**, in both Requests and Slices, and wait for confirmation. Do not do it through an API tool; that can orphan rows.
3. In each repo dir given (default: the current one): `python3 "$SKILL_DIR/scripts/intake_block.py" apply <dir> --project "<new>" --linear-name "<new Linear name>" --linear-id <id> --formerly "<old>" [--file …]` on a branch, then open a PR. Do not commit to the default branch.
4. `intake_block.py check <dirs> --expect-project "<new>"` and show the result. Any DRIFT line is a repo still to update.
