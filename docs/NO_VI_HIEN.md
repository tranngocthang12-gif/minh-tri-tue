# SỔ NỢ VI HIẾN

Vi phạm Luật Kiến trúc Tối cao **đã biết nhưng chưa sửa**. Hệ thống **chưa đạt** các điều dưới đây; không được
tuyên bố khác đi. Nguồn: `docs/reviews/2026-09-30-ra-soat-kien-truc.md` (Ghế 1 tự rà), phản biện PR #3 của
Grok (`grok-review-pr3-2026-09-30`, Ghế 2 — nhà cung cấp khác), Issue #2.

| Mã | Điều | Mức | Vi phạm | Xác nhận | Trạng thái |
|---|---|---|---|---|---|
| V1 | 9 | BLOCKING | Cổng nâng kỹ năng dùng Brier tuyệt đối, không so tỷ lệ nền → dự đoán hiển nhiên vẫn qua cổng. | Grok PR #3: CÓ THẬT | MỞ |
| V2 | 6 | BLOCKING | `adjudicate` chỉ kiểm mã phiên khác nhau, không kiểm khác nhà cung cấp; danh tính phiên tự khai. | Grok PR #3: CÓ THẬT | MỞ |
| V3 | 7 | BLOCKING | Dự đoán và kết quả có thể vào cùng một commit → không chứng minh được "đoán trước". | Grok PR #3: CÓ THẬT | MỞ |
| V4 | 7 | MAJOR | Cấp bằng chứng của bài học do người viết tự khai, không suy từ sổ. | chưa có ghế khác | MỞ |
| V5 | 8 | MAJOR | `brain/providers.json` (điểm AI, champion) và `brain/state.json` sửa tay, không có lịch sử kiểm được. | chưa có ghế khác | MỞ |
| V6 | 8, 12 | MAJOR | Hai PR cùng ghi thêm vào một sổ chuỗi băm sẽ gãy chuỗi khi merge; chưa có công cụ xếp lại. | chưa có ghế khác | MỞ |
| V7 | 10, 14 | MAJOR | `inquiry`, `focus`, `domains` không nối với sổ; chưa có vòng khép kín mục đích → bài học. | chưa có ghế khác | MỞ |
| V8 | 7 | MINOR | Hạn chấm so theo ngày UTC, lệch giờ Việt Nam ở ranh giới ngày. | chưa có ghế khác | MỞ |
| V9 | 13 | MINOR | Nợ Issue #2: P1, P2, P3 (CLI `--skill`), ý 13. Docstring STALE của `lessons.py`: đã sửa trong PR #3. | Grok PR #3 | MỞ một phần |
| V10 | 4 | MINOR | Bảng §3 CONSTITUTION ghép chi phần → luật trong mã. Đã đổi lời; Grok: còn mức ánh xạ nhẹ. | Grok PR #3 | ĐÃ SỬA (theo dõi) |
| V11 | 12 | BLOCKING | `main` chưa bật bảo vệ nhánh → ghi thẳng `main` được; CI chỉ phát hiện sau. | Grok PR #3 | MỞ — đóng khi bảo vệ nhánh được bật **và xác minh** (`gh api …/branches/main/protection`) |
| V12 | 6, Ch. V | BLOCKING | Mọi AI thi công dùng tài khoản GitHub của Owner → CI không phân biệt Owner với AI; `OWNER-APPROVED` chỉ là tín hiệu. | Grok PR #3 | MỞ — cần Owner quyết: tạo tài khoản GitHub riêng cho AI |
| V13 | 14 | MINOR | Dòng `MỞ PHIÊN` trong chat không được CI kiểm (chỉ mô tả PR được kiểm). | Grok PR #3 | MỞ — chấp nhận, phụ thuộc Owner soi |
| V14 | 6, Ch. V.5 | MAJOR | CI chưa thực thi ba điều kiện merge của V.5: chưa kiểm người bấm merge (actor) ≠ tác giả PR, chưa kiểm có comment trích nguyên văn lệnh Owner (nguồn, ngày, đúng PR, đúng head) trước khi merge và phiên trong comment ≠ phiên thi công. Phụ thuộc V12: khi mọi AI dùng tài khoản Owner thì actor = author = Owner. Phép thử rẻ (Grok): test trong `tools/check_law.py` bắt "merge actor ≠ PR author" hoặc "comment trích lệnh chứa session khác" — chạy trên head hiện tại phải đỏ. | Grok PR #3 (`gh-action-36720593143`), Issue #2 | MỞ — chờ V12 |
| V15 | 14 | MINOR | `tools/check_handover.py` còn lỏng: chỉ dòng bàn giao mới cuối phải mang băm luật hiện hành; các dòng mới khác chỉ cần băm của một bản luật từng có ở commit gốc/commit của PR. Cần: dòng mới của phiên hiện tại bắt buộc băm hiện hành; dòng cũ chỉ mang băm của commit luật thật trong lịch sử, dòng seq n khớp bản luật ở commit đã thêm dòng đó. Phép thử rẻ (Ghế 1): sau khi luật đổi, thêm một dòng mới (không phải dòng cuối) mang băm cũ → CI phải đỏ. | Grok PR #3 (`gh-action-36720593143`), Issue #2 | MỞ |
