"use client";

import { useRef, useCallback } from "react";
import {
  motion,
  useReducedMotion,
  useMotionValue,
  useSpring,
  useTransform,
  useMotionTemplate,
} from "framer-motion";

export default function HeroHolographicCard() {
  const reduced = useReducedMotion();
  const ref = useRef<HTMLDivElement>(null);

  // Raw mouse position (0–1) relative to card
  const mx = useMotionValue(0.5);
  const my = useMotionValue(0.5);
  const hov = useMotionValue(0);

  // Smoothed springs
  const smx = useSpring(mx, { stiffness: 140, damping: 18 });
  const smy = useSpring(my, { stiffness: 140, damping: 18 });
  const sHov = useSpring(hov, { stiffness: 60, damping: 14 });

  const onMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!ref.current) return;
      const r = ref.current.getBoundingClientRect();
      mx.set((e.clientX - r.left) / r.width);
      my.set((e.clientY - r.top) / r.height);
    },
    [mx, my]
  );
  const onEnter = useCallback(() => hov.set(1), [hov]);
  const onLeave = useCallback(() => {
    hov.set(0);
    mx.set(0.5);
    my.set(0.5);
  }, [hov, mx, my]);

  // 3-D tilt — subtle
  const rotX = useTransform(smy, [0, 1], [7, -7]);
  const rotY = useTransform(smx, [0, 1], [-7, 7]);
  const scale = useTransform(sHov, [0, 1], [1, 1.025]);

  // Specular highlight — sharp white blob that chases the cursor
  const specX = useTransform(smx, [0, 1], [0, 100]);
  const specY = useTransform(smy, [0, 1], [0, 100]);
  const specBg = useMotionTemplate`radial-gradient(circle at ${specX}% ${specY}%, rgba(255,255,255,0.65) 0%, rgba(255,255,255,0.12) 32%, transparent 62%)`;
  const specOpacity = useTransform(sHov, [0, 1], [0, 1]);

  // Iridescent layer — large 200% gradient shifts position with mouse
  // so you see broad colour washes, not tight banded circles
  const iriPosX = useTransform(smx, [0, 1], [0, 100]);
  const iriPosY = useTransform(smy, [0, 1], [0, 100]);
  const iriPos = useMotionTemplate`${iriPosX}% ${iriPosY}%`;
  const iriOpacity = useTransform(sHov, [0, 1], [0.0, 0.09]);

  // Edge glow — soft radial from the lit side
  const edgeBg = useMotionTemplate`radial-gradient(ellipse at ${specX}% ${specY}%, rgba(13,115,119,0.18) 0%, transparent 70%)`;

  if (reduced) {
    return (
      <div className="aspect-square rounded-3xl bg-gradient-to-br from-brand-soft via-warm-dim to-warm-dim flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-6 rounded-2xl border border-brand/20" />
        <div className="text-center px-6">
          <div className="text-6xl mb-3">🦷</div>
          <div className="font-serif text-2xl text-brand">Know early.</div>
          <div className="font-serif text-2xl text-accent">Act early.</div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ perspective: "1200px" }}>
      {/* Float wrapper — keeps the original float animation */}
      <motion.div
        animate={{ y: [0, -10, 0] }}
        transition={{ duration: 4.5, repeat: Infinity, ease: "easeInOut" as const }}
      >
        {/* Tilt wrapper */}
        <motion.div
          ref={ref}
          onMouseMove={onMove}
          onMouseEnter={onEnter}
          onMouseLeave={onLeave}
          style={{ rotateX: rotX, rotateY: rotY, scale }}
          className="relative aspect-square rounded-3xl cursor-default select-none"
        >
          {/* ── Layers (back to front) ── */}

          {/* 1. Base gradient */}
          <div className="absolute inset-0 rounded-3xl bg-gradient-to-br from-brand-soft via-warm-dim to-warm-dim overflow-hidden">

            {/* 2. Noise texture via SVG feTurbulence */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" aria-hidden>
              <filter id="holo-noise" x="0%" y="0%" width="100%" height="100%">
                <feTurbulence
                  type="fractalNoise"
                  baseFrequency="0.68"
                  numOctaves="4"
                  stitchTiles="stitch"
                />
                <feColorMatrix type="saturate" values="0" />
              </filter>
              <rect
                width="100%"
                height="100%"
                filter="url(#holo-noise)"
                style={{ opacity: 0.09, mixBlendMode: "overlay" }}
              />
            </svg>

            {/* 3. Iridescent sheen — 200% gradient shifts position so colours
                   sweep broadly rather than appearing as tight bands */}
            <motion.div
              aria-hidden
              className="absolute inset-0 pointer-events-none rounded-3xl"
              style={{
                backgroundImage:
                  "linear-gradient(135deg, hsl(0,90%,68%), hsl(45,90%,68%), hsl(100,90%,68%), hsl(160,90%,68%), hsl(210,90%,68%), hsl(270,90%,68%), hsl(320,90%,68%), hsl(360,90%,68%))",
                backgroundSize: "200% 200%",
                backgroundPosition: iriPos,
                opacity: iriOpacity,
                mixBlendMode: "screen",
              }}
            />

            {/* 4. Edge glow */}
            <motion.div
              aria-hidden
              className="absolute inset-0 pointer-events-none rounded-3xl"
              style={{ background: edgeBg }}
            />

            {/* 5. Specular highlight */}
            <motion.div
              aria-hidden
              className="absolute inset-0 pointer-events-none rounded-3xl"
              style={{
                background: specBg,
                opacity: specOpacity,
                mixBlendMode: "overlay",
              }}
            />

            {/* Inner border */}
            <div className="absolute inset-6 rounded-2xl border border-brand/20" />
          </div>

          {/* Content — sits above all layers */}
          <div className="relative h-full flex items-center justify-center text-center px-6">
            <div>
              <div className="text-6xl mb-3">🦷</div>
              <div className="font-serif text-2xl text-brand">Know early.</div>
              <div className="font-serif text-2xl text-accent">Act early.</div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
}
