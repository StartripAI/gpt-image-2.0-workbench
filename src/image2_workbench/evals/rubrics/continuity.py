# SPDX-License-Identifier: Apache-2.0
"""Continuity rubric.

Targets multi-panel and series prompts where the same character or scene
must persist across panels. We check that the prompt enumerates the
character anchors (hairstyle, outfit silhouette, etc.) AND uses an
explicit continuity verb so the model knows to preserve them. Prompts
that name the anchors without a continuity directive often produce
panels that drift, so we require both.
"""

from __future__ import annotations

from typing import Any

from ._base import GradeOutcome, Rubric

_CONTINUITY_PHRASES: list[str] = [
    "consistent",
    "consistency",
    "maintain",
    "preserve",
    "keep the same",
    "across all panels",
    "across panels",
    "throughout",
    "identical across",
    "same character",
]


def _has_continuity_phrase(prompt: str) -> list[str]:
    lowered = prompt.lower()
    return [p for p in _CONTINUITY_PHRASES if p in lowered]


class ContinuityRubric(Rubric):
    name = "continuity"

    def grade(self, case: dict[str, Any]) -> GradeOutcome:
        prompt = case.get("prompt", "")
        expected_anchors: list[str] = list(case.get("expected_anchors", []))
        case_id = case.get("case_id", "<unknown>")

        findings: list[str] = []

        if not expected_anchors:
            return GradeOutcome(
                rubric=self.name,
                case_id=case_id,
                passed=False,
                score=0.0,
                findings=["no expected_anchors provided"],
            )

        lowered_prompt = prompt.lower()
        anchor_hits: list[str] = []
        for anchor in expected_anchors:
            if anchor.lower() in lowered_prompt:
                anchor_hits.append(anchor)
            else:
                findings.append(f"anchor missing from prompt: {anchor!r}")

        anchor_ratio = len(anchor_hits) / len(expected_anchors)

        continuity_hits = _has_continuity_phrase(prompt)
        continuity_ok = bool(continuity_hits)
        if not continuity_ok:
            findings.append(
                "prompt lacks continuity phrasing "
                "(e.g. 'consistent', 'maintain', 'preserve', 'across all panels')"
            )

        score = (anchor_ratio + float(continuity_ok)) / 2.0
        passed = anchor_ratio >= 1.0 and continuity_ok

        return GradeOutcome(
            rubric=self.name,
            case_id=case_id,
            passed=passed,
            score=score,
            findings=findings,
            raw={
                "anchor_hits": anchor_hits,
                "anchor_total": len(expected_anchors),
                "continuity_hits": continuity_hits,
            },
        )
