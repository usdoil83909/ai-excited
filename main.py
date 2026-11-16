import base64
import os
import struct
import sys

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576
MAX_DIMENSION = 1024


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    b64_path = os.path.join(here, "img_b64.txt")
    entry_path = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")

    with open(b64_path, "r", encoding="ascii") as f:
        b64 = f.read().strip()
    data = base64.b64decode(b64)

    if not data.startswith(PNG_SIGNATURE):
        print("Error: invalid PNG signature", file=sys.stderr)
        sys.exit(1)

    if len(data) < 24:
        print("Error: file too short for IHDR", file=sys.stderr)
        sys.exit(1)

    width, height = struct.unpack(">II", data[16:24])

    if len(data) > MAX_BYTES:
        print(f"Error: image size {len(data)} exceeds {MAX_BYTES} bytes", file=sys.stderr)
        sys.exit(1)
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(f"Error: image dimensions {width}x{height} exceed {MAX_DIMENSION}x{MAX_DIMENSION}", file=sys.stderr)
        sys.exit(1)

    with open(entry_path, "wb") as f:
        f.write(data)

    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(data)

    print(f"Decoded {len(data)} bytes, {width}x{height} PNG")
    print(f"Wrote {entry_path}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
