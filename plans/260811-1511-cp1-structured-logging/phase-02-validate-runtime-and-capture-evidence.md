---
phase: 2
title: "Validate runtime and capture evidence"
status: completed
priority: P1
effort: "0.5h"
dependencies: [1]
---

# Phase 2: Validate runtime and capture evidence

## Context Links

- Acceptance: `CHECKPOINTS.md:12`, `CHECKPOINTS.md:15`
- Evidence contract: `SUBMISSION.md:9`, `SUBMISSION.md:15`
- Validator behavior: `scripts/validate_logs.py:40`, `scripts/validate_logs.py:80`

## Overview

Regenerate clean logs, run required gates, inspect PII manually, and capture redacted CP1 evidence.

## Requirements and Data Flow

Sample queries -> running API -> clean `data/logs.jsonl` -> validator parses records and scores schema/correlation/enrichment/PII -> sanitized screenshots/excerpts enter `submission/evidence/` -> results summarized in `submission/REPORT.md`.

## Related Code Files

- Regenerate runtime `data/logs.jsonl` only after preserving any user-needed copy outside Git.
- Create timestamped CP1 validator/log evidence under `submission/evidence/`.
- Modify only CP1 sections of `submission/REPORT.md`.

## Implementation Steps

1. Confirm no needed user evidence resides in current log; remove only `data/logs.jsonl`, then restart app.
2. Run `python scripts/load_test.py`, `python scripts/validate_logs.py`, and `python -m pytest -q`.
3. Search generated log for raw `@`, test-card digits, sample phone/CCCD/passport/address values; separately confirm `REDACTED` markers exist.
4. Capture validator result and one minimal log excerpt showing correlation + redaction. Review every artifact for keys, secrets, raw PII, unrelated terminal history.
5. Answer CP1 reflection: baseline vs final differences; `clear_contextvars()` prevents request-context reuse/leakage.

## Test Matrix

| Gate | Pass condition |
|---|---|
| Log validator | score >= 80/100; no detected raw PII |
| Pytest | all tests pass |
| Manual negative search | no raw sample values |
| Manual positive search | correlation IDs and `[REDACTED_*]` present |
| Evidence review | no `.env`, key, secret, or unredacted payload |

## Failure Modes and Risk Assessment

| Risk | L x I | Mitigation |
|---|---|---|
| Old logs create false validator failure | H x M = High | Use a fresh log after explicit target verification. |
| Evidence screenshot leaks secret/PII | M x H = High | Crop to necessary lines; inspect before saving/committing. |
| Runtime unavailable or stale process | M x M = Medium | Verify `/health`, restart Uvicorn, rerun load test. |
| Validator passes but required evidence absent | M x M = Medium | Check both `CHECKPOINTS.md` and `SUBMISSION.md` evidence list. |

## Backwards Compatibility

No application contract change. Do not edit `config/challenge.json`; CP1 practice remains independent of challenge release.

## Rollback

Evidence artifacts are additive and removable. Restore a preserved user log only if explicitly needed; never overwrite undisclosed evidence.

## Todo List

- [x] Regenerate clean runtime logs.
- [x] Pass validator and full tests.
- [x] Review and save evidence.
- [x] Complete CP1 report answers.

## Success Criteria

- [x] Validator >= 80/100 and pytest fully green.
- [x] Evidence satisfies both CP1 requirements and privacy rules.
- [x] Report cites concrete validator result and log evidence filename.

## Security Considerations

Do not commit `.env`, Langfuse keys, raw logs containing PII, or screenshots exposing terminal secrets.

## Next Steps

Completed. Validator 100/100; pytest 24 passed; 0 PII leaks; 10 unique correlation IDs; report cites CP1 validator and redacted log evidence.

## Blocker

None. Prior Phase 1 runtime dependency resolved.

## Unresolved Questions

None.
