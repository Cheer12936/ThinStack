# External supplier assessment

Mode: VERIFY_ONLY, read-only assessment. Work type: SLICE. Design STANDARD / Verification STANDARD for this assessment; EXTERNAL_API is the directly observed profile. The actual supplier outcome additionally requires persistence and UI consumer proof, neither of which exists in the two supplied files. No product scope was narrowed to mocks.

Reviewed only ../external/REQUEST.md and ../external/provider.py. No network request, execution/import of provider.py, credential discovery or external file mutation was performed. No executable supplier tests were run.

## Requested outcome and proof boundary

Required outcome: actual provider data imported and displayed correctly. To prove delivery, the source response must map correctly into the real import/persistence path and the displayed consumer. Source units, nullability and applicable versions must be established from official schema and authentic samples; persisted behavior needs storage/readback evidence, and presentation needs an inspectable render plus observation. Real provider connectivity requires corresponding live request evidence when claiming actual operation.

## What is observable now

Static code inspection shows parse_response directly indexes payload['value'] and payload['unit'] and returns those fields. It does not establish their meaning, validate types or units, persist data or render anything. A missing required key would raise KeyError under normal Python dict semantics; this is code reasoning, not an executed test result.

Synthetic parser tests could be authored using constructed dictionaries to check pass-through and controlled malformed inputs. Such tests would demonstrate only this local parser behavior. No synthetic test PASS is claimed in this review.

## Missing evidence

- Synthetic contract: parser exists; no executed checks in this review. Hand-built inputs cannot establish the supplier schema.
- Sanitized real-response replay: unavailable; no authentic sample or official schema supplied. Mapping, field meaning, units and version compatibility remain unproven.
- Live integration: unavailable; no credentials or established endpoint/transport supplied. No requests were made.
- Import/storage/display: absent from the reviewed files. No consumer path, refresh/readback or visual evidence available.
- Provider boundary failure handling: timeout, invalid response and network failure remain unverified. Retry, limits, authentication refresh, pagination and idempotency need applicability decisions once the real operation is known. The pure parser has no transport to test; this does not waive those checks for the requested actual import.

## Conclusion

Review completed; actual integration delivery is NOT GREEN. Static parser inspection is the only current evidence level, and it does not prove operational readiness. Conditions for continuing: authorized provider connection details/access, official contract or sanitized authentic response with provenance, and the actual importer/persistence/UI implementation or test environment. Continue safe isolated parser/contract work when authorized, without inventing endpoints or credentials. Missing operational proof cannot be replaced by a mock-only success claim.
