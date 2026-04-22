from PIL import Image, ImageDraw, ImageFont
import os

FONT_BOLD   = "C:/Windows/Fonts/arialbd.ttf"
FONT_NARROW = "C:/Windows/Fonts/ARIALNB.TTF"
FONT_REG    = "C:/Windows/Fonts/arial.ttf"

BG     = (10, 10, 15)
PINK   = (236, 55, 124)   # #EC377C
MID    = (248, 97, 92)    # #F8615C
ORANGE = (254, 120, 75)   # #FE784B
WHITE  = (255, 255, 255)

SIZES = {
    "drawable-port-mdpi":    (320, 480),
    "drawable-port-hdpi":    (480, 800),
    "drawable-port-xhdpi":   (720, 1280),
    "drawable-port-xxhdpi":  (960, 1600),
    "drawable-port-xxxhdpi": (1280, 1920),
    "drawable-land-mdpi":    (480, 320),
    "drawable-land-hdpi":    (800, 480),
    "drawable-land-xhdpi":   (1280, 720),
    "drawable-land-xxhdpi":  (1600, 960),
    "drawable-land-xxxhdpi": (1920, 1280),
    "drawable":              (320, 480),
}

BASE_DIR = "android/app/src/main/res"


def lerp_color(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient_color(t):
    if t < 0.5:
        return lerp_color(PINK, MID, t * 2)
    else:
        return lerp_color(MID, ORANGE, (t - 0.5) * 2)


def make_gradient_stripe_mask(w, h, x_frac, width_frac):
    """Returns an RGBA image with the stripe shape filled white (alpha mask)."""
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    stripe_w = int(w * width_frac)
    x0 = int(w * x_frac)
    slope = h / w
    pts = [
        (x0, 0),
        (x0 + stripe_w, 0),
        (x0 + stripe_w - int(h / slope), h),
        (x0 - int(h / slope), h),
    ]
    md.polygon(pts, fill=200)
    return mask


def make_splash(w, h):
    img = Image.new("RGB", (w, h), BG)

    # Subtle radial glow at top (pink)
    glow = Image.new("RGB", (w, h), BG)
    gd = ImageDraw.Draw(glow)
    glow_r = int(min(w, h) * 0.9)
    cx = w // 2
    steps = 40
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(glow_r * t)
        alpha_col = lerp_color(BG, (236, 55, 124), (1 - t) * 0.12)
        gd.ellipse([cx - r, -r // 2, cx + r, r // 2], fill=alpha_col)
    img = Image.blend(img, glow, 0.6)

    # Horizontal gradient for the stripes
    grad_h = Image.new("RGB", (w, h))
    gd2 = ImageDraw.Draw(grad_h)
    for x in range(w):
        t = x / max(w - 1, 1)
        col = gradient_color(t)
        gd2.line([(x, 0), (x, h)], fill=col)

    # Main stripe
    mask1 = make_gradient_stripe_mask(w, h, 0.55, 0.065)
    stripe1 = Image.new("RGB", (w, h), BG)
    stripe1.paste(grad_h, mask=mask1)
    img = Image.composite(stripe1, img, mask1)

    # Thin secondary stripe
    mask2 = make_gradient_stripe_mask(w, h, 0.635, 0.022)
    stripe2 = Image.new("RGB", (w, h), BG)
    stripe2.paste(grad_h, mask=mask2)
    img = Image.composite(stripe2, img, mask2)

    draw = ImageDraw.Draw(img)
    scale = min(w, h) / 480.0

    cy = h * 0.42

    # "FORZA" — white bold
    sz_forza = max(12, int(90 * scale))
    try:
        font_forza = ImageFont.truetype(FONT_BOLD, sz_forza)
    except Exception:
        font_forza = ImageFont.load_default()

    bb = draw.textbbox((0, 0), "FORZA", font=font_forza)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    tx = (w - tw) / 2
    ty = cy - th / 2
    draw.text((tx, ty), "FORZA", fill=WHITE, font=font_forza)
    text_bottom = ty + th

    # Gradient separator line (drawn pixel by pixel)
    line_h = max(2, int(3 * scale))
    line_pad = int(tw * 0.05)
    line_y = int(text_bottom + 6 * scale)
    line_x0 = int(tx + line_pad)
    line_x1 = int(tx + tw - line_pad)
    for x in range(line_x0, line_x1):
        t = (x - line_x0) / max(line_x1 - line_x0 - 1, 1)
        col = gradient_color(t)
        draw.line([(x, line_y), (x, line_y + line_h)], fill=col)

    # "GALLERY" — orange, letter-spaced
    sz_gallery = max(8, int(28 * scale))
    try:
        font_gallery = ImageFont.truetype(FONT_NARROW, sz_gallery)
    except Exception:
        font_gallery = ImageFont.load_default()

    bb2 = draw.textbbox((0, 0), "G A L L E R Y", font=font_gallery)
    gw, gh = bb2[2] - bb2[0], bb2[3] - bb2[1]
    gx = (w - gw) / 2
    gy = line_y + line_h + int(10 * scale)
    draw.text((gx, gy), "G A L L E R Y", fill=ORANGE, font=font_gallery)
    gallery_bottom = gy + gh

    # Tagline — salmon/mid
    sz_tag = max(6, int(13 * scale))
    try:
        font_tag = ImageFont.truetype(FONT_REG, sz_tag)
    except Exception:
        font_tag = ImageFont.load_default()

    bb3 = draw.textbbox((0, 0), "COMUNIDAD FORZA HORIZON", font=font_tag)
    tagx = (w - (bb3[2] - bb3[0])) / 2
    tagy = gallery_bottom + int(18 * scale)
    draw.text((tagx, tagy), "COMUNIDAD FORZA HORIZON", fill=(*MID, 180), font=font_tag)

    # Two thin gradient lines at bottom
    line2_y = int(h * 0.88)
    lw = int(w * 0.55)
    lx = (w - lw) // 2
    for x in range(lx, lx + lw):
        t = (x - lx) / max(lw - 1, 1)
        col = gradient_color(t)
        draw.line([(x, line2_y), (x, line2_y + max(1, int(1.5 * scale)))], fill=(*col, 140))
        draw.line([(x, line2_y + max(4, int(6 * scale))), (x, line2_y + max(5, int(7.5 * scale)))], fill=(*col, 80))

    return img


def main():
    res_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), BASE_DIR)
    for folder, (w, h) in SIZES.items():
        out_dir = os.path.join(res_dir, folder)
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "splash.png")
        img = make_splash(w, h)
        img.save(out_path, "PNG", optimize=True)
        print(f"  {folder}/splash.png  ({w}×{h})")
    print("Done.")


if __name__ == "__main__":
    main()
