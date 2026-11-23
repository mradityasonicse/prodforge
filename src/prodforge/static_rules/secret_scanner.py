"""
Enterprise Shannon Entropy & Secret Scanner.
Uses information theory math (Shannon Entropy) alongside regex pattern signatures
to catch real credentials, private keys, and high-entropy secrets with minimal false positives.
"""

from __future__ import annotations

import math
import re
from typing import List, Optional
from pydantic import BaseModel


class DetectedSecret(BaseModel):
    rule_id: str
    secret_type: str
    line_number: int
    line_snippet: str
    entropy: float
    remediation: str


# High-confidence credential patterns with designated CWE-798 mapping
KNOWN_SECRET_PATTERNS = [
    {
        "id": "SEC-AWS-001",
        "name": "AWS Access Key ID",
        "pattern": r"\b(AKIA[0-9A-Z]{16})\b",
        "remediation": "Store AWS credentials in AWS Secrets Manager or IAM Instance Roles."
    },
    {
        "id": "SEC-GCP-001",
        "name": "Google Gemini / Cloud API Key",
        "pattern": r"\b(AIzaSy[A-Za-z0-9_-]{30,35})\b",
        "remediation": "Store Google API key in environment variables or Google Secret Manager."
    },
    {
        "id": "SEC-GITHUB-001",
        "name": "GitHub Personal Access Token",
        "pattern": r"\b(gh[pousr]_[A-Za-z0-9_]{36,255}|github_pat_[A-Za-z0-9_]{22,255})\b",
        "remediation": "Revoke exposed GitHub token and switch to fine-grained repository secrets."
    },
    {
        "id": "SEC-SLACK-001",
        "name": "Slack Token / Webhook URL",
        "pattern": r"(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*|https://hooks\.slack\.com/services/T[0-9A-Z]{8}/B[0-9A-Z]{8}/[a-zA-Z0-9]{24})",
        "remediation": "Revoke Slack webhook/token and inject via encrypted environment secrets."
    },
    {
        "id": "SEC-STRIPE-001",
        "name": "Stripe Live API Key",
        "pattern": r"\b([sr]k_live_[0-9a-zA-Z]{24,99})\b",
        "remediation": "Rotate Stripe live key immediately and restrict key permissions in Stripe dashboard."
    },
    {
        "id": "SEC-SSH-001",
        "name": "Private Cryptographic Key",
        "pattern": r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        "remediation": "Never store private keys in code repositories. Use HashiCorp Vault or cloud KMS."
    },
    {
        "id": "SEC-JWT-001",
        "name": "Hardcoded JSON Web Token (JWT)",
        "pattern": r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b",
        "remediation": "Generate short-lived JWTs dynamically at runtime with asymmetric RS256/EdDSA signing."
    },
    {
        "id": "SEC-DB-001",
        "name": "Database Connection URI with Embedded Credentials",
        "pattern": r"(?:postgres|mysql|mongodb|redis)://[^:]+:[^@]+@[^/]+/\w+",
        "remediation": "Construct database connection strings from isolated environment variables at runtime."
    }
]


def calculate_shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string (bits per symbol)."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    frequencies = {}
    for char in data:
        frequencies[char] = frequencies.get(char, 0) + 1
    for count in frequencies.values():
        p = count / length
        entropy -= p * math.log2(p)
    return entropy


def scan_secrets(source_code: str) -> List[DetectedSecret]:
    """Scan code lines for known secret formats and high-entropy assignments."""
    secrets_found: List[DetectedSecret] = []
    lines = source_code.splitlines()

    for idx, line in enumerate(lines, start=1):
        clean_line = line.strip()
        # Ignore comments and rule definitions
        if clean_line.startswith(("//", "#", "/*", "*")):
            continue
        if '"pattern":' in clean_line or '"id":' in clean_line or '"name":' in clean_line:
            continue

        # 1. Signature-based high-confidence matches
        for pattern_def in KNOWN_SECRET_PATTERNS:
            match = re.search(pattern_def["pattern"], clean_line)
            if match:
                matched_token = match.group(0)
                entropy = calculate_shannon_entropy(matched_token)
                secrets_found.append(
                    DetectedSecret(
                        rule_id=pattern_def["id"],
                        secret_type=pattern_def["name"],
                        line_number=idx,
                        line_snippet=clean_line[:120],
                        entropy=round(entropy, 2),
                        remediation=pattern_def["remediation"]
                    )
                )
                break  # Don't duplicate for same line

        # 2. Heuristic high-entropy variable assignment check (e.g. secret = "a9f8e4c7d6b3a2...")
        assignment_match = re.search(
            r"""(?i)(?:api_key|secret|token|password|auth_key|private_key)\s*[:=]\s*['"]([a-zA-Z0-9_\-\.+=/]{16,})['"]""",
            clean_line
        )
        if assignment_match:
            candidate_val = assignment_match.group(1)
            entropy = calculate_shannon_entropy(candidate_val)
            # High-entropy strings typically have entropy > 3.6 for base64/hex
            if entropy >= 3.6 and not any(s.line_number == idx for s in secrets_found):
                secrets_found.append(
                    DetectedSecret(
                        rule_id="SEC-ENTROPY-001",
                        secret_type="High-Entropy Secret / API Credential",
                        line_number=idx,
                        line_snippet=clean_line[:120],
                        entropy=round(entropy, 2),
                        remediation="Move raw secret to .env file and access via process.env or os.getenv."
                    )
                )

    return secrets_found
