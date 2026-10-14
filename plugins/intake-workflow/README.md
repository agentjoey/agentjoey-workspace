# intake-workflow

需求先在 Notion 讨论，Owner 确认后才进 Linear；一个 Milestone 做完写一条 Slices 记录。解决的是：agent 在 Linear 里删不掉 issue，没讨论清楚的条目一旦建出来就永久留下。

Needs are discussed in a Notion Requests database first. A Linear issue is created only after the Owner confirms the need. When the last issue of a Milestone is done, one Slices record is written. The reason: an agent cannot delete a Linear issue, so every issue created for an unconfirmed need is permanent clutter — the control has to be a gate at creation, not cleanup afterwards.

## What it contains

- `skills/intake-workflow/SKILL.md` — when to create a Linear issue, where to log an unconfirmed idea, how to close a Milestone, how to rename a project, how to adopt the flow in another repo.
- `skills/intake-workflow/references/shared-intake-block.md` — the canonical rule block. Every repo carries a copy between `SHARED-INTAKE` markers in `AGENTS.md`; only the project lines differ.
- `skills/intake-workflow/scripts/intake_block.py` — `render`, `check`, `apply`. Zero dependencies.
- `/adopt-intake` and `/intake-check` — slash commands wrapping the script.

## Install

```
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install intake-workflow@agentjoey-workspace
```

On a machine without the plugin, the repo's own `AGENTS.md` block is enough for any coding agent to follow the rules; the plugin only automates adoption and drift checks.

## What it will not do

- It never creates, edits or deletes Notion or Linear data by itself; the script only touches `AGENTS.md` / `CLAUDE.md` files you point it at.
- It does not migrate an old backlog. The rules apply to needs that appear after adoption.
- It does not override a repo's own stricter rules. Where a repo carries the `SHARED-INTAKE` block, the block wins over `linear-roadmap-maintenance` for follow-up issues: unconfirmed follow-ups go to the Requests Inbox, not to Linear.
