"""
Bhashini (National Language Translation Mission - NLTM) API Client.
Connects securely to the Government of India's Bhashini ULCA platform.
Credentials loaded strictly from environment variables:
- BHASHINI_USER_ID
- BHASHINI_API_KEY
- BHASHINI_PIPELINE_ID
- BHASHINI_INFERENCE_URL
"""

import os
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict
from .statutory_guard import StatutoryGuard

logger = logging.getLogger('law_mithra.bhashini')

# In-memory translation cache: (source_lang, target_lang, text) -> translated_text
_TRANSLATION_CACHE: Dict[tuple, str] = {}


class BhashiniClient:
    """
    Client for Bhashini Indic translation pipeline.
    Ensures legal statutory tokens are masked before MT and unmasked after.
    """

    def __init__(self):
        self.user_id = os.environ.get('BHASHINI_USER_ID', '')
        self.api_key = os.environ.get('BHASHINI_API_KEY', '')
        self.pipeline_id = os.environ.get('BHASHINI_PIPELINE_ID', '')
        self.inference_url = os.environ.get(
            'BHASHINI_INFERENCE_URL',
            'https://dhruva-api.bhashini.gov.in/services/inference/pipeline'
        )
        self.timeout_seconds = 5.0
        self.max_retries = 2

    @property
    def is_configured(self) -> bool:
        """Returns True only when valid external Bhashini credentials are provided."""
        return bool(self.user_id and self.api_key and self.pipeline_id)

    def translate(self, text: str, source_lang: str, target_lang: str) -> Optional[str]:
        """
        Translates text from source_lang to target_lang using Bhashini.
        Preserves statutory numbers via StatutoryGuard masking.
        """
        if not text or not text.strip():
            return text
        if source_lang == target_lang:
            return text

        cache_key = (source_lang, target_lang, text)
        if cache_key in _TRANSLATION_CACHE:
            return _TRANSLATION_CACHE[cache_key]

        if not self.is_configured:
            logger.info("Bhashini credentials not set; proceeding with local legal translation fallback.")
            return None

        # Mask legal sections, penalties, fines so MT cannot alter them
        masked_text, token_map = StatutoryGuard.mask_statutory_entities(text)

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "translation",
                    "config": {
                        "language": {
                            "sourceLanguage": source_lang,
                            "targetLanguage": target_lang
                        }
                    }
                }
            ],
            "inputData": {
                "input": [{"source": masked_text}]
            }
        }

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "LawMithra-LegalAI/1.0",
            "userID": self.user_id,
            "ulcaApiKey": self.api_key,
        }

        data_bytes = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(self.inference_url, data=data_bytes, headers=headers, method='POST')

        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    if response.status == 200:
                        res_data = json.loads(response.read().decode('utf-8'))
                        # Extract output from ULCA response schema
                        pipeline_response = res_data.get('pipelineResponse', [])
                        if pipeline_response and 'output' in pipeline_response[0]:
                            raw_mt_output = pipeline_response[0]['output'][0].get('target', '')
                            # Unmask statutory tokens verbatim
                            final_text = StatutoryGuard.unmask_statutory_entities(raw_mt_output, token_map)
                            _TRANSLATION_CACHE[cache_key] = final_text
                            return final_text
            except urllib.error.HTTPError as e:
                logger.warning(f"Bhashini HTTP Error {e.code} on attempt {attempt + 1}: {e.reason}")
            except urllib.error.URLError as e:
                logger.warning(f"Bhashini Network Error on attempt {attempt + 1}: {e.reason}")
            except Exception as e:
                logger.warning(f"Bhashini unexpected error on attempt {attempt + 1}: {e}")

        return None

