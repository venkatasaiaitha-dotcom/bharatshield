import React, { useState } from 'react';
import { Edit3, Check, Globe2, MessageSquareQuote } from 'lucide-react';
import type { LanguageDetectionResult } from '../types';

interface TranscriptViewerProps {
  transcript: string;
  languageInfo: LanguageDetectionResult;
  onUpdateTranscript: (newText: string) => void;
}

export const TranscriptViewer: React.FC<TranscriptViewerProps> = ({
  transcript,
  languageInfo,
  onUpdateTranscript,
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState(transcript);

  const handleSave = () => {
    setIsEditing(false);
    if (editedText.trim() !== transcript.trim()) {
      onUpdateTranscript(editedText.trim());
    }
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 backdrop-blur-md shadow-lg space-y-4">
      {/* Header & Language Detection */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <MessageSquareQuote className="w-5 h-5 text-cyan-400" />
          <h2 className="font-bold text-slate-100 text-sm sm:text-base">
            Conversation Transcript
          </h2>
        </div>

        {/* Language Badge */}
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-800 text-slate-300 text-xs border border-slate-700">
            <Globe2 className="w-3.5 h-3.5 text-cyan-400" />
            <span className="font-semibold text-white">{languageInfo.detected_language}</span>
            <span className="text-slate-400 text-[11px]">
              ({Math.round(languageInfo.confidence * 100)}% confidence)
            </span>
          </div>

          <button
            onClick={() => {
              if (isEditing) {
                handleSave();
              } else {
                setEditedText(transcript);
                setIsEditing(true);
              }
            }}
            className="flex items-center gap-1 px-3 py-1 rounded-lg text-xs font-semibold bg-cyan-950 text-cyan-300 border border-cyan-800/60 hover:bg-cyan-900 transition-colors"
          >
            {isEditing ? (
              <>
                <Check className="w-3.5 h-3.5" /> Save &amp; Re-Analyze
              </>
            ) : (
              <>
                <Edit3 className="w-3.5 h-3.5" /> Edit Transcript
              </>
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      {isEditing ? (
        <div className="space-y-2">
          <textarea
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={5}
            className="w-full p-3 rounded-xl bg-slate-950 border border-cyan-500/60 text-slate-100 text-sm focus:outline-none focus:ring-1 focus:ring-cyan-500 font-sans"
          />
          <p className="text-[11px] text-slate-400">
            Speech recognition may occasionally mishear regional terms or names. Correct any errors above and click "Save &amp; Re-Analyze".
          </p>
        </div>
      ) : (
        <div className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/80 font-mono text-xs sm:text-sm text-slate-300 whitespace-pre-wrap leading-relaxed max-h-56 overflow-y-auto">
          {transcript}
        </div>
      )}
    </div>
  );
};
