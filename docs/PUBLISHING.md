# Publishing the `waddr` package to PyPI

The protocol engine ships as the pip-installable **`waddr`** package (import name
and distribution name are both `waddr`; the source lives in `protocol/`).

## Build the distributables

```bash
python -m pip install --upgrade build twine
cd protocol
rm -rf dist build *.egg-info      # start clean
python -m build                   # -> dist/waddr-<version>-py3-none-any.whl
                                  #    dist/waddr-<version>.tar.gz
```

The wheel is self-contained: it bundles `words.txt` as package data, so
`from waddr import encode_all, decode, alternatives` works and the dictionary
loads with no extra files. Only runtime dependency is `numpy`.

## Verify before publishing

```bash
# metadata / rendering check
python -m twine check dist/*

# install the built wheel (NOT the source dir) into a throwaway venv
python -m venv /tmp/waddr-check
/tmp/waddr-check/bin/pip install dist/waddr-*.whl
/tmp/waddr-check/bin/python -c "from waddr import encode_all, decode, alternatives; \
  print(encode_all(51.5074, -0.1278, 0.1, 5)['words'])"
```

## Publish (when ready)

Test index first (recommended):

```bash
python -m twine upload --repository testpypi dist/*
```

Then the real index:

```bash
python -m twine upload dist/*
```

You'll need a PyPI account and an API token (set `TWINE_USERNAME=__token__` and
`TWINE_PASSWORD=<your-pypi-token>`, or let twine prompt you).

## Versioning

Bump `version` in `protocol/pyproject.toml` **and** `__version__` in
`protocol/__init__.py` together. The version tracks the protocol spec (currently
`0.2.x`). Because addresses must stay stable forever, a version bump must never
change encoder output — `pytest protocol/tests/test_vectors.py` must stay green
across the bump. PyPI refuses to overwrite an already-published version, so every
upload needs a fresh version number.
