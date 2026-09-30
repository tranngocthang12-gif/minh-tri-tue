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


### Vòng 2 (head `1f8d0ef`) — Grok APPROVE; Ghế 1 sửa nốt (r3)

| Ý | Ghế 1 | Đã làm |
|---|---|---|
| 5 (còn lại) | CHẤP NHẬN | CI kiểm Chương I: PR làm đổi chữ Chương I phải có ADR ghi `CHƯƠNG-I: LÀM RÕ — <lý do>`; ghi `ĐẢO NGƯỢC` bị chặn. ADR 0001 trả lời rõ: ban hành lần đầu. |
| 7 / N1 | CHẤP NHẬN | Sơ đồ ARCHITECTURE: L7/L8 → v0.5, khớp lộ trình chữ. |
| N2 | CHẤP NHẬN | Thêm test trùng `session` → CI đỏ. |
| N3 | CHẤP NHẬN | Điều 14 gắn đúng ⚠ V11, V13 (bỏ V7 gắn nhầm). |
| N4 | CHẤP NHẬN MỘT PHẦN | Không nâng `1.1`: chưa từng có bản `1.0` nào có hiệu lực — ghi `1.1` là nói sai (Điều 13). Thêm trường `revision: r3` vào khoá và giải thích trong ADR 0001. |
| 1, 2 | GHI NHẬN | V11, V12 vẫn MỞ đúng như Grok nói; V12 chờ Owner quyết. |


### r4 — lỗi thiết kế CI do Claude Code (thi công) phát hiện

Push nhánh bị so với commit trước **trên cùng nhánh** (`github.event.before`). Bản nháp trong PR được phép viết lại
(sổ bàn giao, băm luật) so với nhau — chỉ không được viết lại những gì **đã vào `main`**. Hệ quả: mọi lần sửa lại
PR (r2, r3…) làm lượt CI khi push đỏ giả. Sửa: push nhánh khác `main` so với **điểm tách khỏi `main`**
(`git merge-base HEAD origin/main`); PR và push vào `main` giữ nguyên. Ghi nhận: lỗi của Ghế 1 (thiết kế CI), không phải của nội dung r3.


### Vòng 3 (head `cd5c120`) — Grok APPROVE (0 BLOCKING · 2 MAJOR · 3 MINOR); Ghế 1 trả lời (r5)

Phản biện nguyên văn: comment `provider: grok · session: owner-relay-2026-09-30` trên PR #3 (Owner chuyển tiếp).
Phiên trả lời: `claude-code-2026-09-30-pr3-r5` · vai **Ghế 1** (một vai, không đổi). r5 **không đổi chữ luật** (băm vẫn `1d84896b`).

| Ý | Mức | Ghế 1 | Đã làm / phản chứng |
|---|---|---|---|
| 1 | MAJOR | CHẤP NHẬN | Dòng `OWNER-APPROVED` của ADR 0001 đổi sang tương lai: "Owner **sẽ** tự tay bấm merge …; dòng này không chứng minh merge đã xảy ra." |
| 2 | MAJOR | CHẤP NHẬN MỘT PHẦN | Lệch có thật **trong sổ**: dòng bàn giao `seq 0` gộp dưới một mã `claude-chat-2026-09-30-law` hai phiên thật — chat Claude (Ghế 1, viết luật; mô tả PR ghi `vai: Ghế 1`) và các phiên Claude Code (thi công CI; mục r4 ở trên tự ghi "Claude Code (thi công)", commit r4 mang `Claude-Session` riêng) — rồi ghi `role: Thi công`. Tức là lỗi **ghi sổ gộp hai phiên**, không phải một phiên đổi vai giữa chừng. Không viết lại dòng `seq 0` (xoá dấu vết đúng thứ Grok phê). Từ dòng `seq 1`: mỗi phiên một mã, một vai. CI kiểm `role` khớp mô tả PR → ghi vào "còn mở" cho v0.3 (Điều 10). |
| 3 | MINOR | CHẤP NHẬN (phương án b) | Giữ `revision: r3` trên khoá: r4 và r5 không đổi chữ luật. ADR 0001 ghi rõ "r4 không đổi chữ luật — chỉ CI và sổ". Giới hạn: r3 và r4 nằm chung commit `cd5c120`, nên bằng chứng tách là mục r4 ở trên + dòng bàn giao, không phải diff git riêng. |
| 4 | MINOR | CHẤP NHẬN | "MINH TRÍ TRÍ TUỆ" → "MINH TRÍ TUỆ" (khớp BAN_GIAO E và mô tả repo). |
| 5 | MINOR | CHẤP NHẬN | `brain/law.lock`: `effective` = "khi PR #3 được merge vào main (ngày của commit merge)"; ADR 0001 nói rõ. Không mã nào đọc trường này (đã `grep`). |
| V1–V3, V11, V12, V13 | — | GHI NHẬN | Vẫn MỞ đúng như Grok xác nhận. Không đóng bằng lời. |

### r6 — Owner ra lệnh sửa Chương V.5 (không phải phản biện)

Nguồn: Owner ra lệnh trong chat Claude (Project MINH TRÍ TRÍ TUỆ), 30/09/2026, nguyên văn "sửa chương v.5".
Phiên thi công: `claude-code-2026-09-30-pr3-r6` · vai **Ghế 1**. ADR: `docs/adr/0002-sua-chuong-V5-ai-bam-merge.md`.

| Mục | Đã làm |
|---|---|
| Chữ luật | Chương V.5, gạch cuối: "Owner tự tay bấm merge các PR sửa tệp được bảo vệ." → AI được bấm merge thay Owner khi đủ ba điều kiện (ACCEPT của AI khác trên đúng head · CI xanh trên head đó · lệnh Owner đúng PR, đúng head được trích lên PR trước khi bấm); AI thi công PR không được bấm merge PR đó; thiếu điều kiện → revert. |
| Khoá | `brain/law.lock`: băm `1d84896b` → `0212d5dc`, `revision` r6, `adr` → ADR 0002. |
| Ghi nhận | Mục vòng 1 ý 2 và vòng 3 ý 1 ở trên nói "Owner tự bấm merge" — đúng với chữ luật lúc đó, không sửa. CI chưa kiểm ba điều kiện mới (ghi "còn mở"). Chữ luật đổi → Grok cần phản biện lại head mới. |
| CI | `tools/check_handover.py`: dòng bàn giao cũ trong PR được giữ băm bản luật đã đọc (phải là bản luật thật ở gốc hoặc trong commit của PR); dòng mới cuối phải khớp luật hiện hành. Lý do: sửa luật r6 làm `seq 0`, `seq 1` bị chặn sai. |
