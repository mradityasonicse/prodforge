"""
Enterprise CI/CD Governance & Pull Request Gate Generator.
Generates automated GitHub Actions and GitLab CI workflows that enforce
SARIF security upload, minimum Production Readiness Score thresholds, and PR comments.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field


class CIWorkflowArtifact(BaseModel):
    platform: str  # "github" | "gitlab"
    filename: str
    target_rel_path: str
    content: str
    description: str


class CIWorkflowResult(BaseModel):
    min_readiness_score: int
    artifacts: List[CIWorkflowArtifact] = Field(default_factory=list)
    applied: bool = False

    @property
    def min_score(self) -> int:
        return self.min_readiness_score

    @property
    def github_actions_workflow(self) -> str:
        for a in self.artifacts:
            if a.platform == "github":
                return a.content
        return ""

    @property
    def gitlab_ci_pipeline(self) -> str:
        for a in self.artifacts:
            if a.platform == "gitlab":
                return a.content
        return ""


def generate_ci_workflows(
    min_score: int = 85,
    project_dir: Optional[Path] = None,
    apply: bool = False,
    **kwargs
) -> CIWorkflowResult:
    """Generate enterprise PR governance CI/CD workflows."""
    github_yaml = f"""name: ProdForge Production Gate

on:
  pull_request:
    branches: [main, master, staging]
  push:
    branches: [main, master]

permissions:
  contents: read
  security-events: write
  pull-requests: write

jobs:
  prodforge-audit:
    name: Production Readiness & Security Gate
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install ProdForge
        run: |
          python -m pip install --upgrade pip
          pip install prodforge

      - name: Run Deep Code Audit & SARIF Generation
        id: audit
        run: |
          prodforge audit . --sarif prodforge.sarif --fail-under {min_score} --out audit-summary.md

      - name: Upload SARIF to GitHub Advanced Security
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: prodforge.sarif
          category: prodforge-governance

      - name: Post PR Summary Comment
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const fs = require('fs');
            if (fs.existsSync('audit-summary.md')) {{
              const summary = fs.readFileSync('audit-summary.md', 'utf8');
              github.rest.issues.createComment({{
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `## ⚡ ProdForge Enterprise Quality Gate\\n\\n` + summary
              }});
            }}
"""

    gitlab_yaml = f"""# ProdForge GitLab CI Governance Gate
stages:
  - test
  - security

prodforge_gate:
  stage: security
  image: python:3.12-slim
  script:
    - pip install --upgrade pip
    - pip install prodforge
    - prodforge audit . --sarif gl-sast-report.json --fail-under {min_score}
  artifacts:
    reports:
      sast: gl-sast-report.json
    when: always
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
"""

    artifacts = [
        CIWorkflowArtifact(
            platform="github",
            filename="prodforge-gate.yml",
            target_rel_path=".github/workflows/prodforge-gate.yml",
            content=github_yaml.strip(),
            description=f"GitHub Actions gate: SARIF upload, PR comment, fail if score < {min_score}"
        ),
        CIWorkflowArtifact(
            platform="gitlab",
            filename=".gitlab-ci.yml",
            target_rel_path=".gitlab-ci.yml",
            content=gitlab_yaml.strip(),
            description=f"GitLab CI SAST gate: fail if score < {min_score}"
        )
    ]

    applied = False
    if apply and project_dir:
        project_dir = Path(project_dir)
        for art in artifacts:
            dest = project_dir / art.target_rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(art.content, encoding="utf-8")
        applied = True

    return CIWorkflowResult(
        min_readiness_score=min_score,
        artifacts=artifacts,
        applied=applied
    )
