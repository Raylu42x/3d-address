"""
dictionary.py — Phase 3 word layer (infrastructure).

Maps cell indices <-> words and assembles/parses the human address format.
Includes support for slightly mistyped words: unknown or wrong words are corrected
against the dictionary, and the checksum is used to pick the right correction.

The real 27,000-word list is generated separately and
dropped in as `words.txt`. If that file is absent, a deterministic PLACEHOLDER list
is generated so the whole pipeline is testable now. The placeholder is NOT the real
dictionary — it exists only to exercise the plumbing.
"""

import os
from .checksum import checksum, validate

NEEDED = 27000


def _dict_path():
    """Locate words.txt whether running from source or pip-installed.

    Prefer importlib.resources (correct for an installed package); fall back to
    a __file__-relative path when this module is executed outside a package.
    """
    try:
        from importlib.resources import files
        return str(files(__package__).joinpath("words.txt"))
    except Exception:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "words.txt")


DICT_PATH = _dict_path()


# --- load or synthesize the word list ---
def _placeholder(n=NEEDED):
    """Deterministic CVCVC pseudo-words. Pronounceable-ish, all distinct."""
    C = "bdfghjklmnprstvwz"   # 17 consonants (excludes c,q,x,y to reduce confusion)
    V = "aeiou"               # 5 vowels
    out = []
    for c1 in C:
        for v1 in V:
            for c2 in C:
                for v2 in V:
                    for c3 in C:
                        out.append(c1 + v1 + c2 + v2 + c3)
                        if len(out) >= n:
                            return out
    return out


def load_words(path=DICT_PATH):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            words = [w.strip().lower() for w in f if w.strip()]
        return words, "file"
    return _placeholder(), "placeholder"


WORD_LIST, SOURCE = load_words()
if len(WORD_LIST) < NEEDED:
    raise ValueError(f"dictionary needs >= {NEEDED} words, got {len(WORD_LIST)}")

WORD_TO_INDEX = {w: i for i, w in enumerate(WORD_LIST)}
INDEX_TO_WORD = WORD_LIST


# --- basic maps ---
def to_words(indices):
    return [INDEX_TO_WORD[i] for i in indices]


def to_indices(words):
    """Exact lookup. Raises KeyError on an unknown word."""
    return [WORD_TO_INDEX[w.lower()] for w in words]


# --- fuzzy matching (Levenshtein with cutoff) ---
def _lev(a, b, maxd):
    if abs(len(a) - len(b)) > maxd:
        return maxd + 1
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i] + [0] * len(b)
        best = cur[0]
        for j, cb in enumerate(b, 1):
            cur[j] = min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb))
            if cur[j] < best:
                best = cur[j]
        if best > maxd:
            return maxd + 1
        prev = cur
    return prev[-1]


def _scan(word, maxd, limit, drop_exact):
    word = word.lower().strip()
    cands = []
    for w in WORD_LIST:
        d = _lev(word, w, maxd)
        if d <= maxd and not (drop_exact and d == 0):
            cands.append((d, w))
    cands.sort()
    return [(w, WORD_TO_INDEX[w], d) for d, w in cands[:limit]]


def suggest(word, maxd=2, limit=5):
    """Nearest dictionary words to a TYPED word as (word, index, distance).
    If the word is already valid, returns just that word."""
    word = word.lower().strip()
    if word in WORD_TO_INDEX:
        return [(word, WORD_TO_INDEX[word], 0)]
    return _scan(word, maxd, limit, drop_exact=False)


def neighbors(word, maxd=2, limit=8):
    """Nearby OTHER dictionary words (excludes the word itself). Used to recover
    from a typo that happened to land on a valid-but-wrong word."""
    return _scan(word, maxd, limit, drop_exact=True)


# --- address assembly / parsing ---
def make_address(indices):
    """Human format: 'word-word-...-C'."""
    return "-".join(to_words(indices)) + "-" + checksum(indices)


def _single_fix(idxs, check):
    """All words known but checksum fails: find one position whose nearby word
    makes the checksum valid (handles a typo that landed on a valid wrong word)."""
    for pos in range(len(idxs)):
        for nw, ni, d in neighbors(INDEX_TO_WORD[idxs[pos]]):
            trial = idxs[:]
            trial[pos] = ni
            if validate(trial, check):
                return pos, nw, ni
    return None


def read_address(text):
    """
    Parse a human word address with single-typo autocorrection driven by the checksum.

    Returns a dict:
        indices     : resolved cell indices (best effort)
        words       : resolved words
        valid       : checksum passed (possibly after correction)
        corrections : {typed_word: corrected_word}
        suggestions : {unknown_word: [candidates]}  (only when it couldn't resolve)
        note        : how it was resolved
    """
    parts = text.strip().lower().split("-")
    if len(parts) < 2:
        return {"valid": False, "error": "address too short"}
    *words, check = parts
    check = check.upper()

    idxs, unknown = [], []
    for k, w in enumerate(words):
        if w in WORD_TO_INDEX:
            idxs.append(WORD_TO_INDEX[w])
        else:
            idxs.append(None)
            unknown.append(k)

    # case A: every word known
    if not unknown:
        if validate(idxs, check):
            return {"indices": idxs, "words": words, "valid": True,
                    "corrections": {}, "note": "exact"}
        fix = _single_fix(idxs, check)
        if fix:
            pos, nw, ni = fix
            idxs2 = idxs[:]; idxs2[pos] = ni
            return {"indices": idxs2, "words": to_words(idxs2), "valid": True,
                    "corrections": {words[pos]: nw}, "note": "checksum-corrected"}
        return {"indices": idxs, "words": words, "valid": False,
                "corrections": {}, "note": "checksum failed, no single fix"}

    # case B: exactly one unknown word -> try its candidates, keep the one that validates
    if len(unknown) == 1:
        pos = unknown[0]
        for nw, ni, d in suggest(words[pos]):
            trial = idxs[:]; trial[pos] = ni
            if None not in trial and validate(trial, check):
                return {"indices": trial, "words": to_words(trial), "valid": True,
                        "corrections": {words[pos]: nw}, "note": "typo-corrected"}
        return {"indices": idxs, "words": words, "valid": False,
                "suggestions": {words[pos]: [s[0] for s in suggest(words[pos])]},
                "note": "unknown word, no checksum-valid candidate"}

    # case C: several unknown words -> just offer suggestions
    return {"indices": idxs, "words": words, "valid": False,
            "suggestions": {words[k]: [s[0] for s in suggest(words[k])] for k in unknown},
            "note": "multiple unknown words"}


if __name__ == "__main__":
    # demo; run with `python -m waddr.dictionary`
    from .encoder import encode
    print(f"dictionary source: {SOURCE}  ({len(WORD_LIST):,} words)")
    idx = encode(51.5074, -0.1278, 0.1, 5)
    addr = make_address(idx)
    print("address  :", addr)
    print("read back:", read_address(addr))
    # corrupt one word and watch it self-correct
    parts = addr.split("-")
    parts[1] = "x" + parts[1][1:]   # break word 2 into a non-dictionary token
    broken = "-".join(parts)
    print("broken   :", broken)
    print("corrected:", read_address(broken))