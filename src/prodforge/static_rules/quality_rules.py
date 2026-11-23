"""
Static Quality & Production Readiness Rules.
Detects error swallowing, unhandled promises, dirty debugging leftovers, and lack of typing.
"""

from __future__ import annotations

import re
from typing import List
from pydantic import BaseModel


class QualityFinding(BaseModel):
    rule_id: str
    title: str
    severity: str  # "HIGH", "MEDIUM", "LOW"
    line_number: int
    line_content: str
    description: str
    remediation: str


QUALITY_RULES = [
    {
        "id": "QUAL-001",
        "title": "Silent Error Swallowing (Blind Try/Catch)",
        "severity": "HIGH",
        "pattern": r"""(?:except\s*:|catch\s*\([^\)]*\)\s*\{\s*\})""",
        "description": "Exception caught and silently ignored without logging or re-throwing.",
        "remediation": "Log the error stack trace and return a structured fallback or re-throw a domain-specific exception."
    },
    {
        "id": "QUAL-002",
        "title": "Debugging Print / Console Artifact Left in Production",
        "severity": "LOW",
        "pattern": r"""\b(?:console\.log|console\.debug|print\s*\(|debugger;)""",
        "description": "Raw stdout print or debugger statement left in production code.",
        "remediation": "Replace with structured logging (e.g. loguru, pino, winston) with configurable log levels."
    },
    {
        "id": "QUAL-003",
        "title": "Use of Loose 'any' Type in TypeScript",
        "severity": "MEDIUM",
        "pattern": r""":\s*any\b|<any>|as\s+any\b""",
        "description": "Loose 'any' type disables compiler type safety and masks runtime errors.",
        "remediation": "Use explicit interfaces, union types, or 'unknown' combined with runtime Zod guards."
    },
    {
        "id": "QUAL-004",
        "title": "Missing Async Await / Floating Promise Risk",
        "severity": "MEDIUM",
        "pattern": r"""\b(?:fetch|axios\.get|axios\.post|db\.query)\s*\([^)]*\)\s*;""",
        "description": "Promise returned by async I/O operation is not awaited or chained with .then()/.catch().",
        "remediation": "Add 'await' before async calls inside async functions or handle rejection explicitly."
    },
    {
        "id": "QUAL-005",
        "title": "Hardcoded Localhost URL",
        "severity": "MEDIUM",
        "pattern": r"""https?://(?:localhost|127\.0\.0\.1)(?::\d+)?""",
        "description": "Hardcoded local URL will break in staging and production environments.",
        "remediation": "Move host endpoints to environment variables (e.g. process.env.API_BASE_URL)."
    },
    {
        "id": "QUAL-006",
        "title": "Unbounded Loop / Sleep in Async Handler",
        "severity": "HIGH",
        "pattern": r"""\b(?:time\.sleep|while\s*True|while\s*\(true\))""",
        "description": "Blocking synchronous sleep or infinite loop inside application handler.",
        "remediation": "Use non-blocking asyncio.sleep() or bounded event-driven loops with timeout safeguards."
    }
]


def scan_quality(source_code: str) -> List[QualityFinding]:
    """Execute static quality & production readiness checks."""
    findings: List[QualityFinding] = []
    lines = source_code.splitlines()

    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        if clean_line.startswith(("//", "#", "/*", "*")):
            continue
        if '"pattern":' in clean_line or '"description":' in clean_line or '"remediation":' in clean_line:
            continue
        if any(marker in clean_line for marker in ("re.search(r", "re.compile(r", "re.sub(r", "re.match(r", "re.search(\"", "re.search('")):
            continue

        for rule in QUALITY_RULES:
            if re.search(rule["pattern"], clean_line):
                findings.append(
                    QualityFinding(
                        rule_id=rule["id"],
                        title=rule["title"],
                        severity=rule["severity"],
                        line_number=idx,
                        line_content=clean_line[:120],
                        description=rule["description"],
                        remediation=rule["remediation"]
                    )
                )

    return findings
