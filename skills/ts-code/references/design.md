# Design Capability

Read for unresolved consequential design decisions or a design-only request. Authorization, depth and delivery gates belong to SKILL.md; do not restart them here.

## Reuse and delta

Use the project's current canonical decisions and explicit user corrections. Current implementation shows what exists, not what should exist. Preserve stable IDs and existing layouts; link adequate material and fill gaps rather than regenerating equivalent documents.

A missing architecture baseline does not block a local understood fix. Do not invent approved global rules. For new architecture establish the durable skeleton before dependent implementation; for an existing system describe the delta only.

## Compact output

For multiple independently verifiable outcomes, include a compact slice map in the existing plan/spec or project index: Slice ID | business goal | acceptance target | prerequisites | execution order. Check that all requested outcomes are covered; label explicitly deferred work rather than silently dropping it. Each slice should deliver an observable result across the necessary layers, not merely complete a database, controller or UI tier. Shared foundations may be prerequisite work, but their completion is not business delivery.

Detail only the slice being implemented. Later slices retain lightweight targets and dependencies until needed. No fixed number of slices, size budget or extra roadmap file is required. A small coherent behavior is one slice. If safe consistency requires an atomic cross-cutting change, state the concrete coupling instead of forcing artificial intermediate deliveries. Within an approved multi-slice scope, refine internal details without repeated approval; changed business scope or consequential unresolved decisions still use the normal boundary rules.

For new feature design, SPEC.md can contain goal/actor/entry, scope, observable acceptance, necessary design delta, assumptions and unresolved decisions. Existing ACCEPTANCE.md and DESIGN.md remain valid; do not create a competing combined copy. Split only substantial content. Use checkpoint-resume.md for persistence when needed.

For a baseline, one ARCHITECTURAL_BASELINE.md can describe major modules/dependencies, core identity/ownership/relationships and expensive global decisions. Include only applicable tenancy, authorization, IDs, history, time/precision, transactions and API conventions. Add an ADR for consequential choices whose rationale must survive; do not design speculative future tables.

## Data decisions when affected

- Distinguish entities by identity/lifecycle/ownership; avoid both catch-all JSON and a table for every noun.
- State cardinality, optionality, reference ownership and deletion/history consequences.
- Separate technical identity from mutable business keys; define uniqueness scope and normalization, including soft-deleted records.
- Distinguish unknown, absent and not applicable from zero/empty values.
- Use historical snapshots only where past values must survive current-entity changes.
- Define database constraints and transaction/concurrency treatment for invariants; a prior SELECT alone does not prevent a race.
- Derive indexes from actual queries and constraints. Specify numerical precision/time ownership when relevant.
- Separate source artifacts, processing runs and versioned results when reprocessing/history matters.

Load the directly linked DATABASE/CORE_DOMAIN, MIGRATION or CONCURRENCY profiles in SKILL.md only when affected; their risk floors and proof requirements remain authoritative.

## API/state decisions when affected

Specify changed operation semantics, actor/ownership, request/response, validation, stable business errors and side effects. Clarify omitted versus null, replacement versus partial update, pagination/order/filtering and replay/idempotency semantics.

For meaningful lifecycles define transition guards and atomic side effects, illegal-transition behavior, failure/retry/cancellation and stale-result handling. Do not introduce a state machine for trivial local UI state.

Trace changed producers/contracts into existing consumers, derived views and historical workflows. Record behavior to preserve and the corresponding proof needed. Use the applicable profile for external mapping or versioned import requirements instead of duplicating its checklist.

## Readiness and handoff

Ready means observable acceptance, explicit consequential deltas/compatibility and resolved blocking decisions. Label nonblocking assumptions and unresolved decisions; retain project readiness vocabulary where useful.

DESIGN_ONLY may persist requested design but must not create product code, executable migrations or tests, or automatically continue into implementation. Readiness is not GREEN delivery. Within authorized DELIVERY, the model can continue using the resulting contract without another approval ceremony.
