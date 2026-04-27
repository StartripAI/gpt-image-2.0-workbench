# SPDX-License-Identifier: Apache-2.0
"""OpenAI Responses API adapter using the ``image_generation`` tool.

This is a thin wrapper around ``client.responses.create`` that lets
gpt-5.x (or another reasoning text model) drive the image tool. It's
useful for multi-turn flows where you want the model to reason about
the prompt before invoking the image generator.
"""

from __future__ import annotations

import base64
import logging
from typing import Any

from .types import ApiCallError, GenerateRequest, GenerateResponse

logger = logging.getLogger(__name__)

_DEFAULT_WRAPPER_MODELS = ("gpt-5.1", "gpt-4.1")


def _new_client() -> Any:
    from openai import OpenAI  # noqa: WPS433

    return OpenAI()


def _pick_wrapper_model(client: Any) -> str:
    # The Responses API needs a text/reasoning model to host the tool.
    # We don't probe live here — gpt-5.1 is preferred, gpt-4.1 is the fallback.
    try:
        listing = client.models.list()
        ids = {getattr(m, "id", None) for m in getattr(listing, "data", []) or []}
        for cand in _DEFAULT_WRAPPER_MODELS:
            if cand in ids:
                return cand
    except Exception:  # noqa: BLE001
        pass
    return _DEFAULT_WRAPPER_MODELS[0]


def _extract_b64_from_responses(resp: Any) -> list[str]:
    out: list[str] = []
    output = getattr(resp, "output", None) or []
    for item in output:
        # Responses API returns image_generation tool calls with a `result` field
        # containing base64. We accept either dict-shaped or attribute-shaped items.
        if isinstance(item, dict):
            if item.get("type") == "image_generation_call" and item.get("result"):
                out.append(item["result"])
            elif item.get("type") == "image" and item.get("b64_json"):
                out.append(item["b64_json"])
            continue
        itype = getattr(item, "type", None)
        if itype == "image_generation_call":
            res = getattr(item, "result", None)
            if res:
                out.append(res)
        elif itype == "image":
            b64 = getattr(item, "b64_json", None)
            if b64:
                out.append(b64)
    if not out:
        raise ApiCallError("responses output had no image_generation_call result")
    return out


def _validate_b64(b: str) -> None:
    # Cheap sanity check — if it isn't decodable as base64, fail loudly here
    # rather than way downstream when we try to write the file.
    try:
        base64.b64decode(b, validate=False)
    except Exception as exc:  # noqa: BLE001
        raise ApiCallError(f"image payload is not valid base64: {exc}") from exc


def generate(
    req: GenerateRequest,
    prior_response_id: str | None = None,
    client: Any | None = None,
) -> GenerateResponse:
    """Generate an image via the Responses API + ``image_generation`` tool."""
    cli = client if client is not None else _new_client()
    wrapper = _pick_wrapper_model(cli)

    tool: dict[str, Any] = {
        "type": "image_generation",
        "size": req.size,
        "quality": req.quality,
        "output_format": req.fmt,
        "background": req.background,
        "moderation": req.moderation,
    }
    if req.partial_images is not None:
        tool["partial_images"] = req.partial_images

    create_kwargs: dict[str, Any] = {
        "model": wrapper,
        "input": req.prompt,
        "tools": [tool],
    }
    if prior_response_id:
        create_kwargs["previous_response_id"] = prior_response_id

    try:
        resp = cli.responses.create(**create_kwargs)
    except Exception as exc:  # noqa: BLE001
        raise ApiCallError(
            f"responses.create failed: {exc!s} "
            f"(wrapper={wrapper}, prior={prior_response_id})"
        ) from exc

    images = _extract_b64_from_responses(resp)
    for b in images:
        _validate_b64(b)

    snapshot = getattr(resp, "model", None) or wrapper
    return GenerateResponse(
        images_b64=images,
        revised_prompt=None,
        snapshot=str(snapshot),
        model=req.model,
    )
