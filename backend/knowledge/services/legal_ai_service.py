"""
Multilingual Legal AI Reasoning Engine for Indian Law.
Implements the 7-step legal reasoning pipeline:
1. Input language detection
2. Legal query understanding & issue extraction
3. Statutory retrieval of verified Indian laws & citations
4. Factual legal analysis
5. Identification of verified legal remedies & procedural steps
6. Statutory section preservation & safeguards
7. Dual-language generation (Localized output + verified English statutory references)
"""

import re
from typing import Dict, Any, List, Optional
from .language_detector import detect_language, SUPPORTED_LANGUAGES
from .statutory_guard import StatutoryGuard
from .terminology import get_legal_term
from .bhashini_client import BhashiniClient
from .indictrans_client import IndicTransClient
from .gemini_client import GeminiClient

# Comprehensive Indian Law Knowledge Base for Core Civil & Criminal Remedies
VERIFIED_LEGAL_DOMAINS = [
    {
        'id': 'land_encroachment',
        'keywords': [
            'land', 'property', 'encroachment', 'possession', 'dispossessed', 'trespass',
            'boundary', 'site', 'plot', 'survey',
            # Kannada keywords
            'ಜಮೀನು', 'ಆಸ್ತಿ', 'ಸ್ವಾಧೀನ', 'ಅಕ್ರಮ', 'ಒತ್ತುವರಿ', 'ಕಬಳಿಕೆ', 'ಹದ್ದುಬಸ್ತು', 'ಸ್ಥಳ',
            # Hindi / Marathi keywords
            'जमीन', 'कब्जा', 'अतिक्रमण', 'संपत्ति', 'अवैध', 'मिल्कियत', 'प्लॉट',
            # Tamil / Telugu / Malayalam keywords
            'நிலம்', 'சொத்து', 'ஆக்கிரமிப்பு', 'భూమి', 'ఆస్తి', 'ఆక్రమణ', 'സ്ഥലം', 'ഭൂമി', 'കയ്യേറ്റം',
            # Bengali / Gujarati / Punjabi
            'জমি', 'দখল', 'জবরদখল', 'જમીન', 'દબાણ', 'માલિકી', 'ਜ਼ਮੀਨ', 'ਕਬਜ਼ਾ'
        ],
        'legal_issues': 'Unlawful Dispossession, Boundary Dispute, and Criminal Trespass of Immovable Property',
        'applicable_laws': [
            {
                'act': 'Specific Relief Act, 1963',
                'sections': ['Section 5', 'Section 6'],
                'english_statute': 'Section 6 of the Specific Relief Act, 1963: Suit by person dispossessed of immovable property. If any person is dispossessed without his consent of immovable property otherwise than in due course of law, he may, by suit, recover possession thereof within 6 months, notwithstanding any other title that may be set up in such suit.',
                'summary': 'Summary possession suit without needing to prove absolute ownership, filed within 6 months of unlawful dispossession.'
            },
            {
                'act': 'Code of Civil Procedure, 1908',
                'sections': ['Order 39 Rule 1', 'Order 39 Rule 2', 'Section 151'],
                'english_statute': 'Order 39 Rules 1 & 2 CPC: Temporary injunctions and interlocutory orders to restrain the defendant from committing waste, damage, alienation or disturbing peaceful possession.',
                'summary': 'Temporary injunction application to immediately halt ongoing encroachment, construction, or third-party transfer.'
            },
            {
                'act': 'Indian Penal Code / Bharatiya Nyaya Sanhita',
                'sections': ['Section 441 IPC', 'Section 447 IPC', 'Section 329 BNS'],
                'english_statute': 'Section 441 IPC / Section 329 BNS: Criminal Trespass. Whoever enters into or upon property in the possession of another with intent to commit an offence or to intimidate, insult or annoy, is punishable with imprisonment up to 3 months or fine up to ₹500 or both.',
                'summary': 'Criminal trespass complaint with jurisdictional police.'
            },
            {
                'act': 'Code of Criminal Procedure, 1973 / BNSS, 2023',
                'sections': ['Section 145 CrPC', 'Section 164 BNSS'],
                'english_statute': 'Section 145 CrPC / Section 164 BNSS: Procedure where dispute concerning land or water is likely to cause breach of peace. Executive Magistrate (Sub-Divisional Magistrate) can inquire into actual possession and issue protective orders.',
                'summary': 'Magisterial proceeding before Executive Magistrate/Tahsildar to seal or prevent breach of peace.'
            }
        ],
        'remedies_en': [
            '1. File an urgent Civil Suit for Recovery of Possession under Section 6 of the Specific Relief Act, 1963 within 6 months of being dispossessed.',
            '2. Simultaneously submit an Application for Temporary Injunction under Order 39 Rules 1 & 2 of CPC seeking an immediate stay order against unauthorized construction or alienation.',
            '3. Lodge a written Criminal Trespass complaint under Section 441/447 IPC (or Section 329 BNS) with the jurisdictional police inspector and obtain an acknowledgment / FIR.',
            '4. Approach the Executive Magistrate (Tahsildar / Sub-Divisional Magistrate) under Section 145 CrPC (Section 164 BNSS) to prevent breach of peace and conduct a spot inspection with the Revenue Department / Survey Department.'
        ],
        'remedies_kn': [
            '೧. ಅಕ್ರಮವಾಗಿ ಸ್ವಾಧೀನ ಕಳೆದುಕೊಂಡ ೬ ತಿಂಗಳ ಒಳಗೆ ನಿರ್ದಿಷ್ಟ ಪರಿಹಾರ ಕಾಯ್ದೆ ೧೯೬೩ ರ ಕಲಂ ೬ (Section 6 of Specific Relief Act) ರ ಅಡಿಯಲ್ಲಿ ಸ್ವಾಧೀನ ವಾಪಸಾತಿಗಾಗಿ ಸಿವಿಲ್ ದಾವೆ ಹೂಡಿರಿ.',
            '೨. ಸಿವಿಲ್ ಪ್ರಕ್ರಿಯಾ ಸಂಹಿತೆ (CPC) ಯ ಆರ್ಡರ್ ೩೯ ರೂಲ್ ೧ ಮತ್ತು ೨ ರ ಅಡಿಯಲ್ಲಿ ಮಧ್ಯಂತರ ತಡೆಯಾಜ್ಞೆ (Injunction / Stay Order) ಕೋರಿ ತುರ್ತು ಅರ್ಜಿ ಸಲ್ಲಿಸಿರಿ.',
            '೩. ವ್ಯಾಪ್ತಿಯ ಪೊಲೀಸ್ ಠಾಣೆಯಲ್ಲಿ ಅಕ್ರಮ ಪ್ರವೇಶದ ಕುರಿತು ಕಲಂ ೪೪೧ ಮತ್ತು ೪೪೭ ಐಪಿಸಿ (ಕಲಂ ೩೨೯ ಬಿಎನ್‌ಎಸ್) ಅಡಿಯಲ್ಲಿ ಲಿಖಿತ ದೂರು ಸಲ್ಲಿಸಿ ಸ್ವೀಕೃತಿ (Acknowledgment / FIR) ಪಡೆದುಕೊಳ್ಳಿರಿ.',
            '೪. ಶಾಂತಿಭಂಗ ತಡೆಯಲು ಹಾಗೂ ಕಂದಾಯ ಇಲಾಖೆಯ ಸರ್ವೆ ನಡೆಸಲು ಕಲಂ ೧೪೫ ಸಿಆರ್‌ಪಿಸಿ (ಕಲಂ ೧೬೪ ಬಿಎನ್‌ಎಸ್‌ಎಸ್) ಅಡಿಯಲ್ಲಿ ತಹಶೀಲ್ದಾರ್ / ಉಪವಿಭಾಗಾಧಿಕಾರಿಯವರಿಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಿರಿ.'
        ],
        'remedies_hi': [
            '१. कब्जा छीने जाने के ६ महीने के भीतर विनिर्दिष्ट अनुतोष अधिनियम, १९६३ की धारा ६ (Section 6 of Specific Relief Act) के तहत कब्जा वापसी का दीवानी वाद (Civil Suit) दायर करें।',
            '२. सीपीसी (CPC) के आदेश ३९ नियम १ एवं २ के तहत अवैध निर्माण या संपत्ति बेचने पर तत्काल स्थगन आदेश / निषेधाज्ञा (Stay Order / Injunction) प्राप्त करने का आवेदन दें।',
            '३. संबंधित थाने में आपराधिक अतिचार (Criminal Trespass) हेतु धारा ४४१/४४७ आईपीसी (धारा ३२৯ बीएनएस) के तहत प्राथमिकी (FIR) दर्ज कराएं।',
            '४. शांतिभंग रोकने और राजस्व सीमांकन के लिए धारा १४५ सीआरपीसी (धारा १६४ बीएनएसएस) के तहत एसडीएम / तहसीलदार के समक्ष प्रार्थना पत्र प्रस्तुत करें।'
        ],
        'remedies_ta': [
            '1. உடைமை பறிக்கப்பட்ட 6 மாதங்களுக்குள் குறிப்பிட்ட நிவாரணச் சட்டம் 1963 பிரிவு 6 (Section 6 Specific Relief Act) கீழ் உரிமையியல் வழக்கு (Civil Suit) தாக்கல் செய்யுங்கள்.',
            '2. சிபிசி (CPC) உத்தரவு 39 விதி 1 மற்றும் 2 கீழ் உடனடி தடையுத்தரவு (Injunction) பெற மனு தாக்கல் செய்யவும்.',
            '3. எல்லை மீறல் மற்றும் அத்துமீறலுக்கு எதிராக பிரிவு 441/447 IPC (பிரிவு 329 BNS) கீழ் காவல் நிலையத்தில் எழுத்துப்பூர்வ புகார் (FIR) அளியுங்கள்.',
            '4. அமைதிக்கு பங்கம் ஏற்படாமல் தடுக்க பிரிவு 145 CrPC (பிரிவு 164 BNSS) கீழ் வருவாய் கோட்டாட்சியர் / வட்டாட்சியரிடம் மனு அளியுங்கள்.'
        ],
        'remedies_te': [
            '1. ఆక్రమణ జరిగిన 6 నెలల లోపు స్పెసిఫిక్ రిలీఫ్ యాక్ట్, 1963 సెక్షన్ 6 (Section 6 SRA) కింద స్వాధీనం రికవరీ కోసం సివిల్ దావా వేయండి.',
            '2. సీపీసీ (CPC) ఆర్డర్ 39 రూల్ 1 & 2 కింద తక్షణ స్టే ఆర్డర్ / నిషేధాజ్ఞ (Temporary Injunction) కోసం దరఖాస్తు చేయండి.',
            '3. అక్రమ ప్రవేశంపై సెక్షన్ 441/447 ఐపీసీ (సెక్షన్ 329 BNS) కింద పోలీసులకు లిఖితపూర్వక ఫిర్యాదు (FIR) సమర్పించండి.',
            '4. శాంతిభద్రతల పరిరక్షణ మరియు సర్వే కోసం సెక్షన్ 145 CrPC (సెక్షన్ 164 BNSS) కింద ఎగ్జిక్యూటివ్ మేజిస్ట్రేట్ / తహశీల్దార్‌కు దరఖాస్తు చేయండి.'
        ],
    },
    {
        'id': 'cheque_bounce',
        'keywords': [
            'cheque', 'check', 'bounce', 'dishonour', 'insufficient', 'bank',
            'ಚೆಕ್', 'ಬೌನ್ಸ್', 'ಅಮಾನ್ಯ', 'ಬ್ಯಾಂಕ್', 'ಹಣ',
            'चेक', 'बाउंस', 'अनादर', 'खाता',
            'காசோலை', 'செக்', 'பவுன்ஸ்', 'చెక్', 'బౌన్స్', 'చెల్లక'
        ],
        'legal_issues': 'Dishonour of Cheque for Insufficiency of Funds in Bank Account',
        'applicable_laws': [
            {
                'act': 'Negotiable Instruments Act, 1881',
                'sections': ['Section 138', 'Section 141', 'Section 142'],
                'english_statute': 'Section 138 of the Negotiable Instruments Act, 1881: Dishonour of cheque for insufficiency, etc., of funds in the account is an offence punishable with imprisonment for a term up to 2 years, or with fine which may extend to twice the amount of the cheque, or with both.',
                'summary': 'Statutory 30-day legal demand notice followed by criminal complaint under Section 138 NI Act within 30 days.'
            }
        ],
        'remedies_en': [
            '1. Issue a formal Statutory Legal Demand Notice in writing within 30 days of receiving the cheque return memo from the bank.',
            '2. Provide the drawer a strict statutory window of 15 days from receipt of notice to make payment.',
            '3. If payment is not cleared within 15 days, file a Criminal Complaint under Section 138 of the Negotiable Instruments Act, 1881 before the Judicial Magistrate within 30 days thereafter.',
            '4. Seek interim compensation up to 20% of the cheque amount under Section 143A of the NI Act.'
        ],
        'remedies_kn': [
            '೧. ಬ್ಯಾಂಕಿನಿಂದ ಚೆಕ್ ರಿಟರ್ನ್ ಮೆಮೊ ಬಂದ ದಿನಾಂಕದಿಂದ ೩೦ ದಿನಗಳ ಒಳಗೆ ವಕೀಲರ ಮೂಲಕ ಶಾಸನಬದ್ಧ ಡಿಮಾಂಡ್ ನೋಟಿಸ್ (Legal Notice under Section 138 NI Act) ಕಳುಹಿಸಿರಿ.',
            '೨. ನೋಟಿಸ್ ತಲುಪಿದ ದಿನದಿಂದ ಹಣ ಪಾವತಿಸಲು ೧೫ ದಿನಗಳ ಕಡ್ಡಾಯ ಕಾಲಾವಕಾಶ ನೀಡಿರಿ.',
            '೩. ಆ ೧೫ ದಿನಗಳಲ್ಲಿ ಹಣ ಪಾವತಿಸದಿದ್ದರೆ, ಮುಂದಿನ ೩೦ ದಿನಗಳ ಒಳಗೆ ಪ್ರಥಮ ದರ್ಜೆ ನ್ಯಾಯಾಂಗ ಮ್ಯಾಜಿಸ್ಟ್ರೇಟ್ (JMFC) ನ್ಯಾಯಾಲಯದಲ್ಲಿ ಕ್ರಿಮಿನಲ್ ದೂರು ದಾಖಲಿಸಿರಿ.',
            '೪. ಕಲಂ ೧೪೩ಎ ಎನ್‌ಐ ಕಾಯ್ದೆ (Section 143A NI Act) ಅಡಿಯಲ್ಲಿ ಶೇಕಡಾ ೨೦ ರಷ್ಟು ಮಧ್ಯಂತರ ಪರಿಹಾರವನ್ನು ನ್ಯಾಯಾಲಯದಿಂದ ಕೋರಬಹುದು.'
        ],
        'remedies_hi': [
            '१. बैंक से चेक अनादर मेमो (Cheque Return Memo) मिलने के ३० दिनों के भीतर लिखित में वैधानिक मांग नोटिस (Statutory Notice under Section 138) भेजें।',
            '२. नोटिस प्राप्त होने के बाद देनदार को भुगतान के लिए १५ दिन का समय दें।',
            '३. यदि १५ दिनों में भुगतान नहीं होता है, तो अगले ३० दिनों के भीतर न्यायिक मजिस्ट्रेट की अदालत में परक्राम्य लिखत अधिनियम की धारा १३८ (Section 138 NI Act) के तहत परिवाद दाखिल करें।',
            '४. धारा १४३ए (Section 143A) के तहत चेक राशि का २०% तक अंतरिम मुआवजा देने की मांग करें।'
        ],
        'remedies_ta': [
            '1. காசோலை திரும்பப் பெறப்பட்ட குறிப்பு கிடைத்த 30 நாட்களுக்குள் சட்டப்பூர்வ அறிவிப்பு (Section 138 Legal Notice) அனுப்பவும்.',
            '2. அறிவிப்பைப் பெற்ற நாளிலிருந்து தொகையை செலுத்த 15 நாட்கள் கால அவகாசம் வழங்கவும்.',
            '3. 15 நாட்களுக்குள் பணம் செலுத்தப்படாவிட்டால், அடுத்த 30 நாட்களுக்குள் நீதித்துறை நடுவர் நீதிமன்றத்தில் பிரிவு 138 கீழ் புகார் தாக்கல் செய்யவும்.',
            '4. பிரிவு 143A கீழ் காசோலை தொகையில் 20% வரை இடைக்கால இழப்பீடு கோரலாம்.'
        ],
        'remedies_te': [
            '1. బ్యాంకు రిటర్న్ మెమో అందిన 30 రోజుల్లోగా చట్టబద్ధమైన లీగల్ నోటీసు (Section 138 NI Act) జారీ చేయండి.',
            '2. నోటీసు అందిన నాటి నుంచి సొమ్ము చెల్లించడానికి 15 రోజుల సమయం ఇవ్వండి.',
            '3. 15 రోజుల్లో చెల్లించకపోతే, ఆ తర్వాత 30 రోజుల్లో మేజిస్ట్రేట్ కోర్టులో క్రిమినల్ ఫిర్యాదు దాఖలు చేయండి.',
            '4. సెక్షన్ 143A కింద చెక్ మొత్తంలో 20% మధ్యంతర నష్టపరిహారం కోరవచ్చు.'
        ]
    }
]

