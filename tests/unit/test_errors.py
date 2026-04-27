# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the granular exit-code system in image2_workbench.errors."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from image2_workbench.errors import (
    ErrorEnvelope,
    ExitCode,
    WorkbenchError,
    api_error,
    auth_error,
    cli_dispatch,
    internal_error,
    moderation_blocked,
    rate_limit_error,
    validation_error,
)


def test_exit_code_enum_has_seven_values() -> None:
    """The contract is OK=0..INTERNAL=6 — seven members, contiguous."""
    members = list(ExitCode)
    assert len(members) == 7
    assert ExitCode.OK == 0
    assert ExitCode.AUTH == 1
    assert ExitCode.RATE_LIMIT == 2
    assert ExitCode.MODERATION_BLOCKED == 3
    assert ExitCode.VALIDATION == 4
    assert ExitCode.API_OTHER == 5
    assert ExitCode.INTERNAL == 6


def test_auth_error_returns_workbench_error_with_auth_exit_code() -> None:
    err = auth_error("OPENAI_API_KEY not set")
    assert isinstance(err, WorkbenchError)
    assert err.envelope.exit_code is ExitCode.AUTH
    assert err.envelope.exit_code.value == 1
    assert err.envelope.code == "missing_api_key"
    assert "OPENAI_API_KEY" in err.envelope.message


def test_rate_limit_error_exit_code() -> None:
    err = rate_limit_error("hit 429")
    assert err.envelope.exit_code is ExitCode.RATE_LIMIT
    assert err.envelope.exit_code.value == 2


def test_moderation_blocked_exit_code() -> None:
    err = moderation_blocked("blocked by safety filter")
    assert err.envelope.exit_code is ExitCode.MODERATION_BLOCKED
    assert err.envelope.exit_code.value == 3


def test_validation_error_carries_explicit_code() -> None:
    err = validation_error(
        "transparent_bg_unsupported",
        "gpt-image-2 does not support background=transparent",
        docs_url="https://platform.openai.com/docs/guides/images",
    )
    assert err.envelope.exit_code is ExitCode.VALIDATION
    assert err.envelope.exit_code.value == 4
    assert err.envelope.code == "transparent_bg_unsupported"
    assert err.envelope.docs_url is not None


def test_api_error_exit_code() -> None:
    err = api_error("upstream 503")
    assert err.envelope.exit_code is ExitCode.API_OTHER
    assert err.envelope.exit_code.value == 5


def test_internal_error_records_cause_repr() -> None:
    cause = ZeroDivisionError("nope")
    err = internal_error("boom", cause=cause)
    assert err.envelope.exit_code is ExitCode.INTERNAL
    assert err.envelope.exit_code.value == 6
    assert err.envelope.cause is not None
    assert "ZeroDivisionError" in err.envelope.cause


def test_cli_dispatch_returns_zero_on_success() -> None:
    def ok() -> None:
        return None

    assert cli_dispatch(ok) == 0


def test_cli_dispatch_returns_auth_int_on_auth_error(capsys: pytest.CaptureFixture[str]) -> None:
    def boom() -> None:
        raise auth_error("OPENAI_API_KEY not set")

    rc = cli_dispatch(boom)
    assert rc == 1
    err_text = capsys.readouterr().err
    assert "missing_api_key" in err_text


def test_cli_dispatch_wraps_unexpected_exception_as_internal(
    capsys: pytest.CaptureFixture[str],
) -> None:
    def boom() -> None:
        raise ZeroDivisionError("divide by zero")

    rc = cli_dispatch(boom)
    assert rc == 6
    err_text = capsys.readouterr().err
    assert "internal_error" in err_text
    assert "ZeroDivisionError" in err_text


def test_cli_dispatch_passes_args_and_kwargs() -> None:
    captured: dict[str, object] = {}

    def echo(a: int, *, b: str) -> None:
        captured["a"] = a
        captured["b"] = b

    rc = cli_dispatch(echo, 3, b="hi")
    assert rc == 0
    assert captured == {"a": 3, "b": "hi"}


def test_error_envelope_rejects_unknown_fields() -> None:
    """Pydantic strict-mode: unknown keys must raise ValidationError."""
    with pytest.raises(ValidationError):
        ErrorEnvelope(
            exit_code=ExitCode.VALIDATION,
            code="x",
            message="m",
            unexpected_field="should not be allowed",  # type: ignore[call-arg]
        )
