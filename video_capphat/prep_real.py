"""Extract the real footage (../video_quytrinh/src/quay_thuc_te.mov) into JPEG frame sequences used by index.html.

  assets/real/a_####.jpg  step 1: driver creates the request (screen recording 16.0-35.8 s)
  assets/real/b_####.jpg  step 2: manager approves (screen recording 44.0-52.35 s)
  assets/real/c_####.jpg  at the pump: QR shown to the reader (camera 52.45-61.9 s)
Frames are 30 fps; the page picks the frame for each video time (see REAL in index.html).
"""
import os, subprocess, shutil
ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, '..', 'video_quytrinh', 'src', 'quay_thuc_te.mov')
D = os.path.join(ROOT, 'assets', 'real')
shutil.rmtree(D, ignore_errors=True); os.makedirs(D)
CUTS = {  # name: (start, end, filter)
    'a': (16.0, 35.8, 'crop=886:1845:0:75,scale=400:-2'),   # drop the phone status bar
    'b': (44.0, 52.35, 'crop=886:1845:0:75,scale=400:-2'),
    'c': (52.45, 61.9, 'crop=886:1576:0:172,scale=720:-2'),
}
for k, (a, b, vf) in CUTS.items():
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', str(a), '-t', f'{b - a:.3f}', '-i', SRC,
                    '-vf', f'fps=30,{vf}', '-q:v', '4', os.path.join(D, f'{k}_%04d.jpg')], check=True)
    print(k, len([f for f in os.listdir(D) if f.startswith(k + '_')]), 'frames')
