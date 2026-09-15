"use client";

import { useTranslations } from "next-intl";

export default function ProgressBar({
  current,
  total,
}: {
  current: number;
  total: number;
}) {
  const t = useTranslations("ScreenerPage");
  const pct = Math.round((current / total) * 100);
  return (
    <div className="space-y-2">
      <div className="flex justify-between text-xs font-mono text-ink-soft tabular-nums">
        <span>{t("questionOf", { current, total })}</span>
        <span>{pct}%</span>
      </div>
      <div
        role="progressbar"
        aria-valuenow={current}
        aria-valuemin={1}
        aria-valuemax={total}
        aria-valuetext={t("questionOf", { current, total })}
        className="h-1.5 bg-warm-dim rounded-full overflow-hidden"
      >
        {/* Width only. transition-all here also animated colour and the
            border-radius on every tick, for no visible benefit. */}
        <div
          className="h-full bg-brand transition-[width] duration-300 ease-out motion-reduce:transition-none"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
