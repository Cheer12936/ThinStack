# Changelog

## 0.1.0-alpha.5 — 2026-09-08

- Require a visible business-outcome slice map for multi-outcome requests before plan approval.
- Detail only the current slice; preserve small/atomic changes without artificial splitting.
- Approval of a mapped multi-slice scope permits continuous in-scope execution without per-slice confirmation.
- Track slice states and prerequisites; overall GREEN requires all requested slices and relevant integration evidence.


## 0.1.0-alpha.4 — 2026-09-08

- Authorization behavior change: new projects and new business features show a concise concrete plan and wait for one confirmation before implementation.
- Local understood fixes remain direct; the same already-approved plan or an explicit instruction to skip confirmation avoids duplicate approval.
- Approval covers continuous in-scope implementation and verification; pending confirmation survives resume.
- No new repeated stage gates, test-layer requirements or reduced evidence floors.


## 0.1.0-alpha.3 — 2026-09-08

- Rename the display name, folder and invocation from thinslack-code to ts-code.
- Update installation tools and documentation; behavior and quality gates unchanged.
- Archive earlier installations after installing ts-code to avoid duplicate active rules.


## 0.1.0-alpha.2 — 2026-09-08

- Rename the displayed skill to Thinslack-Code and its folder/invocation to thinslack-code.
- Update installation tooling, validation and usage examples. Repository name remains ThinStack.
- No workflow, permission or verification-floor changes. Archive the previous slice-to-green installation after installing the new name; historical reports and copyright notices remain unchanged.


## 0.1.0-alpha.1 — 2026-09-08

- Single self-contained skill; removed separate design/test entrypoints from the distribution.
- Project initialization and slice delivery distinguished from design-only/verification-only/implementation scope.
- Independent design and verification depths, risk override floors and evidence-based GREEN.
- Clarified that high failure cost raises verification without automatically requiring full architecture design.
- Scope-appropriate reports for design/review; no fabricated delivery verdict.
- Explicit-target installer with backups; portable structural checks; isolated runnable evaluations.

This alpha changes invocation names and removes legacy compatibility entrypoints. Existing project documentation is preserved. Downgrade rules, risk floors and authorization boundaries must be called out in later changes.
