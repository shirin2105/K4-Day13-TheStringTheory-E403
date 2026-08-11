---
phase: 1
title: "Complete CP1 contracts and tests"
status: completed
priority: P1
effort: "1.5h"
dependencies: []
---

# Phase 1: Complete CP1 contracts and tests

## Context Links

- Requirements: `CHECKPOINTS.md:10`, attachment CP1 steps 1-6
- Schema: `config/logging_schema.json:4`
- Runtime flow: `app/main.py:21`, `app/middleware.py:12`, `app/main.py:46`, `app/agent.py:30`

## Overview

Complete remaining contracts without replacing already-valid middleware, enrichment, and recursive scrubbing work.

## Requirements and Data Flow

1. HTTP input (`x-request-id`, chat body) -> middleware clears context, validates/creates ID, binds request context -> chat binds hashed/enrichment fields -> processors redact strings -> JSONL log + response headers.
2. Chat metadata -> `LabAgent.run()` -> Langfuse trace metadata gains the active `correlation_id`; prompt fields remain intact.
3. Successful requests increment `TRAFFIC`; failures increment `ERRORS`; `/metrics` returns `errors / (successes + errors) * 100` as `error_rate_pct`.
4. Any application exception -> HTTP 500 response retains `x-request-id`; load-test output reads header first and safely handles non-JSON bodies.

## Related Code Files

- Modify `app/pii.py:6`: add passport and Vietnamese address patterns.
- Modify `app/agent.py:46`: merge `correlation_id` into existing trace metadata.
- Modify `app/metrics.py:40`: calculate and return `error_rate_pct`.
- Modify `app/main.py:88`: ensure error response preserves correlation header (prefer existing HTTPException handler or a narrow generic handler; avoid double-counting).
- Modify `scripts/load_test.py:21`: header-first correlation extraction and safe error display.
- Modify tests at `tests/test_pii.py:4`, `tests/test_agent_prompt_trace.py:33`, `tests/test_metrics.py:4`, `tests/test_chat_observability.py:12`.
- No delete/create production files.

## Implementation Steps

1. Add tests first: passport/address redaction; recursive metadata redaction; trace correlation preservation alongside prompt metadata; metric zero/mixed cases; supplied/generated ID propagation; exception response header; cross-request isolation.
2. Add PII patterns with Unicode/case-insensitive behavior deliberately tested. Avoid overbroad replacement of ordinary Vietnamese prose; use value-oriented address matching rather than deleting every occurrence of words such as `thành phố`.
3. Read active structlog context in `LabAgent.run()` and add only `correlation_id` to the existing metadata dict.
4. Compute error rate from current process-global counters. Keep output percentage rounded to two decimals; do not change existing `traffic` semantics.
5. Preserve correlation ID on failures. Verify whether FastAPI's HTTPException path bypasses post-`call_next` headers; implement one response-construction point and keep the sanitized exception type body.
6. Make load-test diagnostics header-first, tolerate invalid JSON, and never print request payload contents.
7. Run focused tests, then full suite.

## Test Matrix

| Layer | Scenarios | Expected |
|---|---|---|
| Unit | email, phone variants, CCCD, card, passport, Vietnamese address; nested dict/list | raw PII absent; stable `[REDACTED_*]` marker |
| Unit | no requests; 2 successes/1 error; errors only | `0.0`, `33.33`, `100.0` |
| Unit | trace with bound and absent context | ID propagated; `MISSING` fallback explicit; prompt metadata unchanged |
| Integration | client-supplied and generated IDs | response/log ID match; generated format `req-[0-9a-f]{8}` |
| Integration | sequential/concurrent requests | no context leakage between IDs/users/sessions |
| Integration | agent failure | status 500, header present, one error recorded, scrubbed failure log |
| Regression | `python -m pytest -q` | all tests pass |

## Failure Modes and Risk Assessment

| Risk | L x I | Mitigation |
|---|---|---|
| Error response loses ID because middleware never receives a response | M x H = High | Integration-test forced agent failure; construct correlated error response at verified exception boundary. |
| Shared module counters contaminate tests | H x M = High | Snapshot/restore or monkeypatch every global collection/counter per test; never depend on test order. |
| Address regex over-redacts benign text | M x H = High | Require nearby address content; add positive and negative Vietnamese cases. |
| Context leaks across reused async tasks | L x H = High | Keep `clear_contextvars()` at request entry and add sequential/concurrent isolation tests. |
| Trace change overwrites prompt metadata | M x M = Medium | Extend existing metadata dict and retain exact assertions for four prompt fields. |

## Backwards Compatibility

- Keep request/response JSON schemas, accepted `x-request-id`, log event names, current trace prompt metadata, and `traffic` meaning unchanged.
- `error_rate_pct` is additive. Existing `/metrics` consumers remain valid.
- No persistent-data migration. Fresh log regeneration is operational evidence, not schema migration.

## Rollback

Revert only phase-owned files. Additive metric/metadata fields can be removed independently; no stored-state conversion required. Existing middleware/logging edits remain untouched.

## Todo List

- [x] Write focused tests for implemented behavior.
- [x] Implement four remaining contracts.
- [x] Run focused tests and full suite.

## Success Criteria

- [x] All matrix assertions pass.
- [x] No regression in prompt metadata or successful response body.
- [x] Every High risk has an automated test.

## Security Considerations

Hash user IDs before logging/tracing; redact before `JsonlFileProcessor`; never emit raw exception messages or request payloads.

## Next Steps

Completed. Python 3.12 venv available; full suite: 24 passed. Phase 2 validation gate cleared.

## Blocker

None. Prior Python runtime blocker resolved.

## Unresolved Questions

None.
