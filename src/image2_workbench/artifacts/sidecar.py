"""JSON sidecar metadata for a produced image.

The sidecar is the audit trail: which model, snapshot, prompt hash,
parameters, cost estimate, and any runtime events (e.g. dropped
``thinking`` parameter). Written next to the image as
``<image>.sidecar.json``.
"""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, Field


class Sidecar(BaseModel):
    model: str
    snapshot: str
    revised_prompt: str | None = None
    size: str
    quality: str
    n: int
    format: str
    background: str
    moderation: str
    thinking: str | None = None
    prompt_hash: str
    image_hash: str
    cost_estimate_usd: float | None = None
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    events: list[str] = Field(default_factory=list)


def hash_prompt(prompt: str) -> str:
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()


def hash_image_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fp:
        for chunk in iter(lambda: fp.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_image_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write(sc: Sidecar, image_path: Path) -> Path:
    """Write the sidecar JSON next to ``image_path`` and return its path."""
    image_path = Path(image_path)
    sidecar_path = image_path.with_name(image_path.name + ".sidecar.json")
    sidecar_path.parent.mkdir(parents=True, exist_ok=True)
    payload = sc.model_dump(mode="json")
    sidecar_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return sidecar_path
