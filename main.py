import math
import struct
import zlib
import os
import sys

WIDTH = 1024
HEIGHT = 1024

def hash2d(x, y):
    n = int((x * 12.9898 + y * 78.233) * 43758.5453)
    n = (n ^ (n >> 13)) * 0x5bd1e995
    n = (n ^ (n >> 15)) * 0x5bd1e995
    n = n ^ (n >> 13)
    return (n & 0x7fffffff) / 0x7fffffff

def hash3d(x, y, z):
    n = int((x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453)
    n = (n ^ (n >> 13)) * 0x5bd1e995
    n = (n ^ (n >> 15)) * 0x5bd1e995
    n = n ^ (n >> 13)
    return (n & 0x7fffffff) / 0x7fffffff

def lerp(a, b, t):
    return a + (b - a) * t

def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3.0 - 2.0 * t)

def gaussian(x, sigma):
    return math.exp(-0.5 * (x / sigma) ** 2)

def dist_point_to_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    proj_x = x1 + t * dx
    proj_y = y1 + t * dy
    return math.hypot(px - proj_x, py - proj_y)

def whale_body_df(x, y):
    cx, cy = 512, 600
    dx = x - cx
    dy = y - cy
    rx = dx * 0.0025
    ry = dy * 0.0035
    body = math.sqrt(rx * rx + ry * ry) - 1.0
    tail_x = dx + 180
    tail_y = dy + 60
    rtx = tail_x * 0.004
    rty = tail_y * 0.006
    tail = math.sqrt(rtx * rtx + rty * rty) - 1.0
    flipper1_x = dx + 80
    flipper1_y = dy - 40
    f1x = flipper1_x * 0.006
    f1y = flipper1_y * 0.004
    flipper1 = math.sqrt(f1x * f1x + f1y * f1y) - 1.0
    flipper2_x = dx - 80
    flipper2_y = dy - 30
    f2x = flipper2_x * 0.006
    f2y = flipper2_y * 0.004
    flipper2 = math.sqrt(f2x * f2x + f2y * f2y) - 1.0
    return min(body, tail, flipper1, flipper2)

def moon_df(x, y):
    mx, my = 800, 200
    return math.hypot(x - mx, y - my) - 280

def crack_df(x, y, cx, cy, angle, length, width):
    dx = x - cx
    dy = y - cy
    rot_x = dx * math.cos(angle) + dy * math.sin(angle)
    rot_y = -dx * math.sin(angle) + dy * math.cos(angle)
    if abs(rot_x) > length / 2:
        return math.hypot(abs(rot_x) - length / 2, rot_y) - width / 2
    return abs(rot_y) - width / 2

