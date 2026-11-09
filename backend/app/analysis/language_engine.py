"""
BharatShield Voice - Multilingual & Code-Mixing Detection Engine
Detects English, Telugu, Hindi, and code-mixed conversations (e.g. Telugu + English).
"""

import re
from typing import Tuple, List
from app.analysis.schemas import LanguageDetectionResult

# Common Telugu romanized and native tokens
TELUGU_NATIVE_REGEX = re.compile(r"[\u0C00-\u0C7F]")
TELUGU_WORDS = {
    "meeru", "nenu", "andi", "cheppandi", "cheppanu", "ivvandi", "ippude", "ventane",
    "kavala", "undi", "ledu", "avtundi", "aipotundi", "cheyandi", "pampandi", "dabbu",
    "dabbulu", "namaskaram", "ela", "unnaru", "chudandi", "telusu", "ravali", "kavali",
    "call", "chestunnanu", "bank", "nunchi", "cheyali", "chustam"
}

# Common Hindi romanized and native tokens
HINDI_NATIVE_REGEX = re.compile(r"[\u0900-\u097F]")
HINDI_WORDS = {
    "aap", "hum", "main", "kya", "kyun", "kaise", "karein", "kijiye", "bataiye",
    "batayein", "bhejo", "turant", "abhi", "hoga", "hogi", "nahi", "raha", "rahe",
    "karo", "karna", "paisa", "paise", "namaste", "dalo", "dekh", "liye", "bol", "hoon"
}

ENGLISH_WORDS = {
    "the", "and", "is", "in", "to", "of", "you", "that", "it", "he", "was", "for",
    "on", "are", "as", "with", "his", "they", "at", "be", "this", "from", "have",
    "or", "by", "one", "had", "not", "but", "what", "all", "were", "when", "we",
    "there", "can", "an", "your", "which", "their", "if", "do", "will", "each",
    "about", "how", "up", "out", "them", "then", "she", "many", "some", "so", "these"
}


def detect_language_and_mixing(transcript: str, hint_language: str = "indic-auto") -> LanguageDetectionResult:
    """
    Analyzes script characters and lexical density to detect language and code-mixing.
    Distinguishes genuine multilingual code-mixing from occasional loan words.
    """
    text = transcript.strip()
    if not text:
        return LanguageDetectionResult(
            detected_language="Unknown",
            confidence=0.0,
            code_mixed=False,
            languages=[]
        )

    # 1. Native script detection
    telugu_native_chars = len(TELUGU_NATIVE_REGEX.findall(text))
    hindi_native_chars = len(HINDI_NATIVE_REGEX.findall(text))
    total_chars = max(1, len(text))

    if telugu_native_chars / total_chars > 0.15:
        # Check if there is also noticeable English script/words
        latin_words = len(re.findall(r"\b[a-zA-Z]{3,}\b", text))
        if latin_words >= 3:
            return LanguageDetectionResult(
                detected_language="Telugu + English",
                confidence=0.94,
                code_mixed=True,
                languages=["Telugu", "English"]
            )
        return LanguageDetectionResult(
            detected_language="Telugu",
            confidence=0.96,
            code_mixed=False,
            languages=["Telugu"]
        )

    if hindi_native_chars / total_chars > 0.15:
        latin_words = len(re.findall(r"\b[a-zA-Z]{3,}\b", text))
        if latin_words >= 3:
            return LanguageDetectionResult(
                detected_language="Hindi + English",
                confidence=0.94,
                code_mixed=True,
                languages=["Hindi", "English"]
            )
        return LanguageDetectionResult(
            detected_language="Hindi",
            confidence=0.96,
            code_mixed=False,
            languages=["Hindi"]
        )

    # 2. Tokenization for Romanized / Latin script Indic analysis
    tokens = [w.lower() for w in re.findall(r"\b[a-zA-Z]{2,}\b", text)]
    total_tokens = max(1, len(tokens))

    telugu_hits = sum(1 for w in tokens if w in TELUGU_WORDS)
    hindi_hits = sum(1 for w in tokens if w in HINDI_WORDS)
    english_hits = sum(1 for w in tokens if w in ENGLISH_WORDS)

    telugu_ratio = telugu_hits / total_tokens
    hindi_ratio = hindi_hits / total_tokens
    english_ratio = english_hits / total_tokens

    # Evaluate code-mixing patterns
    if telugu_hits >= 2 or telugu_ratio > 0.08:
        if english_hits >= 2 or "otp" in tokens or "bank" in tokens or "account" in tokens:
            return LanguageDetectionResult(
                detected_language="Telugu + English",
                confidence=0.92,
                code_mixed=True,
                languages=["Telugu", "English"]
            )
        return LanguageDetectionResult(
            detected_language="Telugu",
            confidence=0.90,
            code_mixed=False,
            languages=["Telugu"]
        )

    if hindi_hits >= 2 or hindi_ratio > 0.08:
        if english_hits >= 2 or "otp" in tokens or "bank" in tokens or "call" in tokens:
            return LanguageDetectionResult(
                detected_language="Hindi + English",
                confidence=0.92,
                code_mixed=True,
                languages=["Hindi", "English"]
            )
        return LanguageDetectionResult(
            detected_language="Hindi",
            confidence=0.90,
            code_mixed=False,
            languages=["Hindi"]
        )

    # Check hint if available
    if hint_language.startswith("te"):
        return LanguageDetectionResult(
            detected_language="Telugu + English",
            confidence=0.88,
            code_mixed=True,
            languages=["Telugu", "English"]
        )
    elif hint_language.startswith("hi"):
        return LanguageDetectionResult(
            detected_language="Hindi + English",
            confidence=0.88,
            code_mixed=True,
            languages=["Hindi", "English"]
        )

    # Default English
    return LanguageDetectionResult(
        detected_language="English",
        confidence=0.95 if english_ratio > 0.25 else 0.85,
        code_mixed=False,
        languages=["English"]
    )
