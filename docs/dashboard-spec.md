# Yêu cầu dashboard

Contract có thể kiểm tra bằng máy nằm tại `config/dashboard.yaml`. Hướng dẫn dựng và kiểm tra runtime nằm tại [DASHBOARD_SETUP.md](DASHBOARD_SETUP.md).

Dashboard chính cần đủ 6 nhóm thông tin:

1. Latency P50/P95/P99.
2. Traffic: request count hoặc QPS.
3. Error rate và breakdown theo loại lỗi.
4. Cost theo thời gian.
5. Tổng token input/output.
6. Quality proxy.

## Đặc tả panel

| Panel | Nguồn và phép tổng hợp | Đơn vị | Khoảng mặc định | Threshold / SLO |
|---|---|---|---|---|
| Latency percentiles | `response_sent.latency_ms`; P50, P95, P99 | ms | 60 phút | P95 <= 3000 ms |
| Request traffic | Đếm `request_received`, tính rate mỗi phút | requests/phút | 60 phút | >= 1 request/phút |
| Error rate and breakdown | `request_failed / request_received * 100`, nhóm theo `error_type` | % | 60 phút | <= 2% |
| Cost over time | Tổng `response_sent.cost_usd` theo phút và toàn cửa sổ | USD | 60 phút | <= USD 2.50 |
| Input/output tokens | Tổng riêng `tokens_in` và `tokens_out` | tokens | 60 phút | <= 50.000 tokens |
| Quality proxy | Trung bình `response_sent.quality_score` | score 0–1 | 60 phút | >= 0.75 |

Nguồn dữ liệu chuẩn là `data/logs.jsonl`. Dashboard evidence local được tạo bằng
`python scripts/render_dashboard.py`; cấu hình có thể chuyển sang Grafana/Langfuse
nhưng phải giữ nguyên logic trong `config/dashboard.yaml`. Dashboard hiển thị cửa sổ
60 phút, mốc SLO của từng panel và thời điểm tạo dữ liệu.

Tiêu chuẩn trình bày:

- Khoảng thời gian mặc định: 1 giờ.
- Tự refresh mỗi 15–30 giây nếu công cụ hỗ trợ.
- Có threshold hoặc SLO line.
- Ghi rõ đơn vị.
- Chỉ giữ 6–8 panel quan trọng ở lớp chính.
- Screenshot phải nhìn được tên panel và khoảng thời gian.

Kiểm tra contract trước khi chụp evidence:

```bash
python scripts/validate_dashboard.py
```
