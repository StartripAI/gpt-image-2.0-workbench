# SPDX-License-Identifier: Apache-2.0
"""Granular exit codes + structured error envelope for image2-workbench.

Other modules raise WorkbenchError(envelope=...) and the CLI catches and exits
with envelope.exit_code.value.
"""
from __future__ import annotations

import traceback
from collections.abc import Callable
from enum import IntEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from rich.console import Console


class ExitCode(IntEnum):
    OK = 0
    AUTH = 1                # missing API key, invalid key, org not verified
    RATE_LIMIT = 2          # 429 from OpenAI; tier limits
    MODERATION_BLOCKED = 3  # /v1/moderations or post-gen filter blocked
    VALIDATION = 4          # local-side validation: bad params, unsupported flags
    API_OTHER = 5           # 4xx/5xx that don't fit above
    INTERNAL = 6            # bug in workbench (unhandled exception)


class ErrorEnvelope(BaseModel):
    """Structured payload describing a workbench failure.

    Pydantic strict-mode: unknown fields are rejected so contract drift between
    callers fails loudly during tests rather than silently in production.
    """

    model_config = ConfigDict(extra="forbid")

    exit_code: ExitCode
    code: str               # short stable identifier, e.g. "transparent_bg_unsupported"
    message: str            # user-facing one-line message
    detail: str | None = None        # multi-line context, optional
    docs_url: str | None = None      # link to relevant docs
    context: dict[str, Any] = Field(default_factory=dict)
    cause: str | None = None         # repr of upstream exception, if any


class WorkbenchError(Exception):
    """Raised throughout the codebase. Always carries an ErrorEnvelope."""

    def __init__(self, envelope: ErrorEnvelope) -> None:
        super().__init__(envelope.message)
        self.envelope = envelope


# --------------------------------------------------------------------------- #
# Convenience constructors — keep these stable, X2/X3/X4 use them.
# --------------------------------------------------------------------------- #

_DEFAULT_CODES: dict[ExitCode, str] = {
    ExitCode.AUTH: "auth_error",
    ExitCode.RATE_LIMIT: "rate_limited",
    ExitCode.MODERATION_BLOCKED: "moderation_blocked",
    ExitCode.API_OTHER: "api_error",
    ExitCode.INTERNAL: "internal_error",
}


def _build(
    exit_code: ExitCode,
    message: str,
    *,
    code: str | None = None,
    detail: str | None = None,
    docs_url: str | None = None,
    context: dict[str, Any] | None = None,
    cause: str | None = None,
) -> WorkbenchError:
    envelope = ErrorEnvelope(
        exit_code=exit_code,
        code=code or _DEFAULT_CODES[exit_code],
        message=message,
        detail=detail,
        docs_url=docs_url,
        context=context or {},
        cause=cause,
    )
    return WorkbenchError(envelope)


def auth_error(message: str, **kwargs: Any) -> WorkbenchError:
    """Authentication / authorization failure. Default code: ``missing_api_key``."""
    kwargs.setdefault("code", "missing_api_key")
    return _build(ExitCode.AUTH, message, **kwargs)


def rate_limit_error(message: str, **kwargs: Any) -> WorkbenchError:
    """OpenAI 429 rate-limit / tier-limit failure."""
    kwargs.setdefault("code", "rate_limited")
    return _build(ExitCode.RATE_LIMIT, message, **kwargs)


def moderation_blocked(message: str, **kwargs: Any) -> WorkbenchError:
    """Moderation endpoint or post-generation filter blocked the request/output."""
    kwargs.setdefault("code", "moderation_blocked")
    return _build(ExitCode.MODERATION_BLOCKED, message, **kwargs)


def validation_error(code: str, message: str, **kwargs: Any) -> WorkbenchError:
    """Local-side parameter validation failure. ``code`` is required and stable."""
    return _build(ExitCode.VALIDATION, message, code=code, **kwargs)


def api_error(message: str, **kwargs: Any) -> WorkbenchError:
    """Generic OpenAI 4xx/5xx that does not fit the more specific buckets."""
    kwargs.setdefault("code", "api_error")
    return _build(ExitCode.API_OTHER, message, **kwargs)


def internal_error(
    message: str,
    cause: BaseException | None = None,
    **kwargs: Any,
) -> WorkbenchError:
    """Unexpected workbench bug. ``cause`` is repr'd into the envelope."""
    kwargs.setdefault("code", "internal_error")
    cause_repr = repr(cause) if cause is not None else None
    return _build(ExitCode.INTERNAL, message, cause=cause_repr, **kwargs)


# --------------------------------------------------------------------------- #
# CLI dispatcher
# --------------------------------------------------------------------------- #

def _print_envelope(envelope: ErrorEnvelope) -> None:
    """Render a WorkbenchError envelope to STDERR with a red exit-code label."""
    err = Console(stderr=True)
    err.print(
        f"[bold red]exit {int(envelope.exit_code)} ({envelope.exit_code.name})[/]"
        f" [yellow]{envelope.code}[/]: {envelope.message}"
    )
    if envelope.detail:
        err.print(envelope.detail, markup=False)
    if envelope.docs_url:
        err.print(f"  docs: {envelope.docs_url}", markup=False)
    if envelope.cause:
        err.print(f"  cause: {envelope.cause}", markup=False)


def cli_dispatch(func: Callable[..., Any], *args: Any, **kwargs: Any) -> int:
    """Run *func*; translate any failure into a granular exit-code int.

    - Returns 0 (``ExitCode.OK``) on success.
    - On :class:`WorkbenchError`, prints the envelope and returns its exit code.
    - On any other ``Exception``, wraps it in :func:`internal_error` with a
      formatted traceback in ``detail`` and returns ``ExitCode.INTERNAL``.
    """
    try:
        func(*args, **kwargs)
    except WorkbenchError as wb:
        _print_envelope(wb.envelope)
        return wb.envelope.exit_code.value
    except Exception as exc:  # noqa: BLE001 — top-level safety net
        tb = traceback.format_exc()
        wb = internal_error(
            f"unhandled {type(exc).__name__}: {exc}",
            cause=exc,
            detail=tb,
        )
        _print_envelope(wb.envelope)
        return wb.envelope.exit_code.value
    return ExitCode.OK.value