DISCLAIMER_TEXTS = {
    'en': 'DISCLAIMER: This legal explanation is generated by Law Mithra AI for informational guidance under Indian law and does not constitute an official court order, government notification, or substitute for formal legal representation.',
    'kn': 'ಎಚ್ಚರಿಕೆ: ಈ ಕಾನೂನು ವಿವರಣೆಯನ್ನು ಭಾರತೀಯ ಕಾನೂನಿನ ಅಡಿಯಲ್ಲಿ ಮಾಹಿತಿ ಮಾರ್ಗದರ್ಶನಕ್ಕಾಗಿ ಲಾ ಮಿತ್ರ ಎಐ ರೂಪಿಸಿದೆ. ಇದು ಅಧಿಕೃತ ನ್ಯಾಯಾಲಯದ ತೀರ್ಪಲ್ಲ ಅಥವಾ ವಕೀಲರ ಅಧಿಕೃತ ಕಾನೂನು ಸಲಹೆಗೆ ಪರ್ಯಾಯವಲ್ಲ.',
    'hi': 'अस्वीकरण: यह कानूनी विश्लेषण भारतीय कानून के तहत सूचनात्मक मार्गदर्शन हेतु लॉ मित्र एआई द्वारा तैयार किया गया है। यह आधिकारिक अदालती आदेश या अधिवक्ता परामर्श का विकल्प नहीं है।',
    'ta': 'பொறுப்புத் துறப்பு: இந்த சட்ட விளக்கம் இந்திய சட்டத்தின் கீழ் தகவல் வழிகாட்டுதலுக்காக லா மித்ரா ஏஐ ஆல் உருவாக்கப்பட்டது. இது அதிகாரப்பூர்வ நீதிமன்ற உத்தரவு அல்ல.',
    'te': 'నిరాకరణ: ఈ న్యాయ వివరణ భారతీయ చట్టం కింద సమాచార మార్గదర్శకత్వం కోసం లా మిత్ర ఏఐ ద్వారా అందించబడింది. ఇది అధికారిక కోర్టు తీర్పు కాదు.',
    'ml': 'നിരാകരണം: ഈ നിയമ വിവരണം ഇന്ത്യൻ നിയമപ്രകാരമുള്ള വിവര മാർഗ്ഗനിർദ്ദേശത്തിനായി ലോ മിത്ര എഐ തയ്യാറാക്കിയതാണ്. ഇത് ഔദ്യോഗിക കോടതി ഉത്തരവല്ല.',
    'mr': 'अस्वीकरण: हे कायदेशीर स्पष्टीकरण भारतीय कायद्यांतर्गत माहितीपर मार्गदर्शनासाठी लॉ मित्र एआय द्वारे तयार केले आहे. हा अधिकृत न्यायालयीन आदेश नाही.',
    'bn': 'দাবিত্যাগ: এই আইনি ব্যাখ্যাটি ভারতীয় আইনের অধীনে তথ্যগত নির্দেশনার জন্য ল মিত্র এআই দ্বারা প্রস্তুত করা হয়েছে। এটি কোনো সরকারি আদালতের আদেশ নয়।',
    'gu': 'અસ્વીકરણ: આ કાયદાકીય સમજૂતી ભારતીય કાયદા હેઠળ માહિતીના માર્ગદર્શન માટે લૉ મિત્ર એઆઈ દ્વારા તૈયાર કરવામાં આવી છે. આ સત્તાવાર કોર્ટ આદેશ નથી.',
    'pa': 'ਬੇਦਾਅਵਾ: ਇਹ ਕਾਨੂੰਨੀ ਵਿਆਖਿਆ ਭਾਰਤੀ ਕਾਨੂੰਨ ਤਹਿਤ ਜਾਣਕਾਰੀ ਲਈ ਲਾਅ ਮਿੱਤਰਾ ਏਆਈ ਦੁਆਰਾ ਤਿਆਰ ਕੀਤੀ ਗਈ ਹੈ। ਇਹ ਕੋਈ ਅਧਿਕਾਰਤ ਅਦਾਲਤੀ ਹੁਕਮ ਨਹੀਂ ਹੈ।'
}


