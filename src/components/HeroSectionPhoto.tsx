"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import Link from "next/link";
import { useRef } from "react";

const PHOTO_URL =
  "https://images.unsplash.com/photo-1489278353717-f64c6ee8a4d2?w=1200&q=85&fit=crop";

const EXPO = [0.16, 1, 0.3, 1] as const;

function LineReveal({
  children,
  delay,
  color,
}: {
  children: React.ReactNode;
  delay: number;
  color?: string;
}) {
  const reduced = useReducedMotion();
  return (
    <span style={{ display: "block", overflow: "hidden", lineHeight: 1.08 }}>
      <motion.span
        style={{ display: "block", color }}
        initial={reduced ? false : { y: "105%" }}
        animate={{ y: 0 }}
        transition={{ duration: 0.72, delay, ease: EXPO }}
      >
        {children}
      </motion.span>
    </span>
  );
}

export default function HeroSectionPhoto() {
  const reduced = useReducedMotion();
  const photoRef = useRef<HTMLDivElement>(null);

  const { scrollY } = useScroll();
  const photoY = useTransform(scrollY, [0, 600], ["0%", "-8%"]);

  const imgFilter = "blur(2px) brightness(1.15) saturate(0.85) contrast(1)";

  // fadeWidth: 60%, fadeStrength: 80% → mid-stop at 21%, opacity 0.80
  const fadeGradient =
    "linear-gradient(to right, #faf9f6 0%, rgba(250,249,246,0.80) 21%, transparent 60%)";

  return (
    <section
      className="min-h-[100dvh] flex flex-col lg:flex-row overflow-hidden"
      style={{ background: "#faf9f6" }}
    >
      {/* ── Left text panel (46% wide) ───────────────── */}
      <div
        className="flex flex-col justify-between px-6 sm:px-12 lg:px-20 pt-14 pb-10 flex-shrink-0"
        style={{ minHeight: "100dvh", width: "46%" }}
      >
        {/* Overline */}
        <motion.p
          style={{
            fontSize: "10px",
            fontWeight: 700,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "#9b9790",
          }}
          initial={reduced ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.05 }}
        >
          Free · Private · Evidence-based
        </motion.p>

        {/* Headline */}
        <div style={{ flex: 1, display: "flex", alignItems: "center", paddingBlock: "2.5rem" }}>
          <h1
            className="font-serif"
            style={{
              fontSize: "clamp(3.2rem, 6.8vw, 6.2rem)",
              letterSpacing: "-0.02em",
              color: "#2d2d2d",
            }}
          >
            <LineReveal delay={0.18}>2 minutes</LineReveal>
            <LineReveal delay={0.30}>
              could <span style={{ color: "#e8634a" }}>save</span>
            </LineReveal>
            <LineReveal delay={0.42} color="#0d7377">
              your life.
            </LineReveal>
          </h1>
        </div>

        {/* Bottom: rule + body + CTAs */}
        <div>
          <motion.div
            style={{
              height: "1px",
              background: "#e0ddd6",
              marginBottom: "1.4rem",
              transformOrigin: "left",
            }}
            initial={reduced ? false : { scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.7, delay: 0.6, ease: EXPO }}
          />

          <motion.p
            style={{
              fontSize: "0.97rem",
              lineHeight: "1.68",
              color: "#6b6b6b",
              maxWidth: "38ch",
              marginBottom: "1.5rem",
            }}
            initial={reduced ? false : { opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.72, ease: EXPO }}
          >
            Oral cancer is one of the most underdiagnosed cancers, largely
            because early symptoms look ordinary. OralCheck helps you
            understand your risk in minutes and points you toward care.
          </motion.p>

          <motion.div
            className="flex flex-wrap gap-3"
            initial={reduced ? false : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.84, ease: EXPO }}
          >
            <motion.div
              whileHover={reduced ? {} : { scale: 1.04, y: -2 }}
              whileTap={reduced ? {} : { scale: 0.97 }}
              transition={{ type: "spring", stiffness: 420, damping: 22 }}
            >
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
                  textDecoration: "none",
                  boxShadow: "0 4px 18px rgba(232,99,74,0.28)",
                }}
              >
                Start Screening →
              </Link>
            </motion.div>

            <motion.div
              whileHover={reduced ? {} : { scale: 1.03, y: -1 }}
              whileTap={reduced ? {} : { scale: 0.97 }}
              transition={{ type: "spring", stiffness: 420, damping: 22 }}
            >
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
                  textDecoration: "none",
                }}
              >
                Learn the signs
              </Link>
            </motion.div>
          </motion.div>

          <motion.p
            style={{ fontSize: "11px", color: "#aaa89f", marginTop: "1.2rem" }}
            initial={reduced ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 1.0 }}
          >
            Not a medical diagnosis. An educational awareness tool.
          </motion.p>
        </div>
      </div>

      {/* ── Right photo panel ────────────────────────── */}
      <motion.div
        ref={photoRef}
        className="relative overflow-hidden"
        style={{ minHeight: "50vh", flex: 1 }}
        initial={reduced ? false : { clipPath: "inset(0 100% 0 0)" }}
        animate={{ clipPath: "inset(0 0% 0 0)" }}
        transition={{ duration: 1.0, delay: 0.1, ease: EXPO }}
      >
        <motion.div
          style={{ position: "absolute", inset: "-10% 0", y: reduced ? 0 : photoY }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={PHOTO_URL}
            alt=""
            aria-hidden
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              objectPosition: "center 20%",
              filter: imgFilter,
              transform: "scale(1.04)",
            }}
          />
        </motion.div>

        {/* Left-edge fade into cream */}
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            background: fadeGradient,
            pointerEvents: "none",
          }}
        />

        {/* Bottom fade */}
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: "auto 0 0",
            height: "18%",
            background: "linear-gradient(to top, rgba(250,249,246,0.5) 0%, transparent 100%)",
            pointerEvents: "none",
          }}
        />
      </motion.div>
    </section>
  );
}
