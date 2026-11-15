# Sky-Whale City

`entry.png` is a 1024x1024 illustration of a sky-whale city: a colossal
whale-shaped metropolis with towers, bridges, and glowing windows rising
from its back, caught mid-leap through a sea of clouds toward a shattered
moon. Shards of the broken moon hang in the sky around it, lit by pale
lunar light.

## Running

`main.py` uses only the Python 3 standard library. It locates its own
directory, reads `entry.png`, verifies the PNG signature (`\x89PNG`), checks
that the file is at most 1 MiB, and rejects oversized dimensions from the
IHDR chunk. It then creates the output directory and writes the exact same
bytes to `entry.png` there.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output directory defaults to `/output`.
