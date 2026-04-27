# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the OpenAI Batch API integration.

No real network calls — every test either uses ``dry_run=True`` or
injects a ``unittest.mock`` stub via the ``client=`` parameter.
"""

from __future__ import annotations

import base64
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from image2_workbench.runtimes.batch_api import (
    BatchApiError,
    BatchJobLine,
    BatchStatus,
    BatchSubmitResult,
    fetch_batch_results,
    get_batch_status,
    submit_batch,
)


def _make_line(
    custom_id: str = "demo_001",
    url: str = "/v1/images/generations",
) -> BatchJobLine:
    return BatchJobLine(
        custom_id=custom_id,
        method="POST",
        url=url,  # type: ignore[arg-type]
        body={"prompt": "a cat", "size": "1024x1024", "quality": "low", "n": 1},
    )


def test_submit_batch_dry_run_returns_fake_result_without_api_call() -> None:
    line = _make_line()
    # No client passed and no env API key needed because dry_run short-circuits.
    result = submit_batch([line], dry_run=True)
    assert isinstance(result, BatchSubmitResult)
    assert result.batch_id.startswith("dryrun-batch-")
    assert result.status == "validating"
    assert result.request_count == 1
    assert isinstance(result.submitted_at, datetime)


def test_submit_batch_empty_list_raises() -> None:
    with pytest.raises(ValueError, match="at least one"):
        submit_batch([], dry_run=True)


def test_submit_batch_rejects_non_batchjobline_entries() -> None:
    with pytest.raises(TypeError):
        submit_batch(["not a line"], dry_run=True)  # type: ignore[list-item]


def test_batchjobline_validates_url_choice() -> None:
    with pytest.raises(ValidationError):
        BatchJobLine(
            custom_id="bad",
            method="POST",
            url="/v1/responses",  # type: ignore[arg-type]
            body={},
        )


def test_batchjobline_accepts_both_image_endpoints() -> None:
    a = BatchJobLine(
        custom_id="a",
        method="POST",
        url="/v1/images/generations",
        body={"prompt": "x"},
    )
    b = BatchJobLine(
        custom_id="b",
        method="POST",
        url="/v1/images/edits",
        body={"prompt": "y"},
    )
    assert a.url.endswith("generations")
    assert b.url.endswith("edits")


def test_batchjobline_requires_nonempty_custom_id() -> None:
    with pytest.raises(ValidationError):
        BatchJobLine(
            custom_id="",
            method="POST",
            url="/v1/images/generations",
            body={},
        )


def test_submit_batch_with_mock_client_returns_real_batch_id() -> None:
    cli = MagicMock()
    cli.files.create.return_value = MagicMock(id="file_abc123")
    cli.batches.create.return_value = MagicMock(id="batch_xyz789", status="validating")

    line = _make_line()
    result = submit_batch([line], client=cli)

    assert result.batch_id == "batch_xyz789"
    assert result.status == "validating"
    assert result.request_count == 1
    cli.files.create.assert_called_once()
    cli.batches.create.assert_called_once()
    create_kwargs = cli.batches.create.call_args.kwargs
    assert create_kwargs["input_file_id"] == "file_abc123"
    assert create_kwargs["endpoint"] == "/v1/images/generations"
    assert create_kwargs["completion_window"] == "24h"


def test_submit_batch_rejects_mixed_endpoints() -> None:
    cli = MagicMock()
    cli.files.create.return_value = MagicMock(id="file_abc123")
    a = _make_line("a", "/v1/images/generations")
    b = _make_line("b", "/v1/images/edits")
    with pytest.raises(ValueError, match="same endpoint"):
        submit_batch([a, b], client=cli)


def test_submit_batch_wraps_sdk_failure() -> None:
    cli = MagicMock()
    cli.files.create.side_effect = RuntimeError("upload exploded")
    with pytest.raises(BatchApiError, match="batch submission failed"):
        submit_batch([_make_line()], client=cli)


def test_get_batch_status_with_mock_client() -> None:
    cli = MagicMock()
    counts = MagicMock()
    counts.completed = 3
    counts.failed = 1
    counts.total = 4
    counts.model_dump = lambda: {"completed": 3, "failed": 1, "total": 4}
    batch = MagicMock(
        id="batch_xyz",
        status="completed",
        request_counts=counts,
        output_file_id="file_out_42",
    )
    cli.batches.retrieve.return_value = batch
    st = get_batch_status("batch_xyz", client=cli)
    assert isinstance(st, BatchStatus)
    assert st.batch_id == "batch_xyz"
    assert st.status == "completed"
    assert st.completed_count == 3
    assert st.failed_count == 1
    assert st.total_count == 4
    assert st.output_file_id == "file_out_42"


def test_get_batch_status_rejects_empty_id() -> None:
    with pytest.raises(ValueError):
        get_batch_status("", client=MagicMock())


def test_get_batch_status_wraps_sdk_failure() -> None:
    cli = MagicMock()
    cli.batches.retrieve.side_effect = RuntimeError("network down")
    with pytest.raises(BatchApiError, match="batches.retrieve"):
        get_batch_status("batch_x", client=cli)


def test_fetch_batch_results_writes_images(tmp_path: Path) -> None:
    cli = MagicMock()
    counts = MagicMock()
    counts.model_dump = lambda: {"completed": 2, "failed": 0, "total": 2}
    cli.batches.retrieve.return_value = MagicMock(
        id="batch_x",
        status="completed",
        request_counts=counts,
        output_file_id="file_out",
    )

    image_bytes = b"\x89PNG\r\n\x1a\nfakepayload"
    b64 = base64.b64encode(image_bytes).decode("ascii")
    line1 = json.dumps(
        {
            "custom_id": "demo_a",
            "response": {"body": {"data": [{"b64_json": b64}]}},
        }
    )
    line2 = json.dumps(
        {
            "custom_id": "demo_b",
            "response": {"body": {"data": [{"b64_json": b64}]}},
        }
    )
    blob = MagicMock()
    blob.text = line1 + "\n" + line2 + "\n"
    cli.files.content.return_value = blob

    written = fetch_batch_results("batch_x", tmp_path, client=cli)
    assert written == 2
    assert (tmp_path / "demo_a.png").read_bytes() == image_bytes
    assert (tmp_path / "demo_b.png").read_bytes() == image_bytes


def test_fetch_batch_results_errors_when_no_output_file() -> None:
    cli = MagicMock()
    counts = MagicMock()
    counts.model_dump = lambda: {"completed": 0, "failed": 0, "total": 1}
    cli.batches.retrieve.return_value = MagicMock(
        id="batch_x",
        status="in_progress",
        request_counts=counts,
        output_file_id=None,
    )
    with pytest.raises(BatchApiError, match="no output file"):
        fetch_batch_results("batch_x", Path("/tmp/nonexistent_out"), client=cli)
