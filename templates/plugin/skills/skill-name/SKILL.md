---
name: skill-name
description: Use when <the concrete situation the agent is in>. Name the triggers an agent can actually detect — a file type, a tool, a phase of work, a symptom — not an abstract topic. This string is the only thing that decides whether the skill loads.
---

# Skill Name

**Core principle:** one or two sentences on the failure mode this skill prevents, and why the obvious approach fails. Be specific; a principle that could apply to any skill teaches nothing.

## Recipe 1 — <the main procedure>

1. Numbered, imperative steps.
2. State costs where they matter (tool calls, tokens, time).
3. Say what NOT to do inline, where the agent is about to do it.

## Recipe 2 — <the next procedure>

Keep SKILL.md skimmable — roughly 150 lines. Detail goes in `references/`,
determinism goes in `scripts/`.

## Red flags — stop and reconsider

- The observable symptom that means the agent is doing the wrong thing
- Another one

## Example

❌ Wrong: what a competent agent does by default, and why it fails.

✅ Right: the same case done by this skill, with the difference made visible.
