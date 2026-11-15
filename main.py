import os
import base64
import struct
import sys

MAX_BYTES = 1048576
MAX_DIMENSION = 1024
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(here, "img_b64.txt")
    entry_path = os.path.join(here, "entry.png")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    output_path = os.path.join(output_dir, "entry.png")

    try:
        with open(source_path, "r", encoding="ascii") as fh:
            encoded = "".join(fh.read().split())
    except OSError as exc:
        return fail("cannot read {}: {}".format(source_path, exc))

    try:
        data = base64.b64decode(encoded, validate=True)
    except ValueError as exc:
        return fail("cannot decode {}: {}".format(source_path, exc))

    print("decoded {} bytes from {}".format(len(data), source_path))

    if not data.startswith(PNG_SIGNATURE):
        return fail("decoded bytes do not start with the PNG signature")

    if len(data) < 24 or data[12:16] != b"IHDR":
        return fail("decoded bytes have no valid IHDR chunk")

    if len(data) > MAX_BYTES:
        return fail(
            "image is {} bytes, exceeding the {} byte limit".format(
                len(data), MAX_BYTES
            )
        )

    width, height = struct.unpack(">II", data[16:24])

    if width == 0 or height == 0:
        return fail("image has invalid zero dimension {}x{}".format(width, height))

    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        return fail(
            "image is {}x{}, exceeding the {}x{} limit".format(
                width, height, MAX_DIMENSION, MAX_DIMENSION
            )
        )

    try:
        with open(entry_path, "wb") as fh:
            fh.write(data)
        os.makedirs(output_dir, exist_ok=True)
        with open(output_path, "wb") as fh:
            fh.write(data)
    except OSError as exc:
        return fail("cannot write output: {}".format(exc))

    print(
        "entry.png: {} bytes, {}x{}, output {}".format(
            len(data), width, height, output_path
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
