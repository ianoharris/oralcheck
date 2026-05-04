"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { learnArticles as articles } from "@/lib/learnArticles";

export default function AnimatedLearnCards() {
  const reduced = useReducedMotion();

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {articles.map(({ href, tag, title, description, icon }, i) => (
        <motion.div
          key={href}
          initial={reduced ? false : { opacity: 0, y: 24 }}
          whileInView={reduced ? {} : { opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-50px" }}
          transition={{ duration: 0.45, ease: "easeOut" as const, delay: i * 0.07 }}
        >
          <Link
            href={href}
            className="group flex flex-col h-full bg-white rounded-2xl border border-warm-dim p-6 hover:border-brand/40 hover:shadow-md transition-all duration-200"
          >
            <div className="flex items-center gap-2 mb-4">
              <span className="text-2xl" aria-hidden>{icon}</span>
              <span className="text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-2 py-0.5 rounded-full">
                {tag}
              </span>
            </div>
            <h2 className="font-serif text-xl text-ink mb-2 group-hover:text-brand transition-colors">
              {title}
            </h2>
            <p className="text-ink-soft text-sm leading-relaxed flex-1">{description}</p>
            <span className="mt-4 text-sm font-semibold text-brand group-hover:underline">
              Read →
            </span>
          </Link>
        </motion.div>
      ))}
    </div>
  );
}
