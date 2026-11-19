# Video quy trình thực tế – cấp phát nhiên liệu (dọc 9:16)

**File:** `out/quy_trinh_thuc_te.mp4` · 1080×1920 · ~42 giây · nhạc nền + âm thanh thật tại trụ.
Dựng từ `src/quay_thuc_te.mov` (quay màn hình app + quay tại trụ bơm).

| Đoạn | Nội dung |
|---|---|
| Mở đầu | Logo · "Quy trình thực tế – Cấp phát nhiên liệu bằng phiếu QR" |
| Bước 1 | Tài xế tạo đề nghị (tua nhanh, có ghi chú "tua nhanh") → đã gửi 20 lít cho quản lý |
| Bước 2 | Quản lý nhận thông báo, xem hạn mức & lịch sử xe → duyệt |
| Bước 3 | Quét mã QR tại trụ bơm (quay thật) |
| Kết | Logo · lợi ích · "Liên hệ ngay để được tư vấn" |

Sửa đoạn cắt / tốc độ / chữ trong `SEGMENTS` của `build.py`, số liên hệ ở `CONTACT`, rồi chạy `python3 build.py`
(cần ffmpeg, Pillow; nhạc lấy từ `../video_capphat/music.py`).
