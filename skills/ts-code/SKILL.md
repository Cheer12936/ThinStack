---
name: ts-code
license: MIT
metadata:
  version: "0.1.0-alpha.11"
description: Design, implement or verify software changes through one adaptive harness. Use for feature specifications, project architecture, bug fixes, implementation or testing; preserve the requested scope while applying independent design and verification depths and evidence-based completion.
---

# ts-code

## Route and convergence
Choose the work type before templates or documents: FAST_FIX for a clear localized defect; PROJECT_INIT for a new foundation; SLICE for a planned business outcome or an evidence-backed escalation. New projects, features and architecture changes use the structured design/slice rules below. FAST_FIX defaults to Design LIGHT / Verification LIGHT; an unknown direct cause alone does not raise those depths.

FAST_FIX permits at most 3 high-discrimination diagnostic steps, stopping earlier when the direct cause is confirmed. Each step answers a specific competing hypothesis using the highest-information observation available (such as the failing request, migration status or direct code path); log findings briefly. Count diagnostic questions, not shell calls, and never disguise a system audit as one step or reset the count on resume. If still unresolved after 3, stop diagnosis and report the narrow missing fact or access needed; do not guess a fix, silently keep exploring, or claim GREEN. Evidence-backed escalation or an explicit user extension can authorize a new bounded investigation; uncertainty alone cannot.

Once the cause is confirmed, freeze the repair promise: symptom to restore, direct cause, smallest correction, and minimum affected-function proof. Fix that cause only. No new baseline/SPEC/RUN, slice roadmap, general audit, adjacent consumer survey, opportunistic refactor, new test framework or unrelated cleanup. Existing plans are context, not a mandate to revalidate all their slices. Read only the relevant contract. Verify the original failure and direct consequences of the correction, not the entire module's production readiness.

Leave FAST_FIX only on concrete evidence that the cause/correction involves data corruption or unsafe transformation, a security-boundary defect/change, or architecture/contract change. Name the observation and affected invariant; a database, permission module, coupon feature or UI nearby does not qualify. Apply relevant proof floors and reuse valid design/approval. For locally applying an unchanged existing migration, use the bounded exception in migration.md instead of automatic FULL.

After the frozen repair promise and applicable explicit gates pass, STOP tools, diagnosis and speculative risk exploration; report cause, correction and proof. Incidental unrelated concerns may be mentioned briefly as uninvestigated follow-up, never absorbed into this repair or counted as missing repair evidence. A failed required check or demonstrated harmful side effect remains blocking. Do not impose a promised duration; converge by evidence and the diagnostic bound.

## Core principle
Own outcomes, risk, quality gates and evidence; the model owns implementation strategy. Local fixes under clear existing requirements may proceed directly. For new projects or new business features, first present a substantive structured design proposal and wait for one confirmation before implementation; an ordinary "build/add/initialize" request alone does not approve an unseen plan. Reuse prior approval of the same concrete plan, or an explicit user instruction to skip plan confirmation. After approval, execute continuously within scope without repeated stage confirmations. Analysis-only requests remain read-only. Read [authorization boundaries](references/preflight-and-gates.md) for new project/feature planning or a consequential decision/scope boundary.

Honor the requested mode: DESIGN_ONLY produces requested design artifacts without product code, migrations or executable tests; VERIFY_ONLY plans/reviews or creates/runs tests as requested without product fixes; DELIVERY implements and verifies within authorization. Depth never expands mode or permission. Existing approval of a concrete implementation/TDD plan remains valid. Design-only output reports readiness, and verification-only output reports tested scope; neither implies implemented delivery. In these modes the implementation loop is inactive and no new contract/scaffold is required merely to perform a review. Reuse adequate existing requirements; fill only consequential gaps.

Choose the work type independently of mode: FAST_FIX restores a narrowly defined existing behavior; PROJECT_INIT establishes the minimum architecture and runnable foundation; SLICE delivers one observable business result against that foundation. For a new project or onboarding an existing one, read [project initialization](references/project-init.md). Existing projects are not reset or scaffolded again. For a slice, use relevant existing baseline constraints and describe only the delta. This skill is self-contained; no other skill is required.

Baseline gate: for a new project, clarify material product/architecture questions through discussion before finalizing the baseline proposal. For an existing project, inspect its actual code, tests, schema/migrations and configuration to create, verify or supplement the baseline; do not rely on conversation or old docs alone. Before new business-slice implementation, persist a confirmed, relevant BASELINE_READY record in ARCHITECTURAL_BASELINE.md (or the established equivalent) with sources, approval and unresolved limits. Missing/unready baseline blocks dependent implementation, not investigation or requested design. Reuse valid existing approval and combine baseline/slice confirmation when sufficient. A narrowly scoped fix restoring clear existing behavior may skip project-wide baselining; record that exception briefly. This exception does not cover new capabilities or global-rule changes. Read-only reviews and early brainstorming do not require forced document writes.

Before proposing a new project/feature plan, determine whether the request contains one or several independently verifiable business outcomes. Multiple outcomes MUST be decomposed into a visible slice map with each slice's goal, acceptance target, dependencies and execution order; cover the entire requested scope rather than hiding future outcomes in one large contract. Slice by usable business results, not database/backend/frontend layers or code volume. Keep small coherent requests as one slice; explain any consistency/atomicity reason an apparently large change must remain indivisible. Read [design](references/design.md) for decomposition details.

Use one project-wide slice registry: docs/SLICES.md. All planned business slices, including single-feature additions, use stable consecutive names Slice 1, Slice 2, etc.; never restart numbering per module, request or session, or create PM/CP-style slice namespaces. Reuse the registry in proposals, progress and final reports, and link detailed designs/evidence rather than copying them. Read [registry and resume rules](references/checkpoint-resume.md) when adding, mapping or updating slices. FAST_FIX does not create a registry or new slice just for a small repair; refer to an existing related slice when useful. Read-only reviews do not force writes.

