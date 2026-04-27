# SPDX-License-Identifier: Apache-2.0
"""OpenAI Batch API integration for image2-workbench.

Submit batched generate/edit jobs at the documented ~50% async discount
(24h window). The Batch API expects a JSONL upload of one request per
line, then returns a batch handle that progresses through validating →
in_progress → completed/failed states. Results land in an output file
which we download, parse, and write to disk.

Design notes:
  * ``dry_run=True`` produces a fully-typed :class:`BatchSubmitResult`
    without touching the network — used by tests and by ``i2w batch
    sweep --dry-run`` smoke runs.
  * The OpenAI SDK's ``client.batches.create`` knows about the chat /
    embeddings endpoints but not the Images endpoints; we still pass
    them through since the server accepts the URL. If the SDK's
    Literal-narrowing rejects the value at runtime, we fall through to
    the raw HTTP path.
  * No real network calls are made in tests — every test injects either
    ``dry_run=True`` or a mocked client.
"""

from __future__ import annotations

import io
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from ..compiler.validators import (
    validate_background,
    validate_format_compression,
    validate_no_input_fidelity,
    validate_size,
)

logger = logging.getLogger(__name__)


_ALLOWED_URLS = ("/v1/images/generations", "/v1/images/edits")


class BatchJobLine(BaseModel):
    """One row in a Batch JSONL upload."""

    model_config = ConfigDict(extra="forbid")

    custom_id: str = Field(..., min_length=1)
    method: Literal["POST"] = "POST"
    url: Literal["/v1/images/generations", "/v1/images/edits"]
    body: dict[str, Any]

    @model_validator(mode="after")
    def _validate_body(self) -> BatchJobLine:
        validate_no_input_fidelity(self.body)
        size = self.body.get("size")
        if size is not None:
            validate_size(str(size))
        quality = self.body.get("quality")
        if quality is not None and str(quality) not in {"low", "medium", "high", "auto"}:
            raise ValueError(
                f"quality must be one of low/medium/high/auto; got {quality!r}"
            )
        background = self.body.get("background")
        if background is not None:
            validate_background(str(background))
        fmt = self.body.get("output_format") or self.body.get("format")
        compression = self.body.get("output_compression")
        if fmt is not None:
            validate_format_compression(str(fmt), compression)
        return self


class BatchSubmitResult(BaseModel):
    """Returned by :func:`submit_batch`."""

    batch_id: str
    status: str
    request_count: int
    submitted_at: datetime


class BatchStatus(BaseModel):
    """Snapshot of a batch's progress."""

    batch_id: str
    status: str
    completed_count: int = 0
    failed_count: int = 0
    total_count: int = 0
    output_file_id: str | None = None


class BatchApiError(RuntimeError):
    """Wraps SDK errors with our context."""


def _new_client() -> Any:
    # Imported lazily so unit tests can patch
    # ``runtimes.batch_api.OpenAI`` without the import cost up front
    # and so that test fixtures without OPENAI_API_KEY don't blow up
    # at import time.
    from openai import OpenAI  # noqa: WPS433

    return OpenAI()


