# Project lifecycle runbook

The standard way to add, change and retire a project in the intake flow. Rule text lives in the repo's `SHARED-INTAKE` block; this file is the procedure. `$S` below is `python3 "$SKILL_DIR/scripts/intake_block.py"`.

Facts every step relies on:

- **Linear project id is the stable key** (`P-AJ-n`). Names change. Agents resolve by id.
- **Notion `Project` option is the filter value** in Requests and Slices. The block carries its name.
- The block names no repo. Repo names never matter to the flow.
- Trashed Linear projects still show up with `includeArchived`. They do not count as a name clash, but their issues stay attached to them.

## A. Onboard a project (new, or existing with history)

Owner supplies three things: the `Project` name, the Linear project (create it and note its `P-AJ-n`), and the list of repos.

| # | Step | Who |
|---|---|---|
| 1 | Confirm the Linear id is live and no other **live** project has the same name (`list_projects`, check the `trashed` flag). | agent |
| 2 | Add the `Project` option to Requests **and** Slices. | agent |
| 3 | For each repo: update the checkout first (`git fetch && git merge --ff-only origin/main`), pick the file the agent actually reads (`AGENTS.md`; the tracked `CLAUDE.md` if `AGENTS.md` is gitignored; every file when `AGENTS.md`, `CLAUDE.md` and `GEMINI.md` differ), then `$S apply <dir> --project … --linear-name … --linear-id … [--file …]` on a branch, PR, CI green. | agent |
| 4 | Merge the PRs. | Owner |
| 5 | Legacy sweep (section A2) if the project has history. | agent, Owner rules |
| 6 | Acceptance test (section G). | Owner, agent reads result |

### A2. Legacy sweep

Inventory first, read-only, then rule once per project.

- **Notion legacy trackers** (backlog mirrors, task tables, decision lists): closed items go to one Issue archive page (id, title, result, date); open needs with **no** live Linear issue go to Requests (`Pending` when they need a ruling, `Inbox` otherwise); items that mirror a live Linear issue get nothing, Linear owns them. Trash a tracker only after the counts match. Research and spec pages stay.
- **Old Linear project with open issues:** default is **drain**. Leave the issues where they are, add `--draining "P-AJ-n Old name"` to the block, create nothing new there, and remove the line when the project is empty. Moving issues is possible (`save_issue` with `project`) but drops their Milestones, so only on the Owner's request.
- **Linear issues that are really undecided ideas** (Backlog, "decision", no acceptance criteria): do not bulk-cancel. Put a keep / convert / drop table in front of the Owner; converted ones become Requests pages and are set to Canceled with a comment pointing at the page.

## B. Rename a project

1. Rename in Linear. The id stays.
2. Rename the `Project` option in the Notion **UI** for both databases (the API tool can orphan rows).
3. In every repo of the project: `$S apply <dir> … --formerly "<old name>"` with the new values, PR, merge.
4. Find repos still on the old name: `$S check <dirs> --expect-project "<new name>"`.

Until step 3 is merged a session filters by the old name and sees zero rows. That is the visible failure; never "fix" it by dropping the filter. Drop the `Formerly:` line at the next block upgrade.

## C. Rename or move a repo

- GitHub renames redirect old URLs. Locally: `git remote set-url origin <new url>`.
- The block names no repo, so nothing in the flow changes. The `Project` value does not have to match the repo name.
- Exception: the marketplace repo itself. After renaming `agentjoey-workspace`, re-add the marketplace on each machine.
- A repo that moves to a different project is handled as a re-adoption: `$S apply` with the new project values. Existing Notion rows keep their old `Project`; re-tag them only if the Owner asks.

## D. Add a repo to an existing project

Same as A step 3 with the project's existing values. Nothing in Notion or Linear changes.

## E. Retire a project

1. Every Request is `Done`, `Shelved` or `Dropped`; every Milestone is closed with a Slices record.
2. Linear project to `Completed`.
3. Leave the Notion `Project` option and all rows (history). Do not delete the option.
4. In the repos, delete the block between its markers, or leave it and add a line saying the project is retired.

## F. Upgrade the block everywhere

Change the rule text only in `references/shared-intake-block.md` and bump the version in the `BEGIN` marker. Then `$S check <all repo dirs>` lists every outdated repo; run `apply` in each with that repo's existing values and open one PR per repo. Optional lines (`Formerly`, `Draining`) do not need a version bump.

## G. Acceptance test

Run it in a **fresh** session started after `git pull` (a session started earlier does not carry the block; Codex needs a new thread). Ask these three, in the project's own repo:

| Ask | Pass |
|---|---|
| "How many pending requests?" | Queries the Requests data source with `Project = <name>`. Gives the number (0 is a valid answer). Does not count Linear issues. Mentions no other project. |
| "How many open issues does this project have in Linear?" | Reads Linear by project id, including the draining project if the block names one. |
| "Log an idea: …" | Creates an Inbox row in Requests. Creates no Linear issue. |

| Symptom | Cause |
|---|---|
| Answers the first question from Linear | Session predates the pull, the instruction file is not the one the tool loads, or the block is older than v2 |
| Reads other projects' rows or pages | Block older than v2, or searched Notion instead of querying by id |
| Says Notion is unreachable | Connector not enabled in that tool. The block requires saying so, which is the correct behaviour |
| Finds nothing in Linear | The block names an empty new project and the real issues sit in an old one: add `--draining` |

## Traps seen so far

- A checkout that was not pulled looks exactly like a rule that does not work. Pull first, then judge.
- `apto` ignores `AGENTS.md` in git; the block lives in its `CLAUDE.md`.
- Old Notion pages predate the flow and answer pending-style questions from the wrong source. Sweep them (A2) rather than hoping the agent ignores them.
- Issues attached to a trashed Linear project are easy to forget; list them with `includeArchived`.
