# waddr — 3D word-address engine

The pure encoding/decoding core of the 3D word-based address protocol. Maps any
point in the near-Earth shell (≈13 km underground to 2,000 km altitude) to a
short, human-readable word address and back. No web dependencies — numpy only.

```python
from protocol import encode_all, decode

info = encode_all(51.5074, -0.1278, alt_km=0.1, words=5)
print(info["words"])      # e.g. dinosaur-epidural-usable-bingo-dusty-C
print(decode(info["words"])["lat"])
```

## Public API

| function | purpose |
|----------|---------|
| `encode_all(lat, lon, alt_km=0.0, words=5)` | full result: `words`, `transfer`, `indices`, decoded center |
| `encode_words(...)` | just the `word-word-...-C` string |
| `encode_transfer(...)` | just the `C-num-num-...` machine string |
| `decode(text)` | auto-detects word/transfer format → location |
| `alternatives(text)` | nearby checksum-valid addresses one confusable word away |

`words.txt` (the official 27,000-word dictionary) ships with the package and is
required at runtime.

Install: `pip install ./protocol`

License: code MIT; `words.txt` is CC BY-ND 4.0 (see `LICENSE-DICTIONARY.md` in
the repository root).
