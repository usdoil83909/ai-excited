#!/usr/bin/env python3
import math
import struct
import zlib
import os
import sys

WIDTH = 1024
HEIGHT = 1024

def write_png(path, pixels):
    png_sig = b'\x89PNG\r\n\x1a\n'
    
    ihdr_data = struct.pack('>IIBBBBB', WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    ihdr_crc = zlib.crc32(b'IHDR' + ihdr_data) & 0xffffffff
    ihdr_chunk = struct.pack('>I', len(ihdr_data)) + b'IHDR' + ihdr_data + struct.pack('>I', ihdr_crc)
    
    scanlines = bytearray()
    for y in range(HEIGHT):
        scanlines.append(0)
        row = pixels[y]
        for x in range(WIDTH):
            r, g, b = row[x]
            scanlines.append(r)
            scanlines.append(g)
            scanlines.append(b)
    
    compressed = zlib.compress(scanlines, level=6)
    idat_crc = zlib.crc32(b'IDAT' + compressed) & 0xffffffff
    idat_chunk = struct.pack('>I', len(compressed)) + b'IDAT' + compressed + struct.pack('>I', idat_crc)
    
    iend_crc = zlib.crc32(b'IEND') & 0xffffffff
    iend_chunk = struct.pack('>I', 0) + b'IEND' + struct.pack('>I', iend_crc)
    
    with open(path, 'wb') as f:
        f.write(png_sig)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)

