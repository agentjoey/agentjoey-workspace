---
description: Preflight for the intake flow in this repo: block, checkout, Notion and Linear reachability, name clashes. Prints the three questions to ask a fresh session.
---

Check that the intake flow will work for the project this repo belongs to. Do not edit anything.

1. `python3 "$SKILL_DIR/scripts/intake_block.py" check .` (add `--file CLAUDE.md` when the block lives there). Not `ok` → say what to run.
2. `git fetch` and report whether the checkout is behind `origin`, with a pull hint. A session started before a pull does not carry the block.
3. Query the Requests data source with `Project = <the block's Project>` and `Stage = Pending`. Report the count, or that Notion is unreachable in this tool.
4. `get_project` on the block's Linear id: confirm it resolves and that no other **live** project has the same name. If the block names a draining project, confirm it too.
5. Print, for the Owner to ask in a **fresh** session after the pull: "How many pending requests?" (expect a Requests count, no Linear numbers, no other project), "How many open issues does this project have in Linear?", and "Log an idea: …" (expect an Inbox row, no Linear issue).
