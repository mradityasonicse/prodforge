"""
FastAPI Backend Server for ProdForge Web Studio.
Serves REST APIs, WebSocket live execution, and modern Awwwards-grade UI assets.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from prodforge.config import get_config
from prodforge.engines.planner import generate_architecture_plan, ArchitecturePlanResult
from prodforge.engines.auditor import audit_code_or_path, CodeAuditResult
from prodforge.engines.qa_tester import generate_test_suite, TestSuiteResult
from prodforge.engines.hardener import generate_production_hardening, HardeningResult
from prodforge.engines.feasibility import analyze_feasibility, FeasibilityResult
from prodforge.engines.sarif_exporter import export_to_sarif
from prodforge.engines.fixer import auto_fix_target, AutoFixResult
from prodforge.engines.k8s_generator import generate_k8s_manifests, K8sManifestResult
from prodforge.engines.ci_generator import generate_ci_workflows, CIWorkflowResult

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="ProdForge Studio",
    description="Interactive Web Studio for Autonomous Production Software Engineering",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# --- Request & Response Models ---

class PlanRequest(BaseModel):
    idea: str
    constraints: Optional[str] = None
    model: Optional[str] = None


class AuditRequest(BaseModel):
    target_path: Optional[str] = None
    raw_code: Optional[str] = None
    language: Optional[str] = "python"
    model: Optional[str] = None
    fail_under: Optional[int] = None


class FixRequest(BaseModel):
    target_path: str
    apply: bool = False


class TestRequest(BaseModel):
    target_path: Optional[str] = None
    raw_code: Optional[str] = None
    framework: Optional[str] = None
    model: Optional[str] = None


class HardenRequest(BaseModel):
    project_path: str = "."
    apply: bool = False
    model: Optional[str] = None


class FeasibilityRequest(BaseModel):
    idea: str
    target_dau: int = 50000
    model: Optional[str] = None


class K8sRequest(BaseModel):
    app_name: str = "prodforge-app"
    namespace: str = "production"
    domain: str = "api.example.com"
    image: str = "ghcr.io/org/app:v1.0.0"


class CIRequest(BaseModel):
    min_score: int = 85
    project_dir: str = "."
    apply: bool = False


# --- Endpoints ---

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return HTMLResponse("<h1>ProdForge Studio Backend Ready</h1><p>Static assets compiling...</p>")


@app.get("/api/status")
def get_status() -> Dict[str, Any]:
    cfg = get_config()
    return {
        "status": "online",
        "version": "1.0.0",
        "detected_provider": cfg.detected_provider,
        "active_model": cfg.active_model,
        "keys_configured": {
            "gemini": bool(cfg.gemini_api_key),
            "openai": bool(cfg.openai_api_key),
            "anthropic": bool(cfg.anthropic_api_key),
            "groq": bool(cfg.groq_api_key),
            "openrouter": bool(cfg.openrouter_api_key)
        },
        "ollama_host": cfg.ollama_host
    }


@app.post("/api/plan")
def api_plan(req: PlanRequest) -> ArchitecturePlanResult:
    if not req.idea.strip():
        raise HTTPException(status_code=400, detail="Product idea cannot be empty.")
    try:
        return generate_architecture_plan(idea=req.idea, constraints=req.constraints, model=req.model)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/audit")
def api_audit(req: AuditRequest) -> CodeAuditResult:
    if not req.target_path and not req.raw_code:
        raise HTTPException(status_code=400, detail="Must provide either target_path or raw_code.")
    try:
        return audit_code_or_path(
            target=req.target_path or "<in-memory>",
            raw_code=req.raw_code,
            language=req.language or "python",
            model=req.model,
            fail_under=req.fail_under
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/sarif")
def api_sarif(req: AuditRequest) -> Dict[str, Any]:
    if not req.target_path and not req.raw_code:
        raise HTTPException(status_code=400, detail="Must provide either target_path or raw_code.")
    try:
        audit_res = audit_code_or_path(
            target=req.target_path or "<in-memory>",
            raw_code=req.raw_code,
            language=req.language or "python",
            model=req.model
        )
        return export_to_sarif(audit_res)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/fix")
def api_fix(req: FixRequest) -> AutoFixResult:
    try:
        return auto_fix_target(target=req.target_path, apply=req.apply)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/test")
def api_test(req: TestRequest) -> TestSuiteResult:
    if not req.target_path and not req.raw_code:
        raise HTTPException(status_code=400, detail="Must provide either target_path or raw_code.")
    try:
        return generate_test_suite(
            target_path=req.target_path or "module_under_test.py",
            raw_code=req.raw_code,
            framework=req.framework,
            model=req.model
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/harden")
def api_harden(req: HardenRequest) -> HardeningResult:
    try:
        return generate_production_hardening(
            project_path=req.project_path,
            apply=req.apply,
            model=req.model
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/feasibility")
def api_feasibility(req: FeasibilityRequest) -> FeasibilityResult:
    if not req.idea.strip():
        raise HTTPException(status_code=400, detail="Idea cannot be empty.")
    try:
        return analyze_feasibility(
            idea=req.idea,
            target_dau=req.target_dau,
            model=req.model
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/k8s")
def api_k8s(req: K8sRequest) -> K8sManifestResult:
    try:
        return generate_k8s_manifests(
            app_name=req.app_name,
            namespace=req.namespace,
            domain=req.domain,
            container_image=req.image
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/ci")
def api_ci(req: CIRequest) -> CIWorkflowResult:
    try:
        return generate_ci_workflows(
            min_score=req.min_score,
            project_dir=Path(req.project_dir),
            apply=req.apply
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
