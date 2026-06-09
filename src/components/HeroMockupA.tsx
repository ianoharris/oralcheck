"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";

/*
  DIRECTION A: "Cartographic" — dark teal field + geometric SVG
  Color strategy: Drenched. The brand color IS the surface.
  The geometry is abstract: concentric rings from off-screen top-right,
  a fine dot grid, and a single coral arc — suggest precision and anatomy
  without being literal. Think deep-ocean cartography.
*/

function GeometricField() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      {/* Base: deep teal, tinted toward the ocean end of the spectrum */}
      <div className="absolute inset-0" style={{ background: "#07292c" }} />

      {/* Fine dot grid via CSS — gives depth without noise */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(224,240,240,0.18) 1px, transparent 1px)",
          backgroundSize: "36px 36px",
          backgroundPosition: "18px 18px",
        }}
      />

      {/* SVG: concentric rings from top-right corner + a coral accent arc */}
      <svg
        className="absolute inset-0 w-full h-full"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 1440 840"
        preserveAspectRatio="xMaxYMin slice"
      >
        {/* Concentric rings centered off top-right */}
        {[420, 560, 700, 850, 1000].map((r, i) => (
          <circle
            key={r}
            cx="1320"
            cy="-40"
            r={r}
            fill="none"
            stroke="rgba(13,115,119,0.55)"
            strokeWidth="0.75"
            opacity={0.5 - i * 0.07}
          />
        ))}

        {/* Single coral accent arc — cuts across the field */}
        <path
          d="M 980 -40 Q 1340 440 960 880"
          fill="none"
          stroke="#e8634a"
          strokeWidth="1.5"
          opacity="0.35"
        />

        {/* Fine horizontal rule at golden ratio */}
        <line
          x1="0"
          y1="520"
          x2="1440"
          y2="520"
          stroke="rgba(224,240,240,0.07)"
          strokeWidth="1"
        />

        {/* Small cross-hair at the ring origin, barely visible */}
        <line x1="1310" y1="-50" x2="1330" y2="-30" stroke="rgba(232,99,74,0.4)" strokeWidth="1" />
        <line x1="1330" y1="-50" x2="1310" y2="-30" stroke="rgba(232,99,74,0.4)" strokeWidth="1" />
      </svg>

      {/* Vignette: soft fade at left edge to keep text legible */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(90deg, rgba(7,41,44,0.45) 0%, transparent 55%)",
        }}
      />

      {/* Bottom fade */}
      <div
        className="absolute inset-x-0 bottom-0 h-32"
        style={{ background: "linear-gradient(to top, rgba(7,41,44,0.8) 0%, transparent 100%)" }}
      />
    </div>
  );
}

const f = (delay: number) => ({
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5, delay, ease: [0.16, 1, 0.3, 1] as const },
});

const stats = [
  { value: "54,000", label: "new US cases yearly" },
  { value: "84%", label: "survive if caught early" },
  { value: "2 min", label: "to complete the screener" },
];

export default function HeroMockupA() {
  const reduced = useReducedMotion();

  return (
    <section className="relative min-h-[100dvh] flex items-center overflow-hidden">
      <GeometricField />

      <div className="relative z-10 max-w-6xl mx-auto px-6 lg:px-12 w-full py-32">
        <div style={{ maxWidth: "660px" }}>

          {/* Eyebrow: rule + label */}
          <motion.div
            className="flex items-center gap-3 mb-8"
            {...(reduced ? {} : f(0.1))}
          >
            <div style={{ width: "28px", height: "1px", backgroundColor: "#e8634a", flexShrink: 0 }} />
            <span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.2em",
                textTransform: "uppercase",
                color: "rgba(224,240,240,0.7)",
              }}
            >
              Free · Private · Evidence-based
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            className="font-serif leading-[1.02]"
            style={{
              fontSize: "clamp(3rem, 5.8vw, 5.25rem)",
              color: "rgba(240,238,232,0.97)",
              marginBottom: "1.75rem",
            }}
            {...(reduced ? {} : f(0.22))}
          >
            2 minutes could
            <br />
            <span style={{ color: "#e8634a" }}>save your life.</span>
          </motion.h1>

          {/* Body */}
          <motion.p
            style={{
              fontSize: "1rem",
              lineHeight: "1.7",
              color: "rgba(224,240,240,0.62)",
              maxWidth: "46ch",
              marginBottom: "2.25rem",
            }}
            {...(reduced ? {} : f(0.36))}
          >
            Oral cancer is one of the most underdiagnosed cancers, largely
            because early symptoms look ordinary. OralCheck helps you understand
            your risk in minutes and points you toward care.
          </motion.p>

          {/* CTAs */}
          <motion.div
            className="flex flex-wrap gap-3"
            style={{ marginBottom: "3rem" }}
            {...(reduced ? {} : f(0.48))}
          >
            <Link
              href="/screener"
              className="inline-flex items-center gap-2 font-semibold transition-all duration-200"
              style={{
                backgroundColor: "#e8634a",
                color: "#fff",
                padding: "0.85rem 1.75rem",
                borderRadius: "9999px",
                fontSize: "0.9rem",
              }}
            >
              Start Screening →
            </Link>
            <Link
              href="/learn"
              className="inline-flex items-center gap-2 font-semibold transition-all duration-200"
              style={{
                border: "1px solid rgba(224,240,240,0.2)",
                color: "rgba(224,240,240,0.82)",
                padding: "0.85rem 1.75rem",
                borderRadius: "9999px",
                fontSize: "0.9rem",
              }}
            >
              Learn the signs
            </Link>
          </motion.div>

          {/* Stats row */}
          <motion.div
            className="flex flex-wrap gap-8"
            style={{
              borderTop: "1px solid rgba(224,240,240,0.1)",
              paddingTop: "1.5rem",
            }}
            {...(reduced ? {} : f(0.6))}
          >
            {stats.map(({ value, label }) => (
              <div key={value}>
                <div
                  className="font-serif"
                  style={{ fontSize: "1.5rem", color: "#e8634a" }}
                >
                  {value}
                </div>
                <div
                  style={{
                    fontSize: "0.7rem",
                    color: "rgba(224,240,240,0.48)",
                    marginTop: "2px",
                  }}
                >
                  {label}
                </div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>
    </section>
  );
}