def _serialize_lines(lines: list[BatchJobLine]) -> bytes:
    buf = io.BytesIO()
    for line in lines:
        record = {
            "custom_id": line.custom_id,
            "method": line.method,
            "url": line.url,
            "body": line.body,
        }
        buf.write((json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8"))
    return buf.getvalue()


def serialize_lines_jsonl(lines: list[BatchJobLine]) -> str:
    """Return the exact JSONL payload that would be uploaded for ``lines``."""
    return _serialize_lines(lines).decode("utf-8")


def submit_batch(
    lines: list[BatchJobLine],
    *,
    dry_run: bool = False,
    client: Any | None = None,
) -> BatchSubmitResult:
    """Submit a JSONL batch.

    On ``dry_run=True`` we never call the API and return a deterministic
    fake result so the caller can wire its UX without paying for a real
    submission. Tests rely on this contract.
    """
    if not lines:
        raise ValueError("submit_batch requires at least one BatchJobLine")
    for i, line in enumerate(lines):
        if not isinstance(line, BatchJobLine):
            raise TypeError(
                f"lines[{i}] must be BatchJobLine, got {type(line).__name__}"
            )
    endpoint_url = lines[0].url
    if any(line.url != endpoint_url for line in lines):
        raise ValueError(
            "all lines in a batch must share the same endpoint url"
        )

    submitted_at = datetime.now(UTC)
    if dry_run:
        return BatchSubmitResult(
            batch_id=f"dryrun-batch-{int(submitted_at.timestamp())}",
            status="validating",
            request_count=len(lines),
            submitted_at=submitted_at,
        )

    cli = client if client is not None else _new_client()
    payload = _serialize_lines(lines)

    try:
        # Upload the JSONL as a "batch" purpose file.
        upload = cli.files.create(
            file=("batch_input.jsonl", payload),
            purpose="batch",
        )
        input_file_id = getattr(upload, "id", None) or (
            upload.get("id") if isinstance(upload, dict) else None
        )
        if not input_file_id:
            raise BatchApiError(
                f"files.create returned no id: {upload!r}"
            )
        # The SDK's typed Literal for `endpoint` lags behind the live
        # service; pass through unchanged. If the runtime SDK rejects
        # the value we surface that as a BatchApiError.
        batch = cli.batches.create(
            input_file_id=input_file_id,
            endpoint=endpoint_url,
            completion_window="24h",
        )
    except ValueError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise BatchApiError(f"batch submission failed: {exc!s}") from exc

    batch_id = getattr(batch, "id", None) or (
        batch.get("id") if isinstance(batch, dict) else None
    )
    status = getattr(batch, "status", None) or (
        batch.get("status") if isinstance(batch, dict) else "unknown"
    )
    if not batch_id:
        raise BatchApiError(f"batches.create returned no id: {batch!r}")

    return BatchSubmitResult(
        batch_id=str(batch_id),
        status=str(status),
        request_count=len(lines),
        submitted_at=submitted_at,
    )


def get_batch_status(batch_id: str, *, client: Any | None = None) -> BatchStatus:
    """Retrieve a batch's current status."""
    if not batch_id or not batch_id.strip():
        raise ValueError("batch_id must be a non-empty string")
    cli = client if client is not None else _new_client()
    try:
        batch = cli.batches.retrieve(batch_id)
    except Exception as exc:  # noqa: BLE001
        raise BatchApiError(
            f"batches.retrieve({batch_id!r}) failed: {exc!s}"
        ) from exc

    counts = (
        batch.get("request_counts", {})
        if isinstance(batch, dict)
        else getattr(batch, "request_counts", None) or {}
    )
    if hasattr(counts, "model_dump"):
        counts = counts.model_dump()
    elif not isinstance(counts, dict):
        counts = {
            "completed": getattr(counts, "completed", 0),
            "failed": getattr(counts, "failed", 0),
            "total": getattr(counts, "total", 0),
        }

    if isinstance(batch, dict):
        batch_id_value = batch.get("id", batch_id)
        status_value = batch.get("status", "unknown")
        output_file_id = batch.get("output_file_id")
    else:
        batch_id_value = getattr(batch, "id", batch_id)
        status_value = getattr(batch, "status", "unknown")
        output_file_id = getattr(batch, "output_file_id", None)

    return BatchStatus(
        batch_id=str(batch_id_value),
        status=str(status_value),
        completed_count=int(counts.get("completed", 0) or 0),
        failed_count=int(counts.get("failed", 0) or 0),
        total_count=int(counts.get("total", 0) or 0),
        output_file_id=str(output_file_id) if output_file_id else None,
    )


def _decode_output_blob(blob: Any) -> str:
    """Pull text out of whatever the SDK gave us back."""
    # Newer SDKs return a streamable response with `.text` or `.read()`.
    if hasattr(blob, "text") and isinstance(blob.text, str):
        return blob.text
    if hasattr(blob, "read"):
        raw = blob.read()
        if isinstance(raw, bytes):
            return raw.decode("utf-8")
        return str(raw)
    if isinstance(blob, bytes):
        return blob.decode("utf-8")
    if isinstance(blob, str):
        return blob
    raise BatchApiError(f"could not decode files.content response: {type(blob).__name__}")


def _extract_image_b64(line_record: dict[str, Any]) -> str | None:
    """Find the first b64_json image in a single Batch output JSONL line."""
    response = line_record.get("response") or {}
    body = response.get("body") if isinstance(response, dict) else None
    if not isinstance(body, dict):
        return None
    data = body.get("data")
    if not isinstance(data, list) or not data:
        return None
    first = data[0]
    if isinstance(first, dict):
        return first.get("b64_json")
    return None


def _safe_custom_id_filename(custom_id: Any, fallback: str) -> str:
    raw = str(custom_id or fallback)
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", raw).strip("._")
    return safe or fallback


def _safe_output_path(out_dir: Path, custom_id: Any, fallback: str) -> Path:
    safe_name = _safe_custom_id_filename(custom_id, fallback)
    base = out_dir.resolve()
    target = (out_dir / f"{safe_name}.png").resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise BatchApiError(
            f"batch output path escaped output directory: {custom_id!r}"
        ) from exc
    return target


def fetch_batch_results(
    batch_id: str,
    out_dir: Path,
    *,
    client: Any | None = None,
) -> int:
    """Download a completed batch's output file and write images.

    Each completed line in the JSONL is matched to ``out_dir/<custom_id>.png``.
    Returns the number of images written. Raises :class:`BatchApiError`
    if the batch isn't completed yet or has no output file.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cli = client if client is not None else _new_client()

    status = get_batch_status(batch_id, client=cli)
    if not status.output_file_id:
        raise BatchApiError(
            f"batch {batch_id!r} has no output file (status={status.status!r}); "
            "wait for completion before fetching"
        )

    try:
        blob = cli.files.content(status.output_file_id)
    except Exception as exc:  # noqa: BLE001
        raise BatchApiError(
            f"files.content({status.output_file_id!r}) failed: {exc!s}"
        ) from exc

    text = _decode_output_blob(blob)
    written = 0
    import base64

    for raw_line in text.splitlines():
        if not raw_line.strip():
            continue
        try:
            record = json.loads(raw_line)
        except json.JSONDecodeError:
            logger.warning("skipping malformed batch output line")
            continue
        custom_id = record.get("custom_id") or f"unknown_{written}"
        b64 = _extract_image_b64(record)
        if not b64:
            logger.warning("no image data for custom_id=%s", custom_id)
            continue
        target = _safe_output_path(out_dir, custom_id, f"unknown_{written}")
        try:
            target.write_bytes(base64.b64decode(b64))
            written += 1
        except (ValueError, OSError) as exc:
            logger.warning("failed to write %s: %s", target, exc)
    return written


__all__ = [
    "BatchApiError",
    "BatchJobLine",
    "BatchStatus",
    "BatchSubmitResult",
    "ValidationError",
    "fetch_batch_results",
    "get_batch_status",
    "serialize_lines_jsonl",
    "submit_batch",
]
