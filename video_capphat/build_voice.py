"""Build the Vietnamese voiceover and the timeline that fits it.

Writes:
  timing.js         -> scene start/end + per-line cue times, read by index.html and music.py
  out/voice.wav     -> voice track placed on the timeline (44.1 kHz stereo)
  out/timeline.json -> when each line is spoken
  out/phu_de.srt    -> Vietnamese subtitles (on-screen spelling, not the phonetic TTS spelling)
Usage: python3 build_voice.py
Model: voices/vi_VN-vais1000-medium.onnx (Piper, VAIS-1000 dataset, CC BY 4.0) - see README.md
"""
import json, os, subprocess, wave, hashlib
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get('VOICE_MODEL', os.path.join(ROOT, 'voices', 'vi_VN-vais1000-medium.onnx'))
CACHE = os.path.join(ROOT, 'out', 'vo_cache')
LENGTH_SCALE = float(os.environ.get('VOICE_SPEED', '0.93'))  # < 1 = faster
os.makedirs(CACHE, exist_ok=True)

# How words are read aloud (TTS) vs. written in the subtitles.
SAY = {'Quốc Anh Gas': 'Quốc Anh Ga', 'mã QR': 'mã kiu a', 'RS485': 'a ét bốn tám lăm', 'Toshiba': 'Tô si ba',
       'Tatsuno': 'Tát su nô', 'Shibata': 'Si ba ta', '50 đến 70': 'năm mươi đến bảy mươi', '±0,3%': 'cộng trừ không phẩy ba phần trăm',
       '4G': 'bốn gờ', 'Wi-Fi': 'oai phai', 'mô-tơ': 'mô tơ'}

# ---- Script ------------------------------------------------------------------------------
# scene: (minimum duration, first-line delay, [(text, minimum slot before the next line)])
OVL = 0.5   # crossfade between scenes
GAP = 0.35  # silence between lines
TAIL = 0.7  # silence after the last line of a scene
SCENES = {
    's1': (9.0, 0.5, [
        ('Mỗi tháng, đội xe của doanh nghiệp tiêu thụ hàng nghìn lít dầu.', 3.6),
        ('Nhưng từng lít có được cấp đúng xe, đúng người, đúng hạn mức?', 3.4),
        ('Ghi sổ thủ công, bơm sai số lít, cuối ca khó đối soát.', 3.0)]),
    's2': (9.0, 0.6, [
        ('Giới thiệu hệ thống cấp phát nhiên liệu nội bộ thông minh của Quốc Anh Gas.', 3.5),
        ('Mỗi lần bơm đều có phiếu mã QR, kiểm soát hạn mức và đối soát tự động.', 3.0)]),
    's3': (8.0, 0.5, [
        ('Quy trình chỉ gồm bốn bước.', 2.3),
        ('Bước một: tài xế tạo đề nghị cấp phát trên điện thoại. Hệ thống tự kiểm tra hạn mức còn lại của từng xe.', 8.4),
        ('Bước hai: người quản lý phê duyệt số lít ngay trên ứng dụng. Các đề nghị được tổng hợp theo biển số xe.', 6.4),
        ('Bước ba: tài xế nhận phiếu mã QR, ghi rõ biển số, loại nhiên liệu, số lít và thời hạn hiệu lực.', 4.0)]),
    's4': (8.0, 0.5, [
        ('Bước bốn: đưa mã QR vào đầu đọc trên trụ bơm. Trụ nhận phiếu, hiện biển số và số lít được cấp.', 6.2),
        ('Trụ tự động bơm đúng số lít đã duyệt, rồi dừng lại.', 6.2),
        ('Biên lai được in ngay tại trụ, dữ liệu đồng bộ về máy chủ theo thời gian thực.', 4.0)]),
    's5': (8.0, 0.6, [  # hardware tour: one line per stop (same order as STOPS in index.html)
        ('Trụ bơm thông minh được tích hợp trọn bộ trong tủ thép sơn tĩnh điện, có khóa an toàn.', 3.0),
        ('Đầu đọc mã QR nhận phiếu cấp phát chỉ trong tích tắc.', 3.0),
        ('Màn hình cảm ứng hiển thị số lít, thành tiền, đơn giá và tồn bồn.', 3.0),
        ('Máy in nhiệt in biên lai cho từng lần bơm.', 3.0),
        ('Bộ đếm số cơ, đối chiếu độc lập với số liệu điện tử.', 3.0),
        ('Ăng ten giữ kết nối liên tục với máy chủ.', 3.0),
        ('Bên trong là mô-tơ bơm Toshiba, bộ đo lường Tatsuno hoặc Shibata và bo điều khiển, giao tiếp qua cổng RS485.', 3.0)]),
    's5b': (8.0, 0.5, [  # technical specifications
        ('Thông số kỹ thuật: mô-tơ bơm Toshiba, bộ đo lường Tatsuno hoặc Shibata, lưu lượng từ 50 đến 70 lít mỗi phút, sai số chỉ ±0,3%.', 6.0),
        ('Kết nối 4G và Wi-Fi, toàn bộ dữ liệu được quản trị trên nền tảng đám mây.', 3.0)]),
    's6': (8.0, 0.5, [
        ('Hệ quản trị đám mây, truy cập mọi lúc trên máy tính và điện thoại.', 3.0),
        ('Quản lý nhiều công ty, nhiều chi nhánh. Đặt hạn mức theo kỳ cho từng xe và tài xế.', 3.5),
        ('Phê duyệt đề nghị, theo dõi tồn bồn, và đối soát số lít với số cơ theo từng ca.', 3.5)]),
    's7': (7.5, 0.5, [
        ('Từ khung tủ, lắp ráp cơ khí đến lập trình phần mềm, tất cả do Quốc Anh Gas thực hiện trọn gói.', 3.0)]),
    's8': (12.0, 0.5, [
        ('Chống thất thoát. Minh bạch từng lít dầu. Tiết kiệm thời gian cho đội xe.', 4.6),
        ('Quốc Anh Gas, hệ thống cấp phát nhiên liệu nội bộ thông minh. Liên hệ ngay để được tư vấn.', 3.0)]),
}


