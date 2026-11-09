import React from 'react';
import { X, ShieldCheck, Cpu, Mic, FileText, Globe2, Volume2, Lock } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HowItWorksModal: React.FC<HowItWorksModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const steps = [
    {
      icon: Mic,
      title: '1. Voice Input & Validation',
      desc: 'Users record or upload conversation audio. The backend validates headers, sizes, and formats to reject malformed files.',
    },
    {
      icon: Cpu,
      title: '2. Gnani Speech Processing',
      desc: 'Multilingual speech is transcribed using Gnani AI (Vachana Prisma series) supporting English, Telugu, Hindi, and regional dialects.',
    },
    {
      icon: Globe2,
      title: '3. Language & Code-Mix Analysis',
      desc: 'Lexical analysis detects mixed language patterns (e.g. Telugu + English or Hindi + English) rather than confusing loan words.',
    },
    {
      icon: FileText,
      title: '4. Deterministic Signal Extraction',
      desc: 'Before AI reasoning, verified signals (urgency, OTP requests, bank/police impersonation) and verbatim quotes are extracted.',
    },
    {
      icon: ShieldCheck,
      title: '5. Defensive AI Investigation',
      desc: 'An AI safety engine investigates the pattern with strict prompt injection immunity, assigning an AI Risk Score and safety tier.',
    },
    {
      icon: Volume2,
      title: '6. Localized Spoken Guidance',
      desc: 'Explanations and spoken voice responses are rendered in natural colloquial Telugu, Hindi, or English for everyday citizens.',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="relative w-full max-w-2xl rounded-3xl border border-slate-800 bg-slate-900 p-6 sm:p-8 shadow-2xl space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-6 h-6 text-cyan-400" />
            <h2 className="text-lg font-bold text-slate-100">
              How BharatShield Voice Works
            </h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[60vh] overflow-y-auto pr-1">
          {steps.map((st, i) => {
            const Icon = st.icon;
            return (
              <div key={i} className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 space-y-2">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-cyan-950/80 text-cyan-400 border border-cyan-800/40">
                    <Icon className="w-4 h-4" />
                  </div>
                  <h3 className="text-xs font-bold text-slate-200">{st.title}</h3>
                </div>
                <p className="text-xs text-slate-400 leading-relaxed">{st.desc}</p>
              </div>
            );
          })}
        </div>

        <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <Lock className="w-3.5 h-3.5 text-cyan-400" />
            <span>Strict privacy: Temporary audio is purged immediately after processing.</span>
          </div>

          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs transition-colors shadow-md shadow-cyan-950"
          >
            Got It
          </button>
        </div>
      </div>
    </div>
  );
};