## Visible delivery checkpoints
- Before work: show the understood outcome and slice plan with acceptance targets, dependencies/order and scope of this run. Explicitly identify a single new feature as one slice. Obtain the existing one-time plan confirmation when required; do not add a second approval step.
- During work: at meaningful slice transitions or blockers, identify the current slice, what is verified, and the next action. A slice is complete only with evidence. Do not narrate every tool call or invent progress percentages; keep the user informed during long work.
- At handoff: account for every planned slice as verified, blocked or remaining, with concise evidence and the overall verdict. A single slice can use a short sentence. Local tiny fixes may compress the plan and result into one or two sentences, with no ceremonial table or new confirmation. For design/review-only work, report design/review progress rather than pretending implementation occurred.

## Risk assessment
Assess blast radius, failure cost, uncertainty, security, data, compatibility and external dependencies—not code volume. State Design Depth, Verification Depth, Change Profiles and a brief rationale before editing. For planned work, default an uncertain dimension to STANDARD. FAST_FIX remains LIGHT/LIGHT unless observed risk warrants escalation. Raise the affected dimension to FULL: consequential unresolved architecture affects design, while high failure cost affects verification. Overrides below set minimum floors.

Apply overrides only to observed causes or actual behavior changes. Profiles combine required evidence by union, not by adding redundant suites; one check may prove several invariants. Do not load or stack profiles based on nearby modules or speculative possibilities. Load only matching references:
| Trigger / profile | Minimum requirement | Reference |
|---|---|---|
| AUTH, PERMISSION, tenant isolation, security boundary | Verification FULL | [auth](references/auth.md) |
| Payment / money; historical data mutation; public API breaking change | Verification FULL | [data and contracts](references/database.md) |
| New/modified production-bound migration | Design >= STANDARD; Verification FULL | [migration](references/migration.md) |
| Local application of unchanged existing migration | Bounded target/backup/execution/function proof; no automatic FULL | [migration](references/migration.md) |
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

The contract remains a short verification summary within the full proposal, not a limit on proposal detail. Link adequate existing specs. FAST_FIX uses its short visible symptom/expected behavior/check statement as the contract; no new planning documents regardless of diagnostic effort. Otherwise use the existing feature documents, or SPEC.md for the contract/design and RUN.md for evidence; restore design substance without requiring separate SPEC/ACCEPTANCE/DESIGN files. Read [checkpoint/resume](references/checkpoint-resume.md) when persisting or resuming work.

For a new project/feature, the structured proposal includes this contract and the applicable design sections, rationale, material impact and decisions needed. Present it before requesting confirmation; do not create a separate approval document or treat silence as approval. While awaiting approval, do only read-only investigation and requested planning artifacts, not scaffolding, product code, executable tests or migrations. A pending plan is awaiting confirmation, not a failed GREEN check.

For a multi-slice plan, detail only the current slice's design and Green Contract; later slices need acceptance targets and dependencies, not speculative full specs. Approval of the whole mapped scope authorizes continuous delivery slice by slice without repeated confirmation. Before advancing to a dependent slice, verify and checkpoint its prerequisites; independent authorized work may continue around a blocker. Each slice needs its own scoped proof, and overall GREEN requires every requested slice plus relevant cross-slice integration evidence.

## Autonomous loop
Implement -> verify -> on failure diagnose/fix -> verify again, until the contract is proven, subject to the FAST_FIX diagnostic bound and mandatory stop condition. The model chooses tactics, sequence and test layers. Prefer test-first for bug regressions, complex business rules, deterministic domain logic and high-risk behavior; do not force RED for every task. Honor explicit TDD requests.
Do not weaken valid tests, mock away the subject, ignore failures or remove required proof to reach GREEN. Environment failure is not behavioral RED. If blocked by missing access, evidence or an unresolved decision, continue independent authorized work, then report NOT GREEN with the condition needed to resume.

## Evidence-based recalibration
Raise depth only for demonstrated impact, not an imagined edge case. The model MAY lower either depth and remove an inapplicable proof item when new evidence disproves its triggering assumption; no user approval is needed for this recalibration. State the observation and revised proof briefly. Actual risk floors remain binding, and a failed/unavailable necessary check cannot be reclassified away for convenience. Recalibration cannot change the user goal, waive applicable explicit gates, hide unresolved harm or grant new action permissions. On escalation, expand only the evidence tied to the demonstrated invariant, not all possible subsystem risks.

## GREEN exit criteria
Declare GREEN for the current promise only: **Acceptance Criteria Proven + Applicable Required Gates Passed + No Demonstrated Repair-Caused Regression + No Unresolved Relevant High-risk Finding**. FAST_FIX GREEN means the reported fault is restored, not that its whole module or prior project roadmap is release-ready. Uninvestigated hypothetical risks outside this promise are not required proof.
Every required proof item needs current, inspectable evidence tied to the tested code; executed checks must have commands/results or equivalent machine-inspectable artifacts. Visual judgment additionally needs an artifact and recorded observation. Test counts alone do not prove acceptance.
Missing, skipped, stale or failed proof required by this scoped promise means NOT GREEN; do not manufacture new requirements after acceptance passes. Unrelated future work is outside the contract, not hidden unfinished acceptance. Previously accepted deferral is still unverified and cannot support a claim that the deferred behavior is GREEN.
Use [final evidence](references/final-report.md) for the final verdict, implementation summary, evidence, changed files, material risks and remaining conditions. Keep output proportional.
