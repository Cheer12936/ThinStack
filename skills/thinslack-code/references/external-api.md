# External API

Every changed external API boundary needs timeout, invalid-response and network-failure verification. Add retry bounds, rate-limit handling and idempotency when relevant; if omitted, explain why the operation cannot incur those risks. Payment inherits Verification FULL from the money override.

Verify source mapping, units/nullability, pagination or auth refresh where changed, and affected downstream consumers. Do not use hand-built fixtures as evidence of the provider's real schema.

Keep three evidence levels distinct:
- Synthetic contract: constructed input and controlled failures.
- Sanitized real-response replay: actual source/version mapping without a live call.
- Live integration: tested environment and request at a recorded time.

The Green Contract must identify which levels prove the requested outcome. Missing credentials or samples are not permission to silently replace required live/replay evidence with mocks. Report NOT GREEN for the missing required boundary, with the access/sample needed.

Keep routine tests isolated from paid/live services unless authorized. Store provenance without credentials/personal data. Do not promise general provider readiness from one successful request.
