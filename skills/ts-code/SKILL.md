---
name: ts-code
license: MIT
metadata:
  version: "0.1.0-alpha.8"
description: Design, implement or verify software changes through one adaptive harness. Use for feature specifications, project architecture, bug fixes, implementation or testing; preserve the requested scope while applying independent design and verification depths and evidence-based completion.
---

# ts-code

## Core principle
Own outcomes, risk, quality gates and evidence; the model owns implementation strategy. Local fixes under clear existing requirements may proceed directly. For new projects or new business features, first present a substantive structured design proposal and wait for one confirmation before implementation; an ordinary "build/add/initialize" request alone does not approve an unseen plan. Reuse prior approval of the same concrete plan, or an explicit user instruction to skip plan confirmation. After approval, execute continuously within scope without repeated stage confirmations. Analysis-only requests remain read-only. Read [authorization boundaries](references/preflight-and-gates.md) for new project/feature planning or a consequential decision/scope boundary.

Honor the requested mode: DESIGN_ONLY produces requested design artifacts without product code, migrations or executable tests; VERIFY_ONLY plans/reviews or creates/runs tests as requested without product fixes; DELIVERY implements and verifies within authorization. Depth never expands mode or permission. Existing approval of a concrete implementation/TDD plan remains valid. Design-only output reports readiness, and verification-only output reports tested scope; neither implies implemented delivery. In these modes the implementation loop is inactive and no new contract/scaffold is required merely to perform a review. Reuse adequate existing requirements; fill only consequential gaps.

Choose the work type independently of mode: PROJECT_INIT establishes the minimum architecture and runnable foundation; SLICE delivers one observable business result against that foundation. For a new project or onboarding an existing one, read [project initialization](references/project-init.md). Existing projects are not reset or scaffolded again. For a slice, use relevant existing baseline constraints and describe only the delta. This skill is self-contained; no other skill is required.

Baseline gate: for a new project, clarify material product/architecture questions through discussion before finalizing the baseline proposal. For an existing project, inspect its actual code, tests, schema/migrations and configuration to create, verify or supplement the baseline; do not rely on conversation or old docs alone. Before new business-slice implementation, persist a confirmed, relevant BASELINE_READY record in ARCHITECTURAL_BASELINE.md (or the established equivalent) with sources, approval and unresolved limits. Missing/unready baseline blocks dependent implementation, not investigation or requested design. Reuse valid existing approval and combine baseline/slice confirmation when sufficient. A narrowly scoped fix restoring clear existing behavior may skip project-wide baselining; record that exception briefly. This exception does not cover new capabilities or global-rule changes. Read-only reviews and early brainstorming do not require forced document writes.

Before proposing a new project/feature plan, determine whether the request contains one or several independently verifiable business outcomes. Multiple outcomes MUST be decomposed into a visible slice map with each slice's goal, acceptance target, dependencies and execution order; cover the entire requested scope rather than hiding future outcomes in one large contract. Slice by usable business results, not database/backend/frontend layers or code volume. Keep small coherent requests as one slice; explain any consistency/atomicity reason an apparently large change must remain indivisible. Read [design](references/design.md) for decomposition details.

## Visible delivery checkpoints
- Before work: show the understood outcome and slice plan with acceptance targets, dependencies/order and scope of this run. Explicitly identify a single new feature as one slice. Obtain the existing one-time plan confirmation when required; do not add a second approval step.
- During work: at meaningful slice transitions or blockers, identify the current slice, what is verified, and the next action. A slice is complete only with evidence. Do not narrate every tool call or invent progress percentages; keep the user informed during long work.
- At handoff: account for every planned slice as verified, blocked or remaining, with concise evidence and the overall verdict. A single slice can use a short sentence. Local tiny fixes may compress the plan and result into one or two sentences, with no ceremonial table or new confirmation. For design/review-only work, report design/review progress rather than pretending implementation occurred.

## Risk assessment
Assess blast radius, failure cost, uncertainty, security, data, compatibility and external dependencies—not code volume. State Design Depth, Verification Depth, Change Profiles and a brief rationale before editing. Default each uncertain dimension to STANDARD; LIGHT needs a positive justification. Raise the affected dimension to FULL: consequential unresolved architecture affects design, while high failure cost affects verification. Overrides below set minimum floors.

Overrides below take precedence over initial judgment. Match profiles to changed behavior, not incidental mentions. Load only matching references:
| Trigger / profile | Minimum requirement | Reference |
|---|---|---|
| AUTH, PERMISSION, tenant isolation, security boundary | Verification FULL | [auth](references/auth.md) |
| Payment / money; historical data mutation; public API breaking change | Verification FULL | [data and contracts](references/database.md) |
| MIGRATION | Design >= STANDARD; Verification FULL | [migration](references/migration.md) |
| CORE_DOMAIN | Design FULL, or explicit impact analysis before retaining lower design depth | [data and contracts](references/database.md) |
| EXTERNAL_API | Verify timeout, invalid response, network failure; retry/idempotency when relevant | [external API](references/external-api.md) |
| CONCURRENCY | Concurrency-specific verification | [concurrency](references/concurrency.md) |
| DATABASE, CRUD | Applicable persistence and consumer invariants | [data and contracts](references/database.md) |
| UI | Observable interaction/presentation proof | [frontend](references/frontend.md) |
| BACKGROUND_JOB, FILE_UPLOAD, CACHE, SEARCH | Applicable lifecycle and consistency risks | [runtime](references/runtime.md) |

