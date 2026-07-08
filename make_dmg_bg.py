#!/usr/bin/env python3
"""Draw the DMG window background (drag-to-Applications arrow) to dmg_bg.png."""
from PIL import Image, ImageDraw, ImageFont

W, H = 640, 420
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# soft vertical gradient background
top, bot = (247, 249, 252), (233, 238, 246)
px = img.load()
for y in range(H):
    t = y / (H - 1)
    c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    for x in range(W):
        px[x, y] = c + (255,)

draw = ImageDraw.Draw(img)


def font(size, bold=False):
    names = (["/System/Library/Fonts/SFNS.ttf"] if not bold
             else ["/System/Library/Fonts/SFNS.ttf"])
    for n in names:
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default()


def center_text(y, text, size, fill, bold=False):
    f = font(size, bold)
    w = draw.textlength(text, font=f)
    draw.text(((W - w) / 2, y), text, font=f, fill=fill)


# title + hint (kept clear of the icon row at y~180)
center_text(46, "Install Autoclicker", 30, (28, 34, 48))
center_text(342, "Drag the app onto the Applications folder", 16, (120, 128, 140))

# big arrow from the app (left, x~160) toward Applications (right, x~480)
ay = 180
x0, x1 = 258, 388
col = (90, 120, 220)
draw.line([(x0, ay), (x1, ay)], fill=col, width=14)
draw.polygon([(x1 - 6, ay - 26), (x1 + 30, ay), (x1 - 6, ay + 26)], fill=col)

img.save("dmg_bg.png")
print("wrote dmg_bg.png")
