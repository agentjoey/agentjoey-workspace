---
name: linear-roadmap-maintenance
description: Use when Linear is the work queue for a repo — picking the next backlog issue by priority and working it, updating/closing issues as part of finishing a task, judging whether a backlog or roadmap pass is worth the tokens at all, or wiring Claude Code / Codex to run that loop on a cadence or after N merged PRs. Also use when roadmap upkeep is eating development time.
---

# Linear as the work queue

**Core principle:** The backlog is where work comes *from*, not a ledger you reconstruct afterwards. An agent that starts from an issue already holds its identifier, its acceptance criterion and its priority — closing it costs two tool calls at the end of a task it was doing anyway. An agent that codes first and reconciles later must re-derive all of that from git: **10–20× the tokens, and it still guesses wrong.** So: **pull → claim → work → close.** Reconstruction is the repair path, never the plan.

**Second principle:** upkeep that costs more than it saves is a tax, not upkeep. Every rule below carries a token budget. Over budget → cut the bookkeeping, never the engineering.

## Recipe 1 — the loop

1. **Pull the top of the backlog — not the backlog.** One call, `fields` always explicit:
   ```
   list_issues { team: "<team>", state: "backlog", limit: 10,
                 fields: ["id","title","priority","labels","projectMilestone","estimate"] }
   ```
   ~400 tokens. Omitting `fields` pulls every description — 5–10k for a real backlog, for information you will not read.
2. **Pick one** (Recipe 2), then `get_issue { id }` for that one's full description. Never open the ones you did not pick.
3. **Claim it:** `save_issue { id, state: "In Progress", assignee: "me" }`. This is what stops two agents from grabbing the same issue. Solo repo with `workLoop.claim: false` → skip the call.
4. **Work normally** — and pay the instrumentation forward, because it is free: branch `agt-123-hero-section`, commit subject `feat(website): hero section (AGT-123)`. Those identifiers are what make the repair pass a no-op later. This is the single highest-leverage habit in the skill.
5. **Close out** (Recipe 3) in the same session, while you still have the context. A separate "sync session" pays to reload everything you already knew.

**Session shape:** one issue per session by default; at most `workLoop.maxIssuesPerSession` (default 3) and only when they share files or project context. Context over ~50% full → close out what is done and stop. Draining a backlog in one context makes quality fall and cost per issue climb.

## Recipe 2 — picking, cheaply

Walk the pulled list in this order and **stop at the first issue that passes the filter**. Do not rank the whole backlog; that is the classic token trap.

1. Priority 1 (Urgent) → 2. blocks other issues → 3. in the current cycle/milestone with the nearest target date → 4. priority 2/3/4 → 5. least recently updated.

Skip — do not start, do not investigate:

- You cannot state the acceptance criterion in one sentence from the issue text. *(Comment one specific question, move on. An underspecified ticket is the biggest token sink there is — an agent flailing at a vague issue burns more than a week of bookkeeping.)*
- Carries `workLoop.skipLabels` (default `needs-human`, `blocked`, `design`).
- `blockedBy` an issue that is not done.
- Estimate above `workLoop.maxEstimate` — that needs a human's plan first.

Nothing passes the filter? Say so and stop. Do **not** invent work, and do not groom the backlog just because you are idle.

## Recipe 3 — close out: write once, write short

One batch of writes at the end:

```
save_issue { id: "AGT-123", state: "Done",
             links: [{ url: "<PR url>", title: "PR #42" }] }
```

Plus, only if you genuinely discovered them, up to **3** follow-up issues: title, two lines, priority, `agent-maintained` label. More than three means you are generating backlog spam that every future pull has to page through.

Never write, on any task:

| Pure tax | Why |
|---|---|
| A "starting work" comment | `state: In Progress` already says it |
| Progress comments mid-task | Nobody reads them; they cost on every later issue read |
| A project status update per issue | At most one per project per *sync*, and only when a human-visible fact changed (a milestone slipped) |
| Re-listing the backlog you already pulled | It is in your context |
| An issue for a typo / lint / format fix | A record nobody reads costs tokens to write and forever to skim |
| A 20-line description where 3 lines do | Written text is a **recurring** cost: every future reader pays it again |
| Reading git log to find out what you just did | You already know |

**If a Linear write fails: do not block, do not retry-loop.** Finish the development work, name the unsynced issue in your summary, and let the repair pass catch it — your commit carries the identifier, so it will.

## Recipe 4 — the repair pass (only for work that skipped the loop)

Human hotfixes, another agent's commits, an emergency push — work that never came from an issue. That, and only that, needs reconstruction.

```bash
python3 "$SKILL_DIR/scripts/roadmap-gate.py"          # compact brief + verdict
python3 "$SKILL_DIR/scripts/roadmap-gate.py" --check  # exit 0 = due, 10 = not due
```

