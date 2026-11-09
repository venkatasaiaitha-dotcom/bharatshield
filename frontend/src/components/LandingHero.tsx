import React, { useState, useRef } from 'react';
import {
  ShieldAlert, ArrowRight, Play, Pause, Lock, AlertTriangle,
  Briefcase, Building2, Landmark, PhoneCall, Volume2, ShieldCheck,
  FileCheck2, Sparkles
} from 'lucide-react';
import type { DemoScenario } from '../types';
import { getDemoAudioUrl } from '../services/api';

interface LandingHeroProps {
  scenarios: DemoScenario[];
  onSelectScenario: (scenario: DemoScenario) => void;
  onStartAnalysis: () => void;
  onOpenHowItWorks: () => void;
}

export const LandingHero: React.FC<LandingHeroProps> = ({
  scenarios,
  onSelectScenario,
  onStartAnalysis,
  onOpenHowItWorks,
}) => {
  const [playingAudioId, setPlayingAudioId] = useState<string | null>(null);
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);

  const handleTogglePlayAudio = (e: React.MouseEvent, scenarioId: string) => {
    e.stopPropagation();

    if (playingAudioId === scenarioId) {
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
      }
      setPlayingAudioId(null);
      return;
    }

    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
    }

    const audioUrl = getDemoAudioUrl(scenarioId);
    const audio = new Audio(audioUrl);
    audioPlayerRef.current = audio;

    audio.onended = () => {
      setPlayingAudioId(null);
    };

    audio.onerror = () => {
      console.warn('Audio playback not ready for this scenario');
      setPlayingAudioId(null);
    };

    audio.play().then(() => {
      setPlayingAudioId(scenarioId);
    }).catch((err) => {
      console.error('Play failed:', err);
      setPlayingAudioId(null);
    });
  };

  return (
    <div className="py-10 sm:py-16 space-y-16">
      {/* Hero Header */}
      <div className="text-center max-w-4xl mx-auto space-y-5">
        <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full border border-cyan-800/60 bg-cyan-950/40 text-cyan-300 text-xs font-semibold shadow-inner">
          <ShieldAlert className="w-3.5 h-3.5 text-cyan-400" />
          <span>India's Multilingual Voice AI Threat Intelligence System</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
        </div>

        <h1 className="text-4xl sm:text-6xl lg:text-7xl font-black tracking-tight text-white leading-tight">
          BharatShield <span className="bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent">Voice</span>
        </h1>

        <p className="text-xl sm:text-2xl font-bold text-slate-200">
          Understand the call. Detect the risk. Protect yourself.
        </p>

        <p className="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto leading-relaxed">
          State-of-the-art voice safety system for Indian citizens. Instantly analyzes calls in
          <span className="text-cyan-300 font-medium"> Telugu, Hindi, English</span>, and code-mixed vernaculars.
          Extracts concrete evidence of urgency, digital arrest extortion, fake KYC, and OTP theft.
        </p>

        {/* Feature Highlights Pills */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
            <Sparkles className="w-3 h-3 text-cyan-400" />
            <span>Gnani AI Vachana (Prisma STT + Timbre TTS)</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
            <ShieldCheck className="w-3 h-3 text-emerald-400" />
            <span>Prompt-Injection Immune</span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-300">
            <FileCheck2 className="w-3 h-3 text-amber-400" />
            <span>National Cyber Crime 1930 Dossier Ready</span>
          </div>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
          <button
            onClick={onStartAnalysis}
            className="flex items-center gap-2.5 px-7 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 via-sky-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold text-sm sm:text-base shadow-xl shadow-cyan-950/60 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <span>Analyze a Conversation</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          <button
            onClick={onOpenHowItWorks}
            className="flex items-center gap-2 px-6 py-3.5 rounded-2xl border border-slate-700 bg-slate-900/80 hover:bg-slate-800 text-slate-200 font-semibold text-sm sm:text-base transition-all"
          >
            <span>How It Works</span>
          </button>
        </div>

        {/* Privacy Note */}
        <div className="flex items-center justify-center gap-2 text-xs text-slate-400 pt-1">
          <Lock className="w-3.5 h-3.5 text-cyan-400" />
          <span>Zero audio persistence: Audio is strictly purged from memory and disk immediately after processing.</span>
        </div>
      </div>

      {/* Demo Scenarios Section */}
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-3 mb-8 pb-4 border-b border-slate-800">
          <div>
            <div className="inline-flex items-center gap-2 text-xs font-bold text-cyan-400 uppercase tracking-wider mb-1">
              <PhoneCall className="w-3.5 h-3.5" />
              <span>Real-World Indian Scam Showcase</span>
            </div>
            <h2 className="text-xl sm:text-2xl font-extrabold text-white">
              Listen &amp; Investigate Live Scenarios
            </h2>
            <p className="text-xs sm:text-sm text-slate-400 mt-1">
              Click <span className="text-cyan-300 font-semibold">"Listen Call"</span> to hear authentic Gnani AI synthesized voice recordings, or click to run full AI investigation:
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {scenarios.map((s) => {
            const isPlaying = playingAudioId === s.id;
            let Icon = Landmark;
            let badgeBg = 'bg-rose-950/70 text-rose-300 border-rose-800/60';

            if (s.id === 'digital_arrest') {
              Icon = ShieldAlert;
              badgeBg = 'bg-rose-950/70 text-rose-300 border-rose-800/60';
            } else if (s.id === 'upi_refund_scam') {
              Icon = AlertTriangle;
              badgeBg = 'bg-red-950/70 text-red-300 border-red-800/60';
            } else if (s.id === 'fake_job_offer') {
              Icon = Briefcase;
              badgeBg = 'bg-amber-950/70 text-amber-300 border-amber-800/60';
            } else if (s.id === 'normal_service_call') {
              Icon = Building2;
              badgeBg = 'bg-emerald-950/70 text-emerald-300 border-emerald-800/60';
            }

            return (
              <div
                key={s.id}
                onClick={() => onSelectScenario(s)}
                className={`group relative flex flex-col justify-between p-6 rounded-3xl border transition-all cursor-pointer shadow-xl ${
                  isPlaying
                    ? 'border-cyan-500 bg-slate-900 shadow-cyan-950/50 scale-[1.02]'
                    : 'border-slate-800/90 bg-slate-900/60 hover:bg-slate-800/70 hover:border-cyan-500/50'
                }`}
              >
                <div className="space-y-4">
                  {/* Category and Severity Pill */}
                  <div className="flex items-center justify-between">
                    <div className="p-2.5 rounded-2xl bg-slate-800 group-hover:bg-cyan-950/80 transition-colors">
                      <Icon className="w-5 h-5 text-cyan-400" />
                    </div>
                    <span className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border ${badgeBg}`}>
                      {s.expected_risk} RISK
                    </span>
                  </div>

                  <div>
                    <h3 className="font-bold text-slate-100 group-hover:text-cyan-300 transition-colors text-base">
                      {s.title}
                    </h3>
                    <p className="text-xs text-slate-400 mt-1 line-clamp-2 leading-relaxed">
                      {s.description}
                    </p>
                  </div>

                  {/* Language and Audio Badge */}
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                      <span>{s.language}</span>
                    </span>

                    {/* Listen Audio Button */}
                    <button
                      type="button"
                      onClick={(e) => handleTogglePlayAudio(e, s.id)}
                      className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all ${
                        isPlaying
                          ? 'bg-cyan-500 text-slate-950 animate-pulse shadow-md shadow-cyan-500/40'
                          : 'bg-slate-800 hover:bg-slate-700 text-cyan-300 border border-slate-700'
                      }`}
                      title={isPlaying ? 'Pause audio' : 'Listen to call voice'}
                    >
                      {isPlaying ? (
                        <>
                          <Pause className="w-3 h-3 fill-current" />
                          <span>Playing</span>
                        </>
                      ) : (
                        <>
                          <Volume2 className="w-3 h-3 text-cyan-400" />
                          <span>Listen Call</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Bottom Trigger Action */}
                <div className="mt-5 pt-3.5 border-t border-slate-800/80 flex items-center justify-between text-xs font-bold text-cyan-400 group-hover:text-cyan-300">
                  <span className="flex items-center gap-1.5">
                    <Play className="w-3 h-3 fill-current" /> Run AI Investigation
                  </span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
