
from math import cos, pi, sin
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "images"
SIZE = (1800, 1100)


def lerp(a, b, t):
    return int(a + (b - a) * t)


def gradient(width, height, stops):
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        ty = y / max(height - 1, 1)
        for x in range(width):
            tx = x / max(width - 1, 1)
            t = (tx * 0.58 + ty * 0.42)
            left = stops[0]
            right = stops[-1]
            for i in range(len(stops) - 1):
                a_pos = i / (len(stops) - 1)
                b_pos = (i + 1) / (len(stops) - 1)
                if a_pos <= t <= b_pos:
                    local = (t - a_pos) / (b_pos - a_pos)
                    left = stops[i]
                    right = stops[i + 1]
                    t = local
                    break
            pixels[x, y] = tuple(lerp(left[c], right[c], t) for c in range(3))
    return image


def add_noise(image, amount, seed):
    random.seed(seed)
    width, height = image.size
    noise = Image.new("L", image.size)
    data = [random.randrange(0, amount) for _ in range(width * height)]
    noise.putdata(data)
    color = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(image, color, 0.08)


def glow_layer(size, shapes, blur):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for shape in shapes:
        draw.ellipse(shape["box"], fill=shape["fill"])
    return layer.filter(ImageFilter.GaussianBlur(blur))


def draw_geometry(draw, width, height, cx, cy, radius, color, rings=5, sides=12):
    for r in range(rings):
        rr = radius * (1 - r * 0.16)
        points = []
        for i in range(sides):
            angle = -pi / 2 + i * pi * 2 / sides
            points.append((cx + cos(angle) * rr, cy + sin(angle) * rr))
        draw.line(points + [points[0]], fill=color, width=2)
        if r % 2 == 0:
            for i in range(0, sides, 2):
                draw.line((cx, cy, points[i][0], points[i][1]), fill=color, width=1)
    for i in range(sides + 8):
        angle = i * pi * 2 / (sides + 8)
        x = cx + cos(angle) * radius * 0.7
        y = cy + sin(angle) * radius * 0.7
        draw.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color)


def draw_starfield(draw, width, height, seed, count=260):
    random.seed(seed)
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, int(height * 0.52))
        r = random.randint(1, 4)
        alpha = random.randint(80, 220)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(255, 220, 140, alpha))


def draw_peak(draw, width, height, seed, base_height, color, highlight):
    points = [(0, height), (0, base_height + 40)]
    peak = int(width * 0.5)
    for i in range(1, 9):
        px = int(width * i / 9)
        offset = int(sin((i + seed * 0.17) * 1.2) * 78) + random.randint(0, 68)
        py = base_height - offset
        points.append((px, py))
    points.append((width, height))
    draw.polygon(points, fill=color)
    draw.line(points, fill=highlight, width=3)


def draw_halo(draw, cx, cy, radius, color, rings=4):
    for i in range(rings):
        rr = radius * (1 - i * 0.18)
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=color, width=2)
        if i % 2 == 0:
            for j in range(8):
                angle = j * pi * 2 / 8
                sx = cx + cos(angle) * rr * 0.82
                sy = cy + sin(angle) * rr * 0.82
                ex = cx + cos(angle) * rr * 1.06
                ey = cy + sin(angle) * rr * 1.06
                draw.line((sx, sy, ex, ey), fill=color, width=1)


def draw_hero_silhouette(draw, cx, cy, size):
    body_top = cy - size * 0.9
    body_bottom = cy + size * 0.4
    head_radius = int(size * 0.12)
    draw.rectangle((cx - 7, body_top, cx + 7, body_bottom), fill=(14, 14, 18, 255))
    draw.ellipse((cx - head_radius, body_top - head_radius * 2, cx + head_radius, body_top), fill=(14, 14, 18, 255))
    draw.line((cx, body_top + 18, cx - 20, body_top + 62), fill=(14, 14, 18, 255), width=7)
    draw.line((cx, body_top + 18, cx + 20, body_top + 62), fill=(14, 14, 18, 255), width=7)
    draw.line((cx, body_bottom - 18, cx - 24, body_bottom + 18), fill=(14, 14, 18, 255), width=7)
    draw.line((cx, body_bottom - 18, cx + 24, body_bottom + 18), fill=(14, 14, 18, 255), width=7)


