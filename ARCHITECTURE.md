# KIẾN TRÚC TẦNG 1 — v0.1

```
OWNER PURPOSE
   │
   ▼
inquiry.py ── THỰC TRẠNG → ĐIỀU KIỆN → ĐÍCH → CON ĐƯỜNG   (khóa thứ tự)
   │
   ▼
domains.py ── mở MIỀN (Tầng 2): 9 câu hỏi bắt buộc, khởi đầu UNKNOWN
   │
   ▼
epistemics.py ── mọi phát biểu có loại + độ tin ≤ trần bằng chứng
   │
   ▼
seats.py ── ĐỀ XUẤT ▸ PHẢN BIỆN ▸ TRỌNG TÀI (3 phiên độc lập)
   │
   ▼
ledger.py ── DỰ ĐOÁN đăng ký trước → Owner làm → KẾT QUẢ thật → chấm (Brier / trúng khoảng)
   │            chuỗi băm SHA-256, chỉ ghi thêm, sửa lén bị phát hiện
   ▼
gates.py ── cổng nâng BÀI HỌC → KỸ NĂNG; xếp cấp L0–L9 theo bằng chứng
   │
   ▼
focus.py ── nút thắt đòn bẩy cao nhất (≤3) hoặc CHỜ; nghiên cứu thêm hay THỬ
   │
   ▼
providers.py ── benchmark AI theo việc; champion/challenger có biên an toàn
   │
   └──────────── ↺ (L7 học cách học, L8 tự sửa — lộ trình v0.2+)
```

## Bộ não chuẩn (`brain/`)
| Tệp | Nội dung |
|---|---|
| `state.json` | biết gì, chưa biết gì, điểm mù, nút thắt kế tiếp |
| `providers.json` | danh sách AI, điểm benchmark, champion theo việc |
| `ledger/predictions.jsonl` | sổ dự đoán + kết quả, chuỗi băm |
| `domains/<miền>/domain.json` | tri thức Tầng 2 của từng miền |

Dữ liệu thô lớn (video, audio, hàng triệu event) **không** vào GitHub — chỉ giữ tóm tắt, checksum, đường dẫn.

## Lộ trình
- **v0.1 (hiện tại):** luật lõi chạy offline + kiểm thử + cửa đóng góp 4 AI.
- **v0.2:** sổ bài học & kỹ năng (lesson → skill) có phiên bản; bộ benchmark đầu tiên cho 4 AI.
- **v0.3:** L7 meta-learning (đo phương pháp học nào cho dự đoán tốt hơn); L8 self-repair qua PR sandbox + rollback.
- **v0.4:** Owner giao miền đầu tiên → chạy vòng thật đầu tiên.
