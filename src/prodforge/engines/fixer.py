"""
Autonomous Code Auto-Fixer & Self-Healing Engine.
Generates unified git patches and can safely apply automated remediations
for hardcoded credentials, unsafe eval/shell executions, weak cryptography,
and error-swallowing antipatterns.
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from pydantic import BaseModel, Field

from prodforge.engines.auditor import audit_single_file, FileAuditFinding


class AutoFixAction(BaseModel):
    file_path: str
    rule_id: str
    line_number: int
    original_snippet: str
    repaired_snippet: str
    explanation: str


class AutoFixResult(BaseModel):
    target_path: str
    total_fixes_generated: int
    applied: bool
    actions: List[AutoFixAction] = Field(default_factory=list)
    unified_patch: str = ""
    env_updates: Dict[str, str] = Field(default_factory=dict)

    @property
    def unified_diff(self) -> str:
        return self.unified_patch


def repair_file_content(file_path: Path, content: str, findings: List[FileAuditFinding]) -> Tuple[str, List[AutoFixAction], Dict[str, str]]:
    """Apply surgical deterministic code repairs to source content."""
    lines = content.splitlines()
    actions: List[AutoFixAction] = []
    env_updates: Dict[str, str] = {}
    is_python = file_path.suffix == ".py"
    is_js_ts = file_path.suffix in (".js", ".jsx", ".ts", ".tsx")

    # Sort findings reverse by line number so edits don't skew line indices
    sorted_findings = sorted(findings, key=lambda f: f.line_number, reverse=True)

    for f in sorted_findings:
        line_idx = f.line_number - 1
        if line_idx < 0 or line_idx >= len(lines):
            continue
        original_line = lines[line_idx]

        # 1. Fix Hardcoded Secrets
        if f.rule_id in ("SEC-001", "SEC-AWS-001", "SEC-GCP-001", "SEC-ENTROPY-001"):
            secret_match = re.search(r"""([A-Z0-9_]+)\s*=\s*['"]([^'"]+)['"]""", original_line)
            if secret_match:
                var_name = secret_match.group(1)
                secret_val = secret_match.group(2)
                env_updates[var_name] = secret_val

                if is_python:
                    repaired_line = re.sub(
                        r"""=\s*['"][^'"]+['"]""",
                        f'= os.getenv("{var_name}")',
                        original_line
                    )
                else:
                    repaired_line = re.sub(
                        r"""=\s*['"][^'"]+['"]""",
                        f'= process.env.{var_name}',
                        original_line
                    )

                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation=f"Extracted hardcoded secret into environment variable '{var_name}'."
                ))
                continue

        # 2. Fix Eval / Exec RCE Risk
        if f.rule_id == "SEC-003":
            if is_python and "eval(" in original_line:
                repaired_line = original_line.replace("eval(", "ast.literal_eval(")
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Replaced dangerous eval() with safe ast.literal_eval()."
                ))
                continue
            elif is_js_ts and "eval(" in original_line:
                repaired_line = original_line.replace("eval(", "JSON.parse(")
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Replaced dangerous eval() with safe JSON.parse()."
                ))
                continue

        # 3. Fix Subprocess Shell=True
        if f.rule_id == "SEC-004":
            if "shell=True" in original_line or "shell = True" in original_line:
                repaired_line = re.sub(r"""shell\s*=\s*True""", "shell=False", original_line)
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Disabled unsafe shell=True execution."
                ))
                continue

        # 4. Fix Weak MD5/SHA1
        if f.rule_id == "SEC-007":
            if "hashlib.md5" in original_line or "hashlib.sha1" in original_line:
                repaired_line = original_line.replace("hashlib.md5", "hashlib.sha256").replace("hashlib.sha1", "hashlib.sha256")
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Upgraded weak hash function to SHA-256."
                ))
                continue

        # 5. Fix Blind Exception Swallowing
        if f.rule_id == "QUAL-001" and is_python:
            if re.search(r"""^\s*except\s*:""", original_line):
                indent = original_line[:len(original_line) - len(original_line.lstrip())]
                repaired_line = f"{indent}except Exception as exc:\n{indent}    import logging; logging.error(f'Handled exception: {{exc}}')"
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Replaced blind except: with structured exception logging."
                ))
                continue

        # 6. Clean Debugging Print Artifact
        if f.rule_id == "QUAL-002":
            if re.search(r"""^\s*print\s*\(.*\)""", original_line) and is_python:
                indent = original_line[:len(original_line) - len(original_line.lstrip())]
                repaired_line = f"{indent}# [prodforge-clean] {original_line.strip()}"
                lines[line_idx] = repaired_line
                actions.append(AutoFixAction(
                    file_path=str(file_path),
                    rule_id=f.rule_id,
                    line_number=f.line_number,
                    original_snippet=original_line.strip(),
                    repaired_snippet=repaired_line.strip(),
                    explanation="Suppressed raw stdout debug print in production code."
                ))
                continue

    repaired_content = "\n".join(lines)
    return repaired_content, actions, env_updates


def auto_fix_target(target: str, apply: bool = False) -> AutoFixResult:
    """Analyze and generate / apply automated code repairs for a target file or project."""
    path = Path(target).resolve()
    if not path.exists():
        raise FileNotFoundError(f"Target path '{target}' does not exist.")

    files_to_fix: List[Path] = []
    if path.is_file():
        files_to_fix.append(path)
    else:
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "node_modules", "__pycache__"}]
            for f in files:
                p = Path(root) / f
                if p.suffix in (".py", ".js", ".jsx", ".ts", ".tsx"):
                    files_to_fix.append(p)

    all_actions: List[AutoFixAction] = []
    combined_env_updates: Dict[str, str] = {}
    patch_lines: List[str] = []

    for file_p in files_to_fix:
        findings, _ = audit_single_file(file_p)
        if not findings:
            continue

        original_code = file_p.read_text(encoding="utf-8", errors="replace")
        repaired_code, actions, env_updates = repair_file_content(file_p, original_code, findings)

        if actions:
            all_actions.extend(actions)
            combined_env_updates.update(env_updates)

            # Generate unified git diff patch
            diff = difflib.unified_diff(
                original_code.splitlines(keepends=True),
                repaired_code.splitlines(keepends=True),
                fromfile=f"a/{file_p.name}",
                tofile=f"b/{file_p.name}",
                n=3
            )
            patch_lines.extend(diff)

            if apply:
                file_p.write_text(repaired_code, encoding="utf-8")

    # If env updates found and apply=True, safely append to .env
    if apply and combined_env_updates:
        env_file = (path if path.is_dir() else path.parent) / ".env"
        existing_env = env_file.read_text(encoding="utf-8") if env_file.exists() else ""
        lines_to_add = []
        for k, v in combined_env_updates.items():
            if k not in existing_env:
                lines_to_add.append(f"{k}={v}")
        if lines_to_add:
            with open(env_file, "a", encoding="utf-8") as ef:
                ef.write("\n# ProdForge Auto-Remediated Secrets\n" + "\n".join(lines_to_add) + "\n")

    return AutoFixResult(
        target_path=str(path),
        total_fixes_generated=len(all_actions),
        applied=apply,
        actions=all_actions,
        unified_patch="".join(patch_lines),
        env_updates=combined_env_updates
    )
