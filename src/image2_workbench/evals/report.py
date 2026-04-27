# SPDX-License-Identifier: Apache-2.0
"""Reporting helpers for grading outcomes."""

from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from .rubrics._base import GradeOutcome


def _group(outcomes: list[GradeOutcome]) -> dict[str, list[GradeOutcome]]:
    grouped: dict[str, list[GradeOutcome]] = defaultdict(list)
    for o in outcomes:
        grouped[o.rubric].append(o)
    return grouped


def report_markdown(outcomes: list[GradeOutcome]) -> str:
    """Compact markdown report grouped by rubric."""
    if not outcomes:
        return "# Eval report\n\n_No cases evaluated._\n"

    grouped = _group(outcomes)
    total = len(outcomes)
    passed = sum(1 for o in outcomes if o.passed)

    lines: list[str] = []
    lines.append("# Eval report")
    lines.append("")
    lines.append(f"**Overall:** {passed}/{total} passed")
    lines.append("")

    for rubric_name in sorted(grouped):
        rubric_outcomes = grouped[rubric_name]
        rubric_passed = sum(1 for o in rubric_outcomes if o.passed)
        lines.append(f"## {rubric_name} ({rubric_passed}/{len(rubric_outcomes)})")
        lines.append("")
        lines.append("| case_id | passed | score | findings |")
        lines.append("|---|---|---|---|")
        for o in rubric_outcomes:
            findings_text = "; ".join(o.findings) if o.findings else "—"
            mark = "yes" if o.passed else "no"
            lines.append(f"| {o.case_id} | {mark} | {o.score:.2f} | {findings_text} |")
        lines.append("")

    return "\n".join(lines)


def report_json(outcomes: list[GradeOutcome]) -> str:
    """JSON-serializable summary string."""
    grouped = _group(outcomes)
    payload: dict[str, Any] = {
        "total": len(outcomes),
        "passed": sum(1 for o in outcomes if o.passed),
        "by_rubric": {},
        "outcomes": [o.model_dump() for o in outcomes],
    }
    for rubric_name, rubric_outcomes in grouped.items():
        payload["by_rubric"][rubric_name] = {
            "total": len(rubric_outcomes),
            "passed": sum(1 for o in rubric_outcomes if o.passed),
            "mean_score": (
                sum(o.score for o in rubric_outcomes) / len(rubric_outcomes)
                if rubric_outcomes
                else 0.0
            ),
        }
    return json.dumps(payload, indent=2, sort_keys=True)
