# Contract, Checkpoint and Resume

FAST_FIX does not create new planning/checkpoint scaffolding. Preserve the diagnostic count (maximum 3), findings and frozen repair promise across interruptions; do not reset the budget or reopen completed investigation. If interrupted, record only the unresolved diagnostic fact and next check in an existing task record when needed; do not restart a project plan on resume. The fuller persistence guidance below applies to planned or escalated work.

Use the established project layout. For new work beyond LIGHT/LIGHT, default to SPEC.md for the Green Contract and needed design, and RUN.md for progress/evidence. Split only substantial material. Existing separate ACCEPTANCE, DESIGN, TEST_PLAN, TEST_RESULT, RUN_STATE and IMPLEMENTATION_REPORT files remain usable; link instead of duplicating them.

A LIGHT/LIGHT contract can remain in a visible message with final evidence. If work becomes long-running or escalates, persist the contract and checkpoint in the existing feature location or the compact layout.

Keep only:
- goal, plan status (awaiting confirmation / approved), and authorization source linked to the concrete approved scope;
- Design Depth, Verification Depth, matching profiles and override floors;
- contract location, material assumptions and reasons for any approved scope/depth revision;
- baseline path/version, relevant readiness and approval/evidence references, or the explicit narrow local-fix exception;
- next action or blocking condition;
- proof items with status, evidence paths and tested revision/worktree context.

## Single project-wide slice registry

docs/SLICES.md is the one authoritative directory of business slices, including projects with only one slice. Read it and any legacy index before assigning IDs. Use Slice 1, Slice 2, etc. plus the business name, never module prefixes or numbering reset per request/session. Allocate the next number above the highest assigned number; cancelled rows stay cancelled, IDs are never reused or renumbered. Dependencies determine execution order independently of numeric order. Modules are optional labels, not another numbering scheme. FR/AC/API/DB requirement IDs are not slice IDs and retain their established forms.

Default columns: Slice | Business goal / acceptance target | Status | Dependencies | Design / evidence. Use planned, active, verified, blocked or cancelled (or clear local-language equivalents); keep the current and next eligible slice visible. Link existing detailed documents without renaming their folders or duplicating summaries. Update the affected row after material state changes; historical verification is dated evidence, not automatically current GREEN.

For existing PM-01/CP-01 or other legacy slice names, establish a one-time mapping here: Slice N -> original ID and document link. Preserve original files, historical references and factual statuses; mapping is not revalidation. Resolve duplicate/ambiguous identities from evidence before numbering; never silently merge distinct slices. Existing indexes may link here but must not remain competing writable inventories. Do not broadly rewrite historical files just for naming.

Before approval, show proposed numbered rows in the conversation; after authorization persist/update docs/SLICES.md before planned implementation. A row never grants implementation permission. Reuse valid approval. Design-only work may persist the registry when requested; read-only work previews only. FAST_FIX never bootstraps the registry or creates a new slice; optionally link an existing related slice's evidence if useful.

Resume through this registry and linked run records: current slice, verified prerequisites and next eligible slice. RUN.md links here rather than maintaining a second map. A verified slice does not imply the remaining slices or whole journey are GREEN.

Update at meaningful stopping points and when risk or Required Proof changes. Do not maintain a second project status system.

On resume, retain the recorded evidence and depths unless new evidence justifies recalibration; validate the contract against current authorized intent and repository state, and invalidate affected evidence after material changes. Continue from the earliest unproven dependency without repeating existing valid authorization. An awaiting-confirmation checkpoint remains pending until the user accepts; the existence of SPEC.md or a delivery-mode label alone does not establish approval.

Historical SLICE_DONE/GREEN labels are snapshots, not fresh proof. Keep the project's progress entrypoint consistent with the current verdict and link superseding work when relevant.
