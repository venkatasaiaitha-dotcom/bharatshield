import React, { useState, useRef } from 'react';
import {
  ShieldAlert, ShieldCheck, AlertTriangle, AlertOctagon, HelpCircle,
  Volume2, Pause, Square, CheckCircle2, XCircle, Quote,
  Key, Clock, UserX, CreditCard, Download, RefreshCw, FileText,
  PhoneCall, Copy, Check, ExternalLink, Shield
} from 'lucide-react';
import type { AnalysisResponse, RiskTier } from '../types';
import { requestSpeechSynthesis, generateIncidentReport } from '../services/api';

interface ResultDashboardProps {
  data: AnalysisResponse;
  onReset: () => void;
}

export const ResultDashboard: React.FC<ResultDashboardProps> = ({ data, onReset }) => {
  const [selectedLang, setSelectedLang] = useState<'en' | 'te' | 'hi'>('en');
  const [isPlayingAudio, setIsPlayingAudio] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [copiedQuote, setCopiedQuote] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [reportSuccess, setReportSuccess] = useState(false);

  const audioRef = useRef<HTMLAudioElement | null>(null);
  const speechSynthUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null);

  const { investigation, explanations, signals } = data;
  const currentExplanation = explanations[selectedLang] || explanations['en'];

  // Risk styling configuration
  const getRiskConfig = (tier: RiskTier) => {
    switch (tier) {
      case 'CRITICAL':
        return {
          label: 'CRITICAL RISK',
          subLabel: 'Immediate Coercion or Credential Theft Flagged',
          badgeBg: 'bg-rose-950/80 text-rose-300 border-rose-800',
          gradient: 'from-rose-950/90 via-red-950/50 to-slate-950',
          barColor: 'bg-rose-500',
          textColor: 'text-rose-400',
          borderColor: 'border-rose-800/80',
          glow: 'glow-danger',
          icon: AlertOctagon,
        };
      case 'HIGH':
        return {
          label: 'HIGH RISK',
          subLabel: 'Strong Social Engineering Indicators Identified',
          badgeBg: 'bg-orange-950/80 text-orange-300 border-orange-800',
          gradient: 'from-orange-950/90 via-amber-950/50 to-slate-950',
          barColor: 'bg-orange-500',
          textColor: 'text-orange-400',
          borderColor: 'border-orange-800/80',
          glow: 'glow-danger',
          icon: ShieldAlert,
        };
      case 'MEDIUM':
        return {
          label: 'MEDIUM RISK',
          subLabel: 'Suspicious Behavior & Unverified Pressure',
          badgeBg: 'bg-amber-950/80 text-amber-300 border-amber-800',
          gradient: 'from-amber-950/90 via-yellow-950/40 to-slate-950',
          barColor: 'bg-amber-500',
          textColor: 'text-amber-400',
          borderColor: 'border-amber-800/80',
          glow: '',
          icon: AlertTriangle,
        };
      case 'LOW':
        return {
          label: 'LOW RISK',
          subLabel: 'Routine Communication — No Scam Patterns',
          badgeBg: 'bg-emerald-950/80 text-emerald-300 border-emerald-800',
          gradient: 'from-emerald-950/90 via-teal-950/40 to-slate-950',
          barColor: 'bg-emerald-500',
          textColor: 'text-emerald-400',
          borderColor: 'border-emerald-800/80',
          glow: 'glow-success',
          icon: ShieldCheck,
        };
      default:
        return {
          label: 'UNKNOWN RISK',
          subLabel: 'Insufficient Dialogue or Audio Context',
          badgeBg: 'bg-slate-800 text-slate-300 border-slate-700',
          gradient: 'from-slate-900 to-slate-950',
          barColor: 'bg-slate-500',
          textColor: 'text-slate-400',
          borderColor: 'border-slate-800',
          glow: '',
          icon: HelpCircle,
        };
    }
  };

  const riskCfg = getRiskConfig(investigation.risk_level);
  const RiskIcon = riskCfg.icon;

  const getCategoryIcon = (category: string) => {
    const c = category.toLowerCase();
    if (c.includes('credential') || c.includes('otp') || c.includes('pin')) return Key;
    if (c.includes('urgency') || c.includes('time')) return Clock;
    if (c.includes('impersonat') || c.includes('officer') || c.includes('bank')) return UserX;
    if (c.includes('financial') || c.includes('fee') || c.includes('money')) return CreditCard;
    if (c.includes('remote') || c.includes('app') || c.includes('software')) return Download;
    return ShieldAlert;
  };

  // Audio Playback
  const handlePlayVoiceExplanation = async () => {
    if (isPlayingAudio) {
      handleStopVoice();
      return;
    }

    const spokenText = currentExplanation?.spoken_summary || currentExplanation?.explanation;
    if (!spokenText) return;

    setAudioLoading(true);

    try {
      const langMap: Record<string, string> = { en: 'en-IN', te: 'te-IN', hi: 'hi-IN' };
      const audioBlob = await requestSpeechSynthesis(spokenText, langMap[selectedLang]);

      if (audioBlob) {
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = new Audio(audioUrl);
        audio.playbackRate = playbackSpeed;
        audioRef.current = audio;

        audio.onended = () => {
          setIsPlayingAudio(false);
          URL.revokeObjectURL(audioUrl);
        };

        await audio.play();
        setIsPlayingAudio(true);
      } else {
        if ('speechSynthesis' in window) {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(spokenText);
          utterance.lang = selectedLang === 'te' ? 'te-IN' : selectedLang === 'hi' ? 'hi-IN' : 'en-IN';
          utterance.rate = playbackSpeed;

          utterance.onend = () => setIsPlayingAudio(false);
          utterance.onerror = () => setIsPlayingAudio(false);

          speechSynthUtteranceRef.current = utterance;
          window.speechSynthesis.speak(utterance);
          setIsPlayingAudio(true);
        }
      }
    } catch (e) {
      console.error('Voice playback error:', e);
    } finally {
      setAudioLoading(false);
    }
  };

  const handleStopVoice = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlayingAudio(false);
  };

  const handleCopyQuote = (quote: string) => {
    navigator.clipboard.writeText(quote);
    setCopiedQuote(quote);
    setTimeout(() => setCopiedQuote(null), 2000);
  };

  // Download Formal Cyber Crime Dossier
  const handleDownloadDossier = async () => {
    setIsGeneratingReport(true);
    try {
      const reportContent = await generateIncidentReport(data.transcript);
      const blob = new Blob([reportContent], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `BharatShield_CyberCrime_Incident_Report_${Date.now()}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      setReportSuccess(true);
      setTimeout(() => setReportSuccess(false), 3000);
    } catch (err) {
      console.error('Report download failed:', err);
    } finally {
      setIsGeneratingReport(false);
    }
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* 1. Main Risk Header Banner */}
      <div className={`p-6 sm:p-8 rounded-3xl border ${riskCfg.borderColor} bg-gradient-to-br ${riskCfg.gradient} shadow-2xl relative overflow-hidden`}>
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-2xl bg-slate-950/80 border border-slate-800 ${riskCfg.textColor}`}>
                <RiskIcon className="w-8 h-8" />
              </div>
              <div>
                <span className={`inline-block text-xs font-black uppercase px-3 py-1 rounded-full border ${riskCfg.badgeBg} tracking-wide`}>
                  {riskCfg.label}
                </span>
                <p className="text-sm font-bold text-slate-200 mt-1">
                  {riskCfg.subLabel}
                </p>
              </div>
            </div>

            <p className="text-xs text-slate-400">
              Evaluation Model: <span className="font-semibold text-slate-200">Defensive AI Reasoning &amp; Deterministic Signal Verification</span>
            </p>
          </div>

          {/* AI Risk Score Gauge */}
          <div className="flex flex-col sm:items-end justify-center p-5 rounded-2xl bg-slate-950/90 border border-slate-800 min-w-[220px]">
            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">
              AI Risk Assessment Score
            </span>
            <div className="flex items-baseline gap-1 mt-1">
              <span className={`text-4xl sm:text-5xl font-black font-mono ${riskCfg.textColor}`}>
                {investigation.risk_score}
              </span>
              <span className="text-slate-400 font-semibold text-sm">/ 100</span>
            </div>
            <div className="w-full bg-slate-800 h-2 rounded-full mt-2.5 overflow-hidden">
              <div
                className={`h-full ${riskCfg.barColor} transition-all duration-700`}
                style={{ width: `${investigation.risk_score}%` }}
              />
            </div>
            <span className="text-[10px] text-slate-400 mt-1.5">
              Confidence Rating: {Math.round(investigation.confidence * 100)}%
            </span>
          </div>
        </div>

        {/* Threat Dimensions Breakdown */}
        <div className="mt-6 pt-5 border-t border-slate-800/80 grid grid-cols-2 sm:grid-cols-5 gap-3 text-center">
          <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Credential Theft</span>
            <p className={`text-xs font-bold mt-0.5 ${signals.credential_request ? 'text-rose-400' : 'text-emerald-400'}`}>
              {signals.credential_request ? 'HIGH RISK' : 'CLEAR'}
            </p>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Impersonation</span>
            <p className={`text-xs font-bold mt-0.5 ${signals.impersonation ? 'text-orange-400' : 'text-emerald-400'}`}>
              {signals.impersonation ? 'DETECTED' : 'CLEAR'}
            </p>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Urgency Pressure</span>
            <p className={`text-xs font-bold mt-0.5 ${signals.urgency ? 'text-amber-400' : 'text-emerald-400'}`}>
              {signals.urgency ? 'DETECTED' : 'CLEAR'}
            </p>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Remote Access</span>
            <p className={`text-xs font-bold mt-0.5 ${signals.remote_access_request ? 'text-rose-400' : 'text-emerald-400'}`}>
              {signals.remote_access_request ? 'CRITICAL' : 'CLEAR'}
            </p>
          </div>

          <div className="p-2 rounded-xl bg-slate-950/50 border border-slate-800/60 col-span-2 sm:col-span-1">
            <span className="text-[10px] text-slate-400 uppercase font-semibold">Financial Loss</span>
            <p className={`text-xs font-bold mt-0.5 ${signals.financial_request ? 'text-rose-400' : 'text-emerald-400'}`}>
              {signals.financial_request ? 'HIGH RISK' : 'CLEAR'}
            </p>
          </div>
        </div>
      </div>

      {/* 2. Multilingual Voice Guidance Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900 border border-slate-800">
        {/* Language Tabs */}
        <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-950 border border-slate-800">
          <span className="text-xs text-slate-400 px-2 font-medium">Guidance Language:</span>
          {(['en', 'te', 'hi'] as const).map((lang) => {
            const labels = { en: 'English', te: 'తెలుగు', hi: 'हिन्दी' };
            const isActive = selectedLang === lang;
            return (
              <button
                key={lang}
                onClick={() => {
                  setSelectedLang(lang);
                  handleStopVoice();
                }}
                className={`px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  isActive
                    ? 'bg-cyan-600 text-white shadow-md shadow-cyan-950'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                {labels[lang]}
              </button>
            );
          })}
        </div>

        {/* Audio Player Controls */}
        <div className="flex items-center gap-2">
          <button
            onClick={handlePlayVoiceExplanation}
            disabled={audioLoading}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white text-xs font-bold shadow-md shadow-cyan-950 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            {audioLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin text-white" />
            ) : isPlayingAudio ? (
              <Pause className="w-3.5 h-3.5 fill-current" />
            ) : (
              <Volume2 className="w-3.5 h-3.5" />
            )}
            <span>{isPlayingAudio ? 'Pause Voice' : '🔊 Explain this to me'}</span>
          </button>

          {isPlayingAudio && (
            <button
              onClick={handleStopVoice}
              className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 transition-colors"
              title="Stop Audio"
            >
              <Square className="w-3.5 h-3.5 fill-current" />
            </button>
          )}

          {/* Speed Selector */}
          <select
            value={playbackSpeed}
            onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
            className="bg-slate-950 border border-slate-800 text-slate-300 text-xs px-2 py-1.5 rounded-xl focus:outline-none"
          >
            <option value="0.85">0.85x</option>
            <option value="1.0">1.0x</option>
            <option value="1.15">1.15x</option>
          </select>

          <button
            onClick={onReset}
            className="flex items-center gap-1.5 px-3 py-2 rounded-xl border border-slate-800 text-slate-400 hover:text-slate-200 text-xs font-medium transition-colors"
          >
            <RefreshCw className="w-3 h-3" /> New Analysis
          </button>
        </div>
      </div>

      {/* 3. Executive Summary Card */}
      <div className="p-6 rounded-3xl bg-slate-900/70 border border-slate-800 space-y-3 shadow-lg">
        <div className="flex items-center justify-between">
          <h3 className="text-xs font-black uppercase tracking-wider text-cyan-400 flex items-center gap-2">
            <Shield className="w-4 h-4 text-cyan-400" />
            <span>AI Safety Assessment Summary</span>
          </h3>
          <span className="text-[11px] text-slate-400">
            Localized for: {selectedLang === 'te' ? 'తెలుగు (Telugu)' : selectedLang === 'hi' ? 'हिन्दी (Hindi)' : 'English'}
          </span>
        </div>
        <p className="text-sm sm:text-base text-slate-100 font-semibold leading-relaxed">
          {currentExplanation?.summary}
        </p>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pt-1">
          {currentExplanation?.explanation}
        </p>
      </div>

      {/* 4. Why We Flagged This - Verified Concrete Evidence */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-extrabold uppercase tracking-wider text-slate-200 flex items-center gap-2">
            <span>Why we flagged this ({investigation.evidence.length} concrete signals)</span>
          </h3>
          <span className="text-[11px] text-cyan-400 font-mono">100% Verbatim Transcript Quotes</span>
        </div>

        {investigation.evidence.length === 0 ? (
          <div className="p-6 rounded-2xl bg-slate-900/40 border border-slate-800 text-center text-xs text-slate-400">
            No malicious scam patterns or credential requests were found in the conversation.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {investigation.evidence.map((ev, index) => {
              const IconComponent = getCategoryIcon(ev.category);
              let badgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
              if (ev.severity === 'CRITICAL') {
                badgeColor = 'bg-rose-950/80 text-rose-300 border-rose-800';
              } else if (ev.severity === 'HIGH') {
                badgeColor = 'bg-orange-950/80 text-orange-300 border-orange-800';
              } else if (ev.severity === 'MEDIUM') {
                badgeColor = 'bg-amber-950/80 text-amber-300 border-amber-800';
              }

              return (
                <div
                  key={index}
                  className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col justify-between space-y-3.5 hover:border-slate-700 transition-colors"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="p-2 rounded-xl bg-slate-800 text-cyan-400">
                          <IconComponent className="w-4 h-4" />
                        </div>
                        <h4 className="font-bold text-slate-200 text-sm">
                          {ev.title}
                        </h4>
                      </div>
                      <span className={`text-[10px] font-black uppercase px-2.5 py-0.5 rounded-full border ${badgeColor}`}>
                        {ev.severity}
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      {ev.explanation}
                    </p>
                  </div>

                  {/* Supporting Verbatim Quote with Copy Action */}
                  {ev.quote && (
                    <div className="pt-2 border-t border-slate-800/80 flex items-start justify-between gap-2 bg-slate-950/80 p-3 rounded-xl border border-slate-800/70">
                      <div className="flex items-start gap-2">
                        <Quote className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        <p className="text-xs font-mono text-cyan-200/90 italic">
                          "{ev.quote}"
                        </p>
                      </div>
                      <button
                        onClick={() => handleCopyQuote(ev.quote)}
                        className="p-1 rounded text-slate-500 hover:text-slate-300 transition-colors shrink-0"
                        title="Copy quote"
                      >
                        {copiedQuote === ev.quote ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* 5. Recommended Actions & Critical Avoidances */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Recommended Actions */}
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-emerald-900/50 space-y-3 shadow-lg">
          <h4 className="font-extrabold text-emerald-400 text-xs uppercase tracking-wider flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>Recommended Actions</span>
          </h4>
          <ul className="space-y-2.5 text-xs sm:text-sm text-slate-300">
            {currentExplanation.recommended_actions.map((act, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="w-4 h-4 rounded-full bg-emerald-950 border border-emerald-800 text-emerald-300 text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                  {i + 1}
                </span>
                <span>{act}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Avoid */}
        <div className="p-6 rounded-3xl bg-slate-900/90 border border-rose-900/50 space-y-3 shadow-lg">
          <h4 className="font-extrabold text-rose-400 text-xs uppercase tracking-wider flex items-center gap-2">
            <XCircle className="w-4 h-4 text-rose-400" />
            <span>Critical Actions to Avoid</span>
          </h4>
          <ul className="space-y-2.5 text-xs sm:text-sm text-slate-300">
            {currentExplanation.do_not_do.map((dont, i) => (
              <li key={i} className="flex items-start gap-2.5">
                <span className="w-4 h-4 rounded-full bg-rose-950 border border-rose-800 text-rose-300 text-[10px] font-black flex items-center justify-center shrink-0 mt-0.5">
                  ✕
                </span>
                <span>{dont}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* 6. Emergency 1930 Cyber Crime & Bank Directory */}
      <div className="p-6 rounded-3xl bg-slate-900/90 border border-cyan-900/50 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h4 className="text-sm font-extrabold text-white flex items-center gap-2">
              <PhoneCall className="w-4 h-4 text-cyan-400" />
              <span>Official Indian Cyber Crime &amp; Bank Fraud Helplines</span>
            </h4>
            <p className="text-xs text-slate-400 mt-0.5">
              If you shared any credentials or transferred funds, report immediately within the golden hour:
            </p>
          </div>

          {/* Download Official Dossier Button */}
          <button
            onClick={handleDownloadDossier}
            disabled={isGeneratingReport}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-bold text-xs shadow-md shadow-cyan-950 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 shrink-0"
          >
            {isGeneratingReport ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : reportSuccess ? (
              <Check className="w-3.5 h-3.5 text-white" />
            ) : (
              <FileText className="w-3.5 h-3.5" />
            )}
            <span>{reportSuccess ? 'Dossier Downloaded!' : 'Download Official 1930 Dossier'}</span>
          </button>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2">
          <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] text-cyan-400 font-bold uppercase">National Cyber Helpline</span>
            <p className="text-base font-black text-white mt-0.5">Dial 1930</p>
            <span className="text-[10px] text-slate-400">Toll-Free 24x7</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase">SBI Fraud Helpline</span>
            <p className="text-xs font-black text-white mt-0.5">1800 11 1109</p>
            <span className="text-[10px] text-slate-400">Card &amp; NetBanking</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-center">
            <span className="text-[10px] text-slate-400 font-bold uppercase">HDFC / ICICI Fraud</span>
            <p className="text-xs font-black text-white mt-0.5">1800 258 3838</p>
            <span className="text-[10px] text-slate-400">Emergency Hotlines</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-950 border border-slate-800 text-center flex flex-col justify-center">
            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center justify-center gap-1"
            >
              <span>cybercrime.gov.in</span>
              <ExternalLink className="w-3 h-3" />
            </a>
            <span className="text-[10px] text-slate-400">File Online Complaint</span>
          </div>
        </div>
      </div>

      {/* 7. Disclaimer */}
      <div className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 text-center">
        <p className="text-[11px] text-slate-400 leading-relaxed">
          {data.disclaimer}
        </p>
      </div>
    </div>
  );
};
