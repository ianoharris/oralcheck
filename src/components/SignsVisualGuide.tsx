"use client";

import { useState } from "react";
import Icon from "@/components/Icon";
import { useTranslations } from "next-intl";
import { motion, AnimatePresence, useReducedMotion } from "framer-motion";

type SignCopy = { name: string; also?: string; where: string; desc: string; watch: string };
// tone is layout metadata (which color the risk cue gets), kept separate from
// the translated copy in messages.SignsVisualGuide.signs (same array order).
const SIGN_META = [
  { id: "white", tone: "watch" as const },
  { id: "red", tone: "higher" as const },
  { id: "mixed", tone: "higher" as const },
  { id: "sore", tone: "higher" as const },
  { id: "lump", tone: "watch" as const },
  { id: "lip", tone: "watch" as const },
];

const TISSUE = "#e7d9d2"; // stylised oral-surface tone (single visual world, on purpose)
const TISSUE_EDGE = "#d8c5bc";

function SignArt({ id }: { id: string }) {
  // A clean diagram, not a clinical photo: a tissue tile with the sign on it.
  return (
    <svg viewBox="0 0 320 240" className="w-full h-full" role="img" aria-hidden>
      <defs>
        <radialGradient id="tissue" cx="50%" cy="42%" r="75%">
          <stop offset="0%" stopColor="#efe3dd" />
          <stop offset="100%" stopColor={TISSUE} />
        </radialGradient>
        <radialGradient id="dome" cx="42%" cy="38%" r="70%">
          <stop offset="0%" stopColor="#f0e2db" />
          <stop offset="100%" stopColor="#cdb2a7" />
        </radialGradient>
      </defs>
      <rect x="8" y="8" width="304" height="224" rx="26" fill="url(#tissue)" stroke={TISSUE_EDGE} strokeWidth="2" />

      {id === "white" && (
        <path d="M118 96 q34-26 70-6 q26 16 12 44 q-16 30-58 24 q-40-6-40-34 q0-18 16-28Z"
          fill="#f6f2e9" stroke="#e4dccb" strokeWidth="2" />
      )}
      {id === "red" && (
        <path d="M112 100 q40-24 78-2 q22 16 8 42 q-18 28-62 22 q-38-6-36-36 q1-16 12-26Z"
          fill="#c0392b" opacity="0.9" />
      )}
      {id === "mixed" && (
        <g>
          <path d="M108 104 q36-24 72-6 q24 16 10 40 q-18 26-58 22 q-36-6-36-34 q0-14 12-22Z"
            fill="#c0392b" opacity="0.85" />
          <path d="M150 96 q30-8 46 12 q10 16-4 30 q-18 14-40 4 q-16-8-12-26 q3-14 10-20Z"
            fill="#f6f2e9" opacity="0.92" />
        </g>
      )}
      {id === "sore" && (
        <g>
          <ellipse cx="160" cy="120" rx="52" ry="40" fill="#e9c9be" />
          <ellipse cx="160" cy="120" rx="34" ry="26" fill="#f6f0e6" />
          <ellipse cx="160" cy="120" rx="20" ry="15" fill="#b98476" />
        </g>
      )}
      {id === "lump" && (
        <g>
          <ellipse cx="164" cy="176" rx="70" ry="14" fill="#000" opacity="0.08" />
          <circle cx="160" cy="126" r="52" fill="url(#dome)" stroke="#c6ab9f" strokeWidth="2" />
        </g>
      )}
      {id === "lip" && (
        <g>
          <path d="M70 120 q90-46 180 0 q-90 40-180 0Z" fill="#cf8f86" />
          <path d="M70 120 q90 34 180 0" fill="none" stroke="#a86d63" strokeWidth="2" />
          <g fill="#e8dccf">
            <circle cx="150" cy="112" r="5" /><circle cx="166" cy="116" r="4" />
            <circle cx="176" cy="110" r="5" /><circle cx="158" cy="120" r="3.5" />
          </g>
        </g>
      )}
    </svg>
  );
}

