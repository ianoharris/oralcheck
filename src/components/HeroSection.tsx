"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";
import HeroHolographicCard from "./HeroHolographicCard";

const items = [0, 1, 2, 3, 4]; // stagger indices for left column children

export default function HeroSection() {
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
    <section className="max-w-6xl mx-auto px-5 pt-16 sm:pt-24 pb-12">
      <div className="grid grid-cols-1 md:grid-cols-5 gap-10 items-center">

        {/* Left column — staggered entrance */}
        <div className="md:col-span-3 space-y-6">
          <motion.div {...fadeItem(0)}>
            <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-3 py-1 rounded-full">
              Free · Private · Evidence-based
            </span>
          </motion.div>

          <motion.div {...fadeItem(1)}>
            <h1 className="font-serif text-5xl sm:text-6xl leading-[1.05] text-ink">
              2 minutes could{" "}
              <span className="text-brand">save your life.</span>
            </h1>
          </motion.div>

          <motion.div {...fadeItem(2)}>
            <p className="text-lg text-ink-soft max-w-xl leading-relaxed">
              Oral cancer is one of the most underdiagnosed cancers — largely
              because early symptoms look ordinary. OralCheck helps you
              understand your risk in minutes and points you toward care.
            </p>
          </motion.div>

          <motion.div {...fadeItem(3)} className="pt-2">
            <div className="flex flex-wrap gap-3">
              <Link
                href="/screener"
                className="bg-accent hover:bg-accent-dark text-white px-7 py-3.5 rounded-full font-semibold transition-colors inline-flex items-center gap-2"
              >
                Start Screening
                <span aria-hidden>→</span>
              </Link>
              <Link
                href="/learn"
                className="bg-white hover:bg-warm-dim text-ink px-7 py-3.5 rounded-full font-semibold transition-colors border border-warm-dim"
              >
                Learn the signs
              </Link>
            </div>
          </motion.div>

          <motion.div {...fadeItem(4)}>
            <p className="text-xs text-ink-soft">
              Not a medical diagnosis. An educational awareness tool.
            </p>
          </motion.div>
        </div>

        {/* Right column — holographic card */}
        <div className="md:col-span-2">
          <HeroHolographicCard />
        </div>

      </div>
    </section>
  );
}
