"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";
import { useInView, useReducedMotion } from "framer-motion";
import { SEER, SEER_DISPLAY } from "@/lib/seerStats";

const STATS = [
  { raw: SEER.newCasesPerYear, display: SEER_DISPLAY.newCases, labelKey: "cases" },
  { raw: Math.round(SEER.survival.localized), display: SEER_DISPLAY.survivalLocalized, labelKey: "survival" },
] as const;

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

function StatItem({ raw, display, label, suffix, active, live, liveLabel }: {
  raw: number; display: string; label: string; suffix?: string; active: boolean;
  live?: boolean; liveLabel?: string;
}) {
  const reduced = useReducedMotion();
  const count = useCountUp(raw, 1400, active && !reduced);

  const formatted = reduced || !active
    ? display
    : raw >= 1000 || suffix === "+"
      ? count.toLocaleString() + "+"
      : count + (suffix ?? (display.endsWith("%") ? "%" : ""));

  return (
    <div>
      <div className="font-mono text-3xl text-brand font-semibold tabular-nums">
        {formatted}
      </div>
      <div className="text-sm text-ink-soft mt-1 leading-snug">{label}</div>
      {live && (
        <div className="mt-2 inline-flex items-center gap-1.5 font-mono text-[11px] uppercase tracking-[0.12em] text-ink-soft">
          <span className="relative flex h-1.5 w-1.5" aria-hidden="true">
            <span className="absolute inline-flex h-full w-full rounded-full bg-brand opacity-60 motion-safe:animate-ping" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-brand" />
          </span>
          {liveLabel}
        </div>
      )}
    </div>
  );
}

export default function AnimatedStats({ reach }: { reach: { users: number; live: boolean } }) {
  const t = useTranslations("AnimatedStats");
  const ref = useRef<HTMLDivElement>(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });

  return (
    <section className="border-y border-warm-dim bg-warm-dim/60">
      <div
        ref={ref}
        className="max-w-6xl mx-auto px-5 py-10 grid grid-cols-1 sm:grid-cols-3 gap-6"
      >
        {STATS.map((s) => (
          <StatItem key={s.labelKey} {...s} label={t(s.labelKey)} active={inView} />
        ))}
        {/* GA's total is a floor (ad blockers, and a month of blocked hits in
            autumn 2026), so it always reads "N+". */}
        <StatItem
          raw={reach.users}
          display={reach.users.toLocaleString() + "+"}
          suffix="+"
          label={t("reach")}
          active={inView}
          live={reach.live}
          liveLabel={t("live")}
        />
      </div>
    </section>
  );
}
