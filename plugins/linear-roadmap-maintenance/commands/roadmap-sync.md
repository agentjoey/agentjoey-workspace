---
description: Run the Linear roadmap/backlog sync pass — gate first, reconcile shipped work, groom the backlog, record state.
argument-hint: "[--force] [project name]"
---

Run the `linear-roadmap-maintenance` skill's sync pass for this repository.

Arguments: $ARGUMENTS (`--force` syncs even when the cadence gate says not due; a project name limits the pass to that project).

Do exactly this:

1. Run `python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py` (add `--force` if asked). If the skill lives elsewhere (e.g. `~/.claude/skills/`), use that path.
2. If `due` is false and `--force` was not passed: report the reason in one line and stop. Do not touch Linear.
3. If there is no `.linear-roadmap.json`: stop and ask for the Linear team and the project↔path mapping, then offer to write the config and a `--record --note "baseline"` baseline.
4. Otherwise follow the skill's five-phase sync pass, respecting the autonomy boundaries and the idempotency contract.
5. Finish with `--record --note "<one line>"`, commit the state file, and print what changed in Linear (closed / created / re-prioritised / flagged).
