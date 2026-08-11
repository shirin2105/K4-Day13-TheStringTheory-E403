# Báo cáo Day 13 Observability

## 1. Thông tin nhóm

- Tên nhóm:
- Repository URL:
- Commit SHA cuối: 0c0e31f
- Thành viên và vai trò:
  - Trần Đăng Bách: Triển khai Checkpoint 1 (Logging, Correlation ID & PII).
  - Nguyễn Trọng Đức: Triển khai Checkpoint 2 (Metrics, Traces, Dashboard & Alerts).
  - Nguyễn Phi Hoàng: Triển khai Checkpoint 3 (Challenge: Điều tra Incident).

## 2. Kết quả kỹ thuật

- Điểm `validate_logs.py`: 100/100 (CP1; baseline: 30/100)
- Tổng số traces: 26 (xác minh qua Langfuse API; có >= 10 trace `run` với metadata)
- Số PII leak còn lại: 0 theo `scripts/validate_logs.py`
- Link/đường dẫn dashboard: `submission/evidence/cp2-dashboard.html`

## 3. Logging và tracing

- Evidence correlation ID: `submission/evidence/cp1-redacted-log-excerpt.jsonl`
- Evidence PII redaction: `submission/evidence/cp1-redacted-log-excerpt.jsonl`
- Evidence trace list và waterfall: `submission/evidence/cp2-trace-list.png`, `submission/evidence/cp2-trace-waterfall.png`; metadata đối chiếu tại `submission/evidence/cp2-trace-summary.json`
- Giải thích một span đáng chú ý: generation span `run` liên kết model, usage/cost và prompt version với trace; đây là điểm vào để đối chiếu cùng correlation ID trong log.

Khác biệt lớn nhất so với baseline CP0 là log CP1 đã có correlation ID xuyên suốt,
metadata phục vụ lọc (`user_id_hash`, `session_id`, `feature`, `model`, `env`) và PII
được che trước khi serialize xuống JSONL. `clear_contextvars()` bắt buộc ở đầu middleware
để context của request trước không bị tái sử dụng, tránh gán nhầm correlation/user/session và
gây rò rỉ dữ liệu giữa các request.

- Evidence validator CP1: `submission/evidence/cp1-validator-100.png`

## 4. Prompt versioning

- Prompt name: `day13-chat`
- Version/label baseline: version 1 / `baseline`, `production`
- Version/label candidate: version 2 / `candidate`
- Trace ID của mỗi version: baseline v1 `406eee5d6eb823aefefc7b2b946f115a`; candidate v2 `f689ee2cf1644796a00b6cb5af9d9556`
- Bằng chứng đổi label hoặc rollback: `submission/evidence/cp2-production-v2.png`, `submission/evidence/cp2-production-rollback-v1.png`; production v2 trace `420fa18518164144a510beaaccfc3cee`, sau rollback v1 trace `a2f29398f7c54ac493becf480975198b`

## 5. Dashboard, SLO và alerts

- Kết quả `validate_dashboard.py`: HỢP LỆ — 6/6 panel
- Evidence dashboard: `submission/evidence/cp2-dashboard.png` và `submission/evidence/cp2-dashboard.html`
- SLO đã chọn và lý do: P95 <= 3000 ms; error rate <= 2%; daily cost <= USD 2.50; quality >= 0.75. Các ngưỡng phản ánh trực tiếp tốc độ, độ tin cậy, ngân sách và chất lượng người dùng nhận được.
- Alert rules và runbook: `config/alert_rules.yaml`, `docs/alerts.md`; cả ba alert đều symptom-based để cảnh báo theo ảnh hưởng người dùng thay vì phụ thuộc tên hàm nội bộ dễ thay đổi.

## 6. Điều tra challenge

- Challenge ID: `day13-k4-observability-v1`
- Triệu chứng từ metrics: Latency p95 tăng vọt lên ~3.6s (3633ms), vượt quá ngưỡng 2s. Client latency lên tới ~18.3s với tải 5 request đồng thời.
- Trace ID liên quan: `req-7dd39beb`
- Log line/correlation ID liên quan: correlation_id `req-7dd39beb`, ghi nhận sự kiện `response_sent` với `latency_ms` = 3526.
- Root cause: Bị ảnh hưởng bởi sự cố `rag_slow` làm hàm `retrieve()` bị chậm thêm 2.5s do `time.sleep()`. Nguyên nhân sâu xa là việc gọi trực tiếp hàm đồng bộ (synchronous) `agent.run` bên trong route `async def chat` của FastAPI làm block toàn bộ event loop, khiến cho các request đồng thời phải xếp hàng chờ đợi nhau.
- Fix action: Thay đổi endpoint `chat` thành hàm `def` đồng bộ, hoặc bọc `agent.run` bằng `run_in_threadpool` để không block event loop. Xử lý triệt để hiệu năng của phần `retrieve()` (ví dụ: bổ sung cache, timeout).
- Preventive measure: Đặt alert khi latency P95 > 2s. Thêm sub-component tracing trực tiếp vào các hàm `retrieve()` thay vì chỉ ở mức agent để dễ dàng phát hiện điểm thắt cổ chai trong tương lai.

## 7. Đóng góp cá nhân

Với mỗi thành viên, ghi rõ nhiệm vụ và link commit/PR tương ứng.

| Thành viên | Phần việc | Commit/PR | Điều đã học |
|---|---|---|---|
| Trần Đăng Bách | CP1: Logging, Correlation ID & PII | `15cec6e` | Hiểu cách luân chuyển context qua request và che PII an toàn trước khi log. |
| Nguyễn Trọng Đức | CP2: Metrics, Traces, Dashboard & Alerts | `e6a9ba6` | Biết cách kết hợp Grafana Dashboard, thiết lập SLOs và tracing prompt trên Langfuse. |
| Nguyễn Phi Hoàng | CP3: Challenge Investigation | `0c0e31f` | Nắm rõ quy trình dùng Metrics để phát hiện, Traces để khoanh vùng và Logs để tìm Root Cause. |
