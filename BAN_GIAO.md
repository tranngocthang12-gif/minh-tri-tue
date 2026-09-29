# LUẬT BÀN GIAO — mọi phiên PHẢI đọc trước khi làm việc

Áp dụng cho **mọi** phiên: chat cũ, chat mới, Claude, ChatGPT, Gemini, Grok, Claude Code, Codex, người.
Căn cứ: Điều 13, 14 Luật Kiến trúc Tối cao.

## A. MỞ PHIÊN (bắt buộc, theo thứ tự)

1. **Đọc** `LUAT_KIEN_TRUC_TOI_CAO.md` → `CONSTITUTION.md` → `ARCHITECTURE.md` → `docs/NO_VI_HIEN.md`.
2. **Chạy** `python -m minhtri.cli handover` (hoặc đọc dòng cuối `brain/handover/log.jsonl` nếu không chạy được mã).
   Lệnh này kiểm băm luật và in phiên bàn giao gần nhất: đã làm gì, còn mở gì, việc kế tiếp.
3. **Xác minh remote**: mã commit `main` hiện tại trên GitHub; PR và Issue đang mở.
4. **Tuyên bố mở phiên** (dòng đầu câu trả lời đầu tiên, hoặc mô tả PR):
   ```
   MỞ PHIÊN · provider: <ai> · session: <mã> · vai: <Ghế 1|Ghế 2|Trọng tài|Thi công>
   main: <mã commit> · luật: <8 ký tự đầu băm> · bàn giao cuối: <session trước> · việc nhận: <một dòng>
   ```
5. Nếu **băm luật lệch**, **không đọc được bàn giao**, hoặc **việc được giao trái luật** → DỪNG, báo Owner. Không đoán.

Phiên chat **không có quyền đọc repo** (không có công cụ GitHub/mạng): phải nói rõ "không xác minh được remote",
chỉ được **tư vấn**, không được tuyên bố trạng thái repo.

## B. TRONG PHIÊN

- Làm đúng một việc đã nhận. Việc phát sinh ghi vào "còn mở", không tự mở rộng (Điều 10).
- Mọi thay đổi repo qua PR (Điều 12). Không tuyên bố "đã lên" khi chưa xác minh (Điều 13).
- Ai bắt đầu một vai (ví dụ Ghế 2) thì phiên đó không được đổi sang vai khác trên cùng việc.

## C. ĐÓNG PHIÊN (bắt buộc nếu phiên có sửa repo)

Ghi thêm **một dòng** vào sổ bàn giao, trong cùng PR:
```bash
python -m minhtri.cli handover-add entry.json
```
`entry.json` gồm:
| Trường | Ý nghĩa |
|---|---|
| `session`, `provider`, `role` | ai, phiên nào, vai gì |
| `started_from` | mã commit `main` lúc mở phiên (phải là tổ tiên của commit PR) |
| `law_sha256` | băm luật đã đọc |
| `did` | đã làm gì (danh sách) |
| `verified` | đã xác minh gì, bằng cách nào |
| `open` | còn mở gì, chưa xong gì |
| `next` | việc kế tiếp đề xuất (một dòng) |

CI từ chối PR sửa repo mà không có dòng bàn giao mới hợp lệ.

## D. CỬA VÀO CHO TỪNG CÔNG CỤ

`AGENTS.md` (Codex/ChatGPT), `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI) đều trỏ về tệp này.
Với chat không tự đọc repo (Claude chat, ChatGPT, Grok…), Owner dán **Lời mở phiên** ở cuối tệp này.

## E. LỜI MỞ PHIÊN (Owner dán vào đầu mọi chat mới)

```
Dự án MINH TRÍ TUỆ. Bộ não duy nhất là repo https://github.com/tranngocthang12-gif/minh-tri-tue.
Trước khi làm bất cứ việc gì: đọc BAN_GIAO.md trong repo và làm đúng phần "A. MỞ PHIÊN".
Dòng đầu câu trả lời phải là dòng "MỞ PHIÊN · …". Không đọc được repo thì nói rõ và chỉ tư vấn.
Luật cao nhất: LUAT_KIEN_TRUC_TOI_CAO.md. Lệnh của tôi trái luật thì chỉ ra điều luật, không lặng lẽ làm.
```