def spoken(text):
    for k, v in SAY.items():
        text = text.replace(k, v)
    return text


def synth(text):
    key = hashlib.md5(f'{text}|{LENGTH_SCALE}'.encode()).hexdigest()[:16] + '.wav'
    path = os.path.join(CACHE, key)
    if not os.path.exists(path):
        subprocess.run(['python3', '-m', 'piper', '-m', MODEL, '--length-scale', str(LENGTH_SCALE),
                        '--sentence-silence', '0.2', '-f', path], input=text.encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(path) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
    nz = np.where(np.abs(x) > 0.01)[0]  # trim leading/trailing silence
    x = x[max(0, nz[0] - int(.02 * sr)): nz[-1] + int(.08 * sr)] if len(nz) else x
    return x, sr


# ---- lay out lines inside scenes, then scenes on the timeline ----------------------------
cues, lens, dur, audio = {}, {}, {}, {}
for sc, (mind, lead, lines) in SCENES.items():
    t, cs, ls, au = lead, [], [], []
    for i, (text, slot) in enumerate(lines):
        a, sr = synth(spoken(text))
        L = len(a) / sr
        cs.append(round(t, 3)); ls.append(round(L, 3)); au.append((a, sr, text))
        t = max(t + slot, t + L + GAP) if i < len(lines) - 1 else t + max(L, slot)
    cues[sc], lens[sc], audio[sc] = cs, ls, au
    dur[sc] = max(mind, cs[-1] + ls[-1] + TAIL + OVL)

order = list(SCENES)
start, t = {}, 0.0
for sc in order:
    start[sc] = t
    t += dur[sc] - OVL
total = start[order[-1]] + dur[order[-1]]

SR = 44100
N = int(total * SR) + SR
track = np.zeros(N, np.float32)
placed = []
for sc in order:
    for c, (a, sr, text) in zip(cues[sc], audio[sc]):
        if sr != SR:
            a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a).astype(np.float32)
        at = start[sc] + c
        i = int(at * SR)
        track[i:i + len(a)] += a[: N - i]
        placed.append((round(at, 2), round(len(a) / SR, 2), text))

track /= max(1e-6, np.abs(track).max()); track *= 0.89
stereo = np.repeat((track * 32767).astype('<i2')[:, None], 2, 1)
with wave.open(os.path.join(ROOT, 'out', 'voice.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())

timing = {'scenes': {k: [round(start[k], 3), round(start[k] + dur[k], 3)] for k in order},
          'cues': cues, 'lens': lens, 'duration': round(total, 3)}
with open(os.path.join(ROOT, 'timing.js'), 'w') as f:
    f.write('window.TIMING = ' + json.dumps(timing) + ';\n')
with open(os.path.join(ROOT, 'out', 'timeline.json'), 'w') as f:
    json.dump({'timing': timing, 'voice': placed}, f, ensure_ascii=False, indent=1)


def ts(x):
    ms = int(round(x * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

with open(os.path.join(ROOT, 'out', 'phu_de.srt'), 'w') as f:
    for n, (at, L, text) in enumerate(placed, 1):
        f.write(f'{n}\n{ts(at)} --> {ts(at + L + 0.25)}\n{text}\n\n')

print(json.dumps({k: timing['scenes'][k] for k in order}), 'total', round(total, 2))
for p in placed: print(p[0], p[1], p[2][:70])
