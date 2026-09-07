# Permission repair report

Mode: DELIVERY. Work type: SLICE. Design LIGHT; Verification FULL.
Profiles: AUTH/PERMISSION, tenant isolation. Explicit approved rule and one understood predicate justify LIGHT design; security boundary requires FULL verification.

## Green Contract (recorded before product change)
Goal: can_read grants access exactly when the actor belongs to the record tenant AND has role reader; anonymous actors are denied.
Acceptance: same tenant reader allowed; same tenant non-reader denied; other tenant reader denied; other tenant non-reader denied; anonymous denied.
Constraints: preserve the approved policy, function interface and existing tests. Change only this isolated permission directory. No HTTP/session integration exists here.
Required Proof: unchanged original tests plus direct real-function truth-table regressions, including tenant substitution and non-reader roles. Capture failing regressions before repair and the complete unittest result after repair. This is sufficient for the only implemented enforcement boundary: the pure function. There are no downstream entrypoints or credential/session lifecycle mechanisms supplied to exercise; expiry/revocation/browser checks are inapplicable, not claimed passed. Input schema validation is outside this predicate repair.

## Evidence
Pending implementation and execution. Logs and tested-file hashes will be recorded below.

## Final verdict: GREEN for the isolated can_read repair

Implemented: access.py changes only the predicate operator from OR to AND. Original test_access.py was not edited. Added test_access_regression.py.

Executed in this permission directory on Windows with Python 3.12; exact timestamp, Python version and final SHA256 identifiers for product/test files are in test-green.log. These hashes identify the tested snapshot without claiming a Git revision.

- Before repair: `python -B -m unittest discover -v` ran 4 test methods; 8 subcases failed because same-tenant non-readers or other-tenant readers were wrongly allowed. Exit 1. Evidence: test-red.log. This was a behavioral RED, not an environment error.
- After repair: the same command ran all 4 test methods successfully, exit 0. Evidence: test-green.log. The matrix exercises 16 actor-role-record combinations (2 record tenants x 2 actor tenants x 4 roles), plus 2 anonymous subcases and the 2 untouched original tests. Counts do not substitute for the asserted behaviors: the conjunction truth table, tenant substitution, exact reader role and anonymous denial are explicitly checked against the approved policy.

All required local proof passed; no skipped cases, known affected regression or unresolved high-risk finding remains in the scoped function repair. Existing framework is unittest; no additional repository gate was supplied for this isolated demo.

Limitations: direct function tests only. No HTTP API, credential validator, session/revocation layer, UI, database or real system integration was exercised or claimed passed. Arbitrary malformed mapping/schema validation and authenticating the actor are outside this repair; the function consumes the given actor mapping. The external task is assessed separately and is not operationally GREEN.

Remaining local repair work: none.

Read skill references: auth.md, verification.md, external-api.md, final-report.md, checkpoint-resume.md. Contract and evidence are combined here because the user specifically requested REPORT.md; no competing SPEC/RUN documents created.
