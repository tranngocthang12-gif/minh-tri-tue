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
