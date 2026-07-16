"""
protocol — the 3D word-address engine.

The pure spatial/word-address core, with no web dependencies (numpy only).
Callers use the small stable facade re-exported here:

    from protocol import encode_all, encode_words, encode_transfer, decode, alternatives

The `dictionary` submodule exposes runtime metadata (SOURCE, WORD_LIST) for
callers that need it (e.g. a health endpoint):

    from protocol import dictionary
"""
from .address import (
    encode_all,
    encode_words,
    encode_transfer,
    decode,
    alternatives,
)

__version__ = "0.2.0"

__all__ = [
    "encode_all",
    "encode_words",
    "encode_transfer",
    "decode",
    "alternatives",
    "__version__",
]
