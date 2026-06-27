# 3D Word-Based Address Protocol — Specification v0.2

A universal, open, 3D addressing protocol. Every point in the near-Earth shell maps
to a short, human-readable, machine-friendly address. This supersedes the v0.1 concept
document; all numbers below reflect the corrected geometry.

---

## 1. Bounding volume

The addressable space is a **hollow spherical shell** centered on Earth's core,
implemented inside an axis-aligned cube.

| Quantity            | Value        | Notes                                   |
|---------------------|--------------|-----------------------------------------|
| Cube width          | 17,000 km    | Half-width 8,500 km                      |
| Inner radius        | 6,358 km     | Earth mean radius (6,371) − 13 km (~8 mi)|
| Outer radius        | 8,371 km     | Earth mean radius + 2,000 km (LEO ceiling)|
| Mean Earth radius   | 6,371 km     | Altitude reference (alt = r − 6,371)     |

Valid altitude range: **−13 km to +2,000 km**. Everything inside the inner sphere
(Earth's interior) and outside the outer sphere (deep space, cube corners) is unaddressable.

---

## 2. Axis orientation

A single fixed Earth-Centered frame. Axes follow the right-hand rule (Z = X × Y):

- **+Z** → North Pole (cube "up")
- **+Y** → 0° longitude at the equator (the London meridian, pointing outward through the core)
- **+X** → 90° E at the equator

Position of a geographic point (latitude φ, longitude λ, altitude a), with r = 6,371 + a:

```
X = r · cos(φ) · sin(λ)      # +X at 90° E
Y = r · cos(φ) · cos(λ)      # +Y at London (λ = 0)
Z = r · sin(φ)               # +Z at North Pole
```

Inverse:

```
r   = √(X² + Y² + Z²)
φ   = asin(Z / r)
λ   = atan2(X, Y)
alt = r − 6,371
```

### Known property: cell tilt
Because the grid is locked to this fixed frame, cells are only "level" with the local
ground at the six points where a cube axis pierces the sphere (both poles, ±Y, ±X).
Everywhere else the cells are tilted relative to the local horizon. **This does not affect
positioning** — every point still maps to exactly one cell with uniform size. The only
consequence: vertical cell-neighbors run along global Z, not local "up," so true altitude
must be derived from the cell-center radius, not from the vertical index.

---

## 3. Subdivision and dictionary

- **Dictionary size:** 27,000 words = 30³ (chosen to equal the recursive subdivision factor).
- **Level-1 grid:** the cube is divided into **41 × 41 × 41 = 68,921** cells.
  After carving (Section 4), **25,460** are valid and receive word indices 0–25,459.
  The remaining **1,540** dictionary words are unclaimed (reserved for future use:
  city/landmark shortcuts, or a finer grid).
- **Levels 2 and deeper:** each cell subdivides into **30 × 30 × 30 = 27,000** children.
  Every child is addressable — no carving below level 1 — which is why the dictionary is
  exactly 27,000.

### Precision (per added word)

| Words | Cell edge   | Real-world scale          |
|-------|-------------|---------------------------|
| 1     | 414.63 km   | Country / large region     |
| 2     | 13.82 km    | City                       |
| 3     | 460.70 m    | Neighborhood / block       |
| 4     | 15.36 m (≈50 ft) | **Property / single home** |
| 5     | 51.19 cm    | Door / parking spot        |
| 6     | 1.71 cm     | Hand / device              |
| 7     | 0.57 mm     | Robotics / engineering     |

**Human standard:** 5 words. **Machine standard:** 6+ words.

---

## 4. Validity rule (carving)

A level-1 cell is **valid** if it touches the shell band at all (partial overlap counts):

- Compute the cell's nearest distance `minD` and farthest distance `maxD` from the core
  (axis-aligned box vs. point).
- **Invalid** if `maxD ≤ INNER` (entirely inside Earth) **or** `minD ≥ OUTER` (entirely in space).
- **Valid** otherwise.

Partial cells are kept so the shell is fully covered with no gaps. The result is a fixed
table of 25,460 valid cells; this is a one-time precompute.

---

## 5. Encoding order

Word indices are assigned to valid level-1 cells in this raster order:

1. **Top layer first** — start at the highest-Z layer, work downward.
2. Within a layer, **minimum-Y to maximum-Y**.
3. Within a row, **minimum-X to maximum-X** (X sweeps fastest).

Origin corner = (min X, min Y, top Z) — the "Atlantic-side" top corner.

For levels 2+, the same top-down / Y / X order maps a child (cx, cy, cz) to an index:

```
child_index = (29 − cz) · 900 + cy · 30 + cx        # cz measured from bottom
```

---

## 6. Address formats

- **Human:**  `word-word-word-word-C`  (checksum letter last)
  e.g. `apple-river-cloud-stone-Q`
- **Machine / data transfer:**  `C-num-num-num-num`  (checksum letter first, raw dictionary indices)
  e.g. `Q-4452-12644-6220-4824`

Separator: dash (`-`). Words lowercase. The dictionary is optional for machines — they
exchange indices directly and never need the word list.

---

## 7. Checksum

A single letter **A–Z** (26 values), placed last in human format and first in transfer
format. Weighted modular checksum over the word indices so that order matters and swaps
are detected:

```
C = ( Σ  wᵢ · pᵢ )  mod 26          →  map 0–25 to A–Z
```

where `pᵢ` are distinct weights (e.g. small primes 3, 5, 7, 11, 13, …). Scales: 1 letter
for 1–5 words, 2 letters for 6–10, etc. (Full algorithm finalized in Phase 4.)

---

## 8. Versioning

The spec is **not** designed for in-place revision — addresses are not version-tagged.
The geometry, dictionary, ordering, and checksum must be correct from launch and then
frozen. Future extension happens only by *adding* optional capability (reserved prefix
words, extra checksum letters), never by changing existing behavior.

---

## 9. Reserved for future (not in MVP)

- `orbit.` prefix — beyond LEO (MEO/GEO+), 6+ words, machine-only.
- `deep.` prefix — below −13 km, 6+ words, machine-only.
- City / landmark shortcut words drawn from the 1,540 unclaimed indices.

---

## 10. Baseline (v0.2)

| Parameter            | Value                          |
|----------------------|--------------------------------|
| Cube width           | 17,000 km                      |
| Inner / outer radius | 6,358 km / 8,371 km            |
| Level-1 grid         | 41³ = 68,921 cells             |
| Valid level-1 cells  | 25,460 (1,540 words unclaimed) |
| Subdivision factor   | 30³ = 27,000 per added word    |
| Dictionary size      | 27,000 words                   |
| Human standard       | 5 words + checksum letter      |
| Status               | Geometry frozen; Phase 1 implemented |
