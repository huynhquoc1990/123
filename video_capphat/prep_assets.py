"""Prepare the images used by index.html from assets/src (crop / resize / blurred backgrounds)."""
from PIL import Image, ImageFilter, ImageEnhance
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
src = lambda n: Image.open(os.path.join(D, 'src', n)).convert('RGB')

def save(im, name, long_side=None, q=88):
    if long_side and max(im.size) > long_side:
        r = long_side / max(im.size)
        im = im.resize((round(im.width * r), round(im.height * r)), Image.LANCZOS)
    im.save(os.path.join(D, name), quality=q)
    print(name, im.size)

# photos (sources are 1932x2576)
save(src('tru_bom_front.jpg'), 'hero.jpg')                               # full res: the tour zooms in deep
save(src('tru_bom_front2.jpg'), 'hero2.jpg', 1600)
save(src('in_bien_lai.jpg'), 'print.jpg', 1600)
save(src('lap_rap.jpg').crop((0, 0, 1690, 2576)), 'assembly.jpg', 1600)  # crop away the technician
save(src('khung_tu.jpg').crop((0, 560, 1932, 2576)), 'frame.jpg', 1600)  # crop away the person behind
save(src('ben_trong.jpg'), 'inside.jpg', 1600)
save(src('cum_bom.jpg'), 'pump.jpg')
save(src('bo_mach.jpg'), 'board.jpg')

# app screenshots (1260x2736): drop the phone status bar
for n in ('app_home', 'app_qr', 'app_tong_hop', 'app_landing'):
    save(src(n + '.png').crop((0, 205, 1260, 2736)), n + '.jpg', 1400, q=92)

# blurred dark backdrop
b = src('tru_bom_front.jpg').resize((480, 640)).crop((0, 140, 480, 410)).resize((1920, 1080))
b = b.filter(ImageFilter.GaussianBlur(26))
ImageEnhance.Brightness(b).enhance(.35).save(os.path.join(D, 'bg_blur.jpg'), quality=85)
print('assets ready')
