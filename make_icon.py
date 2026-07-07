#!/usr/bin/env python3
"""Draw the Autoclicker app icon (cursor + click ripples) to icon_1024.png."""
from PIL import Image, ImageDraw

S = 1024
img = Image.new("RGBA", (S, S), (0, 0, 0, 0))

# --- rounded-rect background with a vertical blue->indigo gradient ---
top = (79, 157, 255)      # #4f9dff
bot = (106, 92, 255)      # #6a5cff
grad = Image.new("RGBA", (S, S))
gd = grad.load()
for y in range(S):
    t = y / (S - 1)
    r = int(top[0] + (bot[0] - top[0]) * t)
    g = int(top[1] + (bot[1] - top[1]) * t)
    b = int(top[2] + (bot[2] - top[2]) * t)
    for x in range(S):
        gd[x, y] = (r, g, b, 255)

mask = Image.new("L", (S, S), 0)
ImageDraw.Draw(mask).rounded_rectangle([48, 48, S - 48, S - 48],
                                       radius=200, fill=255)
img.paste(grad, (0, 0), mask)

draw = ImageDraw.Draw(img)

# --- click ripples emanating from the cursor tip ---
tip = (398, 372)
for radius, alpha, width in [(150, 150, 20), (230, 90, 16), (310, 45, 12)]:
    bbox = [tip[0] - radius, tip[1] - radius, tip[0] + radius, tip[1] + radius]
    # a partial arc on the upper-left, like a click "pulse"
    draw.arc(bbox, start=150, end=320, fill=(255, 255, 255, alpha), width=width)

# --- classic arrow cursor, white with a dark outline ---
# base shape with tip at (0,0), pointing up-left, ~100 unit box
base = [(0, 0), (0, 74), (20, 57), (33, 88), (46, 82), (33, 51), (58, 51)]
scale = 5.4
cursor = [(tip[0] + px * scale, tip[1] + py * scale) for px, py in base]
draw.polygon(cursor, fill=(255, 255, 255, 255),
             outline=(24, 34, 62, 255))
# thicken the outline for crispness at large sizes
draw.line(cursor + [cursor[0]], fill=(24, 34, 62, 255), width=10, joint="curve")

img.save("icon_1024.png")
print("wrote icon_1024.png")
