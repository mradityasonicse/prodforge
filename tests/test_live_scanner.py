"""Tests for the Live DAST & Security Header Scanner Engine."""

import pytest
from prodforge.engines.live_scanner import scan_live_url, convert_live_scan_to_audit_result, inspect_ssl
from prodforge.engines.auditor import is_live_url, is_git_url, audit_code_or_path


def test_is_live_url_vs_git_url():
    # Live URLs
    assert is_live_url("http://localhost:8000") is True
    assert is_live_url("https://example.com") is True
    assert is_live_url("http://127.0.0.1:3000/api") is True

    # Git URLs
    assert is_live_url("https://github.com/octocat/Hello-World.git") is False
    assert is_live_url("git@github.com:owner/repo.git") is False
    assert is_git_url("https://github.com/octocat/Hello-World.git") is True
    assert is_git_url("https://gitlab.com/group/repo") is True

    # Local files
    assert is_live_url("src/main.py") is False
    assert is_live_url("D:\\prodforge") is False


def test_scan_live_url_localhost():
    # Test against the running studio on localhost
    result = scan_live_url("http://127.0.0.1:8000", probe_endpoints=False)
    assert result is not None
    assert result.status_code == 200
    assert result.response_time_ms >= 0.0
    assert len(result.security_headers) > 0

    # Convert to CodeAuditResult
    audit_res = convert_live_scan_to_audit_result(result)
    assert audit_res is not None
    assert audit_res.readiness_score >= 0
    assert audit_res.pillars.security_score is not None
    assert audit_res.summary is not None


def test_audit_code_or_path_routing_to_live():
    # Test that audit_code_or_path automatically detects live URL
    res = audit_code_or_path(target="http://127.0.0.1:8000")
    assert res is not None
    assert "Live DAST Scan" in res.summary
