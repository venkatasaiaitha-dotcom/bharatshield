import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LandingHero } from './components/LandingHero';
import { VoiceRecorder } from './components/VoiceRecorder';
import { ProcessingStages } from './components/ProcessingStages';
import { TranscriptViewer } from './components/TranscriptViewer';
import { ResultDashboard } from './components/ResultDashboard';
import { HowItWorksModal } from './components/HowItWorksModal';
import { fetchHealth, fetchDemoScenarios, analyzeTranscript, analyzeAudioFile } from './services/api';
import type { AnalysisResponse, DemoScenario, HealthStatus } from './types';
import { AlertCircle, ArrowLeft } from 'lucide-react';

export function App() {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [view, setView] = useState<'landing' | 'input' | 'result'>('landing');

  // Analysis State
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modal State
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);

  // Initial load
  useEffect(() => {
    fetchHealth()
      .then(setHealth)
      .catch((err) => console.warn('Backend health check warning:', err));

    fetchDemoScenarios()
      .then(setScenarios)
      .catch((err) => console.warn('Failed to load demo scenarios:', err));
  }, []);

  // Handle Demo Scenario Selection (Runs real pipeline!)
  const handleSelectScenario = async (scenario: DemoScenario) => {
    setErrorMessage(null);
    setIsLoading(true);
    setLoadingStep(0);
    setView('input');

    try {
      const result = await analyzeTranscript(scenario.transcript);
      setAnalysisResult(result);
      setView('result');
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to analyze scenario');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Audio Analysis (File or Mic Recording)
  const handleAnalyzeAudio = async (file: File | Blob, filename: string) => {
    setErrorMessage(null);
    setIsLoading(true);
    setLoadingStep(0);

    try {
      const result = await analyzeAudioFile(file, filename);
      setAnalysisResult(result);
      setView('result');
    } catch (err: any) {
      setErrorMessage(err.message || 'Audio analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Text Transcript Submission
  const handleAnalyzeText = async (text: string) => {
    setErrorMessage(null);
    setIsLoading(true);
    setLoadingStep(0);

    try {
      const result = await analyzeTranscript(text);
      setAnalysisResult(result);
      setView('result');
    } catch (err: any) {
      setErrorMessage(err.message || 'Analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Transcript Edit & Re-analysis
  const handleUpdateTranscript = async (newText: string) => {
    setErrorMessage(null);
    setIsLoading(true);
    try {
      const result = await analyzeTranscript(newText);
      setAnalysisResult(result);
    } catch (err: any) {
      setErrorMessage(err.message || 'Re-analysis failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset to landing
  const handleReset = () => {
    setAnalysisResult(null);
    setErrorMessage(null);
    setIsLoading(false);
    setView('landing');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-cyan-500 selection:text-slate-950">
      <Navbar
        health={health}
        onReset={handleReset}
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        {/* Error Notification Banner */}
        {errorMessage && (
          <div className="max-w-3xl mx-auto mb-6 p-4 rounded-2xl bg-rose-950/60 border border-rose-800 text-rose-200 flex items-start gap-3 shadow-lg">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1 text-xs sm:text-sm">
              <p className="font-semibold text-rose-300">Action Required</p>
              <p className="mt-0.5">{errorMessage}</p>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="text-xs text-rose-400 hover:text-white px-2 py-1 rounded-lg border border-rose-800/80"
            >
              Dismiss
            </button>
          </div>
        )}

        {/* View 1: Landing Page */}
        {view === 'landing' && (
          <LandingHero
            scenarios={scenarios}
            onSelectScenario={handleSelectScenario}
            onStartAnalysis={() => setView('input')}
            onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
          />
        )}

        {/* View 2: Audio Recording & Upload Screen */}
        {view === 'input' && (
          <div className="py-6 space-y-6">
            <div className="max-w-3xl mx-auto flex items-center justify-between">
              <button
                onClick={() => setView('landing')}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Back to Home
              </button>
              <span className="text-xs text-cyan-400 font-semibold uppercase tracking-wider">
                Conversation Input
              </span>
            </div>

            {isLoading ? (
              <ProcessingStages currentStageIndex={loadingStep} />
            ) : (
              <VoiceRecorder
                onAnalyzeAudio={handleAnalyzeAudio}
                onAnalyzeText={handleAnalyzeText}
                isLoading={isLoading}
              />
            )}
          </div>
        )}

        {/* View 3: Results Dashboard */}
        {view === 'result' && analysisResult && (
          <div className="py-6 space-y-6">
            <div className="max-w-5xl mx-auto flex items-center justify-between">
              <button
                onClick={() => setView('input')}
                className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
              >
                <ArrowLeft className="w-3.5 h-3.5" /> Analyze Another Audio
              </button>
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span className="text-xs text-emerald-400 font-medium">Analysis Completed</span>
              </div>
            </div>

            {/* Transcript Viewer with Edit Option */}
            <div className="max-w-5xl mx-auto">
              <TranscriptViewer
                transcript={analysisResult.transcript}
                languageInfo={analysisResult.language_info}
                onUpdateTranscript={handleUpdateTranscript}
              />
            </div>

            {/* Main Result Cards & Localized Explanation */}
            <ResultDashboard
              data={analysisResult}
              onReset={handleReset}
            />
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950 py-6 mt-12 text-center text-xs text-slate-400 space-y-2">
        <p className="font-medium text-slate-300">
          BharatShield Voice — Multilingual Voice AI Safety MVP
        </p>
        <p className="text-slate-400">
          Developed by{' '}
          <a
            href="https://www.linkedin.com/in/aitha-venkata-sai-3b128736b"
            target="_blank"
            rel="noopener noreferrer"
            className="text-cyan-400 hover:text-cyan-300 font-medium underline underline-offset-2 transition-colors"
          >
            Aitha Venkata Sai
          </a>
        </p>
        <p className="text-[11px] text-slate-400">
          AI Risk Score is an assistive security tool and not a replacement for official bank or police consultation.
        </p>
      </footer>

      {/* How It Works Modal */}
      <HowItWorksModal
        isOpen={isHowItWorksOpen}
        onClose={() => setIsHowItWorksOpen(false)}
      />
    </div>
  );
}

export default App;
