---
name: linear-roadmap-maintenance
description: Use when an agent has to keep Linear current on its own — a scheduled or post-merge roadmap sync, reconciling shipped commits/PRs against Linear issues, milestones and project status, grooming a backlog, or wiring Claude Code / Codex to do that on a cadence or after N merged PRs. Also use before hand-editing Linear after a burst of agent-written code.
---

# Linear Roadmap Maintenance

**Core principle:** A roadmap is a *record of what shipped*, not a wish list of what was planned. Agents write code fast and leave the tracker behind, so the tracker starts lying — and a lying tracker is worse than none, because humans plan against it. Every sync must be **evidence-driven** (git decides what is done, not your memory), **idempotent** (the second run changes nothing), and **bounded** (some edits are never made unattended).

Announce the sync in one line when you start one, and never silently mutate Linear inside an unrelated task.

## Recipe 1 — the gate: decide whether to sync at all

Never sync per commit — that is how you get duplicate issues and status-update spam. Run the gate first:

```bash
python3 "$SKILL_DIR/scripts/roadmap-gate.py"          # sync brief as JSON (evidence + due-ness)
python3 "$SKILL_DIR/scripts/roadmap-gate.py" --check  # exit 0 = due, 10 = not due
```

It reads `.linear-roadmap.json` (config) and `.linear-roadmap.state.json` (last sync sha/time) at the repo root and reports **due** when any cadence threshold trips: `everyDays`, `everyMergedPRs`, `everyCommits`. See `references/config-and-state.md` for the schema, `references/scheduling.md` for cron / GitHub Actions / hook / Codex wiring.

- **Not due → stop.** Say "roadmap sync not due (<reason>)" and write nothing to Linear. A no-op is the most common correct outcome.
- **No config file → stop and ask** which team and projects to maintain. Do not guess a team and start creating issues in someone's workspace.
- The brief is your phase-1 evidence; do not re-derive it by hand.

## Recipe 2 — the sync pass (five phases, in order)

1. **Read the evidence.** From the brief: commit range, merges, changed paths → `projectsTouched`, and `issueIdentifiersReferenced` (identifiers scraped from commit subjects/branches). For anything ambiguous, read the actual diff or PR body — never infer scope from a commit subject alone.
2. **Read current Linear state before writing.** `list_projects`, `list_issues` (per touched project, plus `state: "backlog"`), `list_milestones`, `list_cycles`. You cannot reconcile against state you have not loaded; skipping this is how duplicates get created.
3. **Close the loop on shipped work.**
   - Issue referenced by a merged commit but still open → move to the team's done state and attach the PR/commit link.
   - Work shipped with **no** issue → create it *already in the done state*, describing what shipped. This is a record, not fiction; do not invent a planning story for it.
   - Issue whose stated scope the diff contradicts → update the description to what actually shipped, and say so in the report.
4. **Look forward: groom, then re-forecast.**
   - Backlog: merge duplicates, delete nothing, re-prioritise from what the code now demands (newly-blocked work, `TODO(AGT-xx)` markers, follow-ups named in PR descriptions).
   - Milestones: recompute progress from real issue states. If a target date is unreachable at the observed throughput, **say so in a status update — do not quietly move the date.**
   - Post **one** `save_status_update` per project per sync, only when something changed, with `health` justified by evidence (`onTrack` / `atRisk` / `offTrack`) and the commit range cited.
5. **Record and report.** `roadmap-gate.py --record --note "<one line>"`, commit the state file, and print a diff summary: issues closed, created, re-prioritised, milestones flagged. Tool call names and payloads: `references/linear-operations.md`.

## Recipe 3 — autonomy boundaries

| Unattended (just do it) | Propose only (comment / ask, never apply) |
|---|---|
| Create backlog issues for work the code demands | Creating projects, initiatives, or teams |
| Move an issue to done when a merged PR proves it | Closing anything as Cancelled / Won't-do |
| Update an issue's own description, labels, links | Changing project target dates or committed scope |
| Re-prioritise and re-order the backlog | Archiving or deleting issues, or editing a human's issue body |
| Post a project status update | Assigning work to a human, or changing their assignment |

Propose = a comment on the issue/project (`save_comment`), or a single issue titled `Roadmap proposal: …`. When `.linear-roadmap.json` sets a stricter `autonomy`, that wins.

## Idempotency contract — the anti-duplication rules

1. **Search before create.** `list_issues` with `query:` on the title and on the PR URL. A near-title match is a match — update it, don't add a twin.
2. **Mark what you own.** Every agent-created issue gets the `agent-maintained` label and a footer line `<!-- roadmap-sync: <sha> -->`. Only edit bodies carrying that marker; for anything else, comment.
3. **Never create an issue for a commit that already names one.**
4. **One status update per project per sync**, and none when nothing changed.
5. **State is the interlock.** Always `--record` after a successful sync and commit the state file; re-running then reconciles nothing twice. A sync that failed halfway must NOT be recorded.

## Red flags — stop and reconsider

- Syncing on every commit, or because "it has been a while" without running the gate
- Creating issues before listing what already exists
- Moving a milestone date so the roadmap looks green
- Closing an issue because the code "looks done" with no merged commit behind it
- Writing a status update that reports intent ("working on auth") instead of evidence ("14 commits, AGT-12/45 shipped, milestone M2 4/7")
- Editing or archiving issues a human wrote, without a marker and without asking
- Recording sync state after a partial failure

## Example

Gate says due: `5 merges >= everyMergedPRs 5`, `projectsTouched: {Website: [...]}`, `issueIdentifiersReferenced: [AGT-12, AGT-45]`.

❌ Wrong: create five "shipped X" issues from the five merge subjects and post "good progress!" — duplicates AGT-12/45, and the update carries no evidence.

✅ Right: list the project's issues first → AGT-12 and AGT-45 are open, so close both with their PR links; two merges map to no issue, so create one issue in done state (the other was a revert — record nothing); one backlog item is now blocked by the new API shape, so re-prioritise and note why; milestone M2 is 4/7 with 3 weeks left at ~1.5 issues/week → `health: "atRisk"` with those numbers in the body; then `--record` and commit.
