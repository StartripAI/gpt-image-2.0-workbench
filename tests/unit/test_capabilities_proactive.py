# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the proactive parameter-compatibility table.

These tests cover the static ``known_failure_patterns()`` helper added in
V1.5 Phase A and intentionally do not duplicate the live-probe coverage in
``test_capabilities.py``.
"""

from __future__ import annotations

from image2_workbench.runtimes.capabilities import known_failure_patterns


def test_known_failure_patterns_has_at_least_four_entries() -> None:
    patterns = known_failure_patterns()
    assert len(patterns) >= 4


def test_each_entry_has_required_fields() -> None:
    required = {"pattern", "code", "severity", "message"}
    for entry in known_failure_patterns():
        assert required.issubset(entry.keys()), entry
        for field in required:
            assert isinstance(entry[field], str)
            assert entry[field], f"empty {field} in {entry}"


def test_input_fidelity_pattern_present() -> None:
    patterns = known_failure_patterns()
    matches = [p for p in patterns if "input_fidelity" in p["pattern"]]
    assert matches, "input_fidelity pattern missing from compatibility table"
    assert any(p["code"] == "input_fidelity_unsupported" for p in matches)


def test_transparent_pattern_present() -> None:
    patterns = known_failure_patterns()
    matches = [p for p in patterns if "transparent" in p["pattern"]]
    assert matches, "transparent background pattern missing from compatibility table"
    assert any(p["code"] == "transparent_bg_unsupported" for p in matches)


def test_returned_list_is_a_copy_not_module_state() -> None:
    """Mutating the return value must not corrupt later calls."""
    first = known_failure_patterns()
    first.append({"pattern": "x", "code": "x", "severity": "error", "message": "x"})
    second = known_failure_patterns()
    assert len(second) < len(first)
