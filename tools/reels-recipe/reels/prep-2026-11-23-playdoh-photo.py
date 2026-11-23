"""Ritu's Play-Doh solar-system photo (up-c25648bca95f978f): level the board (perspective warp onto a 4:5 rectangle), tight crop,
white balance off the white dough strips, even out the light, lift shadows, a little more colour, light denoise + gentle sharpen.
Outputs: playdoh-solar-post.jpg (800x1000, for the app post, under its 300k data-URL cap) and playdoh-solar-board.jpg (1100x1380, Reel)."""
import base64
import os

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src", "playdoh-original.jpg")
# board corners fitted to its four edges, pulled 2.5% toward the centre to drop the rounded corners and the mat's rim
CORNERS = [(72.6, 138.3), (538.3, 133.6), (581.0, 808.4), (-5.0, 791.0)]   # TL TR BR BL
INSET = 0.975


def warp(im, size):
    cx = sum(p[0] for p in CORNERS) / 4
    cy = sum(p[1] for p in CORNERS) / 4
    q = [(cx + INSET * (x - cx), cy + INSET * (y - cy)) for x, y in CORNERS]
    return im.transform(size, Image.QUAD, (*q[0], *q[3], *q[2], *q[1]), Image.BICUBIC)   # quad order: TL BL BR TR


def white_balance(im):
    px = im.load()
    w, h = im.size
    acc, n = [0, 0, 0], 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b = px[x, y]
            if min(r, g, b) > 170 and max(r, g, b) - min(r, g, b) < 70 and r >= b:   # a bright, near-white strip
                acc[0] += r
                acc[1] += g
                acc[2] += b
                n += 1
    mean = [a / n for a in acc]
    grey = sum(mean) / 3
    gains = [min(1.18, max(0.85, grey / m)) for m in mean]
    print("white pixels", n, [round(m) for m in mean], "gains", [round(g, 3) for g in gains])
    return Image.merge("RGB", [c.point(lambda v, k=k: min(255, v * k)) for c, k in zip(im.split(), gains)])


def even_light(im):
    y, cb, cr = im.convert("YCbCr").split()
    blur = y.filter(ImageFilter.GaussianBlur(im.size[0] // 7))
    mean = sum(blur.getdata()) / (im.size[0] * im.size[1])
    flat = [min(255, int(a * min(1.3, max(0.8, mean / max(b, 1))) ** 0.7)) for a, b in zip(y.getdata(), blur.getdata())]
    y2 = Image.new("L", im.size)
    y2.putdata(flat)
    return Image.merge("YCbCr", (y2, cb, cr)).convert("RGB")


def tone(im):
    lut = [min(255, int(255 * ((v / 255) ** 0.82))) for v in range(256)]      # lift shadows and mids
    return ImageOps.autocontrast(im.point(lut * 3), cutoff=0.15)


def finish(im):
    im = ImageEnhance.Color(im).enhance(1.12)
    im = Image.blend(im, im.filter(ImageFilter.MedianFilter(3)), 0.5)
    return im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=65, threshold=2))


src = ImageOps.exif_transpose(Image.open(SRC)).convert("RGB")
board = finish(tone(even_light(white_balance(warp(src, (1100, 1380))))))
board.save(os.path.join(HERE, "playdoh-solar-board.jpg"), quality=93)
post = board.resize((800, 1000), Image.LANCZOS)
for q in (90, 86, 82, 78, 74, 70):
    out = os.path.join(HERE, "playdoh-solar-post.jpg")
    post.save(out, quality=q, optimize=True)
    with open(out, "rb") as f:
        n = len("data:image/jpeg;base64,") + len(base64.b64encode(f.read()))
    print(q, n)
    if n <= 285000:
        break
