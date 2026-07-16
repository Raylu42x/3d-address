# Dictionary & Specification License

The following files are **not** covered by the MIT license in `LICENSE`:

- `words.txt` — the official 27,000-word protocol dictionary
- `docs/SPEC_v0.2.md` — the protocol specification

These are licensed under **Creative Commons Attribution-NoDerivatives 4.0
International (CC BY-ND 4.0)**: https://creativecommons.org/licenses/by-nd/4.0/

## What this means

**You may:**
- Use the dictionary and specification for any purpose, including commercially
- Copy and redistribute them **verbatim**, in any medium or format
- Implement the protocol in your own software (implementations are your own
  code and are not derivatives of these files)

**You may not:**
- Distribute a modified version of the dictionary or the specification

## Why

Every address in this protocol depends on all implementations sharing the exact
same dictionary (word N must mean the same cell everywhere) and the exact same
geometry. A modified dictionary or spec produces addresses that silently point
to the wrong place while looking valid. Freezing these files is what makes the
addresses trustworthy and interoperable.

## Compatibility policy

An implementation may claim compatibility with this protocol only if it fully
conforms to the published specification and uses the official unmodified
dictionary. Implementations that intentionally modify the protocol or
dictionary should use a different protocol name to avoid confusion.

Future revisions of this specification, if any, will be published as new
versioned documents. Existing versions remain immutable.