"""
BharatShield Voice - Analysis API Routes
Provides endpoints for audio upload analysis, transcript investigation,
speech synthesis, real demo audio streaming, and cybercrime report generation.
"""

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Response
from fastapi.responses import FileResponse, PlainTextResponse
from typing import Optional
from pathlib import Path
import time
import uuid

from app.config import settings, BACKEND_DIR
from app.security.validation import validate_audio_file, TempAudioContext, AudioValidationError
from app.security.rate_limit import check_rate_limit
from app.security.sanitizer import sanitize_response_data
from app.services.transcription_service import TranscriptionService
from app.services.investigation_service import InvestigationService
from app.services.speech_service import SpeechService
from app.analysis.schemas import (
    AnalysisResponse, TranscriptAnalysisRequest, SpeechSynthesisRequest
)
from app.utils.logging import get_logger

logger = get_logger("analyze_route")
router = APIRouter(prefix="/api", tags=["Analysis"], dependencies=[Depends(check_rate_limit)])

transcription_service = TranscriptionService()
investigation_service = InvestigationService()
speech_service = SpeechService()

DEMO_AUDIO_DIR = BACKEND_DIR / "static" / "demo_audio"

# Expanded, Real-World Indian Scam Scenarios
DEMO_SCENARIOS = {
    "fake_bank_kyc": {
        "id": "fake_bank_kyc",
        "title": "Fake SBI Credit Card KYC Deactivation",
        "category": "Banking & OTP Harvesting",
        "description": "Caller claims SBI KYC is expired, threatens account block within 10 minutes, and solicits an OTP.",
        "language": "Telugu + English",
        "expected_risk": "CRITICAL",
        "has_audio": True,
        "transcript": (
            "Caller: Hello sir, I am calling from SBI Card verification department. "
            "Your KYC has expired and your credit card will be blocked immediately within 10 minutes. "
            "Meeru ventane verify chesukovali. To stop the deactivation, please tell me the 6 digit OTP you just received on your mobile. "
            "Ventane OTP cheppandi sir, లేకపోతే account freeze aipotundi.\n"
            "User: Why do you need my OTP for KYC?\n"
            "Caller: Sir this is standard system verification from bank server. "
            "If you do not share the OTP right now, your account will be permanently suspended."
        )
    },
    "digital_arrest": {
        "id": "digital_arrest",
        "title": "Digital Arrest: Police & CBI Extortion",
        "category": "Authority Impersonation & Extortion",
        "description": "Impersonator claims to be Delhi Police / CBI officer alleging illegal narcotics parcel under your Aadhaar.",
        "language": "Hindi + English",
        "expected_risk": "CRITICAL",
        "has_audio": True,
        "transcript": (
            "Caller: Namaste, main Delhi Police Cyber Crime Branch se Inspector Sharma bol raha hoon. "
            "Aapke Aadhaar card par ek illegal parcel customs ne pakda hai jisme narcotics aur fake passports mile hain. "
            "Supreme Court ne aapke khilaf arrest warrant issue kiya hai. "
            "Turant yeh AnyDesk app download karke screen share kijiye aur apni verification complete kijiye, "
            "warna police aapke ghar bhej di jayegi aur arrest kiya jayega."
        )
    },
    "upi_refund_scam": {
        "id": "upi_refund_scam",
        "title": "UPI 'Accidental Transfer' QR Code Scam",
        "category": "UPI Payment Fraud",
        "description": "Caller pretends to have sent money by mistake, urging the user to scan a QR code and enter UPI PIN.",
        "language": "Hindi + English",
        "expected_risk": "CRITICAL",
        "has_audio": True,
        "transcript": (
            "Caller: Hello sir, maine galti se aapke PhonePe number par 25,000 rupees transfer kar diye hain. "
            "Dekhiye maine screenshot bhi bhej diya hai. Mera bacha hospital mein admit hai, please mujhe paise wapas bhej dijiye. "
            "Maine ek QR code WhatsApp kiya hai, bas usko scan karke apna UPI PIN daal dijiye, paise turant wapas aa jayenge. "
            "Please der mat kijiye sir."
        )
    },
    "fake_job_offer": {
        "id": "fake_job_offer",
        "title": "Work-From-Home Task & Job Scam",
        "category": "Advance-Fee Recruitment Fraud",
        "description": "Offers an unrealistic work-from-home salary of ₹85,000/mo and demands upfront ₹2,500 registration deposit.",
        "language": "English",
        "expected_risk": "HIGH",
        "has_audio": True,
        "transcript": (
            "Caller: Good morning ma'am, I am calling from Global Career HR Recruitment Team. "
            "Your resume has been shortlisted for an online part-time data analyst job with a salary of 85,000 rupees per month for just 2 hours of daily work. "
            "To confirm your position and dispatch your company laptop, you need to pay a refundable registration fee of 2,500 rupees right now. "
            "Please transfer the amount to this UPI ID immediately as positions are limited for today."
        )
    },
    "normal_service_call": {
        "id": "normal_service_call",
        "title": "Legitimate Service Maintenance Call",
        "category": "Routine Customer Service",
        "description": "Urban Company technician visit confirmation; explicitly clarifies no payment is required.",
        "language": "English",
        "expected_risk": "LOW",
        "has_audio": True,
        "transcript": (
            "Caller: Hello sir, good evening. I am calling from Urban Company regarding your AC maintenance service scheduled for tomorrow between 2 PM and 4 PM. "
            "Our technician Rajesh will be visiting your location. "
            "Please ensure someone is available at home to provide access to the unit. "
            "You do not need to make any payment as this visit is covered under your annual warranty plan. "
            "If you need to reschedule, you can use the official mobile app. Have a good evening."
        )
    }
}


