"use client";

import {
  motion,
  useMotionValue,
  useTransform,
  useSpring,
  useReducedMotion,
} from "framer-motion";
import { useRef, useCallback } from "react";

/*
  DIRECTION C: "Signal" — warm cream field, character-blur headline,
  SVG scan ring that draws itself in, magnetic CTA buttons, mouse parallax.
  Aesthetic reference: 21st.dev — clean but alive.
*/

/* ── Character-level blur reveal ─────────────────────────────────────────── */
function BlurIn({
  text,
  delay = 0,
  className = "",
}: {
  text: string;
  delay?: number;
  className?: string;
}) {
  return (
    <span aria-label={text} role="text" className={className}>
      {text.split("").map((ch, i) => (
        <motion.span
          key={i}
          className="inline-block"
          initial={{ opacity: 0, y: 14, filter: "blur(10px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          transition={{
            duration: 0.38,
            delay: delay + i * 0.022,
            ease: [0.16, 1, 0.3, 1],
          }}
        >
          {ch === " " ? " " : ch}
        </motion.span>
      ))}
    </span>
  );
}

/* ── Magnetic CTA ─────────────────────────────────────────────────────────── */
function MagneticBtn({
  href,
  variant = "ghost",
  children,
}: {
  href: string;
  variant?: "filled" | "ghost";
  children: React.ReactNode;
}) {
  const ref = useRef<HTMLAnchorElement>(null);
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const x = useSpring(rawX, { stiffness: 320, damping: 24 });
  const y = useSpring(rawY, { stiffness: 320, damping: 24 });

  const onMove = (e: React.MouseEvent) => {
    if (!ref.current) return;
    const r = ref.current.getBoundingClientRect();
    rawX.set((e.clientX - r.left - r.width / 2) * 0.38);
    rawY.set((e.clientY - r.top - r.height / 2) * 0.38);
  };

  const onLeave = () => {
    rawX.set(0);
    rawY.set(0);
  };

  const base: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    gap: "6px",
    padding: "0.85rem 1.85rem",
    borderRadius: "9999px",
    fontWeight: 600,
    fontSize: "0.88rem",
    cursor: "pointer",
    textDecoration: "none",
    userSelect: "none",
  };

  const styles: React.CSSProperties =
    variant === "filled"
      ? { ...base, backgroundColor: "#e8634a", color: "#fff" }
      : {
          ...base,
          backgroundColor: "transparent",
          border: "1.5px solid #ddd8cf",
          color: "#2d2d2d",
        };

  return (
    <motion.a
      ref={ref}
      href={href}
      style={{ ...styles, x, y }}
      onMouseMove={onMove}
      onMouseLeave={onLeave}
      whileHover={
        variant === "filled"
          ? { backgroundColor: "#c84d35" }
          : { borderColor: "#b5b0a8", backgroundColor: "#f5f3ee" }
      }
      whileTap={{ scale: 0.96 }}
      transition={{ duration: 0.15 }}
    >
      {children}
    </motion.a>
  );
}

