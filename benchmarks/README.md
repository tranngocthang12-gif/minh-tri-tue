# BENCHMARK — thi AI bằng đề niêm phong

- Tệp `*.json` ở đây là **đề**, không chứa đáp án — chỉ chứa `key_sha256`.
- **Đáp án** (`<suite>.KEY.json`) do Owner giữ **ngoài repo**. Không bao giờ commit.
- Tác giả đề (trường `authors`) **không được thi** đề của mình.

## Quy trình thi một AI
```bash
python -m minhtri.cli bench-export benchmarks/tang1-core-v1.json > de-thi.md
# dán de-thi.md cho AI (một phiên mới), lưu câu trả lời JSON thành answers.json
python -m minhtri.cli bench-grade benchmarks/tang1-core-v1.json <đường-dẫn-KEY> answers.json <provider>
python -m minhtri.cli champion critique
```
Điểm được ghi vào `brain/providers.json`. Cần ≥ 5 lần thi mỗi việc mới bầu champion.

| Đề | Tác giả | Việc |
|---|---|---|
| `tang1-core-v1` | claude | research, critique, quant |
