"""
address.py — the facade.

One place that ties the spatial core (encoder), the error-detection layer (checksum),
and the word layer (dictionary) into a small, stable API. The API server and UI call
ONLY these functions, never the internals.

    encode_words(lat, lon, alt_km, words)    -> "word-word-...-C"      (or None)
    encode_transfer(lat, lon, alt_km, words) -> "C-num-num-..."        (or None)
    encode_all(lat, lon, alt_km, words)      -> {words, transfer, indices}  (or None)
    decode(text)                             -> {valid, lat, lon, alt_km, ...}

`None` from an encode means the point is outside the addressable shell.
"""
from encoder import encode as _encode, decode as _decode
from checksum import format_transfer, parse_transfer
import dictionary as D


# ---------- encode ----------
def encode_all(lat, lon, alt_km=0.0, words=5):
    # validate inputs up front so bad coordinates are rejected, not silently
    # remapped (lat=100 wrapping onto a real latitude, etc.)
    if not (-90.0 <= lat <= 90.0):
        raise ValueError("latitude must be between -90 and 90")
    if not (-180.0 <= lon <= 180.0):
        raise ValueError("longitude must be between -180 and 180")
    idx = _encode(lat, lon, alt_km, words)
    if idx is None:
        return None
    info = {
        "indices": idx,
        "words": D.make_address(idx),
        "transfer": format_transfer(idx),
    }
    info.update(_geo(idx))   # cell-center lat/lon/alt + cell_edge_m + words_used
    return info


def encode_words(lat, lon, alt_km=0.0, words=5):
    r = encode_all(lat, lon, alt_km, words)
    return r["words"] if r else None


def encode_transfer(lat, lon, alt_km=0.0, words=5):
    r = encode_all(lat, lon, alt_km, words)
    return r["transfer"] if r else None


# ---------- decode ----------
def _geo(idx):
    (lat, lon, alt), edge_km = _decode(idx)
    return {"lat": lat, "lon": lon, "alt_km": alt,
            "cell_edge_m": edge_km * 1000.0, "words_used": len(idx)}


def _looks_like_transfer(text):
    parts = text.strip().split("-")
    return len(parts) >= 2 and parts[0].isalpha() and all(p.isdigit() for p in parts[1:])


def decode_transfer(text):
    idx, ok = parse_transfer(text)
    out = {"valid": ok, "format": "transfer", "indices": idx}
    if ok:
        out.update(_geo(idx))
    return out


def decode_words(text):
    r = D.read_address(text)
    if not r.get("valid"):
        return {"valid": False, "format": "words",
                **{k: r[k] for k in ("suggestions", "corrections", "note", "error") if k in r}}
    out = {"valid": True, "format": "words", "indices": r["indices"],
           "words": r["words"], "corrections": r.get("corrections", {}),
           "note": r.get("note")}
    out.update(_geo(r["indices"]))
    return out


def decode(text):
    """Auto-detect transfer vs word format and decode."""
    text = (text or "").strip()
    if not text:
        return {"valid": False, "error": "empty address"}
    return decode_transfer(text) if _looks_like_transfer(text) else decode_words(text)


def alternatives(text, max_results=24):
    """
    'That doesn't look right' — plausible alternative addresses for a word address.

    For each word position, substitute nearby dictionary words (edit distance <= 2)
    and keep combinations whose checksum still validates. Each result carries:
      - position: which word changed (0-based) — early words move the address far,
        late words move it slightly, so distance-from-shown diagnoses the bad word
      - distance_km: how far the alternative lands from the typed address's decode
      - alt_km: altitude (used to weight results toward ground level)

    Sorted by: near-ground first, then smaller edit distance.
    """
    import math
    from checksum import validate as _validate
    from geometry import geo_to_xyz
    parts = (text or "").strip().lower().split("-")
    if len(parts) < 2:
        return []
    *words, check = parts
    check = check.upper()

    try:
        base = [D.WORD_TO_INDEX[w] for w in words]
    except KeyError:
        return []  # unknown word; normal decode suggestions handle that case

    (blat, blon, balt), _ = _decode(base)
    bx, by, bz = geo_to_xyz(blat, blon, balt)

    out, seen = [], set()
    for pos in range(len(words)):
        for nw, ni, dist in D.neighbors(words[pos], maxd=2, limit=40):
            trial = base[:]
            trial[pos] = ni
            key = tuple(trial)
            if key in seen or trial == base:
                continue
            seen.add(key)
            if not _validate(trial, check):
                continue
            (lat, lon, alt), edge_km = _decode(trial)
            x, y, z = geo_to_xyz(lat, lon, alt)
            out.append({
                "words": "-".join(D.to_words(trial)) + "-" + check,
                "changed": {words[pos]: nw},
                "position": pos,
                "distance": dist,
                "distance_km": math.sqrt((x-bx)**2 + (y-by)**2 + (z-bz)**2),
                "lat": lat, "lon": lon, "alt_km": alt,
                "cell_edge_m": edge_km * 1000.0,
            })
    # weight toward ground level (plausible addresses live near the surface),
    # then prefer the smallest typo
    out.sort(key=lambda r: (abs(r["alt_km"]), r["distance"]))
    return out[:max_results]


if __name__ == "__main__":
    r = encode_all(51.5074, -0.1278, 0.1, 5)
    print("encode_all:", r)
    print("decode words:", decode(r["words"]))
    print("decode transfer:", decode(r["transfer"]))