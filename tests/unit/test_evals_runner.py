# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the eval runner and report layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from image2_workbench.evals.report import report_json, report_markdown
from image2_workbench.evals.runner import RUBRICS, run_rubric_file

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN = REPO_ROOT / "tests" / "golden"


def test_runner_grades_text_fidelity_golden() -> None:
    outcomes = run_rubric_file(GOLDEN / "text_fidelity.yml")
    assert len(outcomes) == 3
    by_id = {o.case_id: o for o in outcomes}
    assert by_id["swot_acme_text"].passed is True
    assert by_id["missing_quote"].passed is False
    assert by_id["smart_quotes_ok"].passed is True
    assert all(o.rubric == "text_fidelity" for o in outcomes)


def test_runner_grades_layout_fidelity_golden() -> None:
    outcomes = run_rubric_file(GOLDEN / "layout_fidelity.yml")
    by_id = {o.case_id: o for o in outcomes}
    assert by_id["swot_quadrants_pass"].passed is True
    assert by_id["three_column_pass"].passed is True
    assert by_id["missing_layout_keyword"].passed is False


def test_runner_grades_edit_locality_golden() -> None:
    outcomes = run_rubric_file(GOLDEN / "edit_locality.yml")
    by_id = {o.case_id: o for o in outcomes}
    assert by_id["replace_logo_only"].passed is True
    assert by_id["missing_locality_phrase"].passed is False
    assert by_id["missing_preserve_item"].passed is False


def test_runner_grades_continuity_golden() -> None:
    outcomes = run_rubric_file(GOLDEN / "continuity.yml")
    by_id = {o.case_id: o for o in outcomes}
    assert by_id["anime_panels_pass"].passed is True
    assert by_id["missing_continuity_phrase"].passed is False
    assert by_id["missing_anchor"].passed is False


def test_runner_rejects_unknown_rubric(tmp_path: Path) -> None:
    bad = tmp_path / "bad.yml"
    bad.write_text("rubric: nope\ncases: []\n", encoding="utf-8")
    with pytest.raises(ValueError, match="unknown rubric"):
        run_rubric_file(bad)


def test_report_markdown_has_rubric_name() -> None:
    outcomes = run_rubric_file(GOLDEN / "text_fidelity.yml")
    md = report_markdown(outcomes)
    assert isinstance(md, str)
    assert md.strip()
    assert "text_fidelity" in md
    assert "Eval report" in md


def test_report_json_round_trips() -> None:
    outcomes = run_rubric_file(GOLDEN / "text_fidelity.yml")
    raw = report_json(outcomes)
    payload = json.loads(raw)
    assert payload["total"] == len(outcomes)
    assert "text_fidelity" in payload["by_rubric"]


def test_rubric_registry_keys_match_classes() -> None:
    for name, cls in RUBRICS.items():
        assert cls().name == name
