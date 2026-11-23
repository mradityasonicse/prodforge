"""
ProdForge Enterprise PDF Audit Report Generator.
Converts executive audit telemetry, gauges, CWE matrices, and remediation
roadmaps into publication-grade vector PDF reports via headless browser engine.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, TYPE_CHECKING

from prodforge.engines.html_reporter import generate_html_audit_report

if TYPE_CHECKING:
    from prodforge.engines.auditor import AuditReport


def find_browser_executable() -> Optional[str]:
    """Locate headless Chrome or Edge executable on Windows, Linux, or macOS."""
    env_paths = [
        os.getenv("PRODFORGE_CHROME_PATH"),
        os.getenv("CHROME_PATH"),
        os.getenv("BROWSER_PATH"),
    ]
    for ep in env_paths:
        if ep and os.path.exists(ep) and os.path.isfile(ep):
            return ep

    # Standard platform locations
    candidates = [
        # Windows
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        # Linux
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        # macOS
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
    ]

    for candidate in candidates:
        if candidate and os.path.exists(candidate) and os.path.isfile(candidate):
            return candidate

    # Search PATH
    for bin_name in ("google-chrome", "google-chrome-stable", "chrome", "msedge", "chromium", "chromium-browser"):
        found = shutil.which(bin_name)
        if found:
            return found

    return None


def generate_pdf_audit_report(report: AuditReport, target_name: str, output_path: str) -> str:
    """
    Render executive audit report into a publication-grade PDF document.
    
    Args:
        report: Complete AuditReport object
        target_name: Name or path of the scanned target
        output_path: Target path for the generated PDF
        
    Returns:
        Absolute path to the created PDF file
    """
    browser = find_browser_executable()
    if not browser:
        raise RuntimeError(
            "Headless browser (Chrome or Edge) not found. "
            "Please ensure Google Chrome or Microsoft Edge is installed, "
            "or set CHROME_PATH in your environment variables."
        )

    out_file = Path(output_path).resolve()
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # 1. Generate standalone HTML
    html_content = generate_html_audit_report(report, target_name)

    # 2. Write to temporary HTML file
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tmp:
        tmp.write(html_content)
        tmp_html_path = tmp.name

    try:
        # Convert file path to file URI format
        file_uri = Path(tmp_html_path).as_uri()

        # Modern Chromium print-to-pdf command
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-pdf-header-footer",
            "--run-all-compositor-stages-before-draw",
            f"--print-to-pdf={str(out_file)}",
            file_uri
        ]

        # Execute headless print
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=45,
            check=False
        )

        if not out_file.exists() or out_file.stat().st_size == 0:
            err_msg = result.stderr.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Browser failed to generate PDF. Exit code: {result.returncode}. Log: {err_msg}")

        return str(out_file)

    finally:
        if os.path.exists(tmp_html_path):
            try:
                os.remove(tmp_html_path)
            except OSError:
                pass
