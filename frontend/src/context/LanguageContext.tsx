import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  SupportedLanguage,
  LanguageMeta,
  SUPPORTED_LANGUAGES,
  localesMap,
  translateKey,
} from '@/lib/translations';
import { useAuth } from './AuthContext';

interface LanguageContextType {
  language: SupportedLanguage;
  setLanguage: (lang: SupportedLanguage) => void;
  currentLanguage: LanguageMeta;
  languages: LanguageMeta[];
  t: (key: string, fallback?: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: React.ReactNode }) {
  const auth = useAuth();

  const [language, setLanguageState] = useState<SupportedLanguage>(() => {
    const saved = localStorage.getItem('law-mithra-lang') as SupportedLanguage;
    if (saved && localesMap[saved]) {
      return saved;
    }
    return 'en';
  });

  // When logged-in user profile loads with preferred_language, sync it
  useEffect(() => {
    if (auth.user?.preferred_language && localesMap[auth.user.preferred_language as SupportedLanguage]) {
      const userLang = auth.user.preferred_language as SupportedLanguage;
      setLanguageState(userLang);
      localStorage.setItem('law-mithra-lang', userLang);
    }
  }, [auth.user?.preferred_language]);

  const setLanguage = useCallback((lang: SupportedLanguage) => {
    if (!localesMap[lang]) return;
    setLanguageState(lang);
    localStorage.setItem('law-mithra-lang', lang);

    // If user is authenticated, sync to backend profile seamlessly
    if (auth.user && auth.updateProfile) {
      auth.updateProfile({ preferred_language: lang }).catch(() => {
        // Non-critical background sync
      });
    }
  }, [auth]);

  const currentLanguage = SUPPORTED_LANGUAGES.find((l) => l.code === language) || SUPPORTED_LANGUAGES[0];

  const t = useCallback((key: string, fallback?: string): string => {
    return translateKey(language, key, fallback);
  }, [language]);

  return (
    <LanguageContext.Provider
      value={{
        language,
        setLanguage,
        currentLanguage,
        languages: SUPPORTED_LANGUAGES,
        t,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage(): LanguageContextType {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}
