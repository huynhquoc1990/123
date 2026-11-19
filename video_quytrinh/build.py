"""Edit the real screen/phone recording into a vertical (1080x1920) demo video with captions, logo and music.

Usage: python3 build.py            -> out/quy_trinh_thuc_te.mp4
Source: src/quay_thuc_te.mov (886x1920): 0-52.4s screen recording of the app, 52.4-62s camera at the pump.
Edit the SEGMENTS list to change cuts, speed or captions.
"""
import os, subprocess, json, shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src', 'quay_thuc_te.mov')
TMP = os.path.join(ROOT, 'tmp'); OUT = os.path.join(ROOT, 'out')
os.makedirs(TMP, exist_ok=True); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1080, 1920, 30
F = '/usr/share/fonts/opentype/inter/Inter-%s.otf'
font = lambda w, s: ImageFont.truetype(F % w, s)
CONTACT = ''  # e.g. 'Hotline/Zalo: 09xx xxx xxx' - shown on the last card when set
LOGO = Image.open(os.path.join(ROOT, 'src', 'logo_qa.png')).convert('RGBA')

# (kind, src_start, src_end, speed, step_label, title, subtitle)
SCREEN, CAMERA = 'screen', 'camera'
T1, T2, T3 = 'Tài xế tạo đề nghị', 'Quản lý phê duyệt', 'Quét mã QR tại trụ bơm'
SEGMENTS = [
    (SCREEN, 6.0, 14.0, 3.0, 'BƯỚC 1 / 3', T1, 'Mở ứng dụng trên điện thoại'),
    (SCREEN, 14.0, 33.6, 1.6, 'BƯỚC 1 / 3', T1, 'Chọn xe · nhập số lít · mục đích'),
    (SCREEN, 33.6, 35.8, 1.0, 'BƯỚC 1 / 3', T1, '✓ Đã gửi đề nghị 20 lít cho quản lý'),
    (SCREEN, 44.0, 47.8, 1.2, 'BƯỚC 2 / 3', T2, 'Nhận thông báo: 1 đề nghị chờ duyệt'),
    (SCREEN, 47.8, 52.35, 1.0, 'BƯỚC 2 / 3', T2, 'Xem hạn mức, lịch sử xe → Duyệt'),
    (CAMERA, 52.45, 61.9, 1.0, 'BƯỚC 3 / 3', T3, 'Trụ đọc phiếu, hiện biển số & số lít được cấp'),
]
INTRO, OUTRO = 2.6, 4.8
BOX_Y, BOX_H = 430, 1370  # video area


def bg():
    im = Image.new('RGB', (W, H), '#06111f')
    glow = Image.new('RGB', (W, H), '#06111f'); d = ImageDraw.Draw(glow)
    d.ellipse((-300, -200, 800, 800), fill='#0f3a66'); d.ellipse((500, 1300, 1400, 2200), fill='#0b3b3a')
    return Image.blend(im, glow.filter(ImageFilter.GaussianBlur(220)), .8)


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f); d.text(((W - w) / 2, y), text, font=f, fill=fill)


