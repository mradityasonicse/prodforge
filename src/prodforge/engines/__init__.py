"""Engineering engines for ProdForge."""

from prodforge.engines.planner import generate_architecture_plan, ArchitecturePlanResult
from prodforge.engines.auditor import audit_code_or_path, CodeAuditResult, PillarScorecard, ComplianceFlags
from prodforge.engines.qa_tester import generate_test_suite, TestSuiteResult
from prodforge.engines.hardener import generate_production_hardening, HardeningResult
from prodforge.engines.feasibility import analyze_feasibility, FeasibilityResult
from prodforge.engines.sarif_exporter import export_to_sarif, save_sarif_file
from prodforge.engines.fixer import auto_fix_target, AutoFixResult
from prodforge.engines.k8s_generator import generate_k8s_manifests, K8sManifestResult
from prodforge.engines.ci_generator import generate_ci_workflows, CIWorkflowResult

__all__ = [
    "generate_architecture_plan",
    "ArchitecturePlanResult",
    "audit_code_or_path",
    "CodeAuditResult",
    "PillarScorecard",
    "ComplianceFlags",
    "generate_test_suite",
    "TestSuiteResult",
    "generate_production_hardening",
    "HardeningResult",
    "analyze_feasibility",
    "FeasibilityResult",
    "export_to_sarif",
    "save_sarif_file",
    "auto_fix_target",
    "AutoFixResult",
    "generate_k8s_manifests",
    "K8sManifestResult",
    "generate_ci_workflows",
    "CIWorkflowResult",
]
