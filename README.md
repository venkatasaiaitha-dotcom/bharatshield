# BharatShield Voice

> **Understand the call. Detect the risk. Protect yourself.**

BharatShield Voice is an AI-powered voice safety and scam intelligence system tailored for multilingual Indian citizens. It analyzes suspicious phone calls, IVR robocalls, and voice messages to uncover fraudulent social engineering tactics, extract concrete evidence, and deliver actionable safety recommendations in English, Telugu, and Hindi.

---

## 1. Problem Statement

India faces a severe surge in voice-driven financial fraud, digital arrest scams, fake KYC deactivations, task/job fraud, and electricity disconnection threats. 
Common challenges with existing solutions:
- **Language & Code-Mixing Barrier:** Scammers frequently mix English with Indian regional languages (e.g. *Telugu + English* or *Hindi + English*), confusing traditional keyword filters.
- **Binary "Scam / No Scam" Labeling:** Binary classification fails to educate citizens on *why* an interaction is dangerous or what steps to take if an OTP was already spoken.
- **Credential Theft Urgency:** Attackers weaponize psychological fear and artificial deadlines ("within 10 minutes your account will be frozen") to bypass rational judgment.

---

## 2. Solution: BharatShield Voice

BharatShield Voice provides an end-to-end voice intelligence pipeline:
1. **Multilingual Speech Ingestion:** Users record live audio via the browser microphone or upload recorded call files (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.webm`).
2. **Speech-to-Text & Diarization:** Powered by Gnani AI's Vachana Speech platform (Prisma series) optimized for Indic accents, noisy channels, and dialectal nuances.
3. **Language & Code-Mixing Detection:** Accurately recognizes regional language and English code-mixing (e.g. Telugu + English, Hindi + English) without mistaking loan words for English-only speech.
4. **Deterministic Signal Extraction:** Automatically flags concrete coercion techniques (urgency, bank/police impersonation, OTP/UPI PIN solicitation, remote screen-sharing tools like AnyDesk).
5. **Defensive AI Investigation:** Evaluates the interaction using strict prompt-injection defenses (untrusted transcript boundaries), generating an **AI Risk Score (0–100)** and calibrated threat tier (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `UNKNOWN`).
6. **Localized Spoken Guidance:** Delivers localized explanations and natural spoken explanations in everyday colloquial Telugu, Hindi, or English.

---

## 3. High-Level Architecture

```text
                    ┌───────────────────────────────────┐
                    │          Frontend (SPA)           │
                    │   React 18 + TypeScript + Vite    │
                    │  Tailwind CSS + Web Audio Canvas  │
                    └─────────────────┬─────────────────┘
                                      │
                         HTTPS / JSON │ Audio Uploads (<=25MB)
                                      ▼
                    ┌───────────────────────────────────┐
                    │          FastAPI Backend          │
                    │   Token-Bucket Rate Limiter       │
                    │   Magic-Byte Audio Validator      │
                    │   Sanitized Secret Isolation      │
                    └────────┬─────────────────┬────────┘
                             │                 │
                STT / TTS    │                 │
         (Server-Side Auth)  │                 │
                             ▼                 ▼
             ┌─────────────────────────┐   ┌──────────────────────────┐
             │      Gnani AI API       │   │  Deterministic Signal    │
             │   (Vachana Prisma STT   │   │  & AI Reasoning Engine   │
             │    & Timbre TTS)        │   │  - Prompt-Injection Proof│
             └─────────────────────────┘   │  - Verbatim Evidence     │
                                           │  - Multilingual Output   │
                                           └──────────────────────────┘
```

### Strict Secret Isolation
```text
Browser / Frontend  ──[ NO SECRET EVER ]──►  FastAPI Backend  ──[ Reads GNANI_API_KEY ]──►  Gnani AI API
```
- **Zero Frontend Secret Exposure:** The browser communicates solely with backend proxy endpoints (`/api/analyze`, `/api/investigate`, `/api/speech`).
- **Git Protection:** `.env` and `.env.*` are strictly excluded in `.gitignore`.
- **Sanitized Outputs:** All response payloads undergo recursive key scrubbing to eliminate sensitive tokens, credentials, or keys.

---

## 4. Technology Stack

- **Backend:** Python 3.10+, FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings, HTTPX, Python-Multipart, Pytest
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, Web Audio API (Canvas Waveform Visualizer)
- **Speech & AI:** Gnani AI (Vachana Speech STT `prisma-v3.0` & TTS `timbre-v2.5`), Regex Deterministic Signal Engine, Defensive AI Safety Orchestrator

---

## 5. Gnani AI Integration Details

BharatShield Voice integrates with Gnani AI's official **Vachana** ecosystem:
- **Speech-to-Text (STT):** `POST https://api.vachana.ai/stt/v3`
  - Models: `prisma-v3.0` / `prisma-v2.5`
  - Language: `indic-auto` for automated Indic code-mix detection, or direct hints (`te-IN`, `hi-IN`, `en-IN`).
  - Auth Header: `X-API-Key-ID: <server_side_key>`
- **Text-to-Speech (TTS):** `POST https://api.vachana.ai/api/v1/tts`
  - Models: `timbre-v2.5`
  - Natural Voices: `Nalini` (Telugu), `Kavya` (Hindi), `Asha` (English).
- **Graceful Degradation:** When the Gnani API key is not yet configured or external networks are unreachable, the system automatically falls back to deterministic rule-based analysis and browser Web Speech synthesis, transparently notifying the user with a "Rule-Based Safety Warning" label.

---

## 6. Directory Structure

```text
.
├── .gitignore                    # Global git ignore (safeguards secrets & build artifacts)
├── README.md                     # Comprehensive documentation
├── sample_audio/                 # Authentic synthesized call audio files ready for drag-and-drop
│   ├── 1_Fake_Bank_KYC_Telugu_English.wav        (1.8 MB - Telugu+English SBI KYC OTP Scam)
│   ├── 2_Digital_Arrest_Police_Hindi_English.wav (1.9 MB - Hindi+English CBI/Police Extortion)
│   ├── 3_UPI_Refund_QR_Scam_Hindi_English.wav    (1.7 MB - Hindi+English QR Refund Scam)
│   ├── 4_Fake_Job_Offer_Advance_Fee_English.wav  (2.3 MB - English Advance-Fee Recruitment)
│   └── 5_Legitimate_Service_Call_English.wav     (1.6 MB - English Urban Company Service Call)
├── backend/
│   ├── .env                      # Local secret file (IGNORED BY GIT)
│   ├── .env.example              # Public example containing only GNANI_API_KEY=
│   ├── .gitignore                # Backend-specific gitignore
│   ├── pytest.ini                # Pytest settings and pythonpath
│   ├── requirements.txt          # Python dependencies
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py             # Pydantic BaseSettings with SecretStr masking
│   │   ├── main.py               # FastAPI entrypoint, CORS, security headers
│   │   ├── analysis/
│   │   │   ├── investigation_engine.py  # Risk tiering, AI reasoning, prompt-injection defense
│   │   │   ├── language_engine.py       # Indic language and code-mix analyzer
│   │   │   ├── multilingual.py          # Localized translations (Telugu, Hindi, English)
│   │   │   ├── prompts.py               # Untrusted boundary directives
│   │   │   ├── schemas.py               # Pydantic data models
│   │   │   └── signal_engine.py         # Deterministic regex scam indicator extractor
│   │   ├── api/
│   │   │   └── routes/
│   │   │       ├── analyze.py           # Analysis, STT, and Speech endpoints
│   │   │       └── health.py            # Public safe health check
│   │   ├── security/
│   │   │   ├── rate_limit.py            # In-memory sliding rate limiter
│   │   │   ├── sanitizer.py             # Deep JSON response secret scrubber
│   │   │   └── validation.py            # Audio magic bytes & size validator
│   │   ├── services/
│   │   │   ├── investigation_service.py # Orchestrator for analysis
│   │   │   ├── speech_service.py        # TTS voice service
│   │   │   ├── transcription_service.py # STT orchestration
│   │   │   └── gnani/
│   │   │       ├── client.py            # Low-level authenticated HTTP client
│   │   │       └── provider.py          # High-level GnaniProvider abstraction
│   │   └── utils/
│   │       └── logging.py               # Sanitized structured logging
│   └── tests/
│       ├── conftest.py
│       ├── fixtures.py                  # Test conversation fixtures
│       ├── test_api.py                  # API endpoint tests
│       ├── test_investigation.py        # Investigation & prompt injection tests
│       ├── test_multilingual.py         # Language & code-mixing tests
│       ├── test_security.py             # Secret masking & sanitization tests
│       ├── test_signal_engine.py        # Signal extraction tests
│       └── test_validation.py           # Audio validation tests
└── frontend/
    ├── package.json
    ├── vite.config.ts                   # Proxies /api & /health to backend (no frontend env secrets)
    ├── tailwind.config.js
    ├── index.html
    └── src/
        ├── App.tsx                      # Primary application controller
        ├── index.css
        ├── types/index.ts               # Shared TypeScript schemas
        ├── services/api.ts              # Clean client API service
        └── components/
            ├── Navbar.tsx               # Header & Gnani status indicator
            ├── LandingHero.tsx          # Tagline, value prop & demo scenarios
            ├── VoiceRecorder.tsx        # Mic capture + canvas waveform + file upload
            ├── ProcessingStages.tsx     # Animated multi-stage processing telemetry
            ├── TranscriptViewer.tsx     # Transcript view with user edit capabilities
            ├── ResultDashboard.tsx      # Risk tier gauge, evidence cards & audio player
            └── HowItWorksModal.tsx      # Architecture & flow explanation modal
```

---

## 7. Setup & Local Execution (Windows PowerShell)

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Node.js v18+ & npm v9+

### Backend Setup
1. Open PowerShell and navigate to the backend directory:
   ```powershell
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Configure your Gnani API key in `backend/.env`:
   ```env
   GNANI_API_KEY=your_actual_gnani_api_key_here
   ```
5. Run the backend test suite:
   ```powershell
   python -m pytest -v
   ```
6. Start the FastAPI development server:
   ```powershell
   python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
   ```
   The backend will be live at `http://127.0.0.1:8000` (Health check: `http://127.0.0.1:8000/health`).

---

### Frontend Setup
1. Open a new PowerShell terminal and navigate to the frontend directory:
   ```powershell
   cd frontend
   ```
2. Install npm packages:
   ```powershell
   npm install
   ```
3. Verify production compilation:
   ```powershell
   npm run build
   ```
4. Start the Vite development server:
   ```powershell
   npm run dev
   ```
   The frontend will be live at `http://localhost:5173`.

---

## 8. API Documentation

| Method | Endpoint | Description | Request Body | Response |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/health` | Diagnostics & Gnani connection status | None | `HealthStatus` (status, version, gnani_configured: bool) |
| `GET` | `/api/demo/scenarios` | Retrieves standard realistic test conversations | None | `DemoScenario[]` (5 Indian scam scenarios) |
| `GET` | `/api/demo/audio/{scenario_id}` | Streams authentic Gnani-synthesized call audio | None | `audio/wav` |
| `POST` | `/api/investigate` | Investigates a raw or user-edited transcript | `TranscriptAnalysisRequest` (JSON) | `AnalysisResponse` |
| `POST` | `/api/transcribe` | Transcribes audio without full investigation | `multipart/form-data` (audio file) | `{ transcript, language_info }` |
| `POST` | `/api/analyze` | End-to-end audio upload, transcription & analysis | `multipart/form-data` (audio file) | `AnalysisResponse` |
| `POST` | `/api/speech` | Synthesizes localized voice explanation (WAV) | `SpeechSynthesisRequest` (JSON) | `audio/wav` |
| `POST` | `/api/report/generate` | Generates official National Cyber Crime 1930 Dossier | `TranscriptAnalysisRequest` (JSON) | `text/plain` |

---

## 9. Testing & Quality Assurance

The test suite covers 26 comprehensive automated test cases:
```powershell
cd backend
.\venv\Scripts\python -m pytest -v
```

### Verified Test Categories:
- **Audio Validation (`test_validation.py`):** Valid WAV RIFF headers, empty file rejection, 25MB file size limit enforcement, unsupported file extension blocking, and corrupted header detection.
- **Scam Signal Extraction (`test_signal_engine.py`):** Detection of OTP requests, UPI PIN requests, urgent deadlines, bank impersonation, upfront fee demands, and Telugu/Hindi regional phrasing.
- **AI Investigation & Safety (`test_investigation.py`):** Calibrated risk scoring, threat tier mapping (`CRITICAL`, `HIGH`, `LOW`, `UNKNOWN`), short/incomplete audio handling, and **adversarial prompt-injection immunity** (attempts to override safety rules are flagged as manipulation attacks).
- **Multilingual Analysis (`test_multilingual.py`):** English, Telugu, Hindi, code-mixing detection, and semantic consistency of localized advice across languages.
- **Security & Secret Isolation (`test_security.py`):** Verification that `Settings` string representations never expose the API key, that response sanitizer scrubs sensitive tokens, and provider status reports omit credentials.
- **API Endpoints (`test_api.py`):** Verification of `/health`, `/api/demo/scenarios`, `/api/investigate`, and security response headers (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`).

