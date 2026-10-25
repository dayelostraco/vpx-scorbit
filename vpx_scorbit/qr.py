"""Publish SDK-supplied links; never construct guessed pairing URLs."""

import os
from pathlib import Path


def write_qr(link, path):
    """Atomically replace a PNG with an exact supplied link and four-module quiet zone.

    Reject empty/multiline text. The caller owns the private path and provenance
    of the link; validation here does not establish that a URI is a pairing code.
    Uses a fixed temporary sibling, so concurrent writers to one path are unsupported.
    """
    import qrcode

    if not link or any(c in link for c in "\r\n"):
        raise ValueError("Expected a nonempty SDK deeplink")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    image = qrcode.make(link, box_size=2, border=4)
    temporary = path.with_suffix(".tmp.png")
    image.save(temporary)
    os.replace(temporary, path)