/* ── SVG scan ring ────────────────────────────────────────────────────────── */
function ScanRing({
  tx,
  ty,
  reduced,
}: {
  tx: ReturnType<typeof useSpring>;
  ty: ReturnType<typeof useSpring>;
  reduced: boolean | null;
}) {
  const round = (n: number) => Math.round(n * 1000) / 1000;
  const ticks = Array.from({ length: 24 }, (_, i) => {
    const a = (i * 15 * Math.PI) / 180;
    const isMajor = i % 6 === 0;
    const r0 = isMajor ? 174 : 178;
    const r1 = 186;
    return {
      x1: round(200 + r0 * Math.cos(a)),
      y1: round(200 + r0 * Math.sin(a)),
      x2: round(200 + r1 * Math.cos(a)),
      y2: round(200 + r1 * Math.sin(a)),
      isMajor,
    };
  });

  return (
    <motion.div
      className="absolute pointer-events-none"
      style={
        reduced
          ? { right: "0px", top: "60px", width: "540px", height: "540px" }
          : {
              right: "0px",
              top: "60px",
              width: "540px",
              height: "540px",
              x: tx,
              y: ty,
            }
      }
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox="0 0 400 400"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outermost faint ring */}
        <circle
          cx="200"
          cy="200"
          r="195"
          stroke="#0d7377"
          strokeWidth="0.5"
          strokeOpacity="0.1"
        />

        {/* Primary ring — draws in */}
        <motion.circle
          cx="200"
          cy="200"
          r="186"
          stroke="#0d7377"
          strokeWidth="1"
          strokeOpacity="0.3"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.6, delay: 0.4, ease: [0.16, 1, 0.3, 1] }}
        />

        {/* Inner ring */}
        <motion.circle
          cx="200"
          cy="200"
          r="155"
          stroke="#0d7377"
          strokeWidth="0.75"
          strokeOpacity="0.12"
          initial={{ pathLength: 0 }}
          animate={{ pathLength: 1 }}
          transition={{ duration: 1.2, delay: 0.7, ease: [0.16, 1, 0.3, 1] }}
        />

        {/* Coral accent arc — top-right quadrant */}
        <motion.path
          d="M 200 14 A 186 186 0 0 1 385 215"
          stroke="#e8634a"
          strokeWidth="2.5"
          strokeLinecap="round"
          fill="none"
          initial={{ pathLength: 0, opacity: 0 }}
          animate={{ pathLength: 1, opacity: 0.65 }}
          transition={{ duration: 0.9, delay: 1.2, ease: [0.16, 1, 0.3, 1] }}
        />

        {/* Tick marks */}
        {ticks.map((t, i) => (
          <motion.line
            key={i}
            x1={t.x1}
            y1={t.y1}
            x2={t.x2}
            y2={t.y2}
            stroke="#0d7377"
            strokeWidth={t.isMajor ? 1.5 : 0.75}
            strokeOpacity={t.isMajor ? 0.35 : 0.15}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.4 + i * 0.03, duration: 0.2 }}
          />
        ))}

        {/* Center dot — springs in */}
        <motion.circle
          cx="200"
          cy="200"
          r="8"
          fill="#0d7377"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            delay: 1.5,
            type: "spring",
            stiffness: 500,
            damping: 20,
          }}
          style={{ transformOrigin: "200px 200px" }}
        />

        {/* Breathing pulse ring */}
        <motion.circle
          cx="200"
          cy="200"
          r="8"
          fill="none"
          stroke="#0d7377"
          strokeWidth="1.5"
          animate={
            reduced
              ? {}
              : { scale: [1, 3.5, 1], opacity: [0.7, 0, 0.7] }
          }
          transition={{
            duration: 2.8,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2,
          }}
          style={{ transformOrigin: "200px 200px" }}
        />

        {/* Central stat — fades in after ring completes */}
        <motion.text
          x="200"
          y="192"
          textAnchor="middle"
          fill="#0d7377"
          fontSize="52"
          fontFamily="var(--font-dm-serif), Georgia, serif"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.9 }}
          transition={{ delay: 1.7, duration: 0.6 }}
        >
          84%
        </motion.text>
        <motion.text
          x="200"
          y="220"
          textAnchor="middle"
          fill="#6b6b6b"
          fontSize="11"
          fontFamily="var(--font-source-sans), system-ui, sans-serif"
          letterSpacing="0.04em"
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.8 }}
          transition={{ delay: 1.9, duration: 0.5 }}
        >
          survive when caught early
        </motion.text>
      </svg>
    </motion.div>
  );
}

