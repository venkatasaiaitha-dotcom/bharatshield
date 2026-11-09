"""
BharatShield Voice - Natural Multilingual Output Generator
Generates localized explanations for English, Telugu (natural everyday spoken style), and Hindi.
Ensures identical underlying risk scoring while providing accessible native-language guidance.
"""

from typing import Dict
from app.analysis.schemas import InvestigationResult, RiskLevel, LocalizedExplanation


def generate_multilingual_explanations(investigation: InvestigationResult) -> Dict[str, LocalizedExplanation]:
    """
    Produces structured localized explanations in English, Telugu, and Hindi.
    """
    level = investigation.risk_level
    score = investigation.risk_score

    # --- 1. ENGLISH ---
    en_spoken = (
        f"This call was assessed with an AI risk score of {score} out of 100. "
        + ("Please do not share any OTP, PIN, or password with the caller. Disconnect immediately."
           if level in (RiskLevel.CRITICAL, RiskLevel.HIGH) else
           "No immediate danger was detected, but never disclose personal financial information over phone calls.")
    )

    en_explanation = LocalizedExplanation(
        language_code="en",
        language_name="English",
        summary=investigation.summary,
        explanation=investigation.explanation,
        recommended_actions=investigation.recommended_actions,
        do_not_do=investigation.do_not_do,
        spoken_summary=en_spoken
    )

    # --- 2. TELUGU (Natural, conversational everyday Telugu) ---
    if level == RiskLevel.CRITICAL:
        te_summary = "చాలా ప్రమాదకరమైన కాల్ సంకేతాలు గుర్తించబడ్డాయి. అవతలి వ్యక్తి మీ రహస్య వివరాలను అడిగారు."
        te_explanation = (
            f"ఈ కాల్‌కు మా AI భద్రతా వ్యవస్థ {score}/100 రిస్క్ స్కోర్ ఇచ్చింది. "
            "కాలర్ మీ బ్యాంక్ వివరాలు, OTP లేదా స్క్రీన్ షేరింగ్ కోరారు. "
            "ఏ బ్యాంక్ లేదా ప్రభుత్వ అధికారి ఫోన్‌లో ఎప్పుడూ OTP లేదా పాస్‌వర్డ్ అడగరని గుర్తుంచుకోండి."
        )
        te_actions = [
            "కాల్ వెంటనే కట్ చేయండి.",
            "ఒకవేళ మీరు ఇప్పటికే OTP చెప్పి ఉంటే, వెంటనే మీ బ్యాంక్ కస్టమర్ కేర్‌కు ఫోన్ చేసి కార్డు బ్లాక్ చేయించండి.",
            "సైబర్ క్రైమ్ హెల్ప్‌లైన్ 1930 కు వెంటనే ఫిర్యాదు చేయండి."
        ]
        te_do_not = [
            "ఎవరితోనూ మీ OTP, UPI పిన్ లేదా పాస్‌వర్డ్ ఎట్టిపరిస్థితుల్లోనూ చెప్పకండి.",
            "కాలర్ చెప్పిన యాప్‌లను (AnyDesk, TeamViewer వంటివి) మీ ఫోన్‌లో ఇన్‌స్టాల్ చేయకండి."
        ]
        te_spoken = (
            f"ఈ కాల్లో OTP అడగడం మరియు వెంటనే చర్య తీసుకోవాలని ఒత్తిడి చేయడం ప్రమాదకరమైన సంకేతాలు. "
            f"రిస్క్ స్కోర్ నూటికి {score}. మీ OTP ఎవరితోనూ పంచుకోకండి, కాల్ వెంటనే కట్ చేయండి."
        )
    elif level == RiskLevel.HIGH:
        te_summary = "అనుమానాస్పద కాల్. ఖాతా రద్దు చేస్తామని లేదా ముందస్తు ఫీజు చెల్లించాలని ఒత్తిడి చేశారు."
        te_explanation = (
            f"ఈ కాల్‌కు {score}/100 రిస్క్ స్కోర్ వచ్చింది. "
            "కాలర్ మిమ్మల్ని భయపెట్టి వెంటనే డబ్బులు పంపాలని లేదా సమాచారం ఇవ్వాలని ఒత్తిడి తెచ్చారు."
        )
        te_actions = [
            "ఫోన్ కాల్ కట్ చేసి సమాచారాన్ని సొంతంగా ధృవీకరించుకోండి.",
            "బ్యాంక్ అధికారిక వెబ్‌సైట్ లేదా శాఖకు వెళ్లి మాత్రమే సమాచారం ఇవ్వండి."
        ]
        te_do_not = [
            "అపరిచిత వ్యక్తులకు లేదా ఉద్యోగాల కోసం ముందస్తు రుసుములు చెల్లించకండి.",
            "కాలర్ పంపిన అనుమానాస్పద లింకులను క్లిక్ చేయకండి."
        ]
        te_spoken = (
            f"ఈ కాల్ చాలా అనుమానాస్పదంగా ఉంది. రిస్క్ స్కోర్ {score}. "
            "ఎటువంటి డబ్బులు ట్రాన్స్‌ఫర్ చేయకండి మరియు మీ రహస్య సమాచారాన్ని ఇవ్వకండి."
        )
    elif level == RiskLevel.MEDIUM:
        te_summary = "మధ్యస్థ స్థాయి రిస్క్. కాల్‌లో కొన్ని అనుమానాస్పద అంశాలు గమనించబడ్డాయి."
        te_explanation = (
            f"ఈ కాల్‌కు {score}/100 రిస్క్ స్కోర్ ఉంది. "
            "ప్రత్యక్షంగా మోసం ధృవీకరించబడకపోయినా, జాగ్రత్తగా ఉండటం ఎంతో ముఖ్యం."
        )
        te_actions = [
            "కాలర్ గుర్తింపును స్వతంత్రంగా నిర్ధారించుకోండి.",
            "అధికారిక కస్టమర్ కేర్ నంబర్‌కు మాత్రమే కాల్ చేయండి."
        ]
        te_do_not = [
            "కాలర్ ఇచ్చిన ఫోన్ నంబర్లకు తిరిగి కాల్ చేయకండి."
        ]
        te_spoken = f"ఈ కాల్‌లో కొన్ని అనుమానాలు ఉన్నాయి. రిస్క్ స్కోర్ {score}. వ్యక్తిగత వివరాలను ధృవీకరించకుండా పంచుకోవద్దు."
    else:
        te_summary = "ఎటువంటి తీవ్రమైన మోసపూరిత సంకేతాలు గుర్తించబడలేదు."
        te_explanation = (
            f"ఈ కాల్‌కు రిస్క్ స్కోర్ {score}/100 వచ్చింది. "
            "ఇది సాధారణ సంభాషణగా కనిపిస్తోంది. అయితే భద్రతా నియమాలు ఎల్లప్పుడూ పాటించండి."
        )
        te_actions = ["ఎల్లప్పుడూ అప్రమత్తంగా ఉండండి."]
        te_do_not = ["ఫోన్ కాల్స్‌లో ఎవరికీ మీ బ్యాంక్ పాస్‌వర్డ్‌లు చెప్పకండి."]
        te_spoken = f"ఈ సంభాషణలో ప్రస్తుతానికి ఎలాంటి మోసం సంకేతాలు కనిపించలేదు. రిస్క్ స్కోర్ {score}."

    te_explanation_obj = LocalizedExplanation(
        language_code="te",
        language_name="తెలుగు",
        summary=te_summary,
        explanation=te_explanation,
        recommended_actions=te_actions,
        do_not_do=te_do_not,
        spoken_summary=te_spoken
    )

    # --- 3. HINDI ---
    if level == RiskLevel.CRITICAL:
        hi_summary = "अत्यधिक जोखिम वाला कॉल। कॉलर ने आपकी गोपनीय बैंकिंग जानकारी या ओटीपी की मांग की है।"
        hi_explanation = (
            f"इस कॉल का AI रिस्क स्कोर {score}/100 आंका गया है। "
            "कॉलर ने आपसे संवेदनशील जानकारी (जैसे OTP, PIN या स्क्रीन शेयर) मांगी है। "
            "कोई भी बैंक या पुलिस अधिकारी फोन पर कभी भी OTP नहीं मांगते।"
        )
        hi_actions = [
            "कॉल तुरंत काट दें।",
            "यदि आपने अनजाने में OTP बता दिया है, तो तुरंत अपने बैंक के हेल्पलाइन नंबर पर संपर्क कर खाता सुरक्षित करें।",
            "साइबर अपराध हेल्पलाइन 1930 पर तुरंत सूचना दें।"
        ]
        hi_do_not = [
            "अपना OTP, UPI PIN या पासवर्ड किसी के साथ भी साझा न करें।",
            "कॉलर के कहने पर कोई भी ऐप (जैसे AnyDesk, TeamViewer) डाउनलोड न करें।"
        ]
        hi_spoken = (
            f"इस कॉल में OTP मांगना और तुरंत दबाव बनाना खतरे का संकेत है। रिस्क स्कोर {score} है। "
            "अपना OTP किसी को न बताएं और कॉल तुरंत काट दें।"
        )
    elif level == RiskLevel.HIGH:
        hi_summary = "संदिग्ध कॉल। खाता बंद होने का डर या अग्रिम शुल्क की मांग की गई है।"
        hi_explanation = (
            f"इस बातचीत को {score}/100 का उच्च जोखिम स्कोर दिया गया है। "
            "कॉलर ने आपको डराकर तुरंत पैसे ट्रांसफर करने या फ़ॉर्म भरने का दबाव बनाया।"
        )
        hi_actions = [
            "कॉल समाप्त करें और संबंधित संस्था से आधिकारिक माध्यम से संपर्क करें।",
            "बैंक की निकटतम शाखा में जाकर स्थिति सत्यापित करें।"
        ]
        hi_do_not = [
            "नौकरी या लॉटरी के नाम पर कोई भी अग्रिम पंजीकरण शुल्क न दें।",
            "अज्ञात लिंक पर क्लिक न करें।"
        ]
        hi_spoken = f"यह कॉल संदिग्ध प्रतीत होती है। रिस्क स्कोर {score} है। कोई भी भुगतान न करें।"
    elif level == RiskLevel.MEDIUM:
        hi_summary = "मध्यम जोखिम। बातचीत में कुछ संदिग्ध संकेत पाए गए।"
        hi_explanation = (
            f"इस कॉल को {score}/100 का रिस्क स्कोर मिला है। "
            "सत्यापन के बिना कोई भी व्यक्तिगत विवरण साझा न करें।"
        )
        hi_actions = ["कंपनी की आधिकारिक वेबसाइट से नंबर लेकर ही बात करें।"]
        hi_do_not = ["कॉलर द्वारा दिए गए नंबरों पर वापस कॉल न करें।"]
        hi_spoken = f"इस कॉल में कुछ असामान्य बातें पाई गईं। रिस्क स्कोर {score} है। सतर्क रहें।"
    else:
        hi_summary = "कोई स्पष्ट धोखाधड़ी या जोखिम का संकेत नहीं मिला।"
        hi_explanation = f"इस कॉल का रिस्क स्कोर {score}/100 है। यह सामान्य सेवा कॉल लग रही है।"
        hi_actions = ["हमेशा सतर्क रहें।"]
        hi_do_not = ["फोन पर पासवर्ड या पिन साझा न करें।"]
        hi_spoken = f"इस बातचीत में कोई खतरा नहीं पाया गया। रिस्क स्कोर {score} है।"

    hi_explanation_obj = LocalizedExplanation(
        language_code="hi",
        language_name="हिन्दी",
        summary=hi_summary,
        explanation=hi_explanation,
        recommended_actions=hi_actions,
        do_not_do=hi_do_not,
        spoken_summary=hi_spoken
    )

    return {
        "en": en_explanation,
        "te": te_explanation_obj,
        "hi": hi_explanation_obj
    }
