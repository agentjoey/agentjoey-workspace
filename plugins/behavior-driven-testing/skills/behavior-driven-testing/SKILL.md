---
name: behavior-driven-testing
description: Use when writing tests for, or claiming completion of, any feature or bugfix that crosses a real boundary (UI render, SDK/API event, network/IPC, multi-process flow) — especially when a unit/CI gate is green but you have not exercised the real data or driven the running system.
---

# Behavior-Driven Testing

**REQUIRED SUB-SKILL:** superpowers:test-driven-development (RED-GREEN, real code not mocks) and superpowers:verification-before-completion (evidence before claims). This skill adds the part they leave open: *where* to test, and *what* proves a feature actually works.

**Core principle:** A green gate proves the code didn't crash. It does NOT prove the feature works. Bugs ship green because the test hit a convenient internal boundary with happy synthetic data, not the real one (a picker tested with 2 models, real data was 300; a role-mapper tested with a hand-built `{role:'user'}`, the real bug was *deriving* role from the SDK envelope; e2e on mocked fixtures). Only a test at the real boundary with real data — plus a probe of the running system — proves it works.

## Recipe 1 — what a behavior test IS

1. **Real boundary.** Feed the production shape — the actual SDK/API event envelope, real props, real summary object — NOT a hand-built version of your own internal type. If the bug is in a transform, test its *real input*, not its already-transformed output.
2. **Real shape AND size.** Real field names/nesting/magnitude, with the edge that broke it: undefined/empty, 300 not 2, role=user, terminal states, long strings.
3. **User-observable assertion.** What the user/consumer sees (options visible in the DOM, message right-aligned, streamed text reads correctly) — not "callback fired" / "element exists".
4. **Integrated, not isolated-with-mocks.** Run the real path (events → transform → component → DOM). Mock only the true external edge.
5. **Reproduce the failure first.** It must FAIL on the old code for the exact reported symptom, then pass. Can't make it fail? It doesn't test the bug.

## Recipe 2 — acceptance before claiming "works"

1. Run the full gate yourself, read the output (necessary, never sufficient).
2. **Probe the running system on the real path:** for UI, a real-rendered-build e2e (Playwright/etc.) or a manual pass; for a backend/agent flow, spawn→send→inspect the real emitted events against the live service. The gate's mocked-fixture e2e is NOT this probe.
3. Claim WITH that evidence, or state what's unverified. A subagent's "gate green" report is not acceptance — re-verify the behavior yourself.

> The *kind* of probe is the requirement; the *specific* tool + harness is project-local — keep it in the project's instructions, not here.

## Five bug classes — self-check every feature

| Class | Guard |
|---|---|
| Role/identity mislabel | feed a real user-role payload → assert user-side render |
| Real-size breaks UI | render at real magnitude → assert the primary control stays usable |
| Missing-value default | test undefined/empty → assert a sensible fallback |
| Display-source inconsistency | assert the same human label across every surface |
| Interaction dead | fire the real event → assert the resulting content appears |

## Red flags — behavior NOT verified

- "Gate is green, so it's fixed/done"
- Test hand-builds your internal type instead of the real external payload
- Test data smaller/cleaner than production (2 not 300, no empty/edge case)
- Assertion is "callback called" / "element exists", not what the user sees
- About to claim it works without driving the real running flow
- Relaying a subagent's "gate green" as proof of behavior

## Example

Bug: opencode user messages render on the assistant side; `normalizeEvent` mislabeled role. The role is NOT on the text part — it's derived from the SDK `message.updated` envelope and matched to the part by `messageID`.

❌ Wrong boundary (green, blind to the bug): hand-build the already-roled internal part and check pass-through — the role is already correct in the input, so it proves nothing.

✅ Real boundary (fails-before): feed the real `message.updated{info.role:'user'}` + `message.part.updated{part.messageID}` through the real subscribe path → assert `{kind:'message', role:'user'}` (fails on old code). Then probe: send to a live run, confirm the text renders user-side.
