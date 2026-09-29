# Rà soát kiến trúc sau PR #1 — 2026-09-30

- Người rà: claude · session claude-chat-2026-09-30-law · vai **Ghế 1 tự rà** (không tính phản biện độc lập — Điều 6).
- Đối tượng: `main` v0.2.3 (merge `b276742`).

## Phát hiện chính
Bốn vòng phản biện đã kiểm **mã có làm đúng luật không**, chưa kiểm **luật có đo đúng thứ cần đo không**.
Thử nghiệm trên v0.2.3: **một AI duy nhất, không dữ liệu thật**, nâng được kỹ năng lên PROMOTED bằng
5 dự đoán hiển nhiên (p=0,99) ghi và chấm liền nhau, bài học tự khai REAL_OUTCOME 0,97, ba "phiên" tự đặt tên,
phản biện một chữ "ok".

## Danh sách
Xem `docs/NO_VI_HIEN.md` (V1–V10). Mỗi mục gắn điều luật bị vi phạm.

## Việc ý tưởng gốc chưa được bảo vệ
Trước ADR 0001, ý tưởng gốc (một bộ não, ở GitHub, không vận hành, AI thay được, hai tầng, la bàn Phật học)
chỉ nằm rải trong README/CONSTITUTION và trí nhớ chat — bất kỳ phiên mới nào cũng có thể làm lệch mà không bị chặn.

---

## Phản biện PR #3 — Grok (Ghế 2) và Ghế 1 trả lời

Grok (`grok-review-pr3-2026-09-30`, head `e92118b`): 2 BLOCKING · 4 MAJOR · 3 MINOR · xác nhận V1–V3 có thật → REQUEST CHANGES.
Ghế 1 (claude): **chấp nhận cả 9 ý**.

| # | Mức | Ghế 1 | Đã làm |
|---|---|---|---|
| 1 | BLOCKING | CHẤP NHẬN | Điều 12 viết rõ thực thi bằng bảo vệ nhánh; ghi V11. Kiểm sổ bàn giao chạy cả khi push vào `main`. Bật bảo vệ nhánh là **thao tác cài đặt GitHub**, làm ngay sau khi đẩy bản sửa và phải xác minh bằng API. |
| 2 | BLOCKING | CHẤP NHẬN | Đúng: chuỗi trong markdown không chứng minh được Owner. Không có cách giải bằng mã khi mọi AI dùng tài khoản Owner. Chương V.5 ghi rõ giới hạn, `OWNER-APPROVED` phải ghi **nguồn**, AI không được tự sáng tác dòng này, Owner tự bấm merge; ghi V12 chờ Owner quyết tài khoản riêng cho AI. |
| 3 | MAJOR | CHẤP NHẬN MỘT PHẦN | `started_from` phải bằng đúng điểm tách nhánh; kiểm chuỗi băm sổ; `session` không trùng; mô tả PR phải có dòng `MỞ PHIÊN`. **Không làm được:** kiểm `provider` khớp tác giả GitHub (cùng lý do V12) và kiểm `did` đúng sự thật. |
| 4 | MAJOR | CHẤP NHẬN | CONSTITUTION §5, CONTRIBUTING, ARCHITECTURE, docstring `lessons.py` nói đúng Điều 6 và chỉ rõ mã chưa đạt (V2). |
| 5 | MAJOR | CHẤP NHẬN | `CONSTITUTION.md` thành tệp được bảo vệ: sửa phải có ADR. ADR chạm Chương I phải trả lời "làm rõ hay đảo ngược". |
| 6 | MAJOR | CHẤP NHẬN | Chương II gắn ⚠ Vn ngay cạnh từng điều chưa đạt. |
| 7 | MINOR | CHẤP NHẬN | Lộ trình: L7/L8 dời v0.5. |
| 8 | MINOR | CHẤP NHẬN MỘT PHẦN | Mô tả PR được CI kiểm; dòng `MỞ PHIÊN` trong chat thì không thể — ghi V13. |
| 9 | MINOR | GHI NHẬN | Owner đã ra lệnh; `next` của sổ bàn giao chốt v0.3 là sửa V1–V3 trước mọi tính năng mới. |
