# Night Sky Whale

Procedurally generated 1024×1024 PNG: a whale leaps from a dark ocean toward a shattered moon, city lights glowing along its back. Built with pure-stdlib zlib PNG writer — no external dependencies.

## Deterministic

Same bytes every run. No input data, no randomness, no external assets.

## Usage

```bash
python3 main.py
```

Regenerates `entry.png` in the working directory and `$MAKEFUN_OUTPUT_DIR/entry.png`.

## Output

- `entry.png` — 1024×1024 RGB PNG (~300–500 KB)
- Verified: dimensions ≤ 1024×1024, file size ≤ 1 MB
- Prints `GEN-DONE` on success