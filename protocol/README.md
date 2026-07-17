# waddr — 3D word-address engine

The pure encoding/decoding core of the 3D word-based address protocol. Maps any
point in the near-Earth shell (≈13 km underground to 2,000 km altitude) to a
short, human-readable word address and back. No web dependencies — **numpy only**.

Addresses are **stable forever**: the dictionary and geometry are frozen, so a
valid address decodes to the same place in every version and every install.

- 🌐 **Try the web app:** [address.kervian.com](https://address.kervian.com)
- 📦 **Source & self-hosting:** [github.com/Raylu42x/3d-address](https://github.com/Raylu42x/3d-address)

## Install

```bash
pip install waddr
```

Only dependency is `numpy`. The official 27,000-word dictionary (`words.txt`)
ships inside the wheel and loads automatically — nothing else to download.

## Quickstart

```python
from waddr import encode_all, decode

info = encode_all(51.5074, -0.1278, alt_km=0.1, words=5)
print(info["words"])                  # e.g. dinosaur-epidural-usable-bingo-dusty-C
print(info["transfer"])               # e.g. C-4452-12644-6220-4824-5130

loc = decode(info["words"])
print(loc["lat"], loc["lon"], loc["alt_km"])   # back to coordinates
```

More or fewer words trade precision for length — 3 words ≈ a city block,
5 ≈ a doorway, 7 ≈ sub-millimeter:

```python
from waddr import encode_words

encode_words(47.6205, -122.3493, alt_km=0.0, words=3)   # ~460 m cell
encode_words(47.6205, -122.3493, alt_km=0.0, words=7)   # ~0.6 mm cell
```

## Public API

| function | purpose |
|----------|---------|
| `encode_all(lat, lon, alt_km=0.0, words=5)` | full result: `words`, `transfer`, `indices`, decoded center, cell size |
| `encode_words(...)` | just the `word-word-...-C` string |
| `encode_transfer(...)` | just the `C-num-num-...` machine string |
| `decode(text)` | auto-detects word/transfer format → location |
| `alternatives(text)` | nearby checksum-valid addresses one confusable word away |

`encode_*` return `None` for points outside the addressable shell (altitude
below −13 km or above +2,000 km). Word addresses carry a checksum letter that
catches typos, and `decode` auto-corrects a single mistyped word when it can.

## License

Split license:

- **Code — MIT.**
- **`words.txt` (the dictionary) — CC BY-ND 4.0.** Redistribute freely, but
  modified versions may not be distributed: every implementation must share the
  identical dictionary or addresses silently break between installs. See
  [`LICENSE-DICTIONARY.md`](https://github.com/Raylu42x/3d-address/blob/main/LICENSE-DICTIONARY.md).
