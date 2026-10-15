---
name: intake-workflow
description: Use when a repo's AGENTS.md or CLAUDE.md contains a SHARED-INTAKE block, when asked about pending, inbox or approved requests or the backlog of a project, when switching to or working on another project, when onboarding or renaming a project, or when about to create a Linear issue, log an idea or defect found while coding, create follow-up issues, or close the last issue of a Linear Milestone.
---

# Intake workflow: Notion first, Linear only when confirmed

**Core principle:** an agent cannot delete a Linear issue, so every issue created for an unconfirmed need is permanent clutter. The control is a gate at creation, not cleanup afterwards. Anything the Owner has not confirmed is written to the Notion Requests database as Inbox, where it can be shelved, dropped or deleted at no cost.

The repo's `AGENTS.md` block (between `SHARED-INTAKE` markers) is the rule text and wins over this skill if they differ. This skill is the how-to.

## Recipe 1 — before you create a Linear issue

1. Has the Owner confirmed this need? Yes if the Requests page is Stage `Approved`, or the Owner said yes in this session. Yes → go on. No → Recipe 2. Your own judgement that "this is obviously needed" is not confirmation.
2. First line of the description is the source: `Request: <Notion page URL>` or `Confirmed: <YYYY-MM-DD> <who> <one line>`. No source line, no issue.
3. Make it self-contained: acceptance criteria and the analysis conclusion in the description. A worker with no Notion access must be able to do it from the issue alone.
4. Create it under the project named in the block (resolve by id). Put it in the slice's Milestone; if it belongs to no slice, leave it loose in the Project. Do not create a catch-all Milestone.

Cost: 1 call. Skipping step 1 costs the Owner a manual delete later.

## Recipe 2 — log an unconfirmed idea or defect

1. Create a page in the Requests database: `Stage = Inbox`, `Project = <the block's Project>`, title in one line.
2. Body: what you saw, where (file, URL, issue id), why it might matter. Do not analyse and do not propose a design; that is the discussion session's job.
3. Tell the Owner in your final message that it is in Inbox. If you have no Notion access, put it in the final message and stop.

Cost: 1–2 calls. This also replaces "up to 3 follow-up issues" at the end of a task: follow-ups go to Inbox, not Linear.

## Recipe 3 — close a Milestone

When the issue you just finished was the last open one in its Milestone:

1. Create a record in the Slices database (`Project`, `Linear` = Milestone URL, `Closed` = today) with a body of **Delivered**, **Evidence** (commit shas, test names, deploy-verify line, the repo's record id), **Deviation** from the acceptance criteria (or "none"), and **Issues**: one line per issue, `<id> · <title> · Done|Canceled (reason)`.
2. Set the related Request to `Done`.
3. Do this before the Owner deletes any issue from that Milestone. The Issues list is how ids cited in the repo are resolved afterwards.

No Notion access? Write the same four parts as a comment on the last issue and say so in your final message; a session with Notion access files it.

## Recipe 4 — rename a project

Rename in Linear (the id stays), rename the `Project` option in the Notion UI for both databases, re-apply the block in each repo with `--formerly "<old>"`, then `intake_block.py check <dirs> --expect-project "<new>"` to find stragglers. A stale name returns zero rows, which is a visible failure; do not fix it by dropping the filter. Full steps: `references/lifecycle.md` section B.

## Recipe 5 — add the flow to a project or repo

Follow `references/lifecycle.md` section A (new project) or D (another repo of a known project). The short form:

1. Notion: add the `Project` option to Requests and Slices. Linear: one live project with the fixed name; note its id.
2. `python3 "$SKILL_DIR/scripts/intake_block.py" apply <repo dir> --project "<P>" --linear-name "<N>" --linear-id <P-AJ-n> --claude-pointer` (add `--file` for each instruction file the repo really uses; add `--draining "P-AJ-n Old name"` only if the Owner wants an older project to run down in place). No checkout? Use `render`.
3. The block contains the Intake page URL and the two data source ids, which grant no access by themselves, so public repos are fine.
4. Acceptance test in a fresh session after `git pull`: `references/lifecycle.md` section G.

Legacy content (old Notion trackers, old Linear projects) is swept once per project under section A2 with `references/legacy-sweep-prompt.md`; the rules themselves apply to needs that appear afterwards.

## Recipe 6 — switching projects

1. **Identity comes from the repo's block and nowhere else.** On entering a repo, or when asked about another project, read that repo's `SHARED-INTAKE` block (local file; through GitHub when it is not checked out) and use its `Project` value and Linear id. Never reuse the previous project's values, ids or Notion rows.
2. Working on several projects from one session: name the target project in every Notion filter and every Linear call, keep the results apart, and write only to the target project's rows.
3. No block in the directory means the project is not onboarded. Say so and offer Recipe 5. Do not guess a project name.
4. Fetch before concluding a rule is missing: a checkout that was not pulled looks exactly like a rule that does not work.

## Red flags — stop and reconsider

- Creating a Linear issue "so it is not forgotten" without the Owner having said yes
- A description whose first line is neither `Request:` nor `Confirmed:`
- A Milestone named "Misc", "Maintenance" or "Backlog" (it never closes; that is how the old project filled up)
- Writing progress into Notion after the Request is `Approved` (Linear owns progress from then on)
- Searching Requests without the `Project` filter, or carrying one project's values into another
- Deleting or renaming Notion `Project` options through an API tool without re-pointing rows

## Example

❌ While fixing AJ-210 you notice the export dialog has no cancel button. You create AJ-231 "Export dialog: add cancel" with priority 3 and carry on. The Owner never saw it, cannot delete it through you, and it sits in Backlog for months.

✅ You create a Requests page "Export dialog has no cancel button" (Inbox, Project = this repo's) with the file and a screenshot reference, and say so in your last message. The Owner replies "do it now": you create the Linear issue with `Confirmed: 2026-10-15 Owner · add cancel to export dialog` as its first line and take it. If the Owner says "later", it stays in Notion and costs nothing.
