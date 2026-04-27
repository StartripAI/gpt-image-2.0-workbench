# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ``compiler.loader.resolve_demo_vars``.

The resolver is convention-over-config: it looks for ``<stem>.yml`` first,
then ``<stem>_demo.yml``, then any single ``*.yml`` in ``_vars_examples/``,
with an optional ``override`` map that wins over all of the above. These
tests exercise every branch using ``tmp_path``-backed synthetic templates.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from image2_workbench.compiler.loader import (
    DEMO_VARS_DIRNAME,
    resolve_demo_vars,
)


def _make_template(domain_dir: Path, stem: str) -> Path:
    """Create a minimal template file and return its path."""
    domain_dir.mkdir(parents=True, exist_ok=True)
    template_path = domain_dir / f"{stem}.yml"
    template_path.write_text(f"id: {domain_dir.name}.{stem}\n", encoding="utf-8")
    return template_path


def _make_vars(vars_dir: Path, name: str, body: str = "k: v\n") -> Path:
    vars_dir.mkdir(parents=True, exist_ok=True)
    p = vars_dir / name
    p.write_text(body, encoding="utf-8")
    return p


def test_resolver_prefers_stem_yml_convention(tmp_path: Path) -> None:
    """``<stem>.yml`` wins over every other candidate when present."""
    domain = tmp_path / "alpha"
    template = _make_template(domain, "card")
    vars_dir = domain / DEMO_VARS_DIRNAME
    convention = _make_vars(vars_dir, "card.yml")
    _make_vars(vars_dir, "card_demo.yml")  # would-be runner-up
    _make_vars(vars_dir, "aaa_first.yml")  # would-be sorted-first fallback

    assert resolve_demo_vars(template) == convention


def test_resolver_falls_back_to_stem_demo_yml(tmp_path: Path) -> None:
    """When ``<stem>.yml`` is absent, ``<stem>_demo.yml`` is selected."""
    domain = tmp_path / "beta"
    template = _make_template(domain, "swot")
    vars_dir = domain / DEMO_VARS_DIRNAME
    demo = _make_vars(vars_dir, "swot_demo.yml")
    _make_vars(vars_dir, "another.yml")  # alphabetically first; should NOT win

    assert resolve_demo_vars(template) == demo


def test_resolver_falls_back_to_first_yml_when_no_stem_match(tmp_path: Path) -> None:
    """With no ``<stem>.yml`` or ``<stem>_demo.yml``, return the first ``*.yml``."""
    domain = tmp_path / "gamma"
    template = _make_template(domain, "pitch_slide")
    vars_dir = domain / DEMO_VARS_DIRNAME
    # Create files in non-sorted insertion order to confirm sorting.
    _make_vars(vars_dir, "zeta.yml")
    first = _make_vars(vars_dir, "alpha_demo.yml")
    _make_vars(vars_dir, "middle.yml")

    assert resolve_demo_vars(template) == first


def test_resolver_returns_none_when_vars_examples_empty(tmp_path: Path) -> None:
    domain = tmp_path / "delta"
    template = _make_template(domain, "anything")
    (domain / DEMO_VARS_DIRNAME).mkdir()

    assert resolve_demo_vars(template) is None


def test_resolver_returns_none_when_vars_examples_missing(tmp_path: Path) -> None:
    """No ``_vars_examples/`` directory at all → ``None`` (not an error)."""
    domain = tmp_path / "epsilon"
    template = _make_template(domain, "lonely")

    assert resolve_demo_vars(template) is None


def test_override_takes_precedence_over_convention(tmp_path: Path) -> None:
    """The ``override`` map wins even when a convention file exists."""
    domain = tmp_path / "business"
    template = _make_template(domain, "swot_card")
    vars_dir = domain / DEMO_VARS_DIRNAME
    _make_vars(vars_dir, "swot_card.yml")  # convention candidate (loses)
    legacy = _make_vars(vars_dir, "swot_acme.yml")

    override = {"business/swot_card": "business/_vars_examples/swot_acme.yml"}
    assert resolve_demo_vars(template, override=override) == legacy


