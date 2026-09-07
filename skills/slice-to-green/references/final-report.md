# Evidence and Verdict

For DESIGN_ONLY report design readiness and unresolved decisions; for VERIFY_ONLY report reviewed/tested scope and whether checks were executed. These modes do not require a delivery verdict or new RUN.md merely to finish a review. The GREEN/NOT GREEN form below applies to DELIVERY only.

Use the existing result document, otherwise RUN.md; LIGHT/LIGHT may report in the response. Do not create a report that repeats the contract.

For each required proof item record:
- acceptance/constraint or override it supports;
- check command or observable procedure and actual result;
- timestamp, environment and tested revision plus relevant worktree changes, or a reproducible snapshot identifier;
- inspectable result/log/report/artifact path.

Command exit status alone does not show meaningful assertions ran: identify the behavior checked and pass/fail/skip result. For visual proof retain a screenshot/render artifact and the observation tied to the relevant criterion. Do not claim machine validation of subjective aesthetics.

Evidence is current only if subsequent changes do not invalidate the behavior it proves. Existing evidence can be reused with that relevance established. No known regression means no known regression left unresolved within the affected system, not a guarantee against every unknown defect; disclose unrelated pre-existing failures without calling their checks passed.

## Final response

Use a concise form, omitting empty categories except the remaining-work verdict:

GREEN or NOT GREEN
- Implemented: resulting behavior.
- Evidence: required check -> actual outcome and artifact; explain sufficiency briefly.
- Changed: key file links.
- Risk: material findings, integration evidence limits or relevant contract revisions.
- Remaining: none, or missing work/proof, why blocked, and conditions to continue.

GREEN requires all contract acceptance and constraints proven, required quality gates passed, no known regression and no unresolved high-risk finding. NOT GREEN applies to any missing/failed/skipped/stale required proof. Do not sum passing tests to hide a missing criterion.

For external integrations report synthetic contract checks, sanitized real-response replay and live integration separately. A missing live check blocks GREEN whenever actual live behavior is required. A mock-only scope can be proven only as mock/adapter behavior; label that scope explicitly and never imply operational readiness.
