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
lessons.py ── SỔ BÀI HỌC & KỸ NĂNG (chuỗi băm): bài học trỏ về dự đoán đã chấm, cùng miền;
   │            kỹ năng chỉ dùng dự đoán của chính bài học; trọng tài ba ghế gọi TRONG hàm;
   │            bản mới rớt không kéo đổ bản active; NÂNG chỉ chấm dự đoán gốc (không chọn lọc);
   │            GIÁM SÁT thêm dự đoán gắn tên SAU lần nâng + quá hạn chưa chấm → SUSPENDED;
   │            cửa sổ trượt không có kết quả gắn tên → STALE; chấm trễ = trượt;
   │            rollback phải qua cổng + ba ghế lại. KỸ NĂNG ≠ CẤP HỌC.
   │
   ▼
focus.py ── nút thắt đòn bẩy cao nhất (≤3) hoặc CHỜ; nghiên cứu thêm hay THỬ
   │
   ▼
providers.py ── benchmark AI theo việc; champion/challenger có biên an toàn
   │
bench.py ── đề công khai, ĐÁP ÁN NIÊM PHONG ngoài repo (chỉ lưu băm);
            cấm tác giả + bí danh + người đã đọc đề (exposed_to) + phiên soạn đề;
            mỗi (provider, đề, việc) ghi một lần; champion cần ≥5 đề khác nhau

tools/check_append_only.py ── CI so sổ với commit gốc: dòng cũ phải còn nguyên
   │
   └──────────── ↺ (L7 học cách học, L8 tự sửa — CHƯA có, lộ trình v0.3)
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
- **v0.2 (hiện tại):** sổ bài học & kỹ năng có phiên bản, đình chỉ, rollback; benchmark niêm phong `tang1-core-v1` (đề THỬ, chưa đủ bầu champion). Sửa theo phản biện Grok PR #1.
- **v0.3:** lệnh CLI ghi bài học/kỹ năng (bắt 3 mã phiên); đề benchmark do AI khác soạn.
- **v0.4:** L7 meta-learning (đo phương pháp học nào cho dự đoán tốt hơn); L8 self-repair qua PR sandbox + rollback.
- **v0.4:** Owner giao miền đầu tiên → chạy vòng thật đầu tiên.
