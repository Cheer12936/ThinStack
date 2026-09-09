# Contract, Checkpoint and Resume

Use the established project layout. For new work beyond LIGHT/LIGHT, default to SPEC.md for the Green Contract and needed design, and RUN.md for progress/evidence. Split only substantial material. Existing separate ACCEPTANCE, DESIGN, TEST_PLAN, TEST_RESULT, RUN_STATE and IMPLEMENTATION_REPORT files remain usable; link instead of duplicating them.

A LIGHT/LIGHT contract can remain in a visible message with final evidence. If work becomes long-running or escalates, persist the contract and checkpoint in the existing feature location or the compact layout.

Keep only:
- goal, plan status (awaiting confirmation / approved), and authorization source linked to the concrete approved scope;
- Design Depth, Verification Depth, matching profiles and override floors;
- contract location, material assumptions and reasons for any approved scope/depth revision;
- baseline path/version, relevant readiness and approval/evidence references, or the explicit narrow local-fix exception;
- next action or blocking condition;
- proof items with status, evidence paths and tested revision/worktree context.

For multi-slice work, keep the slice map and each slice's state (planned / active / verified / blocked), current slice, verified prerequisites and next eligible slice in the existing index/run record. Link individual evidence instead of copying it. Resume the unfinished approved plan, not a new monolithic implementation; prior approval covers only the mapped scope. A verified slice does not imply the remaining slices or overall journey are GREEN.

Update at meaningful stopping points and when risk or Required Proof changes. Do not maintain a second project status system.

On resume, preserve both selected depths, validate the contract against current authorized intent and repository state, and invalidate affected evidence after material changes. Continue from the earliest unproven dependency without repeating existing valid authorization. An awaiting-confirmation checkpoint remains pending until the user accepts; the existence of SPEC.md or a delivery-mode label alone does not establish approval.

Historical SLICE_DONE/GREEN labels are snapshots, not fresh proof. Keep the project's progress entrypoint consistent with the current verdict and link superseding work when relevant.