export default function SignsVisualGuide() {
  const t = useTranslations("SignsVisualGuide");
  const [active, setActive] = useState(0);
  const reduce = useReducedMotion();

  const copy = t.raw("signs") as SignCopy[];
  const SIGNS = SIGN_META.map((meta, i) => ({ ...meta, ...copy[i] }));
  const sign = SIGNS[active];

  return (
    <section
      aria-label={t("heading")}
      className="not-prose my-10 rounded-3xl border border-warm-dim bg-warm-dim/50 p-5 sm:p-7"
    >
      <div className="mb-1 text-xs font-semibold uppercase tracking-wider text-brand">
        {t("eyebrow")}
      </div>
      <h2 className="font-serif text-2xl sm:text-3xl text-ink mb-1">
        {t("heading")}
      </h2>
      <p className="text-sm text-ink-soft mb-5 max-w-xl leading-relaxed">
        {t("subheading")}
      </p>

      {/* chips */}
      <div className="flex flex-wrap gap-2 mb-5">
        {SIGNS.map((s, i) => (
          <button
            key={s.id}
            onClick={() => setActive(i)}
            aria-pressed={i === active}
            className={`relative text-sm font-medium px-4 py-1.5 rounded-full transition-colors ${
              i === active ? "text-white" : "text-ink-soft hover:text-ink bg-warm border border-warm-dim"
            }`}
          >
            {i === active && (
              <motion.span
                layoutId="signChip"
                className="absolute inset-0 rounded-full bg-brand"
                transition={reduce ? { duration: 0 } : { type: "spring", stiffness: 500, damping: 34 }}
              />
            )}
            <span className="relative z-10">{s.name}</span>
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
        {/* diagram viewer */}
        <div className="relative rounded-2xl overflow-hidden bg-warm aspect-[4/3]">
          <AnimatePresence mode="wait">
            <motion.div
              key={sign.id}
              initial={reduce ? { opacity: 0 } : { opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={reduce ? { opacity: 0 } : { opacity: 0, scale: 1.02 }}
              transition={{ duration: 0.3, ease: "easeOut" }}
              className="absolute inset-0 p-4"
            >
              <SignArt id={sign.id} />
            </motion.div>
          </AnimatePresence>
          {!reduce && (
            <motion.span
              key={`ring-${sign.id}`}
              className="pointer-events-none absolute left-1/2 top-1/2 h-24 w-24 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 border-brand"
              initial={{ opacity: 0.5, scale: 0.6 }}
              animate={{ opacity: 0, scale: 1.8 }}
              transition={{ duration: 1.4, ease: "easeOut" }}
            />
          )}
        </div>

        {/* detail */}
        <AnimatePresence mode="wait">
          <motion.div
            key={sign.id}
            initial={reduce ? { opacity: 0 } : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.28, ease: "easeOut" }}
          >
            <div className="flex items-baseline flex-wrap gap-x-2 gap-y-0">
              <h3 className="font-serif text-2xl text-ink">{sign.name}</h3>
              {sign.also && <span className="text-sm text-ink-soft italic">{sign.also}</span>}
            </div>
            <div className="text-xs font-medium text-ink-soft mt-1 mb-3">{sign.where}</div>
            <p className="text-[15px] text-ink-soft leading-relaxed mb-4">{sign.desc}</p>
            <div
              className={`rounded-xl px-4 py-3 text-sm leading-relaxed ${
                sign.tone === "higher"
                  ? "bg-high/10 border border-high/25 text-ink"
                  : "bg-brand-soft border border-brand/15 text-ink"
              }`}
            >
              <span className="font-semibold">
                {sign.tone === "higher" ? `${t("higherAction")} ` : `${t("watchAction")} `}
              </span>
              {sign.watch}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>

      {/* the unifying rule */}
      <div className="mt-6 flex items-center gap-3 rounded-2xl bg-brand px-5 py-4 text-white">
        <span className="shrink-0" aria-hidden><Icon name="timer" size={26} /></span>
        <p className="text-sm sm:text-[15px] leading-snug">
          <span className="font-semibold">{t("twoWeekBold")}</span>{" "}{t("twoWeekRest")}
        </p>
      </div>
    </section>
  );
}