def generate_image():
    pixels = bytearray(WIDTH * HEIGHT * 3)
    
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ux = x / WIDTH
            uy = y / HEIGHT
            
            sky_t = uy
            r = int(lerp(10, 25, sky_t))
            g = int(lerp(5, 15, sky_t))
            b = int(lerp(20, 50, sky_t))
            
            star_hash = hash2d(x * 0.1, y * 0.1)
            if star_hash < 0.0003:
                brightness = star_hash * 3000 + 100
                r = min(255, r + int(brightness))
                g = min(255, g + int(brightness * 0.9))
                b = min(255, b + int(brightness * 0.7))
            elif star_hash < 0.00035:
                brightness = (star_hash - 0.0003) * 20000 + 50
                r = min(255, r + int(brightness))
                g = min(255, g + int(brightness * 0.95))
                b = min(255, b + int(brightness * 0.8))
            
            moon_d = moon_df(x, y)
            if moon_d < 0:
                glow = gaussian(moon_d + 280, 60) * 0.6
                if moon_d < 10:
                    mr = int(lerp(220, 180, -moon_d / 10))
                    mg = int(lerp(210, 170, -moon_d / 10))
                    mb = int(lerp(180, 140, -moon_d / 10))
                else:
                    mr = int(200 + glow * 55)
                    mg = int(190 + glow * 65)
                    mb = int(160 + glow * 95)
                r = int(r * (1 - glow) + mr * glow)
                g = int(g * (1 - glow) + mg * glow)
                b = int(b * (1 - glow) + mb * glow)
                
                crack1 = crack_df(x, y, 800, 200, 0.5, 200, 3)
                crack2 = crack_df(x, y, 750, 250, -0.3, 150, 2.5)
                crack3 = crack_df(x, y, 850, 180, 1.2, 180, 2)
                crack4 = crack_df(x, y, 780, 150, -1.0, 120, 2)
                min_crack = min(crack1, crack2, crack3, crack4)
                if min_crack < 0:
                    crack_amt = gaussian(min_crack, 2)
                    r = int(r * (1 - crack_amt * 0.8))
                    g = int(g * (1 - crack_amt * 0.8))
                    b = int(b * (1 - crack_amt * 0.8))
                
                for i in range(8):
                    shard_hash = hash3d(x * 0.02 + i * 100, y * 0.02 + i * 50, i)
                    sx = 800 + (shard_hash - 0.5) * 600
                    sy = 200 + (hash3d(x * 0.02 + i * 100 + 1, y * 0.02 + i * 50 + 1, i) - 0.5) * 400
                    sd = math.hypot(x - sx, y - sy)
                    if sd < 8:
                        sg = gaussian(sd, 3) * 0.4
                        r = min(255, int(r + 100 * sg))
                        g = min(255, int(g + 90 * sg))
                        b = min(255, int(b + 70 * sg))
            
            if y > HEIGHT - 220:
                ocean_t = (y - (HEIGHT - 220)) / 220
                r = int(lerp(r, 5, ocean_t))
                g = int(lerp(g, 8, ocean_t))
                b = int(lerp(b, 20, ocean_t))
                
                shimmer = math.sin(x * 0.05 + y * 0.02) * 0.5 + math.sin(x * 0.1) * 0.3
                shimmer_val = int(max(0, shimmer * 15 * (1 - ocean_t)))
                r = min(255, r + shimmer_val)
                g = min(255, g + shimmer_val)
                b = min(255, b + shimmer_val * 2)
                
                refl_x = 800
                refl_dist = abs(x - refl_x)
                if refl_dist < 80:
                    refl_str = gaussian(refl_dist, 25) * (1 - ocean_t) * 0.5
                    r = min(255, int(r + 100 * refl_str))
                    g = min(255, int(g + 90 * refl_str))
                    b = min(255, int(b + 60 * refl_str))
            
            whale_d = whale_body_df(x, y)
            if whale_d < 0:
                whale_d_abs = -whale_d
                if whale_d_abs < 8:
                    rim = gaussian(whale_d_abs, 4) * 0.9
                    r = min(255, int(r + 80 * rim))
                    g = min(255, int(g + 180 * rim))
                    b = min(255, int(b + 220 * rim))
                else:
                    r = int(r * 0.05)
                    g = int(g * 0.05)
                    b = int(b * 0.1)
                
                back_y = 600 + (x - 512) * 0.3
                back_dist = abs(y - back_y)
                if back_dist < 35 and x > 400 and x < 620:
                    segment = int((x - 400) / 12)
                    window_hash = hash2d(segment * 100, back_y * 0.5)
                    if window_hash < 0.15:
                        wx = 400 + (segment % 18) * 12
                        wy = back_y + (segment // 18) * 8
                        wd = math.hypot(x - wx, y - wy)
                        if wd < 4:
                            wg = gaussian(wd, 1.5)
                            r = min(255, int(r + 255 * wg))
                            g = min(255, int(g + 200 * wg))
                            b = min(255, int(b + 50 * wg))
            
            if y > HEIGHT - 220 and whale_body_df(x, y) < 50 and whale_body_df(x, y) > -20:
                splash_d = whale_body_df(x, y)
                if splash_d > 0 and splash_d < 30:
                    splash_amt = gaussian(splash_d - 10, 8) * 0.7
                    r = min(255, int(r + 200 * splash_amt))
                    g = min(255, int(g + 210 * splash_amt))
                    b = min(255, int(b + 230 * splash_amt))
            
            idx = (y * WIDTH + x) * 3
            pixels[idx] = max(0, min(255, r))
            pixels[idx + 1] = max(0, min(255, g))
            pixels[idx + 2] = max(0, min(255, b))
    
    return pixels

def write_png(pixels, filename):
    scanlines = bytearray()
    for y in range(HEIGHT):
        scanlines.append(0)
        start = y * WIDTH * 3
        end = start + WIDTH * 3
        scanlines.extend(pixels[start:end])
    
    compressed = zlib.compress(scanlines, 1)
    
    def make_chunk(chunk_type, data):
        crc = zlib.crc32(chunk_type + data) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', crc)
    
    png = bytearray()
    png.extend(b'\x89PNG\r\n\x1a\n')
    
    ihdr_data = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    png.extend(make_chunk(b'IHDR', ihdr_data))
    
    png.extend(make_chunk(b'IDAT', compressed))
    
    png.extend(make_chunk(b'IEND', b''))
    
    with open(filename, 'wb') as f:
        f.write(png)
    
    return len(png)

def validate_png(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    if len(data) < 29:
        return False, "File too small"
    
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        return False, "Invalid PNG signature"
    
    ihdr_len = struct.unpack('>I', data[8:12])[0]
    if data[12:16] != b'IHDR' or ihdr_len != 13:
        return False, "Invalid IHDR chunk"
    
    width, height = struct.unpack('>II', data[16:24])
    bit_depth = data[24]
    color_type = data[25]
    
    if width != 1024 or height != 1024:
        return False, f"Invalid dimensions: {width}x{height}"
    if bit_depth != 8:
        return False, f"Invalid bit depth: {bit_depth}"
    if color_type != 2:
        return False, f"Invalid color type: {color_type}"
    
    if len(data) > 1048576:
        return False, f"File too large: {len(data)} bytes"
    
    return True, f"Valid PNG: {width}x{height}, {len(data)} bytes"

def main():
    print("Generating image...")
    pixels = generate_image()
    
    print("Writing entry.png...")
    size = write_png(pixels, 'entry.png')
    
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'entry.png')
    print(f"Writing {output_path}...")
    write_png(pixels, output_path)
    
    valid, msg = validate_png('entry.png')
    print(msg)
    if not valid:
        sys.exit(1)
    
    print("GEN-DONE")

if __name__ == '__main__':
    main()