def main():
    pixels = [[(0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]
    
    stars = []
    for i in range(300):
        sx = math.sin(i * 1.0 + i * 2.0) * 43758.5453
        sx = (sx - int(sx)) % 1.0
        sy = math.sin(i * 3.0 + i * 5.0) * 43758.5453
        sy = (sy - int(sy)) % 1.0
        b = math.sin(i * 7.0 + i * 11.0) * 43758.5453
        b = ((b - int(b)) % 1.0) * 0.8 + 0.2
        stars.append((sx, sy, b))
    
    big_stars = []
    for i in range(15):
        sx = math.sin(i * 13.0 + i * 17.0) * 43758.5453
        sx = (sx - int(sx)) % 1.0
        sy = math.sin(i * 19.0 + i * 23.0) * 43758.5453
        sy = (sy - int(sy)) % 1.0
        sz = math.sin(i * 29.0 + i * 31.0) * 43758.5453
        sz = ((sz - int(sz)) % 1.0) * 2.0 + 0.5
        big_stars.append((sx, sy, sz))
    
    moon_cracks = []
    for ci in range(5):
        angle = ci * 2.5 + ((math.sin(ci * 100.0 + ci * 200.0) * 43758.5453) % 1.0) * 0.5
        cx = 0.78 + math.cos(angle) * 0.18 * 0.3
        cy = 0.22 + math.sin(angle) * 0.18 * 0.3
        moon_cracks.append((cx, cy))
    
    moon_shards = []
    for di in range(20):
        angle = ((math.sin(di * 37.0 + di * 41.0) * 43758.5453) % 1.0) * 6.28
        dist_f = 0.18 + ((math.sin(di * 43.0 + di * 47.0) * 43758.5453) % 1.0) * 0.15 + 0.02
        sx = 0.78 + math.cos(angle) * dist_f
        sy = 0.22 + math.sin(angle) * dist_f
        moon_shards.append((sx, sy))
    
    whale_windows = []
    for wi in range(40):
        back_x = 0.45 + (wi - 15) * 0.008 + ((math.sin(wi * 11.0 + wi * 13.0) * 43758.5453) % 1.0) * 0.003
        back_y = 0.65 - 0.12 * 0.3 + (wi - 15) * (wi - 15) * 0.0002 + ((math.sin(wi * 17.0 + wi * 19.0) * 43758.5453) % 1.0) * 0.002
        whale_windows.append((back_x, back_y))
    
    splash_particles = []
    for si in range(60):
        angle = ((math.sin(si * 23.0 + si * 29.0) * 43758.5453) % 1.0) * 6.28
        dist_f = ((math.sin(si * 31.0 + si * 37.0) * 43758.5453) % 1.0) * 0.08 + 0.01
        sx = 0.45 + math.cos(angle) * dist_f
        sy = 0.81 + math.sin(angle) * dist_f * 0.5
        splash_particles.append((sx, sy))
    
    shimmer_lines = []
    for si in range(8):
        sy = 0.8 + si * 0.015 + ((math.sin(si * 100.0 + si * 200.0) * 43758.5453) % 1.0) * 0.005
        shimmer_lines.append(sy)
    
    for y in range(HEIGHT):
        ny = y / HEIGHT
        row = pixels[y]
        for x in range(WIDTH):
            nx = x / WIDTH
            
            sky_t = ny
            col_r = 0.04 + 0.04 * sky_t
            col_g = 0.05 + 0.05 * sky_t
            col_b = 0.16 + 0.04 * sky_t
            
            for sx, sy, b in stars:
                dx = nx - sx
                dy = ny - sy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist * 1200.0 < 1.5:
                    glow = math.exp(-(dist * 1200.0) ** 2 / 0.5) * b * 0.6
                    col_r = min(1.0, col_r + glow)
                    col_g = min(1.0, col_g + glow)
                    col_b = min(1.0, col_b + glow)
            
            for sx, sy, sz in big_stars:
                dx = nx - sx
                dy = ny - sy
                dist = math.sqrt(dx * dx + dy * dy)
                if dist * 800.0 < 3.0:
                    glow = math.exp(-(dist * 800.0) ** 2 / 2.0) * sz * 0.8
                    col_r = min(1.0, col_r + glow)
                    col_g = min(1.0, col_g + glow * 0.95)
                    col_b = min(1.0, col_b + glow * 0.9)
            
            dx = nx - 0.78
            dy = ny - 0.22
            moon_dist = math.sqrt(dx * dx + dy * dy)
            
            moon_glow = math.exp(-moon_dist ** 2 / (2 * (0.18 * 1.5) ** 2)) * 0.4
            col_r = min(1.0, col_r + moon_glow * 0.95)
            col_g = min(1.0, col_g + moon_glow * 0.9)
            col_b = min(1.0, col_b + moon_glow * 0.8)
            
            if moon_dist < 0.18:
                t = moon_dist / 0.18
                moon_val = 1.0 - (t * t * (3.0 - 2.0 * t)) if t > 0.85 else 1.0
                if t > 0.85:
                    moon_val = 1.0 - smoothstep(0.85, 1.0, t)
                col_r = col_r * (1 - moon_val) + 0.9 * moon_val
                col_g = col_g * (1 - moon_val) + 0.85 * moon_val
                col_b = col_b * (1 - moon_val) + 0.75 * moon_val
                
                for cx, cy in moon_cracks:
                    cdx = nx - cx
                    cdy = ny - cy
                    cd = math.sqrt(cdx * cdx + cdy * cdy)
                    if cd < 0.18 * 0.35:
                        crack = math.sin(cdx * 120.0 + cdy * 80.0)
                        if crack < -0.3:
                            col_r *= 0.15
                            col_g *= 0.15
                            col_b *= 0.15
            
            for sx, sy in moon_shards:
                sdx = nx - sx
                sdy = ny - sy
                sd = math.sqrt(sdx * sdx + sdy * sdy)
                if sd < 0.008:
                    shard_val = math.exp(-sd ** 2 / (2 * 0.006 ** 2)) * 0.7
                    col_r = min(1.0, col_r + shard_val * 0.8)
                    col_g = min(1.0, col_g + shard_val * 0.75)
                    col_b = min(1.0, col_b + shard_val * 0.7)
            
            if ny > 0.8:
                ocean_t = (ny - 0.8) / 0.2
                col_r = 0.01 * (1 - ocean_t) + 0.005 * ocean_t
                col_g = 0.02 * (1 - ocean_t) + 0.01 * ocean_t
                col_b = 0.06 * (1 - ocean_t) + 0.03 * ocean_t
                
                for sy in shimmer_lines:
                    if ny > sy and ny < sy + 0.003:
                        col_r += 0.03
                        col_g += 0.02
                        col_b += 0.015
                
                rdx = nx - 0.78
                rdy = ny - (1.0 - 0.22 + 0.02)
                rdist = math.sqrt(rdx * rdx + rdy * rdy)
                if rdist < 0.12:
                    reflect = math.exp(-rdist ** 2 / (2 * 0.06 ** 2)) * 0.15
                    col_r = min(1.0, col_r + reflect * 0.7)
                    col_g = min(1.0, col_g + reflect * 0.6)
                    col_b = min(1.0, col_b + reflect * 0.5)
            
            dx = (nx - 0.45) / 0.22
            dy = (ny - 0.65) / 0.12
            whale_dist = math.sqrt(dx * dx + dy * dy)
            
            tdx = (nx - (0.45 - 0.22 * 0.7)) / (0.22 * 0.5)
            tdy = (ny - (0.65 + 0.12 * 0.3)) / (0.12 * 0.4)
            tail_dist = math.sqrt(tdx * tdx + tdy * tdy)
            
            f1dx = (nx - (0.45 + 0.22 * 0.2)) / (0.22 * 0.25)
            f1dy = (ny - (0.65 + 0.12 * 0.5)) / (0.12 * 0.15)
            flipper1_dist = math.sqrt(f1dx * f1dx + f1dy * f1dy)
            
            f2dx = (nx - (0.45 - 0.22 * 0.1)) / (0.22 * 0.2)
            f2dy = (ny - (0.65 + 0.12 * 0.6)) / (0.12 * 0.12)
            flipper2_dist = math.sqrt(f2dx * f2dx + f2dy * f2dy)
            
            whale_shape = min(whale_dist, tail_dist, flipper1_dist, flipper2_dist)
            
            if whale_shape < 1.0:
                if whale_shape > 0.85:
                    t = (whale_shape - 0.85) / 0.15
                    whale_val = 1.0 - t * t * (3.0 - 2.0 * t)
                else:
                    whale_val = 1.0
                col_r = col_r * (1 - whale_val) + 0.02 * whale_val
                col_g = col_g * (1 - whale_val) + 0.02 * whale_val
                col_b = col_b * (1 - whale_val) + 0.03 * whale_val
                
                if whale_shape > 0.88:
                    rim = math.exp(-(whale_shape - 0.92) ** 2 / (2 * 0.02 ** 2)) * 0.6
                    col_r = min(1.0, col_r + rim * 0.3)
                    col_g = min(1.0, col_g + rim * 0.8)
                    col_b = min(1.0, col_b + rim * 1.0)
                
                for wx, wy in whale_windows:
                    wdx = nx - wx
                    wdy = ny - wy
                    wdist = math.sqrt(wdx * wdx + wdy * wdy)
                    if wdist < 0.006:
                        window_glow = math.exp(-wdist ** 2 / (2 * 0.004 ** 2)) * 0.9
                        col_r = min(1.0, col_r + window_glow)
                        col_g = min(1.0, col_g + window_glow * 0.7)
                        col_b = min(1.0, col_b + window_glow * 0.1)
            
            for sx, sy in splash_particles:
                sdx = nx - sx
                sdy = ny - sy
                sd = math.sqrt(sdx * sdx + sdy * sdy)
                if sd < 0.008:
                    splash_val = math.exp(-sd ** 2 / (2 * 0.005 ** 2)) * 0.7
                    col_r = min(1.0, col_r + splash_val * 0.9)
                    col_g = min(1.0, col_g + splash_val * 0.85)
                    col_b = min(1.0, col_b + splash_val * 0.8)
            
            row[x] = (int(col_r * 255), int(col_g * 255), int(col_b * 255))
    
    write_png('entry.png', pixels)
    
    output_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(output_dir, exist_ok=True)
    write_png(os.path.join(output_dir, 'entry.png'), pixels)
    
    with open('entry.png', 'rb') as f:
        data = f.read()
    
    if len(data) >= 24:
        ihdr_offset = 16
        width = struct.unpack('>I', data[ihdr_offset:ihdr_offset + 4])[0]
        height = struct.unpack('>I', data[ihdr_offset + 4:ihdr_offset + 8])[0]
        print(f"Size: {len(data)} bytes, Dimensions: {width}x{height}")
        assert len(data) <= 1048576, f"File too large: {len(data)}"
        assert width <= 1024 and height <= 1024, f"Dimensions too large: {width}x{height}"
    
    print("GEN-DONE")

def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)

if __name__ == '__main__':
    main()