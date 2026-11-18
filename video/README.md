# Video giới thiệu – QA-GAS IoT Gateway ESP32-S3

Video ~100 giây, Full HD 1920×1080, 30 fps, **giọng đọc tiếng Việt** + nhạc nền (tự tổng hợp, không vướng bản quyền).
Logo QA-GAS (Quốc Anh); chữ ZENO PCB in trên bo mạch đã được làm mờ.

**File video:** `out/qa_gas_iot_gateway.mp4` · Thời điểm từng câu thoại: `out/timeline.json`

## Kịch bản
| Cảnh | Nội dung |
|---|---|
| 1 | Mở đầu: "Nhà máy của bạn đang tiêu thụ bao nhiêu điện — ngay lúc này?" → Đo lường. Giám sát. Điều khiển. |
| 2 | Ra mắt sản phẩm: IoT Gateway ESP32-S3 |
| 3 | Khám phá phần cứng (8 điểm): ESP32-S3 + anten, Ethernet, RS485, 4 DI, 4 Relay, RTC + MicroSD, nguồn + USB-C, LTE |
| 4 | Thông số nổi bật |
| 5 | Ứng dụng 1: Thu thập dữ liệu điện năng |
| 6 | Ứng dụng 2: Giám sát IoT nhà máy |
| 7 | Vỏ hộp DIN-rail |
| 8 | Lợi ích + logo QA-GAS |

## Chỉnh sửa & render lại
Cần: Node + Playwright, ffmpeg, Python (numpy, Pillow, `pip install piper-tts`).

1. Giọng đọc (Piper, giọng `vi_VN-vais1000-medium`, dữ liệu VAIS-1000 – CC BY 4.0). Tải model vào `voices/`:
   ```bash
   curl -L https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-vi_VN-vais1000-medium.tar.bz2 | tar xj
   cp vits-piper-vi_VN-vais1000-medium/vi_VN-vais1000-medium.onnx* voices/
   ```
2. Sửa lời thoại trong `build_voice.py` (`SCRIPT`, `TOUR`; cách đọc tên thương hiệu ở `BRAND`), rồi chạy
   `python3 build_voice.py` → tạo `out/voice.wav` và `timing.js` (thời lượng cảnh tự giãn theo lời thoại).
3. Ảnh: ảnh gốc nằm ở `assets/src/`; `python3 prep_assets.py` làm mờ chữ trên bo và tạo ảnh dùng trong video.
4. Hình ảnh/chữ trên màn hình: `index.html`. Nhạc: `music.py`.
5. Render: `node render.cjs` (xem trước: `node render.cjs --stills 5,20,45`).
