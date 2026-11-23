"""
ProdForge CLI - Interactive Autonomous Production Engineering Engine.
Provides commands for planning, deep code auditing, test generation,
autonomous auto-fixing, Kubernetes synthesis, CI/CD PR gates, and local Web Studio.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich import print as rprint

from prodforge.config import get_config
from prodforge.engines.planner import generate_architecture_plan
from prodforge.engines.auditor import audit_code_or_path
from prodforge.engines.qa_tester import generate_test_suite
from prodforge.engines.hardener import generate_production_hardening
from prodforge.engines.feasibility import analyze_feasibility
from prodforge.engines.sarif_exporter import save_sarif_file
from prodforge.engines.html_reporter import save_html_report
from prodforge.governance import create_default_governance_file
from prodforge.engines.fixer import auto_fix_target
from prodforge.engines.k8s_generator import generate_k8s_manifests
from prodforge.engines.ci_generator import generate_ci_workflows

app = typer.Typer(
    name="prodforge",
    help="⚡ ProdForge: Autonomous Production-Grade Software Engineering AI Agent & Studio",
    add_completion=False
)
console = Console()


@app.command(name="plan")
def cmd_plan(
    idea: str = typer.Argument(..., help="Product idea, software specification, or system requirements"),
    constraints: Optional[str] = typer.Option(None, "--constraints", "-c", help="Technical constraints or preferred stack"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Save markdown blueprint to specified file path"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override active LLM model")
):
    """Transform any product idea into production architecture, C4 diagrams, and execution roadmaps."""
    with console.status("[bold cyan]Synthesizing production architecture and threat models...", spinner="dots"):
        result = generate_architecture_plan(idea=idea, constraints=constraints, model=model)

    score_color = "green" if result.feasibility_score >= 80 else "yellow"
    console.print(
        Panel.fit(
            f"[bold white]{result.title}[/]\n"
            f"[dim]Idea:[/] {result.idea_summary}\n"
            f"[dim]Feasibility Score:[/] [{score_color} bold]{result.feasibility_score}/100[/] "
            f"({'Offline Heuristic Engine' if result.is_offline_fallback else 'LLM Autonomous Synthesizer'})",
            title="[bold cyan]PRODFORGE ARCHITECTURE SUITE[/]",
            border_style="cyan"
        )
    )

    console.print(Markdown(result.markdown_report))

    if out:
        out.write_text(result.markdown_report, encoding="utf-8")
        console.print(f"\n[bold green]✓ Architectural plan successfully saved to:[/] [white underline]{out}[/]")


@app.command(name="audit")
def cmd_audit(
    target: str = typer.Argument(..., help="Path to source file or project directory to audit"),
    sarif: Optional[Path] = typer.Option(None, "--sarif", "-s", help="Output OASIS SARIF v2.1.0 file for GitHub Code Scanning"),
    html: Optional[Path] = typer.Option(None, "--html", help="Export standalone executive HTML audit dashboard"),
    fail_under: Optional[int] = typer.Option(None, "--fail-under", help="Exit with code 1 if Production Readiness Index is below threshold"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Export audit report to markdown file"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override active LLM model")
):
    """Deeply audit code for OWASP security vulnerabilities, code smells, and production readiness."""
    with console.status(f"[bold yellow]Executing deep security and quality audit on '{target}'...", spinner="dots"):
        try:
            result = audit_code_or_path(target=target, model=model, fail_under=fail_under)
        except Exception as exc:
            console.print(f"[bold red]Audit error:[/] {exc}")
            raise typer.Exit(code=1)

    # Score coloring
    if result.readiness_score >= 90:
        score_badge = f"[bold green on black] {result.readiness_score}/100 - {result.readiness_status} ({result.readiness_grade}) [/]"
    elif result.readiness_score >= 75:
        score_badge = f"[bold yellow on black] {result.readiness_score}/100 - {result.readiness_status} ({result.readiness_grade}) [/]"
    elif result.readiness_score >= 50:
        score_badge = f"[bold red on black] {result.readiness_score}/100 - {result.readiness_status} ({result.readiness_grade}) [/]"
    else:
        score_badge = f"[bold white on red] {result.readiness_score}/100 - {result.readiness_status} ({result.readiness_grade}) [/]"

    # Metric Table
    metrics_table = Table(title="Codebase Telemetry & Structural Metrics", border_style="dim")
    metrics_table.add_column("Scanned Files", style="cyan", justify="center")
    metrics_table.add_column("Total Lines", style="white", justify="center")
    metrics_table.add_column("Code Lines", style="white", justify="center")
    metrics_table.add_column("Functions", style="blue", justify="center")
    metrics_table.add_column("Max Nesting", style="magenta", justify="center")
    metrics_table.add_column("Cyclomatic Est.", style="yellow", justify="center")

    metrics_table.add_row(
        str(result.total_files_scanned),
        f"{result.metrics.total_lines:,}",
        f"{result.metrics.code_lines:,}",
        str(result.metrics.functions_count),
        f"{result.metrics.max_nesting_depth} lvl",
        str(result.metrics.cyclomatic_estimate)
    )

    console.print("\n", metrics_table)

    # 5-Pillar Scorecard Table
    pillars_table = Table(title="Enterprise 5-Pillar Production Readiness Index (PRI)", border_style="cyan")
    pillars_table.add_column("Pillar", style="bold white")
    pillars_table.add_column("Weight", style="dim", justify="center")
    pillars_table.add_column("Score", style="bold", justify="center")
    pillars_table.add_column("Status", style="white")

    p = result.pillars
    pillars_table.add_row("1. Security & Vulnerability Shield", "35%", f"{p.security_score}/100", "[green]VERIFIED[/]" if p.security_score >= 80 else "[red]RISKS DETECTED[/]")
    pillars_table.add_row("2. Code Quality & Technical Debt", "20%", f"{p.quality_score}/100", "[green]CLEAN[/]" if p.quality_score >= 80 else "[yellow]ATTENTION NEEDED[/]")
    pillars_table.add_row("3. Architecture & Concurrency", "15%", f"{p.architecture_score}/100", "[green]STABLE[/]" if p.architecture_score >= 80 else "[yellow]HIGH COMPLEXITY[/]")
    pillars_table.add_row("4. QA Automation & Testability", "15%", f"{p.test_readiness_score}/100", "[green]TESTS VERIFIED[/]" if p.test_readiness_score >= 80 else "[yellow]COVERAGE GAP[/]")
    pillars_table.add_row("5. DevOps & Container Hardening", "15%", f"{p.devops_hardening_score}/100", "[green]HARDENED[/]" if p.devops_hardening_score >= 80 else "[yellow]MISSING CI/CD[/]")

    console.print(pillars_table)

    # Compliance Badges Table
    comp = result.compliance
    comp_table = Table(title="Enterprise Governance & Compliance Standards", border_style="dim")
    comp_table.add_column("Standard / Gate", style="bold white")
    comp_table.add_column("Status", justify="center")

    comp_table.add_row("Zero Hardcoded Secrets (CWE-798)", "[bold green]PASS[/]" if comp.zero_hardcoded_secrets else "[bold red]FAIL (Secrets in repo)[/]")
    comp_table.add_row("OWASP Top 10 Clean", "[bold green]PASS[/]" if comp.owasp_top_10_clean else "[bold red]FAIL (Vulnerabilities found)[/]")
    comp_table.add_row("Input Sanitization Shield", "[bold green]PASS[/]" if comp.input_sanitization_shield else "[bold red]FAIL[/]")
    comp_table.add_row("Non-Root Container Certified", "[bold green]PASS[/]" if comp.non_root_container_certified else "[bold red]FAIL[/]")
    comp_table.add_row("CI/CD Governance Gate Ready", "[bold green]PASS[/]" if comp.ci_cd_gate_ready else "[bold yellow]NEEDS WORKFLOW[/]")

    console.print(comp_table)

    # Findings Table
    findings_table = Table(title=f"Discovered Findings ({len(result.findings)} total)", border_style="cyan")
    findings_table.add_column("Severity", style="bold", width=12)
    findings_table.add_column("Rule ID", style="dim", width=12)
    findings_table.add_column("Location", style="white", width=22)
    findings_table.add_column("Description", style="white")
    findings_table.add_column("Remediation", style="green")

    for f in result.findings[:25]:
        sev_style = {
            "CRITICAL": "[bold white on red] CRITICAL [/]",
            "HIGH": "[bold red] HIGH [/]",
            "MEDIUM": "[bold yellow] MEDIUM [/]",
            "LOW": "[bold cyan] LOW [/]"
        }.get(f.severity, f.severity)

        loc = f"{Path(f.file_path).name}:{f.line_number}"
        findings_table.add_row(sev_style, f.rule_id, loc, f.title, f.remediation)

    console.print(findings_table)

    # Overview panel
    gate_msg = ""
    if fail_under is not None:
        if result.gate_passed:
            gate_msg = f"\n[bold green]✓ Passed CI/CD Quality Gate (Score {result.readiness_score} >= {fail_under})[/]"
        else:
            gate_msg = f"\n[bold red]✗ FAILED CI/CD Quality Gate (Score {result.readiness_score} < threshold {fail_under})[/]"

    console.print(
        Panel(
            f"[bold]Readiness Verdict:[/]\n{score_badge}{gate_msg}\n\n"
            f"[dim]Telemetry:[/] {result.summary}\n"
            f"[dim]Tally:[/] [red bold]{result.critical_count} Critical[/], [red]{result.high_count} High[/], "
            f"[yellow]{result.medium_count} Medium[/], [cyan]{result.low_count} Low[/]",
            title="[bold cyan]PRODFORGE READINESS SCORECARD[/]",
            border_style="cyan"
        )
    )

    if result.llm_recommendations:
        console.print("\n[bold cyan]─── Enterprise Hardening Recommendations ───[/]")
        console.print(Markdown(result.llm_recommendations))

    # Export SARIF if requested
    if sarif:
        save_sarif_file(result, sarif)
        console.print(f"\n[bold green]✓ OASIS SARIF v2.1.0 report saved to:[/] [white underline]{sarif}[/]")

    # Export Executive HTML dashboard if requested
    if html:
        save_html_report(result, target, html)
        console.print(f"\n[bold green]✓ Standalone executive HTML report saved to:[/] [white underline]{html}[/]")

    if out:
        report_md = f"""# ProdForge Code Audit Report: {target}