def logo(im, h, xy):
    lg = LOGO.resize((round(LOGO.width * h / LOGO.height), h), Image.LANCZOS)
    pad = max(6, h // 14)
    card = Image.new('RGBA', (lg.width + 2 * pad, lg.height + 2 * pad), (0, 0, 0, 0))
    ImageDraw.Draw(card).rounded_rectangle((0, 0, card.width - 1, card.height - 1), radius=pad * 2, fill='white')
    card.alpha_composite(lg, (pad, pad))
    x, y = xy if xy[0] >= 0 else ((W - card.width) // 2, xy[1])
    im.paste(card, (x, y), card)
    return card.size


def frame_png(path, step, title, sub, vw, fast):
    im = bg(); d = ImageDraw.Draw(im)
    # step chip
    f = font('Bold', 30); tw = d.textlength(step, font=f)
    d.rounded_rectangle(((W - tw) / 2 - 26, 70, (W + tw) / 2 + 26, 124), radius=27, fill='#0c2a4a', outline='#38bdf8', width=2)
    centered(d, 80, step, f, '#7dd3fc')
    centered(d, 150, title, font('ExtraBold', 66), 'white')
    centered(d, 252, sub, font('SemiBold', 38), '#4ade80' if sub.startswith('✓') else '#cfe0f5')
    # progress dots
    k = int(step.split()[1])
    for i in range(3):
        x = W / 2 - 60 + i * 60
        d.rounded_rectangle((x - 22, 340, x + 22, 348), radius=4, fill='#38bdf8' if i < k else '#1f3756')
    # video frame shadow + border
    x0 = (W - vw) // 2
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, BOX_Y + 20, x0 + vw, BOX_Y + BOX_H + 20), radius=40, fill=(0, 0, 0, 170))
    im.paste(sh.filter(ImageFilter.GaussianBlur(30)), (0, 0), sh.filter(ImageFilter.GaussianBlur(30)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x0 - 4, BOX_Y - 4, x0 + vw + 4, BOX_Y + BOX_H + 4), radius=42, outline='#2a4568', width=3)
    # footer
    sz = logo(im, 64, (300, 1828))
    d.text((300 + sz[0] + 22, 1838), 'Quốc Anh Gas', font=font('ExtraBold', 30), fill='white')
    d.text((300 + sz[0] + 22, 1874), 'Cấp phát nhiên liệu nội bộ', font=font('Medium', 22), fill='#93a9c6')
    im.save(path)
    # overlay badge (drawn over the video)
    if fast:
        b = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        txt = f'▶▶ tua nhanh x{fast:g}'; f = font('Bold', 26); tw = bd.textlength(txt, font=f)
        bd.rounded_rectangle((x0 + vw - tw - 52, BOX_Y + 22, x0 + vw - 20, BOX_Y + 72), radius=25, fill=(6, 17, 31, 210))
        bd.text((x0 + vw - tw - 36, BOX_Y + 30), txt, font=f, fill='#fbbf24')
        b.save(path.replace('.png', '_badge.png'))


def mask_png(path, w, h, r=40):
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), radius=r, fill=255); m.save(path)


def card_png(path, outro):
    im = bg(); d = ImageDraw.Draw(im)
    logo(im, 300, (-1, 300 if not outro else 230))
    if not outro:
        centered(d, 760, 'QUY TRÌNH THỰC TẾ', font('Bold', 40), '#38bdf8')
        centered(d, 830, 'Cấp phát nhiên liệu', font('ExtraBold', 84), 'white')
        centered(d, 935, 'bằng phiếu QR', font('ExtraBold', 84), '#4ade80')
        centered(d, 1080, 'Đề nghị → Phê duyệt → Bơm tại trụ', font('SemiBold', 40), '#cfe0f5')
    else:
        centered(d, 690, 'QUỐC ANH GAS', font('Black', 88), 'white')
        centered(d, 800, 'Hệ thống cấp phát nhiên liệu nội bộ', font('SemiBold', 42), '#cfe0f5')
        y = 920
        for line in ('✓ Trụ tự bơm đúng số lít đã duyệt', '✓ In biên lai ngay tại trụ', '✓ Dữ liệu đồng bộ lên đám mây'):
            centered(d, y, line, font('Bold', 44), '#4ade80'); y += 78
        f = font('ExtraBold', 44); t = 'Liên hệ ngay để được tư vấn'; tw = d.textlength(t, font=f)
        d.rounded_rectangle(((W - tw) / 2 - 50, 1215, (W + tw) / 2 + 50, 1315), radius=50, fill='#0ea5e9')
        centered(d, 1238, t, f, 'white')
        if CONTACT: centered(d, 1370, CONTACT, font('Bold', 46), 'white')
    im.save(path)


def run(args):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error'] + args, check=True)


ENC = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '19', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-an']
parts, t, marks = [], 0.0, []

# intro
card_png(f'{TMP}/intro.png', False)
run(['-loop', '1', '-t', str(INTRO), '-i', f'{TMP}/intro.png', '-vf', f'fade=in:st=0:d=0.4,fade=out:st={INTRO - .3}:d=0.3', *ENC, f'{TMP}/p00.mp4'])
parts.append(f'{TMP}/p00.mp4'); t += INTRO

