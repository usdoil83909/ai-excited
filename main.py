#!/usr/bin/env python3
"""
Procedural PNG image generator (stdlib only). No PIL/numpy/network/input data.
Scene: night-sky whale leaping from a dark ocean toward a shattered moon, city lights on its back.
Output: 1024x1024 RGB PNG written to ./entry.png and to $MAKEFUN_OUTPUT_DIR (default /output).
"""
from __future__ import annotations

import math
import os
import struct
import sys
import zlib


W, H = 1024, 1024


def clamp(v: float, lo: float = 0.0, hi: float = 255.0) -> int:
    if v < lo:
        return int(lo)
    if v > hi:
        return int(hi)
    return int(v)


def add_rgb(base, dr, dg, db):
    return (
        clamp(base[0] + dr),
        clamp(base[1] + dg),
        clamp(base[2] + db),
    )


def blend_over(dst, src, a):
    # src over dst with alpha a in [0,1]
    return (
        clamp(dst[0] * (1.0 - a) + src[0] * a),
        clamp(dst[1] * (1.0 - a) + src[1] * a),
        clamp(dst[2] * (1.0 - a) + src[2] * a),
    )


def gaussian_falloff(d, sigma):
    if sigma <= 0:
        return 0.0
    return math.exp(-(d * d) / (2.0 * sigma * sigma))


def hash01(x: int, y: int, seed: int = 1337) -> float:
    n = x * 374761393 + y * 668265263 + seed * 1442695041
    n = (n ^ (n >> 13)) * 1274126177
    n = n ^ (n >> 16)
    return (n & 0xFFFFFFFF) / 4294967295.0


def hash_signed(x: int, y: int, seed: int = 1337) -> float:
    return hash01(x, y, seed) * 2.0 - 1.0


def sky_color(y: int):
    t = y / float(H - 1)
    # deep navy near top -> indigo near horizon
    top = (4, 6, 28)
    mid = (10, 14, 55)
    horizon = (30, 22, 70)
    if t < 0.65:
        tt = t / 0.65
        # top->mid
        return (
            top[0] + (mid[0] - top[0]) * tt,
            top[1] + (mid[1] - top[1]) * tt,
            top[2] + (mid[2] - top[2]) * tt,
        )
    else:
        tt = (t - 0.65) / 0.35
        return (
            mid[0] + (horizon[0] - mid[0]) * tt,
            mid[1] + (horizon[1] - mid[1]) * tt,
            mid[2] + (horizon[2] - mid[2]) * tt,
        )


def point_in_polygon(px, py, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / ((yj - yi) if (yj - yi) != 0 else 1e-12) + xi):
            inside = not inside
        j = i
    return inside


