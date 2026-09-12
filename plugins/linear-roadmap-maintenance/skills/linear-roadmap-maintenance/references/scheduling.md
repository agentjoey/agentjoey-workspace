# Wiring the trigger

Two trigger shapes, and you usually want both:

- **Fixed frequency** — a clock fires (cron, CI schedule). Catches drift even when nobody pushes.
- **Work volume** — N merged PRs / commits since the last sync. Catches a busy week before the clock does.

The gate decides in both cases, so every mechanism below is the same one line: *run the gate, sync only if due*. Nothing here needs to know the thresholds.

---

## 1. GitHub Actions — schedule + post-merge (recommended for a shared repo)

`.github/workflows/roadmap-sync.yml`:

```yaml
name: Linear roadmap sync
on:
  schedule:
    - cron: "0 1 * * 1"        # Mondays 01:00 UTC — the fixed-frequency half
  push:
    branches: [main]           # the work-volume half; the gate no-ops when under threshold
  workflow_dispatch:

concurrency:                   # never two syncs at once — that is how duplicates appear
  group: roadmap-sync
  cancel-in-progress: false

jobs:
  sync:
    runs-on: ubuntu-latest
    permissions: { contents: write }
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }          # the gate needs history to measure the delta
      - id: gate
        run: |
          python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py --check \
            && echo "due=true" >> "$GITHUB_OUTPUT" || echo "due=false" >> "$GITHUB_OUTPUT"
      - if: steps.gate.outputs.due == 'true'
        uses: anthropics/claude-code-action@v1
        env:
          LINEAR_API_KEY: ${{ secrets.LINEAR_API_KEY }}
        with:
          claude_code_oauth_token: ${{ secrets.CLAUDE_CODE_OAUTH_TOKEN }}
          prompt: "Run the linear-roadmap-maintenance skill's sync pass, then commit the updated .linear-roadmap.state.json."
```

Check the action's current inputs before copying — they change. The gate step is the load-bearing part; the agent step is interchangeable.

## 2. Local cron — Claude Code or Codex headless

```cron
# Mondays 09:00 local — Claude Code
0 9 * * 1 cd ~/code/myrepo && /usr/local/bin/claude -p "/roadmap-sync" >> ~/.local/state/roadmap-sync.log 2>&1

# Codex, same idea
0 9 * * 1 cd ~/code/myrepo && codex exec "Read .claude/skills/linear-roadmap-maintenance/SKILL.md and run the sync pass." >> ~/.local/state/roadmap-sync.log 2>&1
```

The agent runs the gate first and exits quietly when not due, so a daily cron is fine too — it just no-ops most days.

In a Claude Code session that stays alive (including the web/remote sessions), a scheduled trigger or `/loop` can replace cron; keep the interval at hours, not minutes.

## 3. Work-volume triggers, locally

**`.git/hooks/post-merge`** (and `post-commit` if you don't use branches) — notify, don't auto-launch:

```bash
#!/usr/bin/env sh
GATE="plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py"
[ -f "$GATE" ] || exit 0
python3 "$GATE" --check >/dev/null 2>&1 && echo "▲ Linear roadmap sync is due — run /roadmap-sync"
exit 0
```

A hook must never silently spend tokens or write to Linear behind the user's back. Print, let a human or the next session act.

**Claude Code `SessionStart` hook** — the same signal, delivered where the agent will actually see it. In `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py --check >/dev/null && printf '{\"hookSpecificOutput\":{\"hookEventName\":\"SessionStart\",\"additionalContext\":\"A Linear roadmap sync is due. Offer to run the linear-roadmap-maintenance sync pass before other work.\"}}' || true"
      }]
    }]
  }
}
```

## 4. Codex

Codex has no skill loader, so point it at the file and let it read:

- Add the plugin under `.claude/skills/` (or anywhere in the repo) and reference it from `AGENTS.md`:

```markdown
## Linear roadmap

This repo's roadmap and backlog live in Linear and are maintained by agents.
Before finishing a session that merged work, run:
`python3 plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/scripts/roadmap-gate.py --check`
If it exits 0, read `plugins/linear-roadmap-maintenance/skills/linear-roadmap-maintenance/SKILL.md`
and run the sync pass before ending the session. If it exits 10, do nothing.
```

- Give Codex the Linear MCP server in `~/.codex/config.toml` so it uses the same tools:

```toml
[mcp_servers.linear]
command = "npx"
args = ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
```

Without MCP, Codex uses the GraphQL fallback in `linear-operations.md` with `LINEAR_API_KEY` from the environment.

---

## Picking thresholds

| Repo shape | Start with |
|---|---|
| Solo project, a few pushes a week | `everyDays: 7`, `everyMergedPRs: 5`, `everyCommits: 25` |
| Team repo, many PRs a day | `everyDays: 3`, `everyMergedPRs: 10`, `everyCommits: 999` |
| Agent-heavy repo (many small commits) | `everyDays: 2`, `everyMergedPRs: 3`, `everyCommits: 15` |

If syncs report "nothing changed" repeatedly, the thresholds are too tight. If a human has to fix the roadmap by hand between syncs, they are too loose.

## Two agents, one repo

Concurrency is the real hazard: two syncs at once create duplicate issues. Use the CI `concurrency` group, keep cron schedules apart, and let the committed state file be the tiebreaker — a sync that starts with a stale `lastSyncedSha` reconciles work the other one already handled, which the idempotency rules absorb but should not be routine.
