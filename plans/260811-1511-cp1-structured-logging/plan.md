---
title: "CP1 Structured Logging, Correlation ID and PII"
description: "Close only the remaining CP1 observability gaps, protect existing work, and produce validator-backed evidence."
status: completed
priority: P1
effort: 2h
branch: main
tags: [backend, observability, security]
blockedBy: []
blocks: []
created: 2026-08-11
---

# CP1 Structured Logging, Correlation ID and PII

## Overview

Current worktree already implements request context clearing/binding, response headers, log enrichment, recursive pre-serialization scrubbing, and successful-request metrics. Finish only missing CP1 contracts: passport/address patterns, trace correlation metadata, error rate, failure-path correlation, focused regression tests, then generate evidence.

## Phases

| Phase | Name | Status |
|---|---|---|
| 1 | [Complete CP1 contracts and tests](./phase-01-complete-cp1-contracts-and-tests.md) | Completed |
| 2 | [Validate runtime and capture evidence](./phase-02-validate-runtime-and-capture-evidence.md) | Completed |

## Dependency Graph

`Phase 1 (code + automated tests) -> Phase 2 (fresh runtime logs + evidence)`

## File Ownership

| Phase | Exclusive write ownership |
|---|---|
| 1 | `app/agent.py`, `app/main.py`, `app/metrics.py`, `app/pii.py`, `scripts/load_test.py`, `tests/test_agent_prompt_trace.py`, `tests/test_chat_observability.py`, `tests/test_metrics.py`, `tests/test_pii.py` |
| 2 | `data/logs.jsonl` runtime regeneration; new CP1 artifacts under `submission/evidence/`; CP1 answers in `submission/REPORT.md` |

Existing edits in `app/logging_config.py` and `app/middleware.py` are inputs to verify, not rewrite targets.

## Success Criteria

- `python scripts/validate_logs.py` reports at least `80/100`; `python -m pytest -q` fully passes.
- Success and HTTP 500 responses expose the same request correlation ID in logs/trace and response header.
- No raw tested email, phone, card, CCCD, passport, or Vietnamese address keyword remains in generated log strings.
- Metrics expose deterministic `error_rate_pct`, including zero-request and mixed success/error cases.
- CP1 evidence contains validator output and a log excerpt with `correlation_id` plus `[REDACTED_*]`, without secrets.

## Rollback

Revert Phase 2 artifacts first, then revert only Phase 1-owned files. Do not revert pre-existing worktree edits in middleware/logging configuration.

## Validation Log

- Tier: Light; claims checked: 10; verified: 10; failed: 0; unverified: 0.
- Runtime entry: middleware registration `app/main.py:21` -> dispatch `app/middleware.py:12` -> bind `app/middleware.py:23` -> chat `app/main.py:46` -> agent `app/main.py:63`.
- Contract consumers enumerated: `snapshot()` one caller at `app/main.py:42`; `LabAgent.run()` production caller `app/main.py:63` and direct wrapped test `tests/test_agent_prompt_trace.py:42`.
- 2026-08-11 final validation: Python 3.12 venv available; `pytest` 24 passed; `validate_logs.py` 100/100; 0 PII leaks; 10 unique correlation IDs; evidence and report updated.

## Delivery Status

- Progress: 7/7 phase todo items complete (100%); 6/6 success criteria verified.
- Blocker: none. Python runtime blocker resolved by Python 3.12 venv.
- Scope change: none.
- Risk update: validation and evidence risks closed by 24 passing tests, validator 100/100, 0 PII leaks, and reviewed artifacts.
- Next action: CP1 complete; continue next committed checkpoint under its own plan and acceptance gates.

## Unresolved Questions

None.
