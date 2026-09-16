import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { LanguageSelect } from "../components/LanguageSelect";
import { LANGUAGES } from "../services/languages";

function renderSelect(props: Partial<React.ComponentProps<typeof LanguageSelect>> = {}) {
  return render(
    <LanguageSelect
      id="test-language"
      label="From"
      value="en"
      onChange={vi.fn()}
      {...props}
    />,
  );
}

describe("LanguageSelect", () => {
  it("renders every supported language as an option", () => {
    renderSelect();

    expect(screen.getAllByRole("option")).toHaveLength(LANGUAGES.length);
    expect(screen.getByRole("option", { name: "English" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Chinese (Simplified)" })).toBeInTheDocument();
  });

  it("reflects the selected value", () => {
    renderSelect({ value: "fr" });
    expect(screen.getByRole("combobox")).toHaveValue("fr");
  });

  it("reports the newly selected code", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderSelect({ onChange });

    await user.selectOptions(screen.getByRole("combobox"), "fr");

    expect(onChange).toHaveBeenCalledWith("fr");
  });
});