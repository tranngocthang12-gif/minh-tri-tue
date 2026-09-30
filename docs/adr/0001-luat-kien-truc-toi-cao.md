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

## Chương I
Ban hành lần đầu: Chương I được **viết ra lần đầu** từ ý tưởng Owner trong chat và sổ ghi nhớ dự án — không làm rõ, không đảo ngược bản nào trước đó.

## Phiên bản
Khoá `1.0` = bản ban hành đầu tiên. Nội dung thay đổi 3 lần **trong PR #3, trước khi có hiệu lực** (r1 → r3, theo phản biện Grok), nên không có bản nào khác từng hiệu lực; trường `revision` của `brain/law.lock` ghi lần sửa nháp.
**r4 không đổi chữ luật** — chỉ sửa CI (`.github/workflows/ci.yml`: chọn commit gốc để so) và sổ; vì vậy khoá vẫn ghi `r3` và băm `1d84896b` là băm của chữ r3. Các lần sửa sau r4 trong PR này (vòng 3) cũng không đổi chữ luật.
Trường `effective` của khoá = **khi PR #3 được merge vào `main`**; ngày hiệu lực thật là ngày của commit merge trên `main`, không phải ngày ghi trong tệp.

OWNER-APPROVED: 2026-09-30 — nguồn: Owner ra lệnh trong chat Claude (Project MINH TRÍ TUỆ, phiên claude-chat-2026-09-30-law): "XÂY BỘ LUẬT KIẾN TRÚC TỐI CAO, BẢO VỆ Ý TƯỞNG KIẾN TRÚC. VÀ CÓ LUẬT BÀN GIAO". Owner **sẽ** tự tay bấm merge PR (Chương V.5); dòng này không chứng minh merge đã xảy ra.
