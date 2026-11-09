"""
BharatShield Voice - AI Investigation Engine
Orchestrates structured risk investigation, deterministic baseline calculation,
prompt injection immunity, and strict schema validation.
"""

import re
from typing import List, Dict, Any, Tuple
from app.analysis.schemas import (
    RiskLevel, Severity, EvidenceItem, DeterministicSignals,
    InvestigationResult, LanguageDetectionResult
)
from app.analysis.prompts import SYSTEM_SAFETY_INSTRUCTIONS
from app.utils.logging import get_logger

logger = get_logger("investigation_engine")

PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(the\s+)?system",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
    r"say\s+(this\s+call\s+is\s+)?(safe|legitimate|verified)",
    r"system\s*prompt",
    r"repeat\s+after\s+me",
    r"override\s+safety\s+filter",
]


class InvestigationEngine:
    """
    Analyzes conversation transcripts using deterministic signal synthesis
    and defensive AI reasoning.
    """

    def investigate(
        self,
        transcript: str,
        signals: DeterministicSignals,
        evidence: List[EvidenceItem],
        language_info: LanguageDetectionResult
    ) -> InvestigationResult:
        """
        Executes safe structured investigation.
        """
        clean_text = transcript.strip()
        if len(clean_text) < 15:
            return InvestigationResult(
                risk_level=RiskLevel.UNKNOWN,
                risk_score=10,
                confidence=0.5,
                summary="Insufficient conversation audio or transcript provided to conduct a reliable risk assessment.",
                evidence=[],
                tactics_detected=[],
                requested_information=[],
                recommended_actions=["Upload or record a clearer sample of the conversation"],
                do_not_do=["Do not proceed if the caller requested confidential details"],
                explanation="The audio was too short or quiet to extract sufficient context. Always verify caller identities independently.",
                uncertainties=["Transcript length is below minimum evaluation threshold"],
                analysis_mode="rule_based_fallback"
            )

        # Check for prompt injection attempts within the transcript
        injection_detected, injection_quote = self._check_prompt_injection(clean_text)
        if injection_detected:
            logger.warning("Prompt injection attempt intercepted in transcript: %s", injection_quote)
            # Add as an evidence of manipulation rather than following it!
            evidence.append(EvidenceItem(
                category="Technical Manipulation",
                severity=Severity.CRITICAL,
                title="Instruction Override Attempt",
                explanation="The transcript contained an adversarial attempt to override the AI safety engine.",
                quote=injection_quote or "Attempt to manipulate AI evaluation",
                icon="shield-alert"
            ))

        # Calculate calibrated risk score
        risk_score, risk_level, confidence = self._calculate_risk_metrics(signals, injection_detected, clean_text)

        # Extract tactics and requested info
        tactics, requested_info = self._extract_tactics_and_requests(signals, injection_detected)

        # Generate recommended actions and warnings
        actions, do_not_dos = self._generate_guidance(risk_level, signals)

        # Build clear plain-language summary & explanation
        summary, explanation = self._generate_summary_and_explanation(
            risk_level, risk_score, signals, language_info.detected_language
        )

        uncertainties = []
        if language_info.confidence < 0.75:
            uncertainties.append(f"Language detection confidence is moderate ({int(language_info.confidence * 100)}%)")
        if len(clean_text) < 60:
            uncertainties.append("Short conversation fragment; context may be partial")

        return InvestigationResult(
            risk_level=risk_level,
            risk_score=risk_score,
            confidence=confidence,
            summary=summary,
            evidence=evidence,
            tactics_detected=tactics,
            requested_information=requested_info,
            recommended_actions=actions,
            do_not_do=do_not_dos,
            explanation=explanation,
            uncertainties=uncertainties,
            analysis_mode="ai_investigation"
        )

    def _check_prompt_injection(self, text: str) -> Tuple[bool, str]:
        for pattern in PROMPT_INJECTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                start = max(0, match.start() - 20)
                end = min(len(text), match.end() + 20)
                return True, text[start:end].strip()
        return False, ""

    def _calculate_risk_metrics(
        self,
        signals: DeterministicSignals,
        injection_detected: bool,
        text: str
    ) -> Tuple[int, RiskLevel, float]:
        score = 0
        confidence = 0.85

        # Weighted score evaluation
        if signals.credential_request:
            score += 50
        if signals.remote_access_request:
            score += 40
        if signals.impersonation:
            score += 25
        if signals.urgency:
            score += 20
        if signals.financial_request:
            score += 25
        if signals.social_engineering:
            score += 20
        if injection_detected:
            score += 35

        # Bonus for compound attack (e.g. Impersonation + Urgency + Credential)
        high_risk_signals_count = sum([
            signals.credential_request,
            signals.remote_access_request,
            signals.impersonation,
            signals.urgency,
            signals.financial_request
        ])
        if high_risk_signals_count >= 3:
            score += 15

        score = max(5, min(98, score))

        # Determine Risk Level
        if signals.credential_request or signals.remote_access_request or score >= 80:
            level = RiskLevel.CRITICAL
            confidence = 0.94
        elif score >= 60:
            level = RiskLevel.HIGH
            confidence = 0.90
        elif score >= 30:
            level = RiskLevel.MEDIUM
            confidence = 0.85
        else:
            level = RiskLevel.LOW
            confidence = 0.88

        return score, level, round(confidence, 2)

    def _extract_tactics_and_requests(
        self,
        signals: DeterministicSignals,
        injection_detected: bool
    ) -> Tuple[List[str], List[str]]:
        tactics = []
        requested_info = []

        if signals.credential_request:
            requested_info.extend(["One-Time Password (OTP)", "Account PIN / Password"])
            tactics.append("Credential Harvesting")
        if signals.remote_access_request:
            requested_info.append("Screen Mirroring / Remote Desktop Access")
            tactics.append("Device Takeover via Remote Software")
        if signals.impersonation:
            tactics.append("Authority / Institutional Impersonation")
        if signals.urgency:
            tactics.append("Fabricated Urgency & Fear-Inducing Deadlines")
        if signals.financial_request:
            requested_info.append("Direct UPI / Bank Fund Transfer")
            tactics.append("Advance-Fee Fraud")
        if signals.social_engineering:
            tactics.append("Psychological Isolation / Coercion")
        if injection_detected:
            tactics.append("Adversarial AI Prompt Override")

        if not tactics:
            tactics.append("Routine Customer Support Dialogue")

        return tactics, requested_info

    def _generate_guidance(self, level: RiskLevel, signals: DeterministicSignals) -> Tuple[List[str], List[str]]:
        actions = []
        do_not_dos = []

        if level in (RiskLevel.CRITICAL, RiskLevel.HIGH):
            actions.append("Disconnect the call immediately.")
            if signals.credential_request:
                actions.append("If you already shared an OTP or password, call your bank's official 24x7 fraud helpline right away.")
                do_not_dos.append("NEVER share any OTP, UPI PIN, or password with anyone, even if they claim to be a bank official.")
            if signals.remote_access_request:
                actions.append("Uninstall any remote access apps (AnyDesk, TeamViewer, QuickSupport) if installed during the call.")
                do_not_dos.append("Do NOT install apps or click links sent via SMS, WhatsApp, or email.")
            if signals.financial_request:
                do_not_dos.append("Do NOT send advance fees, registration deposits, or test transactions.")
            actions.append("Report the incident on the National Cyber Crime portal (cybercrime.gov.in or dial 1930).")
        elif level == RiskLevel.MEDIUM:
            actions.append("Do not provide any sensitive details until you independently verify the caller's organization.")
            actions.append("Call the official customer care number listed on the company's verified website or bank card.")
            do_not_dos.append("Do not call back any phone numbers provided directly by the caller.")
        else:
            actions.append("Remain cautious as legitimate callers will never ask for your passwords or OTPs.")
            do_not_dos.append("Never disclose financial credentials over the phone.")

        return actions, do_not_dos

    def _generate_summary_and_explanation(
        self,
        level: RiskLevel,
        score: int,
        signals: DeterministicSignals,
        language: str
    ) -> Tuple[str, str]:
        if level == RiskLevel.CRITICAL:
            summary = "High-severity fraud pattern detected. The caller solicited confidential credentials or device access under urgency."
            explanation = (
                f"Our AI security engine flagged this interaction with an AI Risk Score of {score}/100. "
                "The caller attempted to obtain sensitive banking information (such as an OTP, PIN, or remote device control). "
                "Legitimate institutions (banks, RBI, police, telecom providers) NEVER solicit OTPs or demand remote screen access over the phone."
            )
        elif level == RiskLevel.HIGH:
            summary = "Suspicious activity detected. Multiple high-risk coercion signals were identified."
            explanation = (
                f"Our AI security engine flagged this interaction with an AI Risk Score of {score}/100. "
                "The caller used classic social-engineering tactics including artificial deadlines, threats of account block, "
                "or requests for upfront financial payments."
            )
        elif level == RiskLevel.MEDIUM:
            summary = "Moderate risk. Some suspicious indicators were observed in the conversation."
            explanation = (
                f"Our AI security engine assigned an AI Risk Score of {score}/100. "
                "While direct credential theft was not explicitly detected, the interaction showed elements of pressure or unverified claims."
            )
        else:
            summary = "No immediate scam signals or credential requests were identified."
            explanation = (
                f"Our AI security engine assigned an AI Risk Score of {score}/100. "
                "The interaction appears to be routine communication with no requests for confidential credentials or unverified financial transfers."
            )

        return summary, explanation
