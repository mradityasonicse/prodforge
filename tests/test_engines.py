"""Test suite for all ProdForge core engines."""

import pytest
from pathlib import Path
from prodforge.engines.planner import generate_architecture_plan
from prodforge.engines.auditor import audit_code_or_path
from prodforge.engines.qa_tester import generate_test_suite
from prodforge.engines.hardener import generate_production_hardening
from prodforge.engines.feasibility import analyze_feasibility


def test_planner_engine():
    result = generate_architecture_plan(
        idea="Real-time multi-player game backend with WebSockets",
        constraints="Go or Python, Redis PubSub, PostgreSQL"
    )
    assert result is not None
    assert result.feasibility_score > 0
    assert "Architecture" in result.title or "Blueprint" in result.title
    assert len(result.markdown_report) > 100


def test_auditor_engine_vulnerable_code():
    vuln_code = """
API_KEY = "sk-1234567890abcdef123456"

def login(user, pw):
    query = f"SELECT * FROM users WHERE u = {user} FROM accounts"
    try:
        eval(user)
    except:
        pass
"""
    result = audit_code_or_path(target="<test>", raw_code=vuln_code)
    assert result is not None
    assert result.readiness_score < 60  # Should be heavily penalized
    assert result.critical_count >= 1
    assert result.readiness_grade in ("C", "F")
    assert len(result.findings) >= 2


def test_auditor_engine_clean_code():
    clean_code = """
import os
from pydantic import BaseModel

class UserPayload(BaseModel):
    user_id: int
    name: str

def get_user(payload: UserPayload) -> dict:
    return {"id": payload.user_id, "name": payload.name}
"""
    result = audit_code_or_path(target="<test>", raw_code=clean_code)
    assert result is not None
    assert result.readiness_score >= 90
    assert result.critical_count == 0
    assert result.readiness_grade == "A+"


def test_qa_tester_engine():
    sample_code = """
def add_numbers(a: int, b: int) -> int:
    \"\"\"Adds two integers.\"\"\"
    return a + b

def subtract_numbers(a: int, b: int) -> int:
    return a - b
"""
    result = generate_test_suite(target_path="math_utils.py", raw_code=sample_code)
    assert result is not None
    assert result.framework == "pytest"
    assert "test_add_numbers" in result.test_code
    assert "test_subtract_numbers" in result.test_code
    assert len(result.inferred_functions) == 2


def test_hardener_engine(tmp_path):
    # Create mock python project in tmp_path
    pyproj = tmp_path / "pyproject.toml"
    pyproj.write_text("[project]\nname='testapp'\n", encoding="utf-8")

    result = generate_production_hardening(project_path=str(tmp_path), apply=True)
    assert result is not None
    assert result.detected_stack == "python"
    assert len(result.artifacts) == 4
    assert (tmp_path / "Dockerfile").exists()
    assert (tmp_path / "docker-compose.yml").exists()
    assert (tmp_path / ".github" / "workflows" / "production-ci.yml").exists()
    assert (tmp_path / "health.py").exists()


def test_feasibility_engine():
    result = analyze_feasibility(idea="E-commerce flash sale platform", target_dau=100000)
    assert result is not None
    assert result.concurrency_target_rps > 0
    assert result.estimated_monthly_cost_usd > 50
    assert len(result.cost_breakdown) == 5
    assert len(result.bottlenecks) >= 1
