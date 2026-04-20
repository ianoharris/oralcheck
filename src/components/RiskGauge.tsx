import type { RiskResult } from "@/lib/riskEngine";

export default function RiskGauge({ result }: { result: RiskResult }) {
  const colorVar =
    result.tierColor === "low"
      ? "var(--color-low)"
      : result.tierColor === "mid"
        ? "var(--color-mid)"
        : "var(--color-high)";

  const pct = Math.min(100, Math.max(0, result.percent));
  const angle = -90 + (pct / 100) * 180;

  return (
    <div className="flex flex-col items-center">
      <svg
        viewBox="0 0 200 120"
        className="w-full max-w-sm"
        aria-label={`Risk gauge showing ${result.tierLabel}`}
      >
        <defs>
          <linearGradient id="gauge-grad" x1="0%" x2="100%" y1="0%" y2="0%">
            <stop offset="0%" stopColor="var(--color-low)" />
            <stop offset="50%" stopColor="var(--color-mid)" />
            <stop offset="100%" stopColor="var(--color-high)" />
          </linearGradient>
        </defs>

        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="var(--color-warm-dim)"
          strokeWidth="14"
          strokeLinecap="round"
        />
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="url(#gauge-grad)"
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray="251.3"
          strokeDashoffset={251.3 - (pct / 100) * 251.3}
          style={{ transition: "stroke-dashoffset 1s ease-out" }}
        />

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
          style={{ backgroundColor: colorVar }}
        >
          {result.tierLabel}
        </div>
        <div className="mt-3 font-mono text-xs text-ink-soft">
          Score: {result.score} / {result.maxScore}
        </div>
      </div>
    </div>
  );
}
