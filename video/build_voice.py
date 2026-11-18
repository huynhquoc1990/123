"""Build the Vietnamese voiceover + the video timeline that fits it.

Writes:
  timing.js      -> scene/tour durations read by index.html
  out/voice.wav  -> voice track placed on the timeline (44.1 kHz stereo)
  out/timeline.json
Usage: python3 build_voice.py
Model: voices/vi_VN-vais1000-medium.onnx (Piper, CC-BY-4.0 VAIS-1000 dataset)
Text is written phonetically where needed so the TTS reads English terms the Vietnamese way.
"""
import json, os, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
MODEL = os.environ.get('VOICE_MODEL', os.path.join(ROOT, 'voices', 'vi_VN-vais1000-medium.onnx'))
CACHE = os.path.join(ROOT, 'out', 'vo_cache')
LENGTH_SCALE = float(os.environ.get('VOICE_SPEED', '0.92'))  # < 1 = faster
os.makedirs(CACHE, exist_ok=True)
BRAND = 'Kiu Ây Ga'  # how "QA-GAS" is read aloud

# ---- Script: (scene, local start seconds, text) -----------------------------------------
SCRIPT = {
    's1': [(0.35, 'Nhà máy của bạn đang tiêu thụ bao nhiêu điện, ngay lúc này?'),
           (3.6, 'Đo lường. Giám sát. Điều khiển.')],
    's2': [(0.5, f'Giới thiệu bộ ai ô ti gết uê, e ét pi ba hai, của {BRAND}. '
                 'Thu thập dữ liệu và điều khiển công nghiệp, đưa mọi thiết bị trong nhà máy lên đám mây.')],
    's4': [(0.4, 'Mạnh mẽ, linh hoạt, bền bỉ. Tất cả trong một thiết bị nhỏ gọn.')],
    's5': [(0.5, 'Ứng dụng thứ nhất: thu thập dữ liệu điện năng. '
                 'Gết uê đọc điện áp, dòng điện, công suất và điện năng tiêu thụ từ các đồng hồ điện, '
                 'rồi gửi lên đám mây theo thời gian thực.'),
           ('alert', 'Khi phụ tải vượt ngưỡng, hệ thống cảnh báo ngay lập tức.')],
    's6': [(0.5, 'Ứng dụng thứ hai: giám sát ai ô ti nhà máy. Theo dõi trạng thái từng máy, đếm sản lượng suốt hai mươi bốn giờ.'),
           ('stop', 'Máy dừng đột ngột? Cảnh báo được gửi ngay, rơ le kích hoạt còi báo từ xa.')],
    's7': [(0.4, 'Vỏ hộp gắn thanh ray đin, lắp gọn trong tủ điện, đấu nối nhanh chóng.')],
    's8': [(0.4, f'Biến dữ liệu thành tiết kiệm. {BRAND}, giải pháp ai ô ti cho nhà máy của bạn. '
                 'Liên hệ ngay để được tư vấn.')],
}
# Hardware tour: one line per stop (overview + 8 parts, same order as STOPS in index.html)
TOUR = [
    'Chỉ một bo mạch nhỏ gọn, tích hợp đầy đủ kết nối công nghiệp.',
    'Vi xử lý e ét pi ba hai, lõi kép, có oai phai, blu tút và ăng ten ngoài cho sóng ổn định.',
    'Cổng mạng i tơ nét có dây, ổn định cho hạ tầng nhà máy.',
    'Cổng a ét bốn tám lăm, giao thức mốt bớt, đọc đồng hồ điện, biến tần và cảm biến.',
    'Bốn ngõ vào số cách ly quang, đọc trạng thái máy và đếm sản phẩm.',
    'Bốn rơ le mười am pe có chống xung, bật tắt thiết bị từ xa.',
    'Đồng hồ thời gian thực và thẻ nhớ, lưu dữ liệu ngay cả khi mất mạng.',
    'Nguồn một chiều công nghiệp, cổng u ét bi xi để nạp chương trình.',
    'Và sẵn sàng mở rộng mạng bốn gờ.',
]