def get_subject_theme(filename):
    lower = filename.lower()
    if "path" in lower:
        return "path"
    if "questions" in lower:
        return "questions"
    if "consciousness" in lower:
        return "consciousness"
    if "community" in lower:
        return "community"
    if "outreach" in lower:
        return "outreach"
    if "book" in lower:
        return "book"
    if "hidden" in lower:
        return "hidden"
    if "hero" in lower or "purpose" in lower:
        return "hero"
    return "hero"


def apply_subject_theme(draw, width, height, theme, accent, secondary, seed):
    random.seed(seed + 11)
    cx = int(width * 0.52)
    cy = int(height * 0.36)
    if "path" in theme:
        path_color = (*accent, 120)
        for i in range(6):
            start = (int(width * 0.08), int(height * (0.6 - i * 0.04)))
            end = (int(width * (0.5 + i * 0.08)), int(height * (0.25 + i * 0.02)))
            draw.line((start, end), fill=path_color, width=18 - i * 2)
        for i in range(14):
            x = random.randint(int(width * 0.22), int(width * 0.92))
            y = random.randint(int(height * 0.55), int(height * 0.95))
            draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(*secondary, 142))
    elif "consciousness" in theme:
        for i in range(5):
            radius = int(width * (0.12 + i * 0.06))
            draw.arc((cx - radius, cy - radius, cx + radius, cy + radius), 50, 330, fill=(*secondary, 65 + i * 20), width=3)
        for i in range(7):
            angle = random.uniform(0, pi * 2)
            x = cx + cos(angle) * (150 + i * 18)
            y = cy + sin(angle) * (95 + i * 14)
            draw.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(*accent, 140))
    elif "community" in theme:
        for i in range(8):
            radius = random.randint(38, 68)
            x = random.randint(int(width * 0.18), int(width * 0.82))
            y = random.randint(int(height * 0.42), int(height * 0.84))
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), outline=(*secondary, 96), width=2)
        for i in range(12):
            x = random.randint(int(width * 0.2), int(width * 0.8))
            y = random.randint(int(height * 0.48), int(height * 0.88))
            draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(*accent, 170))
    elif "outreach" in theme:
        for i in range(30):
            angle = random.uniform(-pi * 0.45, pi * 0.45)
            length = random.randint(220, 860)
            y = int(height * (0.35 + (i / 30) * 0.3))
            draw.line((cx, y, cx + cos(angle) * length, y + sin(angle) * length), fill=(*accent, 52), width=2)
        for i in range(8):
            x = int(width * (0.42 + i * 0.06))
            y = int(height * (0.18 + i * 0.04))
            draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(*secondary, 120))
    elif "book" in theme:
        for i in range(4):
            top = int(height * (0.38 + i * 0.08))
            draw.rectangle((int(width * 0.24), top, int(width * 0.76), top + 36), fill=(*accent, 60))
            draw.line((int(width * 0.24), top + 18, int(width * 0.76), top + 18), fill=(*secondary, 96), width=2)
    elif "hidden" in theme:
        arch_width = int(width * 0.24)
        arch_height = int(height * 0.46)
        draw.arc((cx - arch_width, cy - arch_height, cx + arch_width, cy + arch_height), 110, 70, fill=(*secondary, 120), width=5)
        draw.line((cx, cy - arch_height + 12, cx, cy + 180), fill=(*accent, 90), width=6)
    elif "questions" in theme:
        curve_x = cx - 70
        curve_y = cy + 30
        draw.arc((curve_x, curve_y - 160, curve_x + 180, curve_y), 130, 320, fill=(*secondary, 110), width=6)
        draw.ellipse((cx + 60, cy + 92, cx + 80, cy + 112), fill=(*accent, 160))
    elif "hero" in theme:
        draw_halo(draw, cx, int(height * 0.32), 260, (255, 220, 140, 130), rings=5)
        for i in range(6):
            draw.line((cx, int(height * 0.32), cx + cos(i * pi / 3) * 360, int(height * 0.32) + sin(i * pi / 3) * 360), fill=(*accent, 54), width=3)
    else:
        for i in range(7):
            radius = int(width * (0.1 + i * 0.05))
            draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), outline=(*accent, 60), width=2)

