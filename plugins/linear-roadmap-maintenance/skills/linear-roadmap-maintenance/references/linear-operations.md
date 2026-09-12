# Linear operations cookbook

Ordered by how often you should need it: the work loop is 4 calls and runs every task; the repair pass is expensive and should run rarely. Prefer the MCP tools; use GraphQL only where MCP is unavailable (some Codex setups, CI containers).

## A. The work loop — 4 calls, ~1–2.5k tokens

### 1. Pull (one call, ~400 tokens)

```
list_issues { team: "AgentJoey", state: "backlog", limit: 10,
              fields: ["id","title","priority","labels","projectMilestone","estimate"] }
```

**`fields` is not optional.** The default payload carries descriptions: 5–10k tokens for a real backlog, to choose one issue. Narrow further when you can:

```
list_issues { project: "Website", state: "backlog", limit: 5, priority: 1, fields: [...] }  # urgent first
list_issues { cycle: "current", state: "backlog", limit: 10, fields: [...] }                # cycle-driven teams
```

### 2. Read the one you picked (~300–1,500 tokens)

```
get_issue { id: "AGT-123" }
```

Only the chosen one. Reading the runners-up is pure waste — you already have their titles.

### 3. Claim (~150 tokens)

```
save_issue { id: "AGT-123", state: "In Progress", assignee: "me" }
```

Skip when `workLoop.claim` is false.

### 4. Close (~200 tokens, once, at the end)

```
save_issue { id: "AGT-123", state: "Done",
             links: [{ url: "https://github.com/o/r/pull/42", title: "PR #42" }] }
```

Follow-ups you actually found, capped at `maxFollowUpsPerTask` (3):

```
save_issue { team: "AgentJoey", project: "Website", title: "Hero image lacks alt text",
             state: "Backlog", priority: 3, addLabels: ["agent-maintained"],
             description: "Found while shipping AGT-123. <one line of what and where>.\n\n<!-- roadmap-sync: 3f2a1b -->" }
```

Keep the body to a few lines. Description text is a **recurring** cost — every future pull and every future reader pays it again.

### Rules that prevent the expensive mistakes

- `id` present = update, absent = create. Passing `id` on a create is the classic accidental-overwrite.
- `addLabels` (append-only), **not** `labels` (replaces the set and drops a human's labels).
- `patch` with `old_string`/`new_string` to edit part of a long body instead of resending it.
- `state` takes a state type or name (`"Done"`, `"completed"`, `"backlog"`) — use the configured `doneState`.
- A failed write does not block development. Report the issue ID as unsynced; the repair pass will catch it because your commit carries the identifier.

## B. The repair pass — only for unticketed commits

Read before writing, and read narrowly: the gate already told you which commits and which projects are in scope.

```
list_issues   { project: "Website", limit: 50,
                fields: ["id","title","status","statusType","labels","projectMilestone","url"] }
list_milestones { project: "Website" }
```

Then, per unticketed commit that represents real work:

```
save_issue { team: "AgentJoey", project: "Website", title: "Fix signup 500",
             state: "Done", addLabels: ["agent-maintained"],
             links: [{ url: "<commit or PR url>", title: "7aff4a4" }],
             description: "Hotfix shipped outside the backlog.\n\n<!-- roadmap-sync: 7aff4a4 -->" }
```

Search before you create: `list_issues { query: "<title words>" }`. A near-title match is a match.

## C. Roadmap review — projects and milestones only

No issue-by-issue reconciliation. Recompute progress, then at most one update per project, only when a human-visible fact changed:

```
save_status_update {
  type: "project", project: "Website", health: "atRisk",
  body: "Milestone M2: 4/7 issues done. Target 2026-10-01; at ~1.5 issues/week the remaining 3 land ~2026-10-08.\nProposal: move the target or cut AGT-51 — needs a human call." }
```

Health must be justified by numbers, not mood. Never move a target date yourself.

## D. GraphQL fallback (`LINEAR_API_KEY`)

```bash
linear() {  # usage: linear '<query>' '<json variables>'
  curl -sS https://api.linear.app/graphql \
    -H "Authorization: $LINEAR_API_KEY" -H "Content-Type: application/json" \
    --data "$(python3 -c 'import json,sys;print(json.dumps({"query":sys.argv[1],"variables":json.loads(sys.argv[2] or "{}")}))' "$1" "${2:-}")"
}

# top of backlog, minimal fields
linear 'query($t:String!){ team(id:$t){ issues(first:10, filter:{state:{type:{eq:"backlog"}}}){ nodes{ identifier title priority estimate labels{nodes{name}} } } } }' '{"t":"<team-uuid>"}'

# claim / close
linear 'mutation($id:String!,$s:String!){ issueUpdate(id:$id,input:{stateId:$s}){ success } }' '{"id":"<uuid>","s":"<state-uuid>"}'

# create
linear 'mutation($i:IssueCreateInput!){ issueCreate(input:$i){ success issue{ identifier url } } }' '{"i":{"teamId":"<uuid>","title":"…","stateId":"<uuid>","description":"…"}}'
```

Never echo `LINEAR_API_KEY`, and never paste it into a commit, a Linear body, or a PR description.

## Failure handling

| Symptom | Do this |
|---|---|
| Auth/permission error | Stop touching Linear, keep developing, report it. Do **not** `--record`. |
| Rate limited (429) | Do not retry-loop. Finish the dev work, report what is unsynced. |
| Project/team not found | Stop and ask; creating one is `propose`-only. |
| A write fails midway | Report exactly what landed and what did not, do not record, let the retry reconcile. |
