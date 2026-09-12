# linear-roadmap-maintenance

让 agent（Claude Code / Codex）**以固定频率、或在积累了一定开发量之后**，自主维护 Linear 里的 project roadmap 与 backlog。

A Claude Code plugin that fixes the **"the tracker lies"** failure: agents ship code fast, nobody updates Linear, and within two weeks the roadmap describes a project that no longer exists — while humans keep planning against it.

It does not ask the agent to "remember to update Linear". It gives it a **gate** (should I sync at all?), a **five-phase sync pass** driven by git evidence, **explicit autonomy boundaries** (what an agent may change unattended vs. must only propose), and an **idempotency contract** so running twice does not duplicate anything.

## How it works

```
cron / CI schedule ─┐
post-merge / push  ─┴─►  roadmap-gate.py  ──not due──►  stop, write nothing
                              │ due
                              ▼
              1. git evidence (commits, merges, changed paths → projects, AGT-123 refs)
              2. read current Linear state  (never write before reading)
              3. close the loop on shipped work  (merged PR ⇒ issue Done; unticketed work ⇒ record it)
              4. groom backlog + re-forecast milestones  (flag a slipping date, never quietly move it)
              5. --record state, commit, report the diff
```

`roadmap-gate.py` is the deterministic half: it reads `.linear-roadmap.json` + `.linear-roadmap.state.json`, measures the delta since the last sync, and prints a JSON *sync brief*. Due-ness trips on any of `everyDays` / `everyMergedPRs` / `everyCommits`. All judgement stays with the agent.

## Install

From this workspace marketplace:

```
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install linear-roadmap-maintenance@agentjoey-workspace
```

Or copy the skill directly for personal use:

```
cp -R plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance ~/.claude/skills/
```

Then, in the repo you want maintained:

1. Write `.linear-roadmap.json` — team, project↔path mapping, cadence, autonomy (schema: `references/config-and-state.md`).
2. `python3 <skill>/scripts/roadmap-gate.py --record --note "baseline"` and commit both files.
3. Wire a trigger — GitHub Actions, cron, a `post-merge` hook, or a `SessionStart` hook (`references/scheduling.md`).

Run it by hand any time with `/roadmap-sync` (add `--force` to bypass the gate).

## Codex

Codex has no skill loader, so point it at the file: add a short `AGENTS.md` section telling it to run the gate before ending a session and to read `SKILL.md` when the gate exits 0, and give it the Linear MCP server (or `LINEAR_API_KEY` for the GraphQL fallback). Copy-pasteable snippets are in `references/scheduling.md`.

## Requirements

- A Linear workspace, reachable via the Linear MCP server (Claude Code / Codex) or `LINEAR_API_KEY` for the GraphQL fallback.
- `python3` and `git` for the gate script. No other dependencies.

## What it deliberately does NOT do

Create projects or initiatives, move committed target dates, cancel work, archive issues, reassign humans, or edit a human-authored issue body. Those are `propose`-only: the agent comments, a human decides. A roadmap an agent can silently rewrite is not a roadmap.
