"""Test suite for the Enterprise Governance & Policy Engine."""

from pathlib import Path
from prodforge.governance import (
    EnterprisePolicy,
    find_governance_file,
    load_governance_policy,
    create_default_governance_file
)


def test_default_enterprise_policy():
    policy = EnterprisePolicy()
    assert policy.threshold == 80
    assert policy.fail_on_critical is True
    assert policy.fail_on_high is False
    assert "QUAL-002" in policy.ignore_rules
    assert policy.is_path_ignored("tests/test_file.py")
    assert policy.is_path_ignored("node_modules/package/index.js")
    assert not policy.is_path_ignored("src/main.py")


def test_create_and_load_governance_file(tmp_path):
    policy_path = create_default_governance_file(tmp_path)
    assert policy_path.exists()
    assert policy_path.name == ".prodforge.yaml"

    found = find_governance_file(tmp_path)
    assert found == policy_path

    loaded_policy = load_governance_policy(tmp_path)
    assert loaded_policy.threshold == 80
    assert loaded_policy.fail_on_critical is True
    assert loaded_policy.is_rule_ignored("QUAL-002")
