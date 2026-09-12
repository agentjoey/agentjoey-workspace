# linear-roadmap-maintenance

让 agent（Claude Code / Codex）**从 Linear backlog 按优先级自己取任务来做，做完顺手把状态写回去** —— 并且把这件事的 token 成本控制在一次任务的 5% 以内。

A Claude Code plugin that makes Linear the **work queue**, not an audit target.

The failure it fixes is not "the tracker is stale". It is the fix people usually reach for: a scheduled job that reads sixty commits and a hundred issues to reconstruct what happened. That costs **8–40k tokens** and still guesses wrong. An agent that *starts* from the issue already holds its identifier, its acceptance criterion and its priority — closing it costs two calls at the end of work it was doing anyway.

**Pull → claim → work → close. Reconstruction is the repair path, never the plan.**

## The loop

```
/next-task ──► list_issues(state:backlog, limit:10, fields:[…])   ~400 tok   ← never the default payload
               pick the first that passes the skip filter                    ← don't rank the whole backlog
               get_issue(the one you picked)                      ~600 tok
               claim: state=In Progress, assignee=me              ~150 tok
               ...build... branch agt-123-x, commit "feat: … (AGT-123)"   ← free instrumentation
               close: state=Done + PR link (+ ≤3 follow-ups)      ~200 tok
                                                        ───────────────────
                                                         ~1–2.5k, ≈3% of a task
```

The identifier in the commit is the whole trick: it is what tells the repair pass there is nothing to repair.

## The gate — why upkeep stays cheap

`roadmap-gate.py` classifies every commit since the last sync:

| | |
|---|---|
| **ticketed** (carries `AGT-123`) | the loop already handled it — **zero** work |
| **trivial** (chore/docs/ci) | deliberately never ticketed |
| **unticketed** (a human hotfix, another agent's push) | the only thing a repair pass has any reason to read |

No unticketed work → **not due** → the agent stops without loading a single Linear object. Cadence thresholds count *only* unticketed work, so a healthy repo can keep them tight and still pay nothing. A separate, cheap `roadmapReviewDays` clock handles milestone forecasting.

```
$ roadmap-gate.py --check
{"due": false, "mode": null, "reasons": ["all 22 substantive commits carry an issue identifier (5 trivial) — the work loop kept Linear in sync"]}
```

## What it refuses to spend tokens on

A "starting work" comment · progress comments · a status update per issue · re-listing a backlog already in context · an issue for a typo fix · a 20-line description where 3 lines do (written text is a **recurring** cost — every future reader pays it) · reading git log to find out what you just did · blocking development because a Linear write failed.

And the biggest sink of all: starting an issue whose acceptance criterion you cannot state in one sentence. The skill makes the agent skip it and ask one question instead of flailing.

## Install

```
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install linear-roadmap-maintenance@agentjoey-workspace
```

Or copy the skill for personal use: `cp -R plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance ~/.claude/skills/`

Then, in the repo you want driven from Linear:

1. Write `.linear-roadmap.json` — team, project↔path mapping, `workLoop`, cadence (schema: `references/config-and-state.md`).
2. `python3 <skill>/scripts/roadmap-gate.py --record --note "baseline"`, commit both files.
3. Wire the triggers you want: `/next-task` by hand or on a cron, and the gated repair pass in CI (`references/scheduling.md`).

Commands: **`/next-task`** (take the top backlog issue) and **`/roadmap-sync`** (gated repair / roadmap review).

## Codex

No skill loader, so point it at the file: an `AGENTS.md` section telling it to take work from the backlog, put identifiers in commits, and run the gate before ending a session — plus the Linear MCP server (or `LINEAR_API_KEY` for the GraphQL fallback). Copy-pasteable snippets in `references/scheduling.md`.

## Requirements

`python3` and `git` for the gate. Linear via MCP or `LINEAR_API_KEY`. Nothing else.

## What it will not do unattended

Create projects or initiatives, move committed target dates, cancel work, archive issues, reassign humans, or edit a human-authored issue body. Those are `propose`-only: the agent comments, a human decides. A roadmap an agent can silently rewrite is not a roadmap.
