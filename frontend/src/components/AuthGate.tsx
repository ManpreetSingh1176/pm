"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import AIChatSidebar from "@/components/AIChatSidebar";

const STORAGE_KEY = "kanban.loggedIn";
const VALID_USERNAME = "user";
const VALID_PASSWORD = "password";

export function AuthGate() {
  const [signedIn, setSignedIn] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    setSignedIn(stored === "true");
    setInitialized(true);
  }, []);

  const handleSignIn = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (username === VALID_USERNAME && password === VALID_PASSWORD) {
      // call backend login to set cookie for API calls
      fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      })
        .then((res) => {
          if (!res.ok) throw new Error("login failed");
          window.localStorage.setItem(STORAGE_KEY, "true");
          setSignedIn(true);
          setError("");
        })
        .catch(() => {
          setError("Invalid username or password.");
        });
      return;
    }

    setError("Invalid username or password.");
  };

  const handleLogout = () => {
    fetch("/api/auth/logout", { method: "POST" }).finally(() => {
      window.localStorage.removeItem(STORAGE_KEY);
      setSignedIn(false);
      setUsername("");
      setPassword("");
      setError("");
    });
  };

  if (!initialized) {
    return null;
  }

  if (!signedIn) {
    return (
      <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-900">
        <div className="mx-auto flex max-w-3xl flex-col gap-8 rounded-[32px] border border-slate-200 bg-white p-8 shadow-[var(--shadow)]">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-500">
              Welcome back
            </p>
            <h1 className="mt-3 text-4xl font-semibold text-slate-900">
              Sign in to Kanban Studio
            </h1>
            <p className="mt-3 max-w-xl text-sm leading-6 text-slate-600">
              Use the demo credentials to access the Kanban board and keep your workflow visible.
            </p>
          </div>

          <form onSubmit={handleSignIn} className="grid gap-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                placeholder="user"
                autoComplete="username"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-2xl border border-slate-300 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-blue-400 focus:ring-2 focus:ring-blue-100"
                placeholder="password"
                autoComplete="current-password"
              />
            </div>

            {error ? (
              <p className="rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700">{error}</p>
            ) : null}

            <button
              type="submit"
              className="inline-flex justify-center rounded-2xl bg-[var(--primary-blue)] px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-600"
            >
              Sign in
            </button>
          </form>

          <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-600">
            <p>
              Demo credentials: <strong>user</strong> / <strong>password</strong>
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto min-h-screen max-w-[1500px] px-6 pb-16 pt-6">
        <div className="flex items-center justify-between gap-4 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-6 shadow-[var(--shadow)] backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
              Signed in as
            </p>
            <p className="mt-2 text-lg font-semibold text-[var(--navy-dark)]">user</p>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-3 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-slate-100"
          >
            Log out
          </button>
        </div>

        <div className="mt-8 flex gap-6">
          <div className="flex-1">
            <KanbanBoard />
          </div>
          <div className="w-80">
            <AIChatSidebar />
          </div>
        </div>
      </main>
    </div>
  );
}
