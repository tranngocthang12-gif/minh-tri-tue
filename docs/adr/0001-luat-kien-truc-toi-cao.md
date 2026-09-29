# ADR 0001 — Ban hành Luật Kiến trúc Tối cao và Luật Bàn giao

- Ngày: 2026-09-30
- Người đề xuất: claude (session claude-chat-2026-09-30-law)
- Quyết định: Owner

## Bối cảnh
Owner yêu cầu: rà soát kiến trúc, xây bộ luật kiến trúc tối cao bảo vệ ý tưởng xuyên suốt chat cũ và chat mới,
và luật bàn giao để phiên mới phải đọc trước khi làm việc.
Rà soát kiến trúc sau PR #1 (`docs/reviews/2026-09-30-ra-soat-kien-truc.md`) cho thấy ý tưởng gốc chưa được
khoá thành luật, và có các lỗ kiến trúc mà phản biện cấp dòng mã không bắt được.

## Quyết định
- Ban hành `LUAT_KIEN_TRUC_TOI_CAO.md` (Chương I–V), khoá băm tại `brain/law.lock`.
- Ban hành `BAN_GIAO.md` và sổ bàn giao chỉ ghi thêm `brain/handover/log.jsonl`.
- Thêm cửa vào cho từng công cụ AI: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
- CI thực thi: khoá băm luật, sửa luật phải có ADR, PR phải ghi sổ bàn giao.
- Lập `docs/NO_VI_HIEN.md` ghi các vi phạm đã biết.

## Hệ quả
Mọi phiên AI tốn thêm vài phút đọc bàn giao. Đổi lại: không phiên nào làm lệch ý tưởng mà không bị phát hiện.

OWNER-APPROVED: 2026-09-30 (lệnh Owner trong chat: "xây bộ luật kiến trúc tối cao… luật bàn giao"; xác nhận cuối bằng việc Owner merge PR)
