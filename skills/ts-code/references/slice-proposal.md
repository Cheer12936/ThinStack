# Feature / Vertical Slice Proposal

Use for a new feature or the current slice before plan confirmation, and when the user requests a full feature design. Present in the user's language. This restores the former spec-to-design proposal structure. Populate with actual decisions, rationale and observable examples; do not output blank template headings, generic promises or implementation to-dos instead of design.

Keep the numbered coverage below. For an unaffected technical section, explicitly state no change / not applicable and why. Reuse actual approved paths, IDs and contracts; label unknowns instead of inventing them. A low design depth permits reuse, not omission of the user-facing explanation.

## 0. Status and context
Baseline reference/version, current slice, design and verification depths, source requirements, proposal/approval status, material assumptions and blocking decisions. Readiness is not approval or implemented GREEN.

## 1. Feature boundary
Explain the problem, intended result and success signal.
- Actors: actor | goal | permission/ownership.
- Primary flow: user entry, actions, system responses and where the result is observed.
- Scope: requirement ID | item | IN_SCOPE / OUT_OF_SCOPE / LATER | reason.
- Business rules: rule ID | concrete rule | source/baseline relation.
- Dependencies and affected existing behavior.

## 2. Slice map and execution scope
For multiple outcomes: slice ID | business goal | acceptance target | prerequisites | order | included in this run.
For a single outcome, explicitly identify one slice. Explain atomic coupling if the change cannot safely be divided. Cover the full requested scope while detailing only the current slice below.

## 3. Acceptance criteria
Use stable AC IDs and concrete Given / When / Then examples where useful.
Cover applicable success, boundary, invalid input, repeated action, permissions, failure/recovery and persistence/history behavior. Specify observable errors or unchanged state; "works correctly" is insufficient.

## 4. Domain delta
Concept | KEEP / ADD / CHANGE | meaning/relationship/ownership change | rationale.
Identify existing concepts reused, identity and lifecycle implications.

## 5. Schema delta
For each changed table/entity specify fields and types/nullability, relationships/cardinality, constraints and justified indexes.
State deletion/history consequences, migration/backfill, old/new compatibility, and concurrency/idempotency treatment.
If unchanged, state NO_PERSISTENCE_CHANGE and the existing persistence reused.

## 6. API delta
For each changed/reused operation: method/path or event, purpose, actor/permission, request and validation, success shape, business errors, tenant/ownership enforcement, retry/idempotency and side effects.
Give representative request/response examples where they clarify the decision. Clearly distinguish verified existing contracts from proposed ones.

## 7. State delta
If meaningful: state | meaning | allowed actions | terminal status.
Transitions: from | trigger | guard | to | atomic side effects.
Explain failure, retry, cancellation and stale/out-of-order behavior when applicable. Otherwise state why no new state machine is needed.

## 8. UI and end-to-end flow
Where UI is in scope, describe entry/navigation, important fields/actions, visible states, validation feedback, recovery and where saved results appear. Explain how the frontend uses the proposed API/state rules; do not substitute visual mockups for behavior.

## 9. Baseline compatibility and impact
List affected rules/ADRs, duplicate concept check, ownership/permission, deletion/history and producer-to-consumer impact.
If global rules change, state BASELINE_CHANGE_PROPOSAL with the concrete delta, rationale and consequences. Identify important alternative choices and why the recommended option fits the current constraints.

## 10. Cross-layer consistency
Finding | severity | affected requirement/contract | resolution or decision needed.
Check acceptance, domain/schema, API/state and UI agree. Surface unresolved conflicts; do not claim they passed without examination.

## 11. Traceability and Required Proof
Requirement/rule | acceptance | domain/data/API/state | proof/check.
Select Minimum Sufficient Proof with reasons; apply risk overrides without demanding every test layer. Include current-consumer regression and integration where relevant.
Summarize Green Contract here by linking the goal, acceptance, constraints and proof already specified, rather than repeating the proposal.

## 12. Readiness, decisions and confirmation
State what is ready, what is unresolved, and assumptions later implementation must preserve. Use established readiness labels if the project has them; separate design readiness, user approval and execution proof.
List only the decisions the user actually needs to make, then request the existing one-time confirmation for the mapped scope. Reuse prior valid approval rather than restarting it.

## Persistence
Keep the existing project layout. In split layouts: SPEC owns boundary/rules/slice map, ACCEPTANCE owns criteria, DESIGN owns deltas/compatibility/traceability. A combined SPEC.md is equally valid for new work. File count is not a completion gate; conversation-only proposals are sufficient before authorization when no persistence was requested.
