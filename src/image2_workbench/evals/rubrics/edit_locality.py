# SPDX-License-Identifier: Apache-2.0
"""Edit-locality rubric.

For edit-style prompts (replace logo, change background, swap one element),
gpt-image-2 holds nearby pixels best when the prompt explicitly scopes the
change ("change only X", "exclusively X") and lists the elements to
preserve. This rubric checks both halves: locality phrasing AND a roll-call
of the preserve list. It is a prompt-shape proxy; V2 will diff the rendered
image against the source to validate locality directly.
"""

from __future__ import annotations

from typing import Any

from ._base import GradeOutcome, Rubric

_LOCALITY_PHRASES: list[str] = [
    "change only",
    "only the",
    "only modify",
    "only replace",
    "only update",
    "exclusively",
    "leaving the rest",
    "without altering",
    "without changing",
    "preserve everything else",
    "keep everything else",
]


def _has_locality(prompt: str) -> list[str]:
    lowered = prompt.lower()
    return [p for p in _LOCALITY_PHRASES if p in lowered]


class EditLocalityRubric(Rubric):
    name = "edit_locality"

    def grade(self, case: dict[str, Any]) -> GradeOutcome:
        prompt = case.get("prompt", "")
        expected_change: str = case.get("expected_change", "")
        expected_preserve: list[str] = list(case.get("expected_preserve", []))
        case_id = case.get("case_id", "<unknown>")

        findings: list[str] = []

        locality_hits = _has_locality(prompt)
        locality_ok = bool(locality_hits)
        if not locality_ok:
            findings.append(
                "prompt lacks locality phrasing (e.g. 'change only', 'exclusively', "
                "'without altering ...')"
            )

        lowered_prompt = prompt.lower()
        if expected_change and expected_change.lower() not in lowered_prompt:
            findings.append(f"prompt does not mention expected_change: {expected_change!r}")

        preserve_hits: list[str] = []
        for item in expected_preserve:
            if item.lower() in lowered_prompt:
                preserve_hits.append(item)
            else:
                findings.append(f"preserve item not mentioned: {item!r}")

        # Score is the average of (locality_ok, change_mentioned, preserve_coverage).
        change_ok = (not expected_change) or (expected_change.lower() in lowered_prompt)
        if expected_preserve:
            preserve_ratio = len(preserve_hits) / len(expected_preserve)
        else:
            preserve_ratio = 1.0

        score = (float(locality_ok) + float(change_ok) + preserve_ratio) / 3.0
        passed = locality_ok and change_ok and preserve_ratio >= 1.0

        return GradeOutcome(
            rubric=self.name,
            case_id=case_id,
            passed=passed,
            score=score,
            findings=findings,
            raw={
                "locality_hits": locality_hits,
                "preserve_hits": preserve_hits,
                "preserve_total": len(expected_preserve),
            },
        )