for i, (kind, a, b, sp, step, title, sub) in enumerate(SEGMENTS, 1):
    if kind == SCREEN:
        vw = round(886 * BOX_H / 1920 / 2) * 2; crop = ''
    else:
        vw = round(886 * BOX_H / 1576 / 2) * 2; crop = 'crop=886:1576:0:172,'
    png = f'{TMP}/bg{i}.png'; frame_png(png, step, title, sub, vw, sp if sp > 1 else 0)
    mask_png(f'{TMP}/m{i}.png', vw, BOX_H)
    x0 = (W - vw) // 2
    fc = (f'[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{sp},{crop}scale={vw}:{BOX_H},fps={FPS},format=rgba[v];'
          f'[2:v]format=gray[m];[v][m]alphamerge[vm];[1:v][vm]overlay={x0}:{BOX_Y}:shortest=1')
    inputs = ['-i', SRC, '-loop', '1', '-i', png, '-loop', '1', '-i', f'{TMP}/m{i}.png']
    if sp > 1:
        inputs += ['-loop', '1', '-i', png.replace('.png', '_badge.png')]; fc += '[o];[o][3:v]overlay=0:0:shortest=1'
    dur = (b - a) / sp
    fade = []
    if i == 1 or SEGMENTS[i - 2][4] != step: fade.append('fade=in:st=0:d=0.25')
    if i == len(SEGMENTS) or SEGMENTS[i][4] != step: fade.append(f'fade=out:st={dur - .25:.3f}:d=0.25')
    if fade: fc += ',' + ','.join(fade)
    out = f'{TMP}/p{i:02}.mp4'
    run([*inputs, '-filter_complex', fc, '-t', f'{dur:.3f}', *ENC, out])
    marks.append((kind, step, round(t, 2), round(dur, 2), a))
    parts.append(out); t += dur

card_png(f'{TMP}/outro.png', True)
n = len(parts)
run(['-loop', '1', '-t', str(OUTRO), '-i', f'{TMP}/outro.png', '-vf', f'fade=in:st=0:d=0.4,fade=out:st={OUTRO - .6}:d=0.6', *ENC, f'{TMP}/p{n:02}.mp4'])
parts.append(f'{TMP}/p{n:02}.mp4'); outro_at = t; t += OUTRO

with open(f'{TMP}/parts.txt', 'w') as f:
    f.write('\n'.join(f"file '{p}'" for p in parts))
run(['-f', 'concat', '-safe', '0', '-i', f'{TMP}/parts.txt', '-c', 'copy', f'{TMP}/silent.mp4'])

# music follows the edit: s2 = end of intro, s4/s5/s6 = step changes, s7/s8 = outro
step_at = {}
for kind, step, at, dur, a in marks: step_at.setdefault(step, at)
sc = {'s1': 0, 's2': INTRO, 's3': INTRO + .2, 's4': step_at['BƯỚC 1 / 3'] + 8, 's5': step_at['BƯỚC 2 / 3'],
      's6': step_at['BƯỚC 3 / 3'], 's7': outro_at, 's8': outro_at + .2}
with open(f'{TMP}/timing.js', 'w') as f:
    f.write('window.TIMING = ' + json.dumps({'scenes': {k: [v, v + 1] for k, v in sc.items()}, 'duration': t}) + ';')
subprocess.run(['python3', os.path.join(ROOT, '..', 'video_capphat', 'music.py'), f'{TMP}/music.wav', str(t), f'{TMP}/timing.js'], check=True)

# ambient sound of the camera clip, placed where it plays
cam = [m for m in marks if m[0] == CAMERA][0]
final = os.path.join(OUT, 'quy_trinh_thuc_te.mp4')
run(['-i', f'{TMP}/silent.mp4', '-i', f'{TMP}/music.wav', '-ss', str(cam[4]), '-t', str(cam[3]), '-i', SRC,
     '-filter_complex', f'[1:a]volume=0.55[m];[2:a]highpass=f=80,volume=0.9,adelay={int(cam[2] * 1000)}|{int(cam[2] * 1000)}[c];'
     '[m][c]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-15:TP=-1.5:LRA=11,aresample=44100[a]',
     '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', final])
shutil.rmtree(TMP)
print('Done ->', final, f'{t:.1f}s')
