# SPDX-License-Identifier: Apache-2.0
"""Unit tests for `i2w gallery readme` helpers and round-trip behaviour.

The readme subcommand is the L0 (no-friction) homepage atlas surface:
markdown that lives between marker comments inside ``README.md`` /
``README.zh.md``. These tests cover the building blocks (the excerpt
helper, the section generator, the marker-replacement logic) and the
round-trip property — re-injecting the section after a manual edit
between the markers must restore the canonical output without drift.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from image2_workbench.commands import gallery as gallery_mod
from image2_workbench.commands.gallery import (
    README_BEGIN_FULL,
    README_BEGIN_PREFIX,
    README_END_MARKER,
    _excerpt,
    _generate_section,
    _replace_section,
)
from image2_workbench.errors import ExitCode, WorkbenchError


def _spec(description: str = "", subject: str = "") -> SimpleNamespace:
    """Build a duck-typed stand-in for ``TemplateSpec`` for excerpt tests."""
    return SimpleNamespace(description=description, spec=SimpleNamespace(subject=subject))


# --------------------------------------------------------------------------- #
# _excerpt — Jinja stripping, whitespace collapse, truncation.
# --------------------------------------------------------------------------- #

def test_excerpt_strips_jinja_placeholders() -> None:
    text = "A SWOT for {{company_name}} in {{quarter}} {{year}}"
    assert _excerpt(_spec(description=text), max_chars=120) == "A SWOT for … in … …"


def test_excerpt_truncates_with_ellipsis_at_boundary() -> None:
    long = "A" * 120
    out = _excerpt(_spec(description=long), max_chars=20)
    assert len(out) == 20
    assert out.endswith("…")
    assert out.rstrip("…") == "A" * 19


def test_excerpt_collapses_whitespace() -> None:
    raw = "  multi\n  line\t description\nwith   blanks  "
    assert _excerpt(_spec(description=raw), max_chars=80) == (
        "multi line description with blanks"
    )


def test_excerpt_prefers_description_over_subject() -> None:
    spec = _spec(description="explicit description", subject="fallback subject")
    assert _excerpt(spec, max_chars=80) == "explicit description"


def test_excerpt_falls_back_to_subject_when_description_blank() -> None:
    spec = _spec(description="", subject="fallback subject")
    assert _excerpt(spec, max_chars=80) == "fallback subject"


def test_excerpt_returns_empty_string_when_both_blank() -> None:
    assert _excerpt(_spec(), max_chars=80) == ""


# --------------------------------------------------------------------------- #
# _generate_section — overall shape and bilingual variants.
# --------------------------------------------------------------------------- #

def test_section_contains_table_count_and_v1_template() -> None:
    section = _generate_section(lang="en", max_excerpt_chars=60)
    # ``<table cellpadding="12" cellspacing="0">`` post-V0.3.5 polish; we
    # match the open-tag prefix so the assertion stays robust to attribute
    # tweaks while still locking in that a top-level ``<table>`` exists.
    assert "<table " in section
    assert "</table>" in section
    assert "80 templates" in section
    assert "30 domains" in section
    # At least one V1 template id from each V1 domain must appear.
    for tid in (
        "business_swot_card",
        "academic_scientific_diagram",
        "uiux_ios_app_mockup",
        "anime_character_sheet",
    ):
        assert tid in section, f"missing V1 template id {tid!r}"


def test_section_en_and_zh_have_different_headings() -> None:
    en_section = _generate_section(lang="en", max_excerpt_chars=60)
    zh_section = _generate_section(lang="zh-CN", max_excerpt_chars=60)
    assert "## Atlas — 30 domains, 80 templates" in en_section
    assert "## 模板图册" in zh_section
    assert "30 个领域" in zh_section
    assert "80 个模板" in zh_section
    # Sub-table headers must localise too.
    assert "| template | size | grader |" in en_section
    assert "| 模板 | 尺寸 | 评测 |" in zh_section


def test_section_total_length_is_sane() -> None:
    section = _generate_section(lang="en", max_excerpt_chars=220)
    assert len(section) < 30_000


def test_section_starts_and_ends_with_markers() -> None:
    section = _generate_section(lang="en", max_excerpt_chars=60)
    assert section.startswith(README_BEGIN_FULL)
    assert section.rstrip().endswith(README_END_MARKER)


# --------------------------------------------------------------------------- #
# _replace_section — marker handling and round-trip safety.
# --------------------------------------------------------------------------- #

def test_replace_section_swaps_content_between_markers() -> None:
    existing = (
        "# README\n\n"
        "## intro\n\n"
        f"{README_BEGIN_PREFIX} (auto-generated) -->\n"
        "old gallery body\n"
        f"{README_END_MARKER}\n\n"
        "## footer\n"
    )
    section = _generate_section(lang="en", max_excerpt_chars=60)
    updated = _replace_section(existing, section)
    assert "old gallery body" not in updated
    assert "## intro" in updated
    assert "## footer" in updated
    assert "## Atlas — 30 domains, 80 templates" in updated


def test_replace_section_round_trip_is_idempotent() -> None:
    section = _generate_section(lang="en", max_excerpt_chars=60)
    base = (
        "# README\n\n"
        f"{README_BEGIN_PREFIX} (auto) -->\nplaceholder\n{README_END_MARKER}\n"
    )
    once = _replace_section(base, section)
    twice = _replace_section(once, section)
    assert once == twice


def test_replace_section_round_trip_after_manual_edit() -> None:
    """Re-injecting after edits between markers must restore canonical output."""
    section = _generate_section(lang="en", max_excerpt_chars=60)
    base = (
        "# README\n\n"
        f"{README_BEGIN_PREFIX} (auto) -->\nplaceholder\n{README_END_MARKER}\n"
        "after\n"
    )
    injected = _replace_section(base, section)
    # Simulate someone typing junk between the markers.
    tampered = injected.replace(
        "## Atlas — 30 domains, 80 templates",
        "## Atlas — 30 domains, 80 templates\n\nMANUAL EDIT, OOPS",
    )
    fixed = _replace_section(tampered, section)
    assert fixed == injected
    assert "MANUAL EDIT, OOPS" not in fixed


def test_replace_section_missing_begin_marker_raises() -> None:
    existing = "# README\n\nno markers here\n"
    section = _generate_section(lang="en", max_excerpt_chars=60)
    with pytest.raises(WorkbenchError) as excinfo:
        _replace_section(existing, section)
    env = excinfo.value.envelope
    assert env.code == "gallery_marker_missing"
    assert env.exit_code == ExitCode.VALIDATION


def test_replace_section_missing_end_marker_raises() -> None:
    existing = (
        "# README\n\n"
        f"{README_BEGIN_PREFIX} (auto) -->\nbody only, no end marker\n"
    )
    section = _generate_section(lang="en", max_excerpt_chars=60)
    with pytest.raises(WorkbenchError) as excinfo:
        _replace_section(existing, section)
    env = excinfo.value.envelope
    assert env.code == "gallery_marker_missing"
    assert env.exit_code == ExitCode.VALIDATION


def test_replace_section_tolerates_begin_marker_suffix_drift() -> None:
    """Different BEGIN suffixes (older or newer wording) still match the prefix."""
    section = _generate_section(lang="en", max_excerpt_chars=60)
    # Old-style suffix that a previous tool version might have written.
    older = (
        "# README\n"
        f"{README_BEGIN_PREFIX} v0 — old wording -->\nstale\n{README_END_MARKER}\n"
    )
    fixed = _replace_section(older, section)
    assert "stale" not in fixed
    # The injected section now carries the canonical begin marker.
    assert README_BEGIN_FULL in fixed


# --------------------------------------------------------------------------- #
# _generate_section — Jinja-strip behaviour bubbles up through real templates.
# --------------------------------------------------------------------------- #

def test_section_excerpts_have_no_jinja_placeholders() -> None:
    section = _generate_section(lang="en", max_excerpt_chars=220)
    # Real templates contain {{var}} placeholders in their subjects; the
    # excerpt helper must scrub them so the README never shows raw Jinja.
    assert "{{" not in section
    assert "}}" not in section


# --------------------------------------------------------------------------- #
# Module-level constants — guard against accidental rename.
# --------------------------------------------------------------------------- #

def test_marker_constants_are_stable() -> None:
    assert gallery_mod.README_BEGIN_PREFIX == "<!-- BEGIN GALLERY"
    assert gallery_mod.README_END_MARKER == "<!-- END GALLERY -->"
    assert gallery_mod.README_BEGIN_PREFIX in gallery_mod.README_BEGIN_FULL
