"""
Deep Code Auditing & Production Readiness Analyzer Engine.
Performs static analysis, secret detection, OWASP Top 10 vulnerability discovery,
complexity heuristics, and LLM-assisted contextual remediation.
"""

from __future__ import annotations

import ast
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from prodforge.static_rules.security_rules import scan_security, VulnerabilityFinding
from prodforge.static_rules.quality_rules import scan_quality, QualityFinding
from prodforge.client import LLMClient, OfflineModeException


class FileAuditFinding(BaseModel):
    file_path: str
    rule_id: str
    category: str  # "SECURITY" | "QUALITY" | "COMPLEXITY"
    title: str
    severity: str  # "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"
    line_number: int
    line_content: str
    description: str
    remediation: str


class ComplexityMetrics(BaseModel):
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    functions_count: int = 0
    classes_count: int = 0
    max_nesting_depth: int = 0
    cyclomatic_estimate: int = 1


class CodeAuditResult(BaseModel):
    target_path: str
    is_directory: bool
    total_files_scanned: int
    readiness_score: int  # 0 to 100
    readiness_grade: str  # A+, B, C, F
    readiness_status: str
    summary: str
    metrics: ComplexityMetrics
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    findings: List[FileAuditFinding] = Field(default_factory=list)
    llm_recommendations: Optional[str] = None
    is_offline_fallback: bool = False


IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache",
    ".idea", ".vscode", "dist", "build", ".next", ".nuxt", "coverage", ".turbo"
}

AUDIT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".html", ".css", ".go", ".rs",
    ".php", ".java", ".rb", ".json", ".yaml", ".yml", ".env", ".sql"
}


def compute_python_ast_metrics(source: str) -> ComplexityMetrics:
    """Analyze Python code AST for complexity, nesting, and structure."""
    lines = source.splitlines()
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
    code_lines = sum(1 for line in lines if line.strip() and not line.strip().startswith("#"))

    functions_count = 0
    classes_count = 0
    max_nesting = 0
    branches = 1

    try:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions_count += 1
            elif isinstance(node, ast.ClassDef):
                classes_count += 1
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With)):
                branches += 1

        # Check line indentation depth
        for line in lines:
            stripped = line.lstrip()
            if stripped:
                indent_spaces = len(line) - len(stripped)
                depth = indent_spaces // 4
                if depth > max_nesting:
                    max_nesting = depth

    except SyntaxError:
        pass

    return ComplexityMetrics(
        total_lines=total_lines,
        code_lines=code_lines,
        comment_lines=comment_lines,
        functions_count=functions_count,
        classes_count=classes_count,
        max_nesting_depth=max_nesting,
        cyclomatic_estimate=branches
    )


