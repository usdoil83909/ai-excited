import os
import shutil
import struct
import sys

MAX_BYTES = 1048576
MAX_DIMENSION = 8192
PNG_SIGNATURE = b"\x89PNG"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    destination = os.path.join(output_dir, "entry.png")

    with open(source, "rb") as fh:
        data = fh.read()

    if not data.startswith(PNG_SIGNATURE):
        print("error: entry.png does not start with PNG signature", file=sys.stderr)
        return 1

    if len(data) > MAX_BYTES:
        print("error: entry.png exceeds 1 MiB", file=sys.stderr)
        return 1

    if len(data) < 24 or data[12:16] != b"IHDR":
        print("error: entry.png has no valid IHDR chunk", file=sys.stderr)
        return 1

    width, height = struct.unpack(">II", data[16:24])
    if width == 0 or height == 0 or width > MAX_DIMENSION or height > MAX_DIMENSION:
        print(
            "error: invalid image dimensions {}x{}".format(width, height),
            file=sys.stderr,
        )
        return 1

    os.makedirs(output_dir, exist_ok=True)
    shutil.copyfile(source, destination)

    print(
        "entry.png: {} bytes, {}x{} -> {}".format(
            len(data), width, height, destination
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
