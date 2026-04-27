# SPDX-License-Identifier: Apache-2.0
"""Smoke tests for `i2w render generate|edit`.

These mock :func:`runtimes.images_api.generate` / ``.edit`` so the suite
runs offline. The goal is to verify the wiring: prompt-file reading,
local validation, ``cli_dispatch`` exit codes, ledger appending, and
sidecar writing.
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from image2_workbench.cli import app
from image2_workbench.errors import auth_error
from image2_workbench.runtimes.types import GenerateResponse

runner = CliRunner()


# 1x1 white PNG for fake responses (validates pillar bytes-out + sidecar hash).
_FAKE_PNG_B64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNgYAAAAAMAAWg"
    "Z3BkAAAAASUVORK5CYII="
)


def _fake_generate_response(snapshot: str = "snap-test") -> GenerateResponse:
    return GenerateResponse(
        images_b64=[_FAKE_PNG_B64],
        revised_prompt="revised",
        snapshot=snapshot,
        model="gpt-image-2",
    )


@pytest.fixture()
def tmp_ledger(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Path:
    target = tmp_path / "ledger.jsonl"
    monkeypatch.setenv("IMAGE2_LEDGER_PATH", str(target))
    return target


@pytest.fixture()
def prompt_file(tmp_path: Path) -> Path:
    p = tmp_path / "p.md"
    p.write_text("a friendly golden retriever in a park", encoding="utf-8")
    return p


def _read_ledger(path: Path) -> list[dict]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def _fake_sdk_response(snapshot: str = "snap-test"):
    """Build a mock object that mimics ``OpenAI().images.generate(...)``."""
    from unittest.mock import MagicMock

    item = MagicMock()
    item.b64_json = _FAKE_PNG_B64
    item.revised_prompt = "revised"
    resp = MagicMock()
    resp.data = [item]
    resp.model = snapshot
    resp.created = 1_700_000_000
    return resp


def test_render_generate_writes_image_sidecar_and_ledger(
    tmp_path: Path, tmp_ledger: Path, prompt_file: Path
) -> None:
    """Mock the OpenAI client so the runtime's ok-path ledger write fires."""
    from unittest.mock import MagicMock

    out_path = tmp_path / "img.png"
    fake_client = MagicMock()
    fake_client.images.generate.return_value = _fake_sdk_response("snap-test")

    with patch(
        "image2_workbench.runtimes.images_api._new_client",
        return_value=fake_client,
    ):
        result = runner.invoke(
            app,
            [
                "render", "generate",
                "--prompt-file", str(prompt_file),
                "--size", "1024x1024",
                "--quality", "medium",
                "--out", str(out_path),
            ],
        )
    assert result.exit_code == 0, (result.stdout, result.stderr)
    assert out_path.exists()
    sidecar = out_path.with_name(out_path.name + ".sidecar.json")
    assert sidecar.exists()
    body = json.loads(sidecar.read_text(encoding="utf-8"))
    assert body["snapshot"] == "snap-test"
    assert body["size"] == "1024x1024"
    # The image bytes match the decoded fake PNG.
    assert out_path.read_bytes() == base64.b64decode(_FAKE_PNG_B64)
    # Runtime appended one ok entry to the ledger.
    entries = _read_ledger(tmp_ledger)
    ok_entries = [e for e in entries if e.get("status") == "ok"]
    assert len(ok_entries) == 1, entries
    assert ok_entries[0]["kind"] == "generate"
    assert ok_entries[0]["snapshot"] == "snap-test"


def test_render_generate_rejects_transparent_background(
    tmp_path: Path, tmp_ledger: Path, prompt_file: Path
) -> None:
    out_path = tmp_path / "img.png"
    result = runner.invoke(
        app,
        [
            "render", "generate",
            "--prompt-file", str(prompt_file),
            "--background", "transparent",
            "--out", str(out_path),
        ],
    )
    assert result.exit_code == 4, (result.stdout, result.stderr)
    assert "transparent" in (result.stdout + result.stderr).lower()


def test_render_edit_without_image_exits_4(
    tmp_path: Path, tmp_ledger: Path, prompt_file: Path
) -> None:
    out_path = tmp_path / "img.png"
    result = runner.invoke(
        app,
        [
            "render", "edit",
            "--prompt-file", str(prompt_file),
            "--out", str(out_path),
        ],
    )
    assert result.exit_code == 4, (result.stdout, result.stderr)
    combined = (result.stdout + result.stderr).lower()
    assert "reference image" in combined or "missing_reference_image" in combined


def test_render_edit_authentication_error_exits_1_and_logs_ledger(
    tmp_path: Path, tmp_ledger: Path, prompt_file: Path
) -> None:
    """Mock the OpenAI client so the runtime maps AuthenticationError to a
    WorkbenchError, writes an error ledger entry, and the CLI exits 1.
    """
    from unittest.mock import MagicMock

    from openai import AuthenticationError

    img = tmp_path / "in.png"
    img.write_bytes(b"\x89PNG\r\n")
    out_path = tmp_path / "out.png"

    fake_client = MagicMock()
    fake_client.images.edit.side_effect = AuthenticationError(
        message="missing key",
        response=MagicMock(),
        body={"error": {"message": "missing key"}},
    )

    with patch(
        "image2_workbench.runtimes.images_api._new_client",
        return_value=fake_client,
    ):
        result = runner.invoke(
            app,
            [
                "render", "edit",
                "--prompt-file", str(prompt_file),
                "-i", str(img),
                "--out", str(out_path),
            ],
        )
    assert result.exit_code == 1, (result.stdout, result.stderr)
    combined = (result.stdout + result.stderr).lower()
    assert "missing_api_key" in combined or "auth" in combined

    entries = _read_ledger(tmp_ledger)
    error_entries = [e for e in entries if e.get("status") == "error"]
    assert error_entries, f"expected an error ledger entry, got {entries}"
    assert error_entries[0]["error_code"] == "missing_api_key"
    assert error_entries[0]["error_exit_code"] == 1
    assert error_entries[0]["kind"] == "edit"


def test_render_edit_validation_error_keeps_auth_error_unused(
    tmp_path: Path, tmp_ledger: Path, prompt_file: Path
) -> None:
    """The auth_error helper used at module level is still a valid import."""
    err = auth_error("missing key")
    assert err.envelope.exit_code.value == 1
    assert err.envelope.code == "missing_api_key"