## Design depth
LIGHT: existing behavior/contracts suffice. STANDARD: explicit acceptance and necessary design delta. FULL: consequential architecture, identity or core-model decisions and impact analysis.
Read [design](references/design.md) only when such decisions need elaboration or design work is requested. Full design does not require a fixed document count.

For new-project or existing-project baseline proposals, MUST read and use the [baseline proposal format](references/baseline-proposal.md). For new feature/current-slice proposals, MUST read and use the [slice proposal format](references/slice-proposal.md), including when design depth is LIGHT. Restore the former spec-to-design level of substance: concrete rules, observable acceptance and actual domain/data/API/state decisions, not just a task list. Show the structured proposal in the conversation before approval; a file link, slice map or Green Contract alone is not a substitute. Reuse established decisions and mark irrelevant sections explicitly; do not invent detail to fill a template. Local tiny fixes remain concise unless a full proposal is requested.

## Verification depth
LIGHT: focused observable proof for a local low-risk change. STANDARD: acceptance plus affected integration/regression. FULL: risk-specific failure, boundary, compatibility and affected-consumer proof.
Choose Minimum Sufficient Proof, not every test layer. Explain why the selected checks collectively prove acceptance and constraints; overrides and repository-required checks cannot be omitted. Read [verification](references/verification.md) only for nontrivial verification strategy or requested test work. See [depth and proof examples](references/orchestration-flow.md) only when calibration is needed.

## Green Contract
Before any product-code change, record:
- **Goal:** observable outcome.
- **Acceptance Criteria:** behaviors that must hold.
- **Constraints:** invariants and boundaries to preserve.
- **Required Proof:** checks/evidence mapped to those behaviors and constraints, with a short sufficiency rationale.

The contract remains a short verification summary within the full proposal, not a limit on proposal detail. Link adequate existing specs. For local LIGHT/LIGHT fixes, a visible message suffices. Otherwise use the existing feature documents, or SPEC.md for the contract/design and RUN.md for evidence; restore design substance without requiring separate SPEC/ACCEPTANCE/DESIGN files. Read [checkpoint/resume](references/checkpoint-resume.md) when persisting or resuming work.

For a new project/feature, the structured proposal includes this contract and the applicable design sections, rationale, material impact and decisions needed. Present it before requesting confirmation; do not create a separate approval document or treat silence as approval. While awaiting approval, do only read-only investigation and requested planning artifacts, not scaffolding, product code, executable tests or migrations. A pending plan is awaiting confirmation, not a failed GREEN check.

For a multi-slice plan, detail only the current slice's design and Green Contract; later slices need acceptance targets and dependencies, not speculative full specs. Approval of the whole mapped scope authorizes continuous delivery slice by slice without repeated confirmation. Before advancing to a dependent slice, verify and checkpoint its prerequisites; independent authorized work may continue around a blocker. Each slice needs its own scoped proof, and overall GREEN requires every requested slice plus relevant cross-slice integration evidence.

## Autonomous loop
Implement -> verify -> on failure diagnose/fix -> verify again, until the contract is proven. The model chooses tactics, sequence and test layers. Prefer test-first for bug regressions, complex business rules, deterministic domain logic and high-risk behavior; do not force RED for every task. Honor explicit TDD requests.
Do not weaken valid tests, mock away the subject, ignore failures or remove required proof to reach GREEN. Environment failure is not behavioral RED. If blocked by missing access, evidence or an unresolved decision, continue independent authorized work, then report NOT GREEN with the condition needed to resume.

## Escalation
New risk automatically raises the relevant depth and expands Required Proof before dependent work continues. Announce the reason; escalation within scope needs no new approval.
Never autonomously lower either depth after selection, including on resume. Only explicit user authorization permits a downgrade; risk overrides remain minimum floors unless the underlying risky behavior is explicitly removed from scope. Do not silently narrow acceptance or relabel required proof as optional.

## GREEN exit criteria
Declare GREEN only when **Acceptance Criteria Proven + Required Quality Gates Passed + No Known Regression + No Unresolved High-risk Finding**.
Every required proof item needs current, inspectable evidence tied to the tested code; executed checks must have commands/results or equivalent machine-inspectable artifacts. Visual judgment additionally needs an artifact and recorded observation. Test counts alone do not prove acceptance.
Missing, skipped, stale or failed required proof means NOT GREEN. Unrelated future work is outside the contract, not hidden unfinished acceptance. Previously accepted deferral is still unverified and cannot support a claim that the deferred behavior is GREEN.
Use [final evidence](references/final-report.md) for the final verdict, implementation summary, evidence, changed files, material risks and remaining conditions. Keep output proportional.
