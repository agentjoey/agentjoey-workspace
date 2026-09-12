# Config and state

Two files at the repo root. Both are **committed** — that is what makes the volume trigger work across machines, agents and CI.

## `.linear-roadmap.json` — hand-written, the contract

```json
{
  "team": "AgentJoey",
  "issuePrefixes": ["AGT"],
  "cadence": {
    "everyDays": 7,
    "everyMergedPRs": 5,
    "everyCommits": 25,
    "firstRunLookbackDays": 30
  },
  "projects": [
    { "name": "Website",       "paths": ["apps/website/**"] },
    { "name": "Design System", "paths": ["packages/ui/**", "packages/hooks/**"] },
    { "name": "Agent Tooling", "paths": ["plugins/**", "scripts/**"] }
  ],
  "doneState": "Done",
  "backlogState": "Backlog",
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
| `team` | Linear team name or ID. **Required** — without it the agent must stop and ask. |
| `issuePrefixes` | Identifier prefixes to scrape from commits/branches. Omit and a denylist filters obvious non-issues (`UTF-8`, `SHA-1`, `RFC-2119`). Setting it is far more reliable. |
| `cadence.everyDays` | Sync when this many days have passed since the last recorded sync. |
| `cadence.everyMergedPRs` | Sync after this many merge commits since the last sync ("a certain amount of dev work"). |
| `cadence.everyCommits` | Same, counting non-merge commits — for repos that push straight to a branch. |
| `cadence.firstRunLookbackDays` | On the very first run there is no state; the brief looks back this far. |
| `projects[].paths` | Glob/prefix patterns mapping changed files to a Linear project. First match wins per pattern list; a path may map to several projects. |
| `autonomy.*` | `true` = do it unattended, `"propose"` = comment instead, `false` = never. Stricter than the skill's default table always wins. |

Any threshold tripping makes the sync due (OR, not AND). Set a threshold to a huge number to disable it.

## `.linear-roadmap.state.json` — machine-written, never hand-edited

Written only by `roadmap-gate.py --record`, only after a sync that fully succeeded.

```json
{
  "lastSyncedSha": "f965911c2bf2593904f971860a77f7312d14d9a3",
  "lastSyncedAt": "2026-09-12T07:14:29Z",
  "lastSyncNote": "closed AGT-45; created 1 shipped-record; M2 flagged atRisk",
  "history": [{ "sha": "90a976a3…", "at": "2026-09-05T09:02:11Z", "note": "baseline" }]
}
```

`lastSyncedSha` is the interlock: the next brief measures the delta from it, so recording a half-finished sync permanently hides that work from reconciliation. If a sync fails midway, **do not record** — fix and re-run; the idempotency rules make the retry safe.

Merge conflicts on this file are expected on busy repos: take the newer `lastSyncedAt`, keep both `history` entries.

## Bootstrapping a repo

1. Write `.linear-roadmap.json` (ask the human for team + project↔path mapping; do not guess).
2. Run `roadmap-gate.py --record --note "baseline"` so the first real sync measures a sane delta instead of the whole repo history.
3. Commit both files.
4. Wire a trigger — see `scheduling.md`.
