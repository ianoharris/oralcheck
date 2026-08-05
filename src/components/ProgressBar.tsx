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
      <div className="flex justify-between text-xs font-mono text-ink-soft">
        <span>{t("questionOf", { current, total })}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-1.5 bg-warm-dim rounded-full overflow-hidden">
        <div
          className="h-full bg-brand transition-all duration-300 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
