"""
BharatShield Voice - Investigation Service
Orchestrates the entire investigation pipeline:
1. Deterministic signal extraction (verbatim quotes)
2. Language and code-mix detection
3. Defensive AI investigation & risk tier assignment
4. Localized native explanations (English, Telugu, Hindi)
"""

from typing import Optional
from app.analysis.schemas import AnalysisResponse, LanguageDetectionResult
from app.analysis.signal_engine import extract_deterministic_signals
from app.analysis.language_engine import detect_language_and_mixing
from app.analysis.investigation_engine import InvestigationEngine
from app.analysis.multilingual import generate_multilingual_explanations
from app.utils.logging import get_logger

logger = get_logger("investigation_service")


class InvestigationService:
    def __init__(self):
        self.investigation_engine = InvestigationEngine()

    def analyze_transcript(
        self,
        transcript: str,
        hint_language: Optional[str] = "indic-auto"
    ) -> AnalysisResponse:
        """
        Executes complete multi-stage investigation for a transcript.
        """
        clean_text = transcript.strip()
        stages = ["✓ Audio / text received"]

        # Stage 1: Language & Code-Mixing Detection
        language_info = detect_language_and_mixing(clean_text, hint_language or "indic-auto")
        stages.append(f"✓ Language detected: {language_info.detected_language} ({int(language_info.confidence * 100)}%)")

        # Stage 2: Deterministic Scam Signal Extraction
        signals, evidence = extract_deterministic_signals(clean_text)
        triggered_count = len(signals.signals)
        stages.append(f"✓ Scam signals extracted ({triggered_count} indicators flagged)")

        # Stage 3: AI Investigation & Risk Evaluation
        investigation_result = self.investigation_engine.investigate(
            transcript=clean_text,
            signals=signals,
            evidence=evidence,
            language_info=language_info
        )
        stages.append(f"✓ AI investigation complete (Risk Score: {investigation_result.risk_score}/100, Tier: {investigation_result.risk_level.value})")

        # Stage 4: Multilingual Localized Explanations
        explanations = generate_multilingual_explanations(investigation_result)
        stages.append("✓ Multilingual localized guidance generated (EN, TE, HI)")

        return AnalysisResponse(
            transcript=clean_text,
            language_info=language_info,
            signals=signals,
            investigation=investigation_result,
            explanations=explanations,
            processing_stages=stages
        )
