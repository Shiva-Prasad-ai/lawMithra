"""
AI4Bharat IndicTrans2 API Client.
Alternative open-source neural machine translation engine for Indian languages.
Endpoints configured via:
- INDICTRANS_ENDPOINT (e.g. self-hosted vLLM / IndicTrans2 FastAPI service)
- INDICTRANS_API_KEY (optional bearer token)
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional
from .statutory_guard import StatutoryGuard

logger = logging.getLogger('law_mithra.indictrans')


class IndicTransClient:
    """
    Client for IndicTrans2 translation endpoint.
    Guarantees statutory preservation through StatutoryGuard.
    """

    def __init__(self):
        self.endpoint = os.environ.get('INDICTRANS_ENDPOINT', '')
        self.api_key = os.environ.get('INDICTRANS_API_KEY', '')
        self.timeout_seconds = 5.0

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint)

    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        if not text or not text.strip() or source_lang == target_lang:
            return text

        if not self.is_configured:
            return None

        masked_text, token_map = StatutoryGuard.mask_statutory_entities(text)

        payload = {
            "text": masked_text,
            "source_language": source_lang,
            "target_language": target_lang
        }
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "LawMithra-LegalAI/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.endpoint, data=data_bytes, headers=headers, method='POST')

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    translated = data.get('translation') or data.get('translated_text', '')
                    if translated:
                        return StatutoryGuard.unmask_statutory_entities(translated, token_map)
        except Exception as e:
            logger.warning(f"IndicTrans2 request failed: {e}")

        return None

