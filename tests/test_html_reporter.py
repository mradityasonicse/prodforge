"""Test suite for the Standalone Executive HTML Audit Reporter."""

from pathlib import Path
from prodforge.engines.auditor import audit_code_or_path
from prodforge.engines.html_reporter import generate_html_audit_report, save_html_report


def test_generate_html_report(tmp_path):
    code = """
import os

def process():
    return True
"""
    result = audit_code_or_path(target="<test>", raw_code=code)
    html_out = generate_html_audit_report(result, target_name="test_service")

    assert "<!DOCTYPE html>" in html_out
    assert "PRODFORGE" in html_out
    assert "Production Readiness Index" in html_out
    assert "5-Pillar Readiness Scorecard" in html_out
    assert str(result.readiness_score) in html_out

    # Test file saving
    report_file = tmp_path / "executive_report.html"
    save_html_report(result, "test_service", report_file)
    assert report_file.exists()
    content = report_file.read_text(encoding="utf-8")
    assert "<!DOCTYPE html>" in content
