---
name: intake-workflow
description: Use when a repo's AGENTS.md contains a SHARED-INTAKE block, or when you are about to create a Linear issue, log a new idea or defect found while coding, create follow-up issues at the end of a task, close the last issue of a Linear Milestone, rename a project, or add the intake flow to another repo.
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

1. Rename in Linear. The project id does not change, which is why the block carries it.
2. Rename the `Project` option in the Notion UI for **both** databases. Renaming through an API tool may create a new option and orphan the existing rows; if you must use it, re-point the rows afterwards.
3. Update the `Project` and `Linear` lines in each repo's block and add `Formerly: <old name>` for one version.
4. `python3 "$SKILL_DIR/scripts/intake_block.py" check <repo dirs> --expect-project "<new name>"` to find repos still on the old name.

A stale name makes queries return zero rows. That is a visible failure; do not "fix" it by searching without the filter.

## Recipe 5 — add the flow to another repo

1. Notion: add a `Project` option to Requests and to Slices. Linear: make sure exactly one live project has the fixed name.
2. Render or apply the block:
   ```
   python3 "$SKILL_DIR/scripts/intake_block.py" apply <repo dir> --project "<P>" --linear-name "<N>" --linear-id <P-AJ-n> --claude-pointer
   ```
   No checkout (repo edited through the GitHub API)? Use `render` and put the output into `AGENTS.md` yourself.
3. Public repo: the block contains only the Intake page URL, no database ids, so it is safe.
4. Check: `intake_block.py check <dirs>`. Then open a new session and ask it for the Pending requests of the project; it should find the right database and filter without being told.

Do not migrate the old backlog as part of adoption. The rules apply to needs that appear afterwards.

## Red flags — stop and reconsider

- Creating a Linear issue "so it is not forgotten" without the Owner having said yes
- A description whose first line is neither `Request:` nor `Confirmed:`
- A Milestone named "Misc", "Maintenance" or "Backlog" (it never closes; that is how the old project filled up)
- Writing progress into Notion after the Request is `Approved` (Linear owns progress from then on)
- Searching Requests without the `Project` filter
- Deleting or renaming Notion `Project` options through an API tool without re-pointing rows

## Example

❌ While fixing AJ-210 you notice the export dialog has no cancel button. You create AJ-231 "Export dialog: add cancel" with priority 3 and carry on. The Owner never saw it, cannot delete it through you, and it sits in Backlog for months.

✅ You create a Requests page "Export dialog has no cancel button" (Inbox, Project = this repo's) with the file and a screenshot reference, and say so in your last message. The Owner replies "do it now": you create the Linear issue with `Confirmed: 2026-10-15 Owner · add cancel to export dialog` as its first line and take it. If the Owner says "later", it stays in Notion and costs nothing.
