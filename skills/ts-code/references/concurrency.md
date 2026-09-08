# Concurrency

A changed concurrent behavior requires concurrency-specific proof, even if serial tests pass.

Identify the invariant and contention point. Exercise overlapping operations through an appropriate real boundary using a barrier, coordinated transactions or another reproducible interleaving; assert final persisted state, per-request outcomes and relevant side-effect counts.

Relevant cases include competing inventory writes, duplicate callbacks/jobs, lost updates, source-record imports and cancellation versus completion. Choose the interleavings that threaten the specified behavior.

Sequential duplicate calls alone are not proof of race safety. Timing-only sleeps without evidence of overlap are weak evidence. If the race cannot be exercised credibly, report the verification gap rather than GREEN.
