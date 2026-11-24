# Scope, and why the block repeats things you already told Claude

## The overlap is deliberate

Claude Code also reads a user-level `~/.claude/CLAUDE.md`. If that file carries general
engineering guidance, part of this block restates it. Measured against one such file
(244 words) the block (414 words) repeats roughly 100–120 words, concentrated in the
preamble and the `Implementation` section:

| block | typical user-level file |
|---|---|
| Optimize delivery time and total token use while preserving correctness, security, and maintainability | Balance delivery speed and total token use… while preserving correctness, security, and maintainability |
| `Implementation` section | "keep it simple" / "stay focused" guidance, almost sentence for sentence |
| Do not restart approved design unless material assumptions change | execute approved plans without restarting design unless key assumptions change |
| Skipped, unrun, or failed checks are not passes | Never present unrun or failed checks as passed |

**Do not remove the overlap from the block.** codex, kimi, agy and opencode never read
`~/.claude/CLAUDE.md`. Trimming the `Implementation` section to deduplicate for Claude
deletes those rules for the other four harnesses, silently. The block has to stand on
its own.

The cost of the overlap is small — the whole block is about 550 tokens, loaded once per
session — and the real risk is not tokens. It is that the same rule maintained in two
places drifts into two rules that contradict each other. Keep the block canonical here
and treat the user-level file as the place for things only Claude needs (output
language, tone, how to present findings).

## What the block is actually for

By section:

| section | words | overlaps general guidance |
|---|---|---|
| (preamble) | 22 | high |
| Scope and collaboration | 35 | partly |
| Implementation | 38 | high |
| Verification | 63 | partly — the specifics are new |
| Review | 59 | no |
| **Safety and delivery** | **154** | almost none |

`Safety and delivery` is 37% of the block and almost none of it appears in general
single-session guidance: how long an approval stays valid, that phase transitions and
routine fixes do not reset it, that general development permission does not authorize
production writes or destructive actions, batching foreseeable permission gaps into one
request, preserving approval references in handoff notes. Together with `Review` (which
settles when an independent reviewer is required and that another agent may be that
reviewer) that is 213 words — just over half the block — of rules that only matter when
work is delegated across agents and worktrees.

That is the block's reason to exist. A repo whose code is written by delegated harnesses
needs it most, even if a human never reads it.

## Where repo-specific rules go

Outside the markers. Everything between `<!-- BEGIN SHARED-ENGINEERING v2 -->` and
`<!-- END SHARED-ENGINEERING -->` is overwritten by the next `apply`. A repo's own
commands, architecture notes and house rules live above or below it and are never
touched.
