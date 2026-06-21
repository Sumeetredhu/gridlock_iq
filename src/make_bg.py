"""Generate the blue 'blueprint / design-canvas' background for the pitch deck."""
import math
from PIL import Image, ImageDraw, ImageFilter
import config as C

W, H = 2400, 1350


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def run():
    top, bot = (43, 121, 240), (15, 58, 140)         # vivid blue gradient
    img = Image.new("RGB", (W, H))
    px = img.load()
    for y in range(H):
        c = lerp(top, bot, y / H)
        for x in range(W):
            px[x, y] = c

    # radial glow top-right
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W * 0.45, -H * 0.5, W * 1.25, H * 0.7], fill=120)
    glow = glow.filter(ImageFilter.GaussianBlur(180))
    img = Image.composite(Image.new("RGB", (W, H), (90, 150, 255)), img, glow)

    d = ImageDraw.Draw(img, "RGBA")
    # fine grid
    step = 48
    for x in range(0, W, step):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 26), width=1)
    for y in range(0, H, step):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 26), width=1)
    # major grid
    for x in range(0, W, step * 5):
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 46), width=2)
    for y in range(0, H, step * 5):
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 46), width=2)

    # diagonal light streaks (screen)
    streak = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(streak)
    for off, a, w in [(W * 0.55, 60, 120), (W * 0.68, 36, 60)]:
        sd.line([(off, -50), (off - 500, H + 50)], fill=(255, 255, 255, a), width=w)
    streak = streak.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img.convert("RGBA"), streak).convert("RGB")

    # vignette
    vg = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vg)
    vd.rectangle([0, 0, W, H], fill=0)
    vd.rectangle([90, 90, W - 90, H - 90], fill=255)
    vg = vg.filter(ImageFilter.GaussianBlur(160))
    dark = Image.new("RGB", (W, H), (10, 30, 80))
    img = Image.composite(img, dark, vg)

    out = C.ASSETS / "bg_blue.png"
    img.save(out, quality=92)
    print("[bg] wrote", out)


if __name__ == "__main__":
    run()
