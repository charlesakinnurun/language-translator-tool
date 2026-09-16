import { beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import App from "../App";

let fetchMock: ReturnType<typeof vi.fn>;

function stubFetchOk() {
  fetchMock = vi.fn().mockResolvedValue({
    ok: true,
    status: 200,
    json: async () => ({
      translated_text: "Hola",
      source_language: "en",
      target_language: "es",
      detected_language: null,
    }),
  });
  vi.stubGlobal("fetch", fetchMock);
}

async function typeText(user: ReturnType<typeof userEvent.setup>, text: string) {
  await user.type(screen.getByLabelText(/text to translate/i), text);
}

beforeEach(() => {
  vi.stubGlobal("fetch", vi.fn());
});

describe("App", () => {
  it("renders the main heading and language controls", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: /language translation tool/i }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/^from$/i)).toHaveValue("en");
    expect(screen.getByLabelText(/^to$/i)).toHaveValue("es");
    expect(screen.getByRole("button", { name: /translate/i })).toBeInTheDocument();
  });

  it("translates text end to end", async () => {
    const user = userEvent.setup();
    stubFetchOk();
    render(<App />);

    await typeText(user, "Hello");
    await user.click(screen.getByRole("button", { name: /translate/i }));

    expect(await screen.findByText("Hola")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/translate"),
      expect.objectContaining({
        body: JSON.stringify({
          text: "Hello",
          source_language: "en",
          target_language: "es",
        }),
      }),
    );
  });

  it("shows an error alert when submitting empty text", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /translate/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /enter some text to translate/i,
    );
  });

  it("shows an error alert when source and target languages match", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.selectOptions(screen.getByLabelText(/^to$/i), "en");
    await typeText(user, "Hello");
    await user.click(screen.getByRole("button", { name: /translate/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /source and target languages must be different/i,
    );
  });

  it("swaps the source and target languages", async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole("button", { name: /swap languages/i }));

    expect(screen.getByLabelText(/^from$/i)).toHaveValue("es");
    expect(screen.getByLabelText(/^to$/i)).toHaveValue("en");
  });

  it("clears the input when the reset button is used", async () => {
    const user = userEvent.setup();
    render(<App />);

    await typeText(user, "Hello");
    await user.click(screen.getByRole("button", { name: /clear everything/i }));

    expect(screen.getByLabelText(/text to translate/i)).toHaveValue("");
  });

  it("triggers translation with Ctrl + Enter", async () => {
    const user = userEvent.setup();
    stubFetchOk();
    render(<App />);

    const textarea = screen.getByLabelText(/text to translate/i);
    await user.type(textarea, "Hello");
    await user.keyboard("{Control>}{Enter}{/Control}");

    expect(await screen.findByText("Hola")).toBeInTheDocument();
  });
});