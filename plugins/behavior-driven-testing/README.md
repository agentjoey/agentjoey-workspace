# behavior-driven-testing

A Claude Code skill that fixes the **"green gate ≠ works"** failure: tests pass and bugs still ship because the test hit a convenient internal boundary with happy synthetic data, never the real one.

It layers on the `superpowers` skills (test-driven-development, verification-before-completion) — it does **not** restate them. It adds the part they leave open: *where* to test, and *what* proves a feature actually works (real boundary + real data shape/size, plus a probe of the running system before any completion claim). Includes a five-bug-class self-check: role mislabel, real-size breaks UI, missing-value default, display-source inconsistency, interaction dead.

The skill auto-triggers (via its `description`) whenever you write tests for, or claim completion of, a feature/bugfix that crosses a real boundary.

## Provenance

Built and validated with the `superpowers:writing-skills` RED-GREEN-REFACTOR cycle after a real project shipped 14 bugs with a fully-green gate:

- **RED** — a no-skill agent in execution mode wrote a synthetic-internal-boundary test and declared "coverage: done", blind to the real bug.
- **GREEN** — with the skill, the agent tested at the real SDK-envelope boundary and empirically showed the synthetic test stays green while the real one goes red.
- **REFACTOR** — 3/3 pressure scenarios passed across different bug classes, pressures, and a non-UI REST domain (it generalizes).

## Install

From this workspace marketplace:

```
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install behavior-driven-testing@agentjoey-workspace
```

Or copy the skill directly for personal use:

```
cp -R plugins/behavior-driven-testing/skills/behavior-driven-testing ~/.claude/skills/
```

## Project-specific complement

This skill is deliberately tool-agnostic — it states the *kind* of probe required, not the tool. Keep each project's concrete harness (Playwright config, a real-flow probe template, deploy commands) in that project's own instructions (e.g. a `docs/dev-playbook.md`).
