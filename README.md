# MINH TRÍ TUỆ — Universal Intelligence OS

**Một bộ não duy nhất, xây mới hoàn toàn, sống trong repo GitHub này.**

Bộ não **hiểu, chọn cơ hội, thiết kế phép thử, dự đoán, khuyến nghị**.
Bộ não **không vận hành**: mọi hành động ngoài đời (đăng video, chi tiền, giao dịch) do **Owner** làm.

| Tầng | Vai trò | Trạng thái |
|---|---|---|
| **Tầng 1 — Universal Wisdom & Learning Core** | Cách học, hiểu, phản biện, tự sửa. Không sở hữu chuyên môn. | v0.1 — đang xây |
| **Tầng 2 — Domain Intelligence** | Tri thức từng miền (YouTube, tài chính…) do Tầng 1 mở ra khi Owner giao mục tiêu. | Chưa có miền nào |

## ⚠️ Mọi phiên AI/người: đọc [`BAN_GIAO.md`](BAN_GIAO.md) TRƯỚC khi làm bất cứ việc gì

## Đọc theo thứ tự
0. [`LUAT_KIEN_TRUC_TOI_CAO.md`](LUAT_KIEN_TRUC_TOI_CAO.md) — **luật cao nhất**, bảo vệ ý tưởng gốc.
1. [`CONSTITUTION.md`](CONSTITUTION.md) — hệ tư tưởng, kim chỉ nam, ranh giới Phật học.
2. [`ARCHITECTURE.md`](ARCHITECTURE.md) — kiến trúc Tầng 1 và bản đồ mã.
3. [`BAN_GIAO.md`](BAN_GIAO.md) · [`CONTRIBUTING.md`](CONTRIBUTING.md) — mở/đóng phiên, cửa chung cho 4 AI.
4. [`docs/NO_VI_HIEN.md`](docs/NO_VI_HIEN.md) — **điều hệ thống CHƯA đạt** (đọc để không tin quá mức).
5. [`brain/state.json`](brain/state.json) — bộ não đang biết gì, chưa biết gì.

## Chạy
Chỉ cần Python ≥ 3.10, không cần thư viện ngoài, không kết nối mạng.
```bash
python -m unittest discover -s tests -v    # kiểm toàn bộ luật
python -m minhtri.cli status               # xem trạng thái bộ não
python -m minhtri.cli verify               # kiểm chuỗi băm sổ dự đoán
python -m minhtri.cli domain youtube "Kiếm tiền bền vững bằng YouTube"
```

### Ghế 2 tự động (Grok phản biện PR)
Mỗi PR mở/có commit mới, Action `ghe2-grok` gửi mô tả PR + diff cho Grok và đăng "KẾT QUẢ PHẢN BIỆN" lên PR.
Đây là công cụ vận hành repo (`minhtri/tools/`), không thuộc lõi bộ não; cần mạng, `requests` và Secret `XAI_API_KEY`.
**Đổi model:** Settings → Secrets and variables → Actions → tab *Variables* → tạo/sửa biến `GROK_MODEL`
(ví dụ `grok-4`, `grok-3-mini`). Không đặt → mặc định `grok-4`. Chi tiết: [`docs/reviews/GHE2_TU_DONG.md`](docs/reviews/GHE2_TU_DONG.md).
