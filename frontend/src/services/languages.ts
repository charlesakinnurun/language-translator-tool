export interface Language {
  code: string;
  name: string;
  speechCode: string;
}

/**
 * Supported languages. `code` matches the ISO 639-1 codes the backend
 * accepts; `speechCode` is a BCP-47 tag used by the browser SpeechSynthesis
 * API for text-to-speech.
 */
export const LANGUAGES: Language[] = [
  { code: "ar", name: "Arabic", speechCode: "ar-SA" },
  { code: "bn", name: "Bengali", speechCode: "bn-BD" },
  { code: "de", name: "German", speechCode: "de-DE" },
  { code: "en", name: "English", speechCode: "en-US" },
  { code: "es", name: "Spanish", speechCode: "es-ES" },
  { code: "fr", name: "French", speechCode: "fr-FR" },
  { code: "hi", name: "Hindi", speechCode: "hi-IN" },
  { code: "id", name: "Indonesian", speechCode: "id-ID" },
  { code: "it", name: "Italian", speechCode: "it-IT" },
  { code: "ja", name: "Japanese", speechCode: "ja-JP" },
  { code: "ko", name: "Korean", speechCode: "ko-KR" },
  { code: "nl", name: "Dutch", speechCode: "nl-NL" },
  { code: "pl", name: "Polish", speechCode: "pl-PL" },
  { code: "pt", name: "Portuguese", speechCode: "pt-BR" },
  { code: "ru", name: "Russian", speechCode: "ru-RU" },
  { code: "sw", name: "Swahili", speechCode: "sw-KE" },
  { code: "ta", name: "Tamil", speechCode: "ta-IN" },
  { code: "te", name: "Telugu", speechCode: "te-IN" },
  { code: "th", name: "Thai", speechCode: "th-TH" },
  { code: "tr", name: "Turkish", speechCode: "tr-TR" },
  { code: "vi", name: "Vietnamese", speechCode: "vi-VN" },
  { code: "zh", name: "Chinese (Simplified)", speechCode: "zh-CN" },
];

export function getLanguageByCode(code: string): Language | undefined {
  return LANGUAGES.find((language) => language.code === code);
}

export function getSpeechCode(code: string): string {
  return getLanguageByCode(code)?.speechCode ?? code;
}

export function getLanguageName(code: string): string | null {
  return getLanguageByCode(code)?.name ?? null;
}