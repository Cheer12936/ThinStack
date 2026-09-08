# Project Initialization

PROJECT_INIT and SLICE describe the requested work, independently of DESIGN_ONLY / VERIFY_ONLY / DELIVERY and of both depths.

Before implementing a new project, present the structured baseline proposal required by SKILL.md and obtain the single confirmation defined in preflight-and-gates.md. Until approval, investigate read-only and produce requested design only. Do not interpret "initialize a project" alone as approval of unseen architecture/scaffolding decisions.

For a new project establish product goal, actors and initial scope; decide only the core identities, ownership, module dependencies and expensive global rules needed for the first useful slice. Use design.md for consequential gaps. Record a compact ARCHITECTURAL_BASELINE.md at the project convention's location, normally docs/architecture/. Do not design every future entity or require a fixed collection of architecture documents.

When runnable initialization is requested, the Green Contract covers the minimal engineering foundation: launch/build, configured test harness and necessary infrastructure connections. The model chooses stack-appropriate proof. Initialize only infrastructure actually needed; do not introduce databases, auth systems, containers or CI without a task reason. A runnable foundation is not proof of business functionality.

For DESIGN_ONLY deliver the baseline and readiness/decisions; do not scaffold or execute migrations. For DELIVERY, resolve consequential architecture questions before dependent implementation and verify the agreed foundation. Record evidence/progress in the existing layout or an initialization RUN.md. Initialization GREEN is scoped to that foundation; keep planned business slices explicitly unimplemented.

For an existing project reuse code, docs, database history and tooling. Establish a baseline of verified existing constraints only where useful, with unknowns labeled. Do not reset data, replace the architecture or create a parallel scaffold just because no baseline file exists. A local well-defined slice need not trigger project-wide onboarding.

When the request includes several business outcomes, show the lightweight slice map alongside the initialization proposal; baseline preparation is not a substitute for decomposition. Continue into all slices covered by the approved map without repeated confirmation. A new feature outside that plan needs its own structured proposal and confirmation. For each later slice link applicable baseline rules, detail only the current delta, and update the baseline only if a global rule changes.
