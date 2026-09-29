# SỔ NỢ VI HIẾN

Vi phạm Luật Kiến trúc Tối cao **đã biết nhưng chưa sửa**. Hệ thống **chưa đạt** các điều dưới đây; không được
tuyên bố khác đi. Nguồn: `docs/reviews/2026-09-30-ra-soat-kien-truc.md` (Ghế 1 tự rà — cần ghế khác xác nhận),
Issue #2.

| Mã | Điều | Mức | Vi phạm | Trạng thái |
|---|---|---|---|---|
| V1 | 9 | BLOCKING | Cổng nâng kỹ năng dùng Brier tuyệt đối, không so tỷ lệ nền → dự đoán hiển nhiên vẫn qua cổng. | MỞ |
| V2 | 6 | BLOCKING | `adjudicate` chỉ kiểm mã phiên khác nhau, không kiểm khác nhà cung cấp; danh tính phiên tự khai. | MỞ |
| V3 | 7 | BLOCKING | Dự đoán và kết quả có thể vào cùng một commit → không chứng minh được "đoán trước". | MỞ |
| V4 | 7 | MAJOR | Cấp bằng chứng của bài học do người viết tự khai, không suy từ sổ. | MỞ |
| V5 | 8 | MAJOR | `brain/providers.json` (điểm AI, champion) và `brain/state.json` sửa tay, không có lịch sử kiểm được. | MỞ |
| V6 | 12 | MAJOR | Hai PR cùng ghi thêm vào một sổ chuỗi băm sẽ gãy chuỗi khi merge; chưa có công cụ xếp lại. | MỞ |
| V7 | 10, 14 | MAJOR | `inquiry`, `focus`, `domains` không nối với sổ; chưa có vòng khép kín mục đích → bài học. | MỞ |
| V8 | 7 | MINOR | Hạn chấm so theo ngày UTC, lệch giờ Việt Nam ở ranh giới ngày. | MỞ |
| V9 | 13 | MINOR | Nợ Issue #2: P1, P2, P3 (docstring `lessons.py` mô tả STALE sai), ý 13. | MỞ |
| V10 | 4 | MINOR | Bảng §3 CONSTITUTION ghép chi phần → luật trong mã. | **ĐÃ SỬA** (ADR 0001) |
