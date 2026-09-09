# Verification Capability

Read when test strategy has a consequential gap or test work is requested. Consume existing acceptance, constraints and Required Proof; do not regenerate the contract. Recalibrate depth/proof only from new evidence as allowed by SKILL.md, not to conceal failing necessary checks.

FAST_FIX normally does not need this reference. If already loaded, do not turn its layer menu into a checklist: use the original failure/reproduction, existing targeted checks and directly affected regression. Add a focused regression test only when it usefully guards the demonstrated defect; do not introduce test infrastructure for a trivial repair. Honor the 3-step diagnostic bound and frozen repair scope. Broader checks require concrete observed impact or an applicable explicit gate; adjacent modules alone do not trigger a profile. Once the scoped proof passes, stop. Diagnose an unrelated failure separately without absorbing its repair into scope.

## Scope and oracle

For a local defect, a clear request plus verified existing contract may be enough. Otherwise use relevant canonical feature/architecture decisions. Code is not the expected-result oracle. Report only ambiguities that prevent defensible assertions.

A plan/review request creates no executable tests or product changes. VERIFY_ONLY may create/run requested tests but cannot fix product code. Explicit implementation/TDD authorization permits fixes within that scope. A failing test does not expand permission.

## Minimum sufficient proof

Map behavior/constraint -> check and boundary -> observable expected result. Use existing frameworks and coverage. Add IDs or a separate test plan only when traceability/size or project conventions justify them.

- Unit: deterministic calculations, transformations and domain rules.
- Integration/API: real serialization, collaborator, database, transaction and enforcement behavior.
- Component: conditional rendering and interaction/recovery behavior.
- Browser/full-stack: actual user entry through frontend, API and persistence.
- Render/visual: presentation evidence plus criterion-specific observation.

Backend E2E excludes the browser; label it distinctly. Avoid duplicating exhaustive cases at every layer. Existing integrated checks may prove several boundaries together.

Use the matching profiles linked in SKILL.md for mandatory auth, data, external, concurrency and runtime risks. They determine coverage floors; these layer suggestions are not a replacement.

## Execution and test integrity

Prefer regression-test-first for bugs and test-first for complex deterministic/high-risk behavior; explicit TDD requires behavioral RED before implementation. Other work may use another order. A broken runner, compile error in a test or invalid fixture is not behavioral RED.

Use isolated representative test data, unique identities and controlled clocks where relevant. Reading a business database never authorizes resetting it. Do not invoke paid/live providers without authorization.

Do not weaken valid assertions, hardcode product behavior for fixtures, skip failing checks or mock away the subject to pass. Modify tests only for a changed requirement or demonstrated test defect, explaining why.

Run the minimal sufficient checks, affected regression and repository-required gates. Recheck after relevant changes; avoid unchanged full-suite repetitions. Classify failure as product defect/regression, test defect, infrastructure or unresolved requirement before deciding whether to fix, revise or report a blocker.

ACTIVE/PLANNED labels may remain in existing projects but cannot create permission or hide a required unverified item.

## Evidence

Use final-report.md for the canonical evidence format and checkpoint-resume.md for storage/resume; do not introduce separate report rules here. Record actual commands/outcomes and inspectable artifacts tied to tested code.

For VERIFY_ONLY report what was tested and any missing proof. A passing subset or completed test plan is not GREEN delivery. For plan-only work explicitly state tests were not executed.
