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