def image_one(filename, seed, stops, accent, secondary, motif="rings"):
    random.seed(seed)
    width, height = SIZE
    image = gradient(width, height, stops).convert("RGBA")
    image = add_noise(image.convert("RGB"), 85, seed).convert("RGBA")

    stars = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    star_draw = ImageDraw.Draw(stars, "RGBA")
    draw_starfield(star_draw, width, height, seed)
    image.alpha_composite(stars)

    background_glow = glow_layer(
        SIZE,
        [
            {"box": (width * 0.18, height * 0.05, width * 0.65, height * 0.55), "fill": (*accent, 120)},
            {"box": (width * 0.40, height * 0.10, width * 0.90, height * 0.70), "fill": (*secondary, 92)},
        ],
        160,
    )
    image.alpha_composite(background_glow)

    mountain_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    mountain_draw = ImageDraw.Draw(mountain_layer, "RGBA")
    draw_peak(mountain_draw, width, height, seed + 11, int(height * 0.70), (16, 16, 22, 255), (255, 230, 175, 24))
    draw_peak(mountain_draw, width, height, seed + 6, int(height * 0.78), (30, 28, 36, 255), (255, 230, 180, 18))
    draw_peak(mountain_draw, width, height, seed + 1, int(height * 0.86), (42, 38, 48, 255), (255, 230, 190, 10))
    image.alpha_composite(mountain_layer)

    geometry_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    geo_draw = ImageDraw.Draw(geometry_layer, "RGBA")
    cx = int(width * 0.52)
    cy = int(height * 0.38)
    draw_halo(geo_draw, cx, cy, 320, (255, 220, 130, 125))
    draw_geometry(geo_draw, width, height, cx, cy, 240 + seed % 50, (*accent, 180), 4, 14)
    draw_geometry(geo_draw, width, height, cx, cy, 180 + seed % 35, (*secondary, 110), 3, 12)
    geo_draw.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), outline=(255, 230, 170, 138), width=3)
    theme = get_subject_theme(filename)
    apply_subject_theme(geo_draw, width, height, theme, accent, secondary, seed)
    image.alpha_composite(geometry_layer)

    peak_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    peak_draw = ImageDraw.Draw(peak_layer, "RGBA")
    base_y = int(height * 0.70)
    peak_width = int(width * 0.16)
    points = [
        (cx - peak_width, height),
        (cx - peak_width // 2, base_y + 16),
        (cx, base_y - 90),
        (cx + peak_width // 2, base_y + 24),
        (cx + peak_width, height),
    ]
    peak_draw.polygon(points, fill=(28, 24, 32, 255))
    peak_draw.line(points, fill=(255, 235, 165, 74), width=4)
    image.alpha_composite(peak_layer)

    figure_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    figure_draw = ImageDraw.Draw(figure_layer, "RGBA")
    draw_hero_silhouette(figure_draw, cx, base_y - 100, 110)
    image.alpha_composite(figure_layer)

    line_layer = Image.new("RGBA", SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(line_layer, "RGBA")
    if motif == "rays":
        for i in range(45):
            angle = -0.82 + i * 0.036
            start_x = cx + sin(seed * 0.1 + i) * 18
            start_y = cy + 10
            end_x = cx + cos(angle) * 1600
            end_y = start_y + sin(angle) * 900
            draw.line((start_x, start_y, end_x, end_y), fill=(255, 210, 150, 28), width=2)
    elif motif == "woven":
        for i in range(40):
            y = height * (0.06 + i * 0.018)
            offset = sin(i * 0.58 + seed) * 80
            draw.arc(
                (80 + offset, y - 300, width - 90 + offset, y + 550),
                190,
                345,
                fill=(255, 200, 125, 32),
                width=2,
            )
    else:
        for i in range(40):
            y = height * (0.16 + i * 0.018)
            offset = sin(i * 0.52 + seed) * 52
            draw.arc(
                (140 + offset, y - 420, width - 140 + offset, y + 460),
                200,
                350,
                fill=(255, 210, 145, 26),
                width=2,
            )

    for i in range(65):
        x = random.randint(0, width)
        y = random.randint(int(height * 0.62), height)
        length = random.randint(20, 110)
        angle = random.uniform(-0.55, 0.55)
        draw.line(
            (x, y, x + cos(angle) * length, y + sin(angle) * length),
            fill=(255, 220, 185, random.randint(18, 45)),
            width=random.choice((1, 2)),
        )

    line_layer = line_layer.filter(ImageFilter.GaussianBlur(0.18))
    image.alpha_composite(line_layer)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.6, percent=130, threshold=2))
    image.convert("RGB").save(OUT / filename, "WEBP", quality=92, method=6)


def main():
    OUT.mkdir(exist_ok=True)
    specs = [
        ("apoth-hero-2026.webp", 211, [(2, 5, 11), (8, 24, 30), (34, 52, 48), (6, 9, 17)], (84, 231, 212), (239, 92, 151), "woven"),
        ("apoth-purpose-2026.webp", 232, [(4, 7, 14), (21, 32, 38), (72, 58, 35), (8, 10, 18)], (239, 204, 94), (82, 203, 195), "rings"),
        ("apoth-path-2026.webp", 253, [(5, 8, 18), (18, 35, 52), (46, 67, 64), (5, 8, 16)], (75, 211, 228), (217, 188, 91), "rays"),
        ("apoth-questions-2026.webp", 274, [(4, 6, 13), (28, 27, 48), (58, 46, 75), (7, 9, 17)], (184, 139, 255), (88, 224, 207), "woven"),
        ("apoth-consciousness-2026.webp", 295, [(3, 6, 13), (18, 25, 54), (52, 37, 92), (5, 9, 18)], (154, 117, 255), (69, 238, 183), "rings"),
        ("apoth-community-2026.webp", 316, [(4, 8, 14), (18, 39, 36), (86, 48, 62), (8, 10, 16)], (255, 142, 93), (80, 217, 174), "woven"),
        ("apoth-relationships-2026.webp", 337, [(6, 8, 16), (39, 29, 48), (84, 53, 63), (8, 9, 16)], (255, 116, 150), (238, 200, 108), "rings"),
        ("apoth-family-2026.webp", 358, [(4, 9, 15), (18, 40, 54), (37, 75, 75), (7, 11, 18)], (107, 223, 213), (230, 181, 102), "rays"),
        ("apoth-service-2026.webp", 379, [(3, 7, 13), (22, 37, 31), (55, 78, 53), (6, 9, 15)], (106, 231, 161), (236, 188, 92), "woven"),
        ("apoth-book-2026.webp", 400, [(5, 5, 12), (28, 22, 38), (82, 59, 37), (8, 8, 15)], (228, 190, 92), (156, 126, 255), "rings"),
        ("apoth-library-2026.webp", 421, [(3, 6, 13), (20, 30, 47), (62, 61, 74), (6, 9, 16)], (119, 180, 255), (236, 199, 100), "rays"),
        ("apoth-inquiry-2026.webp", 442, [(3, 5, 12), (19, 25, 51), (55, 34, 87), (5, 8, 17)], (99, 234, 219), (205, 116, 255), "woven"),
        ("apoth-outreach-2026.webp", 463, [(4, 8, 13), (25, 41, 35), (85, 53, 42), (7, 10, 15)], (255, 154, 93), (103, 232, 181), "rays"),
        ("apoth-hidden-2026.webp", 484, [(2, 4, 10), (12, 25, 43), (59, 31, 84), (4, 7, 16)], (81, 242, 199), (255, 88, 178), "woven"),
        ("hero.webp", 600, [(2, 6, 11), (20, 28, 42), (64, 44, 76), (7, 8, 16)], (86, 234, 211), (255, 116, 170), "woven"),
        ("light-through-darkness.webp", 610, [(3, 5, 14), (16, 24, 42), (59, 35, 78), (6, 9, 16)], (140, 126, 255), (255, 190, 105), "rings"),
        ("webconcept.webp", 620, [(4, 7, 13), (22, 30, 48), (72, 50, 78), (8, 9, 16)], (105, 224, 212), (228, 120, 255), "woven"),
        ("cosmic-consciousness.webp", 630, [(3, 5, 12), (18, 25, 50), (64, 42, 92), (7, 8, 16)], (120, 126, 255), (79, 239, 188), "rings"),
        ("group-together.webp", 640, [(4, 8, 15), (24, 38, 38), (92, 52, 64), (8, 10, 16)], (255, 145, 96), (90, 220, 176), "woven"),
        ("night-sky.webp", 650, [(2, 4, 12), (16, 24, 36), (54, 45, 90), (6, 8, 16)], (120, 142, 255), (255, 186, 104), "rays"),
        ("hidden-dmt.webp", 660, [(2, 5, 11), (14, 24, 44), (60, 34, 86), (5, 8, 15)], (82, 240, 201), (255, 102, 182), "woven"),
        ("book-of-apotheosis.webp", 670, [(5, 6, 13), (28, 22, 42), (84, 62, 42), (8, 8, 15)], (228, 190, 98), (160, 134, 255), "rings"),
        ("library-of-wisdom.webp", 680, [(3, 6, 14), (20, 30, 48), (64, 62, 74), (6, 9, 16)], (122, 180, 255), (236, 200, 100), "rays"),
        ("philosopher-view.webp", 690, [(3, 6, 12), (18, 24, 52), (56, 36, 90), (5, 8, 16)], (104, 234, 220), (208, 118, 255), "woven"),
        ("volunteer-outreach.webp", 700, [(4, 8, 14), (24, 38, 36), (88, 56, 44), (7, 10, 15)], (255, 154, 92), (102, 232, 180), "rays"),
        ("meditation-mountains.webp", 710, [(4, 7, 13), (16, 34, 48), (42, 74, 72), (6, 10, 16)], (98, 220, 214), (246, 194, 98), "rings"),
        ("sacred-geometry.webp", 720, [(3, 6, 12), (24, 28, 48), (59, 46, 78), (6, 8, 16)], (185, 142, 255), (90, 224, 208), "woven"),
        ("sacred-consciousness.webp", 730, [(3, 5, 12), (18, 26, 54), (54, 38, 92), (6, 8, 16)], (158, 120, 255), (72, 236, 184), "rings"),
        ("love-relationships.webp", 740, [(6, 8, 16), (40, 30, 48), (86, 56, 64), (8, 8, 16)], (255, 118, 152), (238, 200, 110), "rings"),
        ("parent-child.webp", 750, [(4, 8, 14), (18, 40, 54), (38, 76, 76), (7, 10, 18)], (108, 223, 214), (230, 182, 104), "rays"),
    ]

    for spec in specs:
        image_one(*spec)


if __name__ == "__main__":
    main()
