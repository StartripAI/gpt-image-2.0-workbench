"""Unit tests for the Images API adapter and its policy guards."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from image2_workbench.runtimes import images_api
from image2_workbench.runtimes.types import (
    ApiCallError,
    EditRequest,
    GenerateRequest,
    UnsupportedParameterError,
)

# ----- size validation -----


def test_validate_size_default_ok():
    images_api._validate_size("1024x1024")


def test_validate_size_too_small_pixels():
    # 100x100 = 10_000 < 655_360 minimum, plus not multiples of 16
    with pytest.raises(UnsupportedParameterError):
        images_api._validate_size("100x100")


def test_validate_size_max_edge_violated():
    # 4096 > 3840 max edge
    with pytest.raises(UnsupportedParameterError):
        images_api._validate_size("4096x4096")


def test_validate_size_2k_plus_warns_but_passes(caplog):
    # 3840x2160 (4K UHD) is allowed but flagged experimental.
    with caplog.at_level("WARNING"):
        images_api._validate_size("3840x2160")
    assert any("experimental" in r.message for r in caplog.records)


def test_validate_size_non_multiple_of_16():
    with pytest.raises(UnsupportedParameterError) as ei:
        images_api._validate_size("1023x1024")
    assert "multiples of 16" in str(ei.value)


def test_validate_size_aspect_ratio_too_extreme():
    # 32:1 ratio
    with pytest.raises(UnsupportedParameterError):
        images_api._validate_size("3840x16")


def test_validate_size_malformed():
    with pytest.raises(UnsupportedParameterError):
        images_api._validate_size("notasize")


# ----- background guard -----


def test_validate_background_rejects_transparent():
    with pytest.raises(UnsupportedParameterError):
        images_api._validate_background("transparent")


def test_validate_background_accepts_auto_and_opaque():
    images_api._validate_background("auto")
    images_api._validate_background("opaque")


def test_generate_request_rejects_transparent_via_pydantic():
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="x", background="transparent")  # type: ignore[arg-type]


# ----- format / compression guards -----


def test_compression_only_for_lossy_formats():
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="x", fmt="png", output_compression=50)


def test_compression_ok_for_jpeg():
    r = GenerateRequest(prompt="x", fmt="jpeg", output_compression=50)
    assert r.output_compression == 50


def test_compression_ok_for_webp():
    r = GenerateRequest(prompt="x", fmt="webp", output_compression=80)
    assert r.output_compression == 80


# ----- mocked generate() request shaping -----


def _mock_response(b64: str = "ZmFrZQ==", revised: str | None = None, model: str = "snap-x"):
    r = MagicMock()
    item = MagicMock()
    item.b64_json = b64
    item.revised_prompt = revised
    r.data = [item]
    r.model = model
    r.created = 1_700_000_000
    return r


def test_generate_shapes_request_correctly():
    cli = MagicMock()
    cli.images.generate.return_value = _mock_response()
    req = GenerateRequest(
        prompt="A dog",
        size="1024x1024",
        quality="medium",
        n=2,
        fmt="png",
        background="auto",
        moderation="auto",
    )
    out = images_api.generate(req, client=cli)
    cli.images.generate.assert_called_once()
    kwargs = cli.images.generate.call_args.kwargs
    assert kwargs["model"] == "gpt-image-2"
    assert kwargs["prompt"] == "A dog"
    assert kwargs["size"] == "1024x1024"
    assert kwargs["quality"] == "medium"
    assert kwargs["n"] == 2
    assert kwargs["output_format"] == "png"
    assert kwargs["background"] == "auto"
    assert kwargs["moderation"] == "auto"
    # output_compression must NOT appear when it isn't set
    assert "output_compression" not in kwargs
    # snapshot picked from response.model
    assert out.snapshot == "snap-x"
    assert out.images_b64 == ["ZmFrZQ=="]


def test_generate_passes_thinking_when_set():
    cli = MagicMock()
    cli.images.generate.return_value = _mock_response()
    req = GenerateRequest(prompt="x", thinking="medium")
    images_api.generate(req, client=cli)
    kwargs = cli.images.generate.call_args.kwargs
    assert kwargs["thinking"] == "medium"


def test_generate_drops_thinking_on_bad_request():
    from openai import BadRequestError

    cli = MagicMock()
    err = BadRequestError(
        message="Unknown parameter: 'thinking'",
        response=MagicMock(),
        body={"error": {"message": "Unknown parameter: 'thinking'"}},
    )
    cli.images.generate.side_effect = [err, _mock_response()]
    events: list[str] = []
    req = GenerateRequest(prompt="x", thinking="auto")
    out = images_api.generate(req, client=cli, events=events)
    assert cli.images.generate.call_count == 2
    # Second call must NOT include thinking
    second_kwargs = cli.images.generate.call_args_list[1].kwargs
    assert "thinking" not in second_kwargs
    assert "thinking_param_dropped" in events
    assert out.images_b64 == ["ZmFrZQ=="]


def test_generate_wraps_arbitrary_exceptions_in_apicallerror():
    cli = MagicMock()
    cli.images.generate.side_effect = RuntimeError("boom")
    req = GenerateRequest(prompt="x")
    with pytest.raises(ApiCallError) as ei:
        images_api.generate(req, client=cli)
    assert "images.generate failed" in str(ei.value)


def test_generate_invalid_size_raises_before_call():
    cli = MagicMock()
    req = GenerateRequest(prompt="x", size="100x100")
    with pytest.raises(UnsupportedParameterError):
        images_api.generate(req, client=cli)
    cli.images.generate.assert_not_called()


# ----- mocked edit() -----


def test_edit_opens_images_and_passes_to_sdk(tmp_path: Path):
    img = tmp_path / "in.png"
    img.write_bytes(b"\x89PNG\r\n")
    cli = MagicMock()
    cli.images.edit.return_value = _mock_response(b64="ZWRpdA==")
    req = EditRequest(prompt="make it pop", images=[img])
    out = images_api.edit(req, client=cli)
    cli.images.edit.assert_called_once()
    kwargs = cli.images.edit.call_args.kwargs
    assert kwargs["model"] == "gpt-image-2"
    assert kwargs["prompt"] == "make it pop"
    # Single image passed unwrapped
    assert hasattr(kwargs["image"], "read")
    assert out.images_b64 == ["ZWRpdA=="]


def test_edit_with_multiple_images_passes_list(tmp_path: Path):
    a = tmp_path / "a.png"
    b = tmp_path / "b.png"
    a.write_bytes(b"\x89PNG")
    b.write_bytes(b"\x89PNG")
    cli = MagicMock()
    cli.images.edit.return_value = _mock_response()
    req = EditRequest(prompt="merge", images=[a, b])
    images_api.edit(req, client=cli)
    kwargs = cli.images.edit.call_args.kwargs
    assert isinstance(kwargs["image"], list)
    assert len(kwargs["image"]) == 2


def test_edit_missing_image_raises(tmp_path: Path):
    missing = tmp_path / "nope.png"
    cli = MagicMock()
    req = EditRequest(prompt="x", images=[missing])
    with pytest.raises(UnsupportedParameterError):
        images_api.edit(req, client=cli)
    cli.images.edit.assert_not_called()
