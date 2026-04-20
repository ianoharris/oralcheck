"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { computeRisk, type RiskResult } from "@/lib/riskEngine";
import RiskGauge from "@/components/RiskGauge";
import { sendGAEvent } from "@next/third-parties/google";

export default function ResultsPage() {
  const [result, setResult] = useState<RiskResult | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [claudeSummary, setClaudeSummary] = useState<string>("");
  const [summaryLoading, setSummaryLoading] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("oralcheck:answers");
      if (raw) {
        const answers = JSON.parse(raw);
        const risk = computeRisk(answers);
        setResult(risk);
        fetchClaudeSummary(risk);
        sendGAEvent("event", "screener_completed", {
          risk_tier: risk.tier,
          risk_score: risk.score,
          has_urgent_symptom: risk.hasUrgentSymptom,
        });
      }
    } catch {}
    setLoaded(true);
  }, []);

  async function fetchClaudeSummary(risk: RiskResult) {
    setSummaryLoading(true);
    try {
      const res = await fetch("/api/summary", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tier: risk.tier,
          tierLabel: risk.tierLabel,
          factors: risk.factors.map((f) => ({
            label: f.label,
            answerLabel: f.answerLabel,
          })),
          hasUrgentSymptom: risk.hasUrgentSymptom,
        }),
      });
      if (!res.ok || !res.body) return;
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let text = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += decoder.decode(value, { stream: true });
        setClaudeSummary(text);
      }
    } catch {
      // fall through to static summary
    } finally {
      setSummaryLoading(false);
    }
  }

  const handleShare = async () => {
    if (!result) return;
    const url = typeof window !== "undefined" ? window.location.origin : "";
    const text = `I just used OralCheck to understand my oral cancer risk — 2 minutes could save your life. ${url}`;
    if (navigator.share) {
      try {
        await navigator.share({ title: "OralCheck", text, url });
      } catch {}
    } else if (navigator.clipboard) {
      try {
        await navigator.clipboard.writeText(text);
        alert("Share link copied to clipboard");
      } catch {}
    }
  };

  if (!loaded) {
    return (
      <div className="max-w-2xl mx-auto px-5 py-20 text-center text-ink-soft">
        Loading your results…
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto px-5 py-20 text-center">
        <h1 className="font-serif text-3xl text-ink mb-3">No results yet</h1>
        <p className="text-ink-soft mb-8">
          Complete the 2-minute screener to see your personalized risk summary.
        </p>
        <Link
          href="/screener"
          className="inline-block bg-accent hover:bg-accent-dark text-white font-semibold px-7 py-3.5 rounded-full transition-colors"
        >
          Start screener →
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      {result.hasUrgentSymptom && (
        <div className="mb-8 p-4 rounded-2xl bg-high/10 border border-high/30">
          <div className="flex gap-3 items-start">
            <div className="text-2xl">⚠️</div>
            <div className="text-sm text-ink leading-relaxed">
              <span className="font-semibold">
                You mentioned a symptom lasting 2+ weeks.
              </span>{" "}
              This isn&apos;t something to wait on. Please book a dental or
              medical visit this week.
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-3xl border border-warm-dim p-6 sm:p-10">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
          <div className="md:col-span-2">
            <RiskGauge result={result} />
          </div>
          <div className="md:col-span-3 space-y-3">
            <h1 className="font-serif text-3xl sm:text-4xl text-ink leading-tight">
              {result.headline}
            </h1>
            <p className="text-ink-soft leading-relaxed">
              {claudeSummary || result.summary}
              {summaryLoading && !claudeSummary && (
                <span className="inline-block w-1.5 h-4 bg-ink-soft/40 ml-0.5 animate-pulse rounded-sm align-middle" />
              )}
            </p>
          </div>
        </div>
      </div>

      {result.factors.length > 0 && (
        <div className="mt-10">
          <h2 className="font-serif text-2xl text-ink mb-4">
            What&apos;s driving your risk
          </h2>
          <div className="space-y-3">
            {result.factors.map((f) => (
              <div
                key={f.questionId}
                className="bg-white rounded-2xl border border-warm-dim p-5"
              >
                <div className="flex items-start gap-4">
                  <div className="text-2xl" aria-hidden>
                    {f.icon}
                  </div>
                  <div className="flex-1">
                    <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                      <div className="font-semibold text-ink">{f.label}</div>
                      <div className="text-sm text-ink-soft">
                        {f.answerLabel}
                      </div>
                    </div>
                    <p className="text-sm text-ink-soft mt-1.5 leading-relaxed">
                      {f.guidance}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/find-care"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-4 rounded-2xl transition-colors text-center"
        >
          Find care near you →
        </Link>
        <button
          onClick={handleShare}
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-4 rounded-2xl transition-colors border border-warm-dim text-center"
        >
          Share with someone you care about
        </button>
      </div>

      <div className="mt-8 flex justify-center">
        <Link
          href="/screener"
          className="text-sm font-medium text-ink-soft hover:text-ink"
        >
          ↻ Retake the screener
        </Link>
      </div>

      <div className="mt-12 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed">
        <strong className="text-ink">Disclaimer:</strong> OralCheck provides
        general health information only. It is not medical advice, diagnosis, or
        treatment. Scoring is an educational estimate informed by published
        risk factors — not a clinical algorithm. Always consult a qualified
        health provider for concerns about your health.
      </div>
    </div>
  );
}
