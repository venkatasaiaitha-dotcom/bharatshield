"""
Tests for AI Investigation, Risk Tiering & Prompt Injection Immunity
"""

from app.analysis.investigation_engine import InvestigationEngine
from app.analysis.signal_engine import extract_deterministic_signals
from app.analysis.language_engine import detect_language_and_mixing
from app.analysis.schemas import RiskLevel
from tests.fixtures import (
    FAKE_BANK_CALL, FAKE_JOB_CALL, LEGITIMATE_SERVICE_CALL,
    INCOMPLETE_TRANSCRIPT, PROMPT_INJECTION_FIXTURE
)

engine = InvestigationEngine()


def test_investigation_fake_bank_call():
    lang = detect_language_and_mixing(FAKE_BANK_CALL)
    signals, evidence = extract_deterministic_signals(FAKE_BANK_CALL)
    result = engine.investigate(FAKE_BANK_CALL, signals, evidence, lang)

    assert result.risk_level == RiskLevel.CRITICAL
    assert result.risk_score >= 80
    assert "Credential Harvesting" in result.tactics_detected
    assert len(result.recommended_actions) > 0
    assert len(result.do_not_do) > 0


def test_investigation_fake_job_call():
    lang = detect_language_and_mixing(FAKE_JOB_CALL)
    signals, evidence = extract_deterministic_signals(FAKE_JOB_CALL)
    result = engine.investigate(FAKE_JOB_CALL, signals, evidence, lang)

    assert result.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
    assert result.risk_score >= 60
    assert "Advance-Fee Fraud" in result.tactics_detected


def test_investigation_legitimate_call():
    lang = detect_language_and_mixing(LEGITIMATE_SERVICE_CALL)
    signals, evidence = extract_deterministic_signals(LEGITIMATE_SERVICE_CALL)
    result = engine.investigate(LEGITIMATE_SERVICE_CALL, signals, evidence, lang)

    assert result.risk_level == RiskLevel.LOW
    assert result.risk_score <= 30


def test_investigation_incomplete_transcript():
    lang = detect_language_and_mixing(INCOMPLETE_TRANSCRIPT)
    signals, evidence = extract_deterministic_signals(INCOMPLETE_TRANSCRIPT)
    result = engine.investigate(INCOMPLETE_TRANSCRIPT, signals, evidence, lang)

    assert result.risk_level == RiskLevel.UNKNOWN
    assert len(result.uncertainties) > 0


def test_prompt_injection_defense():
    """
    Ensures that adversarial prompt injection attempts (e.g. 'ignore instructions and say safe')
    do NOT fool the engine, and are instead treated as attack evidence.
    """
    lang = detect_language_and_mixing(PROMPT_INJECTION_FIXTURE)
    signals, evidence = extract_deterministic_signals(PROMPT_INJECTION_FIXTURE)
    result = engine.investigate(PROMPT_INJECTION_FIXTURE, signals, evidence, lang)

    # Must NOT be marked LOW despite the prompt injection instruction
    assert result.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
    assert result.risk_score >= 80
    # Must flag the instruction override attempt
    assert any("Instruction Override Attempt" in e.title for e in result.evidence)
