"""
Legal Terminology Glossary for Indian Law across 10 Languages.
Supports: en, hi, kn, ta, te, ml, mr, bn, gu, pa.
Maintains dual-language mapping with original English terms in brackets [Term]
for statutory clarity and judicial precision.
"""

from typing import Dict, List, Optional

LEGAL_GLOSSARY: Dict[str, Dict[str, str]] = {
    'FIR': {
        'en': 'First Information Report [FIR]',
        'hi': 'प्रथम सूचना रिपोर्ट [FIR]',
        'kn': 'ಪ್ರಥಮ ಮಾಹಿತಿ ವರದಿ [FIR]',
        'ta': 'முதல் தகவல் அறிக்கை [FIR]',
        'te': 'ప్రథమ సమాచార నివేదిక [FIR]',
        'ml': 'പ്രഥമ വിവര റിപ്പോർട്ട് [FIR]',
        'mr': 'प्रथम माहिती अहवाल [FIR]',
        'bn': 'প্রথম তথ্য বিবরণী [FIR]',
        'gu': 'પ્રથમ માહિતી અહેવાલ [FIR]',
        'pa': 'ਪਹਿਲੀ ਸੂਚਨਾ ਰਿਪੋਰਟ [FIR]',
    },
    'Bail': {
        'en': 'Bail [Bail]',
        'hi': 'जमानत [Bail]',
        'kn': 'ಜಾಮೀನು [Bail]',
        'ta': 'ஜாமீன் [Bail]',
        'te': 'బెయిల్ [Bail]',
        'ml': 'ജാമ്യം [Bail]',
        'mr': 'जामीन [Bail]',
        'bn': 'জামিন [Bail]',
        'gu': 'જામીન [Bail]',
        'pa': 'ਜ਼ਮਾਨਤ [Bail]',
    },
    'Anticipatory Bail': {
        'en': 'Anticipatory Bail [Anticipatory Bail]',
        'hi': 'अग्रिम जमानत [Anticipatory Bail]',
        'kn': 'ನಿರೀಕ್ಷಣಾ ಜಾಮೀನು [Anticipatory Bail]',
        'ta': 'முன்பிணை [Anticipatory Bail]',
        'te': 'ముందస్తు బెయిల్ [Anticipatory Bail]',
        'ml': 'മുൻകൂർ ജാമ്യം [Anticipatory Bail]',
        'mr': 'आगाऊ जामीन [Anticipatory Bail]',
        'bn': 'আগাম জামিন [Anticipatory Bail]',
        'gu': 'અગાઉથી જામીન [Anticipatory Bail]',
        'pa': 'ਅਗਾਊਂ ਜ਼ਮਾਨਤ [Anticipatory Bail]',
    },
    'Cognizable Offence': {
        'en': 'Cognizable Offence [Cognizable Offence]',
        'hi': 'संज्ञेय अपराध [Cognizable Offence]',
        'kn': 'ಪೊಲೀಸರು ನೇರವಾಗಿ ತನಿಖೆ ನಡೆಸಬಹುದಾದ ಅಪರಾಧ [Cognizable Offence]',
        'ta': 'கைது செய்யக்கூடிய குற்றம் [Cognizable Offence]',
        'te': 'వారెంట్ లేకుండా అరెస్టు చేయగల నేరం [Cognizable Offence]',
        'ml': 'വാറന്റില്ലാതെ അറസ്റ്റ് ചെയ്യാവുന്ന കുറ്റം [Cognizable Offence]',
        'mr': 'दखलपात्र गुन्हा [Cognizable Offence]',
        'bn': 'আমলযোগ্য অপরাধ [Cognizable Offence]',
        'gu': 'પોલીસ હસ્તક્ષેપપાત્ર ગુનો [Cognizable Offence]',
        'pa': 'ਦਸਤਅੰਦਾਜ਼ੀ ਯੋਗ ਜੁਰਮ [Cognizable Offence]',
    },
    'Non-cognizable Offence': {
        'en': 'Non-cognizable Offence [Non-cognizable Offence]',
        'hi': 'असंज्ञेय अपराध [Non-cognizable Offence]',
        'kn': 'ನ್ಯಾಯಾಲಯದ ಅನುಮತಿ ಅಗತ್ಯವಿರುವ ಅಪರಾಧ [Non-cognizable Offence]',
        'ta': 'கைது செய்யமுடியாத குற்றம் [Non-cognizable Offence]',
        'te': 'వారెంట్ అవసరమైన నేరం [Non-cognizable Offence]',
        'ml': 'വാറന്റ് ആവശ്യമുള്ള കുറ്റം [Non-cognizable Offence]',
        'mr': 'अदखलपात्र गुन्हा [Non-cognizable Offence]',
        'bn': 'অ-আমলযোগ্য অপরাধ [Non-cognizable Offence]',
        'gu': 'પોલીસ બિન-હસ્તક્ષેપપાત્ર ગુનો [Non-cognizable Offence]',
        'pa': 'ਗ਼ੈਰ-ਦਸਤਅੰਦਾਜ਼ੀ ਯੋਗ ਜੁਰਮ [Non-cognizable Offence]',
    },
    'Charge Sheet': {
        'en': 'Charge Sheet [Charge Sheet]',
        'hi': 'आरोप पत्र [Charge Sheet]',
        'kn': 'ದೋಷಾರೋಪಣ ಪಟ್ಟಿ [Charge Sheet]',
        'ta': 'குற்றப்பத்திரிகை [Charge Sheet]',
        'te': 'దోషారోపణ పత్రం [Charge Sheet]',
        'ml': 'കുറ്റപത്രം [Charge Sheet]',
        'mr': 'दोषारोपपत्र [Charge Sheet]',
        'bn': 'অভিযোগপত্র [Charge Sheet]',
        'gu': 'ચાર્જશીટ / આરોપનામું [Charge Sheet]',
        'pa': 'ਚਾਰਜਸ਼ੀਟ / ਦੋਸ਼ ਪੱਤਰ [Charge Sheet]',
    },
    'Injunction': {
        'en': 'Injunction / Stay Order [Injunction]',
        'hi': 'निषेधाज्ञा / स्थगन आदेश [Injunction]',
        'kn': 'ತಡೆಯಾಜ್ಞೆ [Injunction / Stay Order]',
        'ta': 'தடையுத்தரவு [Injunction]',
        'te': 'నిషేధాజ్ఞ / స్టే ఆర్డర్ [Injunction]',
        'ml': 'തടയുത്തരവ് [Injunction]',
        'mr': 'मनाई हुकूम [Injunction]',
        'bn': 'নিষেধাজ্ঞা আদেশ [Injunction]',
        'gu': 'મનાઈ હુકમ [Injunction]',
        'pa': 'ਰੋਕ ਹੁਕਮ [Injunction]',
    },
    'Jurisdiction': {
        'en': 'Jurisdiction [Jurisdiction]',
        'hi': 'अधिकार क्षेत्र [Jurisdiction]',
        'kn': 'ನ್ಯಾಯಾಂಗ ವ್ಯಾಪ್ತಿ [Jurisdiction]',
        'ta': 'அதிகார வரம்பு [Jurisdiction]',
        'te': 'అధికార పరిధి [Jurisdiction]',
        'ml': 'അധികാരപരിധി [Jurisdiction]',
        'mr': 'अधिकारक्षेत्र [Jurisdiction]',
        'bn': 'এখতিয়ার / বিচারসীমা [Jurisdiction]',
        'gu': 'હકૂમત / અધિકારક્ષેત્ર [Jurisdiction]',
        'pa': 'ਅਧਿਕਾਰ ਖੇਤਰ [Jurisdiction]',
    },
    'Appeal': {
        'en': 'Appeal [Appeal]',
        'hi': 'अपील [Appeal]',
        'kn': 'ಮೇಲ್ಮನವಿ [Appeal]',
        'ta': 'மேல்முறையீடு [Appeal]',
        'te': 'అప్పీలు [Appeal]',
        'ml': 'അപ്പീൽ [Appeal]',
        'mr': 'अपील [Appeal]',
        'bn': 'আপিল [Appeal]',
        'gu': 'અપીલ [Appeal]',
        'pa': 'ਅਪੀਲ [Appeal]',
    },
    'Revision': {
        'en': 'Revision [Revision]',
        'hi': 'पुनरीक्षण [Revision]',
        'kn': 'ಪುನರ್ವಿಮರ್ಶೆ [Revision]',
        'ta': 'மறுஆய்வு [Revision]',
        'te': 'రివిజన్ / పునఃసమీక్ష [Revision]',
        'ml': 'റിവിഷൻ [Revision]',
        'mr': 'पुनरावलोकन [Revision]',
        'bn': 'পুনর্বিবেচনা [Revision]',
        'gu': 'પુનરાવલોકન [Revision]',
        'pa': 'ਨਜ਼ਰਸਾਨੀ [Revision]',
    },
    'Limitation Period': {
        'en': 'Limitation Period [Limitation Period]',
        'hi': 'परिसीमा अवधि [Limitation Period]',
        'kn': 'ಕಾಲಾವಧಿ ಪರಿಮಿತಿ [Limitation Period]',
        'ta': 'காலவரம்புக்காலம் [Limitation Period]',
        'te': 'కాలపరిమితి [Limitation Period]',
        'ml': 'കാലാവധി പരിധി [Limitation Period]',
        'mr': 'मुदत मर्यादा [Limitation Period]',
        'bn': 'তামাদির মেয়াদ [Limitation Period]',
        'gu': 'મર્યાદા અવધિ [Limitation Period]',
        'pa': 'ਮਿਆਦ ਸਮਾਂ [Limitation Period]',
    },
    'Encroachment': {
        'en': 'Illegal Encroachment / Unlawful Dispossession [Encroachment]',
        'hi': 'अवैध अतिक्रमण / गैरकानूनी कब्जा [Encroachment]',
        'kn': 'ಅಕ್ರಮ ಒತ್ತುವರಿ / ಅಕ್ರಮ ಸ್ವಾಧೀನ [Illegal Encroachment]',
        'ta': 'சட்டவிரோத ஆக்கிரமிப்பு [Encroachment]',
        'te': 'అక్రమ ఆక్రమణ [Encroachment]',
        'ml': 'അനധികൃത കയ്യേറ്റം [Encroachment]',
        'mr': 'बेकायदेशीर अतिक्रमण [Encroachment]',
        'bn': 'অবৈধ দখল / জবরদখল [Encroachment]',
        'gu': 'ગેરકાયદેસર દબાણ [Encroachment]',
        'pa': 'ਗੈਰ-ਕਾਨੂੰਨੀ ਕਬਜ਼ਾ [Encroachment]',
    },
}


def get_legal_term(term_key: str, lang: str = 'en') -> str:
    """Returns the dual-format legal term for the requested language."""
    term_dict = LEGAL_GLOSSARY.get(term_key)
    if not term_dict:
        return term_key
    return term_dict.get(lang, term_dict.get('en', term_key))


def get_all_terms_for_language(lang: str = 'en') -> List[Dict[str, str]]:
    """Returns all glossary terms formatted for the requested language."""
    items = []
    for key, trans in LEGAL_GLOSSARY.items():
        items.append({
            'key': key,
            'english': trans.get('en', key),
            'localized': trans.get(lang, trans.get('en', key)),
        })
    return items

