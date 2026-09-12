# Config and state

Two files at the repo root. Both are **committed** — that is what lets several agents, machines and CI share one clock.

## `.linear-roadmap.json` — hand-written, the contract

```json
{
  "team": "AgentJoey",
  "issuePrefixes": ["AGT"],
  "workLoop": {
    "claim": true,
    "maxIssuesPerSession": 3,
    "maxEstimate": 5,
    "skipLabels": ["needs-human", "blocked", "design"],
    "readyState": "Backlog",
    "inProgressState": "In Progress",
    "doneState": "Done",
    "maxFollowUpsPerTask": 3
  },
  "cadence": {
    "everyDays": 7,
    "everyUnticketedMerges": 3,
    "everyUnticketedCommits": 10,
    "roadmapReviewDays": 14,
    "firstRunLookbackDays": 30
  },
  "projects": [
    { "name": "Website",       "paths": ["apps/website/**"] },
    { "name": "Design System", "paths": ["packages/ui/**", "packages/hooks/**"] },
    { "name": "Agent Tooling", "paths": ["plugins/**", "scripts/**"] }
  ],
  "ignoreCommitPatterns": ["^(chore|docs|style|ci|build|test)(\\(.+\\))?!?:", "^Revert "],
  "agentLabel": "agent-maintained",
  "autonomy": {
    "createIssues": true,
    "closeShippedIssues": true,
    "groomBacklog": true,
    "postStatusUpdates": true,
    "changeTargetDates": "propose",
    "createProjects": "propose",
    "editHumanAuthoredIssues": "propose"
  }
}
```

| Field | Meaning |
|---|---|
| `team` | Linear team name or ID. **Required** — without it, stop and ask rather than guessing into someone's workspace. |
| `issuePrefixes` | Identifier prefixes to recognise in commits (`AGT-123`). Omit and a denylist filters the obvious non-issues (`UTF-8`, `SHA-1`). Setting it is much more reliable, and it is what makes ticketed work free to skip. |
| `workLoop.claim` | Move the issue to `inProgressState` + assign to self before starting. `false` on a solo repo saves one call per task; keep `true` wherever two agents might collide. |
| `workLoop.maxIssuesPerSession` | Hard stop on how many issues one session takes. Cost per issue climbs as context grows — 3 is usually the ceiling before quality drops. |
| `workLoop.maxEstimate` | Above this, the issue needs a human's plan; skip it instead of flailing. |
| `workLoop.skipLabels` | Never auto-start an issue carrying these. |
| `cadence.everyDays` | Repair pass may run after this long — **only if unticketed work exists.** |
| `cadence.everyUnticketedMerges` / `everyUnticketedCommits` | "A certain amount of dev work", counting **only work that skipped the loop.** Ticketed commits never trigger anything: they are already reconciled. (The older names `everyMergedPRs` / `everyCommits` still work.) |
| `cadence.roadmapReviewDays` | Independent, cheap clock for the milestone/forecast pass. `0` disables it. |
| `ignoreCommitPatterns` | Commit subjects that are deliberately never ticketed. Keeps trivia out of the backlog and out of the repair pass. |
| `autonomy.*` | `true` = unattended, `"propose"` = comment instead, `false` = never. Stricter than the skill's default table always wins. |

## `.linear-roadmap.state.json` — machine-written, never hand-edited

Written only by `roadmap-gate.py --record`, only after a pass that fully succeeded.

```json
{
  "lastSyncedSha": "f965911c2bf2593904f971860a77f7312d14d9a3",
  "lastSyncedAt": "2026-09-12T07:26:34Z",
  "lastSyncNote": "repair: recorded 3 hotfix commits; M2 flagged atRisk",
  "lastRoadmapReviewAt": "2026-08-23T07:26:34Z",
  "history": [{ "sha": "90a976a3", "at": "2026-09-05T09:02:11Z", "note": "baseline" }]
}
```

`lastSyncedSha` is the interlock: the next brief measures the delta from it, so recording a half-finished pass permanently hides that work. Fail midway → **do not record**; the idempotency rules make the retry safe.

`lastRoadmapReviewAt` runs on its own clock, so a repair pass does not reset the forecast review (pass `--record --mode repair` to keep them separate).

Merge conflicts on this file are expected on busy repos: take the newer `lastSyncedAt`, keep both `history` entries.

## Bootstrapping a repo

1. Write `.linear-roadmap.json` — ask the human for the team and the project↔path mapping; do not guess.
2. `roadmap-gate.py --record --note "baseline"` so the first pass measures a sane delta instead of all of history.
3. Commit both files.
4. Wire the triggers — `scheduling.md`.
