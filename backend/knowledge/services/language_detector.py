"""
Language Detection Service for Indian Legal Documents and Queries.
Supports: en, hi, kn, ta, te, ml, mr, bn, gu, pa.
Uses Unicode script frequency analysis and specific grammatical/lexical markers
to distinguish related scripts (e.g. Hindi vs Marathi in Devanagari).
"""

from typing import Tuple, Dict

# Unicode codepoint ranges for Indian scripts
SCRIPT_RANGES = {
    'kn': (0x0C80, 0x0CFF),  # Kannada
    'te': (0x0C00, 0x0C7F),  # Telugu
    'ta': (0x0B80, 0x0BFF),  # Tamil
    'ml': (0x0D00, 0x0D7F),  # Malayalam
    'bn': (0x0980, 0x09FF),  # Bengali
    'gu': (0x0A80, 0x0AFF),  # Gujarati
    'pa': (0x0A00, 0x0A7F),  # Gurmukhi / Punjabi
    'devanagari': (0x0900, 0x097F),  # Hindi / Marathi
    'en': (0x0041, 0x007A),  # Basic Latin
}

# Distinguishing lexical / postpositional markers for Marathi vs Hindi
MARATHI_MARKERS = [
    'आहे', 'नाही', 'आणि', 'मध्ये', 'करणे', 'झाले', 'केले', 'च्या', 'कडे', 'वर',
    'जमीन', 'अतिक्रमण', 'तक्रार', 'कायद्यानुसार', 'न्यायालय', 'अर्ज'
]

HINDI_MARKERS = [
    'है', 'नहीं', 'और', 'में', 'करना', 'हुआ', 'किया', 'के', 'पास', 'पर',
    'जमीन', 'कब्जा', 'शिकायत', 'कानून', 'अदालत', 'आवेदन', 'चाहिए'
]

SUPPORTED_LANGUAGES = {
    'en': {'name': 'English', 'native': 'English', 'script': 'Latin'},
    'hi': {'name': 'Hindi', 'native': 'हिन्दी', 'script': 'Devanagari'},
    'kn': {'name': 'Kannada', 'native': 'ಕನ್ನಡ', 'script': 'Kannada'},
    'ta': {'name': 'Tamil', 'native': 'தமிழ்', 'script': 'Tamil'},
    'te': {'name': 'Telugu', 'native': 'తెలుగు', 'script': 'Telugu'},
    'ml': {'name': 'Malayalam', 'native': 'മലയാളം', 'script': 'Malayalam'},
    'mr': {'name': 'Marathi', 'native': 'मराठी', 'script': 'Devanagari'},
    'bn': {'name': 'Bengali', 'native': 'বাংলা', 'script': 'Bengali'},
    'gu': {'name': 'Gujarati', 'native': 'ગુજરાતી', 'script': 'Gujarati'},
    'pa': {'name': 'Punjabi', 'native': 'ਪੰਜਾਬੀ', 'script': 'Gurmukhi'},
}


def detect_language(text: str, fallback: str = 'en') -> Tuple[str, float]:
    """
    Detects the primary Indian language from the given text.
    Returns a tuple of (language_code, confidence).
    """
    if not text or not text.strip():
        return fallback, 1.0

    char_counts: Dict[str, int] = {
        'kn': 0, 'te': 0, 'ta': 0, 'ml': 0,
        'bn': 0, 'gu': 0, 'pa': 0, 'devanagari': 0, 'en': 0
    }
    total_analyzable = 0

    for char in text:
        cp = ord(char)
        for lang, (start, end) in SCRIPT_RANGES.items():
            if start <= cp <= end:
                char_counts[lang] += 1
                total_analyzable += 1
                break

    if total_analyzable == 0:
        return fallback, 0.5

    # Find dominant script
    dominant_script = max(char_counts, key=char_counts.get)
    dominance_ratio = char_counts[dominant_script] / total_analyzable

    # Disambiguate Devanagari into Hindi vs Marathi
    if dominant_script == 'devanagari':
        words = text.split()
        mr_matches = sum(1 for w in words if any(m in w for m in MARATHI_MARKERS))
        hi_matches = sum(1 for w in words if any(m in w for m in HINDI_MARKERS))

        if mr_matches > hi_matches:
            return 'mr', min(1.0, dominance_ratio + 0.1)
        else:
            return 'hi', min(1.0, dominance_ratio + 0.1)

    # Return script code directly for 1:1 scripts
    confidence = min(1.0, dominance_ratio)
    return dominant_script, confidence

