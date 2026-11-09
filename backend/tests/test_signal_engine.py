"""
Tests for Deterministic Scam Signal Engine
"""

from app.analysis.signal_engine import extract_deterministic_signals
from app.analysis.schemas import Severity
from tests.fixtures import (
    FAKE_BANK_CALL, FAKE_JOB_CALL, LEGITIMATE_SERVICE_CALL,
    TELUGU_ENGLISH_CONVERSATION, HINDI_ENGLISH_CONVERSATION
)


def test_extract_signals_fake_bank_call():
    signals, evidence = extract_deterministic_signals(FAKE_BANK_CALL)

    assert signals.credential_request is True
    assert signals.urgency is True
    assert signals.impersonation is True
    assert signals.financial_request is False

    # Check evidence quotes
    otp_ev = next((e for e in evidence if "OTP" in e.title), None)
    assert otp_ev is not None
    assert otp_ev.severity == Severity.CRITICAL
    assert "otp" in otp_ev.quote.lower()


def test_extract_signals_fake_job_call():
    signals, evidence = extract_deterministic_signals(FAKE_JOB_CALL)

    assert signals.financial_request is True
    assert signals.urgency is True
    assert signals.impersonation is True
    assert signals.credential_request is False

    fee_ev = next((e for e in evidence if "Fee" in e.title or "Transfer" in e.title), None)
    assert fee_ev is not None
    assert "registration fee" in fee_ev.quote.lower() or "transfer" in fee_ev.quote.lower()


def test_extract_signals_legitimate_call():
    signals, evidence = extract_deterministic_signals(LEGITIMATE_SERVICE_CALL)

    assert signals.credential_request is False
    assert signals.financial_request is False
    assert signals.urgency is False
    assert len(evidence) == 0


def test_extract_signals_telugu_english():
    signals, evidence = extract_deterministic_signals(TELUGU_ENGLISH_CONVERSATION)

    assert signals.credential_request is True
    assert signals.urgency is True
    assert signals.impersonation is True


def test_extract_signals_hindi_english():
    signals, evidence = extract_deterministic_signals(HINDI_ENGLISH_CONVERSATION)

    assert signals.remote_access_request is True
    assert signals.impersonation is True
    assert any("Remote Access" in e.title or "Screen" in e.title for e in evidence)
