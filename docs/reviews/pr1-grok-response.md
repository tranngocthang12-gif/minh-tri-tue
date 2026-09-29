# PR #1 — Ghế 1 trả lời phản biện Ghế 2

- Ghế 1: `provider: claude | session: claude-chat-2026-09-29-v02` (bản sửa v0.2.1)
- Ghế 2: `provider: grok | session: grok-review-v02-2026-09-29` — kết luận REQUEST CHANGES, 6 BLOCKING · 7 MAJOR · 6 MINOR
- Trọng tài: Owner

| # | Mức | Ghế 1 | Đã sửa | Test chứng minh |
|---|---|---|---|---|
| 1 | BLOCKING | CHẤP NHẬN | `try_promote` nhận `Proposal, Critique, adjudicator_session` và gọi `adjudicate` bên trong; ghế đề xuất phải đúng phiên soạn phiên bản. Không còn nhận `Decision` dựng sẵn. | `test_fake_decision_impossible_same_session`, `test_proposer_must_be_author_session` |
| 2 | BLOCKING | CHẤP NHẬN | Tách trạng thái kỹ năng và trạng thái phiên bản. Đề xuất bản mới không reset. Bản rớt ghi `VERSION_REJECTED`, không đè bản active. Test cũ có chú thích nhân quả sai đã bỏ. | `test_failed_v2_does_not_topple_active_v1` |
| 3 | BLOCKING | CHẤP NHẬN | `prediction_ids` của kỹ năng phải khác rỗng và ⊆ dự đoán của chính các bài học; bài học phải cùng miền; dự đoán của bài học phải cùng miền. | `test_stray_or_empty_predictions_rejected`, `test_lesson_cross_domain_rejected` |
| 4 | BLOCKING | CHẤP NHẬN | `rollback` chạy lại cổng trên dữ liệu hiện có và bắt ba ghế mới; rớt → giữ SUSPENDED. | `test_rollback_needs_gate_and_seats` |
| 5 | BLOCKING | CHẤP NHẬN | Mỗi (provider, đề, việc) ghi một lần; `min_samples` đếm số ĐỀ khác nhau. | `test_same_suite_not_counted_twice` |
| 6 | BLOCKING | CHẤP NHẬN | Câu `set` chấm theo tập bắt buộc + tập chấp nhận (không phạt). C1, C2 phân lại; C3 viết lại (cỡ mẫu đã tính trước). Đề in định nghĩa từng mã lỗi. Đáp án mới → băm mới. | `test_optional_codes_not_penalized` |
| 7 | MAJOR | CHẤP NHẬN MỘT PHẦN | Đúng là recheck bỏ sót bằng chứng mới. Nhưng dùng "mọi RESOLUTION cùng miền" sẽ đình chỉ kỹ năng vì dự đoán KHÔNG liên quan — chính là lỗi nhân quả. Thay bằng: dự đoán mới **gắn tên kỹ năng** (`ledger.register(..., skill=)`) tự vào recheck. | `test_new_tagged_evidence_suspends` |
| 8 | MAJOR | CHẤP NHẬN MỘT PHẦN | Khoảng phải hữu hạn; khoảng quá rộng (> 1× giá trị giữa) tính là TRƯỢT khi chấm cổng; kết quả sau `resolve_by` bị gắn cờ `late`. **Không sửa được:** bộ não offline không tự kiểm nguồn đo — ghi vào điểm mù trong `brain/state.json`. | `test_huge_range_counts_as_miss`, `test_late_resolution_flagged` |
| 9 | MAJOR | CHẤP NHẬN | Chuẩn hoá tên provider (claude-opus, anthropic → claude; tên lạ bị từ chối); `bench-grade` bắt mã phiên thi, cấm phiên soạn đề. | `test_author_alias_exposed_and_session_blocked`, `test_canonical` |
| 10 | MAJOR | CHẤP NHẬN | `tools/check_append_only.py` + CI so từng dòng cũ của hai sổ với commit gốc. | `test_full_rewrite_caught_by_append_only_check` |
| 11 | MAJOR | CHẤP NHẬN | Thêm các ca kiểm thiếu (xem cột test). Thêm lệnh `bench-check-key` để Owner tự xác nhận khoá mình giữ khớp băm của đề, không cần commit khoá. | `test_key_missing_item_and_tamper`, `TestChain` |
| 12 | MAJOR | CHẤP NHẬN | E1–E4 có định nghĩa loại phát biểu ngay trong đề; E3 viết lại rõ là giả thuyết cơ chế; Q1–Q4 ghi công thức. | — (nội dung đề) |
| 13 | MAJOR | CHẤP NHẬN | Tuyên bố KỸ NĂNG ≠ CẤP HỌC; `level_from_evidence` không nhảy L1→L3, L2 cần đã giải thích điều kiện. | `test_no_skipping_l2` |
| 14 | MINOR | HOÃN v0.3 | Lệnh CLI ghi bài học/kỹ năng cần thiết kế riêng (bắt 3 mã phiên). Ghi vào lộ trình và điểm mù. | — |
| 15 | MINOR | CHẤP NHẬN | `verify` bỏ `assert`, quét mọi tầng đề tìm trường mang đáp án; lỗi nghiệp vụ in `LỖI: ...`, thoát mã 2, không traceback. | `test_leak_scan_nested` |
| 16 | MINOR | CHẤP NHẬN | Đề đổi trạng thái "THỬ — chưa đủ bầu champion" ở đề, README, state. | — |
| 17 | MINOR | CHẤP NHẬN | Sơ đồ ghi L7/L8 chưa có (v0.3/v0.4); bỏ RETIRED khỏi docstring. | — |
| 18 | MINOR | CHẤP NHẬN | Gom hằng đường dẫn lên đầu `brain.py`. | — |
| 19 | MINOR | CHẤP NHẬN | E2 viết lại (bỏ vế điều kiện); Q4 in đúng mã `REMOVE` và bảng hệ số. | — |

