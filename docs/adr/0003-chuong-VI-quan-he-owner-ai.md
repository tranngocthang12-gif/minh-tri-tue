# ADR 0003 — Thêm Chương VI "Quan hệ Owner – AI" (Điều 15, 16, 17)

- Ngày: 2026-10-01
- Người đề xuất: claude (session claude-code-2026-10-01-chuong-VI; r8: claude-code-2026-10-01-chuong-VI-r8), thi công theo lệnh Owner (Lệnh 7, Lệnh 9)
- Quyết định: Owner

## Điều bị sửa
`LUAT_KIEN_TRUC_TOI_CAO.md`: **thêm** Chương VI sau Chương V. Không đổi chữ của Chương I–V.

## Chữ thêm
> ## CHƯƠNG VI — QUAN HỆ OWNER – AI
>
> **Điều 15 — AI quên, repo nhớ.** AI biết nhiều nhưng không giữ được giữa các phiên, và AI thay thế không thừa kế trí nhớ của AI trước. Vì vậy mọi tri thức, bài học, kỹ năng, bản đồ công cụ và dự đoán của bộ não phải nằm trong repo dưới dạng tệp đọc được, có đường nạp lại ở phần A BAN_GIAO.md. Điều AI "nhớ" mà không có trong repo không được coi là tri thức của bộ não. Phiên nào mở cũng nạp lại từ repo, không tin trí nhớ chat.
>
> **Điều 16 — Owner có quyền làm tắt trong sản xuất.** Điều này áp dụng cho giai đoạn **vận hành và sản xuất** (làm MV, nhạc, nội dung, phép thử thị trường, thao tác ngoài đời), tức quy trình sản xuất mà bộ não đề xuất ở Tầng 2 và lớp vận hành. Khi lệnh của Owner lệch quy trình sản xuất đó, hệ thống hỏi đúng một câu "Làm tắt bước <X> à?"; Owner trả lời OK thì làm theo lệnh, KHÔNG thì theo quy trình; AI nêu rủi ro một lần, không cãi, không chặn, không lặp lại. AI tự ghi dòng "LÀM TẮT: <bước X> — Owner OK <ngày>" vào sổ của việc đó để kết quả không bị tính là bằng chứng đã qua quy trình; không yêu cầu Owner viết gì thêm.
> Điều này **không áp dụng** cho việc xây và sửa bộ não: phản biện độc lập (Điều 6), mọi thay đổi qua PR (Điều 12), kiểm băm luật (Điều 13), Chương III và Chương V. Những điều đó chỉ đổi bằng ADR, không bằng một chữ OK trong chat.
>
> **Điều 17 — Không biết thì nói không biết.** AI không biết, không chắc, không xác minh được thì phải nói rõ "không biết" / "không xác minh được" và gắn UNKNOWN. Cấm bịa số liệu, link, tên tệp, kết quả, trích dẫn. Mọi phát biểu không có nguồn kiểm được là HYPOTHESIS hoặc OPINION, không được trình bày như FACT. Vi phạm Điều này là lỗi BLOCKING trong phản biện.

## Lý do (Owner)
OPINION (Owner): AI "biết hết nhưng hay quên", và AI thay thế vào lại quên; trong thực chiến Owner cần quyền làm tắt
mà AI chỉ tư vấn, không cãi; AI không biết thì phải nói không biết, không bịa. Owner yêu cầu ghi vào luật, và bổ sung:
khi AI hỏi "làm tắt à" và Owner nói OK thì AI phải hiểu.

r8 (Lệnh 9, sau Grok REJECT trên head `254e547`): Owner làm rõ ý — làm tắt là cho **sau khi dự án hoàn tất, đi vào sản
xuất**; khi lệnh lệch quy trình sản xuất thì hệ thống hỏi lại "đồng ý làm tắt không", Owner trả lời OK hoặc KHÔNG.
Điều 16 được viết lại theo đó: chỉ áp dụng cho vận hành và sản xuất; **không** áp dụng cho việc xây và sửa bộ não.

