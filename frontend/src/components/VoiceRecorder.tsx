import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play, Upload, AlertCircle, FileAudio, RotateCcw } from 'lucide-react';

interface VoiceRecorderProps {
  onAnalyzeAudio: (file: File | Blob, filename: string) => void;
  onAnalyzeText: (text: string) => void;
  isLoading: boolean;
}

export const VoiceRecorder: React.FC<VoiceRecorderProps> = ({
  onAnalyzeAudio,
  onAnalyzeText,
  isLoading,
}) => {
  const [mode, setMode] = useState<'record' | 'upload' | 'text'>('record');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const [micError, setMicError] = useState<string | null>(null);

  // File Upload State
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);

  // Text Input State
  const [customText, setCustomText] = useState('');

  // Refs for audio capture and animation
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const timerIntervalRef = useRef<number | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  // Format seconds into MM:SS
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Start microphone recording
  const startRecording = async () => {
    setMicError(null);
    setRecordedBlob(null);
    setRecordingDuration(0);
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Audio visualization setup
      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 64;
      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      audioContextRef.current = audioCtx;
      analyserRef.current = analyser;

      // MediaRecorder setup (prefers webm/opus or wav)
      let mimeType = 'audio/webm';
      if (!MediaRecorder.isTypeSupported('audio/webm')) {
        if (MediaRecorder.isTypeSupported('audio/ogg')) {
          mimeType = 'audio/ogg';
        } else {
          mimeType = '';
        }
      }

      const recorder = mimeType ? new MediaRecorder(stream, { mimeType }) : new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = () => {
        const fullBlob = new Blob(audioChunksRef.current, { type: recorder.mimeType || 'audio/webm' });
        setRecordedBlob(fullBlob);

        // Stop all media tracks
        stream.getTracks().forEach((track) => track.stop());
        if (audioContextRef.current) {
          audioContextRef.current.close().catch(() => {});
        }
      };

      recorder.start(100);
      setIsRecording(true);

      // Start duration counter
      timerIntervalRef.current = window.setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);

      // Start canvas waveform visualizer
      drawWaveform();
    } catch (err: any) {
      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setMicError('Microphone permission was denied. Please allow microphone access in your browser settings.');
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setMicError('No microphone found on your system. Please connect an audio input device.');
      } else {
        setMicError(err.message || 'Could not access microphone.');
      }
    }
  };

  // Stop recording
  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current);
        timerIntervalRef.current = null;
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    }
  };

  // Render dynamic audio waveform on canvas
  const drawWaveform = () => {
    const canvas = canvasRef.current;
    const analyser = analyserRef.current;
    if (!canvas || !analyser) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    const render = () => {
      animationFrameRef.current = requestAnimationFrame(render);
      analyser.getByteFrequencyData(dataArray);

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      const barWidth = (canvas.width / bufferLength) * 2;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        const barHeight = (dataArray[i] / 255) * canvas.height * 0.85;

        // Gradient bar
        const gradient = ctx.createLinearGradient(0, canvas.height, 0, 0);
        gradient.addColorStop(0, '#0284c7');
        gradient.addColorStop(1, '#38bdf8');

        ctx.fillStyle = gradient;
        ctx.fillRect(x, (canvas.height - barHeight) / 2, barWidth - 2, barHeight || 3);

        x += barWidth;
      }
    };
    render();
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
      if (animationFrameRef.current) cancelAnimationFrame(animationFrameRef.current);
      if (audioContextRef.current) audioContextRef.current.close().catch(() => {});
    };
  }, []);

  // Handle file input selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setUploadError(null);
    const file = e.target.files?.[0];
    if (!file) return;

    // Check size limit (25 MB)
    if (file.size > 25 * 1024 * 1024) {
      setUploadError('File size exceeds the 25 MB limit.');
      return;
    }

    setUploadedFile(file);
  };

  // Trigger analysis explicitly
  const handleAnalyze = () => {
    if (mode === 'record' && recordedBlob) {
      onAnalyzeAudio(recordedBlob, 'recording.webm');
    } else if (mode === 'upload' && uploadedFile) {
      onAnalyzeAudio(uploadedFile, uploadedFile.name);
    } else if (mode === 'text' && customText.trim()) {
      onAnalyzeText(customText.trim());
    }
  };

  return (
    <div className="max-w-3xl mx-auto rounded-3xl border border-slate-800 bg-slate-900/70 p-6 sm:p-8 backdrop-blur-md shadow-2xl">
      {/* Tab Navigation */}
      <div className="flex rounded-xl bg-slate-950 p-1 mb-6 border border-slate-800">
        <button
          onClick={() => setMode('record')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
            mode === 'record'
              ? 'bg-slate-800 text-cyan-300 shadow-md shadow-cyan-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Mic className="w-4 h-4" />
          <span>Record Microphone</span>
        </button>

        <button
          onClick={() => setMode('upload')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
            mode === 'upload'
              ? 'bg-slate-800 text-cyan-300 shadow-md shadow-cyan-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Upload className="w-4 h-4" />
          <span>Upload Audio</span>
        </button>

        <button
          onClick={() => setMode('text')}
          className={`flex-1 flex items-center justify-center gap-2 py-2.5 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
            mode === 'text'
              ? 'bg-slate-800 text-cyan-300 shadow-md shadow-cyan-900/30'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <FileAudio className="w-4 h-4" />
          <span>Paste Transcript</span>
        </button>
      </div>

      {/* Mode 1: Record Microphone */}
      {mode === 'record' && (
        <div className="space-y-6">
          <div className="flex flex-col items-center justify-center p-8 rounded-2xl border border-dashed border-slate-700/80 bg-slate-950/50">
            {/* Visualizer Canvas */}
            <div className="w-full max-w-md h-24 flex items-center justify-center mb-4 bg-slate-900/50 rounded-xl overflow-hidden border border-slate-800">
              {isRecording ? (
                <canvas ref={canvasRef} width={400} height={96} className="w-full h-full" />
              ) : recordedBlob ? (
                <div className="flex items-center gap-2 text-cyan-400 text-xs font-medium">
                  <span className="w-2 h-2 rounded-full bg-cyan-400" />
                  <span>Recording ready for investigation ({formatDuration(recordingDuration)})</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 text-slate-400 text-xs">
                  <span>Waveform will animate while recording</span>
                </div>
              )}
            </div>

            {/* Duration Display */}
            <div className="text-3xl font-mono font-bold text-slate-100 mb-6">
              {formatDuration(recordingDuration)}
            </div>

            {/* Controls */}
            <div className="flex items-center gap-4">
              {!isRecording ? (
                <button
                  onClick={startRecording}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-6 py-3 rounded-full bg-rose-600 hover:bg-rose-500 text-white font-semibold text-sm shadow-lg shadow-rose-950 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                  <Mic className="w-4 h-4" />
                  <span>{recordedBlob ? 'Re-record Audio' : 'Start Recording'}</span>
                </button>
              ) : (
                <button
                  onClick={stopRecording}
                  className="flex items-center gap-2 px-6 py-3 rounded-full bg-slate-700 hover:bg-slate-600 text-white font-semibold text-sm shadow-lg animate-pulse"
                >
                  <Square className="w-4 h-4 fill-current" />
                  <span>Stop Recording</span>
                </button>
              )}

              {recordedBlob && !isRecording && (
                <button
                  onClick={handleAnalyze}
                  disabled={isLoading}
                  className="flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-lg shadow-cyan-950 transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                >
                  <Play className="w-4 h-4 fill-current" />
                  <span>Analyze Conversation</span>
                </button>
              )}
            </div>

            {/* Microphone Permission Error Notice */}
            {micError && (
              <div className="mt-6 flex items-start gap-2.5 p-3 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs max-w-md">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" />
                <span>{micError}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mode 2: Upload Audio */}
      {mode === 'upload' && (
        <div className="space-y-6">
          <label className="flex flex-col items-center justify-center p-8 rounded-2xl border-2 border-dashed border-slate-700 hover:border-cyan-500/60 bg-slate-950/50 hover:bg-slate-900/40 transition-all cursor-pointer group">
            <input
              type="file"
              accept=".wav,.mp3,.m4a,.ogg,.webm,.flac"
              onChange={handleFileChange}
              className="hidden"
            />
            <div className="p-4 rounded-2xl bg-slate-900 group-hover:bg-cyan-950/60 border border-slate-800 group-hover:border-cyan-800/50 transition-colors mb-3">
              <Upload className="w-8 h-8 text-cyan-400" />
            </div>
            <p className="font-semibold text-sm text-slate-200 group-hover:text-cyan-300">
              {uploadedFile ? uploadedFile.name : 'Choose audio file or drag & drop'}
            </p>
            <p className="text-xs text-slate-400 mt-1">
              Supported formats: WAV, MP3, M4A, OGG, WebM (Max: 25 MB)
            </p>
          </label>

          {/* Quick-Load Pre-Built Sample Audio Files */}
          <div className="p-4 rounded-2xl bg-slate-950/70 border border-slate-800/80 space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">
                Or Select a Ready-To-Test Sample Audio File:
              </span>
              <span className="text-[11px] text-cyan-400 font-mono">Located in /sample_audio</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {[
                { id: 'fake_bank_kyc', name: '1_Fake_Bank_KYC_Telugu_English.wav', label: 'Fake SBI KYC (Telugu + English)', risk: 'CRITICAL' },
                { id: 'digital_arrest', name: '2_Digital_Arrest_Police_Hindi_English.wav', label: 'Digital Arrest / Police (Hindi + English)', risk: 'CRITICAL' },
                { id: 'upi_refund_scam', name: '3_UPI_Refund_QR_Scam_Hindi_English.wav', label: 'UPI QR Refund Scam (Hindi + English)', risk: 'CRITICAL' },
                { id: 'fake_job_offer', name: '4_Fake_Job_Offer_Advance_Fee_English.wav', label: 'Fake Job Offer (English)', risk: 'HIGH' },
                { id: 'normal_service_call', name: '5_Legitimate_Service_Call_English.wav', label: 'Normal Service Call (English)', risk: 'LOW' },
              ].map((sample) => (
                <button
                  key={sample.id}
                  type="button"
                  onClick={async () => {
                    try {
                      setUploadError(null);
                      const res = await fetch(`/api/demo/audio/${sample.id}`);
                      if (!res.ok) throw new Error('Failed to fetch sample');
                      const blob = await res.blob();
                      const file = new File([blob], sample.name, { type: 'audio/wav' });
                      setUploadedFile(file);
                    } catch (err: any) {
                      setUploadError('Could not load sample audio file.');
                    }
                  }}
                  className={`flex items-center justify-between p-2.5 rounded-xl border text-left text-xs transition-all ${
                    uploadedFile?.name === sample.name
                      ? 'border-cyan-500 bg-cyan-950/50 text-cyan-200'
                      : 'border-slate-800 bg-slate-900/60 hover:border-slate-700 text-slate-300 hover:text-white'
                  }`}
                >
                  <div className="truncate mr-2">
                    <p className="font-semibold truncate">{sample.label}</p>
                    <p className="text-[10px] text-slate-400 font-mono">{sample.name}</p>
                  </div>
                  <span className={`text-[9px] font-black uppercase px-2 py-0.5 rounded-full shrink-0 border ${
                    sample.risk === 'CRITICAL' ? 'border-rose-800 bg-rose-950 text-rose-300' :
                    sample.risk === 'HIGH' ? 'border-amber-800 bg-amber-950 text-amber-300' :
                    'border-emerald-800 bg-emerald-950 text-emerald-300'
                  }`}>
                    {sample.risk}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {uploadError && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-rose-950/40 border border-rose-800 text-rose-300 text-xs">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}

          {uploadedFile && (
            <div className="flex items-center justify-between p-4 rounded-xl bg-slate-950 border border-slate-800">
              <div className="flex items-center gap-3">
                <FileAudio className="w-5 h-5 text-cyan-400" />
                <div>
                  <p className="text-sm font-medium text-slate-200">{uploadedFile.name}</p>
                  <p className="text-xs text-slate-400">
                    {(uploadedFile.size / (1024 * 1024)).toFixed(2)} MB
                  </p>
                </div>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-md shadow-cyan-950 disabled:opacity-50"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Conversation</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* Mode 3: Text Transcript */}
      {mode === 'text' && (
        <div className="space-y-4">
          <textarea
            value={customText}
            onChange={(e) => setCustomText(e.target.value)}
            rows={5}
            placeholder="Paste suspicious phone conversation transcript here in English, Telugu, Hindi, or code-mixed text..."
            className="w-full p-4 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 placeholder-slate-500 text-sm focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all"
          />

          <div className="flex items-center justify-between">
            <span className="text-xs text-slate-400">
              {customText.length} characters
            </span>

            <div className="flex gap-2">
              {customText && (
                <button
                  onClick={() => setCustomText('')}
                  className="px-3 py-2 rounded-lg border border-slate-800 text-slate-400 hover:text-white text-xs transition-colors flex items-center gap-1.5"
                >
                  <RotateCcw className="w-3 h-3" /> Clear
                </button>
              )}
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !customText.trim()}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-semibold text-sm shadow-md disabled:opacity-50"
              >
                <Play className="w-4 h-4 fill-current" />
                <span>Analyze Conversation</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
