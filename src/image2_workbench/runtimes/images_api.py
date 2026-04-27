"""OpenAI Images API adapter (``client.images.generate`` / ``.edit``).

Maps :class:`GenerateRequest` / :class:`EditRequest` to the SDK call,
applies the project's policy guards (no transparent background, no
``input_fidelity``, sane size validation), and normalizes the response
into :class:`GenerateResponse`.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

from ..errors import (
    WorkbenchError,
    api_error,
    auth_error,
    rate_limit_error,
    validation_error,
)
from .types import (
    ApiCallError,
    EditRequest,
    GenerateRequest,
    GenerateResponse,
    UnsupportedParameterError,
)

logger = logging.getLogger(__name__)

# Documented hard limits for gpt-image-2.
_MAX_EDGE = 3840
_MIN_EDGE = 256  # implied by the multiples-of-16 + min-pixel rules
_MIN_PIXELS = 655_360
_MAX_PIXELS = 8_294_400
_EXPERIMENTAL_PIXELS = 2560 * 1440  # >2K is documented as experimental
_SIZE_RE = re.compile(r"^(\d+)x(\d+)$")
_DEFAULT_SNAPSHOT = "gpt-image-2-2026-04-21"


def _parse_size(size: str) -> tuple[int, int]:
    m = _SIZE_RE.match(size)
    if not m:
        raise UnsupportedParameterError(
            f"size must be 'WIDTHxHEIGHT' (e.g. '1024x1024'); got {size!r}"
        )
    return int(m.group(1)), int(m.group(2))


def _validate_size(size: str) -> None:
    """Enforce gpt-image-2 documented size constraints.

    Returns ``None`` on success, raises :class:`UnsupportedParameterError`
    otherwise. Logs a warning for experimental >2K sizes but allows them.
    """
    w, h = _parse_size(size)
    if w <= 0 or h <= 0:
        raise UnsupportedParameterError(f"size must have positive dimensions; got {size!r}")
    if max(w, h) > _MAX_EDGE:
        raise UnsupportedParameterError(
            f"size {size!r} exceeds max edge {_MAX_EDGE}px"
        )
    if w % 16 != 0 or h % 16 != 0:
        raise UnsupportedParameterError(
            f"size {size!r} edges must be multiples of 16"
        )
    long, short = max(w, h), min(w, h)
    if long > 3 * short:
        raise UnsupportedParameterError(
            f"size {size!r} aspect ratio exceeds 3:1"
        )
    pixels = w * h
    if pixels < _MIN_PIXELS:
        raise UnsupportedParameterError(
            f"size {size!r} has {pixels} pixels; min is {_MIN_PIXELS}"
        )
    if pixels > _MAX_PIXELS:
        raise UnsupportedParameterError(
            f"size {size!r} has {pixels} pixels; max is {_MAX_PIXELS}"
        )
    if pixels > _EXPERIMENTAL_PIXELS:
        logger.warning(
            "size %s is above 2560x1440 — experimental on gpt-image-2", size
        )


def validate_size(size: str) -> None:
    """Validate a gpt-image-2 size string without creating an API client."""
    _validate_size(size)


def _validate_quality(quality: str) -> None:
    if quality not in ("low", "medium", "high", "auto"):
        raise UnsupportedParameterError(
            f"quality must be one of low/medium/high/auto; got {quality!r}"
        )


def _validate_background(background: str) -> None:
    # The Literal already constrains pydantic-validated callers, but
    # adapters may be called with raw strings (e.g. from CLI plumbing).
    if background == "transparent":
        raise UnsupportedParameterError(
            "background='transparent' is not supported by gpt-image-2; "
            "use 'auto' or 'opaque'"
        )
    if background not in ("auto", "opaque"):
        raise UnsupportedParameterError(
            f"background must be 'auto' or 'opaque'; got {background!r}"
        )


def _reject_input_fidelity(extra: dict[str, Any] | None) -> None:
    if extra and "input_fidelity" in extra:
        raise UnsupportedParameterError(
            "input_fidelity is not supported on gpt-image-2"
        )


def _new_client() -> Any:
    # Imported lazily so unit tests can patch ``runtimes.images_api.OpenAI``
    # without paying the import cost up front.
    from openai import OpenAI  # noqa: WPS433

    return OpenAI()


def _validate_request(req: GenerateRequest | EditRequest) -> None:
    _validate_size(req.size)
    _validate_quality(req.quality)
    _validate_background(req.background)


def _build_generate_kwargs(req: GenerateRequest) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": req.model,
        "prompt": req.prompt,
        "size": req.size,
        "quality": req.quality,
        "n": req.n,
        "output_format": req.fmt,
        "background": req.background,
        "moderation": req.moderation,
    }
    if req.output_compression is not None:
        kwargs["output_compression"] = req.output_compression
    if req.partial_images is not None:
        kwargs["partial_images"] = req.partial_images
    return kwargs


def _is_unknown_param_error(exc: Exception) -> bool:
    msg = str(exc).lower()
    return (
        "unknown" in msg
        or "unrecognized" in msg
        or "unexpected" in msg
        or "not a valid" in msg
        or "thinking" in msg
    )


def _extract_b64(resp: Any) -> list[str]:
    data = getattr(resp, "data", None) or []
    out: list[str] = []
    for item in data:
        b64 = getattr(item, "b64_json", None) or (
            item.get("b64_json") if isinstance(item, dict) else None
        )
        if b64:
            out.append(b64)
    if not out:
        raise ApiCallError("response contained no b64_json image data")
    return out


def _extract_revised_prompt(resp: Any) -> str | None:
    data = getattr(resp, "data", None) or []
    if not data:
        return None
    first = data[0]
    return getattr(first, "revised_prompt", None) or (
        first.get("revised_prompt") if isinstance(first, dict) else None
    )


def _extract_snapshot(resp: Any, fallback_model: str) -> str:
    # Newer SDK responses include a ``model`` field; older ones don't.
    snap = getattr(resp, "model", None)
    if snap:
        return str(snap)
    created = getattr(resp, "created", None) or getattr(resp, "created_at", None)
    if created is not None:
        return f"{fallback_model}@{created}"
    return _DEFAULT_SNAPSHOT


def generate(
    req: GenerateRequest,
    client: Any | None = None,
    events: list[str] | None = None,
) -> GenerateResponse:
    """Call ``images.generate`` and return a normalized response.

    ``events`` is an optional sink for sidecar-bound notes (e.g. when
    we drop the ``thinking`` parameter on a 400). Pass an empty list
    to capture them.
    """
    _validate_request(req)
    kwargs = _build_generate_kwargs(req)

    try:
        cli = client if client is not None else _new_client()
        if req.thinking is not None:
            try:
                resp = cli.images.generate(thinking=req.thinking, **kwargs)
            except Exception as exc:  # noqa: BLE001 — narrow below
                from openai import BadRequestError  # noqa: WPS433

                if isinstance(exc, BadRequestError) and _is_unknown_param_error(exc):
                    note = "thinking parameter unsupported by current snapshot"
                    logger.info(note)
                    if events is not None:
                        events.append("thinking_param_dropped")
                    resp = cli.images.generate(**kwargs)
                else:
                    raise
        else:
            resp = cli.images.generate(**kwargs)
    except UnsupportedParameterError:
        raise
    except WorkbenchError:
        raise
    except Exception as exc:  # noqa: BLE001
        wrapped = _wrap_openai_exception(exc)
        if wrapped is not None:
            raise wrapped from exc
        raise ApiCallError(
            f"images.generate failed: {exc!s} (req={_safe_req_summary(req)})"
        ) from exc

    snapshot = _extract_snapshot(resp, req.model)
    return GenerateResponse(
        images_b64=_extract_b64(resp),
        revised_prompt=_extract_revised_prompt(resp),
        snapshot=snapshot,
        model=req.model,
    )


def edit(
    req: EditRequest,
    client: Any | None = None,
) -> GenerateResponse:
    """Call ``images.edit`` with one or more reference images and an optional mask."""
    _validate_request(req)
    if not req.images:
        raise UnsupportedParameterError(
            "images.edit requires at least one reference image"
        )

    image_handles: list[Any] = []
    mask_handle: Any = None
    try:
        for p in req.images:
            image_handles.append(_open_binary(p))
        if req.mask is not None:
            mask_handle = _open_binary(req.mask)
        cli = client if client is not None else _new_client()

        kwargs: dict[str, Any] = {
            "model": req.model,
            "prompt": req.prompt,
            "image": image_handles if len(image_handles) > 1 else image_handles[0],
            "size": req.size,
            "quality": req.quality,
            "background": req.background,
            "moderation": req.moderation,
            "output_format": req.fmt,
        }
        if mask_handle is not None:
            kwargs["mask"] = mask_handle

        resp = cli.images.edit(**kwargs)
    except UnsupportedParameterError:
        raise
    except WorkbenchError:
        raise
    except Exception as exc:  # noqa: BLE001
        wrapped = _wrap_openai_exception(exc)
        if wrapped is not None:
            raise wrapped from exc
        raise ApiCallError(
            f"images.edit failed: {exc!s} (req={_safe_req_summary(req)})"
        ) from exc
    finally:
        for h in image_handles:
            _safe_close(h)
        _safe_close(mask_handle)

    snapshot = _extract_snapshot(resp, req.model)
    return GenerateResponse(
        images_b64=_extract_b64(resp),
        revised_prompt=_extract_revised_prompt(resp),
        snapshot=snapshot,
        model=req.model,
    )


def _open_binary(path: Path) -> Any:
    p = Path(path)
    if not p.exists():
        raise UnsupportedParameterError(f"input image not found: {p}")
    if not p.is_file():
        raise UnsupportedParameterError(f"input image is not a file: {p}")
    return p.open("rb")


def _safe_close(h: Any) -> None:
    if h is None:
        return
    try:
        h.close()
    except Exception:  # noqa: BLE001
        pass


def _extract_openai_error_code(exc: Exception) -> str | None:
    """Pull the ``error.code`` field out of an OpenAI SDK exception body, if any."""
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            code = err.get("code")
            if isinstance(code, str) and code:
                return code
    return None


def _wrap_openai_exception(exc: Exception) -> WorkbenchError | None:
    """Translate an OpenAI SDK exception into a ``WorkbenchError`` envelope.

    Returns ``None`` if ``exc`` is not a recognised OpenAI exception type;
    callers fall back to :class:`ApiCallError`.
    """
    msg = str(exc).lower()
    if "api_key" in msg or "api key" in msg:
        return auth_error(
            f"OpenAI authentication failed: {exc!s}",
            cause=repr(exc),
        )

    try:
        from openai import (  # noqa: WPS433
            APIError,
            AuthenticationError,
            BadRequestError,
            OpenAIError,
            RateLimitError,
        )
    except Exception:  # noqa: BLE001 — openai missing is itself an API error
        return None

    if isinstance(exc, AuthenticationError):
        return auth_error(
            f"OpenAI authentication failed: {exc!s}",
            cause=repr(exc),
        )
    if isinstance(exc, RateLimitError):
        return rate_limit_error(
            f"OpenAI rate-limit / tier-limit hit: {exc!s}",
            cause=repr(exc),
        )
    if isinstance(exc, BadRequestError):
        code = _extract_openai_error_code(exc) or "bad_request"
        return validation_error(
            code,
            f"OpenAI rejected the request: {exc!s}",
            cause=repr(exc),
        )
    if isinstance(exc, APIError):
        return api_error(
            f"OpenAI API error: {exc!s}",
            cause=repr(exc),
        )
    if isinstance(exc, OpenAIError):
        return api_error(
            f"OpenAI client error: {exc!s}",
            cause=repr(exc),
        )
    return None


def _safe_req_summary(req: GenerateRequest | EditRequest) -> dict[str, Any]:
    d = req.model_dump()
    # Don't include the prompt body in error messages — it can be long.
    if "prompt" in d and isinstance(d["prompt"], str):
        d["prompt"] = d["prompt"][:80] + ("..." if len(d["prompt"]) > 80 else "")
    if "images" in d and isinstance(d["images"], list):
        d["images"] = [str(p) for p in d["images"]]
    if "mask" in d and d["mask"] is not None:
        d["mask"] = str(d["mask"])
    return d