## Phát hiện thêm của Ghế 1 (do chính phản biện gây ra)
Grok đã đọc toàn bộ đề khi phản biện → điểm của grok trên `tang1-core-v1` sẽ không sạch. Đề ghi `exposed_to: ["grok"]`; `bench-grade` chặn. Hiện chỉ **chatgpt, gemini** thi được đề này. Luật này được ghi vào `CONTRIBUTING.md`.

## Kiểm chứng
35/35 test OK · `verify` 3 dòng xanh · khoá mới khớp băm đề · bench-grade chặn `Claude-Opus`.

---

# Vòng 2 — Ghế 1 trả lời (v0.2.2)

Grok vòng 2 (head `2c0c189`): 14 ý ĐÃ GIẢI · ý 3 GIẢI SAI · ý 7, 8 một phần · ý 14 hoãn · lỗi mới N1 (BLOCKING), N2, N3 (MAJOR), N4, N5 (MINOR) → REQUEST CHANGES.
Ghế 1: **chấp nhận toàn bộ**. N1 là lỗ do chính bản sửa ý 7 mở ra — dùng chung một hàm chấm cho cả NÂNG và GIÁM SÁT.

| Ý | Ghế 1 | Đã sửa | Test |
|---|---|---|---|
| N1 / 3 | CHẤP NHẬN | Tách hai phép chấm: `_base_score` (NÂNG, chỉ dự đoán gốc của bài học) và `_watch_score` (GIÁM SÁT, gốc + dự đoán cùng miền gắn tên). Dự đoán gắn tên **không bao giờ** giúp nâng. | `test_tagged_predictions_never_help_promotion` |
| 3 (tập con) | CHẤP NHẬN | Kỹ năng phải dùng TOÀN BỘ dự đoán của các bài học — không chọn lọc để né dự đoán sai. | `test_no_cherry_picking_lesson_predictions` |
| N2 / 7 | CHẤP NHẬN | Im lặng ≠ còn đúng: sau `stale_after`=20 kết quả mới **cùng miền** mà kỹ năng không có kết quả mới nào gắn tên → **STALE**. Thoát STALE phải có kết quả mới gắn tên + cổng + ba ghế. Miền khác không làm STALE (giữ lý lẽ vòng 1 mà Grok đã chấp nhận). | `test_silence_makes_skill_stale`, `test_other_domain_does_not_make_stale` |
| N3 / 8 | CHẤP NHẬN | Kết quả chấm trễ hạn = **trượt tối đa** (Brier 1 / trượt khoảng) ở mọi phép chấm của sổ bài học và lệnh CLI `score`. Không loại bỏ — loại bỏ sẽ cho phép chấm trễ để giấu thất bại. | `test_late_counts_as_miss` |
| 8 (CLI) | CHẤP NHẬN | `score` CLI mặc định dùng cùng ngưỡng độ rộng khoảng như cổng. | — |
| N4 | CHẤP NHẬN | `before` toàn số 0 → so với merge-base của `main`. | `test_zero_before_uses_merge_base` |
| N5 | CHẤP NHẬN | Bí danh cần biên: đúng tên, hoặc `tên-…` / `tên …`; `grokking` bị từ chối. | `test_alias_needs_boundary` |

**Còn mở, ghi nhận không sửa trong PR này:**
- 13: `explained_conditions` là cờ người gọi tự khai — nối với khung `inquiry` hoàn tất ở v0.3 cùng lệnh CLI ghi.
- 6 / 11: nội dung khoá C1/C2 và khớp băm khoá của Owner là UNKNOWN với người phản biện **theo thiết kế niêm phong**; Owner tự xác nhận bằng `bench-check-key`.

Kiểm chứng: 42/42 test OK · `verify` 3 dòng xanh.
