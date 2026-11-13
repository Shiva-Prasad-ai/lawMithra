"""
Statutory Guard Service for Indian Legal AI.
Enforces Rule 6: Absolute preservation of statutory section numbers, Act citations,
penalties, imprisonment durations, fines, and legal citations during machine translation.
"""

import re
from typing import Tuple, List, Dict

# Regex patterns for immutable legal facts
STATUTORY_PATTERNS = [
    # Legal sections (e.g. "Section 498A", "Sec. 420 IPC", "u/s 138 NI Act", "Order 39 Rule 1 CPC")
    r'\b(?:Section|Sec\.?|S\.?|u\/s|U\/Sec\.?)\s+[0-9]+[A-Za-z]?(?:\([0-9a-zA-Z]+\))*(?:\s+(?:of\s+the\s+|of\s+)?[A-Za-z\.\s]+(?:Act|Code|Sanhita|IPC|BNS|CrPC|BNSS|CPC|NI\s+Act|IEA|BSA))?',
    # Specific Order & Rule citations in CPC
    r'\bOrder\s+[0-9IVXLCDM]+\s+Rule\s+[0-9]+(?:\s+of\s+CPC)?',
    # Law Acts and Codes
    r'\b(?:Indian\s+Penal\s+Code|Bharatiya\s+Nyaya\s+Sanhita|Code\s+of\s+Criminal\s+Procedure|Bharatiya\s+Nagarik\s+Suraksha\s+Sanhita|Code\s+of\s+Civil\s+Procedure|Specific\s+Relief\s+Act(?:\s+1963)?|Transfer\s+of\s+Property\s+Act(?:\s+1882)?|Negotiable\s+Instruments\s+Act(?:\s+1881)?|Constitution\s+of\s+India)\b',
    # Imprisonment periods
    r'\b(?:[0-9]+(?:\s*-\s*[0-9]+)?\s*(?:years?|months?|days?)\s+(?:imprisonment|rigorous\s+imprisonment|simple\s+imprisonment|jail)|life\s+imprisonment)\b',
    # Fines & monetary amounts
    r'(?:₹|Rs\.?|INR)\s*[0-9]+(?:,[0-9]+)*(?:\.[0-9]{2})?',
    # Legal citations (AIR, SCC, SCR)
    r'\b(?:AIR\s+[0-9]{4}\s+(?:SC|Del|Bom|Mad|Kar)\s+[0-9]+|\([0-9]{4}\)\s+[0-9]+\s+SCC\s+[0-9]+|[0-9]{4}\s+INSC\s+[0-9]+)\b',
]

COMBINED_GUARD_RE = re.compile('|'.join(f'({p})' for p in STATUTORY_PATTERNS), re.IGNORECASE)


class StatutoryGuard:
    """
    Safely masks statutory elements before machine translation and restores
    them verbatim after translation, ensuring 0% corruption of legal numbers.
    """

    @classmethod
    def mask_statutory_entities(cls, text: str) -> Tuple[str, Dict[str, str]]:
        """
        Replaces protected legal entities with immutable placeholder tokens like __STAT_GUARD_0__.
        Returns the masked text and the token-to-original dictionary.
        """
        token_map: Dict[str, str] = {}
        counter = 0

        def replace_match(match):
            nonlocal counter
            original = match.group(0)
            token = f"__STAT_GUARD_{counter}__"
            token_map[token] = original
            counter += 1
            return token

        masked_text = COMBINED_GUARD_RE.sub(replace_match, text)
        return masked_text, token_map

    @classmethod
    def unmask_statutory_entities(cls, text: str, token_map: Dict[str, str]) -> str:
        """
        Restores masked statutory tokens back to their exact original text verbatim.
        """
        restored = text
        for token, original in token_map.items():
            # Account for any whitespace that may have been added by MT around tokens
            pattern = re.escape(token).replace(r'\_', r'\s*_\s*')
            restored = re.sub(pattern, original, restored)
        return restored

    @classmethod
    def validate_preservation(cls, original_text: str, translated_text: str) -> Tuple[bool, List[str]]:
        """
        Verifies that every Section number, fine, and penalty present in the source
        is strictly present in the translated text.
        """
        missing = []
        source_matches = [m.group(0).strip() for m in COMBINED_GUARD_RE.finditer(original_text)]
        for item in source_matches:
            # Check if this item is present in translated text
            if item not in translated_text:
                missing.append(item)

        is_valid = (len(missing) == 0)
        return is_valid, missing

