"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";

const articles = [
  {
    href: "/learn/signs",
    tag: "Symptoms",
    title: "Signs & Warning Symptoms",
    description: "Red and white patches, sores that don't heal, lumps, and numbness — what to look for and when to act.",
    icon: "⚠️",
  },
  {
    href: "/learn/self-exam",
    tag: "How-to",
    title: "How to Do a 2-Minute Self-Exam",
    description: "Step-by-step: lips, gums, tongue, floor of mouth, palate, throat. All you need is a mirror.",
    icon: "🔎",
  },
  {
    href: "/learn/facts",
    tag: "Facts",
    title: "Oral Cancer Facts & Stats",
    description: "Incidence, survival rates by stage, who's most affected, and the growing role of HPV.",
    icon: "📊",
  },
  {
    href: "/learn/hpv",
    tag: "Risk Factor",
    title: "HPV and Oral Cancer",
    description: "HPV-16 is now the leading cause of throat cancer in the US. What that means, who's at risk, and how the vaccine helps.",
    icon: "🦠",
  },
  {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "How to Prevent Oral Cancer",
    description: "Six evidence-based steps: quit tobacco, limit alcohol, get vaccinated, protect your lips, and get screened regularly.",
    icon: "🛡️",
  },
  {
    href: "/learn/oral-cancer",
    tag: "Overview",
    title: "What Is Oral Cancer?",
    description: "Definition, types, key statistics, causes, and what the warning signs look like — a plain-English overview.",
    icon: "📖",
  },
  {
    href: "/learn/canker-sore-vs-oral-cancer",
    tag: "Comparison",
    title: "Canker Sore vs. Oral Cancer",
    description: "They can look similar. Here's how to tell them apart — and when a sore in your mouth needs a clinical eye.",
    icon: "🔬",
  },
];

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
