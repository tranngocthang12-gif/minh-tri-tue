# MINH TRÍ TUỆ — Universal Intelligence OS

**Một bộ não duy nhất, xây mới hoàn toàn, sống trong repo GitHub này.**

Bộ não **hiểu, chọn cơ hội, thiết kế phép thử, dự đoán, khuyến nghị**.
Bộ não **không vận hành**: mọi hành động ngoài đời (đăng video, chi tiền, giao dịch) do **Owner** làm.

| Tầng | Vai trò | Trạng thái |
|---|---|---|
| **Tầng 1 — Universal Wisdom & Learning Core** | Cách học, hiểu, phản biện, tự sửa. Không sở hữu chuyên môn. | v0.1 — đang xây |
| **Tầng 2 — Domain Intelligence** | Tri thức từng miền (YouTube, tài chính…) do Tầng 1 mở ra khi Owner giao mục tiêu. | Chưa có miền nào |

## Đọc theo thứ tự
1. [`CONSTITUTION.md`](CONSTITUTION.md) — hệ tư tưởng, kim chỉ nam, ranh giới Phật học.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — kiến trúc Tầng 1 và bản đồ mã.
3. [`CONTRIBUTING.md`](CONTRIBUTING.md) — cửa chung cho ChatGPT, Claude, Gemini, Grok.
4. [`brain/state.json`](brain/state.json) — bộ não đang biết gì, chưa biết gì.

## Chạy
Chỉ cần Python ≥ 3.10, không cần thư viện ngoài, không kết nối mạng.
```bash
python -m unittest discover -s tests -v    # kiểm toàn bộ luật
python -m minhtri.cli status               # xem trạng thái bộ não
python -m minhtri.cli verify               # kiểm chuỗi băm sổ dự đoán
python -m minhtri.cli domain youtube "Kiếm tiền bền vững bằng YouTube"
```
