# Depth and Minimum Sufficient Proof

The historical filename is retained for existing links. These are depth examples, not execution sequences.

| Change | Design | Verification | Representative sufficient proof |
|---|---|---|---|
| Button spacing | LIGHT | LIGHT | Render the affected layout; artifact plus observation at relevant viewport |
| Existing permission predicate fix | LIGHT | FULL | Authorized/denied API behavior, escalation and tenant/ownership regressions; browser journey where UI/session wiring matters |
| Ordinary CRUD | STANDARD | STANDARD | API with persistence and affected consumer behavior; UI journey if UI is in scope |
| Core database model refactor | FULL | FULL | Migration against representative old data, constraints/history, affected readers/writers and regression |
| Third-party payment | STANDARD or FULL | FULL | Money invariants, provider failure modes, duplicate/retry behavior and evidence at the actual integration boundary |
| External API change without other override | STANDARD by default | STANDARD or FULL by impact | Required timeout, invalid-response and network-failure checks, plus mapping/consumer proof |
| Pure deterministic calculation | LIGHT or STANDARD | LIGHT or STANDARD | Unit cases may suffice unless money/security or another override raises the floor |

Design measures consequential decisions. Verification measures evidence strength. FULL verification can use a few decisive checks; it does not mean every layer or all repository suites. High uncertainty/broad consequences can independently raise either dimension.

To justify sufficiency, connect each acceptance criterion and relevant constraint to an observable check at the boundary that could fail. Add regression where existing consumers or shared invariants can be affected. Reuse valid current evidence; rerun it if changes invalidate its relevance.

An API integration test can cover transport, service and database in one check. An exhaustively tested rule usually needs only representative integrated wiring proof. No rule mandates Unit + Integration + API + Component + E2E together.

If no available check can prove a required behavior, mark the gap NOT GREEN rather than substituting a narrower mock test. A specialist skill may refine the strategy but cannot lower this harness's override floors or exit criteria.
