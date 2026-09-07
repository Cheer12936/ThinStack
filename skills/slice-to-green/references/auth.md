# Authentication, Permission and Security Boundaries

Changed authentication, authorization, RBAC, tenant isolation or another security boundary forces Verification FULL, regardless of patch size. Design can remain LIGHT when the existing rule is clear.

Required Proof must exercise applicable allow and deny paths at the enforcing boundary, including unauthenticated/expired or revoked credentials, insufficient privilege, ownership/tenant substitution and privilege escalation. Test server enforcement where the server owns the boundary; a hidden button does not prove denial.

Cover affected existing roles/sessions and downstream entrypoints. Add a browser/session journey when client/session wiring could change the result. Use the fewest checks that expose these risks, with explicit rationale for inapplicable cases.

Do not invent new access policy to fit implementation. Any unresolved high-risk finding or missing relevant denial evidence prevents GREEN. Keep secrets and personal records out of fixtures/logs.
