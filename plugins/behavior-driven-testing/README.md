# behavior-driven-testing

A portable agent skill that fixes the **"green gate ≠ works"** failure: tests pass and bugs still ship because the test hit a convenient internal boundary with happy synthetic data, never the real one. The `SKILL.md` is plain Markdown and runtime-agnostic, so it works in any agent runtime that loads skills (Claude Code, Kimi Code, Codex, Copilot CLI, Gemini CLI) — only the *install* step differs per runtime (below).

It layers on the `superpowers` skills (test-driven-development, verification-before-completion) — it does **not** restate them. It adds the part they leave open: *where* to test, and *what* proves a feature actually works (real boundary + real data shape/size, plus a probe of the running system before any completion claim). Includes a five-bug-class self-check: role mislabel, real-size breaks UI, missing-value default, display-source inconsistency, interaction dead.

The skill auto-triggers (via its `description`) whenever you write tests for, or claim completion of, a feature/bugfix that crosses a real boundary.

## Provenance

Built and validated with the `superpowers:writing-skills` RED-GREEN-REFACTOR cycle after a real project shipped 14 bugs with a fully-green gate:

- **RED** — a no-skill agent in execution mode wrote a synthetic-internal-boundary test and declared "coverage: done", blind to the real bug.
- **GREEN** — with the skill, the agent tested at the real SDK-envelope boundary and empirically showed the synthetic test stays green while the real one goes red.
- **REFACTOR** — 3/3 pressure scenarios passed across different bug classes, pressures, and a non-UI REST domain (it generalizes).

## Prerequisite (recommended)

This skill **layers on `superpowers`** — it cross-references `superpowers:test-driven-development` and `superpowers:verification-before-completion` as REQUIRED SUB-SKILLs and does not restate them. Install superpowers too for the links to resolve. Without it the skill still stands on its own (the recipes + five-bug-class checklist are self-contained), but those two references won't load.

## Install

The skill is the same `SKILL.md` everywhere; pick the install for your runtime.

### Claude Code — plugin marketplace

```
/plugin marketplace add agentjoey/agentjoey-workspace
/plugin install behavior-driven-testing@agentjoey-workspace
```

### Kimi Code / Codex / Copilot CLI / Gemini CLI — cross-runtime skills dir

These runtimes don't read the Claude Code plugin format, but they load skills from a directory. Put the skill in the shared cross-runtime dir `~/.agents/skills/` (a symlink to a clone keeps it auto-updating):

```
git clone https://github.com/agentjoey/agentjoey-workspace ~/.agentjoey-workspace
mkdir -p ~/.agents/skills
ln -s ~/.agentjoey-workspace/plugins/behavior-driven-testing/skills/behavior-driven-testing \
      ~/.agents/skills/behavior-driven-testing
```

Then point the runtime at that dir:

- **Kimi Code** — add it to `~/.kimi-code/config.toml`: `extra_skill_dirs = ["/Users/<you>/.agents/skills"]` (or run `kimi --skills-dir ~/.agents/skills`). Verify with: `kimi -p "list your available skills"`.
- **Codex / Copilot CLI / Gemini CLI** — these recognize `~/.agents/skills/` as a cross-runtime skills location automatically.

### Any runtime — copy directly (no auto-update)

```
cp -R plugins/behavior-driven-testing/skills/behavior-driven-testing <your-runtime-skills-dir>/
```

## Project-specific complement

This skill is deliberately tool-agnostic — it states the *kind* of probe required, not the tool. Keep each project's concrete harness (Playwright config, a real-flow probe template, deploy commands) in that project's own instructions (e.g. a `docs/dev-playbook.md`).
