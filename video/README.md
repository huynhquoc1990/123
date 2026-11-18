# Video giới thiệu – ZENO IoT Gateway ESP32-S3

Video 82 giây, Full HD 1920×1080, 30 fps, có nhạc nền (tự tổng hợp, không vướng bản quyền).

**File video:** `out/zeno_iot_gateway.mp4`

## Kịch bản
| Thời gian | Cảnh |
|---|---|
| 0–6s | Mở đầu: "Nhà máy của bạn đang tiêu thụ bao nhiêu điện — ngay lúc này?" → Đo lường. Giám sát. Điều khiển. |
| 6–12s | Ra mắt sản phẩm: IoT Gateway ESP32-S3 |
| 12–35s | Khám phá phần cứng (8 điểm): ESP32-S3 + anten, Ethernet, RS485, 4 DI, 4 Relay, RTC + MicroSD, nguồn + USB-C, LTE |
| 35–41s | Thông số nổi bật |
| 41–55s | Ứng dụng 1: Thu thập dữ liệu điện năng (đồng hồ điện → RS485 → Gateway → Cloud → Dashboard) |
| 55–68s | Ứng dụng 2: Giám sát IoT nhà máy (trạng thái máy, đếm sản lượng, cảnh báo, relay từ xa, OEE) |
| 68–75s | Vỏ hộp DIN-rail |
| 75–82s | Lợi ích + thương hiệu ZENO PCB / zenopcb.vn |

## Chỉnh sửa & render lại
- Nội dung, chữ, thời lượng từng cảnh: sửa trong `index.html` (mảng `SCENES`, `STOPS`, và từng khối `S1`…`S8`).
- Nhạc nền: `music.py`.
- Render (cần Node + Playwright + ffmpeg + Python/numpy):
  ```bash
  node render.cjs                    # render video đầy đủ -> out/zeno_iot_gateway.mp4
  node render.cjs --stills 5,20,45   # xuất ảnh xem trước tại các giây chỉ định
  ```
