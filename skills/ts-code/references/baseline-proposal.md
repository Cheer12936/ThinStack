# Architectural Baseline Proposal

Use for a new project, code-derived onboarding of an existing project, or a requested full baseline design before implementation confirmation. Present in the user's language. Restore the former spec-to-design structure below with concrete recommendations and reasons, not just a scaffolding checklist. Keep the durable skeleton focused on current scope; do not invent all future features.

## 0. Status and source context
Product, version/date, source requirements, mode, design/verification depths, existing constraints, proposed/approved status, assumptions and blocking decisions. Never conflate baseline readiness with approval or implemented GREEN.

For existing code include source paths/revision or worktree context and claim provenance: OBSERVED / VERIFIED / PROPOSED / UNKNOWN. Document discrepancies between code and prior rules, with affected slices and resolution needs. Do not quote secrets or treat tests that were only read as executed proof.

## 1. Product overview and scope
Explain the problem, product goal, first usable outcome and success criteria.
Actors: actor | purpose | permission/ownership scope.
Modules: capability | responsibility | dependencies | in scope / later.
Identify IN_SCOPE, OUT_OF_SCOPE, LATER, external systems and concrete constraints.

## 2. Core domain skeleton
Entities: ID | business meaning | identity | owner/tenant | lifecycle.
Relationships: from | cardinality | to | meaning | historical consequence.
Explain reusable core concepts and why they are distinct; defer feature-local schema detail.

## 3. Global system rules
Rule ID | rule | scope | why global.
Cover applicable tenancy/isolation, identity/auth, IDs, deletion/history, audit, time/precision, money, files, async results, API/errors, idempotency and concurrency.
Mark inapplicable rules; explicitly surface consequential unknowns.

## 4. Architecture and technical decisions
Decision | recommended approach | alternatives | rationale | change cost.
Explain system shape, module boundaries, stack/runtime, storage and external integration choices needed for the first slice. Reuse user/project constraints; do not choose tools because a template lists them.

## 5. Database skeleton
Persistence concept | CORE / DEFERRED / UNRESOLVED | ownership | key relationships | constraints/history.
Define enough logical structure to support the first slices, not every future column or index. Include evolution/migration principles if existing data is involved.

## 6. API and state conventions
API style/versioning, request/response and error conventions, pagination/filtering and ownership enforcement. Explain shared lifecycle/job/retry/versioning rules only where applicable. Distinguish defaults from feature-specific decisions deferred to slices.

## 7. Module dependency map
Show allowed dependencies and prerequisites in a clear list, table or small diagram. Explain which module owns facts and which consumes them. Avoid coupling modules solely to mirror UI pages.

## 8. Business slice roadmap
Order | slice ID/name | observable business outcome | acceptance target | prerequisites | authorized now / later.
Cover all requested outcomes. Separate runnable foundation from business delivery. Fully detail only the current slice using the slice proposal format if it is requested; do not predesign every later slice.

## 9. Foundation Green Contract and proof
For runnable initialization, specify goal, acceptance, constraints and Required Proof for launch/build, harness and necessary connections. Explain why the checks suffice. No unneeded database/auth/container scaffolding. For design-only, identify future proof without pretending to execute it.

## 10. Consistency review and decision log
Finding/decision | severity or status | affected IDs | recommendation/resolution.
Check module/domain/data/auth/API assumptions agree. Distinguish agreed choices, recommendations, nonblocking assumptions and genuinely blocking questions.

## 11. Baseline readiness and confirmation
State readiness, unresolved decisions, retained assumptions and the proposed next slice. Ask for one confirmation of the concrete scope if not already approved; do not begin scaffolding or code while waiting.

Record the baseline gate explicitly: DRAFT / BASELINE_NOT_READY / BASELINE_READY plus persistence state and approval source. READY requires relevant decisions resolved, scope approved and the baseline saved; existence of a draft file alone is insufficient. Explain which intended slices remain blocked by unresolved architecture. No dependent business implementation until the gate is satisfied, subject only to the narrow local-fix exception in SKILL.md.

## Persistence and document index
Normally ARCHITECTURAL_BASELINE.md owns the baseline; list real supporting files only where they exist or are proposed for substantial content. Existing MODULE_MAP / DOMAIN_MODEL / DATA_RULES / API_CONVENTIONS / PERMISSION_MODEL / STATE_RULES / ADR layouts remain valid. Do not require seven architecture files for a small project or create empty placeholders. Preserve current status/evidence separately in the established run record when implementation starts.