/* ── Main hero ────────────────────────────────────────────────────────────── */
export default function HeroMockupC() {
  const reduced = useReducedMotion();

  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const smoothX = useSpring(rawX, { stiffness: 55, damping: 18 });
  const smoothY = useSpring(rawY, { stiffness: 55, damping: 18 });

  // Parallax layers for SVG ring (opposite direction = depth)
  const ringX = useTransform(smoothX, [-0.5, 0.5], [14, -14]);
  const ringY = useTransform(smoothY, [-0.5, 0.5], [10, -10]);

  // Ambient glow that drifts with mouse
  const glowX = useTransform(smoothX, [-0.5, 0.5], [-60, 60]);
  const glowY = useTransform(smoothY, [-0.5, 0.5], [-40, 40]);

  const onMouseMove = useCallback(
    (e: React.MouseEvent<HTMLElement>) => {
      if (reduced) return;
      const r = e.currentTarget.getBoundingClientRect();
      rawX.set((e.clientX - r.left) / r.width - 0.5);
      rawY.set((e.clientY - r.top) / r.height - 0.5);
    },
    [reduced, rawX, rawY]
  );

  return (
    <section
      className="relative min-h-[100dvh] flex items-center overflow-hidden"
      style={{ backgroundColor: "#faf9f6" }}
      onMouseMove={onMouseMove}
    >
      {/* Ambient glow blob that drifts with mouse */}
      {!reduced && (
        <motion.div
          className="absolute pointer-events-none"
          aria-hidden
          style={{
            width: "65%",
            height: "65%",
            borderRadius: "50%",
            background: "radial-gradient(ellipse, rgba(13,115,119,0.06) 0%, transparent 70%)",
            left: "28%",
            top: "15%",
            x: glowX,
            y: glowY,
          }}
        />
      )}

      {/* SVG scan ring — upper right, parallax */}
      <ScanRing tx={ringX} ty={ringY} reduced={reduced} />

      {/* Thin left accent bar */}
      <motion.div
        className="absolute left-0 top-0 bottom-0 w-[3px]"
        style={{ backgroundColor: "#e8634a", transformOrigin: "top" }}
        initial={{ scaleY: 0 }}
        animate={{ scaleY: 1 }}
        transition={{ duration: 1, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-6xl mx-auto px-8 lg:px-14 w-full py-32">
        <div style={{ maxWidth: "640px" }}>

          {/* Overline: line draws then text appears */}
          <div className="flex items-center gap-3 mb-9" aria-hidden={false}>
            <motion.div
              style={{
                height: "1px",
                backgroundColor: "#e8634a",
                transformOrigin: "left",
              }}
              initial={{ scaleX: 0, opacity: 1 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.45, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            >
              <div style={{ width: "28px" }} />
            </motion.div>
            <motion.span
              style={{
                fontSize: "10px",
                fontWeight: 600,
                letterSpacing: "0.2em",
                textTransform: "uppercase" as const,
                color: "#9b9b9b",
              }}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.4, delay: 0.55 }}
            >
              Free · Private · Evidence-based
            </motion.span>
          </div>

          {/* Headline — character blur reveal */}
          <h1
            className="font-serif leading-[1.03]"
            style={{
              fontSize: "clamp(3rem, 5.8vw, 5.25rem)",
              marginBottom: "1.75rem",
              color: "#2d2d2d",
            }}
          >
            {reduced ? (
              <>
                2 minutes could{" "}
                <span style={{ color: "#e8634a" }}>save your life.</span>
              </>
            ) : (
              <>
                <BlurIn text="2 minutes could" delay={0.3} />
                <br />
                <BlurIn
                  text="save your life."
                  delay={0.68}
                  className="text-accent"
                />
              </>
            )}
          </h1>

          {/* Body */}
          <motion.p
            style={{
              fontSize: "1rem",
              lineHeight: "1.75",
              color: "#6b6b6b",
              maxWidth: "46ch",
              marginBottom: "2.5rem",
            }}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 1.15, ease: [0.16, 1, 0.3, 1] }}
          >
            Oral cancer is one of the most underdiagnosed cancers, largely
            because early symptoms look ordinary. OralCheck helps you understand
            your risk in minutes and points you toward care.
          </motion.p>

          {/* CTAs */}
          <motion.div
            className="flex flex-wrap gap-3 mb-12"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 1.35, ease: [0.16, 1, 0.3, 1] }}
          >
            <MagneticBtn href="/screener" variant="filled">
              Start Screening →
            </MagneticBtn>
            <MagneticBtn href="/learn" variant="ghost">
              Learn the signs
            </MagneticBtn>
          </motion.div>

          {/* Stats row */}
          <motion.div
            className="flex flex-wrap gap-8"
            style={{ borderTop: "1px solid #eeebe4", paddingTop: "1.5rem" }}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.4, delay: 1.55 }}
          >
            {[
              { value: "54,000", label: "new US cases yearly" },
              { value: "1 death", label: "every 50 minutes" },
              { value: "2 min", label: "to complete the screener" },
            ].map(({ value, label }, i) => (
              <motion.div
                key={value}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.65 + i * 0.1, duration: 0.38 }}
              >
                <div
                  className="font-serif"
                  style={{ fontSize: "1.35rem", color: "#0d7377" }}
                >
                  {value}
                </div>
                <div
                  style={{ fontSize: "0.68rem", color: "#b0aba3", marginTop: "2px" }}
                >
                  {label}
                </div>
              </motion.div>
            ))}
          </motion.div>

          {/* Attribution */}
          <motion.div
            className="flex items-center gap-2 mt-5"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.95, duration: 0.4 }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: "#0d7377",
                display: "inline-block",
                flexShrink: 0,
              }}
            />
            <p style={{ fontSize: "11px", color: "#c0bbb3" }}>
              Featured in{" "}
              <span style={{ fontWeight: 600, color: "#8a8580" }}>
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
