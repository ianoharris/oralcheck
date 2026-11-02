"use client";

import { useTranslations } from "next-intl";
import { TIER_BOUNDS, type RiskResult, type RiskTier } from "@/lib/riskEngine";

const ARC = 251.3; // length of the semicircle path below
const TIERS: RiskTier[] = ["low", "moderate", "elevated", "high"];
const SEG = ARC / TIERS.length;
const GAP = 2; // visible break between tier segments

const TINT: Record<RiskTier, string> = {
  low: "var(--color-low)",
  moderate: "var(--color-mid)",
  elevated: "var(--color-elevated)",
  high: "var(--color-high)",
};
const STRONG: Record<RiskTier, string> = {
  low: "var(--color-low-strong)",
  moderate: "var(--color-mid-strong)",
  elevated: "var(--color-elevated-strong)",
  high: "var(--color-high-strong)",
};

/**
 * Where the needle sits, 0 to 1. Each tier owns an equal quarter of the dial
 * and the score is placed within its tier's range, so the needle always points
 * into the segment whose colour matches the label under it. An urgent symptom
 * forces the High tier whatever the score, so it sits well into that segment.
 */
function needlePosition(result: RiskResult): number {
  const i = TIERS.indexOf(result.tier);
  const [lo, hiBound] = TIER_BOUNDS[result.tier];
  const hi = result.tier === "high" ? result.maxScore : hiBound;
  const within = result.hasUrgentSymptom
    ? 0.85
    : Math.min(1, Math.max(0, (result.score - lo) / Math.max(1, hi - lo)));
  // Keep the needle off the exact segment edges so it never reads as the
  // neighbouring tier.
  return (i + 0.08 + within * 0.84) / TIERS.length;
}

export default function RiskGauge({ result }: { result: RiskResult }) {
  const t = useTranslations("RiskGauge");
  const pos = needlePosition(result);
  const active = TIERS.indexOf(result.tier);
  const angle = -90 + pos * 180;

  return (
    <div className="flex flex-col items-center">
      <svg
        viewBox="0 0 200 120"
        className="w-full max-w-[15rem] md:max-w-sm"
        aria-label={t("ariaLabel", { tier: result.tierLabel })}
      >
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          // The track used to be warm-dim, which is also the colour of the
          // results card the gauge sits on, so it vanished and a low score
          // drew as a lone blob beside the needle. A faint ink stroke reads
          // as a track on the card in both themes.
          stroke="var(--color-ink)"
          strokeOpacity="0.1"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* One segment per tier, filled up to the active one. A single
            green-to-coral gradient used to run by percentage, not by tier. */}
        {TIERS.map((tier, i) => {
          if (i > active) return null;
          const start = i * SEG + (i === 0 ? 0 : GAP / 2);
          const end = i === active ? pos * ARC : (i + 1) * SEG - GAP / 2;
          const len = Math.max(0, end - start);
          return (
            <path
              key={tier}
              d="M 20 100 A 80 80 0 0 1 180 100"
              fill="none"
              stroke={TINT[tier]}
              strokeWidth="14"
              strokeLinecap="butt"
              strokeDasharray={`${len} ${ARC}`}
              strokeDashoffset={-start}
              style={{ transition: "stroke-dasharray 1s ease-out" }}
            />
          );
        })}

        <g
          transform={`rotate(${angle} 100 100)`}
          style={{ transition: "transform 1s ease-out" }}
        >
          <line
            x1="100"
            y1="100"
            x2="100"
            y2="32"
            stroke="var(--color-ink)"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx="100" cy="100" r="8" fill="var(--color-ink)" />
          <circle cx="100" cy="100" r="3" fill="var(--color-warm)" />
        </g>
      </svg>

      <div className="text-center mt-4">
        <div
          className="inline-block px-4 py-1.5 rounded-full text-sm font-semibold text-white"
          style={{ backgroundColor: STRONG[result.tier] }}
        >
          {result.tierLabel}
        </div>
        <div className="mt-3 font-mono text-xs text-ink-soft">
          {t("score", { score: result.score, maxScore: result.maxScore })}
        </div>
      </div>
    </div>
  );
}
