"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import Icon from "@/components/Icon";

/**
 * Collects a short review of the screener.
 *
 * Posts through the existing /api/contact route rather than adding a second
 * public endpoint: the route is already rate limited and already delivers to
 * the same inbox, and a review is just feedback with a rating and a decision
 * about whether it can be quoted.
 */
export default function ReviewForm() {
  const t = useTranslations("ReviewForm");
  const [rating, setRating] = useState(0);
  const [hovered, setHovered] = useState(0);
  const [text, setText] = useState("");
  const [name, setName] = useState("");
  const [consent, setConsent] = useState(false);
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [error, setError] = useState("");

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (status === "sending" || rating === 0) return;
    setStatus("sending");
    setError("");

    const message = [
      "REVIEW",
      `Rating: ${rating}/5`,
      `Name: ${name.trim() || "Anonymous"}`,
      `Okay to publish: ${consent ? "yes" : "no"}`,
      "",
      text.trim(),
    ].join("\n");

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message }),
      });
      if (!res.ok) {
        const d = await res.json().catch(() => ({}));
        throw new Error(d.error || t("genericError"));
      }
      setStatus("sent");
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : t("genericError"));
    }
  };

  if (status === "sent") {
    return (
      <div className="text-center py-4">
        <div className="w-11 h-11 rounded-full bg-brand-soft text-brand flex items-center justify-center mx-auto mb-3">
          <Icon name="check" size={22} weight="bold" />
        </div>
        <div className="font-serif text-xl text-ink mb-1">{t("sentTitle")}</div>
        <p className="text-sm text-ink-soft">{t("sentBody")}</p>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-4">
      <fieldset>
        <legend className="text-sm font-medium text-ink mb-2">{t("ratingLabel")}</legend>
        <div className="flex gap-1" onMouseLeave={() => setHovered(0)}>
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              key={n}
              type="button"
              onClick={() => setRating(n)}
              onMouseEnter={() => setHovered(n)}
              aria-label={t("starLabel", { n })}
              aria-pressed={rating === n}
              className="p-0.5 text-accent hover:scale-110 transition-transform"
            >
              <Icon name="star" size={26} weight={n <= (hovered || rating) ? "fill" : "regular"} />
            </button>
          ))}
        </div>
      </fieldset>

      <textarea
        required
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        maxLength={1000}
        placeholder={t("textPlaceholder")}
        aria-label={t("textLabel")}
        className="w-full bg-warm px-4 py-3 rounded-xl border border-warm-dim focus:outline-none focus:ring-2 focus:ring-brand text-ink placeholder:text-ink-soft resize-y"
      />

      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        maxLength={80}
        placeholder={t("namePlaceholder")}
        aria-label={t("nameLabel")}
        className="w-full bg-warm px-4 py-3 rounded-xl border border-warm-dim focus:outline-none focus:ring-2 focus:ring-brand text-ink placeholder:text-ink-soft"
      />

      <label className="flex items-start gap-2.5 text-sm text-ink-soft leading-relaxed cursor-pointer">
        <input
          type="checkbox"
          checked={consent}
          onChange={(e) => setConsent(e.target.checked)}
          className="mt-0.5 w-4 h-4 accent-[var(--brand)] shrink-0"
        />
        {t("consent")}
      </label>

      <button
        type="submit"
        disabled={status === "sending" || rating === 0 || !text.trim()}
        className="bg-brand hover:bg-brand-dark disabled:opacity-60 text-white font-semibold px-6 py-3 rounded-xl transition-colors"
      >
        {status === "sending" ? t("sending") : t("submit")}
      </button>

      {rating === 0 && text.trim() && (
        <p className="text-sm text-ink-soft">{t("needRating")}</p>
      )}
      {status === "error" && <p className="text-sm text-accent">{error}</p>}
    </form>
  );
}
