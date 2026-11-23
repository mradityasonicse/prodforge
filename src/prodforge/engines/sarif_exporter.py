"""
OASIS SARIF v2.1.0 Exporter for ProdForge.
Enables native ingestion into GitHub Advanced Security, GitLab Security,
SonarQube, and VSCode/JetBrains SARIF viewers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List
from prodforge.engines.auditor import CodeAuditResult


def export_to_sarif(audit_result: CodeAuditResult) -> Dict[str, Any]:
    """Convert ProdForge CodeAuditResult into standard SARIF v2.1.0 JSON format."""
    rules_dict: Dict[str, Dict[str, Any]] = {}
    sarif_results: List[Dict[str, Any]] = []

    # Map ProdForge severities to SARIF levels: 'error', 'warning', 'note'
    severity_map = {
        "CRITICAL": "error",
        "HIGH": "error",
        "MEDIUM": "warning",
        "LOW": "note"
    }

    for f in audit_result.findings:
        # Register rule if not already present
        if f.rule_id not in rules_dict:
            rules_dict[f.rule_id] = {
                "id": f.rule_id,
                "name": f.title.replace(" ", ""),
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.description},
                "help": {
                    "text": f"Remediation: {f.remediation}",
                    "markdown": f"### Remediation\n{f.remediation}"
                },
                "properties": {
                    "category": f.category,
                    "precision": "high",
                    "security-severity": "9.0" if f.severity == "CRITICAL" else ("7.0" if f.severity == "HIGH" else "4.0")
                }
            }

        file_uri = Path(f.file_path).as_uri() if Path(f.file_path).is_absolute() else f"file:///{f.file_path.replace('\\', '/')}"

        sarif_results.append({
            "ruleId": f.rule_id,
            "level": severity_map.get(f.severity, "warning"),
            "message": {
                "text": f"{f.title}: {f.description} (Remediation: {f.remediation})"
            },
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": file_uri
                        },
                        "region": {
                            "startLine": f.line_number,
                            "startColumn": 1,
                            "snippet": {
                                "text": f.line_content
                            }
                        }
                    }
                }
            ]
        })

    sarif_doc = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "ProdForge",
                        "organization": "ProdForge Engineering",
                        "semanticVersion": "1.0.0",
                        "informationUri": "https://github.com/mradityasonicse/prodforge",
                        "rules": list(rules_dict.values())
                    }
                },
                "results": sarif_results,
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "toolExecutionNotifications": []
                    }
                ]
            }
        ]
    }

    return sarif_doc


def save_sarif_file(audit_result: CodeAuditResult, output_path: Path) -> None:
    """Serialize and write SARIF document to disk."""
    sarif_data = export_to_sarif(audit_result)
    output_path.write_text(json.dumps(sarif_data, indent=2), encoding="utf-8")
