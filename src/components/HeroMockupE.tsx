"use client";

import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion";
import Link from "next/link";
import { useRef, useState } from "react";

const PHOTO_URL =
  "https://images.unsplash.com/photo-1489278353717-f64c6ee8a4d2?w=900&q=85&fit=crop";

const EXPO = [0.16, 1, 0.3, 1] as const;

// ── Defaults ────────────────────────────────────────────────────────────────
const DEFAULTS = {
  blur: 6,
  brightness: 1,
  saturation: 1,
  contrast: 1,
  leftWidth: 52,      // % of viewport width for text panel
  fadeWidth: 28,      // % of photo panel where the cream fade ends
  fadeStrength: 18,   // opacity% of the mid-stop in the fade gradient
};

// ── Masked line reveal ───────────────────────────────────────────────────────
function LineReveal({ children, delay, color }: { children: React.ReactNode; delay: number; color?: string }) {
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

// ── Control panel ────────────────────────────────────────────────────────────
type Controls = typeof DEFAULTS;

function Slider({
  label, k, controls, setControls, min, max, step, unit = "",
}: {
  label: string;
  k: keyof Controls;
  controls: Controls;
  setControls: (c: Controls) => void;
  min: number; max: number; step: number; unit?: string;
}) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 3 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10 }}>
        <span style={{ color: "#999" }}>{label}</span>
        <span style={{ color: "#ccc", fontVariantNumeric: "tabular-nums" }}>
          {controls[k]}{unit}
        </span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={controls[k] as number}
        onChange={e => setControls({ ...controls, [k]: parseFloat(e.target.value) })}
        style={{ width: "100%", accentColor: "#e8634a", cursor: "pointer" }}
      />
    </label>
  );
}

