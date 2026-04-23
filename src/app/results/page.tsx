"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { computeRisk, type RiskResult, type RiskTier } from "@/lib/riskEngine";
import type { Question } from "@/lib/questions";
import RiskGauge from "@/components/RiskGauge";
import { sendGAEvent } from "@next/third-parties/google";
import { track } from "@vercel/analytics";

// ─── Next-step content keyed by tier ─────────────────────────────────────────

const nextStepsByTier: Record<
  RiskTier,
  { title: string; desc: string; link?: { href: string; label: string } }[]
> = {
  low: [
    {
      title: "Keep up your annual dental visit",
      desc: "Oral cancer screening is already part of a routine cleaning — it takes 2 minutes and is included at no extra cost.",
    },
    {
      title: "Do a monthly self-exam",
      desc: "Two minutes with a mirror, once a month. You're looking for anything that hasn't gone away after 2 weeks.",
      link: { href: "/learn/self-exam", label: "See how →" },
    },
    {
      title: "Know the warning signs",
      desc: "Most oral cancers caught early are found by people who already knew what to look for.",
      link: { href: "/learn/signs", label: "See warning signs →" },
    },
  ],
  moderate: [
    {
      title: "Mention your risk factors at your next dental visit",
      desc: "Your dentist can pay closer attention during your screening if they know your history. It only takes a sentence.",
    },
    {
      title: "Know the warning signs — and act on them",
      desc: "Anything in your mouth or throat lasting more than 2 weeks deserves attention. Don't wait it out.",
      link: { href: "/learn/signs", label: "See warning signs →" },
    },
    {
      title: "Learn how to reduce your risk",
      desc: "Several of the factors that raised your score are modifiable. Even small changes lower risk over time.",
      link: { href: "/learn/prevention", label: "Prevention guide →" },
    },
  ],
  elevated: [
    {
      title: "Book a dental visit this month",
      desc: "Ask specifically for an oral cancer screening when you book. It's included in a routine cleaning and takes about 2 minutes.",
      link: { href: "/find-care", label: "Find care near you →" },
    },
    {
      title: "Know the warning signs — and act on them",
      desc: "A sore, patch, lump, or numbness lasting 2+ weeks should be seen by a dentist or doctor. Don't wait it out.",
      link: { href: "/learn/signs", label: "See warning signs →" },
    },
    {
      title: "Work on your modifiable risk factors",
      desc: "Your score includes factors you can change. Even modest reductions in tobacco, alcohol, or sun exposure add up.",
      link: { href: "/learn/prevention", label: "Prevention guide →" },
    },
  ],
  high: [
    {
      title: "Book a dental or medical visit this week",
      desc: "Not this month — this week. If you have a sore, patch, or lump that's been there 2+ weeks, mention it specifically when you call.",
      link: { href: "/find-care", label: "Find care near you →" },
    },
    {
      title: "Don't wait to see if it goes away",
      desc: "The most common reason oral cancers are caught late is that people wait. Most findings turn out to be benign — but you want to know either way.",
    },
    {
      title: "Know what the exam involves",
      desc: "An oral cancer screening is painless, takes 2 minutes, and can be done by your dentist or doctor.",
      link: { href: "/learn/self-exam", label: "What to expect →" },
    },
  ],
};

// ─── Contextual learn links keyed by risk factor category ────────────────────

const categoryLearnMap: Partial<
  Record<
    Question["category"],
    { href: string; tag: string; title: string; icon: string }
  >
> = {
  tobacco: {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "How to reduce tobacco risk",
    icon: "🛡️",
  },
  alcohol: {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "Alcohol, tobacco, and combined risk",
    icon: "🛡️",
  },
  hpv: {
    href: "/learn/hpv",
    tag: "Risk Factor",
    title: "HPV and oral cancer",
    icon: "🦠",
  },
  sun: {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "Protecting your lips from the sun",
    icon: "🛡️",
  },
  symptoms: {
    href: "/learn/signs",
    tag: "Symptoms",
    title: "Warning signs of oral cancer",
    icon: "⚠️",
  },
  family: {
    href: "/learn/facts",
    tag: "Facts",
    title: "Oral cancer facts & statistics",
    icon: "📊",
  },
  diet: {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "Diet and oral cancer risk",
    icon: "🛡️",
  },
  dental: {
    href: "/learn/self-exam",
    tag: "How-to",
    title: "How to do a 2-minute self-exam",
    icon: "🔎",
  },
  other: {
    href: "/learn/prevention",
    tag: "Prevention",
    title: "Reducing betel / paan risk",
    icon: "🛡️",
  },
};

// ─── Tier-specific primary CTA text ──────────────────────────────────────────

