# BENCHMARK — thi AI bằng đề niêm phong

- Tệp `*.json` ở đây là **đề**, không chứa đáp án — chỉ chứa `key_sha256`. CI quét mọi tầng của đề, cấm các trường mang đáp án.
- **Đáp án** (`<suite>.KEY.json`) do Owner giữ **ngoài repo**. Không bao giờ commit (`.gitignore` chặn `*.KEY.json`).
- **Không được thi:** tác giả đề (`authors`, kể cả bí danh như `claude-opus`, `anthropic`), provider đã đọc đề ngoài phòng thi (`exposed_to` — ví dụ khi phản biện PR có đề), và mọi phiên soạn đề (`author_sessions`).
- Mỗi (provider, đề, việc) chỉ ghi điểm **một lần**. Champion cần **≥ 5 đề khác nhau** mỗi việc.
- Câu `set` chấm theo tập **bắt buộc**; mã trong tập **chấp nhận** không bị phạt.

## Quy trình thi một AI
```bash
python -m minhtri.cli bench-check-key benchmarks/tang1-core-v1.json ~/minh-tri-keys/tang1-core-v1.KEY.json
python -m minhtri.cli bench-export benchmarks/tang1-core-v1.json > de-thi.md
# dán de-thi.md cho AI trong MỘT PHIÊN MỚI, lưu câu trả lời JSON thành answers.json
python -m minhtri.cli bench-grade benchmarks/tang1-core-v1.json ~/minh-tri-keys/tang1-core-v1.KEY.json answers.json <provider> <mã-phiên-thi>
```

| Đề | Trạng thái | Tác giả | Đã lộ cho | Ai thi được |
|---|---|---|---|---|
| `tang1-core-v1` | **THỬ — chưa đủ bầu champion** | claude | grok | chatgpt, gemini |
