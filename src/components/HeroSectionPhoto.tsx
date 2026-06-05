"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import Link from "next/link";
import { useRef } from "react";

const PHOTO_URL =
  "https://images.unsplash.com/photo-1489278353717-f64c6ee8a4d2?w=1200&q=85&fit=crop";

const EXPO = [0.16, 1, 0.3, 1] as const;

// ── Word-by-word blur reveal ─────────────────────────────────────────────────
function WordBlur({
  words,
  startDelay = 0,
  color,
}: {
  words: string[];
  startDelay?: number;
  color?: string;
}) {
  const reduced = useReducedMotion();
  return (
    // inline-flex + gap keeps words properly spaced regardless of display context
    <span style={{ display: "inline-flex", gap: "0.24em", flexWrap: "nowrap" }}>
      {words.map((word, i) => (
        <motion.span
          key={`${word}-${i}`}
          style={{ display: "inline-block", color }}
          initial={reduced ? false : { opacity: 0, y: 28, filter: "blur(10px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{
            duration: 0.65,
            delay: startDelay + i * 0.09,
            ease: EXPO,
          }}
        >
          {word}
        </motion.span>
      ))}
    </span>
  );
}

export default function HeroSectionPhoto() {
  const reduced = useReducedMotion();
  const photoRef = useRef<HTMLDivElement>(null);

  const { scrollY } = useScroll();
  const photoY = useTransform(scrollY, [0, 600], ["0%", "-8%"]);

  const imgFilter = "blur(2px) brightness(1.15) saturate(0.85) contrast(1)";

  return (
    <section
      className="min-h-[100dvh] flex flex-col lg:flex-row overflow-hidden"
      style={{ background: "var(--color-warm)" }}
    >
      {/* ── Left text panel ──────────────────────────── */}
      <div
        className="flex flex-col px-6 sm:px-12 lg:px-20 pt-16 pb-12 flex-shrink-0"
        style={{ minHeight: "100dvh", width: "46%" }}
      >
        {/* Overline */}
        <motion.p
          style={{
            fontSize: "10px",
            fontWeight: 700,
            letterSpacing: "0.22em",
            textTransform: "uppercase",
            color: "var(--color-ink-soft)",
            marginBottom: "2rem",
          }}
          initial={reduced ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.05 }}
        >
          Free · Private · Evidence-based
        </motion.p>

        {/* Headline — word-blur stagger */}
        <h1
          className="font-serif"
          style={{
            fontSize: "clamp(3.2rem, 6.8vw, 6.2rem)",
            letterSpacing: "-0.02em",
            lineHeight: 1.05,
            color: "var(--color-ink)",
            marginBottom: "2.5rem",
          }}
        >
          {/* Line 1: "2 minutes" */}
          <span style={{ display: "block" }}>
            <WordBlur words={["2", "minutes"]} startDelay={0.15} color="var(--color-ink)" />
          </span>
          {/* Line 2: "could save" — mixed colors, flex row keeps spacing */}
          <span style={{ display: "flex", gap: "0.24em" }}>
            <WordBlur words={["could"]} startDelay={0.32} color="var(--color-ink)" />
            <WordBlur words={["save"]} startDelay={0.41} color="#e8634a" />
          </span>
          {/* Line 3: "your life." */}
          <span style={{ display: "block" }}>
            <WordBlur words={["your", "life."]} startDelay={0.52} color="#0d7377" />
          </span>
        </h1>

        {/* Rule */}
        <motion.div
          style={{
            height: "1px",
            background: "var(--color-warm-dim)",
            marginBottom: "1.4rem",
            transformOrigin: "left",
          }}
          initial={reduced ? false : { scaleX: 0 }}
          animate={{ scaleX: 1 }}
          transition={{ duration: 0.7, delay: 0.7, ease: EXPO }}
        />

        {/* Body */}
        <motion.p
          style={{
            fontSize: "0.97rem",
            lineHeight: "1.68",
            color: "var(--color-ink-soft)",
            maxWidth: "38ch",
            marginBottom: "1.5rem",
          }}
          initial={reduced ? false : { opacity: 0, y: 14 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, delay: 0.82, ease: EXPO }}
        >
          Oral cancer is one of the most underdiagnosed cancers, largely
          because early symptoms look ordinary. OralCheck helps you
          understand your risk in minutes and points you toward care.
        </motion.p>

        {/* CTAs */}
        <motion.div
          className="flex flex-wrap gap-3"
          initial={reduced ? false : { opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.94, ease: EXPO }}
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
                border: "1px solid var(--color-warm-dim)",
                color: "var(--color-ink)",
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

        <motion.div
          style={{ marginTop: "1.2rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}
          initial={reduced ? false : { opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5, delay: 1.1 }}
        >
          <p style={{ fontSize: "11px", color: "var(--color-ink-soft)" }}>
            Not a medical diagnosis. An educational awareness tool.
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ display: "inline-block", width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#0d7377", flexShrink: 0 }} />
            <p style={{ fontSize: "11px", color: "var(--color-ink-soft)" }}>
              Featured in{" "}
              <span style={{ fontWeight: 600, color: "var(--color-ink)" }}>The Drill</span>
              {" · Wisconsin Dental Association"}
            </p>
          </div>
        </motion.div>
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

        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            background: "var(--hero-photo-fade)",
            pointerEvents: "none",
          }}
        />
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: "auto 0 0",
            height: "18%",
            background: "var(--hero-photo-bottom)",
            pointerEvents: "none",
          }}
        />
      </motion.div>
    </section>
  );
}
