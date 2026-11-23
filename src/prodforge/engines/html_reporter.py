"""
ProdForge Standalone Executive HTML Audit Report Generator.
Produces self-contained, high-impact HTML audit dashboards with SVG gauges,
5-pillar telemetry, CWE/OWASP vulnerability details, and compliance matrices.
"""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from prodforge.engines.auditor import AuditReport


def generate_html_audit_report(report: AuditReport, target_name: str) -> str:
    """Generate self-contained HTML executive audit report."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    score = report.readiness_score
    grade = report.readiness_grade
    status = report.readiness_status

    # Theme colors based on score
    if score >= 85:
        accent_color = "#10b981"  # Emerald
        accent_bg = "rgba(16, 185, 129, 0.1)"
    elif score >= 70:
        accent_color = "#f59e0b"  # Amber
        accent_bg = "rgba(245, 158, 11, 0.1)"
    else:
        accent_color = "#ef4444"  # Rose
        accent_bg = "rgba(239, 68, 68, 0.1)"

    # SVG circular progress gauge calculations
    radius = 54
    circumference = 2 * 3.14159 * radius
    stroke_offset = circumference - (score / 100) * circumference

    p = report.pillars
    comp = report.compliance

    # Findings rows
    findings_rows = []
    for f in report.findings:
        sev = f.severity.upper()
        if sev == "CRITICAL":
            badge_class = "sev-critical"
        elif sev == "HIGH":
            badge_class = "sev-high"
        elif sev == "MEDIUM":
            badge_class = "sev-medium"
        else:
            badge_class = "sev-low"

        file_disp = Path(f.file_path).name if f.file_path else "target"
        findings_rows.append(f"""
        <tr>
            <td><span class="badge {badge_class}">{html.escape(sev)}</span></td>
            <td><code>{html.escape(f.rule_id)}</code></td>
            <td><code>{html.escape(f.cwe_id or "CWE-General")}</code></td>
            <td><strong>{html.escape(file_disp)}:{f.line_number}</strong></td>
            <td>
                <div class="finding-title">{html.escape(f.title)}</div>
                <div class="finding-desc">{html.escape(f.description)}</div>
                <div class="finding-remediation"><strong>Fix:</strong> {html.escape(f.remediation)}</div>
            </td>
        </tr>
        """)

    findings_html = "".join(findings_rows) if findings_rows else "<tr><td colspan='5' class='text-center py-4'>No vulnerabilities detected. All security checks passed!</td></tr>"

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProdForge Audit: {html.escape(target_name)}</title>
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-hover: #1f2937;
            --border: #1f293d;
            --text-main: #f9fafb;
            --text-muted: #9ca3af;
            --accent: {accent_color};
            --accent-bg: {accent_bg};
            --red: #ef4444;
            --green: #10b981;
            --yellow: #f59e0b;
            --blue: #3b82f6;
            --purple: #8b5cf6;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            padding: 32px 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 24px;
            margin-bottom: 32px;
            flex-wrap: wrap;
            gap: 16px;
        }}
        .brand {{ display: flex; align-items: center; gap: 12px; }}
        .brand h1 {{ font-size: 24px; font-weight: 800; letter-spacing: -0.5px; }}
        .brand span {{ background: var(--accent); color: #000; font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 4px; }}
        .meta-info {{ text-align: right; font-size: 13px; color: var(--text-muted); }}
        
        .grid-hero {{
            display: grid;
            grid-template-columns: 340px 1fr;
            gap: 24px;
            margin-bottom: 32px;
        }}
        @media (max-width: 860px) {{
            .grid-hero {{ grid-template-columns: 1fr; }}
            .meta-info {{ text-align: left; }}
        }}
        .card {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
        }}
        .score-card {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }}
        .gauge-svg {{ width: 140px; height: 140px; transform: rotate(-90deg); }}
        .gauge-bg {{ fill: none; stroke: #1f293d; stroke-width: 10; }}
        .gauge-fill {{
            fill: none;
            stroke: var(--accent);
            stroke-width: 10;
            stroke-dasharray: {circumference};
            stroke-dashoffset: {stroke_offset};
            stroke-linecap: round;
            transition: stroke-dashoffset 1s ease;
        }}
        .gauge-text {{
            font-size: 26px;
            font-weight: 800;
            fill: var(--text-main);
            transform: rotate(90deg);
            transform-origin: center;
        }}
        .grade-badge {{
            font-size: 14px;
            font-weight: 700;
            color: var(--accent);
            margin-top: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .score-status {{ font-size: 13px; color: var(--text-muted); margin-top: 4px; }}
        
        .pillars-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .pillar-box {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .pillar-title {{ font-size: 12px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; }}
        .pillar-score {{ font-size: 22px; font-weight: 800; color: var(--text-main); }}
        .pillar-bar {{ height: 4px; background: #1f293d; border-radius: 2px; margin-top: 8px; overflow: hidden; }}
        .pillar-bar-fill {{ height: 100%; border-radius: 2px; }}
        
        .stats-row {{ display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 32px; }}
        .stat-item {{
            flex: 1;
            min-width: 140px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
        }}
        .stat-val {{ font-size: 20px; font-weight: 800; }}
        .stat-lbl {{ font-size: 12px; color: var(--text-muted); margin-top: 2px; }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }}
        th, td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border);
            vertical-align: top;
        }}
        th {{
            background: rgba(255, 255, 255, 0.02);
            color: var(--text-muted);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }}
        tr:hover td {{ background: var(--surface-hover); }}
        code {{
            background: rgba(255, 255, 255, 0.05);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 12px;
        }}
        .badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 4px;
            text-align: center;
        }}
        .sev-critical {{ background: #7f1d1d; color: #fecaca; }}
        .sev-high {{ background: #991b1b; color: #fee2e2; }}
        .sev-medium {{ background: #78350f; color: #fef3c7; }}
        .sev-low {{ background: #1e3a8a; color: #dbeafe; }}
        .badge-pass {{ background: #064e3b; color: #a7f3d0; }}
        .badge-fail {{ background: #7f1d1d; color: #fecaca; }}
        
        .finding-title {{ font-weight: 700; color: #fff; margin-bottom: 2px; }}
        .finding-desc {{ color: var(--text-muted); margin-bottom: 6px; }}
        .finding-remediation {{
            background: rgba(16, 185, 129, 0.08);
            border-left: 2px solid var(--green);
            padding: 6px 10px;
            border-radius: 0 4px 4px 0;
            color: #d1fae5;
            font-size: 12px;
        }}
        
        .compliance-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-top: 16px;
        }}
        .comp-card {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 16px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .comp-name {{ font-size: 13px; font-weight: 600; }}
        
        footer {{
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid var(--border);
            text-align: center;
            font-size: 12px;
            color: var(--text-muted);
        }}
        @media print {{
            body {{ background: #fff; color: #000; padding: 0; }}
            .card {{ border: 1px solid #ccc; background: #fff; color: #000; }}
            :root {{ --text-main: #000; --text-muted: #555; --surface: #fff; --border: #ddd; }}
            .badge {{ border: 1px solid #000; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>PRODFORGE</h1>
                <span>ENTERPRISE AUDIT</span>
            </div>
            <div class="meta-info">
                <div><strong>Target:</strong> {html.escape(target_name)}</div>
                <div><strong>Audited:</strong> {now_str}</div>
            </div>
        </header>

        <!-- Hero Section: Score & Pillars -->
        <div class="grid-hero">
            <div class="card score-card">
                <svg class="gauge-svg" viewBox="0 0 120 120">
                    <circle class="gauge-bg" cx="60" cy="60" r="{radius}"></circle>
                    <circle class="gauge-fill" cx="60" cy="60" r="{radius}"></circle>
                    <text class="gauge-text" x="60" y="68" text-anchor="middle">{score}</text>
                </svg>
                <div class="grade-badge">Grade {html.escape(grade)} — {html.escape(status)}</div>
                <div class="score-status">Production Readiness Index (PRI)</div>
            </div>

            <div class="card">
                <h3 style="font-size: 15px; margin-bottom: 16px; text-transform: uppercase; letter-spacing: 0.5px;">5-Pillar Readiness Scorecard</h3>
                <div class="pillars-grid">
                    <div class="pillar-box">
                        <div class="pillar-title">1. Security Shield (35%)</div>
                        <div class="pillar-score">{p.security_score}/100</div>
                        <div class="pillar-bar"><div class="pillar-bar-fill" style="width: {p.security_score}%; background: {'var(--green)' if p.security_score >= 80 else 'var(--red)'};"></div></div>
                    </div>
                    <div class="pillar-box">
                        <div class="pillar-title">2. Code Quality (20%)</div>
                        <div class="pillar-score">{p.quality_score}/100</div>
                        <div class="pillar-bar"><div class="pillar-bar-fill" style="width: {p.quality_score}%; background: {'var(--green)' if p.quality_score >= 80 else 'var(--yellow)'};"></div></div>
                    </div>
                    <div class="pillar-box">
                        <div class="pillar-title">3. Architecture (15%)</div>
                        <div class="pillar-score">{p.architecture_score}/100</div>
                        <div class="pillar-bar"><div class="pillar-bar-fill" style="width: {p.architecture_score}%; background: {'var(--green)' if p.architecture_score >= 80 else 'var(--yellow)'};"></div></div>
                    </div>
                    <div class="pillar-box">
                        <div class="pillar-title">4. QA Automation (15%)</div>
                        <div class="pillar-score">{p.test_readiness_score}/100</div>
                        <div class="pillar-bar"><div class="pillar-bar-fill" style="width: {p.test_readiness_score}%; background: {'var(--green)' if p.test_readiness_score >= 80 else 'var(--yellow)'};"></div></div>
                    </div>
                    <div class="pillar-box">
                        <div class="pillar-title">5. DevOps & K8s (15%)</div>
                        <div class="pillar-score">{p.devops_hardening_score}/100</div>
                        <div class="pillar-bar"><div class="pillar-bar-fill" style="width: {p.devops_hardening_score}%; background: {'var(--green)' if p.devops_hardening_score >= 80 else 'var(--yellow)'};"></div></div>
                    </div>
                </div>
                <p style="font-size: 13px; color: var(--text-muted);">{html.escape(report.summary)}</p>
            </div>
        </div>

        <!-- Telemetry Stats -->
        <div class="stats-row">
            <div class="stat-item">
                <div class="stat-val">{report.total_files_scanned}</div>
                <div class="stat-lbl">Files Scanned</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">{report.metrics.total_lines:,}</div>
                <div class="stat-lbl">Total Lines</div>
            </div>
            <div class="stat-item">
                <div class="stat-val" style="color: {'var(--red)' if report.critical_count > 0 else 'var(--text-main)'};">{report.critical_count}</div>
                <div class="stat-lbl">Critical Issues</div>
            </div>
            <div class="stat-item">
                <div class="stat-val" style="color: {'var(--yellow)' if report.high_count > 0 else 'var(--text-main)'};">{report.high_count}</div>
                <div class="stat-lbl">High Issues</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">{report.medium_count + report.low_count}</div>
                <div class="stat-lbl">Medium / Low</div>
            </div>
        </div>

        <!-- Compliance Matrix -->
        <div class="card" style="margin-bottom: 32px;">
            <h3 style="font-size: 16px; margin-bottom: 4px;">Regulatory Compliance & Governance Standards</h3>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">Continuous mapping against enterprise security baselines and CI/CD policy gates.</p>
            <div class="compliance-grid">
                <div class="comp-card">
                    <span class="comp-name">Zero Hardcoded Secrets (CWE-798)</span>
                    <span class="badge {'badge-pass' if comp.zero_hardcoded_secrets else 'badge-fail'}">{'PASSED' if comp.zero_hardcoded_secrets else 'FAILED'}</span>
                </div>
                <div class="comp-card">
                    <span class="comp-name">OWASP Top 10 (2021) Baseline</span>
                    <span class="badge {'badge-pass' if comp.owasp_top_10_clean else 'badge-fail'}">{'PASSED' if comp.owasp_top_10_clean else 'FAILED'}</span>
                </div>
                <div class="comp-card">
                    <span class="comp-name">Input Sanitization (CWE-89 / CWE-78)</span>
                    <span class="badge {'badge-pass' if comp.input_sanitization_shield else 'badge-fail'}">{'PASSED' if comp.input_sanitization_shield else 'FAILED'}</span>
                </div>
                <div class="comp-card">
                    <span class="comp-name">Non-Root Container Enforcement</span>
                    <span class="badge {'badge-pass' if comp.non_root_container_certified else 'badge-fail'}">{'PASSED' if comp.non_root_container_certified else 'FAILED'}</span>
                </div>
                <div class="comp-card">
                    <span class="comp-name">Automated CI/CD PR Quality Gate</span>
                    <span class="badge {'badge-pass' if comp.ci_cd_gate_ready else 'badge-fail'}">{'PASSED' if comp.ci_cd_gate_ready else 'ATTENTION'}</span>
                </div>
            </div>
        </div>

        <!-- Findings Table -->
        <div class="card">
            <h3 style="font-size: 16px; margin-bottom: 4px;">Discovered Findings ({len(report.findings)} total)</h3>
            <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">Detailed vulnerability taxonomy mapped to MITRE CWE and actionable engineering remediations.</p>
            <div style="overflow-x: auto;">
                <table>
                    <thead>
                        <tr>
                            <th>Severity</th>
                            <th>Rule</th>
                            <th>CWE</th>
                            <th>Location</th>
                            <th>Issue & Remediation</th>
                        </tr>
                    </thead>
                    <tbody>
                        {findings_html}
                    </tbody>
                </table>
            </div>
        </div>

        <footer>
            <p>Generated autonomously by <strong>ProdForge Enterprise Suite v1.0.0</strong> • <a href="https://github.com/mradityasonicse/prodforge" style="color: var(--text-muted); text-decoration: none;">GitHub Repository</a></p>
        </footer>
    </div>
</body>
</html>
"""
    return html_content


def save_html_report(report: AuditReport, target_name: str, output_path: Path) -> Path:
    """Save generated HTML executive audit report to disk."""
    content = generate_html_audit_report(report, target_name)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path
