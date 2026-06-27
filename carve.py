"""
carve.py — level-1 carving (the valid / invalid table).

Generates the fixed table of valid level-1 cells: the 41x41x41 cube grid with every
cell that does not touch the shell removed. Valid cells are numbered 0..24,459... in
the protocol's raster order (top layer first, then Y, then X).

Run directly to print statistics:
    python carve.py
"""

import numpy as np
from geometry import N1, CELL1, HALF, INNER, OUTER, DICT_SIZE


def build_valid_table():
    """
    Returns:
        valid     : bool array (N1,N1,N1) indexed [ix,iy,iz] (iz from bottom)
        raw2word  : int32 array (N1,N1,N1); word index for each cell, -1 if invalid
        word2raw  : list of (ix,iy,iz) indexed by word index
    """
    c1 = -HALF + (np.arange(N1) + 0.5) * CELL1
    lo = c1 - CELL1 / 2.0
    hi = c1 + CELL1 / 2.0
    near = np.where((lo <= 0) & (0 <= hi), 0.0, np.minimum(np.abs(lo), np.abs(hi)))
    far = np.maximum(np.abs(lo), np.abs(hi))

    NX = near[:, None, None]; NY = near[None, :, None]; NZ = near[None, None, :]
    FX = far[:, None, None];  FY = far[None, :, None];  FZ = far[None, None, :]
    minD = np.sqrt(NX**2 + NY**2 + NZ**2)   # nearest point of cell to core
    maxD = np.sqrt(FX**2 + FY**2 + FZ**2)   # farthest point of cell to core

    # touching the shell band counts as valid (full coverage)
    valid = ~((maxD <= INNER) | (minD >= OUTER))

    # assign word indices in raster order: top layer first (max Z), then Y, then X
    raw2word = -np.ones((N1, N1, N1), dtype=np.int32)
    word2raw = []
    w = 0
    for iztop in range(N1):
        iz = N1 - 1 - iztop
        for iy in range(N1):
            for ix in range(N1):
                if valid[ix, iy, iz]:
                    raw2word[ix, iy, iz] = w
                    word2raw.append((ix, iy, iz))
                    w += 1
    return valid, raw2word, word2raw


def stats():
    valid, raw2word, word2raw = build_valid_table()
    n = len(word2raw)
    return {
        "total_cells": int(N1**3),
        "valid_cells": n,
        "dictionary": DICT_SIZE,
        "unclaimed_words": DICT_SIZE - n,
        "level1_cell_km": CELL1,
    }


if __name__ == "__main__":
    s = stats()
    print(f"level-1 grid      : {N1}^3 = {s['total_cells']:,} cells")
    print(f"level-1 cell edge : {s['level1_cell_km']:.2f} km")
    print(f"valid cells       : {s['valid_cells']:,}")
    print(f"dictionary        : {s['dictionary']:,}")
    print(f"unclaimed words   : {s['unclaimed_words']:,}")
