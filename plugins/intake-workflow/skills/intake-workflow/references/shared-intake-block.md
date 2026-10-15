<!-- BEGIN SHARED-INTAKE v2 -->
## Requirement intake and work tracking

Owner decision 2026-10-15. Needs are discussed in Notion first; Linear holds only work the Owner has confirmed (approved on the Requests page, or confirmed directly in a session). The Intake page holds the stage table, the page templates and the databases: https://app.notion.com/p/3f98c5850c4380588d3fcfa22d8bc62e

- Project: `{{PROJECT}}` (the value of `Project` in the Requests and Slices databases; always filter by it).
- Notion data sources: **Requests** `b20c9483-9aab-42fe-bea0-edafb0ee193d`, **Slices** `53cfefa3-69e8-4fcd-99c9-296946092dd2`. Query them directly by id with `Project = {{PROJECT}}`. Do not find them by searching Notion.
- Linear: team `AJ`, project `{{LINEAR_NAME}}` ({{LINEAR_ID}}). Resolve the project by its id, because names change. A slice is a **Milestone** inside this project, named after the slice goal.{{FORMERLY}}{{DRAINING}}

### Where to look

- Needs, requests, ideas, "pending", "inbox", "approved" → the Requests database (Notion). Issues, tickets, tasks, "todo", "in progress" → Linear. "How many pending requests" is a Requests question, so answer it from Notion and never from Linear counts.
- Read only rows where `Project = {{PROJECT}}`. Do not open other projects' rows or pages, and do not search Notion by keyword (search returns other projects' pages). Notion pages that predate this flow (old backlogs, decision lists) are not the source for this flow; read them only when the Owner points at one.
- If Notion is not reachable in this tool, say so. Do not substitute a Linear count for a Requests count.

### Two kinds of session

- **Discussion session:** reads and writes Requests, analyses, records the discussion on the request page, and after the Owner confirms creates the Linear Milestone and issues. Writes no code.
- **Development session:** takes issues from Linear and implements them. It reads Requests when the Owner asks about requests (see above); otherwise it reads only Linear.

### Rules

1. A Linear issue is created only after the Owner has confirmed the need: the request's Stage is Approved in Notion, or the Owner confirmed it directly in any session, including a development session (small, clear items found outside Intake). Agents cannot delete Linear issues, so an unconfirmed need must not be created there; write it to Requests as Inbox instead.
2. A Linear issue is self-contained: put the analysis conclusion and the acceptance criteria in its description. Sub-agents and worktrees cannot rely on reading Notion. The first line of the description is its source: `Request: <Notion page URL>` or `Confirmed: <YYYY-MM-DD> <who> <one line of what was confirmed>`. An issue with neither line is a violation; list them by searching the project.
3. Ideas and defects found while developing that the Owner has not confirmed go to Requests as Inbox. If the Owner confirms one on the spot, create the issue directly with a `Confirmed:` line, in a Milestone if it belongs to a slice and otherwise loose in the Project.
4. When the last issue of a Milestone is Done, write one Slices record (Delivered, Evidence, Deviation, and an Issues list of every issue id with title and result) and set the Request to Done.
5. The Owner deletes finished Linear issues by hand and tells the agent first. Before any bulk delete, write the Slices record or an archive page so issue ids cited in the repo can still be resolved.
6. Never track progress in two places. If this repo also has its own record-keeping rules, follow them in addition.
7. Renaming the project: rename it in Linear (the id stays), rename the `Project` option in the Notion UI for both databases (the option id stays), update the `Project` and `Linear` lines above, and keep a `Formerly:` line for one version.
<!-- END SHARED-INTAKE -->