const primaryCTA: Record<RiskTier, string> = {
  low: "Find a dentist for your next screening →",
  moderate: "Find care near you →",
  elevated: "Book a dental visit →",
  high: "Find care — book this week →",
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function ResultsPage() {
  const [result, setResult] = useState<RiskResult | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [claudeSummary, setClaudeSummary] = useState<string>("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [copied, setCopied] = useState(false);

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
        track("Screener Completed", { risk_tier: risk.tier });
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
      // fall through — static summary shown as fallback
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
        setCopied(true);
        setTimeout(() => setCopied(false), 2500);
      } catch {}
    }
  };

  // ── Loading / empty states ────────────────────────────────────────────────

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

  // ── Derive contextual learn links from top factors ────────────────────────

  const learnLinks = result.factors
    .map((f) => categoryLearnMap[f.category])
    .filter((l): l is NonNullable<typeof l> => l !== undefined)
    .filter((l, i, arr) => arr.findIndex((x) => x.href === l.href) === i)
    .slice(0, 2);

  const nextSteps = nextStepsByTier[result.tier];

  // ── Main render ───────────────────────────────────────────────────────────

  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">

      {/* Urgent symptom banner */}
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

      {/* Risk card */}
      <div className="bg-white rounded-3xl border border-warm-dim p-6 sm:p-10">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
          <div className="md:col-span-2">
            <RiskGauge result={result} />
          </div>
          <div className="md:col-span-3 space-y-3">
            <h1 className="font-serif text-3xl sm:text-4xl text-ink leading-tight">
              {result.headline}
            </h1>

            {/* Summary with skeleton loading state */}
            {summaryLoading && !claudeSummary ? (
              <div className="space-y-2 pt-1">
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
                  <span className="text-xs text-ink-soft/70 font-medium">
                    Personalizing your summary…
                  </span>
                </div>
                <div className="h-3 bg-warm-dim rounded-full w-full animate-pulse" />
                <div className="h-3 bg-warm-dim rounded-full w-5/6 animate-pulse" />
                <div className="h-3 bg-warm-dim rounded-full w-4/6 animate-pulse" />
              </div>
            ) : (
              <p className="text-ink-soft leading-relaxed">
                {claudeSummary || result.summary}
                {summaryLoading && claudeSummary && (
                  <span className="inline-block w-1.5 h-4 bg-ink-soft/40 ml-0.5 animate-pulse rounded-sm align-middle" />
                )}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* What's driving your risk */}
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

      {/* Next steps */}
      <div className="mt-10">
        <h2 className="font-serif text-2xl text-ink mb-4">Your next steps</h2>
        <div className="space-y-3">
          {nextSteps.map((step, i) => (
            <div
              key={step.title}
              className="bg-white rounded-2xl border border-warm-dim p-5 flex gap-4 items-start"
            >
              <div className="flex-shrink-0 w-7 h-7 rounded-full bg-brand/10 text-brand text-xs font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-ink mb-1">{step.title}</div>
                <p className="text-sm text-ink-soft leading-relaxed">
                  {step.desc}
                </p>
                {step.link && (
                  <Link
                    href={step.link.href}
                    className="inline-block mt-2 text-sm font-semibold text-brand hover:underline"
                  >
                    {step.link.label}
                  </Link>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Contextual learn links */}
      {learnLinks.length > 0 && (
        <div className="mt-10">
          <h2 className="font-serif text-2xl text-ink mb-4">
            Related reading
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {learnLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="group bg-white rounded-2xl border border-warm-dim p-5 hover:border-brand/40 transition-all"
              >
                <div className="text-2xl mb-2" aria-hidden>
                  {link.icon}
                </div>
                <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-2 py-0.5 rounded-full mb-2">
                  {link.tag}
                </span>
                <div className="font-serif text-lg text-ink group-hover:text-brand transition-colors leading-snug">
                  {link.title}
                </div>
                <div className="mt-2 text-xs font-semibold text-brand">
                  Read →
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* CTAs */}
      <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
        <Link
          href="/find-care"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-4 rounded-2xl transition-colors text-center"
        >
          {primaryCTA[result.tier]}
        </Link>
        <button
          onClick={handleShare}
          className="bg-white hover:bg-warm-dim text-ink font-semibold px-6 py-4 rounded-2xl transition-colors border border-warm-dim text-center"
        >
          {copied ? "✓ Link copied!" : "Share with someone you care about"}
        </button>
      </div>

      <div className="mt-6 flex justify-center">
        <Link
          href="/screener"
          className="text-sm font-medium text-ink-soft hover:text-ink"
        >
          ↻ Retake the screener
        </Link>
      </div>

      {/* Disclaimer */}
      <div className="mt-12 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed">
        <strong className="text-ink">Disclaimer:</strong> OralCheck provides
        general health information only. It is not medical advice, diagnosis, or
        treatment. Scoring is an educational estimate informed by published risk
        factors — not a clinical algorithm. Always consult a qualified health
        provider for concerns about your health.
      </div>
    </div>
  );
}