@router.get("/demo/scenarios")
async def list_demo_scenarios():
    """Returns available demo scenarios for interactive testing."""
    return {"scenarios": list(DEMO_SCENARIOS.values())}


@router.get("/demo/audio/{scenario_id}")
async def get_demo_audio(scenario_id: str):
    """
    Streams authentic pre-synthesized WAV audio for the specified demo scenario.
    Generated using Gnani Vachana TTS.
    """
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail="Demo scenario not found")

    audio_file = DEMO_AUDIO_DIR / f"{scenario_id}.wav"
    if not audio_file.exists():
        # Fallback dynamic synthesis via Gnani TTS
        scenario = DEMO_SCENARIOS[scenario_id]
        lang = "te-IN" if "Telugu" in scenario["language"] else ("hi-IN" if "Hindi" in scenario["language"] else "en-IN")
        raw_audio = await speech_service.generate_spoken_explanation(scenario["transcript"], language=lang)
        if raw_audio:
            DEMO_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
            audio_file.write_bytes(raw_audio)
        else:
            raise HTTPException(status_code=404, detail="Audio file not available")

    return FileResponse(
        path=str(audio_file),
        media_type="audio/wav",
        filename=f"{scenario_id}.wav"
    )


@router.get("/demo/audio/{scenario_id}/download")
async def download_single_demo_audio(scenario_id: str):
    """
    Direct file download endpoint for a specific sample WAV file.
    Forces browser download prompt.
    """
    if scenario_id not in DEMO_SCENARIOS:
        raise HTTPException(status_code=404, detail="Demo scenario not found")

    audio_file = DEMO_AUDIO_DIR / f"{scenario_id}.wav"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")

    file_name_map = {
        "fake_bank_kyc": "1_Fake_Bank_KYC_Telugu_English.wav",
        "digital_arrest": "2_Digital_Arrest_Police_Hindi_English.wav",
        "upi_refund_scam": "3_UPI_Refund_QR_Scam_Hindi_English.wav",
        "fake_job_offer": "4_Fake_Job_Offer_Advance_Fee_English.wav",
        "normal_service_call": "5_Legitimate_Service_Call_English.wav",
    }
    download_name = file_name_map.get(scenario_id, f"{scenario_id}.wav")

    return FileResponse(
        path=str(audio_file),
        media_type="application/octet-stream",
        filename=download_name,
        headers={"Content-Disposition": f'attachment; filename="{download_name}"'}
    )


