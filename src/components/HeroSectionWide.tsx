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
    <section className="max-w-4xl mx-auto px-5 pt-32 sm:pt-44 pb-16 text-center">
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

      <motion.div {...fadeItem(4)} className="mt-6">
        <p className="text-xs text-ink-soft">Not a medical diagnosis. An educational awareness tool.</p>
      </motion.div>

    </section>
  );
}
