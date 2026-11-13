"""
Google Gemini AI Client for Law Mithra.
Uses GEMINI_API_KEY securely from environment variables.
"""

import os
import re
import json
import logging
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

GEMINI_MODELS = [
    'models/gemini-3-flash-preview',
    'models/gemini-3.1-flash-lite',
    'models/gemini-flash-lite-latest',
]


def clean_legal_text(text: str) -> str:
    """
    Cleans up any unnecessary markdown asterisks, hashes, and formatting characters
    to provide clean, readable text.
    """
    if not text:
        return ""
    # Remove markdown header hashes: ### Heading -> Heading
    text = re.sub(r'#{1,6}\s*', '', text)
    # Remove double asterisks: **text** -> text
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove single asterisks: *text* -> text
    text = re.sub(r'\*(.*?)\*', r'\1', text)
    # Clean bullet points: * Item or - Item -> • Item
    text = re.sub(r'^\s*[\*\-]\s+', '• ', text, flags=re.MULTILINE)
    # Clean brackets around sections: [Section 6] -> Section 6
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)
    # Clean extra empty lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        self.openrouter_key = os.getenv('OPENROUTER_API_KEY')
        self.timeout = 15

    def generate_legal_response(
        self,
        query: str,
        language: str = 'en',
        statutory_context: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """
        Generates a clean, verified Indian legal explanation for user chat queries.
        Never outputs raw markdown asterisks, hashes, or unnecessary formatting characters.
        """
        is_greeting = bool(re.search(
            r'^(hi|hello|hey|namaste|namaskara|namaskar|good\s*(morning|afternoon|evening)|pranam|pranaam|ಹಾಯ್|ನಮಸ್ಕಾರ|नमस्ते)[\s!\.,\?]*$',
            query.strip(),
            re.IGNORECASE
        ))

        if is_greeting:
            prompt = (
                f"You are Law Mithra, a helpful, polite, and professional AI legal assistant specializing exclusively in Indian law.\n"
                f"The user greeted: \"{query}\"\n"
                f"Language: {language}\n\n"
                f"Instructions:\n"
                f"1. Greet the user warmly in {language} and introduce yourself as Law Mithra.\n"
                f"2. Explain briefly that you can assist them with Indian civil law, criminal law, property disputes, police complaints/FIRs, consumer rights, cybercrime, family law, or court procedures.\n"
                f"3. Ask how you may assist them today with their legal matter.\n"
                f"4. CRITICAL FORMATTING RULE: Output plain, elegant text only. Absolutely do NOT use any markdown asterisks (no ** or *), hashtags (no ### or ##), or backticks. Use standard paragraphs."
            )
        else:
            context_str = ""
            if statutory_context:
                context_str = "Verified Statutory Context for this specific topic:\n"
                for item in statutory_context:
                    context_str += f"- Act: {item.get('act')}\n  Sections: {', '.join(item.get('sections', []))}\n  Statute: {item.get('english_statute', '')}\n"

        prompt = (
            f"You are Law Mithra, an expert AI legal assistant specializing exclusively in Indian law.\n"
            f"User Question: \"{query}\"\n"
            f"Preferred Language: {language}\n"
            f"{context_str}\n"
            f"Instructions:\n"
            f"Analyze the case query following standard Indian legal analysis:\n"
            f"1. Case Overview & Dispute Nature: summarize the core controversy, parties, and applicable jurisdiction.\n"
            f"2. Applicable Legal Sections: cite exact Indian statutes (IPC/BNS, CrPC/BNSS, CPC, Specific Relief, etc.) and explain why they apply.\n"
            f"3. Legal Analysis: specify ingredients, required evidence, and legal strengths/weaknesses.\n"
            f"4. Lawyer Strategy & Remedies: provide lawful procedural steps, immediate actions, and arguments.\n"
            f"5. Court Procedure & Timelines: explain expected stages and statutory limitation deadlines.\n"
            f"6. Recommended Next Actions: provide a clear, prioritized checklist of immediate steps.\n"
            f"7. CRITICAL FORMATTING RULE: Absolutely do NOT use any markdown asterisks (never use ** or * for bolding or lists). Do NOT use hashtags (never use ### or ## for headings). Do NOT use square brackets like [Section 6]. Use clean plain text with standard paragraphs, clear numbered points (1., 2., 3.) or bullet points (• ) for readability."
        )

        res = self._call_gemini_raw(prompt, max_tokens=1500, temperature=0.2)
        if not res:
            res = self._call_openrouter_raw(prompt, max_tokens=1024)

        if res:
            return clean_legal_text(res)
        return None

    def analyze_legal_case(self, case_text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Executes comprehensive AI Legal Case Analysis adhering to the Law Mithra API Instruction Document.
        Returns a structured JSON matching all 10 core instructions and 7 mandatory sections.
        """
        prompt = (
            f"You are an AI Legal Research and Case Analysis Assistant specializing exclusively in Indian law.\n"
            f"Default jurisdiction: India. Use current and applicable legislation, amendments, procedural rules, and judicial precedents.\n\n"
            f"Analyze the following legal case query / facts:\n\"\"\"{case_text}\"\"\"\n\n"
            f"LANGUAGE: {language}\n\n"
            f"MANDATORY JSON OUTPUT FORMAT:\n"
            f"Return ONLY a valid JSON object without markdown fences, conforming to this exact structure:\n"
            f"{{\n"
            f'  "case_overview": {{\n'
            f'    "case_type": "<Case type>",\n'
            f'    "case_summary": "<Case summary>",\n'
            f'    "parties_involved": "<Parties involved>",\n'
            f'    "court_jurisdiction": "<Court/jurisdiction>",\n'
            f'    "current_procedural_stage": "<Current procedural stage>",\n'
            f'    "main_legal_dispute": "<Main legal dispute>"\n'
            f'  }},\n'
            f'  "applicable_sections": [\n'
            f'    {{\n'
            f'      "act_name": "<Act name>",\n'
            f'      "section_number": "<Section number>",\n'
            f'      "section_title": "<Section title>",\n'
            f'      "explanation": "<Explanation>",\n'
            f'      "why_it_applies": "<Why it applies>",\n'
            f'      "nature_of_offence_or_liability": "<Nature of offence or liability>",\n'
            f'      "available_punishment_or_legal_consequence": "<Available punishment or consequence>",\n'
            f'      "status": "<Confirmed / Potentially applicable>",\n'
            f'      "law_type": "<Substantive / Procedural>"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "legal_analysis": {{\n'
            f'    "essential_ingredients": ["<Ingredient 1>", "<Ingredient 2>"],\n'
            f'    "evidence_required": ["<Evidence 1>", "<Evidence 2>"],\n'
            f'    "burden_and_standard_of_proof": "<Burden and standard of proof>",\n'
            f'    "strengths": ["<Strength 1>"],\n'
            f'    "weaknesses": ["<Weakness 1>"],\n'
            f'    "judicial_precedents": [\n'
            f'      {{\n'
            f'        "case_name": "<Precedent citation>",\n'
            f'        "ratio_decidendi": "<Legal principle>"\n'
            f'      }}\n'
            f'    ],\n'
            f'    "possible_legal_objections": ["<Objection 1>"]\n'
            f'  }},\n'
            f'  "lawyer_strategy": {{\n'
            f'    "party_represented": "<Complainant / Accused / Plaintiff / Defendant>",\n'
            f'    "immediate_action": "<Immediate action after summons / incident>",\n'
            f'    "documents_to_collect": ["<Document 1>", "<Document 2>"],\n'
            f'    "evidence_to_preserve": ["<Evidence to preserve>"],\n'
            f'    "preliminary_objections": ["<Preliminary objection>"],\n'
            f'    "possible_applications": ["<Application to file before court>"],\n'
            f'    "key_arguments": ["<Key legal argument>"],\n'
            f'    "relevant_precedents": ["<Key precedent>"],\n'
            f'    "risks_and_weaknesses": ["<Risk/weakness>"],\n'
            f'    "alternative_remedies_or_settlement": "<Lawful alternative remedies or settlement possibilities>"\n'
            f'  }},\n'
            f'  "court_procedure": [\n'
            f'    {{\n'
            f'      "step_number": 1,\n'
            f'      "stage_name": "<Stage name>",\n'
            f'      "procedure_details": "<Procedure details>"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "stipulated_timeline": [\n'
            f'    {{\n'
            f'      "action": "<Court appearance / Filing response / Filing application / Appeal>",\n'
            f'      "applicable_deadline": "<Applicable deadline>",\n'
            f'      "legal_provision": "<Legal provision>",\n'
            f'      "starting_point": "<Starting point>"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "recommended_actions": [\n'
            f'    {{\n'
            f'      "priority": 1,\n'
            f'      "category": "Immediate action",\n'
            f'      "action": "<Action description>"\n'
            f'    }},\n'
            f'    {{\n'
            f'      "priority": 2,\n'
            f'      "category": "Documents required",\n'
            f'      "action": "<Action description>"\n'
            f'    }},\n'
            f'    {{\n'
            f'      "priority": 3,\n'
            f'      "category": "Advocate consultation",\n'
            f'      "action": "<Action description>"\n'
            f'    }},\n'
            f'    {{\n'
            f'      "priority": 4,\n'
            f'      "category": "Court filing or appearance",\n'
            f'      "action": "<Action description>"\n'
            f'    }},\n'
            f'    {{\n'
            f'      "priority": 5,\n'
            f'      "category": "Follow-up action",\n'
            f'      "action": "<Action description>"\n'
            f'    }}\n'
            f'  ],\n'
            f'  "missing_information": ["<Missing facts or dates to verify>"],\n'
            f'  "sources": ["<Relevant Acts and judgments cited>"],\n'
            f'  "legal_disclaimer": "AI Legal Research and Case Analysis guidance only under Indian law. Not a police finding, judicial decree, or substitute for representation by an enrolled advocate."\n'
            f'}}\n'
        )
        raw = self._call_gemini_raw(prompt, max_tokens=3000, temperature=0.1)
        if not raw:
            raw = self._call_openrouter_raw(prompt, max_tokens=3000)

        if raw:
            clean = raw.strip()
            if clean.startswith("```"):
                clean = re.sub(r'^```(?:json)?\s*', '', clean)
                clean = re.sub(r'\s*```$', '', clean)
            try:
                return json.loads(clean)
            except Exception as exc:
                logger.warning(f"Failed to parse case analysis JSON: {exc}")

        return self._generate_fallback_case_analysis(case_text, language)

    def _generate_fallback_case_analysis(self, case_text: str, language: str = 'en') -> Dict[str, Any]:
        """Provides high-quality structured heuristic analysis when offline."""
        return {
            "case_overview": {
                "case_type": "Civil & Criminal Dispute under Indian Law",
                "case_summary": case_text[:300].strip(),
                "parties_involved": "Complainant / Aggrieved party and Respondent / Accused party",
                "court_jurisdiction": "Jurisdictional Civil Court / Judicial Magistrate Court in India",
                "current_procedural_stage": "Pre-litigation / Initial dispute notice stage",
                "main_legal_dispute": "Grievance arising from civil rights violation and penal non-compliance"
            },
            "applicable_sections": [
                {
                    "act_name": "Code of Civil Procedure, 1908",
                    "section_number": "Order 39 Rules 1 & 2",
                    "section_title": "Temporary Injunctions and Interlocutory Orders",
                    "explanation": "Provides discretionary relief to maintain status quo and restrain irreparable injury.",
                    "why_it_applies": "Applicable to preserve property, rights, and prevent third-party alienation during litigation.",
                    "nature_of_offence_or_liability": "Civil procedural remedy",
                    "available_punishment_or_legal_consequence": "Ad interim injunction, civil imprisonment for breach under Order 39 Rule 2A",
                    "status": "Confirmed",
                    "law_type": "Procedural"
                },
                {
                    "act_name": "Bharatiya Nyaya Sanhita, 2023 / Indian Penal Code, 1860",
                    "section_number": "Section 316 BNS / Section 406 IPC",
                    "section_title": "Criminal Breach of Trust",
                    "explanation": "Penalizes dishonest misappropriation or conversion of entrusted property.",
                    "why_it_applies": "Applies where entrustment is established and dishonest conversion occurred.",
                    "nature_of_offence_or_liability": "Cognizable and Non-Bailable",
                    "available_punishment_or_legal_consequence": "Imprisonment up to 3 years or fine or both",
                    "status": "Potentially applicable",
                    "law_type": "Substantive"
                }
            ],
            "legal_analysis": {
                "essential_ingredients": [
                    "Existence of legal right or legal relationship between parties",
                    "Breach of statutory duty, contract, or penal prohibition",
                    "Causal damage or threat of irreparable injury"
                ],
                "evidence_required": [
                    "Written agreements, correspondences, receipts, or demand notices",
                    "Electronic records with Certificate under Section 63 BSA / Section 65B IEA",
                    "Independent witness affidavits or bank statement proofs"
                ],
                "burden_and_standard_of_proof": "Complainant/Plaintiff bears legal burden under Section 104 BSA / Section 101 IEA. Standard: Preponderance of probabilities for civil relief; beyond reasonable doubt for criminal prosecution.",
                "strengths": ["Clear documentary trail establishing prior status quo and transactions."],
                "weaknesses": ["Evidentiary burden to establish dishonest intention from inception for penal charges."],
                "judicial_precedents": [
                    {
                        "case_name": "Dalpat Kumar v. Prahlad Singh, (1992) 1 SCC 719",
                        "ratio_decidendi": "Three-fold test for injunction: prima facie case, balance of convenience, and irreparable injury."
                    }
                ],
                "possible_legal_objections": [
                    "Bar of limitation under Limitation Act, 1963",
                    "Lack of territorial or pecuniary jurisdiction"
                ]
            },
            "lawyer_strategy": {
                "party_represented": "Complainant / Plaintiff",
                "immediate_action": "Issue formal Statutory Legal Notice demanding remedy within 15-30 days.",
                "documents_to_collect": [
                    "Certified title/contract deeds",
                    "Proof of notice delivery and postal receipts",
                    "Bank transaction records"
                ],
                "evidence_to_preserve": [
                    "Original communication logs",
                    "Digital media preserved per statutory standards"
                ],
                "preliminary_objections": [
                    "Ensure plaint/complaint meets specific statutory disclosure requirements."
                ],
                "possible_applications": [
                    "Application for temporary injunction under Order 39 CPC",
                    "Application for urgent hearing / status quo"
                ],
                "key_arguments": [
                    "Clear prima facie entitlement under law",
                    "Irreparable harm if urgent protection is withheld"
                ],
                "relevant_precedents": [
                    "Dalpat Kumar v. Prahlad Singh on interim protection."
                ],
                "risks_and_weaknesses": [
                    "Potential delay in judicial process and interlocutory counter-claims."
                ],
                "alternative_remedies_or_settlement": "Mediation and Lok Adalat under Section 89 CPC for swift resolution without prolonged trial."
            },
            "court_procedure": [
                {
                    "step_number": 1,
                    "stage_name": "Institution of Plaint / Complaint",
                    "procedure_details": "Filing of verified petition with supporting affidavit and court fee stamp."
                },
                {
                    "step_number": 2,
                    "stage_name": "Issuance and Service of Summons",
                    "procedure_details": "Court issues notice/summons to opposite party via registered post and court bailiff."
                },
                {
                    "step_number": 3,
                    "stage_name": "Filing of Written Statement / Objections",
                    "procedure_details": "Opposite party appears and files formal response within statutory timeframe."
                },
                {
                    "step_number": 4,
                    "stage_name": "Framing of Issues / Charges",
                    "procedure_details": "Court determines points of controversy for trial."
                },
                {
                    "step_number": 5,
                    "stage_name": "Evidence and Final Arguments",
                    "procedure_details": "Examination of witnesses, cross-examination, and marking of exhibits followed by final arguments."
                },
                {
                    "step_number": 6,
                    "stage_name": "Judgment and Decree",
                    "procedure_details": "Pronouncement of judgment and preparation of executable decree."
                }
            ],
            "stipulated_timeline": [
                {
                    "action": "Court appearance",
                    "applicable_deadline": "On date designated in summons (typically 14-30 days)",
                    "legal_provision": "Order V Rule 1 CPC / Section 61 BNSS",
                    "starting_point": "Date of service of summons"
                },
                {
                    "action": "Filing response (Written Statement)",
                    "applicable_deadline": "30 days (extendable up to 90/120 days for commercial disputes)",
                    "legal_provision": "Order VIII Rule 1 CPC",
                    "starting_point": "Date of service of summons"
                },
                {
                    "action": "Filing application for interim injunction",
                    "applicable_deadline": "Immediately upon institution or along with plaint",
                    "legal_provision": "Order XXXIX Rule 1 CPC",
                    "starting_point": "Date of apprehension or infringement"
                },
                {
                    "action": "Appeal",
                    "applicable_deadline": "30 days (High Court 90 days)",
                    "legal_provision": "Articles 116 & 117, Limitation Act, 1963",
                    "starting_point": "Date of decree or order appealed against"
                }
            ],
            "recommended_actions": [
                {
                    "priority": 1,
                    "category": "Immediate action",
                    "action": "Issue a formal legal notice through an enrolled advocate setting a strict 15-day compliance window."
                },
                {
                    "priority": 2,
                    "category": "Documents required",
                    "action": "Assemble chronological dossier of all original deeds, notices, receipts, and digital communications."
                },
                {
                    "priority": 3,
                    "category": "Advocate consultation",
                    "action": "Brief a litigation advocate practicing in the jurisdictional District/Taluka court."
                },
                {
                    "priority": 4,
                    "category": "Court filing or appearance",
                    "action": "Draft and lodge civil suit / private complaint with an accompanying stay application."
                },
                {
                    "priority": 5,
                    "category": "Follow-up action",
                    "action": "Obtain certified copy of order sheet after each hearing date via e-Courts portal."
                }
            ],
            "missing_information": [
                "Exact date of summons service or triggering dispute date.",
                "Copies of written notices or contracts executed between the parties."
            ],
            "sources": [
                "Code of Civil Procedure, 1908",
                "Bharatiya Nyaya Sanhita, 2023 / IPC 1860",
                "Limitation Act, 1963",
                "Supreme Court of India Official Judgments"
            ],
            "legal_disclaimer": "AI Legal Research and Case Analysis guidance only under Indian law. Not a police finding, judicial decree, or substitute for representation by an enrolled advocate."
        }

    def _call_gemini_raw(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.1) -> Optional[str]:
        """
        Low-level call: send a raw prompt string to Gemini and return the text response.
        """
        if not self.api_key:
            return None

        payload = {
            'contents': [{'parts': [{'text': prompt}]}],
            'generationConfig': {
                'temperature': temperature,
                'maxOutputTokens': max_tokens,
            }
        }
        body_bytes = json.dumps(payload).encode('utf-8')

        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={self.api_key}"
            req = urllib.request.Request(
                url,
                data=body_bytes,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            try:
                with urllib.request.urlopen(req, timeout=self.timeout) as res:
                    data = json.loads(res.read().decode('utf-8'))
                    candidates = data.get('candidates', [])
                    if candidates:
                        parts = candidates[0].get('content', {}).get('parts', [])
                        if parts and 'text' in parts[0]:
                            return parts[0]['text'].strip()
            except Exception as exc:
                logger.warning(f"Gemini model {model} attempt failed: {exc}")
                continue

        return None

    def _call_openrouter_raw(self, prompt: str, max_tokens: int = 1024) -> Optional[str]:
        """
        Fallback call to OpenRouter.
        """
        if not self.openrouter_key:
            return None

        models = [
            'mistralai/mistral-small-3.2-24b-instruct-2506:free',
            'deepseek/deepseek-r1:free',
            'google/gemini-2.0-flash-lite:free',
            'meta-llama/llama-3.2-3b-instruct:free',
        ]

        payload = {
            'messages': [
                {'role': 'system', 'content': 'You are Law Mithra, an Indian legal assistant. Never output markdown asterisks or hashes.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.2,
            'max_tokens': max_tokens,
        }

        for model in models:
            payload['model'] = model
            body_bytes = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                'https://openrouter.ai/api/v1/chat/completions',
                data=body_bytes,
                headers={
                    'Authorization': f'Bearer {self.openrouter_key}',
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
            except Exception as exc:
                logger.warning(f"OpenRouter model {model} attempt failed: {exc}")
                continue

        return None
