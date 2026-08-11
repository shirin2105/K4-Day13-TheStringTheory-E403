# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối:
- Thành viên và vai trò:

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (CP1; baseline: 30/100)
- Tổng số traces:
- Số PII leak còn lại: 0 theo `scripts/validate_logs.py`
- Link/đường dẫn dashboard:

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/cp1-redacted-log-excerpt.jsonl`
- Evidence PII redaction: `submission/evidence/cp1-redacted-log-excerpt.jsonl`
- Evidence trace waterfall:
- Giải thích một span đáng chú ý:

Khác biệt lớn nhất so với baseline CP0 là log CP1 đã có correlation ID xuyên suốt,
metadata phục vụ lọc (`user_id_hash`, `session_id`, `feature`, `model`, `env`) và PII
được che trước khi serialize xuống JSONL. `clear_contextvars()` bắt buộc ở đầu middleware
để context của request trước không bị tái sử dụng, tránh gán nhầm correlation/user/session và
gây rò rỉ dữ liệu giữa các request.

- Evidence validator CP1: `submission/evidence/cp1-validator-100.png`

## 4. Prompt versioning

- Prompt name:
- Version/label baseline:
- Version/label candidate:
- Trace ID của mỗi version:
- Bằng chứng đổi label hoặc rollback:

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`:
- Evidence dashboard:
- SLO đã chọn và lý do:
- Alert rules và runbook:

## 6. Điều tra challenge

- Challenge ID:
- Triệu chứng từ metrics:
- Trace ID liên quan:
- Log line/correlation ID liên quan:
- Root cause:
- Fix action:
- Preventive measure:

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| | | | |
