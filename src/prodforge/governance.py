"""
Enterprise Governance and Policy Engine for ProdForge.
Allows security and platform teams to enforce organizational quality gates,
ignore rules, whitelist test paths, and compliance frameworks via .prodforge.yaml.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
import fnmatch
from pydantic import BaseModel, Field


class EnterprisePolicy(BaseModel):
    """Declarative enterprise security & quality policy."""
    threshold: int = Field(default=80, description="Minimum Production Readiness Index required to pass PR gates")
    fail_on_critical: bool = Field(default=True, description="Fail immediately if any CRITICAL vulnerability is found")
    fail_on_high: bool = Field(default=False, description="Fail immediately if any HIGH vulnerability is found")
    ignore_rules: List[str] = Field(
        default_factory=lambda: ["QUAL-002"],
        description="Rule IDs to suppress organization-wide (e.g. QUAL-002 for debug prints in development)"
    )
    ignore_paths: List[str] = Field(
        default_factory=lambda: [
            "tests/**",
            "test/**",
            "fixtures/**",
            "dist/**",
            "build/**",
            "node_modules/**",
            ".git/**",
            "__pycache__/**",
            "*.min.js",
            "*.bundle.js",
            "venv/**",
            ".venv/**"
        ],
        description="Glob patterns of files and directories to exclude from audit"
    )
    allowed_secrets: List[str] = Field(
        default_factory=list,
        description="Regex patterns for allowed test credentials or sample mock keys"
    )
    compliance_frameworks: List[str] = Field(
        default_factory=lambda: ["OWASP Top 10", "SOC2 Type II", "HIPAA §164.312", "PCI-DSS v4.0"],
        description="Active compliance frameworks evaluated during code audits"
    )

    def is_path_ignored(self, path: Path | str, base_dir: Optional[Path] = None) -> bool:
        """Check if a file path matches any organization ignore glob pattern."""
        p_str = str(path).replace("\\", "/")
        if base_dir:
            try:
                rel = Path(path).resolve().relative_to(base_dir.resolve())
                p_str = str(rel).replace("\\", "/")
            except ValueError:
                pass

        for pattern in self.ignore_paths:
            clean_pat = pattern.replace("\\", "/")
            if fnmatch.fnmatch(p_str, clean_pat) or fnmatch.fnmatch(Path(path).name, clean_pat):
                return True
            if "**" in clean_pat:
                pat_suffix = clean_pat.replace("**/", "")
                if fnmatch.fnmatch(p_str, f"*{pat_suffix}"):
                    return True
        return False

    def is_rule_ignored(self, rule_id: str) -> bool:
        """Check if a specific rule ID is suppressed in enterprise policy."""
        return rule_id in self.ignore_rules


def find_governance_file(target_dir: Path) -> Optional[Path]:
    """Search for enterprise configuration file (.prodforge.yaml or .prodforge.json)."""
    search_dir = target_dir.resolve()
    if search_dir.is_file():
        search_dir = search_dir.parent

    candidates = [
        ".prodforge.yaml",
        "prodforge.yaml",
        ".prodforge.yml",
        "prodforge.yml",
        ".prodforge.json",
        "prodforge.json"
    ]

    curr = search_dir
    while curr != curr.parent:
        for c in candidates:
            fp = curr / c
            if fp.is_file():
                return fp
        curr = curr.parent

    return None


def load_governance_policy(target_dir: Optional[Path] = None) -> EnterprisePolicy:
    """Load enterprise policy from file, falling back to secure enterprise defaults."""
    if not target_dir:
        target_dir = Path.cwd()

    config_path = find_governance_file(target_dir)
    if not config_path:
        return EnterprisePolicy()

    try:
        content = config_path.read_text(encoding="utf-8")
        if config_path.suffix in (".yaml", ".yml"):
            try:
                import yaml  # type: ignore
                data = yaml.safe_load(content) or {}
            except ImportError:
                # Fallback simple parser if pyyaml is not present
                data = _simple_yaml_parse(content)
        else:
            data = json.loads(content)
        
        return EnterprisePolicy(**data)
    except Exception:
        return EnterprisePolicy()


def _simple_yaml_parse(content: str) -> dict:
    """Zero-dependency basic YAML parser for standard key-value and list configs."""
    result = {}
    current_list_key = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("- ") and current_list_key:
            val = line[2:].strip().strip("'\"")
            result.setdefault(current_list_key, []).append(val)
            continue

        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()

            if not val:
                current_list_key = key
                result[key] = []
            else:
                current_list_key = None
                if val.lower() == "true":
                    result[key] = True
                elif val.lower() == "false":
                    result[key] = False
                elif val.isdigit():
                    result[key] = int(val)
                elif val.startswith("[") and val.endswith("]"):
                    items = [x.strip().strip("'\"") for x in val[1:-1].split(",") if x.strip()]
                    result[key] = items
                else:
                    result[key] = val.strip("'\"")

    return result


def create_default_governance_file(target_dir: Path) -> Path:
    """Generate a clean, production-ready .prodforge.yaml policy in target directory."""
    target_path = target_dir / ".prodforge.yaml"
    template = """# ==============================================================================
# ProdForge Enterprise Governance & Quality Gate Policy
# https://github.com/mradityasonicse/prodforge
# ==============================================================================
version: "1.0"

# 1. CI/CD Gate Threshold
# Minimum Production Readiness Index (0-100) required to pass builds & PR checks.
threshold: 80

# Fail pipeline immediately if any CRITICAL vulnerability (CWE-798, CWE-89, CWE-94) is found.
fail_on_critical: true

# Fail pipeline if HIGH severity issues are detected.
fail_on_high: false

# 2. Ignored Rules
# Suppress specific rule IDs organization-wide if they conflict with your stack.
ignore_rules:
  - QUAL-002  # Console log / debug prints

# 3. Excluded Paths
# Directories and glob patterns to exclude from automated security audits.
ignore_paths:
  - "tests/**"
  - "test/**"
  - "fixtures/**"
  - "dist/**"
  - "build/**"
  - "node_modules/**"
  - ".git/**"
  - "__pycache__/**"
  - "*.min.js"
  - "venv/**"
  - ".venv/**"

# 4. Whitelisted Test Credentials
# Regex patterns for mock or test credentials used in integration tests.
allowed_secrets:
  - "test_secret_.*"
  - "mock_token_.*"

# 5. Regulatory Compliance Frameworks Evaluated
compliance_frameworks:
  - "OWASP Top 10 (2021)"
  - "SOC2 Type II (CC6.1 - CC6.8)"
  - "HIPAA Security Rule (§164.312)"
  - "PCI-DSS v4.0 (Requirement 6)"
"""
    target_path.write_text(template, encoding="utf-8")
    return target_path
