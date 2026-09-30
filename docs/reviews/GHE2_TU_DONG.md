# Ghế 2 tự động — Grok phản biện PR qua GitHub Action

- Workflow: `.github/workflows/ghe2-grok.yml`
- Script: `minhtri/tools/ghe2_grok.py`
- Lời nhắc hệ thống: `docs/reviews/LOI_NHAC_GHE2.md`

## Cách chạy
- **Tự động:** mỗi PR `opened` / `synchronize` (commit mới) / `reopened`. Lần chạy mới hủy lần cũ đang chạy của cùng PR.
- **Tay (PR đã mở, không cần commit mới):** Actions → `ghe2-grok` → *Run workflow* → nhập số PR.
- Kết quả là một comment trên PR, dòng đầu:
  `KẾT QUẢ PHẢN BIỆN — PR #<n> — provider: grok · session: gh-action-<run_id> · head: <sha> · model: <model>`,
  tiếp theo là nguyên văn trả lời của Grok. Cuối comment có ghi chú ẩn `<!-- ghe2-usage: … -->` chứa số token.
- Log của Action in số tệp, độ dài diff, model và `usage` — **không bao giờ in khóa API**.
- Đổi model: biến repo `GROK_MODEL` (Settings → Secrets and variables → Actions → Variables). Mặc định `grok-4`.
- Chạy thử tại máy (cần khóa thật):
  `PR_NUMBER=2 GITHUB_REPOSITORY=tranngocthang12-gif/minh-tri-tue GITHUB_TOKEN=… XAI_API_KEY=… python -m minhtri.tools.ghe2_grok`

## Chi phí ước tính mỗi lần chạy (ESTIMATE — kiểm lại bảng giá xAI)
Giả định giá `grok-4` ≈ 3 USD / 1 triệu token vào, 15 USD / 1 triệu token ra (gồm token suy luận). HYPOTHESIS: tiếng Việt ≈ 2,5–3 ký tự/token.

| Cỡ PR | Token vào | Token ra (kể cả suy luận) | Ước tính |
|---|---|---|---|
| Nhỏ (diff ~5.000 ký tự) | ~3.000 | ~2.000–5.000 | ~0,04–0,08 USD |
| Lớn (diff cắt ở 60.000 ký tự) | ~22.000–25.000 | ~3.000–8.000 | ~0,11–0,20 USD |

Mỗi commit mới đẩy lên PR là một lần chạy. Số token thật của mỗi lần nằm trong log Action và ghi chú ẩn cuối comment.

## Cách tắt
- Một PR: gắn nhãn `skip-ghe2` **trước** khi đẩy commit tiếp (nhãn gắn sau không hủy lần chạy đang chạy).
- Toàn repo: Actions → `ghe2-grok` → *Disable workflow*, hoặc xóa Secret `XAI_API_KEY` (khi đó Action chỉ đăng "Ghế 2 tự động lỗi: thiếu XAI_API_KEY").
- PR do bot/Action tạo tự bị bỏ qua.

## Giới hạn
- **Diff cắt ở 60.000 ký tự.** Thứ tự giữ: tệp luật (`CONSTITUTION.md`, `CONTRIBUTING.md`, `ARCHITECTURE.md`, `LUAT*`) → ADR → `minhtri/` → `brain/` → còn lại. Khi cắt, comment gửi Grok ghi rõ "⚠ diff đã cắt" và liệt kê tệp bị cắt/bỏ.
- **Grok không đọc được toàn repo** — chỉ thấy mô tả PR, danh sách tệp và diff. Lời nhắc bảo Grok "đọc CONSTITUTION.md trên repo" nhưng khi chạy tự động Grok không có quyền đó: phản biện về mâu thuẫn luật chỉ đúng với phần luật nằm trong diff.
- Tệp nhị phân / tệp quá lớn GitHub không trả patch → chỉ có tên tệp.
- **Lỗi không chặn CI:** lỗi API/mạng → comment ngắn "Ghế 2 tự động lỗi: <mã lỗi>, không có phán quyết", thoát mã 0. Không có phán quyết ≠ ACCEPT.
- PR từ fork không nhận được Secret → Action không đăng được comment (token chỉ đọc); cần chạy tay.
- Script `minhtri/tools/ghe2_grok.py` và lời nhắc `LOI_NHAC_GHE2.md` được lấy **từ `main`**, không từ nhánh PR — PR sửa hai tệp này chỉ có tác dụng sau khi merge. **Ngoại lệ khởi tạo:** PR #4 (PR đưa Ghế 2 vào repo) chạy bằng bản của chính nhánh PR vì `main` chưa có; PR khác mà `main` chưa có hai tệp thì bị bỏ qua.
- Còn hở: tệp workflow `.github/workflows/ghe2-grok.yml` với sự kiện `pull_request` vẫn lấy **từ nhánh PR** (GitHub quy định), nên PR sửa chính workflow vẫn đổi được cách chạy. Owner phải đọc kỹ PR nào đụng vào tệp này.
- Grok được báo tệp luật (`LUAT_KIEN_TRUC_TOI_CAO.md`, `CONSTITUTION.md`) có hay chưa trên head PR; thiếu thì Grok phải ghi "chưa có tệp luật trên nhánh này".
- Trả lời Grok dài quá giới hạn comment GitHub thì bị cắt và ghi rõ.
- Grok được gửi kèm **toàn bộ comment trước đó trên PR** (phản biện Grok cũ, trả lời Ghế 1, comment khác; bỏ ghi chú token ẩn), tối đa 30.000 ký tự — quá thì bỏ comment cũ nhất trước và ghi rõ. Lời nhắc yêu cầu Grok chỉ nêu điểm mới hoặc điểm chưa được trả lời thỏa đáng: "Điểm đã được trả lời có bằng chứng thì không nhắc lại." Chưa gửi review comment gắn dòng mã (chỉ comment chung của PR).
- Theo CONTRIBUTING luật 2, comment Grok tính là phản biện của AI khác nhà cung cấp, nhưng **không thay** Owner chốt merge.

## Mục còn mở
- **`pull_request_target`:** chưa dùng. Nó sẽ lấy tệp workflow từ `main` (đóng chỗ hở "PR sửa chính workflow") và cho PR từ fork nhận Secret — nhưng chạy mã của nhánh PR với Secret là rủi ro lộ khóa, nên cần thiết kế riêng (chỉ checkout `main`, không chạy mã nhánh PR). Chưa quyết; Owner chốt.
- **PR từ fork:** chưa thử (repo chưa có fork). Với sự kiện `pull_request`, fork không nhận Secret `XAI_API_KEY` và `GITHUB_TOKEN` chỉ đọc → script đi nhánh "thiếu XAI_API_KEY", đăng comment thất bại, thoát mã 0; không có phán quyết. Cách xử lý hiện tại: maintainer chạy tay `workflow_dispatch` với số PR fork. Chưa có luật riêng cho PR fork.
- **Workflow lấy từ nhánh PR và ngoại lệ khởi tạo PR #4:** ngoại lệ một lần; sau merge mọi PR chạy script/lời nhắc trên `main`, nhưng tệp workflow vẫn lấy từ nhánh PR (xem Giới hạn).
