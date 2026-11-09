"""
BharatShield Voice - Deterministic Scam Signal Engine
Extracts verified signals from conversation transcripts without hallucinations.
Supports English, Hindi, Telugu, and code-mixed Indian conversations.
"""

import re
from typing import List, Tuple, Dict, Any
from app.analysis.schemas import DeterministicSignals, SignalItem, EvidenceItem, Severity


# Category patterns with regexes and severity mappings
PATTERNS = {
    "credential_request": [
        (r"\b(otp|one[ -]time[ -]password|verification[ -]code)\b", "OTP Request", Severity.CRITICAL,
         "The caller explicitly asked for a One-Time Password (OTP)"),
        (r"\b(upi[ -]?pin|mpin|atm[ -]?pin|secret[ -]?pin)\b", "UPI/ATM PIN Request", Severity.CRITICAL,
         "The caller asked for a UPI PIN or ATM PIN, which must never be shared"),
        (r"\b(cvv|card[ -]?verification|cvv2)\b", "Card CVV Request", Severity.CRITICAL,
         "The caller requested payment card security digits (CVV)"),
        (r"\b(net[ -]?banking[ -]?password|login[ -]?password|account[ -]?password)\b", "Password Request", Severity.CRITICAL,
         "The caller requested a confidential account password"),
        # Telugu / Hindi phrases
        (r"(?i)(otp\s*(cheppandi|ivvandi|cheppu|pampandi|batayein|bhejo|share\s*kijiye|bolo))", "OTP Verbal Request", Severity.CRITICAL,
         "The caller verbally pressured the user to speak or forward an OTP"),
        (r"(?i)(pin\s*(number\s*)?(enter\s*chey|cheppandi|batayein|dalo))", "PIN Entry Solicitation", Severity.CRITICAL,
         "The caller asked the user to enter or share their private PIN"),
    ],
    "urgency": [
        (r"\b(immediately|right now|within 5 minutes|within 10 minutes|urgent|urgently)\b", "Urgent Time Pressure", Severity.HIGH,
         "The caller demanded immediate compliance to prevent rational thinking"),
        (r"\b(account (will be|is being) (blocked|suspended|frozen|closed|deactivated))\b", "Account Suspension Threat", Severity.HIGH,
         "The caller threatened that the user's account will be blocked"),
        (r"\b(kyc (has expired|needs update|is blocked|pending)|update kyc)\b", "Urgent KYC Threat", Severity.HIGH,
         "The caller claimed KYC expired and demands urgent action"),
        (r"\b(sim (will be|is being) deactivated|electricity (will be|is being) disconnected)\b", "Service Disconnection Threat", Severity.HIGH,
         "The caller threatened immediate disconnection of essential services"),
        # Telugu / Hindi phrases
        (r"(?i)(ventane|urgent\s*ga|ippude|block\s*aipotundi|cancel\s*avtundi)", "High Urgency Pressure", Severity.HIGH,
         "Urgency marker in Telugu/Hindi pushing user to act without verifying"),
        (r"(?i)(turant|abhi\s*ke\s*abhi|band\s*ho\s*jayega|kat\s*jayegi|aaj\s*raat\s*tak)", "Urgency & Threat Marker", Severity.HIGH,
         "Immediate deadline or disconnection threat in Indic vernacular"),
    ],
    "impersonation": [
        (r"\b(calling from (sbi|hdfc|icici|axis|punjab national|bank|rbi|reserve bank))\b", "Bank Impersonation", Severity.HIGH,
         "The caller claimed to represent a financial institution or the Reserve Bank"),
        (r"\b(icici|sbi|hdfc|axis|pnb|kotak|bank)\b[\w\s]{0,35}\b(support|manager|verification|team|executive)\b", "Bank Staff Impersonation", Severity.HIGH,
         "The caller referenced bank customer support or verification executive"),
        (r"\b(police|crime\s*branch|cbi|ed|income\s*tax|cyber\s*cell|customs|inspector)\b", "Law Enforcement / Authority Impersonation", Severity.CRITICAL,
         "The caller claimed authority as police, cyber cell, CBI, or customs officer (Digital Arrest tactic)"),
        (r"\b(calling from (airtel|jio|vi|bsnl) (support|headquarters|team))\b", "Telecom Impersonation", Severity.MEDIUM,
         "The caller impersonated telecom customer support"),
        (r"\b(calling from (amazon|flipkart|fedex|dhl|courier))\b", "Courier/Delivery Impersonation", Severity.MEDIUM,
         "The caller claimed to be an e-commerce or courier service agent"),
        (r"\b(hr manager|hiring manager|recruitment team|telegram job)\b", "Recruitment Impersonation", Severity.MEDIUM,
         "The caller claimed to represent a hiring or recruitment department"),
        # Telugu / Hindi phrases
        (r"(?i)(bank[\w\s]{0,25}(nunchi|se)[\w\s]{0,20}(call|bol|manager))", "Bank Staff Regional Impersonation", Severity.HIGH,
         "Caller claimed to be a bank official in regional conversation"),
        (r"(?i)(police|cyber\s*cell|customs)[\w\s]{0,25}(nunchi|se|station|officer|inspector)", "Officer Authority Impersonation", Severity.CRITICAL,
         "Claim of official legal or regulatory authority"),
    ],
    "financial_request": [
        (r"\b(registration fee|processing fee|security deposit|refundable deposit|advance payment)\b", "Upfront Fee Demand", Severity.HIGH,
         "The caller demanded an upfront fee or advance payment before releasing funds or jobs"),
        (r"\b(transfer (money|amount|funds) to (this|the) (upi|account|number))\b", "Direct Money Transfer", Severity.HIGH,
         "The caller requested a direct transfer of funds to an unverified recipient"),
        (r"\b(send money to receive|pay Rs\.?\s*\d+|pay ₹\s*\d+)\b", "Pay-to-Receive Tactic", Severity.HIGH,
         "The caller asked the user to pay money in order to claim a prize or payment"),
        # Telugu / Hindi phrases
        (r"(?i)(dabbu\s*(pampandi|veye|transfer\s*cheyandi)|paisa\s*(bhejo|dal do|transfer\s*karo))", "Money Transfer Demand", Severity.HIGH,
         "Direct request for funds in regional conversation"),
        (r"(?i)(fees\s*(kattali|pay\s*cheyali|bharna\s*hoga))", "Advance Fee Obligation", Severity.HIGH,
         "Claim that fees must be paid first to unlock a benefit"),
    ],
    "remote_access_request": [
        (r"\b(anydesk|teamviewer|quicksupport|rustdesk|screen share|screenshare)\b", "Remote Access Tool Request", Severity.CRITICAL,
         "The caller instructed the user to install remote desktop/screen sharing tools"),
        (r"\b(download (this|the) app|install (this|the) apk|open (this|the) link)\b", "Suspicious App/Link Solicitation", Severity.HIGH,
         "The caller urged downloading an unverified application or clicking an external link"),
        # Telugu / Hindi phrases
        (r"(?i)(app\s*(install\s*cheyandi|download\s*cheyandi|dal lo))", "App Installation Pressure", Severity.HIGH,
         "Instructed user to install software on their mobile device"),
        (r"(?i)(screen\s*(share\s*cheyandi|dikhayein))", "Screen Sharing Request", Severity.CRITICAL,
         "Requested screen sharing which exposes banking screens and OTPs"),
    ],
    "social_engineering": [
        (r"\b(don't tell anyone|keep this confidential|do not disconnect|stay on the line)\b", "Secrecy & Isolation", Severity.HIGH,
         "The caller attempted to isolate the victim and prevent seeking outside help"),
        (r"\b(arrest warrant|court case|fir has been filed|illegal parcel|narcotics)\b", "Intimidation & False Legal Threat", Severity.CRITICAL,
         "The caller used false legal or criminal threats to cause panic"),
        (r"\b(won a lottery|cashback of|reward points worth|selected for prize)\b", "Lottery / Reward Bait", Severity.MEDIUM,
         "The caller baited the user with fictitious rewards or lotteries"),
        # Telugu / Hindi phrases
        (r"(?i)(evvariki\s*cheppakandi|kisi\s*ko\s*mat\s*batana|line\s*lo\s*undandi)", "Secrecy / Isolation Command", Severity.HIGH,
         "Demanded secrecy or that the user remain on the phone"),
    ]
}


