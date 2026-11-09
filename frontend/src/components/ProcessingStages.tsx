import React, { useEffect, useState } from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

interface ProcessingStagesProps {
  currentStageIndex: number;
}

const STAGES = [
  'Audio received & validated',
  'Gnani speech processing & Indic transcription',
  'Language & code-mix detection',
  'Scam signal engine extraction',
  'Defensive AI investigation & risk tiering',
  'Generating multilingual localized guidance',
];

export const ProcessingStages: React.FC<ProcessingStagesProps> = ({ currentStageIndex }) => {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    // Automatically advance steps smoothly to show live pipeline telemetry
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev < STAGES.length - 1 ? prev + 1 : prev));
    }, 700);

    return () => clearInterval(interval);
  }, []);

  const displayStep = Math.max(activeStep, currentStageIndex);

  return (
    <div className="max-w-xl mx-auto my-8 p-6 rounded-2xl border border-cyan-800/50 bg-slate-900/90 backdrop-blur-md shadow-2xl space-y-4">
      <div className="flex items-center gap-2 pb-2 border-b border-slate-800 text-sm font-bold text-cyan-400">
        <Loader2 className="w-4 h-4 animate-spin text-cyan-400" />
        <span>BharatShield Voice Pipeline Active</span>
      </div>

      <div className="space-y-3">
        {STAGES.map((label, idx) => {
          const isDone = idx < displayStep;
          const isCurrent = idx === displayStep;

          return (
            <div
              key={label}
              className={`flex items-center gap-3 text-xs sm:text-sm transition-all duration-300 ${
                isDone
                  ? 'text-emerald-400 font-medium'
                  : isCurrent
                  ? 'text-cyan-300 font-semibold'
                  : 'text-slate-400'
              }`}
            >
              {isDone ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
              ) : isCurrent ? (
                <Loader2 className="w-4 h-4 animate-spin text-cyan-400 shrink-0" />
              ) : (
                <Circle className="w-4 h-4 text-slate-700 shrink-0" />
              )}
              <span>{label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
