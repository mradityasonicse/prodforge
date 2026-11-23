"""Test suite for the OASIS SARIF v2.1.0 Exporter."""

import json
from pathlib import Path
from prodforge.engines.auditor import audit_code_or_path
from prodforge.engines.sarif_exporter import export_to_sarif, save_sarif_file


def test_sarif_export_structure(tmp_path):
    vuln_code = """
AWS_KEY = "AKIAIOSFODNN7EXAMPLE"
query = f"SELECT * FROM users WHERE id = {user_id} FROM accounts"
"""
    result = audit_code_or_path(target="<test>", raw_code=vuln_code)
    sarif = export_to_sarif(result)

    assert sarif["version"] == "2.1.0"
    assert "$schema" in sarif
    assert len(sarif["runs"]) == 1

    run = sarif["runs"][0]
    assert run["tool"]["driver"]["name"] == "ProdForge"
    assert len(run["tool"]["driver"]["rules"]) > 0
    assert len(run["results"]) > 0

    first_result = run["results"][0]
    assert "ruleId" in first_result
    assert "level" in first_result
    assert "locations" in first_result

    # Test file saving
    sarif_file = tmp_path / "test_report.sarif"
    save_sarif_file(result, sarif_file)
    assert sarif_file.exists()

    content = json.loads(sarif_file.read_text(encoding="utf-8"))
    assert content["version"] == "2.1.0"
