# Linear operations cookbook

Two transports. Prefer the MCP tools; fall back to GraphQL only where MCP is unavailable (some Codex setups, CI containers).

## A. Linear MCP tools (Claude Code, and Codex with the Linear MCP server configured)

### Read before you write — phase 2

```
list_teams                                            → confirm the configured team exists
list_projects     { teamId | query }                  → id/name/state/targetDate of each maintained project
list_issues       { project, limit: 250,
                    fields: ["id","title","status","statusType","labels",
                            "projectMilestone","priority","updatedAt","url","assignee"] }
list_issues       { project, state: "backlog" }       → the grooming set
list_milestones   { project }                         → names, target dates
list_cycles       { team }                            → only if the team runs cycles
list_issue_labels { team }                            → verify `agent-maintained` exists before using it
```

Ask for `fields` explicitly: the default payload is large and a full backlog will crowd out the diff you still need to read.

### Close the loop — phase 3

```
save_issue { id: "AGT-45", state: "Done",
             links: [{ url: "https://github.com/o/r/pull/42", title: "PR #42" }] }
```

Record work that shipped without an issue (create straight into the done state):

```
save_issue { team: "AgentJoey", project: "Website", title: "Ship hero section",
             state: "Done", labels: ["agent-maintained"],
             links: [{ url: "<pr url>", title: "PR #43" }],
             description: "Shipped in 3f2a1b…\n\n<what changed, one paragraph>\n\n<!-- roadmap-sync: 3f2a1b -->" }
```

- `id` present = update, absent = create. Passing `id` on a create is the classic accidental-overwrite bug.
- Use `addLabels` (append-only), not `labels` (replaces the whole set and silently drops a human's labels).
- Use `patch` with `old_string`/`new_string` to edit part of a long description instead of resending it — safer against concurrent human edits.
- `state` takes a state *type or name* (`"Done"`, `"completed"`, `"backlog"`); use the repo's configured `doneState`.

### Groom and forecast — phase 4

```
save_issue      { id: "AGT-77", priority: 2, milestone: "M2" }     # 1=Urgent … 4=Low
save_milestone  { project: "Website", id: "M2", description: "…" } # targetDate only if autonomy allows
save_comment    { issueId: "AGT-77", body: "Roadmap proposal: …" } # the "propose" path
save_status_update {
  type: "project", project: "Website", health: "atRisk",
  body: "Sync 3f2a1b…9c1d0e (14 commits, 5 merges).\n\nShipped: AGT-12, AGT-45.\nMilestone M2: 4/7 issues, target 2026-10-01; at ~1.5 issues/week the remaining 3 land ~2026-10-08.\nProposal: move M2 target or cut AGT-51 — needs a human call." }
```

One status update per project per sync, only when something changed, always citing the commit range.

## B. GraphQL fallback (`LINEAR_API_KEY`)

```bash
linear() {  # usage: linear '<query>' '<json variables>'
  curl -sS https://api.linear.app/graphql \
    -H "Authorization: $LINEAR_API_KEY" \
    -H "Content-Type: application/json" \
    --data "$(python3 -c 'import json,sys;print(json.dumps({"query":sys.argv[1],"variables":json.loads(sys.argv[2] or "{}")}))' "$1" "${2:-}")"
}

# issues in a project
linear 'query($p:String!){ project(id:$p){ name issues(first:250){ nodes{ identifier title state{name type} priority url } } } }' '{"p":"<project-uuid>"}'

# move an issue to done
linear 'mutation($id:String!,$s:String!){ issueUpdate(id:$id,input:{stateId:$s}){ success } }' '{"id":"<uuid>","s":"<state-uuid>"}'

# create
linear 'mutation($i:IssueCreateInput!){ issueCreate(input:$i){ success issue{ identifier url } } }' '{"i":{"teamId":"<uuid>","title":"…","stateId":"<uuid>","description":"…"}}'
```

Never echo `LINEAR_API_KEY`, never paste it into a commit, a Linear body, or a PR description. Read it from the environment only.

## Failure handling

| Symptom | Do this |
|---|---|
| Auth/permission error | Stop. Report it. Do **not** `--record`. |
| Rate limited (429) | Back off, finish the remaining writes, then record — or stop and report the half-done set. |
| Project/team name not found | Stop and ask; do not create it (creation is `propose`-only). |
| A write fails midway | Report exactly what did and did not land, do not record, let the retry reconcile. |
