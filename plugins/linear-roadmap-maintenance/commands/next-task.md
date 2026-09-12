---
description: Pull the highest-priority workable issue from the Linear backlog and start it.
argument-hint: "[project name or issue id]"
---

Start the `linear-roadmap-maintenance` work loop for this repository.

Arguments: $ARGUMENTS (a project name narrows the pull; an issue identifier takes that issue directly, skipping selection).

1. Read `.linear-roadmap.json` for the team, `workLoop` settings and project↔path mapping. Missing → ask for the team and mapping instead of guessing; offer to write the config.
2. Pull the top of the backlog in **one** call with an explicit `fields` list (never the default payload). Stop at the first issue that passes the skip filter — do not rank the whole backlog.
3. `get_issue` for that one issue only. If you cannot state its acceptance criterion in one sentence, leave one specific question as a comment and move to the next candidate.
4. Claim it (`state: In Progress`, `assignee: "me"`) unless `workLoop.claim` is false. Report which issue you took and why, in one line.
5. Build it. Put the identifier in the branch name and the commit subject — that is what keeps the expensive repair pass from ever being needed.
6. Close out in this same session: `state: Done` plus the PR link, and at most 3 genuine follow-up issues. No progress comments, no status update for a single issue.
7. Stop at `workLoop.maxIssuesPerSession`, or sooner if context is over half full.
