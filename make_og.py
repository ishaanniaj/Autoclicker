#!/usr/bin/env python3
"""Draw the social-share / Open Graph preview image -> docs/og-image.png (1200x630)."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

# gradient background (brand blue -> indigo)
top, bot = (79, 157, 255), (106, 92, 255)
px = img.load()
for y in range(H):
    t = y / (H - 1)
    c = tuple(int(top[i] + (bot[i] - top[i]) * t) for i in range(3))
    for x in range(W):
        px[x, y] = c + (255,)

draw = ImageDraw.Draw(img)


def font(size):
    for n in ("/System/Library/Fonts/SFNS.ttf",
              "/System/Library/Fonts/Supplemental/Arial.ttf"):
        try:
            return ImageFont.truetype(n, size)
        except OSError:
            pass
    return ImageFont.load_default()


# app icon on the left (icon_1024.png already has rounded corners)
icon = Image.open("icon_1024.png").convert("RGBA").resize((300, 300))
img.paste(icon, (110, 165), icon)

# text block on the right
tx = 470
draw.text((tx, 210), "AutoClicker", font=font(96), fill="white",
          stroke_width=1, stroke_fill="white")
draw.text((tx, 310), "for Mac", font=font(96), fill="white",
          stroke_width=1, stroke_fill="white")
draw.text((tx, 440), "Free auto clicker · Apple Silicon",
          font=font(34), fill=(233, 238, 255))

img.convert("RGB").save("docs/og-image.png")
print("wrote docs/og-image.png")
