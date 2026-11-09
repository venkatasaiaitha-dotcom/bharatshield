import React from 'react';
import { Shield, Activity, Radio, CheckCircle2, AlertCircle } from 'lucide-react';
import type { HealthStatus } from '../types';

interface NavbarProps {
  health: HealthStatus | null;
  onReset: () => void;
  onOpenHowItWorks: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ health, onReset, onOpenHowItWorks }) => {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <button
          onClick={onReset}
          className="flex items-center gap-3 group text-left transition-transform hover:scale-[1.01]"
        >
          <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-sky-500 to-indigo-600 shadow-md shadow-sky-500/20">
            <Shield className="w-5 h-5 text-white" />
            <Activity className="w-3.5 h-3.5 text-cyan-200 absolute -bottom-0.5 -right-0.5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-lg tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                BharatShield <span className="text-cyan-400 font-extrabold">Voice</span>
              </span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-cyan-950/80 text-cyan-400 border border-cyan-800/50">
                AI Safety
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">
              Understand the call. Detect the risk. Protect yourself.
            </p>
          </div>
        </button>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          <button
            onClick={onOpenHowItWorks}
            className="text-xs sm:text-sm font-medium text-slate-300 hover:text-white px-3 py-1.5 rounded-lg hover:bg-slate-800/60 transition-colors"
          >
            How It Works
          </button>

          {/* Backend / Gnani Status Indicator */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-slate-800 bg-slate-900/90 text-xs">
            <Radio className="w-3.5 h-3.5 text-cyan-400 animate-pulse" />
            <span className="text-slate-400 hidden sm:inline">Gnani AI:</span>
            {health?.gnani_configured ? (
              <span className="flex items-center gap-1 text-emerald-400 font-medium">
                <CheckCircle2 className="w-3 h-3" /> Ready
              </span>
            ) : (
              <span className="flex items-center gap-1 text-amber-400 font-medium">
                <AlertCircle className="w-3 h-3" /> Standby
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
