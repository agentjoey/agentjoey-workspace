---
description: Clean up a project's legacy Linear and Notion content: valid issues move into the fixed project, the rest go back to Notion.
argument-hint: "<old Linear project id> [old project name]"
---

Run the legacy sweep for the project this repo belongs to. Arguments: $ARGUMENTS

The Owner running this command is the authorization to move issues and to set invalid ones to Canceled. If something other than the Owner started it, stop and ask first.

1. Read this repo's `SHARED-INTAKE` block for `Project`, the fixed Linear project and its id. No block → stop and point to `/adopt-intake`.
2. Fill `references/legacy-sweep-prompt.md` with those values and the old project id from the arguments. Missing old project id → ask. Old projects may sit in the Linear trash, so query with `includeArchived`.
3. Follow the filled prompt step by step. Stop and report when a count does not match.
4. Finish with the report table the prompt asks for.