---

## 10. Interactive Demo Scenarios

The landing page features 3 built-in scenarios that pass through the **real analysis pipeline** without hard-coded results:
1. **Fake Bank / KYC Call (Telugu + English):**
   - *Transcript:* Caller claims SBI KYC expired, threatens deactivation within 10 minutes ("ventane OTP cheppandi sir"), and demands an OTP.
   - *Result:* **CRITICAL RISK (Score: 90+/100)** — Flags Bank Impersonation, Urgency Pressure, and Credential Harvesting.
2. **Fake Job Offer & Task Scam (English):**
   - *Transcript:* Caller offers an unrealistic remote data analyst role (₹85,000/mo) and demands an upfront ₹2,500 registration deposit via UPI.
   - *Result:* **HIGH RISK (Score: 70+/100)** — Flags Advance-Fee Fraud, Recruitment Impersonation, and Time Pressure.
3. **Legitimate Service Call (English):**
   - *Transcript:* Urban Company technician appointment confirmation; explicitly notes no payment is needed.
   - *Result:* **LOW RISK (Score: <25/100)** — Confirms normal customer support dialogue with zero scam indicators.

---

## 11. Security & Privacy Guarantees

- **Audio Lifecycle:** Audio files uploaded or recorded for analysis are stored in temporary files and **guaranteed to be deleted immediately** after STT processing completes (`TempAudioContext`).
- **Data Protection:** No raw conversation audio, passwords, OTPs, or bank account numbers are permanently logged or saved to disk.
- **Prompt-Injection Defense:** Untrusted transcript text is strictly encapsulated between `<UNTRUSTED_TRANSCRIPT>` boundaries and evaluated as data, ensuring caller dialogue cannot override system safety directives.
- **Rate Limiting:** In-memory token bucket limits prevent endpoint abuse (60 requests/min per IP).

---

## 12. Known Limitations

- **Speaker Diarization:** Diarization (distinguishing Caller vs User) relies on transcript cues and pauses; if audio has heavy background noise, speaker tags default to a unified conversation transcript. Users can use the **Edit Transcript** feature to correct speaker dialogue before analysis.
- **Dialectal STT Nuances:** In extremely noisy real-world call recordings, rare regional dialects or rapid colloquial slang may require user correction in the transcript editor.

---

## 13. Author & Developer

**Aitha Venkata Sai**  
- **LinkedIn Profile:** [https://www.linkedin.com/in/aitha-venkata-sai-3b128736b](https://www.linkedin.com/in/aitha-venkata-sai-3b128736b)

---

## 14. License

Developed for the BharatShield Voice AI safety initiative. All rights reserved.
