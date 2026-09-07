---
name: slice-to-green
license: MIT
metadata:
  version: "0.1.0-alpha.1"
description: Design, implement or verify software changes through one adaptive harness. Use for feature specifications, project architecture, bug fixes, implementation or testing; preserve the requested scope while applying independent design and verification depths and evidence-based completion.
---

# Slice to Green

## Core principle
Own outcomes, risk, quality gates and evidence; the model owns implementation strategy. Preserve existing project conventions and authorization. A clear implementation request authorizes routine in-scope work; analysis-only requests remain read-only. No repeated approval ceremony. Read [authorization boundaries](references/preflight-and-gates.md) only when a consequential decision or scope boundary arises.

Honor the requested mode: DESIGN_ONLY produces requested design artifacts without product code, migrations or executable tests; VERIFY_ONLY plans/reviews or creates/runs tests as requested without product fixes; DELIVERY implements and verifies within authorization. Depth never expands mode or permission. Existing explicit implementation/TDD authorization remains valid. Design-only output reports readiness, and verification-only output reports tested scope; neither implies implemented delivery. In these modes the implementation loop is inactive and no new contract/scaffold is required merely to perform a review. Reuse adequate existing requirements; fill only consequential gaps.

Choose the work type independently of mode: PROJECT_INIT establishes the minimum architecture and runnable foundation; SLICE delivers one observable business result against that foundation. For a new project or onboarding an existing one, read [project initialization](references/project-init.md). Existing projects are not reset or scaffolded again. For a slice, use relevant existing baseline constraints and describe only the delta. This skill is self-contained; no other skill is required.

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
LIGHT: existing behavior/contracts suffice. STANDARD: concise acceptance and necessary design delta. FULL: consequential architecture, identity or core-model decisions and impact analysis.
Read [design](references/design.md) only when such decisions need elaboration or design work is requested. Full design does not require a fixed document count.

## Verification depth
LIGHT: focused observable proof for a local low-risk change. STANDARD: acceptance plus affected integration/regression. FULL: risk-specific failure, boundary, compatibility and affected-consumer proof.
Choose Minimum Sufficient Proof, not every test layer. Explain why the selected checks collectively prove acceptance and constraints; overrides and repository-required checks cannot be omitted. Read [verification](references/verification.md) only for nontrivial verification strategy or requested test work. See [depth and proof examples](references/orchestration-flow.md) only when calibration is needed.

## Green Contract
Before any product-code change, record:
- **Goal:** observable outcome.
- **Acceptance Criteria:** behaviors that must hold.
- **Constraints:** invariants and boundaries to preserve.
- **Required Proof:** checks/evidence mapped to those behaviors and constraints, with a short sufficiency rationale.

Keep it brief; link adequate existing specs. For LIGHT/LIGHT, a visible message suffices. Otherwise use the existing feature documents, or SPEC.md for the contract and RUN.md for evidence; do not create competing copies. Read [checkpoint/resume](references/checkpoint-resume.md) when persisting or resuming work.

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
