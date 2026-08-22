#!/usr/bin/env bash
# Runs every test suite in this repo and fails if any of them do.
#
# The protocol package must be importable as `waddr`:
#     pip install -e ./protocol
#
# Two styles live side by side:
#   pytest         protocol/tests/test_*.py, backend/tests/test_*.py
#   plain scripts  protocol/tests/tests_*.py — own PASS/FAIL accounting
set -uo pipefail

PY="${PYTHON:-$(command -v python || command -v python3)}"
status=0

echo "=== pytest ==="
"$PY" -m pytest protocol/tests backend/tests -q || status=1

for f in protocol/tests/tests_checksum.py \
         protocol/tests/tests_dictionary.py \
         protocol/tests/tests_edge.py; do
  echo
  echo "=== $f ==="
  "$PY" "$f" || status=1
done

echo
[ "$status" -eq 0 ] && echo "All suites passed." || echo "FAILURES — see above."
exit "$status"
