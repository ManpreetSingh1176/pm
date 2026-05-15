import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { vi } from "vitest";
import AIChatSidebar from "./AIChatSidebar";

describe("AIChatSidebar", () => {
  beforeEach(() => {
    // @ts-ignore
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  it("toggles open and shows input", async () => {
    render(<AIChatSidebar />);
    const toggle = screen.getByLabelText("toggle-ai");
    expect(toggle).toBeInTheDocument();

    fireEvent.click(toggle);
    await waitFor(() => {
      expect(screen.getByPlaceholderText("Ask the AI to update the board...")).toBeInTheDocument();
    });
  });

  it("shows login notification on 401 response", async () => {
    // @ts-ignore
    global.fetch.mockResolvedValue({ status: 401, json: async () => ({}) });
    render(<AIChatSidebar />);
    const toggle = screen.getByLabelText("toggle-ai");
    fireEvent.click(toggle);

    const input = await screen.findByPlaceholderText("Ask the AI to update the board...");
    fireEvent.change(input, { target: { value: "Update title" } });

    const send = screen.getByText("Send");
    fireEvent.click(send);

    await waitFor(() => {
      expect(screen.getByText("AI chat requires backend login.")).toBeInTheDocument();
    });
  });
});
