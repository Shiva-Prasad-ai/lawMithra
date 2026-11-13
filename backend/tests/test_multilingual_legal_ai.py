import pytest
from rest_framework.test import APIClient
from django.urls import reverse

from knowledge.services.language_detector import detect_language
from knowledge.services.statutory_guard import StatutoryGuard
from knowledge.services.terminology import get_legal_term, get_all_terms_for_language
from knowledge.services.legal_ai_service import LegalAIService


@pytest.mark.django_db
class TestMultilingualLegalAI:
    def setup_method(self):
        self.client = APIClient()
        self.service = LegalAIService()

    def test_language_detection_all_scripts(self):
        """Verify language detection across all supported Indian languages."""
        samples = {
            'kn': 'ನನ್ನ ಜಮೀನನ್ನು ಇನ್ನೊಬ್ಬರು ಅಕ್ರಮವಾಗಿ ಸ್ವಾಧೀನಪಡಿಸಿಕೊಂಡಿದ್ದಾರೆ.',
            'hi': 'मेरी जमीन पर किसी ने अवैध कब्जा कर लिया है।',
            'ta': 'எனது நிலத்தை ஒருவர் சட்டவிரோதமாக ஆக்கிரமித்துள்ளார்.',
            'te': 'నా భూమిని వేరొకరు అక్రమంగా ఆక్రమించారు.',
            'ml': 'എന്റെ ഭൂമി മറ്റൊരാൾ അനധികൃതമായി കൈയേറി.',
            'mr': 'माझ्या जमिनीवर बेकायदेशीर अतिक्रमण झाले आहे.',
            'bn': 'আমার জমি অন্য কেউ অবৈধভাবে দখল করেছে।',
            'gu': 'મારી જમીન પર કોઈએ ગેરકાયદેસર દબાણ કર્યું છે.',
            'pa': 'ਮੇਰੀ ਜ਼ਮੀਨ ਤੇ ਕਿਸੇ ਨੇ ਗੈਰ-ਕਾਨੂੰਨੀ ਕਬਜ਼ਾ ਕਰ ਲਿਆ ਹੈ।',
            'en': 'Someone has unlawfully encroached and dispossessed my agricultural land.'
        }

        for expected_lang, text in samples.items():
            detected, confidence = detect_language(text)
            assert detected == expected_lang, f"Failed for {expected_lang}: detected {detected}"
            assert confidence > 0.6

    def test_statutory_guard_preserves_numbers_and_citations(self):
        """Verify Rule 6: Section numbers, penalties, and fines are 100% preserved."""
        legal_text = (
            "Under Section 498A of Indian Penal Code, an accused faces up to 3 years imprisonment "
            "and fine of ₹50,000. In (2021) 5 SCC 123, the Supreme Court affirmed Order 39 Rule 1 CPC."
        )

        masked, token_map = StatutoryGuard.mask_statutory_entities(legal_text)
        assert "__STAT_GUARD_" in masked
        assert "Section 498A" not in masked
        assert "₹50,000" not in masked

        # Simulate translation transformation (e.g. Indic text with tokens intact)
        tokens = list(token_map.keys())
        simulated_translation = f"ಕಲಂ ಪ್ರಕಾರ {tokens[0]} ಅಡಿಯಲ್ಲಿ ಶಿಕ್ಷೆ {tokens[1]} ಮತ್ತು ದಂಡ {tokens[2]}"

        restored = StatutoryGuard.unmask_statutory_entities(simulated_translation, token_map)
        assert "Section 498A" in restored
        assert "3 years imprisonment" in restored
        assert "₹50,000" in restored

    def test_legal_terminology_glossary(self):
        """Verify legal glossary terms for multiple languages with dual English brackets."""
        # Kannada
        kn_bail = get_legal_term('Anticipatory Bail', 'kn')
        assert 'ನಿರೀಕ್ಷಣಾ ಜಾಮೀನು' in kn_bail
        assert '[Anticipatory Bail]' in kn_bail

        # Hindi
        hi_fir = get_legal_term('FIR', 'hi')
        assert 'प्रथम सूचना रिपोर्ट' in hi_fir
        assert '[FIR]' in hi_fir

        # Tamil
        ta_inj = get_legal_term('Injunction', 'ta')
        assert 'தடையுத்தரவு' in ta_inj

    def test_exact_kannada_query_resolution(self):
        """
        Verify the exact prompt user question:
        'ನನ್ನ ಜಮೀನನ್ನು ಇನ್ನೊಬ್ಬರು ಅಕ್ರಮವಾಗಿ ಸ್ವಾಧೀನಪಡಿಸಿಕೊಂಡಿದ್ದಾರೆ. ನಾನು ಏನು ಮಾಡಬೇಕು?'
        AI extracts Section 6 Specific Relief Act, Injunction, Criminal Trespass.
        """
        kannada_query = "ನನ್ನ ಜಮೀನನ್ನು ಇನ್ನೊಬ್ಬರು ಅಕ್ರಮವಾಗಿ ಸ್ವಾಧೀನಪಡಿಸಿಕೊಂಡಿದ್ದಾರೆ. ನಾನು ಏನು ಮಾಡಬೇಕು?"
        response = self.service.process_query(kannada_query, preferred_lang='kn', auto_detect_lang=True)

        assert response['detected_language'] == 'kn'
        assert response['target_language'] == 'kn'
        assert len(response['remedies']) > 0

        # Check that specific relief act and injunction sections are retrieved
        statutes = [item['act'] for item in response['applicable_sections']]
        assert any('Specific Relief Act' in act for act in statutes)
        assert any('Civil Procedure' in act for act in statutes)

        # Check disclaimer presence
        assert 'ಎಚ್ಚರಿಕೆ:' in response['disclaimer']

    def test_chat_api_endpoint(self):
        """Verify POST /api/knowledge/chat/ endpoint."""
        url = reverse('knowledge-chat')
        payload = {
            'query': 'How to file complaint for Section 138 cheque bounce?',
            'preferred_language': 'en',
            'auto_detect_language': True
        }
        res = self.client.post(url, payload, format='json')
        assert res.status_code == 200
        data = res.json()
        assert data['detected_language'] == 'en'
        assert any('Section 138' in str(s) for s in data['applicable_sections'])

    def test_languages_and_glossary_api(self):
        """Verify GET /api/knowledge/languages/ and /api/knowledge/glossary/."""
        lang_url = reverse('knowledge-languages')
        res = self.client.get(lang_url)
        assert res.status_code == 200
        languages = res.json()['languages']
        assert len(languages) == 10
        codes = [l['code'] for l in languages]
        assert 'en' in codes and 'hi' in codes and 'kn' in codes and 'gu' in codes and 'pa' in codes

        glossary_url = reverse('knowledge-glossary') + '?lang=kn'
        res_g = self.client.get(glossary_url)
        assert res_g.status_code == 200
        terms = res_g.json()['terms']
        assert len(terms) >= 10
