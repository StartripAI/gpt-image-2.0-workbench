from datetime import UTC, datetime
from pathlib import Path

from image2_workbench.catalog.provenance import (
    ProvenanceRecord,
    license_audit,
    read_jsonl,
    write_jsonl,
)


def _record(**overrides) -> ProvenanceRecord:
    base = dict(
        record_id="rec-001",
        source_id="openai-cookbook-image-prompting",
        source_url="https://developers.openai.com/cookbook/example-1",
        author=None,
        captured_at=datetime(2026, 4, 1, 12, 0, tzinfo=UTC),
        language="en",
        license_declared="OpenAI documentation (citation only)",
        license_observed="OpenAI documentation (citation only)",
        license_status="metadata_only",
        redistributable="none",
        metadata_only=True,
        tags=["poster", "marketing"],
        notes="",
    )
    base.update(overrides)
    return ProvenanceRecord(**base)


def test_roundtrip_write_then_read(tmp_path: Path):
    records = [
        _record(record_id="rec-001"),
        _record(
            record_id="rec-002",
            source_id="wuyoscar-gpt-image-2-skill",
            source_url="https://github.com/wuyoscar/gpt_image_2_skill/blob/main/README.md",
            author="wuyoscar",
            license_declared="CC-BY-4.0",
            license_observed="CC-BY-4.0",
            license_status="clear",
            redistributable="with_attribution",
            tags=["skill", "methodology"],
        ),
    ]
    out = tmp_path / "provenance.jsonl"
    write_jsonl(records, out)
    loaded = read_jsonl(out)
    assert loaded == records


def test_write_jsonl_creates_parent_dirs(tmp_path: Path):
    out = tmp_path / "nested" / "deeper" / "p.jsonl"
    write_jsonl([_record()], out)
    assert out.exists()


def test_license_audit_clean():
    records = [
        _record(record_id="rec-001"),
        _record(
            record_id="rec-002",
            license_declared="CC-BY-4.0",
            license_observed="CC-BY-4.0",
            license_status="clear",
            redistributable="with_attribution",
        ),
    ]
    assert license_audit(records) == []


def test_license_audit_flags_ambiguous_and_mismatch():
    records = [
        _record(
            record_id="amb-1",
            license_declared="MIT",
            license_observed="Unknown",
            license_status="ambiguous",
        ),
    ]
    findings = license_audit(records)
    joined = "\n".join(findings)
    assert "amb-1" in joined
    assert "ambiguous" in joined
    assert "license_declared != license_observed" in joined


def test_license_audit_flags_full_text_with_no_redistribution():
    records = [
        _record(
            record_id="bad-fulltext",
            license_status="clear",
            redistributable="none",
            metadata_only=False,
        ),
    ]
    findings = license_audit(records)
    assert any("bad-fulltext" in f and "metadata_only=False" in f for f in findings)


def test_license_audit_flags_full_text_with_unclear_license():
    records = [
        _record(
            record_id="bad-unclear",
            license_status="metadata_only",
            redistributable="none",
            metadata_only=False,
        ),
    ]
    findings = license_audit(records)
    assert any(
        "bad-unclear" in f and "full-text storage requires clear license" in f
        for f in findings
    )
