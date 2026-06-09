"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";

const steps = [
  { label: "Tobacco use", value: "None", color: "text-low" },
  { label: "Alcohol", value: "Occasional", color: "text-mid" },
  { label: "Recent symptoms", value: "None", color: "text-low" },
];

export default function HeroResultCard() {
  const reduced = useReducedMotion();

  return (
    <motion.div
      initial={reduced ? false : { opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" as const, delay: 0.35 }}
      className="relative"
    >
      {/* Glow behind the card */}
      <div className="absolute -inset-3 bg-brand/10 rounded-3xl blur-xl" aria-hidden />

      <div className="relative bg-warm-dim rounded-2xl border border-warm-dim shadow-sm overflow-hidden">
        {/* Card header */}
        <div className="bg-brand/5 border-b border-warm-dim px-5 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-accent" />
            <span className="text-xs font-bold tracking-widest text-ink uppercase">OralCheck</span>
          </div>
          <span className="text-[10px] text-ink-soft font-mono">Sample result</span>
        </div>

        <div className="px-5 py-5">
          {/* Risk tier */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <div className="text-[10px] font-semibold uppercase tracking-widest text-ink-soft mb-1">Your risk level</div>
              <div className="font-serif text-2xl text-low font-bold">Low Risk</div>
            </div>
            {/* Score dots */}
            <div className="flex gap-1 items-center" aria-hidden>
              {[1,2,3,4].map((i) => (
                <div
                  key={i}
                  className={`w-3 h-3 rounded-full ${i === 1 ? "bg-low" : "bg-warm-dim"}`}
                />
              ))}
            </div>
          </div>

          {/* Factors */}
          <div className="space-y-2 mb-4">
            {steps.map((s) => (
              <div key={s.label} className="flex items-center justify-between text-xs">
                <span className="text-ink-soft">{s.label}</span>
                <span className={`font-semibold ${s.color}`}>{s.value}</span>
              </div>
            ))}
          </div>

          {/* AI summary */}
          <div className="bg-brand-soft rounded-xl px-4 py-3 mb-4">
            <p className="text-xs text-ink leading-relaxed">
              "Your risk factors are within normal range. Keep up your annual dental visit — oral cancer screening takes 2 minutes and is included at no extra cost."
            </p>
          </div>

          {/* CTA */}
          <Link
            href="/screener"
            className="block w-full text-center bg-accent hover:bg-accent-dark text-white text-sm font-semibold py-2.5 rounded-full transition-colors"
          >
            Get your real results →
          </Link>
        </div>

        {/* Privacy note */}
        <div className="border-t border-warm-dim px-5 py-2.5 flex items-center gap-1.5">
          <svg className="w-3 h-3 text-ink-soft flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
          </svg>
          <span className="text-[10px] text-ink-soft">Nothing saved. Answers stay on your device.</span>
        </div>
      </div>
    </motion.div>
  );
}
