"""Tests for the File Upload and Live Scan REST API Endpoints."""

import io
import zipfile
import pytest
from fastapi.testclient import TestClient
from prodforge.studio.server import app

client = TestClient(app)


def test_api_live_scan():
    resp = client.post("/api/live", json={"url": "http://127.0.0.1:8000", "probe_endpoints": False})
    assert resp.status_code == 200
    data = resp.json()
    assert "live_scan" in data
    assert "audit_result" in data
    assert data["live_scan"]["status_code"] == 200
    assert data["audit_result"]["readiness_score"] >= 0


def test_api_upload_single_file():
    code = b"import os\nAWS_KEY = 'AKIA1234567890EXAMPLEKEY'\nquery = f'SELECT * FROM u WHERE id={raw} FROM a'\ndef test(): eval('1+1')"
    files = {"file": ("test_module.py", io.BytesIO(code), "text/x-python")}
    resp = client.post("/api/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_path"] == "test_module.py"
    assert data["critical_count"] >= 1
    assert data["readiness_score"] < 80


def test_api_upload_zip_archive():
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        z.writestr("src/main.py", "import os\ndef query(u): return f'SELECT * FROM u WHERE id={u}'")
        z.writestr("src/secret.py", "TOKEN = 'ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'")
    zip_buf.seek(0)

    files = {"file": ("my_project.zip", zip_buf, "application/zip")}
    resp = client.post("/api/upload", files=files)
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_path"] == "my_project.zip"
    assert len(data["findings"]) >= 1


def test_api_upload_zipslip_rejection():
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w") as z:
        # Malicious ZipSlip path traversal member
        z.writestr("../../../../../evil.py", "import os")
    zip_buf.seek(0)

    files = {"file": ("evil.zip", zip_buf, "application/zip")}
    resp = client.post("/api/upload", files=files)
    assert resp.status_code == 400
    assert "traversal" in resp.json()["detail"].lower()
