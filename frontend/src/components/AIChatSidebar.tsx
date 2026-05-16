"use client";

import { useState } from "react";

type Message = { role: "user" | "assistant"; text: string };

export function AIChatSidebar() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [notification, setNotification] = useState<string | null>(null);

  const send = async () => {
    if (!text.trim()) return;
    const question = text.trim();
    setMessages((m) => [...m, { role: "user", text: question }]);
    setText("");
    setBusy(true);
    setNotification(null);

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, history: [] }),
      });

      if (res.status === 401) {
        setNotification("AI chat requires backend login.");
        setBusy(false);
        return;
      }

      const data = await res.json().catch(() => null);
      if (!res.ok) {
        const errorText = data?.detail || data?.message || `AI request failed (${res.status})`;
        setNotification(errorText);
        setBusy(false);
        return;
      }

      const reply = data?.userMessage || data?.message || data?.detail;
      if (!reply) {
        setNotification("AI returned no reply.");
        setBusy(false);
        return;
      }

      setMessages((m) => [...m, { role: "assistant", text: reply }]);

      if (data.kanbanUpdate) {
        // Dispatch a window event so the board can update itself in-place
        try {
          window.dispatchEvent(new CustomEvent("ai:kanbanUpdate", { detail: data.kanbanUpdate }));
          setNotification("AI applied board updates.");
        } catch (e) {
          setNotification("AI returned board updates. Reload to apply.");
        }
      }
    } catch (err) {
      setNotification("AI request failed.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <aside className={`transition-all ${open ? "w-80" : "w-12"} relative` }>
      <div className="flex h-full flex-col gap-2">
        <div className="flex items-center justify-between p-2">
          <button
            aria-label="toggle-ai"
            className="rounded-full bg-[var(--primary-blue)] p-2 text-white"
            onClick={() => setOpen((v) => !v)}
          >
            AI
          </button>
        </div>

        {open ? (
          <div className="flex h-[640px] flex-col gap-3 overflow-hidden rounded-lg border border-[var(--stroke)] bg-white p-3 shadow">
            <div className="flex-1 overflow-auto p-1">
              {messages.length === 0 ? (
                <p className="text-sm text-[var(--gray-text)]">Ask about the board or request changes.</p>
              ) : (
                messages.map((m, i) => (
                  <div key={i} className={`mb-2 rounded-lg p-2 ${m.role === 'user' ? 'bg-slate-100 text-slate-900' : 'bg-blue-50 text-slate-900'}`}>
                    <div className="text-xs font-semibold uppercase text-[var(--gray-text)]">{m.role}</div>
                    <div className="mt-1 text-sm">{m.text}</div>
                  </div>
                ))
              )}
            </div>

            <div className="mt-2 flex gap-2">
              <input
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="flex-1 rounded-2xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none"
                placeholder="Ask the AI to update the board..."
                onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
              />
              <button
                disabled={busy}
                onClick={send}
                className="rounded-2xl bg-[var(--primary-blue)] px-4 py-2 text-sm font-semibold text-white disabled:opacity-60"
              >
                Send
              </button>
            </div>

            {notification ? <div className="mt-2 text-sm text-slate-700">{notification}</div> : null}
          </div>
        ) : null}
      </div>
    </aside>
  );
}

export default AIChatSidebar;
