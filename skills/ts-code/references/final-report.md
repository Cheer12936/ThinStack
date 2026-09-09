# Evidence and Verdict

For DESIGN_ONLY report design readiness and unresolved decisions; for VERIFY_ONLY report reviewed/tested scope and whether checks were executed. These modes do not require a delivery verdict or new RUN.md merely to finish a review. The GREEN/NOT GREEN form below applies to DELIVERY only.

FAST_FIX reports the frozen repair promise, direct cause, correction and actual affected-function proof in a few lines; no module-wide certification or new report document. Use the existing result document for planned work, otherwise RUN.md; LIGHT/LIGHT may report in the response. Do not create a report that repeats the contract.

For each required proof item record:
- acceptance/constraint or override it supports;
- check command or observable procedure and actual result;
- timestamp, environment and tested revision plus relevant worktree changes, or a reproducible snapshot identifier;
- inspectable result/log/report/artifact path.

Command exit status alone does not show meaningful assertions ran: identify the behavior checked and pass/fail/skip result. For visual proof retain a screenshot/render artifact and the observation tied to the relevant criterion. Do not claim machine validation of subjective aesthetics.

Evidence is current only if subsequent changes do not invalidate the behavior it proves. Existing evidence can be reused with that relevance established. For FAST_FIX, the regression check concerns demonstrated side effects of this correction and its promised behavior, not every pre-existing issue in nearby modules. Disclose relevant observed limits without claiming unseen risks were audited. Unrelated findings do not expand Required Proof.

## Final response

For multi-slice DELIVERY, distinguish the current slice verdict from the whole request: list verified/blocked/remaining slices compactly and include relevant cross-slice journey proof. Do not announce overall GREEN after only the first slice or from isolated passing slice tests that leave their integration unproven.

Use the same slice identifiers/names shown in the approved plan so the user can reconcile planned and delivered work. Pair each status with its business result and concise evidence or blocking condition. Do not hide unstarted slices behind a generic success summary. For a tiny single-slice fix, a sentence covering outcome and proof is sufficient; a table is optional.

Use a concise form, omitting empty categories except the remaining-work verdict:

GREEN or NOT GREEN
- Implemented: resulting behavior.
- Evidence: required check -> actual outcome and artifact; explain sufficiency briefly.
- Changed: key file links.
- Risk: material findings, integration evidence limits or relevant contract revisions.
- Remaining: none, or missing work/proof, why blocked, and conditions to continue.

GREEN requires the current scoped acceptance and constraints proven, applicable required gates passed, no demonstrated repair-caused regression and no unresolved relevant high-risk finding. NOT GREEN applies to missing/failed/skipped/stale proof required for that promise. Once these conditions pass, stop investigating; do not add hypothetical cases or reinterpret the repair as a whole-module release audit. Do not sum passing tests to hide a missing criterion.

For external integrations report synthetic contract checks, sanitized real-response replay and live integration separately. A missing live check blocks GREEN whenever actual live behavior is required. A mock-only scope can be proven only as mock/adapter behavior; label that scope explicitly and never imply operational readiness.
