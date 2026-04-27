"""Runtime capability probe.

Best-effort, side-effect-free interrogation of the local OpenAI
environment. We deliberately avoid any paid call (e.g. a 1x1 image
generation): the probe only lists models, which is free and quick.
The contract: never raise. Return a populated :class:`CapabilityProbe`
even when the network is down.
"""

from __future__ import annotations

import os
from typing import Any

from .types import CapabilityProbe

_TARGET_MODEL_PREFIX = "gpt-image-2"

# Static table of parameter combinations known to fail against the documented
# gpt-image-2 surface. The probe never *calls* the API to learn these — they
# come from the official compatibility matrix and let `i2w doctor` warn users
# even when no API key is configured. Keep entries small, factual, and
# documentation-driven; do not speculate.
_KNOWN_FAILURE_PATTERNS: list[dict[str, str]] = [
    {
        "pattern": "input_fidelity",
        "code": "input_fidelity_unsupported",
        "severity": "error",
        "message": (
            "input_fidelity is not accepted on gpt-image-2 — the parameter is "
            "rejected by the API. Remove it or target gpt-image-1.5."
        ),
    },
    {
        "pattern": "background=transparent",
        "code": "transparent_bg_unsupported",
        "severity": "error",
        "message": (
            "background=transparent is not supported on gpt-image-2 — only "
            "auto/opaque are accepted. Use gpt-image-1.5 or post-process."
        ),
    },
    {
        "pattern": "max_edge>3840",
        "code": "max_edge_exceeded",
        "severity": "error",
        "message": (
            "max_edge greater than 3840 is rejected by gpt-image-2 — the "
            "documented hard cap on either edge is 3840 pixels."
        ),
    },
    {
        "pattern": "aspect_ratio>3:1",
        "code": "aspect_ratio_exceeded",
        "severity": "error",
        "message": (
            "aspect ratio greater than 3:1 (or 1:3) is rejected — gpt-image-2 "
            "constrains generations to within a 3:1 ratio."
        ),
    },
    {
        "pattern": "format=png+output_compression",
        "code": "compression_format_mismatch",
        "severity": "error",
        "message": (
            "output_compression is only valid for jpeg/webp; combining it with "
            "format=png is rejected client-side and by the API."
        ),
    },
]


def known_failure_patterns() -> list[dict[str, str]]:
    """Return the static known-bad parameter patterns for gpt-image-2.

    Each entry has stable keys: ``pattern`` (human-readable trigger string),
    ``code`` (matches the ``code`` field used by ``validation_error``),
    ``severity`` (currently always ``"error"``), and ``message`` (a single
    user-facing line). The list is returned as a fresh shallow copy so callers
    cannot mutate the module-level table.
    """
    return [dict(entry) for entry in _KNOWN_FAILURE_PATTERNS]


def probe(client: Any | None = None) -> CapabilityProbe:
    """Return a capability snapshot, swallowing all network/auth errors."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return CapabilityProbe(
            has_api_key=False,
            notes=[
                "OPENAI_API_KEY is not set; runtime calls will fail until configured."
            ],
        )

    notes: list[str] = []
    snapshot_id: str | None = None
    org_verified: bool | None = None

    try:
        cli = client if client is not None else _new_client()
    except Exception as exc:  # noqa: BLE001
        notes.append(f"could not initialize OpenAI client: {exc!s}")
        return CapabilityProbe(has_api_key=True, notes=notes)

    try:
        listing = cli.models.list()
        candidates: list[str] = []
        for m in getattr(listing, "data", []) or []:
            mid = getattr(m, "id", None)
            if isinstance(mid, str) and mid.startswith(_TARGET_MODEL_PREFIX):
                candidates.append(mid)
        if candidates:
            # Prefer the latest snapshot (lex sort works because they're
            # date-stamped: gpt-image-2-YYYY-MM-DD).
            snapshot_id = sorted(candidates)[-1]
            notes.append(f"latest gpt-image-2 snapshot visible: {snapshot_id}")
            org_verified = True
        else:
            notes.append(
                "no gpt-image-2 snapshot visible to this account "
                "(org may not be verified for image generation)"
            )
            org_verified = False
    except Exception as exc:  # noqa: BLE001
        notes.append(f"models.list failed: {exc!s}")

    return CapabilityProbe(
        has_api_key=True,
        org_verified=org_verified,
        supports_thinking=None,  # only known by attempting a real call
        supports_transparent_background=False,
        max_resolution_seen=None,
        streaming_partial_images=None,
        notes=notes,
    )


def _new_client() -> Any:
    from openai import OpenAI  # noqa: WPS433

    return OpenAI()
