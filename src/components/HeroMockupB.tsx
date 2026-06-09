"use client";

import { motion, useReducedMotion } from "framer-motion";
import Link from "next/link";

/*
  DIRECTION B: "Editorial Portrait" — warm dark field, photo-backed feel
  Color strategy: Committed. A warm amber-bronze darkness dominates the right
  half, evoking the warmth of skin under examination lighting. The left panel
  pulls toward the composition anchor. Text lives at bottom-left, editorial.

  In production: replace the CSS portrait simulation with a real stock image
  (e.g., a close-up of a confident person with open mouth, warm studio lighting).
  The gradient overlay layer handles legibility regardless of photo choice.
*/

function WarmField() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none" aria-hidden>
      {/* Dark warm base */}
      <div
        className="absolute inset-0"
        style={{ background: "#1a1008" }}
      />

      {/* Simulated warm portrait — right 60% of frame */}
      {/* Replace this entire block with <Image> + overlay in production */}
      <div
        className="absolute"
        style={{
          right: 0,
          top: 0,
          bottom: 0,
          width: "65%",
          background:
            "radial-gradient(ellipse at 52% 42%, #c47a35 0%, #8b4b1a 38%, #3d1e08 72%, transparent 90%)",
          opacity: 0.72,
        }}
      />

      {/* Subtle portrait highlight — suggests face/neck under exam light */}
      <div
        className="absolute"
        style={{
          right: "14%",
          top: "18%",
          width: "clamp(180px, 28vw, 380px)",
          aspectRatio: "3 / 4",
          borderRadius: "50% 50% 46% 46% / 38% 38% 62% 62%",
          background:
            "radial-gradient(ellipse at 48% 32%, rgba(220,160,80,0.55) 0%, rgba(160,90,30,0.25) 55%, transparent 80%)",
        }}
      />

      {/* Grain texture — editorial authenticity */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.82' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`,
          backgroundSize: "180px 180px",
          opacity: 0.055,
        }}
      />

      {/* Left gradient: ensures text legibility */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(105deg, rgba(15,8,2,0.95) 0%, rgba(15,8,2,0.8) 28%, rgba(15,8,2,0.3) 58%, transparent 78%)",
        }}
      />

      {/* Bottom anchor gradient */}
      <div
        className="absolute inset-x-0 bottom-0"
        style={{
          height: "50%",
          background: "linear-gradient(to top, rgba(10,5,0,0.88) 0%, transparent 100%)",
        }}
      />

      {/* Subtle teal grade over the top — connects to brand */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse at 15% 10%, rgba(13,115,119,0.12) 0%, transparent 55%)",
        }}
      />
    </div>
  );
}

const f = (delay: number) => ({
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] as const },
});

export default function HeroMockupB() {
  const reduced = useReducedMotion();

  return (
    <section className="relative min-h-[100dvh] flex items-end overflow-hidden">
      <WarmField />

      {/* Content — anchored bottom-left, editorial */}
      <div className="relative z-10 max-w-6xl mx-auto px-6 lg:px-12 w-full pb-16 pt-32">
        <div style={{ maxWidth: "600px" }}>

          {/* Eyebrow */}
          <motion.p
            style={{
              fontSize: "10px",
              fontWeight: 600,
              letterSpacing: "0.22em",
              textTransform: "uppercase",
              color: "rgba(200,140,70,0.85)",
              marginBottom: "1.4rem",
            }}
            {...(reduced ? {} : f(0.12))}
          >
            Free · Private · Evidence-based
          </motion.p>

          {/* Headline — mixed color for tonal drama */}
          <motion.h1
            className="font-serif leading-[1.02]"
            style={{
              fontSize: "clamp(2.8rem, 5.5vw, 5rem)",
              marginBottom: "1.5rem",
            }}
            {...(reduced ? {} : f(0.24))}
          >
            <span style={{ color: "rgba(242,234,220,0.97)" }}>2 minutes</span>
            <br />
            <span style={{ color: "rgba(242,234,220,0.97)" }}>could </span>
            <span style={{ color: "#e8a060" }}>save</span>
            <br />
            <span style={{ color: "#e8a060" }}>your life.</span>
          </motion.h1>

          {/* Body */}
          <motion.p
            style={{
              fontSize: "0.97rem",
              lineHeight: "1.7",
              color: "rgba(210,185,150,0.68)",
              maxWidth: "44ch",
              marginBottom: "2rem",
            }}
            {...(reduced ? {} : f(0.38))}
          >
            Oral cancer is one of the most underdiagnosed cancers, largely
            because early symptoms look ordinary. OralCheck helps you
            understand your risk in minutes and points you toward care.
          </motion.p>

          {/* CTAs */}
          <motion.div
            className="flex flex-wrap gap-3 mb-10"
            {...(reduced ? {} : f(0.5))}
          >
            <Link
              href="/screener"
              className="inline-flex items-center gap-2 font-semibold transition-all duration-200"
              style={{
                backgroundColor: "#0d7377",
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
                border: "1px solid rgba(200,160,90,0.3)",
                color: "rgba(230,200,155,0.82)",
                padding: "0.85rem 1.75rem",
                borderRadius: "9999px",
                fontSize: "0.9rem",
              }}
            >
              Learn the signs
            </Link>
          </motion.div>

          {/* Credit / attribution */}
          <motion.div
            className="flex items-center gap-2"
            {...(reduced ? {} : f(0.62))}
          >
            <span
              style={{
                display: "inline-block",
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: "#0d7377",
                flexShrink: 0,
              }}
            />
            <p style={{ fontSize: "11px", color: "rgba(200,170,120,0.5)" }}>
              Featured in{" "}
              <span style={{ fontWeight: 600, color: "rgba(200,170,120,0.75)" }}>
                The Drill
              </span>{" "}
              · Wisconsin Dental Association
            </p>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