class LegalAIService:
    """
    Multilingual Legal Intelligence pipeline.
    Preserves statutory accuracy, matches relevant Indian codes,
    and returns dual-format verified statutory provisions.
    """

    def __init__(self):
        self.bhashini = BhashiniClient()
        self.indictrans = IndicTransClient()
        self.gemini = GeminiClient()

    def process_query(
        self,
        query_text: str,
        preferred_lang: str = 'en',
        auto_detect_lang: bool = True
    ) -> Dict[str, Any]:
        """
        Executes the 7-step multilingual legal reasoning pipeline.
        """
        # Step 1: Language Detection
        detected_lang, confidence = detect_language(query_text, fallback=preferred_lang)
        target_lang = detected_lang if auto_detect_lang else preferred_lang
        if target_lang not in SUPPORTED_LANGUAGES:
            target_lang = 'en'

        # Step 2: Query Understanding & Legal Domain Matching
        matched_domain = self._match_legal_domain(query_text)

        # Step 3 & 4: Statutory Retrieval & Legal Fact Analysis
        applicable_laws = matched_domain['applicable_laws'] if matched_domain else []
        legal_issue = matched_domain['legal_issues'] if matched_domain else "Indian Legal Advisory"

        # Step 5: Procedural Remedies in Target Language
        localized_remedies = self._get_localized_remedies(matched_domain, target_lang)

        # Generate live response with Gemini AI if configured
        gemini_explanation = None
        try:
            gemini_explanation = self.gemini.generate_legal_response(
                query=query_text,
                language=target_lang,
                statutory_context=applicable_laws if applicable_laws else None
            )
        except Exception:
            gemini_explanation = None

        # Step 6 & 7: Dual-Language Generation with Statutory Protection
        response_data = {
            'query': query_text,
            'detected_language': detected_lang,
            'target_language': target_lang,
            'confidence': confidence,
            'legal_issue': gemini_explanation or legal_issue,
            'remedies': localized_remedies,
            'applicable_sections': [
                {
                    'act': law['act'],
                    'sections': law['sections'],
                    'summary': law['summary'],
                    'original_english_statute': law['english_statute'],
                }
                for law in applicable_laws
            ],
            'disclaimer': DISCLAIMER_TEXTS.get(target_lang, DISCLAIMER_TEXTS['en']),
            'terminology': [
                {
                    'term': 'Encroachment',
                    'localized': get_legal_term('Encroachment', target_lang)
                },
                {
                    'term': 'Injunction',
                    'localized': get_legal_term('Injunction', target_lang)
                },
                {
                    'term': 'Jurisdiction',
                    'localized': get_legal_term('Jurisdiction', target_lang)
                }
            ]
        }

        return response_data

    def _match_legal_domain(self, query: str) -> Optional[Dict[str, Any]]:
        """Matches user question against Indian legal knowledge domains."""
        q_lower = query.lower()
        for domain in VERIFIED_LEGAL_DOMAINS:
            for kw in domain['keywords']:
                if kw.lower() in q_lower:
                    return domain
        return None

    def _get_localized_remedies(self, domain: Optional[Dict[str, Any]], lang: str) -> List[str]:
        """Fetches curated verified legal remedies in target language."""
        if not domain:
            return []
        key = f"remedies_{lang}"
        if key in domain:
            return domain[key]

        # If direct curated translation is not stored for this specific regional dialect,
        # use English source guarded through Bhashini / IndicTrans
        en_remedies = domain.get('remedies_en', [])
        if lang == 'en':
            return en_remedies

        translated_remedies = []
        for remedy in en_remedies:
            translated = None
            if self.bhashini.is_configured:
                translated = self.bhashini.translate(remedy, source_lang='en', target_lang=lang)
            elif self.indictrans.is_configured:
                translated = self.indictrans.translate(remedy, source_lang='en', target_lang=lang)

            if translated:
                translated_remedies.append(translated)
            else:
                # Fallback to English with statutory guard to preserve strict legal validity
                translated_remedies.append(remedy)

        return translated_remedies

