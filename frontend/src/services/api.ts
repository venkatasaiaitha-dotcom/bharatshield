import type { AnalysisResponse, DemoScenario, HealthStatus } from '../types';

export async function fetchHealth(): Promise<HealthStatus> {
  const res = await fetch('/health');
  if (!res.ok) {
    throw new Error(`Health check failed with HTTP ${res.status}`);
  }
  return res.json();
}

export async function fetchDemoScenarios(): Promise<DemoScenario[]> {
  const res = await fetch('/api/demo/scenarios');
  if (!res.ok) {
    throw new Error('Failed to load demo scenarios');
  }
  const data = await res.json();
  return data.scenarios;
}

export function getDemoAudioUrl(scenarioId: string): string {
  return `/api/demo/audio/${scenarioId}`;
}

export async function analyzeTranscript(transcript: string, languageCode = 'indic-auto'): Promise<AnalysisResponse> {
  const res = await fetch('/api/investigate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      transcript,
      language_code: languageCode,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(errorData.detail || errorData.message || `Analysis failed (${res.status})`);
  }

  return res.json();
}

export async function transcribeAudioFile(file: File | Blob, filename = 'recording.wav'): Promise<{ transcript: string; language_info: any }> {
  const formData = new FormData();
  formData.append('audio', file, filename);
  formData.append('language_hint', 'indic-auto');

  const res = await fetch('/api/transcribe', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Transcription failed' }));
    throw new Error(errorData.detail || errorData.message || `Transcription failed (${res.status})`);
  }

  return res.json();
}

export async function analyzeAudioFile(file: File | Blob, filename = 'recording.wav'): Promise<AnalysisResponse> {
  const formData = new FormData();
  formData.append('audio', file, filename);
  formData.append('language_hint', 'indic-auto');

  const res = await fetch('/api/analyze', {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Audio analysis failed' }));
    throw new Error(errorData.detail || errorData.message || `Audio analysis failed (${res.status})`);
  }

  return res.json();
}

export async function requestSpeechSynthesis(text: string, language = 'te-IN'): Promise<Blob | null> {
  try {
    const res = await fetch('/api/speech', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, language }),
    });

    if (res.status === 204 || !res.ok) {
      return null;
    }

    return await res.blob();
  } catch {
    return null;
  }
}

export async function generateIncidentReport(transcript: string, languageCode = 'indic-auto'): Promise<string> {
  const res = await fetch('/api/report/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ transcript, language_code: languageCode }),
  });
  if (!res.ok) {
    throw new Error('Failed to generate incident report');
  }
  return res.text();
}
