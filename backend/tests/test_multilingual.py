"""
Tests for Multilingual & Code-Mixing Detection and Translation
"""

from app.analysis.language_engine import detect_language_and_mixing
from app.analysis.multilingual import generate_multilingual_explanations
from app.analysis.schemas import InvestigationResult, RiskLevel
from tests.fixtures import (
    TELUGU_ENGLISH_CONVERSATION, HINDI_ENGLISH_CONVERSATION, LEGITIMATE_SERVICE_CALL
)


def test_telugu_english_detection():
    result = detect_language_and_mixing(TELUGU_ENGLISH_CONVERSATION)
    assert "Telugu" in result.detected_language
    assert result.code_mixed is True or result.confidence >= 0.85


def test_hindi_english_detection():
    result = detect_language_and_mixing(HINDI_ENGLISH_CONVERSATION)
    assert "Hindi" in result.detected_language


def test_english_detection():
    result = detect_language_and_mixing(LEGITIMATE_SERVICE_CALL)
    assert result.detected_language == "English"


def test_multilingual_explanations_consistency():
    investigation = InvestigationResult(
        risk_level=RiskLevel.CRITICAL,
        risk_score=92,
        confidence=0.95,
        summary="High risk OTP fraud attempt",
        evidence=[],
        tactics_detected=["Credential Harvesting"],
        requested_information=["OTP"],
        recommended_actions=["Disconnect immediately"],
        do_not_do=["Do not share OTP"],
        explanation="The caller requested an OTP under pressure.",
        uncertainties=[]
    )

    explanations = generate_multilingual_explanations(investigation)

    assert "en" in explanations
    assert "te" in explanations
    assert "hi" in explanations

    # Telugu translation check
    te = explanations["te"]
    assert "OTP" in te.spoken_summary
    assert "రిస్క్ స్కోర్" in te.spoken_summary
    assert len(te.recommended_actions) > 0

    # Hindi translation check
    hi = explanations["hi"]
    assert "OTP" in hi.spoken_summary
    assert "जोखिम" in hi.summary or "ओटीपी" in hi.summary or "OTP" in hi.summary