@router.get("/demo/audio/download-all/pack")
async def download_all_demo_audio_pack():
    """
    Bundles all 5 sample audio WAV files into a zip archive for one-click download.
    """
    import zipfile
    zip_path = DEMO_AUDIO_DIR / "BharatShield_Sample_Audio_Pack.zip"

    file_name_map = {
        "fake_bank_kyc": "1_Fake_Bank_KYC_Telugu_English.wav",
        "digital_arrest": "2_Digital_Arrest_Police_Hindi_English.wav",
        "upi_refund_scam": "3_UPI_Refund_QR_Scam_Hindi_English.wav",
        "fake_job_offer": "4_Fake_Job_Offer_Advance_Fee_English.wav",
        "normal_service_call": "5_Legitimate_Service_Call_English.wav",
    }

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for sid, fname in file_name_map.items():
            src_file = DEMO_AUDIO_DIR / f"{sid}.wav"
            if src_file.exists():
                zipf.write(src_file, arcname=fname)

    return FileResponse(
        path=str(zip_path),
        media_type="application/zip",
        filename="BharatShield_Sample_Audio_Pack.zip",
        headers={"Content-Disposition": 'attachment; filename="BharatShield_Sample_Audio_Pack.zip"'}
    )


@router.post("/transcribe")
async def transcribe_only(
    audio: UploadFile = File(...),
    language_hint: Optional[str] = Form("indic-auto")
):
    """
    Speech-to-Text endpoint.
    Transcribes audio using Gnani STT and returns the transcript for user review/editing.
    """
    contents = await audio.read()
    validate_audio_file(audio.filename or "recording.wav", audio.content_type, contents)

    with TempAudioContext(audio.filename or "audio.wav", contents) as temp_path:
        stt_result = await transcription_service.transcribe_audio(
            file_path=temp_path,
            mime_type=audio.content_type or "audio/wav",
            language_hint=language_hint or "indic-auto"
        )

    return sanitize_response_data(stt_result)


@router.post("/investigate", response_model=AnalysisResponse)
async def investigate_transcript(request: TranscriptAnalysisRequest):
    """
    Investigates a transcript (either generated from audio or edited by the user).
    Runs deterministic signal extraction, AI safety reasoning, and localized explanations.
    """
    response = investigation_service.analyze_transcript(
        transcript=request.transcript,
        hint_language=request.language_code
    )
    return sanitize_response_data(response.model_dump())


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(
    audio: UploadFile = File(...),
    language_hint: Optional[str] = Form("indic-auto")
):
    """
    End-to-end analysis endpoint:
    Audio Upload -> Gnani STT -> Signal Engine -> AI Investigation -> Localized Output.
    """
    contents = await audio.read()
    validate_audio_file(audio.filename or "audio.wav", audio.content_type, contents)

    with TempAudioContext(audio.filename or "audio.wav", contents) as temp_path:
        stt_result = await transcription_service.transcribe_audio(
            file_path=temp_path,
            mime_type=audio.content_type or "audio/wav",
            language_hint=language_hint or "indic-auto"
        )

    transcript = stt_result.get("transcript", "").strip()

    if not transcript:
        if not settings.is_gnani_configured:
            raise HTTPException(
                status_code=503,
                detail="Gnani AI API key is not yet configured. Please provide the key or use text investigation / demo mode."
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Could not detect clear speech in the provided audio file. Please try a clearer sample or enter text."
            )

    response = investigation_service.analyze_transcript(
        transcript=transcript,
        hint_language=language_hint
    )
    return sanitize_response_data(response.model_dump())


