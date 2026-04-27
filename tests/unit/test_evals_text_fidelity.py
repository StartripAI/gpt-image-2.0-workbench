# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the text-fidelity rubric."""

from __future__ import annotations

from image2_workbench.evals.rubrics.text_fidelity import TextFidelityRubric


def test_all_blocks_quoted_passes() -> None:
    rubric = TextFidelityRubric()
    case = {
        "case_id": "all_quoted",
        "expected_text_blocks": ["Acme Corp", "Strengths", "Weaknesses"],
        "prompt": (
            'Render a SWOT poster titled "Acme Corp" with quadrants labeled '
            '"Strengths", "Weaknesses", "Opportunities", and "Threats".'
        ),
    }
    outcome = rubric.grade(case)
    assert outcome.passed is True
    assert outcome.score == 1.0
    assert outcome.findings == []
    assert outcome.rubric == "text_fidelity"
    assert outcome.case_id == "all_quoted"


def test_one_of_two_missing_fails() -> None:
    rubric = TextFidelityRubric()
    case = {
        "case_id": "half_missing",
        "expected_text_blocks": ["Quarterly Earnings", "Acme 2026"],
        "prompt": 'Render a poster with the title "Quarterly Earnings" set in serif.',
    }
    outcome = rubric.grade(case)
    assert outcome.passed is False
    assert outcome.score == 0.5
    assert any("Acme 2026" in f for f in outcome.findings)


def test_unquoted_mention_fails() -> None:
    rubric = TextFidelityRubric()
    case = {
        "case_id": "no_quotes",
        "expected_text_blocks": ["Q3 Report"],
        "prompt": "Render a one-page Q3 Report cover for Acme.",
    }
    outcome = rubric.grade(case)
    assert outcome.passed is False
    assert outcome.score == 0.0
    assert outcome.findings


def test_smart_quotes_accepted() -> None:
    rubric = TextFidelityRubric()
    case = {
        "case_id": "smart_quotes",
        "expected_text_blocks": ["Vision 2030"],
        "prompt": "Render a billboard with the headline “Vision 2030” centered.",
    }
    outcome = rubric.grade(case)
    assert outcome.passed is True
    assert outcome.score == 1.0


def test_no_expected_blocks_fails_clearly() -> None:
    rubric = TextFidelityRubric()
    case = {"case_id": "empty", "expected_text_blocks": [], "prompt": "anything"}
    outcome = rubric.grade(case)
    assert outcome.passed is False
    assert outcome.score == 0.0
    assert "no expected_text_blocks" in outcome.findings[0]
