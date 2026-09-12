# Wiring the triggers

Three different things get triggered, and they cost wildly different amounts. Do not wire them the same way.

| What | When | Cost |
|---|---|---|
| **The work loop** | Whenever an agent has capacity to build something | ~1–2.5k tokens of upkeep on top of work it was doing anyway |
| **The repair pass** | Cadence, **and only if unticketed work exists** | 8–40k — this is the one worth avoiding |
| **The roadmap review** | Every `roadmapReviewDays` | ~2–5k (projects and milestones only) |

The gate decides for the last two, so every mechanism below is the same line: *run the gate, act only if due*. When the loop is healthy the gate exits 10 and nothing else runs — one script execution, no model tokens.

---

## 1. Starting the work loop

There is nothing to schedule here: the loop starts when someone (or something) gives an agent capacity.

- **A human:** `/next-task`, or "what should I pick up?"
- **Session start** — offer, never auto-start. `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "printf '{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"This repo takes work from Linear. If the user has no task in mind, offer to run /next-task (pull the top backlog issue by priority).\"}}'"
      }]
    }]
  }
}
```

- **Unattended batch** (a nightly agent that works the queue): one issue per run, `maxIssuesPerSession` respected, and only with `workLoop.claim: true` so runs cannot collide.

```cron
0 2 * * 1-5 cd ~/code/myrepo && claude -p "/next-task" >> ~/.local/state/next-task.log 2>&1
```

Do not schedule the loop more often than you can review its output. An agent shipping unreviewed PRs at 3am is a throughput problem, not a scheduling win.

## 2. The repair pass — schedule + push, gated

`.github/workflows/roadmap-sync.yml`:

```yaml
name: Linear roadmap sync
on:
  schedule:
    - cron: "0 1 * * 1"        # weekly clock
  push:
    branches: [main]           # volume half; the gate no-ops on ticketed work
  workflow_dispatch:

concurrency:                   # two syncs at once is how duplicates appear
  group: roadmap-sync
  cancel-in-progress: false

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }          # the gate needs history
      - id: gate
        run: |
          GATE=plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py
          if OUT=$(python3 "$GATE" --check); then
            echo "due=true" >> "$GITHUB_OUTPUT"
            echo "mode=$(echo "$OUT" | python3 -c 'import json,sys;print(json.load(sys.stdin)["mode"])')" >> "$GITHUB_OUTPUT"
          else
            echo "due=false" >> "$GITHUB_OUTPUT"; echo "$OUT"
          fi
      - if: steps.gate.outputs.due == 'true'
        uses: anthropics/claude-code-action@v1
        env:
          LINEAR_API_KEY: ${{ secrets.LINEAR_API_KEY }}
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          prompt: "Run the linear-roadmap-maintenance skill's ${{ steps.gate.outputs.mode }} pass, then commit .linear-roadmap.state.json."
```

The gate step is the load-bearing part — it is what keeps a `push` trigger from costing anything on a normal day. Check the action's current inputs before copying; they change.

Local equivalent:

```cron
0 9 * * 1 cd ~/code/myrepo && claude -p "/roadmap-sync" >> ~/.local/state/roadmap-sync.log 2>&1
```

## 3. Nudges, not launches

**`.git/hooks/post-merge`** — print, never spend:

```bash
#!/usr/bin/env sh
GATE="plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py"
[ -f "$GATE" ] || exit 0
python3 "$GATE" --check >/dev/null 2>&1 && echo "▲ unticketed work has piled up — run /roadmap-sync"
exit 0
```

A hook must never silently spend tokens or write to Linear behind the user's back.

## 4. Codex

Codex has no skill loader, so point it at the file. In `AGENTS.md`:

```markdown
## Work comes from Linear

Pick work from the Linear backlog, do not invent it. To start a task, read
`plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/SKILL.md`
and follow the work loop: pull the top of the backlog with an explicit field
list, claim one issue, put its identifier in the branch and commit subject
(`feat: hero (AGT-123)`), and close it with the PR link when done.

Before ending a session, run:
`python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py --check`
Exit 0 → run the pass it names. Exit 10 → do nothing; that is the normal case.
```

Give Codex the same tools via `~/.codex/config.toml`:

```toml
[mcp_servers.linear]
command = "npx"
args = ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
```

Without MCP it uses the GraphQL fallback in `linear-operations.md` with `LINEAR_API_KEY`.

---

## Picking thresholds

Thresholds only ever count **unticketed** work, so a healthy repo can leave them tight without paying anything.

| Repo shape | Start with |
|---|---|
| Solo, work loop used consistently | `everyDays: 7`, `everyUnticketedMerges: 3`, `everyUnticketedCommits: 10` |
| Team repo, humans push outside Linear | `everyDays: 3`, `everyUnticketedMerges: 5`, `everyUnticketedCommits: 15` |
| Mostly agent-driven, few humans | `everyDays: 14`, `everyUnticketedCommits: 5`, `roadmapReviewDays: 14` |

Symptoms: repair passes that repeatedly find nothing → thresholds too tight, or `ignoreCommitPatterns` too narrow. Humans fixing the roadmap by hand → too loose. Repair passes that find *a lot* every time → the work loop is not being used; fix that, not the cadence.

## Two agents, one repo

Concurrency is the real hazard. `workLoop.claim: true` so two agents cannot take the same issue; a `concurrency` group so two repair passes cannot run at once; separated cron schedules; and the committed state file as the tiebreaker.