The gate classifies every commit since the last sync as **ticketed** (carries an identifier — the loop already handled it, zero work), **trivial** (chore/docs/ci — deliberately never ticketed), or **unticketed**. Then:

- `unticketed == 0` → **not due. Stop without loading any Linear state at all.** This is the design paying off: when the loop is working, the repair pass costs one script run and nothing else.
- Unticketed work exists *and* a cadence threshold trips (`everyDays` / `everyUnticketedMerges` / `everyUnticketedCommits`) → **repair mode**: reconcile only the unticketed commits. Read the issues for the touched projects, close what shipped, record genuinely new work as an issue already in the done state, ≤1 status update per project. Do not re-audit the ticketed ones.
- `roadmapReviewDays` elapsed → **roadmap-review mode**: projects and milestones only, no issue-by-issue reconciliation. Recompute milestone progress; if a target date is unreachable at the observed rate, post one status update saying so with the numbers. **Never quietly move the date.**

Finish with `--record --note "<one line>"` and commit the state file. A sync that failed halfway is **not** recorded — the retry is safe by design (Recipe 5).

## Recipe 5 — idempotency (what makes retries free)

1. **Search before create:** `list_issues { query: "<title>" }`. A near-title match is a match — update it, do not add a twin.
2. **Mark what you own:** agent-created issues get the `agent-maintained` label and a `<!-- roadmap-sync: <sha> -->` footer. Only edit bodies carrying that marker; comment on anything else.
3. **Never ticket a commit that already names an issue.**
4. **Use `addLabels`, not `labels`** — the latter replaces the set and silently drops a human's labels. Use `patch` to edit part of a long description rather than resending it.
5. `lastSyncedSha` in the state file is the interlock. Record only after a fully successful pass.

## Token budget — the numbers that decide the rules

| Step | Calls | ~Tokens |
|---|---|---|
| Pull top of backlog (with `fields`) | 1 | 300–600 *(5–10k without)* |
| Read the one issue you picked | 1 | 300–1,500 |
| Claim | 1 | ~150 |
| Close + link | 1 | ~200 |
| Follow-ups (capped at 3) | 0–3 | ~200 each |
| **In-loop total** | **3–6** | **~1–2.5k** |
| Repair pass for the same work, after the fact | 5–15 | **8–40k** |

**The rule:** if Linear upkeep exceeds ~5% of a task's tokens, you are bookkeeping instead of engineering — cut it. Everything in this skill follows from that ratio: pull one issue not a hundred, write at the end not throughout, keep bodies short because reads recur, and instrument commits so the expensive path never runs.

## Autonomy boundaries

| Unattended | Propose only (comment; never apply) |
|---|---|
| Claim, work and close backlog issues | Create projects, initiatives or teams |
| Create follow-up issues (≤3/task) | Close anything as Cancelled / Won't-do |
| Update an issue's own body, labels, links | Change project target dates or committed scope |
| Re-prioritise the backlog during a repair pass | Archive or delete issues; edit a human's issue body |
| One status update per project per sync | Assign work to a human |

A stricter `autonomy` block in `.linear-roadmap.json` always wins. Schema: `references/config-and-state.md`. Tool payloads: `references/linear-operations.md`. Triggers: `references/scheduling.md`.

## Red flags

- Writing code first and planning to "sync Linear afterwards" — that is the 10–20× path
- Pulling the backlog without `fields`, or reading issues you did not pick
- Grooming, re-prioritising or status-updating when you were asked to ship something
- Commenting progress, or posting a status update per issue
- Starting an issue whose acceptance criterion you cannot state in one sentence
- Blocking or retry-looping development because a Linear write failed
- Running a repair pass when every commit is already ticketed
- Moving a milestone date so the roadmap looks green

## Example

Session starts. Pull 10 backlog issues with `fields` (~450 tokens). Top is AGT-51 "Redesign onboarding" — priority 2, no acceptance criterion, label `design` → skip, one comment asking what "done" means. Next is AGT-123 "Hero section responsive breakpoints", priority 2, one-sentence criterion → take it. `get_issue` (~600), claim, branch `agt-123-hero`, build, commit `fix(website): hero breakpoints (AGT-123)`, PR. Close with the PR link; the layout bug found on the way becomes one follow-up issue. **Total upkeep: 4 calls, ~1.4k tokens, ~3% of the task.**

Two weeks later a human hotfixes production directly on main. The gate sees 1 unticketed commit among 22 ticketed ones, trips `everyDays`, and enters repair mode for that *one* commit — not the 22.

❌ The anti-pattern this replaces: code all week, then a Monday job reads 60 commits and 100 issues to guess what happened — tens of thousands of tokens to reconstruct what the loop records for free.
