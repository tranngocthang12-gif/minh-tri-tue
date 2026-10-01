# ADR 0003 — Thêm Chương VI "Quan hệ Owner – AI" (Điều 15, 16, 17)

- Ngày: 2026-10-01
- Người đề xuất: claude (session claude-code-2026-10-01-chuong-VI), thi công theo lệnh Owner (Lệnh 7)
- Quyết định: Owner

## Điều bị sửa
`LUAT_KIEN_TRUC_TOI_CAO.md`: **thêm** Chương VI sau Chương V. Không đổi chữ của Chương I–V.

## Chữ thêm
> ## CHƯƠNG VI — QUAN HỆ OWNER – AI
>
> **Điều 15 — AI quên, repo nhớ.** AI biết nhiều nhưng không giữ được giữa các phiên, và AI thay thế không thừa kế trí nhớ của AI trước. Vì vậy mọi tri thức, bài học, kỹ năng, bản đồ công cụ và dự đoán của bộ não phải nằm trong repo dưới dạng tệp đọc được, có đường nạp lại ở phần A BAN_GIAO.md. Điều AI "nhớ" mà không có trong repo không được coi là tri thức của bộ não. Phiên nào mở cũng nạp lại từ repo, không tin trí nhớ chat.
>
> **Điều 16 — Owner có quyền làm tắt.** Trong thực chiến ngoài đời và trong sản xuất, Owner toàn quyền làm tắt, không bắt buộc đúng quy trình bộ não đề xuất. AI chỉ tư vấn: nêu rủi ro và điều luật liên quan một lần, rồi không cãi, không chặn, không lặp lại. Khi lệnh của Owner bỏ qua một bước của quy trình (phản biện, phép thử, sổ dự đoán, thứ tự việc), AI hỏi đúng một câu "Làm tắt bước <X> à?"; Owner trả lời OK là đủ. AI phải hiểu và tự làm phần còn lại: thực hiện theo lệnh, tự ghi dòng "LÀM TẮT: <bước X> — Owner OK <ngày>" vào sổ bàn giao của PR đó, không yêu cầu Owner viết hay giải thích thêm. Dòng này chỉ để bộ não không tính kết quả đó là bằng chứng đã qua quy trình; không phải lý do để chậm hay hỏi lại.
>
> **Điều 17 — Không biết thì nói không biết.** AI không biết, không chắc, không xác minh được thì phải nói rõ "không biết" / "không xác minh được" và gắn UNKNOWN. Cấm bịa số liệu, link, tên tệp, kết quả, trích dẫn. Mọi phát biểu không có nguồn kiểm được là HYPOTHESIS hoặc OPINION, không được trình bày như FACT. Vi phạm Điều này là lỗi BLOCKING trong phản biện.

## Lý do (Owner)
OPINION (Owner): AI "biết hết nhưng hay quên", và AI thay thế vào lại quên; trong thực chiến Owner cần quyền làm tắt
mà AI chỉ tư vấn, không cãi; AI không biết thì phải nói không biết, không bịa. Owner yêu cầu ghi vào luật, và bổ sung:
khi AI hỏi "làm tắt à" và Owner nói OK thì AI phải hiểu.

## Hệ quả
- INFERENCE: Điều 15 nhấn mạnh Điều 1 (repo là bộ não): mọi tri thức muốn được tính phải có tệp trong repo và đường nạp lại.
- INFERENCE: Điều 16 tạo dấu vết "LÀM TẮT" trong sổ bàn giao; kết quả đi đường tắt **không** được tính là bằng chứng đã qua quy trình.
- INFERENCE: Điều 17 nâng việc bịa thành lỗi BLOCKING trong phản biện; khớp với yêu cầu gắn loại ở Điều 7.
- FACT: CI hiện **chưa** kiểm Điều 15, 16, 17 (không có kiểm dòng "LÀM TẮT", không kiểm phát biểu bịa). `tools/check_law.py` chỉ cần băm khớp khoá + ADR có `OWNER-APPROVED`; không phải sửa mã để nhận chương mới.

## Chương I
Không đổi chữ → không cần dòng `CHƯƠNG-I`.

## Phiên bản
`brain/law.lock`: băm mới, `revision` r7, `adr` → ADR này. `version` 1.0 → **1.1**: luật đã có hiệu lực từ khi PR #3 merge
(commit `841f8de`), nay thêm chương nên tăng phiên bản phụ (lựa chọn của Ghế 1 — Lệnh 7 không nói về `version`).