def test_override_returns_none_when_target_missing(tmp_path: Path) -> None:
    """If the override points to a non-existent file, return ``None`` (no fallback)."""
    domain = tmp_path / "business"
    template = _make_template(domain, "swot_card")
    (domain / DEMO_VARS_DIRNAME).mkdir()

    override = {"business/swot_card": "business/_vars_examples/does_not_exist.yml"}
    # Override resolution is final once the key matches; we don't silently
    # fall through to convention. This makes mis-typed overrides loud.
    assert resolve_demo_vars(template, override=override) is None


def test_override_unmatched_falls_through_to_convention(tmp_path: Path) -> None:
    """If the override map has no matching key, convention still applies."""
    domain = tmp_path / "uiux"
    template = _make_template(domain, "ios_app_mockup")
    vars_dir = domain / DEMO_VARS_DIRNAME
    convention = _make_vars(vars_dir, "ios_app_mockup.yml")

    override = {"business/swot_card": "business/_vars_examples/swot_acme.yml"}
    assert resolve_demo_vars(template, override=override) == convention


def test_resolver_skips_dotfiles_and_gitkeep(tmp_path: Path) -> None:
    """Dotfiles and ``.gitkeep`` must never be returned as a vars file."""
    domain = tmp_path / "zeta"
    template = _make_template(domain, "ghost")
    vars_dir = domain / DEMO_VARS_DIRNAME
    vars_dir.mkdir()
    (vars_dir / ".gitkeep").write_text("", encoding="utf-8")
    (vars_dir / ".hidden.yml").write_text("k: v\n", encoding="utf-8")

    # Nothing else exists, so the resolver should return None rather than
    # return a dotfile.
    assert resolve_demo_vars(template) is None


def test_resolver_skips_dotfiles_when_real_vars_present(tmp_path: Path) -> None:
    """A real vars file is preferred even if a dotfile sorts earlier."""
    domain = tmp_path / "eta"
    template = _make_template(domain, "report")
    vars_dir = domain / DEMO_VARS_DIRNAME
    vars_dir.mkdir()
    (vars_dir / ".hidden.yml").write_text("k: v\n", encoding="utf-8")
    real = _make_vars(vars_dir, "report.yml")

    assert resolve_demo_vars(template) == real


def test_resolver_does_not_recurse_into_nested_vars_examples(tmp_path: Path) -> None:
    """A pathological ``_vars_examples/_vars_examples/foo.yml`` must NOT be picked up.

    The resolver scans only the immediate ``_vars_examples/`` directory; an
    accidentally-nested second level is invisible (and harmless).
    """
    domain = tmp_path / "theta"
    template = _make_template(domain, "weird")
    vars_dir = domain / DEMO_VARS_DIRNAME
    vars_dir.mkdir()
    nested = vars_dir / DEMO_VARS_DIRNAME
    nested.mkdir()
    (nested / "deep.yml").write_text("k: v\n", encoding="utf-8")

    # Top level has only the nested dir; resolver must return None.
    assert resolve_demo_vars(template) is None


def test_resolver_ignores_non_yml_files(tmp_path: Path) -> None:
    """Non-``.yml`` files (READMEs, JSON, etc.) must not be selected."""
    domain = tmp_path / "iota"
    template = _make_template(domain, "doc")
    vars_dir = domain / DEMO_VARS_DIRNAME
    vars_dir.mkdir()
    (vars_dir / "README.md").write_text("# notes\n", encoding="utf-8")
    (vars_dir / "data.json").write_text("{}\n", encoding="utf-8")

    assert resolve_demo_vars(template) is None


@pytest.mark.parametrize("override_arg", [None, {}])
def test_resolver_accepts_none_or_empty_override(tmp_path: Path, override_arg) -> None:
    """``override=None`` and ``override={}`` both behave as 'no override'."""
    domain = tmp_path / "kappa"
    template = _make_template(domain, "card")
    vars_dir = domain / DEMO_VARS_DIRNAME
    expected = _make_vars(vars_dir, "card.yml")

    assert resolve_demo_vars(template, override=override_arg) == expected
