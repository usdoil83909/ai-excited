# Sky-Whale City

`entry.png` is a 1024x1024 illustration of a sky-whale city: a colossal
whale-shaped metropolis with towers, bridges, and glowing windows rising
from its back, caught mid-leap through a sea of clouds toward a shattered
moon. Shards of the broken moon hang in the sky around it, lit by pale
lunar light.

## Running

`main.py` reads `entry.png` from its own directory, verifies the PNG
signature and IHDR dimensions, checks the file is at most 1 MiB, and copies
the exact bytes to the output directory.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The output directory defaults to `/output`.
