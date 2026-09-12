---
description: Run the gated Linear repair / roadmap-review pass — for work that skipped the backlog loop.
argument-hint: "[--force]"
---

Run the `linear-roadmap-maintenance` skill's gated pass. This is the *repair* path: the work loop (`/next-task`) is what normally keeps Linear in sync.

Arguments: $ARGUMENTS (`--force` runs a repair pass even when the gate says not due).

1. Run `python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py` (add `--force` if asked). If the skill lives elsewhere (e.g. `~/.claude/skills/`), use that path.
2. `due: false` → report the reason in one line and stop. **Do not load any Linear state.** This is the expected outcome when every commit carries an issue identifier, and it should cost nothing.
3. No `.linear-roadmap.json` → stop and ask for the Linear team and project↔path mapping, then offer to write it plus a `--record --note "baseline"` baseline.
4. `mode: repair` → reconcile **only** the commits listed in `unticketedCommits`. Read the touched projects' issues first, search before creating, and leave the ticketed commits alone.
5. `mode: roadmap-review` → projects and milestones only. Recompute progress; if a target date is unreachable at the observed rate, post one status update with the numbers. Never move the date yourself.
6. Finish with `--record --mode <mode> --note "<one line>"`, commit the state file, and report what changed in Linear. A pass that failed partway is **not** recorded.
