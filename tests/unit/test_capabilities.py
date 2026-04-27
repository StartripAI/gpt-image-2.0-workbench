"""Unit tests for the capability probe."""

from __future__ import annotations

from unittest.mock import MagicMock

from image2_workbench.runtimes import capabilities


def test_probe_no_api_key(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    p = capabilities.probe()
    assert p.has_api_key is False
    assert p.supports_transparent_background is False
    assert any("OPENAI_API_KEY" in n for n in p.notes)
    # Never crashes, always returns a probe.


def test_probe_transparent_always_false(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    cli = MagicMock()
    listing = MagicMock()
    m1 = MagicMock()
    m1.id = "gpt-image-2-2026-04-21"
    m2 = MagicMock()
    m2.id = "gpt-4o"
    listing.data = [m1, m2]
    cli.models.list.return_value = listing
    p = capabilities.probe(client=cli)
    assert p.has_api_key is True
    assert p.supports_transparent_background is False
    assert p.org_verified is True
    assert p.notes  # has a note about the snapshot


def test_probe_no_image_model_visible(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    cli = MagicMock()
    listing = MagicMock()
    m1 = MagicMock()
    m1.id = "gpt-4o"
    listing.data = [m1]
    cli.models.list.return_value = listing
    p = capabilities.probe(client=cli)
    assert p.has_api_key is True
    assert p.org_verified is False
    assert p.supports_transparent_background is False


def test_probe_swallows_network_errors(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-fake")
    cli = MagicMock()
    cli.models.list.side_effect = ConnectionError("offline")
    p = capabilities.probe(client=cli)
    # Should not raise.
    assert p.has_api_key is True
    assert p.supports_transparent_background is False
    assert any("models.list failed" in n for n in p.notes)