- **Production Readiness Index:** {result.readiness_score}/100 ({result.readiness_grade})
- **Status:** {result.readiness_status}
- **Scanned Files:** {result.total_files_scanned} ({result.metrics.total_lines:,} lines)
- **Critical Issues:** {result.critical_count}
- **High Issues:** {result.high_count}
- **Medium Issues:** {result.medium_count}
- **Low Issues:** {result.low_count}

## 5-Pillar Scorecard
- **Security Shield (35%):** {result.pillars.security_score}/100
- **Code Quality & Debt (20%):** {result.pillars.quality_score}/100
- **Architecture & Resilience (15%):** {result.pillars.architecture_score}/100
- **QA & Testability (15%):** {result.pillars.test_readiness_score}/100
- **DevOps & Containers (15%):** {result.pillars.devops_hardening_score}/100

## Discovered Findings
| Severity | Rule ID | Location | Title | Remediation |
|---|---|---|---|---|
""" + "\n".join([f"| {f.severity} | {f.rule_id} | `{Path(f.file_path).name}:{f.line_number}` | {f.title} | {f.remediation} |" for f in result.findings])

        if result.llm_recommendations:
            report_md += f"\n\n## Recommendations\n{result.llm_recommendations}"

        out.write_text(report_md, encoding="utf-8")
        console.print(f"\n[bold green]✓ Full report saved to:[/] [white underline]{out}[/]")

    if not result.gate_passed:
        console.print(f"\n[bold red]Pipeline failed: Production Readiness Gate was NOT met (Score: {result.readiness_score}, Gate Passed: False).[/]")
        raise typer.Exit(code=1)


@app.command(name="fix")
def cmd_fix(
    target: str = typer.Argument(..., help="Path to file or directory to autonomously repair"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Directly write code repairs in-place to files"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Write unified patch diff to specified file")
):
    """Autonomously remediate code vulnerabilities, extract secrets to .env, and fix error handling."""
    with console.status(f"[bold green]Generating autonomous code repairs for '{target}'...", spinner="dots"):
        try:
            result = auto_fix_target(target=target, apply=apply)
        except Exception as exc:
            console.print(f"[bold red]Auto-fix error:[/] {exc}")
            raise typer.Exit(code=1)

    console.print(
        Panel.fit(
            f"[bold white]Autonomous Code Remediation Complete[/]\n"
            f"[dim]Target:[/] {result.target_path}\n"
            f"[dim]Repairs Generated:[/] [green bold]{result.total_fixes_generated}[/]\n"
            f"[dim]Applied to Disk:[/] [{'bold green]YES' if result.applied else 'bold yellow]NO (Preview Mode - pass --apply to write)'}[/]",
            title="[bold green]PRODFORGE SELF-HEALING ENGINE[/]",
            border_style="green"
        )
    )

    if result.actions:
        actions_table = Table(title="Generated Code Repairs", border_style="dim")
        actions_table.add_column("File:Line", style="cyan")
        actions_table.add_column("Rule ID", style="dim")
        actions_table.add_column("Repair Action", style="white")

        for act in result.actions:
            actions_table.add_row(f"{Path(act.file_path).name}:{act.line_number}", act.rule_id, act.explanation)
        console.print(actions_table)

    if result.unified_patch:
        console.print("\n[bold cyan]─── Unified Git Patch Diff ───[/]")
        console.print(Syntax(result.unified_patch, "diff", theme="monokai"))

    if out and result.unified_patch:
        out.write_text(result.unified_patch, encoding="utf-8")
        console.print(f"\n[bold green]✓ Unified patch saved to:[/] [white underline]{out}[/]")

    if result.env_updates:
        console.print("\n[bold yellow]Secrets safely extracted for .env:[/]")
        for k in result.env_updates:
            console.print(f"  [green]✓[/] {k}=[dim]****[/]")


@app.command(name="k8s")
def cmd_k8s(
    app_name: str = typer.Option("prodforge-app", "--app", help="Application name for Kubernetes manifests"),
    namespace: str = typer.Option("production", "--namespace", "-n", help="Kubernetes namespace"),
    domain: str = typer.Option("api.example.com", "--domain", "-d", help="Domain for TLS Ingress"),
    image: str = typer.Option("ghcr.io/org/app:v1.0.0", "--image", "-i", help="Container image tag"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="Directory to write Kubernetes manifest files")
):
    """Generate enterprise-grade Kubernetes manifests with Pod Security Restricted standards."""
    with console.status("[bold cyan]Synthesizing Kubernetes manifests (Deployment, HPA, NetworkPolicy, Ingress)...", spinner="dots"):
        result = generate_k8s_manifests(
            app_name=app_name,
            namespace=namespace,
            domain=domain,
            container_image=image,
            output_dir=out
        )

    console.print(
        Panel.fit(
            f"[bold white]Enterprise Kubernetes Manifest Suite Generated[/]\n"
            f"[dim]App Name:[/] [cyan bold]{result.app_name}[/]\n"
            f"[dim]Namespace:[/] [white]{result.namespace}[/]\n"
            f"[dim]Artifacts:[/] {len(result.artifacts)} (Deployment, Service, HPA, NetPol, Ingress)\n"
            f"[dim]Written to Disk:[/] [{'bold green]YES: ' + str(out) if result.applied else 'bold yellow]NO (Preview Mode - pass --out <dir> to write)'}[/]",
            title="[bold cyan]PRODFORGE KUBERNETES SUITE[/]",
            border_style="cyan"
        )
    )

    for art in result.artifacts:
        console.print(f"\n[bold cyan]► {art.filename}[/] [dim]({art.description})[/]")
        console.print(Syntax(art.content, "yaml", theme="monokai", line_numbers=True))


@app.command(name="ci")
def cmd_ci(
    min_score: int = typer.Option(85, "--min-score", "-m", help="Minimum Production Readiness Score required to pass PR gate"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Directly write workflow files into repository"),
    project_dir: str = typer.Option(".", "--project-dir", "-p", help="Target project root directory")
):
    """Generate enterprise GitHub Actions PR gate and GitLab CI SAST workflows."""
    with console.status("[bold green]Generating CI/CD governance and Pull Request gates...", spinner="dots"):
        result = generate_ci_workflows(
            min_score=min_score,
            project_dir=Path(project_dir),
            apply=apply
        )

    console.print(
        Panel.fit(
            f"[bold white]Enterprise CI/CD Governance Gate Generated[/]\n"
            f"[dim]Min Score Threshold:[/] [green bold]{result.min_readiness_score}/100[/]\n"
            f"[dim]Workflows:[/] GitHub Actions + GitLab CI\n"
            f"[dim]Applied to Disk:[/] [{'bold green]YES' if result.applied else 'bold yellow]NO (Preview Mode - pass --apply to write)'}[/]",
            title="[bold green]PRODFORGE CI/CD GOVERNANCE[/]",
            border_style="green"
        )
    )

    for art in result.artifacts:
        console.print(f"\n[bold cyan]► {art.target_rel_path}[/] [dim]({art.description})[/]")
        console.print(Syntax(art.content, "yaml", theme="monokai", line_numbers=True))


@app.command(name="test")
def cmd_test(
    target: str = typer.Argument(..., help="Path to source file to generate test suite for"),
    framework: Optional[str] = typer.Option(None, "--framework", "-f", help="Test framework (pytest | vitest | jest)"),
    out: Optional[Path] = typer.Option(None, "--out", "-o", help="File path to write generated test suite"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override active LLM model")
):
    """Autonomously generate comprehensive, production-grade test suites with fixtures & edge cases."""
    with console.status(f"[bold green]Generating test suite for '{target}'...", spinner="dots"):
        try:
            result = generate_test_suite(target_path=target, framework=framework, model=model)
        except Exception as exc:
            console.print(f"[bold red]Test generation error:[/] {exc}")
            raise typer.Exit(code=1)

    console.print(
        Panel.fit(
            f"[bold white]Autonomous Test Suite Generated[/]\n"
            f"[dim]Target:[/] {result.target_path}\n"
            f"[dim]Framework:[/] [cyan bold]{result.framework}[/]\n"
            f"[dim]Inferred Callables:[/] {', '.join(result.inferred_functions) or 'General module exports'}\n"
            f"[dim]Estimated Tests:[/] [green bold]{result.test_count_estimate}[/]",
            title="[bold green]PRODFORGE QA AUTOMATION ENGINE[/]",
            border_style="green"
        )
    )

    lexer = "python" if result.framework == "pytest" else "typescript"
    console.print(Syntax(result.test_code, lexer, theme="monokai", line_numbers=True))

    if out:
        out.write_text(result.test_code, encoding="utf-8")
        console.print(f"\n[bold green]✓ Test suite written to:[/] [white underline]{out}[/]")


@app.command(name="harden")
def cmd_harden(
    project_path: str = typer.Argument(".", help="Root directory of the project to harden"),
    apply: bool = typer.Option(False, "--apply", "-a", help="Directly write Dockerfile, CI/CD, and healthcheck files"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override active LLM model")
):
    """Transform code into production-grade containerized system with CI/CD and health checks."""
    with console.status(f"[bold cyan]Hardening project at '{project_path}'...", spinner="dots"):
        result = generate_production_hardening(project_path=project_path, apply=apply, model=model)

    console.print(
        Panel.fit(
            f"[bold white]Production Hardening Suite Generated[/]\n"
            f"[dim]Detected Stack:[/] [cyan bold]{result.detected_stack.upper()}[/]\n"
            f"[dim]Artifacts Generated:[/] {len(result.artifacts)}\n"
            f"[dim]Applied to Disk:[/] [{'bold green]YES' if result.applied else 'bold yellow]NO (Preview Mode - pass --apply to write)'}[/]",
            title="[bold cyan]PRODFORGE PRODUCTION HARDENING[/]",
            border_style="cyan"
        )
    )

    for art in result.artifacts:
        console.print(f"\n[bold cyan]► {art.filename}[/] [dim]({art.description})[/]")
        lexer = "dockerfile" if "Dockerfile" in art.filename else ("yaml" if "yml" in art.filename else "python")
        console.print(Syntax(art.content, lexer, theme="monokai", line_numbers=True))

    if result.action_log:
        console.print("\n[bold green]Successfully applied the following files to disk:[/]")
        for action in result.action_log:
            console.print(f"  [green]✓[/] {action}")


@app.command(name="feasibility")
def cmd_feasibility(
    idea: str = typer.Argument(..., help="System concept or architecture description to analyze"),
    dau: int = typer.Option(50000, "--dau", "-d", help="Target daily active user volume"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Override active LLM model")
):
    """Analyze architectural feasibility, latency, peak RPS thresholds, and itemized FinOps cloud costs."""
    with console.status("[bold magenta]Calculating FinOps cost models and concurrency limits...", spinner="dots"):
        result = analyze_feasibility(idea=idea, target_dau=dau, model=model)

    console.print(
        Panel.fit(
            f"[bold white]FinOps & Scaling Feasibility Analysis[/]\n"
            f"[dim]Target Users:[/] [cyan bold]{dau:,} DAU[/]\n"
            f"[dim]Estimated Peak RPS:[/] [green bold]{result.concurrency_target_rps} req/sec[/]\n"
            f"[dim]Estimated Cloud Run-rate:[/] [yellow bold]${result.estimated_monthly_cost_usd:.2f} USD/mo[/]\n"
            f"[dim]Verdict:[/] [bold green]{result.scalability_verdict}[/]",
            title="[bold magenta]PRODFORGE FINOPS & CAPACITY ENGINE[/]",
            border_style="magenta"
        )
    )

    cost_table = Table(title="Itemized Monthly Cloud Infrastructure Estimate", border_style="magenta")
    cost_table.add_column("Component", style="white bold")
    cost_table.add_column("Recommended Service", style="cyan")
    cost_table.add_column("Monthly USD", style="green", justify="right")
    cost_table.add_column("Architecture Notes", style="dim")

    for item in result.cost_breakdown:
        cost_table.add_row(item.component, item.recommended_service, f"${item.monthly_estimate_usd:.2f}", item.notes)

    console.print(cost_table)
    console.print(Markdown(result.executive_markdown))


@app.command(name="studio")
def cmd_studio(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host interface to bind"),
    port: int = typer.Option(8000, "--port", "-p", help="Port number for Studio web server"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not automatically launch web browser")
):
    """Launch the local ProdForge Interactive Web Studio dashboard."""
    import uvicorn
    import webbrowser
    import threading

    url = f"http://{host}:{port}"
    console.print(
        Panel.fit(
            f"[bold green]⚡ ProdForge Studio Launching on [underline]{url}[/][/]\n"
            f"[dim]Features:[/] Real-time Architecture Planner, Deep Code Auditor, QA Test Generator, Production Hardening\n"
            f"[dim]Press Ctrl+C to terminate server.[/]",
            title="[bold cyan]PRODFORGE INTERACTIVE STUDIO[/]",
            border_style="cyan"
        )
    )

    if not no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    from prodforge.studio.server import app as studio_app
    uvicorn.run(studio_app, host=host, port=port, log_level="info")


@app.command(name="share")
def cmd_share(
    port: int = typer.Option(8000, "--port", "-p", help="Studio port to expose"),
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host interface")
):
    """Launch Web Studio and expose it publicly over the internet via Cloudflare Tunnel."""
    import uvicorn
    import threading
    import subprocess
    import shutil
    import re
    import time
    import webbrowser

    from prodforge.studio.server import app as studio_app
    server_thread = threading.Thread(
        target=lambda: uvicorn.run(studio_app, host=host, port=port, log_level="warning"),
        daemon=True
    )
    server_thread.start()
    time.sleep(1.2)

    cloudflared_bin = shutil.which("cloudflared") or r"C:\Program Files (x86)\cloudflared\cloudflared.exe"
    if not os.path.exists(cloudflared_bin) and not shutil.which("cloudflared"):
        console.print("[bold red]Cloudflared binary not found.[/] Install cloudflared or ngrok to enable instant public sharing.")
        return

    console.print(f"[bold cyan]⚡ Initializing Cloudflare Tunnel to port {port}...[/]")
    proc = subprocess.Popen(
        [cloudflared_bin, "tunnel", "--url", f"http://{host}:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    public_url = None
    for line in iter(proc.stderr.readline, ""):
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        console.print(
            Panel.fit(
                f"[bold green]🚀 ProdForge Studio is LIVE Publicly on the Internet![/]\n\n"
                f"[dim]Public HTTPS URL:[/] [bold underline cyan]{public_url}[/]\n"
                f"[dim]Localhost URL:[/] [underline white]http://{host}:{port}[/]\n\n"
                f"[yellow]Share this link with anyone! It is accessible from mobile, tablet, or any laptop.[/]\n"
                f"[dim]Press Ctrl+C to terminate the public tunnel.[/]",
                title="[bold green]PRODFORGE PUBLIC CLOUDFLARE TUNNEL[/]",
                border_style="green"
            )
        )
        webbrowser.open(public_url)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            proc.terminate()
            console.print("\n[bold yellow]Public tunnel terminated.[/]")
    else:
        console.print("[bold red]Failed to acquire public Cloudflare URL.[/]")


@app.command(name="config")
def cmd_config():
    """Inspect detected API keys, active model, and Ollama connectivity."""
    cfg = get_config()

    table = Table(title="ProdForge Environment & Provider Configuration", border_style="cyan")
    table.add_column("Provider / Setting", style="bold white")
    table.add_column("Status / Configured Value", style="cyan")
    table.add_column("Default Model", style="green")

    table.add_row("Gemini API", "[green]Configured[/]" if cfg.gemini_api_key else "[dim]Not Set[/]", "gemini-2.5-flash")
    table.add_row("OpenAI API", "[green]Configured[/]" if cfg.openai_api_key else "[dim]Not Set[/]", "gpt-4o-mini")
    table.add_row("Anthropic API", "[green]Configured[/]" if cfg.anthropic_api_key else "[dim]Not Set[/]", "claude-3-5-sonnet-20241022")
    table.add_row("Groq API", "[green]Configured[/]" if cfg.groq_api_key else "[dim]Not Set[/]", "llama-3.3-70b-versatile")
    table.add_row("OpenRouter API", "[green]Configured[/]" if cfg.openrouter_api_key else "[dim]Not Set[/]", "meta-llama/llama-3.3-70b-instruct")
    table.add_row("Ollama Host", f"[white]{cfg.ollama_host}[/]", "llama3")
    table.add_row("Active Provider", f"[bold green]{cfg.detected_provider.upper()}[/]", f"[bold yellow]{cfg.active_model}[/]")

    console.print(table)
    if cfg.detected_provider == "offline":
        console.print(
            "\n[dim yellow]Tip: No cloud API keys found. ProdForge will operate in [bold]Offline Heuristic Mode[/] "
            "with zero network requirements. To enable LLM dynamic synthesis, set GEMINI_API_KEY, OPENAI_API_KEY, or GROQ_API_KEY in .env.[/]"
        )


@app.command(name="init")
def cmd_init(
    target: Path = typer.Option(Path("."), "--target", "-t", help="Directory to initialize ProdForge enterprise governance in"),
    ci: bool = typer.Option(True, "--ci/--no-ci", help="Generate GitHub Actions PR gate workflow"),
    hooks: bool = typer.Option(True, "--hooks/--no-hooks", help="Install local Git pre-commit security hook")
):
    """Initialize enterprise governance policy, CI/CD PR gate, and pre-commit hooks in any repository."""
    target_dir = target.resolve()
    console.print(f"[bold cyan]Initializing ProdForge Enterprise Suite in:[/] [white underline]{target_dir}[/]")

    created_artifacts = []

    # 1. Create .prodforge.yaml policy
    policy_file = target_dir / ".prodforge.yaml"
    if not policy_file.exists():
        create_default_governance_file(target_dir)
        created_artifacts.append((".prodforge.yaml", "Enterprise Quality Gate & Rule Policy (threshold: 80)"))
    else:
        created_artifacts.append((".prodforge.yaml", "Existing policy preserved"))

    # 2. Create .github/workflows/prodforge-gate.yml
    if ci:
        ci_dir = target_dir / ".github" / "workflows"
        ci_dir.mkdir(parents=True, exist_ok=True)
        gate_file = ci_dir / "prodforge-gate.yml"
        workflows = generate_ci_workflows(min_score=80)
        gate_file.write_text(workflows.github_actions_workflow, encoding="utf-8")
        created_artifacts.append((".github/workflows/prodforge-gate.yml", "GitHub Actions Automated PR Quality Gate"))

    # 3. Create .pre-commit-config.yaml and Git hook
    if hooks:
        pre_commit_cfg = target_dir / ".pre-commit-config.yaml"
        if not pre_commit_cfg.exists():
            pre_commit_cfg.write_text(
"""repos:
  - repo: local
    hooks:
      - id: prodforge-audit
        name: ProdForge Production Gate
        entry: prodforge audit . --fail-under 80
        language: system
        pass_filenames: false
