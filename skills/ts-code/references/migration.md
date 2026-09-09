# Migration: authoring versus local repair

## New or modified production-bound migration
Creating or changing a migration intended for production requires Design at least STANDARD and Verification FULL. Identify schema/data delta, old-data assumptions, affected readers/writers and compatibility treatment. Prove it against an isolated representative prior state, preserving required data/references and exercising affected behavior. Verify restart/concurrency and rollback or forward recovery where applicable; no destructive down-migration merely for symmetry.

## Local application of an unchanged existing migration
A missed local migration can remain FAST_FIX LIGHT/LIGHT. Bound proof to:
- Confirm the local target and exact pending migration using current status and inspect the script for unsafe/destructive or historical-data effects. A local database may still contain valuable data.
- Establish an appropriate backup/recovery point before execution; do not alter or generate migration code, reset data or run unrelated pending changes.
- Apply the intended existing migration through the established runner and verify success plus updated migration status.
- Reproduce the originally failing request/page and confirm the affected function is restored.

These target/backup/execution/function checks are the repair proof, not an invitation to verify the entire business module. Once they pass, stop. Multiple pending migrations with unclear relevance, unknown target, corruption, unsafe transformation or a failed required check prevent blindly applying this exception; identify the concrete issue and escalate only the affected work.

Do not invent an endpoint, database or migration command. A production target is not covered by the local-repair exception: use its authorized deployment/runbook and explicit data safeguards, with proof selected for actual impact. Production execution is not automatically migration authoring, and local success never authorizes production writes.

For authoring/changing migrations or repairing damaged historical data, an empty database pass cannot establish preservation of old data. For a known missed local migration, this is not a mandate to create a new historical-data test matrix once the bounded repair proof is sufficient.
