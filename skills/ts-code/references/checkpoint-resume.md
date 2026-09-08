# Contract, Checkpoint and Resume

Use the established project layout. For new work beyond LIGHT/LIGHT, default to SPEC.md for the Green Contract and needed design, and RUN.md for progress/evidence. Split only substantial material. Existing separate ACCEPTANCE, DESIGN, TEST_PLAN, TEST_RESULT, RUN_STATE and IMPLEMENTATION_REPORT files remain usable; link instead of duplicating them.

A LIGHT/LIGHT contract can remain in a visible message with final evidence. If work becomes long-running or escalates, persist the contract and checkpoint in the existing feature location or the compact layout.

Keep only:
- goal, plan status (awaiting confirmation / approved), and authorization source linked to the concrete approved scope;
- Design Depth, Verification Depth, matching profiles and override floors;
- contract location, material assumptions and reasons for any approved scope/depth revision;
- next action or blocking condition;
- proof items with status, evidence paths and tested revision/worktree context.

Update at meaningful stopping points and when risk or Required Proof changes. Do not maintain a second project status system.

On resume, preserve both selected depths, validate the contract against current authorized intent and repository state, and invalidate affected evidence after material changes. Continue from the earliest unproven dependency without repeating existing valid authorization. An awaiting-confirmation checkpoint remains pending until the user accepts; the existence of SPEC.md or a delivery-mode label alone does not establish approval.

Historical SLICE_DONE/GREEN labels are snapshots, not fresh proof. Keep the project's progress entrypoint consistent with the current verdict and link superseding work when relevant.
