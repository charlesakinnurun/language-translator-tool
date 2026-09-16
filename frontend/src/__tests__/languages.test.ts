import { describe, expect, it } from "vitest";

import {
  LANGUAGES,
  getLanguageByCode,
  getLanguageName,
  getSpeechCode,
} from "../services/languages";

describe("languages service", () => {
  it("contains more than 20 languages", () => {
    expect(LANGUAGES.length).toBeGreaterThan(20);
  });

  it("uses unique language codes", () => {
    const codes = LANGUAGES.map((language) => language.code);
    expect(new Set(codes).size).toBe(codes.length);
  });

  it("looks up a language by code", () => {
    expect(getLanguageByCode("fr")?.name).toBe("French");
    expect(getLanguageByCode("zz")).toBeUndefined();
  });

  it("provides the name of a language", () => {
    expect(getLanguageName("en")).toBe("English");
    expect(getLanguageName("xx")).toBeNull();
  });

  it("maps language codes to BCP-47 speech codes", () => {
    expect(getSpeechCode("en")).toBe("en-US");
    expect(getSpeechCode("zh")).toBe("zh-CN");
    expect(getSpeechCode("pt")).toBe("pt-BR");
  });

  it("falls back to the raw code for unknown languages", () => {
    expect(getSpeechCode("ff")).toBe("ff");
  });
});