""",
                encoding="utf-8"
            )
            created_artifacts.append((".pre-commit-config.yaml", "Pre-commit framework integration"))

        git_hooks_dir = target_dir / ".git" / "hooks"
        if git_hooks_dir.is_dir():
            hook_file = git_hooks_dir / "pre-commit"
            hook_script = """#!/bin/sh
# ProdForge Autonomous Pre-Commit Security Gate
echo "⚡ Running ProdForge Pre-Commit Security Scan..."
python -m prodforge audit . --fail-under 80
if [ $? -ne 0 ]; then
    echo "❌ ProdForge Quality Gate Failed. Aborting commit."
    exit 1
fi
"""
            hook_file.write_text(hook_script, encoding="utf-8")
            created_artifacts.append((".git/hooks/pre-commit", "Direct Git pre-commit enforcement hook"))

    # 4. Create .env.example if missing
    env_example = target_dir / ".env.example"
    if not env_example.exists():
        env_example.write_text(
"""# ProdForge Enterprise Provider Keys (Optional - runs 100% offline without keys)
GEMINI_API_KEY=
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
""",
            encoding="utf-8"
        )
        created_artifacts.append((".env.example", "Environment secrets template"))

    # Summary table
    table = Table(title="ProdForge Enterprise Initialization Summary", border_style="green")
    table.add_column("Asset / Config", style="bold white")
    table.add_column("Status / Purpose", style="green")
    for asset, desc in created_artifacts:
        table.add_row(asset, desc)

    console.print(table)
    console.print(
        Panel.fit(
            "[bold green]✓ Repository is now 100% production-governed![/]\n"
            "[dim]• CI/CD will block PRs if score drops below 80 or critical secrets are committed.\n"
            "• Run [bold cyan]prodforge audit .[/] anytime to verify production readiness.\n"
            "• Run [bold cyan]prodforge fix .[/] to auto-repair any discovered issues.[/]",
            title="[bold green]ENTERPRISE READY[/]",
            border_style="green"
        )
    )


if __name__ == "__main__":
    app()
