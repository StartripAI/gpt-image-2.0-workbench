# SPDX-License-Identifier: Apache-2.0
"""Eval runner.

Loads a YAML rubric file and grades every case under the rubric named in
the file header. The file format is intentionally minimal so authors can
add cases without writing Python.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .rubrics._base import GradeOutcome, Rubric
from .rubrics.continuity import ContinuityRubric
from .rubrics.edit_locality import EditLocalityRubric
from .rubrics.layout_fidelity import LayoutFidelityRubric
from .rubrics.text_fidelity import TextFidelityRubric

RUBRICS: dict[str, type[Rubric]] = {
    "text_fidelity": TextFidelityRubric,
    "layout_fidelity": LayoutFidelityRubric,
    "edit_locality": EditLocalityRubric,
    "continuity": ContinuityRubric,
}


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a mapping at top-level, got {type(data).__name__}")
    return data


def run_rubric_file(path: Path) -> list[GradeOutcome]:
    """Load and grade every case in a YAML rubric file.

    Expected schema::

        rubric: <rubric_name>
        cases:
          - case_id: ...
            <rubric-specific fields>
    """
    data = _load_yaml(path)
    rubric_name = data.get("rubric")
    if rubric_name not in RUBRICS:
        raise ValueError(
            f"{path}: unknown rubric {rubric_name!r}; known: {sorted(RUBRICS)}"
        )
    grader = RUBRICS[rubric_name]()

    cases = data.get("cases") or []
    if not isinstance(cases, list):
        raise ValueError(f"{path}: 'cases' must be a list")

    outcomes: list[GradeOutcome] = []
    for raw_case in cases:
        if not isinstance(raw_case, dict):
            raise ValueError(f"{path}: each case must be a mapping")
        outcomes.append(grader.grade(raw_case))
    return outcomes


def run_rubric_files(paths: list[Path]) -> list[GradeOutcome]:
    out: list[GradeOutcome] = []
    for p in paths:
        out.extend(run_rubric_file(p))
    return out
