# SPDX-License-Identifier: Apache-2.0
"""Layout-fidelity rubric.

A V1, prompt-level proxy for "does the rendered image obey the requested
composition?". We check that the prompt mentions the expected layout
keywords; if a template asks for a 4-quadrant SWOT but the compiled prompt
never mentions quadrants/grids, the image will almost certainly drift.
"""

from __future__ import annotations

from typing import Any

from ._base import GradeOutcome, Rubric

# Each canonical grid maps to a set of acceptable surface forms. We require
# at least one keyword per group ("any of") for the case to pass — this is
# loose enough to allow phrasing variation but strict enough to catch
# templates that forgot composition wording entirely.
_GRID_KEYWORDS: dict[str, list[str]] = {
    "4-quadrant": ["4-quadrant", "four-quadrant", "quadrant", "2x2 grid"],
    "2x2": ["2x2", "two-by-two", "quadrant", "2x2 grid"],
    "3-column": ["3-column", "three-column", "three columns", "tri-column"],
    "2-column": ["2-column", "two-column", "two columns"],
    "2x4": ["2x4", "two-by-four", "2 by 4", "8-cell grid"],
    "3x3": ["3x3", "three-by-three", "9-cell grid"],
    "single": ["single panel", "single composition", "one frame"],
    "diptych": ["diptych", "two-panel", "side-by-side panels"],
    "triptych": ["triptych", "three-panel"],
    "storyboard": ["storyboard", "panel sequence", "comic strip"],
}


def _normalize(text: str) -> str:
    return text.lower()


class LayoutFidelityRubric(Rubric):
    name = "layout_fidelity"

    def grade(self, case: dict[str, Any]) -> GradeOutcome:
        prompt = _normalize(case.get("prompt", ""))
        expected_grid: str = case.get("expected_grid", "")
        case_id = case.get("case_id", "<unknown>")

        if not expected_grid:
            return GradeOutcome(
                rubric=self.name,
                case_id=case_id,
                passed=False,
                score=0.0,
                findings=["no expected_grid provided"],
            )

        keywords = _GRID_KEYWORDS.get(expected_grid)
        if keywords is None:
            return GradeOutcome(
                rubric=self.name,
                case_id=case_id,
                passed=False,
                score=0.0,
                findings=[f"unknown expected_grid: {expected_grid!r}"],
                raw={"expected_grid": expected_grid},
            )

        hits = [k for k in keywords if k.lower() in prompt]
        score = 1.0 if hits else 0.0
        passed = score >= 1.0
        findings: list[str] = []
        if not hits:
            findings.append(
                f"prompt missing any of layout keywords for {expected_grid!r}: {keywords}"
            )

        return GradeOutcome(
            rubric=self.name,
            case_id=case_id,
            passed=passed,
            score=score,
            findings=findings,
            raw={"expected_grid": expected_grid, "matched_keywords": hits},
        )