def audit_single_file(file_path: Path) -> tuple[List[FileAuditFinding], ComplexityMetrics]:
    """Audit an individual file with security, quality, and complexity scanners."""
    findings: List[FileAuditFinding] = []
    metrics = ComplexityMetrics()

    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        findings.append(
            FileAuditFinding(
                file_path=str(file_path),
                rule_id="IO-ERR-001",
                category="QUALITY",
                title="Unreadable Source File",
                severity="LOW",
                line_number=1,
                line_content="",
                description=f"File could not be opened: {exc}",
                remediation="Ensure proper UTF-8 encoding and read permissions."
            )
        )
        return findings, metrics

    # 1. Static Security Scan
    sec_violations = scan_security(content)
    for v in sec_violations:
        findings.append(
            FileAuditFinding(
                file_path=str(file_path),
                rule_id=v.rule_id,
                category="SECURITY",
                title=v.title,
                severity=v.severity,
                line_number=v.line_number,
                line_content=v.line_content,
                description=v.description,
                remediation=v.remediation
            )
        )

    # 2. Static Quality Scan
    qual_violations = scan_quality(content)
    for q in qual_violations:
        findings.append(
            FileAuditFinding(
                file_path=str(file_path),
                rule_id=q.rule_id,
                category="QUALITY",
                title=q.title,
                severity=q.severity,
                line_number=q.line_number,
                line_content=q.line_content,
                description=q.description,
                remediation=q.remediation
            )
        )

    # 3. Complexity Heuristics
    if file_path.suffix == ".py":
        metrics = compute_python_ast_metrics(content)
        if metrics.max_nesting_depth >= 5:
            findings.append(
                FileAuditFinding(
                    file_path=str(file_path),
                    rule_id="COMPLEX-001",
                    category="COMPLEXITY",
                    title="Excessive Nesting Depth (>= 5 Levels)",
                    severity="MEDIUM",
                    line_number=1,
                    line_content="",
                    description=f"File contains nested control blocks reaching {metrics.max_nesting_depth} levels.",
                    remediation="Extract inner loops/conditions into dedicated helper functions or guard clauses."
                )
            )
        if metrics.cyclomatic_estimate > 20:
            findings.append(
                FileAuditFinding(
                    file_path=str(file_path),
                    rule_id="COMPLEX-002",
                    category="COMPLEXITY",
                    title="High Cyclomatic Complexity (> 20 Branches)",
                    severity="MEDIUM",
                    line_number=1,
                    line_content="",
                    description=f"File has estimated cyclomatic complexity of {metrics.cyclomatic_estimate}.",
                    remediation="Refactor branching decision trees into polymorphic strategies or lookup tables."
                )
            )
    else:
        lines = content.splitlines()
        metrics = ComplexityMetrics(
            total_lines=len(lines),
            code_lines=sum(1 for l in lines if l.strip()),
            comment_lines=0,
            functions_count=0,
            classes_count=0,
            max_nesting_depth=0,
            cyclomatic_estimate=1
        )

    return findings, metrics


