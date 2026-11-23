"""Test suite for the Enterprise PDF Audit Reporter."""

import os
from pathlib import Path
from prodforge.engines.auditor import audit_code_or_path
from prodforge.engines.pdf_reporter import find_browser_executable, generate_pdf_audit_report


def test_find_browser_executable():
    browser = find_browser_executable()
    # On systems with Chrome or Edge installed, browser is found
    if browser:
        assert os.path.exists(browser)
        assert os.path.isfile(browser)


def test_generate_pdf_report(tmp_path):
    browser = find_browser_executable()
    if not browser:
        return  # Skip test on environments without headless browser installed

    code = """
import os

def process():
    # Safe code
    return True
"""
    result = audit_code_or_path(target="<test>", raw_code=code)
    pdf_out = tmp_path / "executive_report.pdf"

    generated_path = generate_pdf_audit_report(result, target_name="test_service", output_path=str(pdf_out))
    assert Path(generated_path).exists()
    assert Path(generated_path).stat().st_size > 0

    with open(generated_path, "rb") as f:
        header = f.read(5)
        assert header.startswith(b"%PDF-")
