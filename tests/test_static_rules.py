"""Test suite for static security and quality analysis rules."""

from prodforge.static_rules.security_rules import scan_security
from prodforge.static_rules.quality_rules import scan_quality


def test_detect_hardcoded_secret():
    code = 'DATABASE_PASSWORD = "SuperSecretPassword12345!"'
    findings = scan_security(code)
    assert any(f.rule_id == "SEC-001" for f in findings)


def test_detect_sql_injection():
    code = 'query = f"SELECT * FROM users WHERE id = {user_id} FROM accounts"'
    findings = scan_security(code)
    assert any(f.rule_id == "SEC-002" for f in findings)


def test_detect_eval_rce():
    code = 'result = eval(user_input)'
    findings = scan_security(code)
    assert any(f.rule_id == "SEC-003" for f in findings)


def test_detect_shell_true_injection():
    code = 'subprocess.call(cmd, shell=True)'
    findings = scan_security(code)
    assert any(f.rule_id == "SEC-004" for f in findings)


def test_detect_dangerously_set_inner_html():
    code = '<div dangerouslySetInnerHTML={{ __html: userRawHtml }} />'
    findings = scan_security(code)
    assert any(f.rule_id == "SEC-005" for f in findings)


def test_detect_blind_exception():
    code = """
try:
    process_data()
except:
    pass
"""
    findings = scan_quality(code)
    assert any(f.rule_id == "QUAL-001" for f in findings)


def test_detect_console_log():
    code = 'console.log("Debugging user transaction", txId);'
    findings = scan_quality(code)
    assert any(f.rule_id == "QUAL-002" for f in findings)


def test_detect_loose_any_type():
    code = 'function process(data: any) { return data; }'
    findings = scan_quality(code)
    assert any(f.rule_id == "QUAL-003" for f in findings)
