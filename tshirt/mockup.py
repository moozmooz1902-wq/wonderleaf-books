#!/usr/bin/env python3
"""Their own product photo, cleaned to a blank tee, plus a compositor.

Base is listing 101812 from the seller's catalogue (eBay's 1600px original,
not the 500px thumbnail): black crew neck, ghost mannequin, white ground -
the template most of the catalogue is shot on. Its small chest print is
patched out with clean garment lifted from lower down the same shirt, so
the lighting and fold shading carry over.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SRC = "mock_1600.webp"
BLANK = "BLANK_TEE.png"

# measured off the coordinate grid
BODY_L, BODY_R = 292, 1312          # measured: torso between the sleeves
COLLAR_Y       = 190          # neckline bottom, read off the grid
PRINT_BOX      = (400, 320, 1200, 620)   # the print being removed


def make_blank():
    im = Image.open(SRC).convert("RGB")
    x0, y0, x1, y1 = PRINT_BOX
    h = y1 - y0
    # lift clean garment from below the print, same x range so the horizontal
    # shading profile matches, and slide it up over the artwork
    patch = im.crop((x0, y0 + h + 140, x1, y1 + h + 140))
    mask = Image.new("L", (x1 - x0, h), 255)
    d = ImageDraw.Draw(mask)
    d.rectangle([0, 0, x1 - x0 - 1, h - 1], outline=0, width=2)
    mask = mask.filter(ImageFilter.GaussianBlur(26))     # feather the seam
    im.paste(patch, (x0, y0), mask)
    im.save(BLANK)
    return im


# ---------------------------------------------------------------- placement
# Chest, not belly: the print sits just under the collar, centred on the torso.
PRINT_W   = int((BODY_R - BODY_L) * 0.46)      # ~418px  - the smaller print
PRINT_CX  = (BODY_L + BODY_R) // 2             # 725
PRINT_TOP = COLLAR_Y + 60                      # chest, just under the collar


def place(design, base=None):
    """design: RGBA artwork on transparent. Returns the finished mockup."""
    tee = (base or Image.open(BLANK)).convert("RGBA").copy()
    w = PRINT_W
    h = int(design.height * (w / design.width))
    art = design.resize((w, h), Image.LANCZOS)
    tee.alpha_composite(art, (PRINT_CX - w // 2, PRINT_TOP))
    return tee.convert("RGB")


if __name__ == "__main__":
    make_blank()
    im = Image.open(BLANK)
    d = ImageDraw.Draw(im)
    d.rectangle([PRINT_CX - PRINT_W//2, PRINT_TOP,
                 PRINT_CX + PRINT_W//2, PRINT_TOP + int(PRINT_W*0.75)],
                outline=(255, 0, 0), width=4)
    im.save("BLANK_TEE_guide.png")
    print("wrote", BLANK, "and BLANK_TEE_guide.png")
