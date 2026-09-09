# Data, Money and Shared Contracts

For DATABASE/CRUD, select proof for the changed constraints, transactions, ownership, nullability, ordering/pagination and rollback behavior. Use isolated real persistence when database semantics determine correctness.

For CORE_DOMAIN, use Design FULL unless an explicit pre-change impact analysis supports retaining lower design depth. Record changed identities/relationships, readers/writers, business invariants, history and compatibility consequences. Evidence may justify lowering a previously selected depth under the recalibration rule in SKILL.md; actual core-model changes still need the appropriate impact analysis.

Historical data mutation, payment/money behavior and public API breaking changes force Verification FULL:
- Historical data: representative pre-existing records, preserved references/history, intended changes only, repeated application and recovery behavior where applicable. Load migration guidance when data migration is involved.
- Money: precision/rounding, duplicate processing, partial failure/atomicity, reversal or refund behavior where affected. Load external API/concurrency guidance when those boundaries apply.
- Breaking API: known affected consumers, explicit version/transition treatment and representative old/new compatibility or intentional rejection. Acceptance must state the authorized break.

For shared data/contracts trace producer -> persistence/transport -> existing consumers, including reports and derived workflows. Separate passing producer/consumer fixtures are not proof of compatibility.

For versioned imports define business identity independently of representation. Verify old/new coexistence, duplicate/revised source records, optional-field or mapper-version changes and protected downstream references. Never assume JSON equality or mutable contact fields establish source identity.

Unverified necessary consumer compatibility or risky existing-data effects prevent GREEN.
