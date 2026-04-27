"""Write decoded image bytes from the runtime to disk."""

from __future__ import annotations

import base64
from pathlib import Path


def write_image(b64: str, out_path: Path, fmt: str) -> Path:
    """Decode ``b64`` and write to ``out_path``.

    Ensures the parent directory exists. ``fmt`` is recorded for the
    sidecar but not enforced against the file extension (callers
    decide their naming convention).
    """
    if not isinstance(b64, str) or not b64:
        raise ValueError("b64 must be a non-empty string")
    if not isinstance(fmt, str) or not fmt:
        raise ValueError("fmt must be a non-empty string")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(b64, validate=False)
    out.write_bytes(raw)
    return out
