import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
test_vectors.py — frozen behavior-preservation vectors.

vectors.json pins (lat, lon, alt_km, words) -> (word address, transfer address)
for a diverse set of points captured from the reference implementation. A valid
address must decode to the same place forever, so any drift in encoder output is
a protocol-breaking bug. This re-encodes every vector and asserts the exact
strings still come back, and that each address round-trips through decode().

Runs two ways:
    pytest protocol/tests/test_vectors.py     # one parametrized case per vector
    python protocol/tests/test_vectors.py      # PASS/FAIL summary, exits nonzero on drift

Regenerate ONLY if the protocol geometry/dictionary intentionally changes (which
also changes the protocol version).
"""
import json

from waddr import encode_all, decode

HERE = os.path.dirname(os.path.abspath(__file__))
VECTORS = os.path.join(HERE, "vectors.json")


def _load():
    with open(VECTORS, encoding="utf-8") as fh:
        return json.load(fh)


def verify_vector(v):
    """Return a list of failure strings for one vector (empty == all good)."""
    lat, lon, alt_km, words = v["lat"], v["lon"], v["alt_km"], v["words"]
    tag = f"({lat},{lon},{alt_km}km,{words}w)"
    fails = []
    try:
        enc = encode_all(lat, lon, alt_km, words)
    except ValueError as e:
        if v.get("address") is not None:
            fails.append(f"{tag} raised {e} but a value was frozen")
        return fails

    if v["address"] is None:
        if enc is not None:
            fails.append(f"{tag} produced a result where None was frozen")
        return fails

    if enc is None:
        fails.append(f"{tag} returned None; expected {v['address']}")
        return fails
    if enc["words"] != v["address"]:
        fails.append(f"{tag} word address drift: {enc['words']} != {v['address']}")
    if enc["transfer"] != v["transfer"]:
        fails.append(f"{tag} transfer drift: {enc['transfer']} != {v['transfer']}")
    dec = decode(v["address"])
    if dec.get("valid") is not True:
        fails.append(f"{tag} does not decode valid ({dec.get('note')})")
    return fails


# --- pytest entry point: one case per frozen vector ---
try:
    import pytest

    @pytest.mark.parametrize("v", _load(), ids=lambda v: f"{v['lat']},{v['lon']},{v['alt_km']},{v['words']}w")
    def test_frozen_vector(v):
        fails = verify_vector(v)
        assert not fails, "; ".join(fails)
except ImportError:
    pass  # pytest not installed — script mode below still works


# --- script entry point: human PASS/FAIL summary ---
def main():
    vectors = _load()
    print(f"\nFROZEN VECTORS  ({len(vectors)} points)")
    all_fails = []
    for v in vectors:
        fails = verify_vector(v)
        all_fails += fails
        for f in fails:
            print(f"  [FAIL] {f}")
    passed = len(vectors) - len({f.split(')')[0] for f in all_fails})
    print(f"\nSUMMARY: {passed}/{len(vectors)} vectors OK, {len(all_fails)} assertion failures")
    return len(all_fails)


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
