import React, { useState, useRef, useEffect } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLanguage } from '@/context/LanguageContext';
import { cn } from '@/lib/utils';

interface GoldLanguageSwitchProps {
  className?: string;
  dropDirection?: 'down' | 'up';
}

export function GoldLanguageSwitch({ className, dropDirection = 'down' }: GoldLanguageSwitchProps) {
  const { language, setLanguage, currentLanguage, languages } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={cn('relative inline-block text-left z-50', className)} ref={dropdownRef}>
      {/* Switcher Pill Button */}
      <motion.button
        type="button"
        whileHover={{ y: -1, scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        onClick={() => setIsOpen(!isOpen)}
        className="group relative inline-flex items-center gap-2 px-3.5 sm:px-4 py-2 rounded-full border border-[#D9A441]/70 hover:border-[#F7DE9B] bg-[#0A0A0A]/85 hover:bg-[#14120D] backdrop-blur-md shadow-[0_0_15px_rgba(217,164,65,0.18)] hover:shadow-[0_0_24px_rgba(217,164,65,0.38)] transition-all duration-200 cursor-pointer text-white"
        aria-haspopup="listbox"
        aria-expanded={isOpen}
      >
        {/* Subtle top inner glow line */}
        <span className="absolute inset-x-2 top-0 h-[1px] bg-gradient-to-r from-transparent via-[#F7DE9B]/50 to-transparent pointer-events-none" />

        {/* Globe Icon */}
        <Globe className="w-4 h-4 text-[#D9A441] group-hover:text-[#F7DE9B] transition-colors" />

        {/* Active Language in native script */}
        <span className="font-sans text-xs sm:text-sm font-medium tracking-wide">
          {currentLanguage.nativeName}
        </span>

        {/* Chevron */}
        <ChevronDown
          className={cn(
            'w-3.5 h-3.5 text-[#D9A441] transition-transform duration-200',
            isOpen && 'rotate-180'
          )}
        />
      </motion.button>

      {/* Dropdown Menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: dropDirection === 'down' ? 6 : -6, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: dropDirection === 'down' ? 6 : -6, scale: 0.96 }}
            transition={{ duration: 0.16 }}
            className={cn(
              'absolute right-0 w-52 sm:w-56 rounded-[18px] bg-[rgba(14,14,14,0.95)] backdrop-blur-xl border border-[#C8963E]/80 shadow-[0_12px_40px_rgba(0,0,0,0.85)] shadow-[0_0_25px_rgba(217,164,65,0.2)] p-1.5 z-50 focus:outline-none',
              dropDirection === 'down' ? 'mt-2 top-full' : 'mb-2 bottom-full'
            )}
          >
            <div className="px-3 py-1.5 border-b border-[#6B4D1F]/50 text-[10px] font-semibold tracking-wider text-[#A88C61] uppercase flex items-center justify-between">
              <span>Select Language</span>
              <span className="text-[9px] text-[#D9A441] font-normal">{languages.length} Languages</span>
            </div>

            <div className="max-h-72 overflow-y-auto py-1 space-y-0.5">
              {languages.map((lang) => {
                const isSelected = language === lang.code;
                return (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => {
                      setLanguage(lang.code);
                      setIsOpen(false);
                    }}
                    className={cn(
                      'w-full text-left px-3 py-2 rounded-[12px] text-xs flex items-center justify-between transition-all duration-150 cursor-pointer',
                      isSelected
                        ? 'bg-gradient-to-r from-[#D9A441]/25 to-[#F7DE9B]/10 border border-[#D9A441]/50 text-[#F7DE9B] font-semibold'
                        : 'text-white/80 hover:text-white hover:bg-white/5'
                    )}
                  >
                    <div className="flex flex-col">
                      <span className="text-sm font-medium leading-tight">
                        {lang.nativeName}
                      </span>
                      <span className="text-[10px] text-white/50">{lang.name}</span>
                    </div>

                    {isSelected && (
                      <Check className="w-4 h-4 text-[#F7DE9B] shrink-0 drop-shadow-[0_0_6px_#D9A441]" />
                    )}
                  </button>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default GoldLanguageSwitch;

