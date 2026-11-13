"""
OpenRouter Document Modification Service for Law Mithra.
Uses OPENROUTER_API_KEY securely from environment variables.
"""

import os
import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any

OPENROUTER_MODELS = [
    'nvidia/nemotron-3.5-super-vl:free',
    'recursive/flint-v1.0:free',
    'liquid/lfm-2.5-2.6b:free',
]

class OpenRouterDocService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.timeout = 20

    def modify_or_analyze_document(
        self,
        document_text: str,
        instructions: str,
        language: str = 'en'
    ) -> Optional[str]:
        if not self.api_key:
            return None

        prompt = (
            f"You are Law Mithra Document Editor & Intelligence Engine for Indian legal documents.\n"
            f"Instructions / New Changes: {instructions}\n"
            f"Target Language: {language}\n\n"
            f"Document Content:\n\"\"\"\n{document_text}\n\"\"\"\n\n"
            f"Task: Modify and review the document according to the changes. Keep verified Indian statutory terms precise."
        )

        payload = {
            'messages': [
                {'role': 'system', 'content': 'You are an expert Indian legal document modifier and compliance analyst.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.1,
            'max_tokens': 1500,
        }
        body_bytes = json.dumps(payload).encode('utf-8')

        for model in OPENROUTER_MODELS:
            payload['model'] = model
            body_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                'https://openrouter.ai/api/v1/chat/completions',
                data=body_bytes,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://lawmithra.in',
                    'X-Title': 'Law Mithra',
                },
                method='POST'
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as res:
                    data = json.loads(res.read().decode('utf-8'))
                    choices = data.get('choices', [])
                    if choices:
                        msg = choices[0].get('message', {})
                        content = msg.get('content')
                        if content:
                            return content.strip()
            except (urllib.error.HTTPError, urllib.error.URLError, Exception):
                continue

        return None

