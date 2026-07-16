import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
tests_dictionary.py — Phase 3 plumbing tests (run against the placeholder list).

    python tests_dictionary.py
"""
import random
from encoder import encode, decode
import dictionary as D

rng = random.Random(11)
_pass = _fail = 0
def check(name, cond, detail=""):
    global _pass, _fail
    _pass += bool(cond); _fail += (not cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  —  {detail}" if detail else ""))

print(f"\ndictionary source: {D.SOURCE}  ({len(D.WORD_LIST):,} words)")

print("\n1. MAPS ARE BIJECTIVE")
check("word_to_index size == word_list size", len(D.WORD_TO_INDEX) == len(D.WORD_LIST),
      f"{len(D.WORD_TO_INDEX):,} unique of {len(D.WORD_LIST):,} (no duplicate words)")
sample = [rng.randint(0, 26999) for _ in range(1000)]
check("index -> word -> index round-trips", D.to_indices(D.to_words(sample)) == sample)

print("\n2. ADDRESS ASSEMBLY")
idx = encode(40.7128, -74.0060, 0.05, 5)        # New York
addr = D.make_address(idx)
r = D.read_address(addr)
check("make/read exact round-trip", r["valid"] and r["indices"] == idx, addr)

print("\n3. TYPO CORRECTION (unknown word)")
parts = addr.split("-")
parts[2] = "x" + parts[2][1:]                   # corrupt word 3 into a non-word
r = D.read_address("-".join(parts))
check("single unknown word self-corrects", r["valid"] and r["indices"] == idx,
      f"corrected {r.get('corrections')}")

print("\n4. CHECKSUM-DRIVEN FIX (typo landed on a valid wrong word)")
# replace word 2 with a near valid word -> all known, checksum should fail then fix
near = D.neighbors(D.INDEX_TO_WORD[idx[1]], maxd=1, limit=5)
alt = next((w for w, i, d in near if i != idx[1]), None)
if alt:
    parts = D.to_words(idx)[:]; parts[1] = alt
    broken = "-".join(parts) + "-" + addr.split("-")[-1]
    r = D.read_address(broken)
    check("valid-but-wrong word corrected via checksum", r["valid"] and D.validate(r["indices"], addr.split("-")[-1]),
          f"note={r.get('note')}, corrections={r.get('corrections')}")
else:
    check("valid-but-wrong word corrected via checksum", False, "no near word found")

print("\n5. UNRESOLVABLE INPUT -> SUGGESTIONS, NOT A WRONG ANSWER")
parts = addr.split("-")
parts[1] = "xx" + parts[1][2:]; parts[3] = "xx" + parts[3][2:]   # two unknown words
r = D.read_address("-".join(parts))
check("multiple unknown words flagged invalid", not r["valid"] and "suggestions" in r,
      f"suggested for {list(r.get('suggestions', {}).keys())}")

print("\n6. FULL INTEGRATION: geo -> words -> geo")
lat, lon, alt = 35.6762, 139.6503, 0.04          # Tokyo
idx = encode(lat, lon, alt, 5)
addr = D.make_address(idx)
back = D.read_address(addr)
(dlat, dlon, dalt), edge = decode(back["indices"])
import math
x1, y1, z1 = __import__("geometry").geo_to_xyz(lat, lon, alt)
x2, y2, z2 = __import__("geometry").geo_to_xyz(dlat, dlon, dalt)
err = math.sqrt((x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2) * 1000
check("Tokyo geo->address->geo within cell", err <= edge*1000*math.sqrt(3)/2 + 1e-6,
      f"address={addr}  err={err:.2f}m")

print(f"\nSUMMARY: {_pass} passed, {_fail} failed")