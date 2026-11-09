"""
Tests for API Routes & Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures import FAKE_BANK_CALL

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "gnani_configured" in data
    # Ensure no secret key in health response
    assert "PASTE_KEY_HERE" not in str(data)
    assert "api_key" not in data


def test_demo_scenarios_endpoint():
    response = client.get("/api/demo/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert "scenarios" in data
    assert len(data["scenarios"]) >= 3
    scenario_ids = [s["id"] for s in data["scenarios"]]
    assert "fake_bank_kyc" in scenario_ids
    assert "fake_job_offer" in scenario_ids
    assert "digital_arrest" in scenario_ids


def test_investigate_endpoint():
    payload = {
        "transcript": FAKE_BANK_CALL,
        "language_code": "indic-auto"
    }
    response = client.post("/api/investigate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["investigation"]["risk_level"] == "CRITICAL"
    assert data["investigation"]["risk_score"] >= 80
    assert "en" in data["explanations"]
    assert "te" in data["explanations"]
    assert "hi" in data["explanations"]


def test_demo_audio_endpoint():
    response = client.get("/api/demo/audio/fake_bank_kyc")
    assert response.status_code == 200
    assert "audio/wav" in response.headers["content-type"]
    assert len(response.content) > 1000


def test_generate_incident_report_endpoint():
    payload = {
        "transcript": FAKE_BANK_CALL,
        "language_code": "indic-auto"
    }
    response = client.post("/api/report/generate", json=payload)
    assert response.status_code == 200
    assert "NATIONAL CYBER CRIME INCIDENT DOSSIER" in response.text
    assert "1930" in response.text
    assert "Section 66D" in response.text


def test_security_headers_present():
    response = client.get("/health")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