def audit_code_or_path(
    target: str,
    raw_code: Optional[str] = None,
    language: Optional[str] = "python",
    model: Optional[str] = None
) -> CodeAuditResult:
    """Audit a directory, a single file, or a raw code string snippet."""
    all_findings: List[FileAuditFinding] = []
    combined_metrics = ComplexityMetrics()
    scanned_count = 0
    is_dir = False

    if raw_code is not None:
        # Audit raw in-memory code
        scanned_count = 1
        sec_violations = scan_security(raw_code)
        for v in sec_violations:
            all_findings.append(
                FileAuditFinding(
                    file_path="<in-memory-snippet>",
                    rule_id=v.rule_id,
                    category="SECURITY",
                    title=v.title,
                    severity=v.severity,
                    line_number=v.line_number,
                    line_content=v.line_content,
                    description=v.description,
                    remediation=v.remediation
                )
            )
        qual_violations = scan_quality(raw_code)
        for q in qual_violations:
            all_findings.append(
                FileAuditFinding(
                    file_path="<in-memory-snippet>",
                    rule_id=q.rule_id,
                    category="QUALITY",
                    title=q.title,
                    severity=q.severity,
                    line_number=q.line_number,
                    line_content=q.line_content,
                    description=q.description,
                    remediation=q.remediation
                )
            )
        if language == "python":
            combined_metrics = compute_python_ast_metrics(raw_code)
        else:
            lines = raw_code.splitlines()
            combined_metrics = ComplexityMetrics(
                total_lines=len(lines),
                code_lines=sum(1 for l in lines if l.strip())
            )
    else:
        path = Path(target).resolve()
        if not path.exists():
            raise FileNotFoundError(f"Target path '{target}' does not exist.")

        if path.is_file():
            scanned_count = 1
            f_findings, f_metrics = audit_single_file(path)
            all_findings.extend(f_findings)
            combined_metrics = f_metrics
        else:
            is_dir = True
            for root, dirs, files in os.walk(path):
                # Filter ignore dirs in-place
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".")]
                for f in files:
                    file_path = Path(root) / f
                    if file_path.suffix.lower() in AUDIT_EXTENSIONS:
                        scanned_count += 1
                        f_findings, f_metrics = audit_single_file(file_path)
                        all_findings.extend(f_findings)
                        combined_metrics.total_lines += f_metrics.total_lines
                        combined_metrics.code_lines += f_metrics.code_lines
                        combined_metrics.comment_lines += f_metrics.comment_lines
                        combined_metrics.functions_count += f_metrics.functions_count
                        combined_metrics.classes_count += f_metrics.classes_count
                        if f_metrics.max_nesting_depth > combined_metrics.max_nesting_depth:
                            combined_metrics.max_nesting_depth = f_metrics.max_nesting_depth
                        combined_metrics.cyclomatic_estimate += f_metrics.cyclomatic_estimate

    # Tally findings by severity
    critical_count = sum(1 for f in all_findings if f.severity == "CRITICAL")
    high_count = sum(1 for f in all_findings if f.severity == "HIGH")
    medium_count = sum(1 for f in all_findings if f.severity == "MEDIUM")
    low_count = sum(1 for f in all_findings if f.severity == "LOW")

    # Calculate Production Readiness Score (100 Base)
    penalty = (critical_count * 25) + (high_count * 15) + (medium_count * 8) + (low_count * 3)
    readiness_score = max(0, min(100, 100 - penalty))

    if readiness_score >= 90:
        grade = "A+"
        status = "READY FOR PRODUCTION"
    elif readiness_score >= 75:
        grade = "B"
        status = "NEEDS HARDENING BEFORE DEPLOYMENT"
    elif readiness_score >= 50:
        grade = "C"
        status = "HIGH RISK - MAJOR FLAWS DETECTED"
    else:
        grade = "F"
        status = "CRITICAL FAILURE - DO NOT DEPLOY"

    summary = (
        f"Audited {scanned_count} file(s) across {combined_metrics.total_lines} lines of code. "
        f"Found {len(all_findings)} issue(s): {critical_count} critical, {high_count} high, "
        f"{medium_count} medium, {low_count} low."
    )

    # Optional LLM contextual synthesis
    llm_recommendations = None
    is_offline = False

    try:
        client = LLMClient(model=model)
        findings_snippet = "\n".join(
            [f"- [{f.severity}] {f.title} ({f.rule_id}) at {f.file_path}:{f.line_number} -> {f.line_content}"
             for f in all_findings[:15]]
        )
        prompt = f"""Review the following code audit findings and provide a concise, expert architectural action plan to bring this codebase to 100/100 production readiness:

{summary}

Key Findings:
{findings_snippet or "No critical or high issues detected! Code passed static security & quality filters."}

Provide:
1. Root-cause assessment.
2. Immediate 3-step prioritized remediation patch.
3. Production hardening recommendations (Docker, Secrets management, Monitoring).
"""
        system_prompt = "You are a Principal Security Auditor and DevSecOps Architect at a top-tier tech firm."
        llm_recommendations = client.generate(prompt=prompt, system_prompt=system_prompt)

    except OfflineModeException:
        is_offline = True
        llm_recommendations = (
            "### ProdForge Heuristic Remediation Plan (Offline Mode)\n\n"
            "1. **Address Critical Secrets & SQL Injections First:** Remove hardcoded credentials, rotate compromised tokens immediately, and enforce parameterized queries.\n"
            "2. **Eliminate Blind Try/Catch:** Ensure all exceptions are logged with full stack traces rather than swallowed silently.\n"
            "3. **Add Input Validation:** Wrap all untrusted HTTP or user input with Pydantic or Zod schemas before processing."
        )

    return CodeAuditResult(
        target_path=target,
        is_directory=is_dir,
        total_files_scanned=scanned_count,
        readiness_score=readiness_score,
        readiness_grade=grade,
        readiness_status=status,
        summary=summary,
        metrics=combined_metrics,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        findings=all_findings,
        llm_recommendations=llm_recommendations,
        is_offline_fallback=is_offline
    )
