import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
test_vectors.py — frozen behavior-preservation vectors.

vectors.json pins (lat, lon, alt_km, words) -> (word address, transfer address)
for a diverse set of points captured from the reference implementation. A valid
address must decode to the same place forever, so any drift in encoder output is
a protocol-breaking bug. This test re-encodes every vector and asserts the exact
strings still come back, and that each address round-trips through decode().

Regenerate ONLY if the protocol geometry/dictionary intentionally changes (which
also changes the protocol version). Run:

    python protocol/tests/test_vectors.py
"""
import json

from protocol import encode_all, decode

HERE = os.path.dirname(os.path.abspath(__file__))
VECTORS = os.path.join(HERE, "vectors.json")

_p = _f = 0
def check(n, cond, d=""):
    global _p, _f; _p += bool(cond); _f += (not cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {n}" + (f"  —  {d}" if d else ""))


def main():
    with open(VECTORS, encoding="utf-8") as fh:
        vectors = json.load(fh)

    print(f"\nFROZEN VECTORS  ({len(vectors)} points)")
    for v in vectors:
        lat, lon, alt_km, words = v["lat"], v["lon"], v["alt_km"], v["words"]
        tag = f"({lat},{lon},{alt_km}km,{words}w)"
        try:
            enc = encode_all(lat, lon, alt_km, words)
        except ValueError as e:
            check(f"{tag} raises as frozen", v.get("address") is None,
                  f"error={e}")
            continue

        if v["address"] is None:
            # frozen as outside the addressable shell
            check(f"{tag} stays outside shell (None)", enc is None,
                  "got a result where None was frozen" if enc else "")
            continue

        check(f"{tag} word address exact", enc is not None and enc["words"] == v["address"],
              v["address"] if enc is None or enc["words"] != v["address"] else "")
        check(f"{tag} transfer address exact",
              enc is not None and enc["transfer"] == v["transfer"],
              v["transfer"] if enc is None or enc["transfer"] != v["transfer"] else "")

        # and it must still decode back to a valid location
        dec = decode(v["address"])
        check(f"{tag} decodes valid", dec.get("valid") is True, dec.get("note", ""))

    print(f"\nSUMMARY: {_p} passed, {_f} failed")
    return _f


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
