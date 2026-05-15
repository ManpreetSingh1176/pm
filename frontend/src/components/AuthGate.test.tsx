import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AuthGate } from "@/components/AuthGate";

describe("AuthGate", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  it("shows the login form and signs in with valid credentials", async () => {
    render(<AuthGate />);

    expect(await screen.findByRole("heading", { name: /sign in to kanban studio/i })).toBeVisible();

    await userEvent.type(screen.getByLabelText(/username/i), "user");
    await userEvent.type(screen.getByLabelText(/password/i), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("heading", { name: /kanban studio/i })).toBeVisible();
  });

  it("shows an error for invalid credentials", async () => {
    render(<AuthGate />);

    await userEvent.type(screen.getByLabelText(/username/i), "wrong");
    await userEvent.type(screen.getByLabelText(/password/i), "credentials");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByText(/invalid username or password/i)).toBeVisible();
  });
});