def build_scene():
    img = [[(0, 0, 0) for _ in range(W)] for _ in range(H)]

    # 1) Sky gradient + stars
    for y in range(H):
        sc = sky_color(y)
        for x in range(W):
            img[y][x] = (clamp(sc[0]), clamp(sc[1]), clamp(sc[2]))

    # Deterministic stars via sin-based hash
    stars = []
    # generate ~300 stars
    for i in range(420):
        h = math.sin(i * 127.1 + 311.7) * 43758.5453
        h2 = math.sin(i * 269.5 + 183.3) * 43758.5453
        sx = int((h - math.floor(h)) * (W - 1))
        sy = int((h2 - math.floor(h2)) * (H * 0.62))  # mostly sky upper part
        sz = ((math.sin(i * 74.7) * 0.5 + 0.5))
        stars.append((sx, sy, sz))

    # dedupe roughly by placing
    placed = set()
    star_list = []
    for sx, sy, sz in stars:
        key = (sx // 2, sy // 2)
        if key in placed:
            continue
        placed.add(key)
        star_list.append((sx, sy, sz))
        if len(star_list) >= 320:
            break

    for sx, sy, sz in star_list:
        brightness = 140 + sz * 115
        # size category
        if sz > 0.92:
            # larger glowing star
            for oy in range(-2, 3):
                for ox in range(-2, 3):
                    px = sx + ox
                    py = sy + oy
                    if 0 <= px < W and 0 <= py < H:
                        d = math.sqrt(ox * ox + oy * oy)
                        a = gaussian_falloff(d, 1.4)
                        img[py][px] = add_rgb(img[py][px], brightness * a, brightness * a, brightness * a * 1.1)
        elif sz > 0.75:
            for oy in range(-1, 2):
                for ox in range(-1, 2):
                    px = sx + ox
                    py = sy + oy
                    if 0 <= px < W and 0 <= py < H:
                        d = math.sqrt(ox * ox + oy * oy)
                        a = gaussian_falloff(d, 0.9)
                        img[py][px] = add_rgb(img[py][px], brightness * a * 0.9, brightness * a * 0.9, brightness * a)
        else:
            if 0 <= sx < W and 0 <= sy < H:
                img[sy][sx] = add_rgb(img[sy][sx], brightness * 0.7, brightness * 0.7, brightness * 0.85)

    # 2) Moon: big pale circle upper-right with soft glow; dark crack polygons; faint debris shards
    moon_cx, moon_cy = int(W * 0.78), int(H * 0.22)
    moon_r = int(min(W, H) * 0.18)

    # glow layers
    for gy in range(max(0, moon_cy - moon_r - 80), min(H, moon_cy + moon_r + 80)):
        for gx in range(max(0, moon_cx - moon_r - 80), min(W, moon_cx + moon_r + 80)):
            dx = gx - moon_cx
            dy = gy - moon_cy
            d = math.sqrt(dx * dx + dy * dy)
            if d < moon_r + 70:
                glow = gaussian_falloff(d - moon_r * 0.6, 55.0) * 0.35
                if glow > 0.001:
                    img[gy][gx] = add_rgb(img[gy][gx], 120 * glow, 120 * glow, 90 * glow)

    # moon body
    for y in range(max(0, moon_cy - moon_r - 2), min(H, moon_cy + moon_r + 2)):
        for x in range(max(0, moon_cx - moon_r - 2), min(W, moon_cx + moon_r + 2)):
            dx = x - moon_cx
            dy = y - moon_cy
            d = math.sqrt(dx * dx + dy * dy)
            if d <= moon_r:
                # pale color with slight shading
                shade = 1.0 - (d / moon_r) * 0.12
                val = 220 * shade
                img[y][x] = (clamp(val), clamp(val * 0.98), clamp(val * 0.9))
            elif d <= moon_r + 1.5:
                a = 1.0 - (d - moon_r) / 1.5
                img[y][x] = blend_over(img[y][x], (230, 228, 210), a * 0.8)

    # cracks (dark polygons)
    cracks = [
        [(moon_cx - 10, moon_cy - 30), (moon_cx + 15, moon_cy - 5), (moon_cx + 5, moon_cy + 10), (moon_cx - 20, moon_cy - 10)],
        [(moon_cx + 20, moon_cy - 10), (moon_cx + 60, moon_cy + 5), (moon_cx + 45, moon_cy + 25), (moon_cx + 10, moon_cy + 5)],
        [(moon_cx - 30, moon_cy + 20), (moon_cx - 5, moon_cy + 40), (moon_cx - 15, moon_cy + 65), (moon_cx - 45, moon_cy + 35)],
    ]
    for poly in cracks:
        minx = max(0, min(p[0] for p in poly) - 2)
        maxx = min(W - 1, max(p[0] for p in poly) + 2)
        miny = max(0, min(p[1] for p in poly) - 2)
        maxy = min(H - 1, max(p[1] for p in poly) + 2)
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                if point_in_polygon(xx + 0.5, yy + 0.5, poly):
                    dxm = xx - moon_cx
                    dym = yy - moon_cy
                    if math.sqrt(dxm * dxm + dym * dym) <= moon_r:
                        img[yy][xx] = blend_over(img[yy][xx], (90, 88, 78), 0.75)

    # faint debris shards
    shards = [
        [(moon_cx + moon_r + 15, moon_cy - 20), (moon_cx + moon_r + 35, moon_cy - 10), (moon_cx + moon_r + 20, moon_cy + 5)],
        [(moon_cx + moon_r + 5, moon_cy + 30), (moon_cx + moon_r + 25, moon_cy + 40), (moon_cx + moon_r + 10, moon_cy + 55)],
        [(moon_cx - moon_r - 10, moon_cy - 5), (moon_cx - moon_r - 30, moon_cy + 5), (moon_cx - moon_r - 15, moon_cy + 20)],
    ]
    for poly in shards:
        minx = max(0, min(p[0] for p in poly) - 1)
        maxx = min(W - 1, max(p[0] for p in poly) + 1)
        miny = max(0, min(p[1] for p in poly) - 1)
        maxy = min(H - 1, max(p[1] for p in poly) + 1)
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                if point_in_polygon(xx + 0.5, yy + 0.5, poly):
                    img[yy][xx] = blend_over(img[yy][xx], (200, 198, 180), 0.55)

    # 3) Ocean bottom ~200px
    ocean_top = H - 200
    for y in range(ocean_top, H):
        ty = (y - ocean_top) / 199.0
        base = (
            6 + ty * 4,
            10 + ty * 8,
            30 + ty * 25,
        )
        for x in range(W):
            shimmer = 0.0
            shimmer += math.sin(x * 0.03 + y * 0.15) * 4.0
            shimmer += math.sin(x * 0.07 - y * 0.08 + 1.7) * 3.0
            val = (
                clamp(base[0] + shimmer * 0.3),
                clamp(base[1] + shimmer * 0.5),
                clamp(base[2] + shimmer * 0.8),
            )
            img[y][x] = val

    # Moon reflection column on ocean
    ref_x = moon_cx
    for y in range(ocean_top, H):
        for x in range(W):
            dx = x - ref_x
            width = 18 + (y - ocean_top) * 0.35
            a = gaussian_falloff(dx, width) * 0.35
            if a > 0.002:
                img[y][x] = add_rgb(img[y][x], 80 * a, 78 * a, 60 * a)

    # 4) Whale: large dark silhouette leaping upward-left
    # Body as distance field (ellipse-ish) + curved tail + flippers
    whale_cx = W * 0.52
    whale_cy = H * 0.56
    for y in range(H):
        for x in range(W):
            # body: elongated ellipse rotated-ish by moving coords
            dx = (x - whale_cx)
            dy = (y - whale_cy)
            # rotate slightly
            ang = -0.35
            rx = dx * math.cos(ang) - dy * math.sin(ang)
            ry = dx * math.sin(ang) + dy * math.cos(ang)
            body = (rx / 260.0) ** 2 + (ry / 110.0) ** 2
            inside_body = body <= 1.0

            # tail (down-right curved)
            tx = x - (whale_cx + 200)
            ty = y - (whale_cy + 30)
            tail = (tx / 140.0) ** 2 + ((ty - 40 * math.sin(tx / 80.0)) / 50.0) ** 2
            inside_tail = tail <= 1.0 and x > whale_cx + 120

            # flipper
            fx = x - (whale_cx - 40)
            fy = y - (whale_cy + 40)
            flipper = (fx / 90.0) ** 2 + (fy / 35.0) ** 2
            inside_flipper = flipper <= 1.0 and y > whale_cy

            if inside_body or inside_tail or inside_flipper:
                # dark silhouette
                img[y][x] = (8, 10, 22)

    # Pale-cyan rim light on top edge of whale
    for y in range(H):
        for x in range(W):
            dx = (x - whale_cx)
            dy = (y - whale_cy)
            ang = -0.35
            rx = dx * math.cos(ang) - dy * math.sin(ang)
            ry = dx * math.sin(ang) + dy * math.cos(ang)
            body = (rx / 260.0) ** 2 + (ry / 110.0) ** 2
            # rim: just outside top side
            if 0.98 <= body <= 1.08 and ry < 0:
                a = (1.08 - body) / 0.10
                img[y][x] = blend_over(img[y][x], (140, 220, 230), a * 0.9)

    # 5) City lights on whale back (warm yellow in grid clusters following curve)
    for i in range(120):
        h = math.sin(i * 91.7 + 17.3) * 43758.5453
        h2 = math.sin(i * 233.1 + 51.7) * 43758.5453
        lx = int(whale_cx - 180 + (h - math.floor(h)) * 360)
        ly = int(whale_cy - 90 + (h2 - math.floor(h2)) * 120)
        dx = (lx - whale_cx)
        dy = (ly - whale_cy)
        ang = -0.35
        rx = dx * math.cos(ang) - dy * math.sin(ang)
        ry = dx * math.sin(ang) + dy * math.cos(ang)
        body = (rx / 260.0) ** 2 + (ry / 110.0) ** 2
        if body <= 0.85 and ry < 10:
            # draw small lit block
            for oy in range(0, 3):
                for ox in range(0, 2):
                    px = lx + ox
                    py = ly + oy
                    if 0 <= px < W and 0 <= py < H:
                        img[py][px] = blend_over(img[py][px], (255, 210, 120), 0.95)
            # tiny glow
            for oy in range(-1, 4):
                for ox in range(-1, 3):
                    px = lx + ox
                    py = ly + oy
                    if 0 <= px < W and 0 <= py < H:
                        d = math.sqrt((ox - 0.5) ** 2 + (oy - 1.0) ** 2)
                        a = gaussian_falloff(d, 1.8) * 0.25
                        img[py][px] = add_rgb(img[py][px], 255 * a, 210 * a, 120 * a)

    # 6) Splash/foam where whale left water
    splash_cx = int(whale_cx - 220)
    splash_cy = ocean_top + 10
    for i in range(90):
        h = math.sin(i * 55.3 + 9.1) * 43758.5453
        h2 = math.sin(i * 141.7 + 33.3) * 43758.5453
        px = int(splash_cx + (h - math.floor(h)) * 220 - 110)
        py = int(splash_cy + (h2 - math.floor(h2)) * 60 - 20)
        if 0 <= px < W and 0 <= py < H:
            r = 1 + int((math.sin(i * 12.3) * 0.5 + 0.5) * 2)
            for oy in range(-r, r + 1):
                for ox in range(-r, r + 1):
                    qx = px + ox
                    qy = py + oy
                    if 0 <= qx < W and 0 <= qy < H:
                        d = math.sqrt(ox * ox + oy * oy)
                        a = gaussian_falloff(d, r + 0.5) * 0.8
                        img[qy][qx] = blend_over(img[qy][qx], (210, 230, 240), a)

    return img


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    c = chunk_type + data
    return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)


