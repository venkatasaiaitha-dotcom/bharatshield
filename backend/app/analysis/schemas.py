"""
BharatShield Voice - Analysis Schemas and Models
Defines strictly validated data models for risk levels, evidence, signals, and investigation outputs.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class EvidenceItem(BaseModel):
    category: str = Field(description="Category e.g. Credential Request, Urgency, Impersonation")
    severity: Severity = Field(default=Severity.MEDIUM)
    title: str = Field(description="Short concise title e.g. OTP Request")
    explanation: str = Field(description="Clear explanation of why this was flagged")
    quote: str = Field(description="Direct verbatim quote from transcript")
    icon: Optional[str] = Field(default="alert-triangle")


class SignalItem(BaseModel):
    category: str
    indicator: str
    triggered: bool
    quotes: List[str] = Field(default_factory=list)
    weight: float = 0.0


class DeterministicSignals(BaseModel):
    urgency: bool = False
    impersonation: bool = False
    credential_request: bool = False
    financial_request: bool = False
    remote_access_request: bool = False
    social_engineering: bool = False
    signals: List[SignalItem] = Field(default_factory=list)


class InvestigationResult(BaseModel):
    risk_level: RiskLevel = Field(description="Calculated risk tier")
    risk_score: int = Field(ge=0, le=100, description="Risk score 0-100")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in assessment 0.0 - 1.0")
    summary: str = Field(description="Concise executive summary of what transpired")
    evidence: List[EvidenceItem] = Field(default_factory=list)
    tactics_detected: List[str] = Field(default_factory=list)
    requested_information: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    do_not_do: List[str] = Field(default_factory=list)
    explanation: str = Field(description="Clear, non-technical explanation for everyday users")
    uncertainties: List[str] = Field(default_factory=list)
    analysis_mode: str = Field(default="ai_investigation", description="'ai_investigation' or 'rule_based_fallback'")

    @field_validator("risk_score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        return max(0, min(100, v))


class LanguageDetectionResult(BaseModel):
    detected_language: str
    confidence: float
    code_mixed: bool = False
    languages: List[str] = Field(default_factory=list)


class LocalizedExplanation(BaseModel):
    language_code: str
    language_name: str
    summary: str
    explanation: str
    recommended_actions: List[str]
    do_not_do: List[str]
    spoken_summary: str


class AnalysisResponse(BaseModel):
    transcript: str
    language_info: LanguageDetectionResult
    signals: DeterministicSignals
    investigation: InvestigationResult
    explanations: Dict[str, LocalizedExplanation]
    processing_stages: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "AI-generated assessment. This result is based only on the available information "
        "and is not a guarantee that an interaction is fraudulent or legitimate."
    )


class TranscriptAnalysisRequest(BaseModel):
    transcript: str = Field(..., min_length=3, max_length=15000)
    language_code: Optional[str] = "indic-auto"
    user_context: Optional[str] = None


class SpeechSynthesisRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    language: str = Field(default="te-IN")
