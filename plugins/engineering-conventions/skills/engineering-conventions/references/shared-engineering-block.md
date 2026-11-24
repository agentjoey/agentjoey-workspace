<!-- BEGIN SHARED-ENGINEERING v2 -->
## Shared engineering conventions

Optimize delivery time and total token use while preserving correctness, security, and maintainability.

### Scope and collaboration
Follow the task's goal and acceptance criteria. Confirm the checkout and existing changes before editing; preserve unrelated work and isolate concurrent writes. Read applicable instructions and relevant code, expanding context as needed.

### Implementation
Prefer the simplest complete solution, not the smallest diff. Follow sound project patterns. Use refactoring or abstraction when it directly improves the current solution. Avoid unrelated cleanup and speculative features; remove code made unused by your changes.

### Verification
Check changed behavior with focused tests or reproducible checks; ensure regression coverage for bug fixes. Run broader checks when impact or project requirements justify them; inexpensive full checks are fine.
Reuse results only while relevant code, dependencies, configuration, environment, and coverage remain valid. After fixes, rerun affected checks. Do not weaken tests to hide failures; distinguish regressions, existing failures, and environment blockers.

### Review
Review coherent changesets, not each internal task. Self-review low-risk changes; use independent review for high-risk changes such as authorization, destructive data operations, or concurrency. Independent review may use another agent; it is not a human approval gate unless explicitly required.
Focus follow-up reviews on findings, fixes, and affected behavior; expand for new risks. Separate blockers from optional improvements.

### Workflows
Use skills as needed, not as a fixed sequence. Do not restart approved design unless material assumptions change. Check actual rendering for visual changes and real user paths for interaction, authorization, or persistence changes. Use screenshots, e2e, and mutation testing where useful.

### Safety and delivery
Execute approved work end to end. Reuse approvals within their scope, conditions, and validity; phase transitions and routine fixes do not reset them.
Check existing authorization before asking. Batch foreseeable gaps into one request naming targets, operations, and material side effects. General development permission does not authorize unspecified production writes, destructive actions, or external data transfers.
Ask only for a missing consequential decision or permission, a material change beyond agreed scope or risk, or a required human checkpoint. Explain the specific gap or rule and why prior approval is insufficient. Pause affected work only; continue independent authorized tasks.
Mitigate avoidable risks within scope, protect secrets, and respect enforced permissions; never bypass denials. Preserve approval references and limits in existing handoff notes. Finish when acceptance criteria and required checks are met and blockers resolved; report changes, checks, and gaps accurately. Skipped, unrun, or failed checks are not passes.
<!-- END SHARED-ENGINEERING -->
