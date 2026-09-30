# PR #3 — Bản mô tả r6 (gửi Grok: "PHẢN BIỆN PR #3 lần 2 — head <head r6>")

- PR: https://github.com/tranngocthang12-gif/minh-tri-tue/pull/3 · nhánh `v0.2.4-luat-toi-cao`
- Head trước r6: `91fc871` (Grok vòng 3 APPROVE trên `cd5c120`; r5 không đổi chữ luật)
- Phiên: `provider: claude` · `session: claude-code-2026-09-30-pr3-r6` · vai Ghế 1
- Nguồn quyết định: Owner ra lệnh trong chat Claude (Project MINH TRÍ TRÍ TUỆ), 30/09/2026, nguyên văn "sửa chương v.5".

## Đổi gì
1. FACT — `LUAT_KIEN_TRUC_TOI_CAO.md`, Chương V.5, **chỉ gạch đầu dòng cuối**:
   - Cũ: "Owner tự tay bấm merge các PR sửa tệp được bảo vệ."
   - Mới: AI được bấm merge PR sửa tệp được bảo vệ thay Owner **chỉ khi đủ cả ba**: (1) phản biện của AI khác trên PR,
     ACCEPT trên đúng head sẽ merge; (2) CI xanh trên head đó; (3) Owner ra lệnh merge đúng PR, đúng head trong chat,
     và AI bấm merge trích nguyên văn lệnh + nguồn vào comment trên PR **trước** khi bấm. AI thi công PR không được bấm
     merge PR đó. Thiếu một điều kiện → merge là vi phạm, phải revert.
2. FACT — Thêm `docs/adr/0002-sua-chuong-V5-ai-bam-merge.md`: chữ cũ, chữ mới, lý do, rủi ro, dòng `OWNER-APPROVED` ghi nguồn.
3. FACT — `brain/law.lock`: băm `1d84896b…` → `0212d5dc…`, `revision` r6, `adr` → ADR 0002, `version` giữ `1.0` (luật chưa từng hiệu lực).
4. FACT — Sổ rà soát (`docs/reviews/2026-09-30-ra-soat-kien-truc.md`) thêm mục r6; sổ bàn giao thêm dòng `seq 2`. Không sửa dòng cũ.
5. FACT — Chương I không đổi chữ → không có dòng `CHƯƠNG-I`.

## Vì sao
OPINION (Owner): giao thao tác merge cho AI để giảm việc tay; chấp nhận dấu vết Owner chuyển từ "cú bấm" sang
"câu lệnh trong chat được trích lên PR".

## Điều Ghế 1 tự thấy có thể sai (để Grok soi)
- INFERENCE: Vì AI dùng chung tài khoản Owner (⚠ V12), comment trích lệnh do chính AI bấm merge viết → là tín hiệu, không phải bằng chứng. Điều kiện (3) là dấu vết duy nhất.
- FACT: CI **chưa** kiểm ba điều kiện mới; tuân thủ dựa vào AI bấm merge tự kiểm. Ghi "còn mở" cho v0.3.
- OBSERVATION: ADR 0001 vẫn ghi "Owner **sẽ** tự tay bấm merge PR (Chương V.5)"; không sửa vì ADR là dấu vết lịch sử — ADR 0002 ghi rõ việc này.
- OBSERVATION: `brain/law.lock` chỉ trỏ một ADR (0002); ADR 0001 không còn được khoá trỏ tới — CI chỉ cần ADR mới nhất.
- HYPOTHESIS: "AI khác" và "AI thi công" chưa định nghĩa theo provider hay theo phiên; ADR 0002 hiểu là theo phiên (`provider`/`session`).
- FACT: chuỗi "MINH TRÍ TRÍ TUỆ" giữ nguyên văn như Owner ghi trong lệnh (vòng 3 ý 4 từng sửa lỗi chữ này ở ADR 0001).

## Kiểm chứng (local, base `b2767427`)
Xem mục "Kiểm chứng r6" trong mô tả PR #3.
