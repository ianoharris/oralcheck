"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";

/*
  DIRECTION D: Pure typography.
  The headline IS the design — no decorative elements, no shapes.
  Scale, color splits, and air do all the work.
*/

const headline = [
  { text: "2 minutes", color: "#e8634a" },
  { text: "could save", color: "#2d2d2d" },
  { text: "your life.", color: "#0d7377" },
];

const ease = [0.16, 1, 0.3, 1] as const;

export default function HeroMockupD() {
  const reduced = useReducedMotion();

  return (
    <section
      className="min-h-[100dvh] flex flex-col px-6 sm:px-10 lg:px-16 pt-14 pb-10"
      style={{ background: "#faf9f6" }}
    >
      {/* Top bar */}
      <motion.div
        className="flex items-center justify-between mb-auto"
        initial={reduced ? false : { opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.05 }}
      >
        <span
          style={{
            fontSize: "10px",
            fontWeight: 700,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "#9b9790",
          }}
        >
          Free · Private · Evidence-based
        </span>
      </motion.div>

      {/* Headline — full width, fills the middle */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", paddingBlock: "3rem" }}>
        <h1
          className="font-serif w-full"
          style={{
            fontSize: "clamp(3.8rem, 11vw, 9.5rem)",
            lineHeight: 0.95,
            letterSpacing: "-0.02em",
          }}
        >
          {headline.map((line, i) => (
            <motion.span
              key={line.text}
              style={{ display: "block", color: line.color }}
              initial={reduced ? false : { opacity: 0, y: 48 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.7, delay: 0.2 + i * 0.13, ease }}
            >
              {line.text}
            </motion.span>
          ))}
        </h1>
      </div>

      {/* Bottom: rule + body + CTAs */}
      <motion.div
        initial={reduced ? false : { opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.72, ease }}
      >
        <div
          style={{
            height: "1px",
            background: "#e0ddd6",
            marginBottom: "1.4rem",
          }}
        />
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6">
          <p
            style={{
              fontSize: "0.97rem",
              lineHeight: "1.68",
              color: "#6b6b6b",
              maxWidth: "42ch",
            }}
          >
            Oral cancer is one of the most underdiagnosed cancers, largely
            because early symptoms look ordinary. Take 2 minutes to understand
            your risk.
          </p>

          <div className="flex gap-3 flex-shrink-0">
            <Link
              href="/screener"
              style={{
                backgroundColor: "#e8634a",
                color: "#fff",
                padding: "0.85rem 1.75rem",
                borderRadius: "9999px",
                fontWeight: 600,
                fontSize: "0.875rem",
                display: "inline-flex",
                alignItems: "center",
                gap: "6px",
                whiteSpace: "nowrap",
                textDecoration: "none",
              }}
            >
              Start Screening →
            </Link>
            <Link
              href="/learn"
              style={{
                border: "1px solid #d6d3cc",
                color: "#2d2d2d",
                padding: "0.85rem 1.75rem",
                borderRadius: "9999px",
                fontWeight: 600,
                fontSize: "0.875rem",
                display: "inline-flex",
                alignItems: "center",
                whiteSpace: "nowrap",
                textDecoration: "none",
              }}
            >
              Learn the signs
            </Link>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
