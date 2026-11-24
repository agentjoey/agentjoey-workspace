---
name: engineering-conventions
description: Use when a repo's AGENTS.md, CLAUDE.md or GEMINI.md carries a SHARED-ENGINEERING block, when onboarding a repo to the shared engineering conventions, when asked whether a repo's conventions are current or have drifted, when the same rule text needs changing in several repos at once, or when a harness other than Claude (codex, kimi, agy, opencode) is not picking up a repo's conventions.
---

# Shared engineering conventions

## Core principle

The conventions must live in **one file that every harness reads**, and they must be
**byte-identical everywhere**.

Both halves fail silently, which is why copy-paste loses:

- **The wrong file is invisible.** codex reads `AGENTS.md` and nothing else. A block in
  `CLAUDE.md` works perfectly in Claude Code and does not exist for codex. Nothing
  errors; the agent just behaves as if the rules were never written.
- **Drift has no symptom.** Two repos whose blocks differ by one sentence look fine in
  review. You find out when two agents follow different rules on the same kind of task.

So this skill does not ask you to read the conventions and apply them by judgement. It
ships the canonical text and a script that compares byte for byte.

## Which file each harness reads

Measured by searching each harness binary for the filenames it looks up:

| harness | AGENTS.md | CLAUDE.md | GEMINI.md |
|---|---|---|---|
| Claude Code 2.1.331 | yes | yes | — |
| codex 0.166.0 | **yes, only this** | no | no |
| kimi 2.4.0 | yes | yes | — |
| agy 1.5.2 | yes | no | yes |
| opencode 1.19.3 | yes | yes | — |

`AGENTS.md` is the only file all five read, so it is where the block goes. Keep
`CLAUDE.md` as a one-line `@AGENTS.md` pointer, or make the other names symlinks to a
single real file (see Recipe 3).

## Recipes

### 1. Check whether repos are current — 1 tool call, ~100 tokens

```sh
python3 "$SKILL_DIR/scripts/engineering_block.py" check <dir> [<dir> ...] [--quiet]
```

Looks in `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`, resolving symlinks so one real file
reached by three names counts once. Exits 1 on any problem:

| status | meaning | fix |
|---|---|---|
| `MISSING` | no agent file carries the block | Recipe 2 |
| `DRIFT` | block text differs from the canonical source | Recipe 2 (it replaces in place) |
| `DUP` | two separate real files carry it, so some harnesses load it twice | Recipe 3 |
| `NO-CODEX` | the block is there but not reachable through `AGENTS.md` | Recipe 4 |

Use `--quiet` to print only the repos with problems.

### 2. Adopt or update the block in a repo — 2 tool calls, ~200 tokens

```sh
python3 "$SKILL_DIR/scripts/engineering_block.py" apply <dir> --claude-pointer
```

Inserts the block, or replaces an older or edited one, leaving the rest of the file
untouched. Safe to run again: an already-current file prints `already current` and is
not rewritten. Add `--dry-run` first when the file already holds a lot.

`--claude-pointer` adds `@AGENTS.md` to `CLAUDE.md` so Claude Code reaches the block,
unless that file already reaches it, already carries the block, or is a symlink.

Work on a branch or worktree, never on the default branch. Do not commit unless the
Owner asks.

### 3. One real file, several names (`DUP` fix)

When a repo needs the conventions under more than one filename, do not copy the text.
Keep one real file and symlink the rest:

```sh
cd <repo> && ln -sf CLAUDE.md AGENTS.md && ln -sf CLAUDE.md GEMINI.md
```

Every harness then reads the same bytes whichever name it looks for, and `check`
reports it as `AGENTS.md=CLAUDE.md=GEMINI.md`.

### 4. Block is invisible to codex (`NO-CODEX` fix)

The block sits in `CLAUDE.md` while `AGENTS.md` is missing or holds something else
(often a generated block from another tool, which must be kept). Either move the
conventions into `AGENTS.md` and leave `CLAUDE.md` pointing at it with `@AGENTS.md`, or
apply Recipe 3. Do not delete a generated block to make room — append instead.

### 5. Change the conventions themselves

Edit `references/shared-engineering-block.md`, the only source. Bump the version in both
markers (`<!-- BEGIN SHARED-ENGINEERING v3 -->` and the `END` line stays as is), then run
Recipe 1 across every repo: each one now reports `DRIFT`, and Recipe 2 updates it.
Never edit the block inside a repo — that is what creates drift.

## Red flags

| You are about to | Stop, because |
|---|---|
| paste the block from another repo | that repo may already have drifted; render from the canonical source instead |
| edit the block inside a repo's `AGENTS.md` | the next `apply` overwrites it, and meanwhile that repo disagrees with the others |
| put the conventions in `CLAUDE.md` only | codex will never see them, with no error |
| copy the text into `AGENTS.md` and `GEMINI.md` both | two copies drift; symlink instead (Recipe 3) |
| trust that blocks match because they look alike | run `check`; it compares byte for byte |

## Examples

❌ **Default approach.** Open a repo that has the conventions, copy the block, paste it
into the new repo's `CLAUDE.md`, eyeball it. Result: the pasted text is from a repo that
was edited by hand three weeks ago, and codex cannot read `CLAUDE.md` at all. Both
failures are silent.

✅ **With this skill.** `apply <dir> --claude-pointer` writes the canonical text to
`AGENTS.md` and points `CLAUDE.md` at it; `check <dir>` then prints
`ok <dir>: v2 in AGENTS.md`. Running `check` across every repo afterwards proves they
are identical rather than similar.

## What this block is not

It does not replace a repo's own rules — it is the shared floor, and a repo's specific
conventions go outside the markers. It also overlaps on purpose with Claude Code's
user-level `CLAUDE.md`: the other four harnesses never read that file, so the block has
to stand alone. See `references/scope-and-overlap.md`.
