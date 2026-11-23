"""
ProdForge - The Autonomous Production Engineering, Architecture & QA Engine.
"""

from prodforge.config import get_config, ProdForgeConfig
from prodforge.client import LLMClient
from prodforge.engines import (
    generate_architecture_plan,
    audit_code_or_path,
    generate_test_suite,
    generate_production_hardening,
    analyze_feasibility,
)
from prodforge.cli import app

__version__ = "1.0.0"
__author__ = "ProdForge Team"

def main():
    """CLI entry point for console script."""
    app()

__all__ = [
    "__version__",
    "get_config",
    "ProdForgeConfig",
    "LLMClient",
    "generate_architecture_plan",
    "audit_code_or_path",
    "generate_test_suite",
    "generate_production_hardening",
    "analyze_feasibility",
    "app",
    "main",
]
