# SPDX-License-Identifier: Apache-2.0
"""Base types for rubric graders.

V1 rubrics are *prompt-level* graders: they inspect the compiled prompt text
and a few golden expectations, never the rendered image. A V2 hook for vision
grading is anticipated but not implemented here — we keep `Rubric.grade`
generic enough to take a free-form `case` mapping so V2 can attach OCR
results, image hashes, etc., without breaking the V1 callers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class GradeOutcome(BaseModel):
    rubric: str
    case_id: str
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    findings: list[str] = []
    raw: dict[str, Any] = {}


class Rubric(ABC):
    name: str

    @abstractmethod
    def grade(self, case: dict[str, Any]) -> GradeOutcome:
        ...
