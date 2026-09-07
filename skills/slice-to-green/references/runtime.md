# Runtime Profiles

Load only the applicable sections. These prompts select proof, not a fixed workflow.

- BACKGROUND_JOB: observable completion/failure, bounded retry and duplicate execution; stale/out-of-order results must not overwrite newer truth. If concurrency matters, load concurrency guidance.
- FILE_UPLOAD: accepted/rejected file boundaries, interrupted transfer and processing failure; verify ownership and safe interpretation when they are affected, loading auth guidance for changed security boundaries.
- CACHE: invalidation after changed writes, scope/key isolation, expiry and stale result behavior. Security-boundary changes inherit Verification FULL.
- SEARCH: empty-query baseline, normalization/matching, permissions, ordering/pagination and realistic relevant data distribution. Verify limits are applied consistently with filtering and stale responses cannot replace current results when applicable.

Use checks that assert the underlying business result. A successful job enqueue, upload response, cache hit or search HTTP status alone may not prove the requested outcome.