# ---- default (minimum) durations, must match index.html defaults ------------------------
OVL = 0.4
MIN_DUR = {'s1': 6.2, 's2': 6.5, 's4': 6.4, 's5': 14.4, 's6': 13.4, 's7': 7.4, 's8': 8.2}
TOUR_T0, TOUR_STEP, TOUR_TR = 2.6, 2.55, 0.85
TOUR_LEAD = 0.45           # voice starts this long after a stop's camera move begins
EVENT = {'alert': ('s5', 11.0), 'stop': ('s6', 6.2)}  # named cue points inside scenes
TAIL = 0.6


def synth(text):
    key = f'{abs(hash((text, LENGTH_SCALE))) % 10**12}.wav'
    path = os.path.join(CACHE, key)
    if not os.path.exists(path):
        subprocess.run(['python3', '-m', 'piper', '-m', MODEL, '--length-scale', str(LENGTH_SCALE),
                        '--sentence-silence', '0.18', '-f', path], input=text.encode(), check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(path) as w:
        sr = w.getframerate(); x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32768
    # trim leading/trailing silence
    nz = np.where(np.abs(x) > 0.01)[0]
    x = x[max(0, nz[0] - int(.02 * sr)): nz[-1] + int(.08 * sr)] if len(nz) else x
    return x, sr


segs = []  # (scene, local_t, audio, sr)
for sc, items in SCRIPT.items():
    for t, text in items:
        a, sr = synth(text)
        if isinstance(t, str):
            sc2, t = EVENT[t]
            assert sc2 == sc
        segs.append([sc, t, a, sr, text])

# tour durations
tour_audio = [synth(x) for x in TOUR]
tour = []
for i, (a, sr) in enumerate(tour_audio):
    L = len(a) / sr
    if i == 0:
        tour.append(max(TOUR_T0, 0.6 + L + 0.35))
    else:
        tour.append(max(TOUR_STEP, TOUR_LEAD + L + 0.45))
last_hold = tour[-1]
s3_dur = sum(tour) + 0.4

# scene durations: each scene must outlast its voice
dur = dict(MIN_DUR); dur['s3'] = s3_dur
for sc, t, a, sr, _ in segs:
    dur[sc] = max(dur[sc], t + len(a) / sr + TAIL + OVL)
order = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
start, t = {}, 0.0
for sc in order:
    start[sc] = t
    t += dur[sc] - OVL
total = start['s8'] + dur['s8']

# place voice
SR = 44100
N = int(total * SR) + SR
track = np.zeros(N, np.float32)

def place(a, sr, at):
    if sr != SR:
        a = np.interp(np.arange(int(len(a) * SR / sr)) * sr / SR, np.arange(len(a)), a).astype(np.float32)
    i = int(at * SR)
    track[i:i + len(a)] += a[: N - i]

placed = []
for sc, lt, a, sr, text in segs:
    place(a, sr, start[sc] + lt); placed.append((round(start[sc] + lt, 2), round(len(a) / sr, 2), text))
acc = 0.0
for i, (a, sr) in enumerate(tour_audio):
    at = start['s3'] + (0.6 if i == 0 else acc + TOUR_LEAD)
    place(a, sr, at); placed.append((round(at, 2), round(len(a) / sr, 2), TOUR[i]))
    acc += tour[i]

track /= max(1e-6, np.abs(track).max()); track *= 0.89
stereo = np.repeat((track * 32767).astype('<i2')[:, None], 2, 1)
with wave.open(os.path.join(ROOT, 'out', 'voice.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(stereo.tobytes())

timing = {'scenes': {k: [round(start[k], 3), round(start[k] + dur[k], 3)] for k in order},
          'tour': [round(x, 3) for x in tour], 'duration': round(total, 3)}
with open(os.path.join(ROOT, 'timing.js'), 'w') as f:
    f.write('window.TIMING = ' + json.dumps(timing) + ';\n')
with open(os.path.join(ROOT, 'out', 'timeline.json'), 'w') as f:
    json.dump({'timing': timing, 'voice': sorted(placed)}, f, ensure_ascii=False, indent=1)
print(json.dumps(timing, indent=1))
for p in sorted(placed): print(p[0], p[1], p[2][:60])