function ControlPanel({ controls, setControls }: { controls: Controls; setControls: (c: Controls) => void }) {
  const [open, setOpen] = useState(true);

  const code = [
    `blur: ${controls.blur}px`,
    `brightness: ${controls.brightness}`,
    `saturation: ${controls.saturation}`,
    `contrast: ${controls.contrast}`,
    `leftWidth: ${controls.leftWidth}%`,
    `fadeWidth: ${controls.fadeWidth}%`,
    `fadeStrength: ${controls.fadeStrength}%`,
  ].join(" | ");

  return (
    <div
      style={{
        position: "fixed",
        bottom: 20,
        right: 20,
        zIndex: 9999,
        background: "rgba(18,18,18,0.94)",
        backdropFilter: "blur(12px)",
        borderRadius: 12,
        border: "1px solid rgba(255,255,255,0.08)",
        fontFamily: "ui-monospace, monospace",
        width: open ? 260 : "auto",
        overflow: "hidden",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      }}
    >
      {/* Header */}
      <button
        onClick={() => setOpen(o => !o)}
        style={{
          width: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "10px 14px",
          background: "none",
          border: "none",
          cursor: "pointer",
          color: "#fff",
          fontSize: 11,
          fontFamily: "inherit",
          fontWeight: 600,
          letterSpacing: "0.08em",
        }}
      >
        <span>⚙ CONTROLS</span>
        <span style={{ opacity: 0.5 }}>{open ? "↓" : "↑"}</span>
      </button>

      {open && (
        <div style={{ padding: "0 14px 14px", display: "flex", flexDirection: "column", gap: 12 }}>
          {/* Photo adjustments */}
          <div style={{ fontSize: 9, color: "#666", letterSpacing: "0.12em", textTransform: "uppercase", paddingTop: 2 }}>Photo</div>
          <Slider label="Blur" k="blur" min={0} max={24} step={0.5} unit="px" controls={controls} setControls={setControls} />
          <Slider label="Brightness" k="brightness" min={0.4} max={1.6} step={0.05} controls={controls} setControls={setControls} />
          <Slider label="Saturation" k="saturation" min={0} max={2} step={0.05} controls={controls} setControls={setControls} />
          <Slider label="Contrast" k="contrast" min={0.5} max={1.5} step={0.05} controls={controls} setControls={setControls} />

          {/* Layout adjustments */}
          <div style={{ fontSize: 9, color: "#666", letterSpacing: "0.12em", textTransform: "uppercase", paddingTop: 4 }}>Layout</div>
          <Slider label="Photo starts at" k="leftWidth" min={30} max={75} step={1} unit="%" controls={controls} setControls={setControls} />
          <Slider label="Fade width" k="fadeWidth" min={0} max={60} step={1} unit="%" controls={controls} setControls={setControls} />
          <Slider label="Fade strength" k="fadeStrength" min={0} max={80} step={1} unit="%" controls={controls} setControls={setControls} />

          {/* Reset + copy */}
          <div style={{ display: "flex", gap: 6, paddingTop: 4 }}>
            <button
              onClick={() => setControls(DEFAULTS)}
              style={{
                flex: 1, padding: "6px 0", background: "rgba(255,255,255,0.07)",
                border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6,
                color: "#aaa", fontSize: 10, cursor: "pointer", fontFamily: "inherit",
              }}
            >
              Reset
            </button>
            <button
              onClick={() => navigator.clipboard?.writeText(code)}
              style={{
                flex: 2, padding: "6px 0", background: "rgba(232,99,74,0.2)",
                border: "1px solid rgba(232,99,74,0.3)", borderRadius: 6,
                color: "#e8634a", fontSize: 10, cursor: "pointer", fontFamily: "inherit",
              }}
            >
              Copy values
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ── Hero ─────────────────────────────────────────────────────────────────────
export default function HeroMockupE() {
  const reduced = useReducedMotion();
  const photoRef = useRef<HTMLDivElement>(null);
  const [controls, setControls] = useState<Controls>(DEFAULTS);

  const { scrollY } = useScroll();
  const photoY = useTransform(scrollY, [0, 600], ["0%", "-8%"]);

  const imgFilter = [
    `blur(${controls.blur}px)`,
    `brightness(${controls.brightness})`,
    `saturate(${controls.saturation})`,
    `contrast(${controls.contrast})`,
  ].join(" ");

  const fadeGradient = `linear-gradient(to right, #faf9f6 0%, rgba(250,249,246,${controls.fadeStrength / 100}) ${Math.round(controls.fadeWidth * 0.35)}%, transparent ${controls.fadeWidth}%)`;

  return (
    <>
      <section
        className="min-h-[100dvh] flex flex-col lg:flex-row overflow-hidden"
        style={{ background: "#faf9f6" }}
      >
        {/* ── Left panel ───────────────────────────────── */}
        <div
          className="flex flex-col justify-between px-6 sm:px-10 lg:px-14 pt-14 pb-10 flex-shrink-0"
          style={{ minHeight: "100dvh", width: `${controls.leftWidth}%` }}
        >
          <motion.p
            style={{ fontSize: "10px", fontWeight: 700, letterSpacing: "0.22em", textTransform: "uppercase", color: "#9b9790" }}
            initial={reduced ? false : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.05 }}
          >
            Free · Private · Evidence-based
          </motion.p>

          <div style={{ flex: 1, display: "flex", alignItems: "center", paddingBlock: "2.5rem" }}>
            <h1
              className="font-serif"
              style={{ fontSize: "clamp(3.2rem, 6.8vw, 6.2rem)", letterSpacing: "-0.02em", color: "#2d2d2d" }}
            >
              <LineReveal delay={0.18}>2 minutes</LineReveal>
              <LineReveal delay={0.30}>could <span style={{ color: "#e8634a" }}>save</span></LineReveal>
              <LineReveal delay={0.42} color="#0d7377">your life.</LineReveal>
            </h1>
          </div>

          <div>
            <motion.div
              style={{ height: "1px", background: "#e0ddd6", marginBottom: "1.4rem", transformOrigin: "left" }}
              initial={reduced ? false : { scaleX: 0 }}
              animate={{ scaleX: 1 }}
              transition={{ duration: 0.7, delay: 0.6, ease: EXPO }}
            />

            <motion.p
              style={{ fontSize: "0.97rem", lineHeight: "1.68", color: "#6b6b6b", maxWidth: "38ch", marginBottom: "1.5rem" }}
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
                <Link href="/screener" style={{ backgroundColor: "#e8634a", color: "#fff", padding: "0.85rem 1.75rem", borderRadius: "9999px", fontWeight: 600, fontSize: "0.875rem", display: "inline-flex", alignItems: "center", gap: "6px", textDecoration: "none", boxShadow: "0 4px 18px rgba(232,99,74,0.28)" }}>
                  Start Screening →
                </Link>
              </motion.div>
              <motion.div
                whileHover={reduced ? {} : { scale: 1.03, y: -1 }}
                whileTap={reduced ? {} : { scale: 0.97 }}
                transition={{ type: "spring", stiffness: 420, damping: 22 }}
              >
                <Link href="/learn" style={{ border: "1px solid #d6d3cc", color: "#2d2d2d", padding: "0.85rem 1.75rem", borderRadius: "9999px", fontWeight: 600, fontSize: "0.875rem", display: "inline-flex", alignItems: "center", textDecoration: "none" }}>
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

        {/* ── Right panel ──────────────────────────────── */}
        <motion.div
          ref={photoRef}
          className="relative overflow-hidden"
          style={{ minHeight: "50vh", flex: 1 }}
          initial={reduced ? false : { clipPath: "inset(0 100% 0 0)" }}
          animate={{ clipPath: "inset(0 0% 0 0)" }}
          transition={{ duration: 1.0, delay: 0.1, ease: EXPO }}
        >
          <motion.div style={{ position: "absolute", inset: "-10% 0", y: reduced ? 0 : photoY }}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={PHOTO_URL}
              alt="A smiling person"
              style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 20%", filter: imgFilter, transform: "scale(1.04)" }}
            />
          </motion.div>

          {/* Fade */}
          <div aria-hidden style={{ position: "absolute", inset: 0, background: fadeGradient, pointerEvents: "none" }} />

          {/* Bottom fade */}
          <div aria-hidden style={{ position: "absolute", inset: "auto 0 0", height: "18%", background: "linear-gradient(to top, rgba(250,249,246,0.5) 0%, transparent 100%)", pointerEvents: "none" }} />
        </motion.div>
      </section>

      <ControlPanel controls={controls} setControls={setControls} />
    </>
  );
}
