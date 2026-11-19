# Video giới thiệu – Hệ thống cấp phát nhiên liệu nội bộ thông minh (Quốc Anh Gas)

Video ~113 giây, Full HD 1920×1080, 30 fps, **giọng đọc tiếng Việt** + nhạc nền tự tổng hợp (không vướng bản quyền).

**File video:** `out/he_thong_cap_phat_nhien_lieu.mp4` · Phụ đề: `out/phu_de.srt` · Thời điểm từng câu: `out/timeline.json`

## Kịch bản
| Cảnh | Nội dung |
|---|---|
| 1 | Vấn đề: hàng nghìn lít dầu mỗi tháng — có cấp đúng xe, đúng người, đúng hạn mức? Ghi sổ thủ công, bơm sai số lít, khó đối soát |
| 2 | Giới thiệu hệ thống (ảnh trụ bơm thật) |
| 3 | Quy trình 4 bước (ảnh chụp app thật): 1 Đề nghị → 2 Phê duyệt → 3 Phiếu QR |
| 4 | Bước 4 tại trụ: quét QR → màn hình bơm đếm 0 → 18,5 L rồi tự ngắt → in biên lai, đồng bộ máy chủ |
| 5 | Trụ bơm thông minh (7 điểm): tủ thép, đầu đọc QR, màn hình cảm ứng, máy in nhiệt, bộ đếm số cơ, ăng-ten, cụm bơm + bo điều khiển RS485 |
| 6 | Phần mềm quản trị: nhiều công ty/chi nhánh, hạn mức theo kỳ, phê duyệt, tồn bồn, đối soát theo ca, lịch sử bơm |
| 7 | Năng lực sản xuất: gia công tủ → lắp ráp → hoàn thiện |
| 8 | Lợi ích + logo Quốc Anh Gas + lời kêu gọi liên hệ |

## Chỉnh sửa & render lại
Cần: Node + Playwright, ffmpeg, Python (numpy, Pillow, `pip install piper-tts`).

1. Giọng đọc (Piper `vi_VN-vais1000-medium`, dữ liệu VAIS-1000 – CC BY 4.0), tải vào `voices/`:
   ```bash
   curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-vi_VN-vais1000-medium.tar.bz2 | tar xj
   cp vits-piper-vi_VN-vais1000-medium/vi_VN-vais1000-medium.onnx* voices/
   ```
2. Lời thoại: sửa `SCENES` trong `build_voice.py` (cách đọc từ khó ở `SAY`), chạy `python3 build_voice.py`
   → `out/voice.wav`, `timing.js`, `out/phu_de.srt` (thời lượng cảnh tự giãn theo lời).
3. Ảnh gốc ở `assets/src/`; `python3 prep_assets.py` cắt/thu nhỏ ảnh dùng trong video.
4. Hình ảnh/chữ: `index.html` (số hotline cuối video: hằng `CONTACT`, đang để trống). Nhạc: `music.py`.
5. Render: `node render.cjs` (xem trước: `node render.cjs --stills 5,45,60`).
