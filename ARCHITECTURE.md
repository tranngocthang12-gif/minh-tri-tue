# KIẾN TRÚC TẦNG 1 — v0.2

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
lessons.py ── SỔ BÀI HỌC & KỸ NĂNG (chuỗi băm): bài học phải trỏ về dự đoán đã chấm;
   │            kỹ năng có phiên bản; PROMOTED → recheck → SUSPENDED; rollback về bản đã từng đạt
   │
   ▼
focus.py ── nút thắt đòn bẩy cao nhất (≤3) hoặc CHỜ; nghiên cứu thêm hay THỬ
   │
   ▼
providers.py ── benchmark AI theo việc; champion/challenger có biên an toàn
   │
bench.py ── đề công khai, ĐÁP ÁN NIÊM PHONG ngoài repo (chỉ lưu băm);
            tác giả đề không được thi đề của mình; chấm tự động
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
| `lessons/book.jsonl` | sổ bài học & kỹ năng, chuỗi băm |
| `../benchmarks/*.json` | đề thi AI (không chứa đáp án) |

Dữ liệu thô lớn (video, audio, hàng triệu event) **không** vào GitHub — chỉ giữ tóm tắt, checksum, đường dẫn.

## Lộ trình
- **v0.1:** luật lõi chạy offline + kiểm thử + cửa đóng góp 4 AI.
- **v0.2 (hiện tại):** sổ bài học & kỹ năng có phiên bản, đình chỉ, rollback; benchmark niêm phong `tang1-core-v1`.
- **v0.3:** L7 meta-learning (đo phương pháp học nào cho dự đoán tốt hơn); L8 self-repair qua PR sandbox + rollback.
- **v0.4:** Owner giao miền đầu tiên → chạy vòng thật đầu tiên.
