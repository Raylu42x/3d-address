"""
validate_wordlist.py — mechanical checks for a candidate dictionary.

Run on the agent's output before adopting it:
    python validate_wordlist.py words.txt

Checks the rules a script CAN verify: count, charset, length, duplicates, and the number
of risky single-edit-distance pairs. Human-judgment rules (offensiveness, homophones,
cultural neutrality) still need a human/agent review — this only catches mechanical issues.
"""
import sys
import re

NEEDED = 27000
PATTERN = re.compile(r"^[a-z]{3,7}$")


def load(path):
    with open(path, encoding="utf-8") as f:
        return [ln.strip() for ln in f if ln.strip()]


def edit1_pairs(words, cap=200000):
    """Count pairs at Levenshtein distance 1 using the deletion-neighborhood trick
    (fast, no O(n^2) scan). Returns the count of colliding pairs."""
    from collections import defaultdict
    buckets = defaultdict(list)
    for w in words:
        # substitutions/same-length: bucket by each position blanked
        for i in range(len(w)):
            buckets[(len(w), i, w[:i] + "*" + w[i + 1:])].append(w)
        # insertions/deletions: bucket by each single deletion
        for i in range(len(w)):
            buckets[("del", w[:i] + w[i + 1:])].append(w)
    pairs = set()
    for group in buckets.values():
        if len(group) > 1:
            for a in range(len(group)):
                for b in range(a + 1, len(group)):
                    pairs.add(tuple(sorted((group[a], group[b]))))
                    if len(pairs) >= cap:
                        return len(pairs), True
    return len(pairs), False


def main(path):
    words = load(path)
    print(f"file: {path}")
    print(f"lines (non-empty): {len(words):,}")

    ok = True
    def rule(name, cond, detail=""):
        nonlocal ok
        ok &= cond
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  —  {detail}" if detail else ""))

    rule(f"exactly {NEEDED:,} words", len(words) == NEEDED, f"got {len(words):,}")

    bad = [w for w in words if not PATTERN.match(w)]
    rule("charset/length (^[a-z]{3,7}$)", not bad,
         "all valid" if not bad else f"{len(bad)} bad, e.g. {bad[:5]}")

    dupes = len(words) - len(set(words))
    rule("no duplicates", dupes == 0, "unique" if dupes == 0 else f"{dupes} duplicate(s)")

    n_pairs, capped = edit1_pairs(words)
    pct = n_pairs / max(len(words), 1) * 100
    suffix = "+ (capped)" if capped else ""
    # advisory, not a hard fail — flag if a large fraction are confusable
    rule("single-edit pairs are rare (< 5% of size)", pct < 5.0,
         f"{n_pairs:,}{suffix} risky pairs (~{pct:.1f}% of list)")

    print(f"\n{'ALL MECHANICAL CHECKS PASSED' if ok else 'SOME CHECKS FAILED'}")
    print("Reminder: offensiveness, homophones, and cultural neutrality still need review.")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python validate_wordlist.py <words.txt>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
    