export type RiskTier = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'UNKNOWN';

export interface EvidenceItem {
  category: string;
  severity: 'INFO' | 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  title: string;
  explanation: string;
  quote: string;
  icon?: string;
}

export interface SignalItem {
  category: string;
  indicator: string;
  triggered: boolean;
  quotes: string[];
  weight: number;
}

export interface DeterministicSignals {
  urgency: boolean;
  impersonation: boolean;
  credential_request: boolean;
  financial_request: boolean;
  remote_access_request: boolean;
  social_engineering: boolean;
  signals: SignalItem[];
}

export interface LanguageDetectionResult {
  detected_language: string;
  confidence: number;
  code_mixed: boolean;
  languages: string[];
}

export interface InvestigationResult {
  risk_level: RiskTier;
  risk_score: number;
  confidence: number;
  summary: string;
  evidence: EvidenceItem[];
  tactics_detected: string[];
  requested_information: string[];
  recommended_actions: string[];
  do_not_do: string[];
  explanation: string;
  uncertainties: string[];
  analysis_mode: string;
}

export interface LocalizedExplanation {
  language_code: string;
  language_name: string;
  summary: string;
  explanation: string;
  recommended_actions: string[];
  do_not_do: string[];
  spoken_summary: string;
}

export interface AnalysisResponse {
  transcript: string;
  language_info: LanguageDetectionResult;
  signals: DeterministicSignals;
  investigation: InvestigationResult;
  explanations: Record<string, LocalizedExplanation>;
  processing_stages: string[];
  disclaimer: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  category?: string;
  description: string;
  language: string;
  expected_risk: string;
  has_audio?: boolean;
  transcript: string;
}

export interface HealthStatus {
  status: string;
  service: string;
  version: string;
  gnani_configured: boolean;
  gnani_status: string;
  environment: string;
}