def write_png(path: str, img):
    # Build raw scanlines with filter type 0
    raw = bytearray()
    for y in range(H):
        raw.append(0)  # filter type None
        for x in range(W):
            r, g, b = img[y][x]
            raw.extend((r & 0xFF, g & 0xFF, b & 0xFF))

    compressed = zlib.compress(bytes(raw), level=6)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)  # 8-bit RGB
    out = bytearray()
    out.extend(sig)
    out.extend(png_chunk(b"IHDR", ihdr))
    out.extend(png_chunk(b"IDAT", compressed))
    out.extend(png_chunk(b"IEND", b""))

    with open(path, "wb") as f:
        f.write(out)

    return len(out)


def validate_png(path: str):
    with open(path, "rb") as f:
        data = f.read()
    if len(data) < 24:
        raise ValueError("PNG too small")
    # IHDR at offset 8: length(4)+type(4)=8, then data starts at 16 for width/height
    width = struct.unpack(">I", data[16:20])[0]
    height = struct.unpack(">I", data[20:24])[0]
    size = len(data)
    return width, height, size


def main():
    img = build_scene()
    out_path = os.path.join(os.getcwd(), "entry.png")
    size_bytes = write_png(out_path, img)

    # Also write to output dir
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    try:
        os.makedirs(out_dir, exist_ok=True)
        out_copy = os.path.join(out_dir, "entry.png")
        with open(out_path, "rb") as src, open(out_copy, "wb") as dst:
            dst.write(src.read())
        wrote_copy = True
    except Exception as e:
        wrote_copy = False
        copy_err = str(e)

    w, h, fsize = validate_png(out_path)
    if w > 1024 or h > 1024:
        print(f"VALIDATION FAIL: dimensions {w}x{h} exceed 1024x1024")
        sys.exit(2)
    if fsize > 1048576:
        print(f"VALIDATION FAIL: file size {fsize} bytes > 1048576")
        sys.exit(3)

    print("=== PNG Summary ===")
    print(f"File: {out_path}")
    print(f"Width: {w}")
    print(f"Height: {h}")
    print(f"Size(bytes): {fsize}")
    if wrote_copy:
        print(f"Copied to: {os.path.join(out_dir, 'entry.png')}")
    else:
        print(f"Copy to {out_dir} failed: {copy_err}")
    print("GEN-DONE")


if __name__ == "__main__":
    main()
