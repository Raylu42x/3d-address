"""
checksum.py — Phase 2 error-detection layer.

A weighted-modular checksum over the cell-index list, emitted as A-Z letter(s).
Order matters (each position has a distinct weight), so the checksum catches both
single mistyped words and transposed/swapped words.

Scaling (per spec): one letter per group of 5 indices.
    1-5 words   -> 1 letter
    6-10 words  -> 2 letters
    etc.

Placement:
    human format    : word-word-word-word-C    (checksum LAST)
    transfer format : C-num-num-num-num         (checksum FIRST)

This module operates on index lists; the word layer arrives in Phase 3.
"""

# Weights are coprime to 26 (all odd, none equal to 13) so that a single-index
# error is invisible only when the index changes by an exact multiple of 26 --
# the best a single base-26 letter can do. No two weights differ by 13 or 26,
# which keeps swap detection at its ceiling too.
WEIGHTS = (3, 5, 7, 9, 11)
ALPHA = 26
GROUP = 5
_A = ord('A')


def _letter(group):
    s = sum(idx * WEIGHTS[i] for i, idx in enumerate(group))
    return chr(_A + (s % ALPHA))


def checksum(indices):
    """Return the checksum string (one letter per 5 indices)."""
    if not indices:
        raise ValueError("need at least one index")
    return ''.join(_letter(indices[g:g + GROUP]) for g in range(0, len(indices), GROUP))


def validate(indices, check):
    """True if `check` matches the checksum of `indices`."""
    return checksum(indices) == check


def format_transfer(indices):
    """Machine format: 'C-num-num-...' (checksum first)."""
    return checksum(indices) + '-' + '-'.join(str(i) for i in indices)


def parse_transfer(s):
    """Parse 'C-num-num-...' -> (indices, ok). ok is False if the checksum fails."""
    parts = s.strip().split('-')
    check, nums = parts[0], parts[1:]
    indices = [int(p) for p in nums]
    return indices, validate(indices, check)


def format_human(indices):
    """
    Human layout with checksum LAST. Until the Phase 3 dictionary lands, indices
    stand in for words: 'num-num-num-num-C'.
    """
    return '-'.join(str(i) for i in indices) + '-' + checksum(indices)


if __name__ == "__main__":
    # demo; run with `python -m waddr.checksum`
    from .encoder import encode
    idx = encode(51.5074, -0.1278, 0.1, 5)   # London
    print("indices  :", idx)
    print("checksum :", checksum(idx))
    print("transfer :", format_transfer(idx))
    print("human    :", format_human(idx))
    back, ok = parse_transfer(format_transfer(idx))
    print("re-parsed:", back, "valid:", ok)