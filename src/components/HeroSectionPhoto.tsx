"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { Fragment, useRef } from "react";

const PHOTO_URL =
  "https://images.unsplash.com/photo-1489278353717-f64c6ee8a4d2?w=1200&q=85&fit=crop";

const EXPO = [0.16, 1, 0.3, 1] as const;

// ── Word-by-word blur reveal ─────────────────────────────────────────────────
function WordBlur({
  words,
  startDelay = 0,
  color,
  wrap = false,
}: {
  words: string[];
  startDelay?: number;
  color?: string;
  wrap?: boolean;
}) {
  const reduced = useReducedMotion();
  return (
    // Words are inline-blocks separated by ordinary spaces, so a long run
    // wraps like normal text. Without `wrap` the group is held on one line.
    <span style={{ whiteSpace: wrap ? "normal" : "nowrap" }}>
      {words.map((word, i) => (
        <Fragment key={`${word}-${i}`}>
          {i > 0 && " "}
          <motion.span
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
        </Fragment>
      ))}
    </span>
  );
}

export default function HeroSectionPhoto() {
  const t = useTranslations("HeroSectionPhoto");
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
        className="flex flex-col px-6 sm:px-10 lg:px-20 pt-16 pb-12 flex-shrink-0 w-full lg:w-[46%]"
        style={{ minHeight: "100dvh" }}
      >
        {/* Headline, word-blur stagger.
            A <p>, not an <h1>: the page already carries a descriptive h1
            ("Free Oral Cancer Risk Screener") and two h1s on one document is a
            hierarchy error. It says what the tool does rather than making a
            promise it cannot keep: the screener cannot find cancer, so it
            cannot "save your life". The line is long, so it wraps freely, and
            only the accent phrase is held together on one line. */}
        <p
          className="font-serif"
          style={{
            fontSize: "clamp(2.5rem, 4.4vw, 4.25rem)",
            letterSpacing: "-0.02em",
            lineHeight: 1.08,
            color: "var(--color-ink)",
            marginBottom: "2.5rem",
            marginTop: "1rem",
          }}
        >
          <WordBlur
            words={t("headlineLead").split(" ")}
            startDelay={0.15}
            color="var(--color-ink)"
            wrap
          />{" "}
          <WordBlur
            words={t("headlineAccent").split(" ")}
            startDelay={0.15 + t("headlineLead").split(" ").length * 0.09}
            color="#0d7377"
          />
        </p>

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
          {t("body")}
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
              {t("startScreening")}
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
              {t("learnSigns")}
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
            {t("disclaimer")}
          </p>
          <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
            <span style={{ display: "inline-block", width: "6px", height: "6px", borderRadius: "50%", backgroundColor: "#0d7377", flexShrink: 0 }} />
            <p style={{ fontSize: "11px", color: "var(--color-ink-soft)" }}>
              {t.rich("featured", {
                b: (chunks) => <span style={{ fontWeight: 600, color: "var(--color-ink)" }}>{chunks}</span>,
              })}
            </p>
          </div>
        </motion.div>
      </div>

      {/* ── Right photo panel ────────────────────────── */}
      <motion.div
        ref={photoRef}
        className="hidden lg:block relative overflow-hidden"
        style={{ minHeight: "100dvh", flex: 1 }}
        initial={reduced ? false : { clipPath: "inset(0 100% 0 0)" }}
        animate={{ clipPath: "inset(0 0% 0 0)" }}
        transition={{ duration: 1.0, delay: 0.1, ease: EXPO }}
      >
        <motion.div
          style={{ position: "absolute", inset: "-10% 0", y: reduced ? 0 : photoY }}
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          {/* Explicit intrinsic size so the browser reserves the box before
              the bytes land, and a priority hint because this is the largest
              element above the fold on every page load. */}
          <img
            src={PHOTO_URL}
            alt=""
            aria-hidden
            width={1200}
            height={800}
            fetchPriority="high"
            decoding="async"
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
