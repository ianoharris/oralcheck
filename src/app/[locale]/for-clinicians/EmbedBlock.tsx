"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";

const EMBED_CODE = `<iframe
  src="https://oralcheck.org/screener"
  style="width:100%;height:620px;border:none;border-radius:12px;"
  title="Oral Cancer Risk Screener"
  loading="lazy"
></iframe>`;

export default function EmbedBlock() {
  const t = useTranslations("EmbedBlock");
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(EMBED_CODE);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
      <h2 className="font-serif text-2xl text-ink mb-2">{t("heading")}</h2>
      <p className="text-ink-soft text-sm leading-relaxed mb-4">{t("body")}</p>
      <div className="bg-warm rounded-xl border border-warm-dim p-4 font-mono text-xs text-ink-soft overflow-x-auto whitespace-pre mb-4 leading-relaxed">
        {EMBED_CODE}
      </div>
      <button
        onClick={handleCopy}
        className="bg-brand hover:bg-brand-dark text-white font-semibold px-5 py-2.5 rounded-full text-sm transition-colors"
      >
        {copied ? t("copied") : t("copy")}
      </button>
    </section>
  );
}