def _split_into_sentences(text: str) -> List[str]:
    """Splits transcript into readable sentences for clean quote extraction."""
    # Split by common sentence delimiters while keeping meaningful segments
    segments = re.split(r"(?<=[.!?\n])\s+|(?<=\b[A-Za-z0-9]\:)\s+", text)
    return [s.strip() for s in segments if len(s.strip()) > 3]


def extract_deterministic_signals(transcript: str) -> Tuple[DeterministicSignals, List[EvidenceItem]]:
    """
    Deterministically extracts scam indicators and verbatim quotes from transcript.
    Never fabricates quotes - every quote is verified against the input text.
    """
    sentences = _split_into_sentences(transcript)
    signals_list: List[SignalItem] = []
    evidence_list: List[EvidenceItem] = []

    category_triggered = {
        "urgency": False,
        "impersonation": False,
        "credential_request": False,
        "financial_request": False,
        "remote_access_request": False,
        "social_engineering": False
    }

    seen_titles = set()

    for category, pattern_group in PATTERNS.items():
        for regex_str, title, severity, explanation in pattern_group:
            pattern = re.compile(regex_str, re.IGNORECASE)
            matched_quotes = []

            # Find matching verbatim sentences from the transcript
            for sent in sentences:
                if pattern.search(sent):
                    # Ensure quote is verbatim and not too long
                    cleaned = sent.strip().strip('"').strip("'")
                    if cleaned and cleaned not in matched_quotes:
                        matched_quotes.append(cleaned)

            # Fallback if sentence splitter missed inline match
            if not matched_quotes:
                match = pattern.search(transcript)
                if match:
                    start = max(0, match.start() - 25)
                    end = min(len(transcript), match.end() + 25)
                    matched_quotes.append(transcript[start:end].strip())

            if matched_quotes:
                category_triggered[category] = True
                signals_list.append(SignalItem(
                    category=category,
                    indicator=title,
                    triggered=True,
                    quotes=matched_quotes[:2],
                    weight=1.5 if severity == Severity.CRITICAL else (1.0 if severity == Severity.HIGH else 0.5)
                ))

                if title not in seen_titles:
                    seen_titles.add(title)
                    evidence_list.append(EvidenceItem(
                        category=category.replace("_", " ").title(),
                        severity=severity,
                        title=title,
                        explanation=explanation,
                        quote=matched_quotes[0],
                        icon=_get_icon_for_category(category)
                    ))

    summary = DeterministicSignals(
        urgency=category_triggered["urgency"],
        impersonation=category_triggered["impersonation"],
        credential_request=category_triggered["credential_request"],
        financial_request=category_triggered["financial_request"],
        remote_access_request=category_triggered["remote_access_request"],
        social_engineering=category_triggered["social_engineering"],
        signals=signals_list
    )

    return summary, evidence_list


def _get_icon_for_category(category: str) -> str:
    icons = {
        "credential_request": "key",
        "urgency": "clock",
        "impersonation": "user-x",
        "financial_request": "credit-card",
        "remote_access_request": "download",
        "social_engineering": "shield-alert"
    }
    return icons.get(category, "alert-circle")
