import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { ResultCard } from "../components/ResultCard";
import { TranslationResponse } from "../types/translation";

const SAMPLE: TranslationResponse = {
  translated_text: "Bonjour le monde",
  source_language: "en",
  target_language: "fr",
  detected_language: null,
};

function mockClipboard() {
  const writeText = vi.fn().mockResolvedValue(undefined);
  Object.defineProperty(navigator, "clipboard", {
    value: { writeText },
    configurable: true,
  });
  return writeText;
}

function renderCard(props: Partial<React.ComponentProps<typeof ResultCard>> = {}) {
  return render(
    <ResultCard
      result={null}
      isLoading={false}
      canUseSpeech={false}
      isSpeaking={false}
      onSpeak={vi.fn()}
      onStopSpeaking={vi.fn()}
      {...props}
    />,
  );
}

describe("ResultCard", () => {
  it("shows an empty state before any translation", () => {
    renderCard();
    expect(screen.getByText(/your translation will appear here/i)).toBeInTheDocument();
  });

  it("shows a loading indicator while translating", () => {
    renderCard({ result: null, isLoading: true });
    expect(screen.getByLabelText(/translating/i)).toBeInTheDocument();
  });

  it("displays the translated text", () => {
    renderCard({ result: SAMPLE });
    expect(screen.getByText("Bonjour le monde")).toBeInTheDocument();
  });

  it("shows the detected language when provided", () => {
    renderCard({ result: { ...SAMPLE, detected_language: "en" } });
    expect(screen.getByText(/detected language/i)).toBeInTheDocument();
  });

  it("copies the translated text to the clipboard", async () => {
    const user = userEvent.setup();
    const writeText = mockClipboard();
    renderCard({ result: SAMPLE });

    await user.click(screen.getByRole("button", { name: /copy translation/i }));

    expect(writeText).toHaveBeenCalledWith("Bonjour le monde");
    expect(await screen.findByText("Copied!")).toBeInTheDocument();
  });

  it("only renders the listen button when speech is supported", () => {
    const { unmount } = renderCard({ result: SAMPLE, canUseSpeech: true });
    expect(screen.getByRole("button", { name: /listen/i })).toBeInTheDocument();
    unmount();

    renderCard({ result: SAMPLE, canUseSpeech: false });
    expect(screen.queryByRole("button", { name: /listen/i })).not.toBeInTheDocument();
  });
});