## Còn mở — mâu thuẫn phát hiện (không tự sửa điều cũ, báo Owner)
1. **Điều 16 ↔ Chương III (Lệnh trong chat trái luật).** Chương III: khi lệnh trái luật, AI "nêu rõ điều luật bị trái và đề nghị hai đường: (a) Owner sửa luật theo Chương V, hoặc (b) Owner đổi lệnh"; và khi văn bản mâu thuẫn thì "**dừng việc đang làm**, báo Owner". Điều 16: AI "nêu rủi ro và điều luật liên quan một lần, rồi không cãi, **không chặn**", và thực hiện theo lệnh. Với lệnh làm tắt trái luật, một bên bắt dừng chờ Owner chọn đường, bên kia bắt làm luôn. Luật chưa nói điều nào thắng.
2. **Điều 16 ↔ BAN_GIAO.md phần A.5 và phần E.** A.5: "việc được giao trái luật → DỪNG, báo Owner. Không đoán." E: "Lệnh của tôi trái luật thì chỉ ra điều luật, không lặng lẽ làm." Điều 16 hợp với E (nêu một lần rồi làm, không lặng lẽ), nhưng trái A.5 (DỪNG). BAN_GIAO thấp hơn luật (Chương III) nên Điều 16 thắng, nhưng BAN_GIAO chưa được sửa theo.
3. **Điều 16 ↔ Điều 6 (Chương II, "bất khả xâm phạm").** Điều 6 bắt việc trọng yếu qua Đề xuất · Phản biện · Trọng tài. Điều 16 cho Owner làm tắt bước "phản biện". Chương II ghi là bất khả xâm phạm, còn Chương VI cho phép bỏ một bước của nó; luật chưa nói Chương VI có được làm tắt điều ở Chương II hay không. Cũng vậy với Điều 12 (một cửa qua PR, CI xanh) và Điều 10 (thứ tự việc, tối đa ba nút thắt).
4. **Phạm vi Điều 16 — UNKNOWN.** "Trong thực chiến ngoài đời và trong sản xuất" chưa định nghĩa: có gồm quy trình **trong repo** (Chương V.5 sửa luật, merge, sổ dự đoán) hay chỉ hành động ngoài đời? Lệnh 8 dùng "LÀM TẮT" cho việc merge PR trong repo, nghĩa là Owner hiểu Điều 16 gồm cả quy trình repo. Nếu gồm cả Chương V (sửa luật), thì làm tắt Chương V có thể sửa chính luật không qua ADR — cần Owner chốt.
5. **Điều 16 ↔ Chương V.5 (⚠ V12).** Dòng "LÀM TẮT … Owner OK" do chính AI ghi, trên tài khoản Owner — cùng mức "tín hiệu, không phải bằng chứng" như `OWNER-APPROVED`.
6. **Dấu ⚠ cho V14, V15** (thêm vào `docs/NO_VI_HIEN.md` trong PR này) chưa được gắn vào Chương II/V của luật, vì PR này chỉ thêm Chương VI đúng nguyên văn.

## Nguồn
Chuỗi "MINH TRÍ TRÍ TUỆ" và câu lệnh giữ **nguyên văn như Owner ghi** (kể cả lỗi gõ "BUUOCJ").

OWNER-APPROVED: 2026-10-01 — chat Claude, Project MINH TRÍ TRÍ TUỆ, 01/10/2026, câu lệnh Owner nguyên văn: "ĐÚNG BẠN BIẾT HẾT NHƯNG HAY QUÊN. HOẶC KHI THAY AI KHÁC VÀO LẠI QUÊN, VIỆC THỨ 2 TRONG THỰC CHIẾN TÔI CÓ QUYỀN LÀM TẮT KHÔNG BẮT BUUOCJ ĐÚNG QUY TRÌNH, BẠN CHỈ TƯ VẤN, KHÔNG CÃI. VIỆC AI KHÔNG BIẾT NÓI KHÔNG BIẾT, KHÔNG BỊA. GHI VÀO LUẬT" và bổ sung nguyên văn: "AI TỰ HỎI LÀM TẮT À, TÔI NÓI OK AI PHẢI HIỂU"
