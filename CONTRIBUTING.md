# CỬA CHUNG — ChatGPT · Claude · Gemini · Grok

Bốn AI cùng đóng góp **qua Pull Request**, không ai ghi thẳng vào `main`.

## Luật
1. **Một PR = một phiên AI.** Ghi rõ `provider` và `session` trong mô tả PR.
2. **Không tự duyệt.** PR của phiên A phải được phiên B (khác phiên) phản biện trong review, và Owner hoặc phiên C chốt merge.
3. Một AI đóng bốn vai trong cùng một phiên **không** được tính là bốn người độc lập.
4. Mọi thay đổi luật lõi (`minhtri/`, `CONSTITUTION.md`) phải kèm kiểm thử và giữ CI xanh.
5. Không sửa dòng cũ trong `brain/ledger/` — sổ chỉ ghi thêm. CI kiểm chuỗi băm.
6. Không thêm mã có quyền hành động ngoài đời (đăng, chi tiền, giao dịch).
7. Phát biểu trong PR phải gắn loại: FACT / OBSERVATION / INFERENCE / HYPOTHESIS / PREDICTION / OPINION / UNKNOWN.

## Quy trình
```
Owner mở Issue (giao việc)
  → AI #1 (phiên s1) mở PR đề xuất
  → AI #2 (phiên s2) review: phản chứng, giả định, lỗi nhân quả, điểm mù
  → AI #1 trả lời / sửa
  → Trọng tài (Owner hoặc AI phiên s3) quyết: ACCEPT / NEEDS_TEST / REJECT
  → merge khi CI xanh
```

## Phản biện có đọc đề benchmark
Phiên phản biện nào đọc nội dung đề trong `benchmarks/` thì provider đó bị ghi vào `exposed_to` của đề và **không được thi đề đó**. Người phản biện không bao giờ được xem tệp đáp án.
