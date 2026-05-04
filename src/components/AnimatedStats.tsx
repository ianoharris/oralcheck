"use client";

import { useEffect, useRef, useState } from "react";
import { useInView, useReducedMotion } from "framer-motion";

const stats = [
  { raw: 54000, display: "54,000+", label: "new US oral & oropharyngeal cancer cases each year" },
  { raw: 84,    display: "84%",     label: "five-year survival when caught early" },
  { raw: 2,     display: "2 min",   label: "is all a dental screening takes", suffix: " min" },
];

function useCountUp(target: number, duration = 1400, active: boolean) {
  const [value, setValue] = useState(0);
  const frame = useRef<number | null>(null);

  useEffect(() => {
    if (!active) return;
    const start = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      // ease-out-quart
      const eased = 1 - Math.pow(1 - progress, 4);
      setValue(Math.round(eased * target));
      if (progress < 1) frame.current = requestAnimationFrame(tick);
    };
    frame.current = requestAnimationFrame(tick);
    return () => { if (frame.current) cancelAnimationFrame(frame.current); };
  }, [active, target, duration]);

  return value;
}

function StatItem({ raw, display, label, suffix, active }: {
  raw: number; display: string; label: string; suffix?: string; active: boolean;
}) {
  const reduced = useReducedMotion();
  const count = useCountUp(raw, 1400, active && !reduced);

  const formatted = reduced || !active
    ? display
    : raw >= 1000
      ? count.toLocaleString() + "+"
      : count + (suffix ?? (display.endsWith("%") ? "%" : ""));

  return (
    <div>
      <div className="font-mono text-3xl text-brand font-semibold tabular-nums">
        {formatted}
      </div>
      <div className="text-sm text-ink-soft mt-1 leading-snug">{label}</div>
    </div>
  );
}

export default function AnimatedStats() {
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <section className="border-y border-warm-dim bg-white/60">
      <div
        ref={ref}
        className="max-w-6xl mx-auto px-5 py-10 grid grid-cols-1 sm:grid-cols-3 gap-6"
      >
        {stats.map((s) => (
          <StatItem key={s.label} {...s} active={inView} />
        ))}
      </div>
    </section>
  );
}
