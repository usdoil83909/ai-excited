[![make.fun · ai-excited-01](https://make.fun/badge/ai-excited-01.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![rank](https://make.fun/badge/ai-excited-01/usdoil83909/ai-excited/rank.svg)](https://make.fun/bounty/ai-excited-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
[![reward](https://make.fun/badge/ai-excited-01/usdoil83909/ai-excited/reward.svg)](https://make.fun/bounty/ai-excited-01?utm_source=github&utm_medium=readme&utm_campaign=ai-excited-01)
Bountied by make.fun — see the bounty page link above.

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