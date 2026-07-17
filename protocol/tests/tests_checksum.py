import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
tests_checksum.py — correctness + empirical error-detection rates for Phase 2.

    python tests_checksum.py
"""
import random
from waddr.checksum import checksum, validate, format_transfer, parse_transfer, format_human

rng = random.Random(7)
def rand_addr(n=5):
    return [rng.randint(0, 25459)] + [rng.randint(0, 26999) for _ in range(n - 1)]

_pass = _fail = 0
def check(name, cond, detail=""):
    global _pass, _fail
    _pass += bool(cond); _fail += (not cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  —  {detail}" if detail else ""))

print("\n1. ROUND-TRIP & FORMAT")
a = rand_addr(5)
check("validate accepts correct checksum", validate(a, checksum(a)))
idxs, ok = parse_transfer(format_transfer(a))
check("transfer parse round-trips", idxs == a and ok)
check("human format ends with checksum", format_human(a).endswith("-" + checksum(a)))
check("transfer format starts with checksum", format_transfer(a).startswith(checksum(a) + "-"))

print("\n2. SCALING (one letter per 5 indices)")
check("5 words -> 1 letter", len(checksum(rand_addr(5))) == 1)
check("6 words -> 2 letters", len(checksum(rand_addr(6))) == 2)
check("10 words -> 2 letters", len(checksum(rand_addr(10))) == 2)

print("\n3. EMPIRICAL DETECTION RATES (100,000 trials each)")
N = 100_000

# single-word error: change one position to a different random value
caught = total = 0
for _ in range(N):
    a = rand_addr(5); c = checksum(a)
    pos = rng.randint(0, 4)
    new = rng.randint(0, 25459 if pos == 0 else 26999)
    if new == a[pos]: continue
    b = a[:]; b[pos] = new
    total += 1; caught += (checksum(b) != c)
rate_single = caught / total * 100
check("single-word error detection >= 95%", rate_single >= 95.0, f"{rate_single:.2f}% ({total:,} trials)")

# swap two positions with different values
caught = total = 0
for _ in range(N):
    a = rand_addr(5); c = checksum(a)
    i, j = rng.sample(range(5), 2)
    if a[i] == a[j]: continue
    b = a[:]; b[i], b[j] = b[j], b[i]
    total += 1; caught += (checksum(b) != c)
rate_swap = caught / total * 100
check("swap detection >= 90%", rate_swap >= 90.0, f"{rate_swap:.2f}% ({total:,} trials)")

# adjacent transposition (most common real typo: swap neighbors)
caught = total = 0
for _ in range(N):
    a = rand_addr(5); c = checksum(a)
    i = rng.randint(0, 3)
    if a[i] == a[i+1]: continue
    b = a[:]; b[i], b[i+1] = b[i+1], b[i]
    total += 1; caught += (checksum(b) != c)
rate_adj = caught / total * 100
check("adjacent-transposition detection >= 90%", rate_adj >= 90.0, f"{rate_adj:.2f}% ({total:,} trials)")

print("\n4. CORRUPTION REJECTION")
a = rand_addr(5); t = format_transfer(a)
broke = t.replace("-" + str(a[2]) + "-", "-" + str((a[2] + 1) % 27000) + "-", 1)
_, ok = parse_transfer(broke)
check("corrupted transfer string rejected", not ok)

print(f"\nSUMMARY: {_pass} passed, {_fail} failed")
print(f"detection — single:{rate_single:.2f}%  swap:{rate_swap:.2f}%  adjacent:{rate_adj:.2f}%")