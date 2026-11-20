# DraveKaraoke - icoon (Pillow): microfoon met muzieknootjes, Dravenlock-paars
import os
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
S = 1024
im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
d = ImageDraw.Draw(im)
d.rounded_rectangle((40, 40, S - 40, S - 40), 210, fill=(22, 19, 31, 255), outline=(127, 119, 221, 255), width=34)
gloed = Image.new("RGBA", (S, S), (0, 0, 0, 0)); g = ImageDraw.Draw(gloed)
g.ellipse((300, 170, 620, 560), fill=(181, 156, 255, 150)); gloed = gloed.filter(ImageFilter.GaussianBlur(60)); im.alpha_composite(gloed)
d = ImageDraw.Draw(im)
# microfoon-kop (schuin)
kop = Image.new("RGBA", (S, S), (0, 0, 0, 0)); k = ImageDraw.Draw(kop)
k.rounded_rectangle((350, 190, 590, 520), 120, fill=(181, 156, 255, 255), outline=(240, 236, 255, 255), width=14)
for y in range(250, 480, 46):
    k.line((375, y, 565, y), fill=(127, 100, 210, 255), width=10)
k.rectangle((350, 470, 590, 520), fill=(127, 100, 210, 255))
k.rounded_rectangle((440, 520, 500, 830), 30, fill=(90, 80, 120, 255), outline=(200, 190, 240, 255), width=10)
kop = kop.rotate(-28, center=(470, 520), resample=Image.BICUBIC)
im.alpha_composite(kop)
d = ImageDraw.Draw(im)
# muzieknootjes (turquoise en geel)
def noot(x, y, kl, s=1.0):
    d.ellipse((x, y, x + 70 * s, y + 52 * s), fill=kl)
    d.rectangle((x + 58 * s, y - 150 * s, x + 72 * s, y + 26 * s), fill=kl)
    d.polygon([(x + 72 * s, y - 150 * s), (x + 135 * s, y - 115 * s), (x + 135 * s, y - 80 * s), (x + 72 * s, y - 112 * s)], fill=kl)
noot(660, 420, (94, 224, 200, 255), 1.15)
noot(720, 700, (255, 220, 90, 255), 0.95)
noot(180, 690, (255, 130, 170, 255), 0.85)
im.save(os.path.join(HERE, "assets", "icon_256.png"), sizes=None) if False else im.resize((256, 256), Image.LANCZOS).save(os.path.join(HERE, "assets", "icon_256.png"))
im.save(os.path.join(HERE, "assets", "icon.ico"), format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
im.resize((192, 192), Image.LANCZOS).save(os.path.join(HERE, "web", "icon.png"))
print("icoon klaar")
