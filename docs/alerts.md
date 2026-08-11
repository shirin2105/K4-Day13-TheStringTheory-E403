# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert 1

- Tên: `high_latency_p95`
- Severity: warning
- SLI/SLO liên quan: P95 latency <= 3000 ms, target 99.5%.
- Điều kiện và thời gian duy trì: `latency_p95_ms > 3000` liên tục 5 phút.
- Ảnh hưởng tới người dùng: Phản hồi chat chậm, dễ timeout hoặc người dùng gửi lại request.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận thời điểm P50/P95/P99 bắt đầu tăng trên dashboard.
  2. Mở trace chậm, so sánh thời lượng span `retrieve` và `generate`.
  3. Dùng correlation ID tìm log, kiểm tra feature/model và incident đang bật.
- Mitigation tạm thời: Giảm concurrency, tắt `rag_slow`, dùng fallback và giới hạn output.
- Owner: `on-call-engineer`.

## Alert 2

- Tên: `elevated_error_rate`
- Severity: critical
- SLI/SLO liên quan: Error rate <= 2%, target 99.0%.
- Điều kiện và thời gian duy trì: `error_rate_pct > 5` liên tục 3 phút.
- Ảnh hưởng tới người dùng: Request thất bại hoặc nhận HTTP 500, luồng chat gián đoạn.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận error rate và breakdown theo `error_type`.
  2. Mở trace lỗi gần nhất để tìm span đầu tiên thất bại.
  3. Tra log `request_failed` theo correlation ID và kiểm tra dependency liên quan.
- Mitigation tạm thời: Tắt `tool_fail`, chuyển sang fallback an toàn và giảm tải dependency lỗi.
- Owner: `on-call-engineer`.

## Alert 3

- Tên: `cost_budget_exceeded`
- Severity: warning
- SLI/SLO liên quan: Daily cost <= USD 2.50, target 100%.
- Điều kiện và thời gian duy trì: `daily_cost_usd > 2.5` trong ngày hiện tại.
- Ảnh hưởng tới người dùng: Nguy cơ hết ngân sách, rate-limit hoặc phải dừng dịch vụ sớm.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận tổng cost và tốc độ tăng cost theo phút.
  2. Kiểm tra token input/output theo feature và model trong trace.
  3. Tìm request có `cost_usd` hoặc `tokens_out` cao nhất, đối chiếu `cost_spike`.
- Mitigation tạm thời: Tắt `cost_spike`, giới hạn output tokens hoặc chuyển model rẻ hơn.
- Owner: `team-lead`.