## Hệ quả
- INFERENCE: Điều 15 nhấn mạnh Điều 1 (repo là bộ não): mọi tri thức muốn được tính phải có tệp trong repo và đường nạp lại.
- INFERENCE: Điều 16 (r8) tạo dấu vết "LÀM TẮT" trong sổ của việc sản xuất đó; kết quả đi đường tắt **không** được tính là bằng chứng đã qua quy trình. Việc xây/sửa bộ não (Điều 6, 12, 13, Chương III, V) không làm tắt được bằng chữ OK.
- INFERENCE: Điều 17 nâng việc bịa thành lỗi BLOCKING trong phản biện; khớp với yêu cầu gắn loại ở Điều 7.
- FACT: CI hiện **chưa** kiểm Điều 15, 16, 17 (không có kiểm dòng "LÀM TẮT", không kiểm phát biểu bịa). `tools/check_law.py` chỉ cần băm khớp khoá + ADR có `OWNER-APPROVED`; không phải sửa mã để nhận chương mới.

## Chương I
Không đổi chữ → không cần dòng `CHƯƠNG-I`.

## Phiên bản
`brain/law.lock`: băm mới, `revision` r7 → **r8** (viết lại Điều 16), `adr` → ADR này. `version` 1.0 → **1.1**: luật đã có hiệu lực từ khi PR #3 merge
(commit `841f8de`), nay thêm chương nên tăng phiên bản phụ (lựa chọn của Ghế 1 — Lệnh 7 không nói về `version`).

## Còn mở
r8: mâu thuẫn 1–4 của bản r7 (Điều 16 ↔ Chương III; ↔ BAN_GIAO A.5/E; ↔ Điều 6, 10, 12; phạm vi Điều 16 UNKNOWN) **đã giải**
bằng cách tách phạm vi: Điều 16 chỉ áp dụng cho vận hành và sản xuất, không áp dụng cho việc xây và sửa bộ não.
BAN_GIAO A.5 không sửa (Lệnh 9).

5. **Điều 16 ↔ Chương V.5 (⚠ V12).** Dòng "LÀM TẮT … Owner OK" do chính AI ghi, trên tài khoản Owner — cùng mức "tín hiệu, không phải bằng chứng" như `OWNER-APPROVED`.
6. **Dấu ⚠ cho V14, V15** (thêm vào `docs/NO_VI_HIEN.md` trong PR này) chưa được gắn vào Chương II/V của luật — làm ở PR-5 của Lệnh 8.

## Nguồn
Chuỗi "MINH TRÍ TRÍ TUỆ" và câu lệnh giữ **nguyên văn như Owner ghi** (kể cả lỗi gõ "BUUOCJ", "HỆ THÔNG", "LÊN", "ĐỰA", "CẨU").

OWNER-APPROVED: 2026-10-01 — chat Claude, Project MINH TRÍ TRÍ TUỆ, 01/10/2026, câu lệnh Owner nguyên văn: "ĐÚNG BẠN BIẾT HẾT NHƯNG HAY QUÊN. HOẶC KHI THAY AI KHÁC VÀO LẠI QUÊN, VIỆC THỨ 2 TRONG THỰC CHIẾN TÔI CÓ QUYỀN LÀM TẮT KHÔNG BẮT BUUOCJ ĐÚNG QUY TRÌNH, BẠN CHỈ TƯ VẤN, KHÔNG CÃI. VIỆC AI KHÔNG BIẾT NÓI KHÔNG BIẾT, KHÔNG BỊA. GHI VÀO LUẬT" và bổ sung nguyên văn: "AI TỰ HỎI LÀM TẮT À, TÔI NÓI OK AI PHẢI HIỂU"

OWNER-APPROVED: 2026-10-01 — chat Claude, Project MINH TRÍ TRÍ TUỆ, 01/10/2026, câu lệnh Owner nguyên văn (r8, Điều 16): "Ý TÔI LÀ SAU NÀY KHI DỰ ÁN HOÀN TẤT, ĐI VÀO SẢN XUẤT, CÓ THỂ NHIỀU VIỆC CẦN LÀM TẮT, HỆ THÔNG SẼ KHÔNG NGHE. LÊN KHI TÔI VIẾT LỆNH NẾU KHÔNG ĐÚNG QUY TRÌNH SẢN XUẤT, THÌ HỆ THỐNG SẼ ĐỰA RA CẨU HỎI LẠI ĐỒNG Ý LÀM TẮT KHÔNG. KHI ĐÓ TÔI OK HOẶC KHÔNG."
