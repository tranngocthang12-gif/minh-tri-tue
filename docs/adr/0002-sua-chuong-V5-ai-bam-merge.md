# ADR 0002 — Sửa Chương V.5: AI được bấm merge thay Owner theo ba điều kiện

- Ngày: 2026-09-30
- Người đề xuất: claude (session claude-code-2026-09-30-pr3-r6), thi công theo lệnh Owner
- Quyết định: Owner

## Điều bị sửa
`LUAT_KIEN_TRUC_TOI_CAO.md` — Chương V, khoản 5 (Giới hạn hiện tại ⚠ V12), **gạch đầu dòng cuối**. Các gạch khác của V.5
và các chương khác không đổi chữ.

### Chữ cũ
> - Owner tự tay bấm merge các PR sửa tệp được bảo vệ.

### Chữ mới
> - Một AI được bấm merge PR sửa tệp được bảo vệ thay Owner **chỉ khi đủ cả ba**: (1) có phản biện của AI khác đăng
>   trên PR với phán quyết ACCEPT trên đúng head sẽ merge; (2) CI xanh trên head đó; (3) Owner ra lệnh merge **đúng PR
>   đó, đúng head đó** trong chat, và AI bấm merge phải trích nguyên văn câu lệnh + nguồn (chat nào, ngày) vào comment
>   trên PR **trước** khi bấm. AI thi công PR không được là AI bấm merge của PR đó. Thiếu một điều kiện thì merge là
>   vi phạm luật, phải revert.

## Lý do
Owner muốn giao thao tác merge cho AI để giảm việc tay. Owner chấp nhận dấu vết của mình chuyển từ **"cú bấm"** sang
**"câu lệnh trong chat được trích lên PR"**.

## Hệ quả và rủi ro
- FACT: AI vẫn dùng chung tài khoản GitHub của Owner (⚠ V12), nên GitHub không phân biệt được ai bấm merge. Trước đây
  cú bấm của Owner cũng không chứng minh được bằng mã; nay **điều kiện (3) là dấu vết duy nhất** cho thấy Owner muốn merge.
- INFERENCE: Comment trích lệnh do chính AI bấm merge viết, nên nó chỉ là **tín hiệu, không phải bằng chứng** (cùng mức
  với dòng `OWNER-APPROVED`). Chống gian lận dựa vào: phản biện ACCEPT của AI **khác** gắn đúng head, CI xanh trên đúng head,
  và việc Owner đọc lại comment trích lệnh sau merge.
- FACT: Hiện **CI chưa kiểm** ba điều kiện này; việc tuân thủ dựa vào AI bấm merge tự kiểm và dấu vết comment. Nếu thiếu
  một điều kiện, luật bắt **revert**.
- FACT: "AI thi công PR không được là AI bấm merge của PR đó" — tách vai theo phiên. Vì cùng tài khoản (V12), chỉ kiểm được
  qua `provider`/`session` ghi trong comment và mô tả PR.
- Áp dụng ngay cho PR #3: nếu Owner chọn cho AI bấm merge PR #3, phải đủ ba điều kiện trên **head sau lần sửa này**.
- ADR 0001 (dòng `OWNER-APPROVED`) ghi "Owner **sẽ** tự tay bấm merge PR (Chương V.5)". Dòng đó không sửa (ADR là dấu vết lịch sử);
  từ ADR này, V.5 cho phép thêm đường AI bấm merge theo ba điều kiện.

## Chương I
Không đổi chữ → không cần dòng `CHƯƠNG-I`.

## Phiên bản
`brain/law.lock`: băm mới, `revision` = r6, `adr` = ADR này. `version` vẫn `1.0` vì luật **chưa từng có hiệu lực**
(PR #3 chưa merge); r6 là lần sửa nháp thứ tư của chữ luật trong PR #3 (r1 → r3, r6).

## Nguồn
Chuỗi "MINH TRÍ TRÍ TUỆ" trong dòng dưới giữ **nguyên văn như Owner ghi trong lệnh** (tên đúng của dự án: MINH TRÍ TUỆ).

OWNER-APPROVED: 2026-09-30 — chat Claude, Project MINH TRÍ TRÍ TUỆ, 30/09/2026, câu lệnh Owner nguyên văn: "sửa chương v.5"
