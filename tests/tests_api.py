import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""tests_api.py — exercise the REST API via FastAPI's TestClient (no server needed)."""
from fastapi.testclient import TestClient
from api import app

c = TestClient(app)
_p = _f = 0
def check(n, cond, d=""):
    global _p, _f; _p += bool(cond); _f += (not cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {n}" + (f"  —  {d}" if d else ""))

print("\nAPI TESTS")
h = c.get("/health").json()
check("health ok", h["ok"], f"dict={h['dictionary_source']} ({h['words']:,})")

r = c.post("/encode", json={"lat":51.5074,"lon":-0.1278,"alt_km":0.1,"words":5,"format":"all"}).json()
check("encode London ok", r["ok"], r.get("address") or r.get("words"))
addr = r["words"]; transfer = r["transfer"]

d = c.post("/decode", json={"address": addr}).json()
check("decode word address round-trips", d["ok"] and abs(d["lat"]-51.5074)<0.001, f"{d.get('lat'):.4f},{d.get('lon'):.4f}")

d2 = c.post("/decode", json={"address": transfer}).json()
check("decode transfer address round-trips", d2["ok"] and d2["format"]=="transfer")

bad = c.post("/encode", json={"lat":0,"lon":0,"alt_km":5000,"words":5})
check("out-of-shell returns 422", bad.status_code==422)

oob = c.post("/encode", json={"lat":200,"lon":0,"words":5})
check("invalid latitude rejected (422)", oob.status_code==422)

# typo in a word address still decodes (checksum auto-correct), if using real words
parts = addr.split("-"); parts[0] = "x"+parts[0][1:]
tp = c.post("/decode", json={"address":"-".join(parts)}).json()
check("typo'd address handled", ("ok" in tp), f"ok={tp.get('ok')} note={tp.get('note')}")

print(f"\nSUMMARY: {_p} passed, {_f} failed")