import en from '@/locales/en.json';
import hi from '@/locales/hi.json';
import kn from '@/locales/kn.json';
import ta from '@/locales/ta.json';
import te from '@/locales/te.json';
import ml from '@/locales/ml.json';
import mr from '@/locales/mr.json';
import bn from '@/locales/bn.json';
import gu from '@/locales/gu.json';
import pa from '@/locales/pa.json';

export type SupportedLanguage = 'en' | 'hi' | 'kn' | 'ta' | 'te' | 'ml' | 'mr' | 'bn' | 'gu' | 'pa';

export interface LanguageMeta {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  fontClass: string;
}

export const SUPPORTED_LANGUAGES: LanguageMeta[] = [
  { code: 'en', name: 'English', nativeName: 'English', fontClass: 'font-sans' },
  { code: 'hi', name: 'Hindi', nativeName: 'हिन्दी', fontClass: 'font-devanagari' },
  { code: 'kn', name: 'Kannada', nativeName: 'ಕನ್ನಡ', fontClass: 'font-kannada' },
  { code: 'ta', name: 'Tamil', nativeName: 'தமிழ்', fontClass: 'font-tamil' },
  { code: 'te', name: 'Telugu', nativeName: 'తెలుగు', fontClass: 'font-telugu' },
  { code: 'ml', name: 'Malayalam', nativeName: 'മലയാളം', fontClass: 'font-malayalam' },
  { code: 'mr', name: 'Marathi', nativeName: 'मराठी', fontClass: 'font-devanagari' },
  { code: 'bn', name: 'Bengali', nativeName: 'বাংলা', fontClass: 'font-bengali' },
  { code: 'gu', name: 'Gujarati', nativeName: 'ગુજરાતી', fontClass: 'font-gujarati' },
  { code: 'pa', name: 'Punjabi', nativeName: 'ਪੰਜਾਬੀ', fontClass: 'font-gurmukhi' },
];

export const localesMap: Record<SupportedLanguage, any> = {
  en,
  hi,
  kn,
  ta,
  te,
  ml,
  mr,
  bn,
  gu,
  pa,
};

/**
 * Traverses a nested JSON object with a dot-notated string key (e.g. 'hero.badge').
 */
function getNestedValue(obj: any, path: string): string | undefined {
  if (!obj || typeof obj !== 'object') return undefined;
  const keys = path.split('.');
  let current = obj;
  for (const k of keys) {
    if (current && typeof current === 'object' && k in current) {
      current = current[k];
    } else {
      return undefined;
    }
  }
  return typeof current === 'string' ? current : undefined;
}

/**
 * Translates key for given language, with strict fallback to English.
 */
export function translateKey(lang: SupportedLanguage, key: string, fallback?: string): string {
  const targetDict = localesMap[lang];
  if (targetDict) {
    const val = getNestedValue(targetDict, key);
    if (val !== undefined) return val;
  }

  // Fallback to English
  const enDict = localesMap['en'];
  if (enDict) {
    const val = getNestedValue(enDict, key);
    if (val !== undefined) return val;
  }

  return fallback || key;
}
