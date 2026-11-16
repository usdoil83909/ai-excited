# Sky-Whale City

An image entry depicting a sky-whale city leaping toward a shattered moon.

## Contents

- `img_b64.txt` — embedded base64-encoded PNG data (single line)
- `main.py` — regenerates `entry.png` from the embedded base64 data (pure stdlib)
- `entry.png` — generated PNG image

## Usage

```sh
python3 main.py
```

`main.py` reads `img_b64.txt`, base64-decodes and verifies the PNG signature, writes `entry.png` in the repository, and writes the same bytes to the output directory (`MAKEFUN_OUTPUT_DIR`, default `/output`). It validates the image is <= 1,048,576 bytes and <= 1024x1024 (from the IHDR chunk) and prints a summary.
