"""Test suite for the CI/CD Pipeline Generator Engine."""

from prodforge.engines.ci_generator import generate_ci_workflows


def test_ci_generator_github_actions():
    workflows = generate_ci_workflows(min_score=85)

    assert workflows is not None
    assert workflows.min_score == 85

    # Check GitHub Actions syntax
    gh = workflows.github_actions_workflow
    assert "name: ProdForge Production Gate" in gh
    assert "--fail-under 85" in gh
    assert "upload-sarif" in gh

    # Check GitLab CI syntax
    gl = workflows.gitlab_ci_pipeline
    assert gl is not None
    assert "prodforge_gate:" in gl
    assert "--fail-under 85" in gl
    assert "reports:" in gl
    assert "sast: gl-sast-report.json" in gl
