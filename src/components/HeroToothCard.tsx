"use client";

import { useEffect } from "react";
import { motion, useReducedMotion, useMotionValue, useSpring, useTransform } from "framer-motion";

function ClinicalToothSVG() {
  return (
    <svg viewBox="0 0 200 285" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-36 h-auto">
      {/* ── Crown ── */}
      <path
        d="M32 108 C27 93 22 68 27 48 C32 28 44 12 59 12
           C67 12 73 19 80 19 C87 19 93 12 101 12
           C116 12 128 28 133 48 C138 68 133 93 128 108
           C119 124 103 132 80 132 C57 132 41 124 32 108Z"
        fill="#d6edf0"
        stroke="#0d7377"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      {/* Crown grooves */}
      <path d="M80 17 L80 130" stroke="#0d7377" strokeWidth="1.5" strokeLinecap="round" opacity="0.18" />
      <path d="M29 70 C52 66 108 66 131 70" stroke="#0d7377" strokeWidth="1.5" strokeLinecap="round" opacity="0.18" />

      {/* Pulp chamber */}
      <path
        d="M59 46 C59 38 67 33 80 33 C93 33 101 38 101 46
           L99 94 C98 105 90 111 80 111
           C70 111 62 105 61 94Z"
        stroke="#0d7377"
        strokeWidth="1.5"
        strokeLinejoin="round"
        fill="none"
        opacity="0.28"
      />

      {/* ── Left root ── */}
      <path
        d="M50 132 L42 200 C40 214 45 225 53 226
           C61 227 66 217 67 204 L71 132"
        fill="#d6edf0"
        stroke="#0d7377"
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
      {/* ── Right root ── */}
      <path
        d="M110 132 L118 200 C120 214 115 225 107 226
           C99 227 94 217 93 204 L89 132"
        fill="#d6edf0"
        stroke="#0d7377"
        strokeWidth="2.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />

      {/* Root canals */}
      <path d="M60 111 L54 218" stroke="#0d7377" strokeWidth="1" strokeLinecap="round" opacity="0.18" />
      <path d="M100 111 L106 218" stroke="#0d7377" strokeWidth="1" strokeLinecap="round" opacity="0.18" />
    </svg>
  );
}

export default function HeroToothCard() {
  const reduced = useReducedMotion();

  const rawX = useMotionValue(0.5);
  const rawY = useMotionValue(0.5);
  const smoothX = useSpring(rawX, { stiffness: 22, damping: 16 });
  const smoothY = useSpring(rawY, { stiffness: 22, damping: 16 });

  useEffect(() => {
    if (reduced) return;
    const onMove = (e: MouseEvent) => {
      rawX.set(e.clientX / window.innerWidth);
      rawY.set(e.clientY / window.innerHeight);
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, [rawX, rawY, reduced]);

  // Primary glow follows mouse
  const g1x = useTransform(smoothX, [0, 1], [-55, 55]);
  const g1y = useTransform(smoothY, [0, 1], [-55, 55]);
  // Secondary glow moves opposite for depth
  const g2x = useTransform(smoothX, [0, 1], [45, -45]);
  const g2y = useTransform(smoothY, [0, 1], [35, -35]);

  return (
    <motion.div
      initial={reduced ? false : { opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" as const, delay: 0.3 }}
      className="relative"
    >
      {/* Mouse-tracking glows */}
      {!reduced && (
        <>
          <motion.div
            aria-hidden
            style={{ x: g1x, y: g1y }}
            className="absolute -inset-8 bg-brand/25 rounded-3xl blur-3xl pointer-events-none"
          />
          <motion.div
            aria-hidden
            style={{ x: g2x, y: g2y }}
            className="absolute -inset-8 bg-accent/15 rounded-3xl blur-3xl pointer-events-none"
          />
        </>
      )}

      {/* Frosted card */}
      <div className="relative aspect-square rounded-3xl bg-white/70 backdrop-blur-lg border border-white/60 shadow-xl overflow-hidden flex flex-col items-center justify-center gap-6 px-8">
        <ClinicalToothSVG />

        {/* Clinical footer bar */}
        <div className="absolute bottom-0 inset-x-0 border-t border-brand/10 px-5 py-3 flex items-center justify-between bg-white/40 backdrop-blur-sm">
          <span className="text-[10px] font-mono text-ink-soft uppercase tracking-widest">Oral examination</span>
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
            <span className="text-[10px] font-mono text-brand">Active</span>
          </span>
        </div>
      </div>
    </motion.div>
  );
}
