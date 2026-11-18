"""Prepare video images from assets/src: blur third-party silkscreen branding on the board photos,
then derive the cropped board and blurred background images."""
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import os
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

# (x0, y0, x1, y1) boxes in the 1500x2000 source images
BLUR = {
    'board_top.jpg': [(878, 1022, 978, 1158), (578, 1022, 708, 1058)],
    'side_view.jpg': [(522, 952, 612, 1048), (788, 1018, 918, 1048)],
}

def blur_boxes(im, boxes, pad=14, radius=16):
    out = im.copy()
    for x0, y0, x1, y1 in boxes:
        bx = (x0 - pad * 3, y0 - pad * 3, x1 + pad * 3, y1 + pad * 3)
        region = im.crop(bx)
        b = region.filter(ImageFilter.GaussianBlur(radius)).filter(ImageFilter.GaussianBlur(radius))
        b = ImageEnhance.Brightness(b).enhance(.75)
        mask = Image.new('L', region.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((pad * 2, pad * 2, region.width - pad * 2, region.height - pad * 2), radius=pad, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(pad / 1.5))
        out.paste(b, bx[:2], mask)
    return out

for name, boxes in BLUR.items():
    blur_boxes(Image.open(os.path.join(D, 'src', name)).convert('RGB'), boxes).save(os.path.join(D, name), quality=90)

Image.open(os.path.join(D, 'board_top.jpg')).crop((300, 850, 1270, 1680)).save(os.path.join(D, 'board_crop.jpg'), quality=90)
b = Image.open(os.path.join(D, 'src', 'board_antenna.jpg')).resize((960, 1280)).filter(ImageFilter.GaussianBlur(18))
ImageEnhance.Brightness(b).enhance(.45).save(os.path.join(D, 'bg_blur.jpg'), quality=85)
print('assets ready')
