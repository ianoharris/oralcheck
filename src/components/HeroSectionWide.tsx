"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";

export default function HeroSectionWide() {
  const reduced = useReducedMotion();

  const fadeItem = (i: number) =>
    reduced
      ? {}
      : {
          initial: { opacity: 0, y: 22 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.55, ease: "easeOut" as const, delay: 0.05 + i * 0.1 },
        };

  return (
    <section className="max-w-4xl mx-auto px-5 pt-24 sm:pt-32 pb-16 text-center">
      <motion.div {...fadeItem(0)}>
        <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full">
          Free · Private · Evidence-based
        </span>
      </motion.div>

      <motion.div {...fadeItem(1)} className="mt-6">
        <h1 className="font-serif text-6xl sm:text-7xl leading-[1.05] text-ink">
          2 minutes could
          <br />
          <span className="text-brand">save your life.</span>
        </h1>
      </motion.div>

      <motion.div {...fadeItem(2)} className="mt-6">
        <p className="text-xl text-ink-soft max-w-2xl mx-auto leading-relaxed">
          Oral cancer is one of the most underdiagnosed cancers — largely because
          early symptoms look ordinary. OralCheck helps you understand your risk
          in minutes and points you toward care.
        </p>
      </motion.div>

      <motion.div {...fadeItem(3)} className="mt-8 flex flex-wrap gap-3 justify-center">
        <Link
          href="/screener"
          className="bg-accent hover:bg-accent-dark text-white px-8 py-4 rounded-full font-semibold text-lg transition-colors inline-flex items-center gap-2"
        >
          Start Screening
          <span aria-hidden>→</span>
        </Link>
        <Link
          href="/learn"
          className="bg-white hover:bg-warm-dim text-ink px-8 py-4 rounded-full font-semibold text-lg transition-colors border border-warm-dim"
        >
          Learn the signs
        </Link>
      </motion.div>

      <motion.div {...fadeItem(4)} className="mt-6 space-y-1">
        <p className="text-xs text-ink-soft">Not a medical diagnosis. An educational awareness tool.</p>
        <div className="flex items-center gap-2 justify-center">
          <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand flex-shrink-0" />
          <span className="text-xs text-ink-soft">
            Shared by the{" "}
            <span className="font-semibold text-ink">Wisconsin Dental Association</span>
          </span>
        </div>
      </motion.div>

      {/* Stat strip */}
      <motion.div
        {...(reduced ? {} : {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          transition: { duration: 0.8, delay: 0.7 },
        })}
        className="mt-14 grid grid-cols-3 gap-6 border-t border-warm-dim pt-10"
      >
        {[
          { stat: "54,000+", label: "new US cases each year" },
          { stat: "84%", label: "survival rate if caught early" },
          { stat: "2 min", label: "is all it takes to screen" },
        ].map(({ stat, label }) => (
          <div key={stat} className="text-center">
            <div className="font-serif text-3xl text-brand">{stat}</div>
            <div className="text-xs text-ink-soft mt-1">{label}</div>
          </div>
        ))}
      </motion.div>
    </section>
  );
}
