"use client";

import { useState } from "react";

export default function ContactForm() {
  const [message, setMessage] = useState("");
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    setStatus("sending");

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message, email: email.trim() || undefined }),
      });

      if (res.ok) {
        setStatus("sent");
        setMessage("");
        setEmail("");
      } else {
        setStatus("error");
      }
    } catch {
      setStatus("error");
    }
  };

  if (status === "sent") {
    return (
      <div className="text-center py-6">
        <div className="text-3xl mb-3">✓</div>
        <p className="font-semibold text-ink">Got it — thanks for reaching out.</p>
        <p className="text-sm text-ink-soft mt-1">
          If you left an email, I&apos;ll get back to you soon.
        </p>
        <button
          onClick={() => setStatus("idle")}
          className="mt-4 text-sm text-brand hover:underline"
        >
          Send another message
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="feedback-message" className="block text-sm font-semibold text-ink mb-1.5">
          Message
        </label>
        <textarea
          id="feedback-message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="A bug you found, something that could be clearer, a question — anything."
          rows={4}
          maxLength={2000}
          required
          className="w-full rounded-xl border border-warm-dim bg-warm px-4 py-3 text-sm text-ink placeholder:text-ink-soft/60 focus:outline-none focus:ring-2 focus:ring-brand/30 resize-none"
        />
      </div>
      <div>
        <label htmlFor="feedback-email" className="block text-sm font-semibold text-ink mb-1.5">
          Email <span className="font-normal text-ink-soft">(optional — leave blank to stay anonymous)</span>
        </label>
        <input
          id="feedback-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          className="w-full rounded-xl border border-warm-dim bg-warm px-4 py-3 text-sm text-ink placeholder:text-ink-soft/60 focus:outline-none focus:ring-2 focus:ring-brand/30"
        />
      </div>
      {status === "error" && (
        <p className="text-sm text-accent">Something went wrong — please try again.</p>
      )}
      <button
        type="submit"
        disabled={status === "sending" || !message.trim()}
        className="bg-brand hover:bg-brand-dark disabled:bg-warm-dim disabled:text-ink-soft disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-full transition-colors text-sm"
      >
        {status === "sending" ? "Sending…" : "Send message"}
      </button>
    </form>
  );
}
