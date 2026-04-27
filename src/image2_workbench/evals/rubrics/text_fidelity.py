# SPDX-License-Identifier: Apache-2.0
"""Text-fidelity rubric.

The gpt-image-2 prompting guidance recommends putting any literal text the
model must render inside double quotes, so the renderer treats the contents
as exact glyphs rather than a paraphrase target. The V1 rubric therefore
checks the *prompt* itself: every expected text block must appear verbatim,
surrounded by double quotes (ASCII " or curly Unicode quotes). This is a
necessary precondition for the rendered image to honor the text — without
quoting, downstream OCR-based grading is moot. V2 will additionally compare
OCR of the rendered image against the same expected blocks.
"""

from __future__ import annotations

from typing import Any

from ._base import GradeOutcome, Rubric

_QUOTE_PAIRS: list[tuple[str, str]] = [
    ('"', '"'),
    ("“", "”"),
    ("‘", "’"),
    ("'", "'"),
]


def _is_quoted(prompt: str, block: str) -> bool:
    for left, right in _QUOTE_PAIRS:
        needle = f"{left}{block}{right}"
        if needle in prompt:
            return True
    return False


class TextFidelityRubric(Rubric):
    name = "text_fidelity"

    def grade(self, case: dict[str, Any]) -> GradeOutcome:
        prompt = case.get("prompt", "")
        expected_blocks: list[str] = list(case.get("expected_text_blocks", []))
        case_id = case.get("case_id", "<unknown>")

        if not expected_blocks:
            return GradeOutcome(
                rubric=self.name,
                case_id=case_id,
                passed=False,
                score=0.0,
                findings=["no expected_text_blocks provided"],
            )

        findings: list[str] = []
        matched = 0
        for block in expected_blocks:
            if _is_quoted(prompt, block):
                matched += 1
            else:
                findings.append(f"missing quoted block: {block!r}")

        score = matched / len(expected_blocks)
        # 0.9 leaves room for a single very-short block (e.g. label) being
        # rephrased, but a real failure (none quoted) still trips the gate.
        passed = score >= 0.9

        return GradeOutcome(
            rubric=self.name,
            case_id=case_id,
            passed=passed,
            score=score,
            findings=findings,
            raw={"matched": matched, "total": len(expected_blocks)},
        )
