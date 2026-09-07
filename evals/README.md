# Alpha evaluation evidence

Date: 2026-09-08. Environment: Windows, PowerShell, Python 3.12.5; browser demo used cached Playwright CLI and installed Chrome. Independent agents were explicitly assigned narrow isolated tasks; these evaluations do not make delegation a requirement of the distributed skill.

## Actual execution

| Task | Selected design / verification | Evidence and result |
|---|---|---|
| Notes.create with SQLite persistence | LIGHT / STANDARD | 4 unittest methods pass; input preservation, invalid-input nonmutation, committed cross-instance read and order. [Report](../examples/business/REPORT.md) |
| Permission predicate repair | LIGHT / FULL | 4 unittest methods pass including a 16-combination permission matrix; [report](../examples/permission/REPORT.md) |
| Button horizontal padding | LIGHT / LIGHT | Desktop/mobile browser style and overflow checks, click behavior, rendered screenshots. [Report](../examples/ui/REPORT.md) |
| Missing supplier credentials/schema | STANDARD / STANDARD review | No supplier tests executed; correctly reports real integration NOT GREEN. [Assessment](../examples/permission/EXTERNAL_ASSESSMENT.md) |

The permission demo has only a pure-function boundary. FULL verification covers that demo's risks; this does not establish real HTTP/session authorization safety. The business demo has SQLite, not PostgreSQL or an ERP. The UI is a synthetic static page. Missing external conditions were assessed on provided files, not live integration.

The main agent independently reran both Python example suites successfully. Package management has five separate executable tests, covering update/uninstall preservation and refusal of unintended overwrite. See [release validation](RELEASE_VALIDATION.md).

## Reproduce

From each relevant example directory:
- business: python -B -m unittest discover -v
- permission: python -B -m unittest discover -v
- ui: serve index.html on localhost and inspect its page in a browser; recorded operations and screenshots are included. No browser package is installed by this repository.
- external: static incomplete fixture; no endpoint or credentials are supplied, and no live PASS is claimed.

These are completed demonstration artifacts, not an automated independent benchmark. Historical red logs are sanitized snapshots; final tests against completed code should pass. Personal absolute paths in published reports/logs are replaced; no temporary databases or real business records are included. Some earlier decision-only scenarios resembled skill examples and are not counted here as executable tests.

## Limits and next work

No claims of cross-model accuracy, fixed success rate, production safety, CI execution, or Linux/macOS host compatibility. Initial project bootstrapping has documented guidance but was not independently exercised end-to-end in this alpha evaluation. The GitHub matrix is supplied for future runs, not reported as already passed.

Historical business RED logs contain localized Windows error text with unreadable glyphs from the original console capture; error types and final fresh PASS logs remain available. Sanitized logs are supporting evidence, not exact raw-byte originals.