@router.post("/speech")
async def generate_speech(request: SpeechSynthesisRequest):
    """
    Synthesizes spoken guidance via Gnani TTS.
    Returns audio/wav data for the browser to play.
    """
    audio_bytes = await speech_service.generate_spoken_explanation(
        text=request.text,
        language=request.language
    )

    if not audio_bytes:
        return Response(status_code=204)

    return Response(content=audio_bytes, media_type="audio/wav")


@router.post("/report/generate")
async def generate_incident_report(request: TranscriptAnalysisRequest):
    """
    Generates an official formatted Incident Dossier ready to submit
    to the National Cyber Crime Reporting Portal (cybercrime.gov.in) or local police.
    """
    analysis = investigation_service.analyze_transcript(request.transcript, request.language_code)
    inv = analysis.investigation

    ref_id = f"BVS-CYBER-{int(time.time())}-{uuid.uuid4().hex[:6].upper()}"
    report_text = f"""================================================================================
          NATIONAL CYBER CRIME INCIDENT DOSSIER (ASSISTIVE REPORT)
          Generated by BharatShield Voice AI Safety System
================================================================================

INCIDENT REFERENCE ID  : {ref_id}
TIMESTAMP              : {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
ASSESSED RISK TIER     : {inv.risk_level.value}
AI RISK SCORE          : {inv.risk_score} / 100
CONFIDENCE RATING      : {int(inv.confidence * 100)}%
DETECTED LANGUAGE      : {analysis.language_info.detected_language}

--------------------------------------------------------------------------------
1. EXECUTIVE SUMMARY & MODUS OPERANDI
--------------------------------------------------------------------------------
{inv.summary}

Detailed Analysis:
{inv.explanation}

Tactics Detected:
{chr(10).join(f"- {t}" for t in inv.tactics_detected)}

Sensitive Credentials / Actions Solicited:
{chr(10).join(f"- {s}" for s in inv.requested_information) if inv.requested_information else "- None explicitly detected"}

--------------------------------------------------------------------------------
2. VERBATIM TRANSCRIPT EVIDENCE EXTRACTED
--------------------------------------------------------------------------------
{chr(10).join(f'[{e.severity.value}] {e.title}:{chr(10)}  "{e.quote}"{chr(10)}  Explanation: {e.explanation}{chr(10)}' for e in inv.evidence) if inv.evidence else "No malicious evidence signals extracted."}

--------------------------------------------------------------------------------
3. FULL RECORDED DIALOGUE TRANSCRIPT
--------------------------------------------------------------------------------
{request.transcript}

--------------------------------------------------------------------------------
4. RECOMMENDED CITIZEN ACTIONS
--------------------------------------------------------------------------------
{chr(10).join(f"{i+1}. {a}" for i, a in enumerate(inv.recommended_actions))}

DANGEROUS ACTIONS TO AVOID:
{chr(10).join(f"- {d}" for d in inv.do_not_do)}

--------------------------------------------------------------------------------
5. EMERGENCY CONTACT DIRECTORY (INDIA)
--------------------------------------------------------------------------------
- National Cyber Crime Helpline : 1930 (Toll-Free 24x7)
- Official Reporting Portal     : https://cybercrime.gov.in
- SBI Fraud Reporting          : 1800 11 1109 / 1800 425 3800
- HDFC Fraud Helpline          : 1800 258 3838
- ICICI Fraud Helpline         : 1800 1080
- Axis Bank Helpline           : 1800 419 5959
- RBI Sachet Portal            : https://sachet.rbi.org.in

LEGAL PROVISIONS INVOKED:
- Section 66D, Information Technology Act, 2000 (Punishment for cheating by personation using computer resource)
- Section 318(4) / Section 319, Bharatiya Nyaya Sanhita (BNS), 2023 (Cheating and dishonestly inducing delivery of property)

================================================================================
DISCLAIMER: This report is generated by BharatShield Voice AI based upon available conversation data.
It serves as an assistive evidentiary document for law enforcement and banking authorities.
================================================================================
"""
    return PlainTextResponse(content=report_text, media_type="text/plain; charset=utf-8")
