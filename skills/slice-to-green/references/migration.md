# Migration

Any database migration requires Design at least STANDARD and Verification FULL, including additive migrations.

Before dependent changes, identify the schema/data delta, old-data assumptions, affected readers/writers and transaction/compatibility treatment. Required Proof includes applying the migration to an isolated representative prior state, verifying resulting constraints and preserved data/references, and exercising affected application behavior.

Verify interruption, repeat/restart and concurrency behavior where the migration mechanism makes them relevant. Prove rollback or a documented forward-recovery strategy appropriate to the migration; do not require destructive down-migrations merely for symmetry.

Historical-data mutation needs a current preview and protected-reference checks. Production execution requires authorization for the target/treatment and appropriate backup/recovery preparation; local test success does not authorize production writes.

A migration that passes only against an empty new database cannot establish preservation of existing data. Missing required migration/compatibility proof means NOT GREEN.
