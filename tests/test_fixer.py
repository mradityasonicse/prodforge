"""Test suite for the Autonomous Self-Healing Fixer Engine."""

from pathlib import Path
from prodforge.engines.fixer import auto_fix_target


def test_auto_fixer_dry_run(tmp_path):
    test_file = tmp_path / "vulnerable_app.py"
    test_file.write_text(
        'DATABASE_PASSWORD = "HardcodedSecretPassword123!"\n'
        'try:\n'
        '    execute_job()\n'
        'except:\n'
        '    pass\n',
        encoding="utf-8"
    )

    result = auto_fix_target(target=str(test_file), apply=False)

    assert result.total_fixes_generated >= 1
    assert result.applied is False
    assert len(result.unified_diff) > 0
    assert "os.getenv" in result.unified_diff or "logger" in result.unified_diff

    # Ensure original file was NOT modified in dry-run
    content = test_file.read_text(encoding="utf-8")
    assert "HardcodedSecretPassword123!" in content


def test_auto_fixer_apply(tmp_path):
    test_file = tmp_path / "dirty_code.py"
    test_file.write_text(
        'try:\n'
        '    do_something()\n'
        'except:\n'
        '    pass\n',
        encoding="utf-8"
    )

    result = auto_fix_target(target=str(test_file), apply=True)

    assert result.applied is True
    updated_content = test_file.read_text(encoding="utf-8")
    assert "except Exception as exc:" in updated_content
