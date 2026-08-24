"use client";

import { useEffect, useState } from "react";
import Icon, { type IconName } from "@/components/Icon";
import { useLocale, useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import { computeRisk, type RiskResult, type RiskTier } from "@/lib/riskEngine";
import type { Question } from "@/lib/questions";
import RiskGauge from "@/components/RiskGauge";
import Modal from "@/components/Modal";
import { sendGAEvent } from "@next/third-parties/google";
import { track } from "@vercel/analytics";

// href/icon are locale-independent; title/tag/desc come from messages.ResultsPage.
const nextStepsHref: Record<RiskTier, (string | undefined)[]> = {
  low: [undefined, "/learn/self-exam", "/learn/signs"],
  moderate: [undefined, "/learn/signs", "/learn/prevention"],
  elevated: ["/find-care", "/learn/signs", "/learn/prevention"],
  high: ["/find-care", undefined, "/learn/self-exam"],
};

const categoryLearnMeta: Partial<Record<Question["category"], { href: string; icon: IconName }>> = {
  tobacco: { href: "/learn/prevention", icon: "prevention" },
  alcohol: { href: "/learn/prevention", icon: "prevention" },
  hpv: { href: "/learn/hpv", icon: "virus" },
  sun: { href: "/learn/prevention", icon: "prevention" },
  symptoms: { href: "/learn/signs", icon: "signs" },
  family: { href: "/learn/facts", icon: "facts" },
  diet: { href: "/learn/prevention", icon: "prevention" },
  dental: { href: "/learn/self-exam", icon: "selfExam" },
  other: { href: "/learn/prevention", icon: "prevention" },
};

export default function ResultsPage() {
  const t = useTranslations("ResultsPage");
  const locale = useLocale();
  const [result, setResult] = useState<RiskResult | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [claudeSummary, setClaudeSummary] = useState<string>("");
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [email, setEmail] = useState("");
  const [emailStatus, setEmailStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [emailError, setEmailError] = useState("");
  const [showAllFactors, setShowAllFactors] = useState(false);
  const [emailModalOpen, setEmailModalOpen] = useState(false);

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("oralcheck:answers");
      if (raw) {
        const answers = JSON.parse(raw);
        const risk = computeRisk(answers, locale);
        setResult(risk);
        fetchClaudeSummary(risk);
        // Count a completion once per finished screener, not once per view of
        // this page. Results renders from sessionStorage, so a refresh, a back
        // navigation, or reopening the tab used to re-fire this: completions
        // outran starts and the completion rate read over 100%.
        let alreadyCounted = false;
        try {
          alreadyCounted = sessionStorage.getItem("oralcheck:completionCounted") === "1";
        } catch {}
        if (!alreadyCounted) {
          try {
            sessionStorage.setItem("oralcheck:completionCounted", "1");
          } catch {}
          sendGAEvent("event", "screener_completed", {
            risk_tier: risk.tier,
            risk_score: risk.score,
            has_urgent_symptom: risk.hasUrgentSymptom,
          });
          track("Screener Completed", { risk_tier: risk.tier });
        }
      }
    } catch {}
    setLoaded(true);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Offer the emailed copy as a dialog rather than a block at the foot of the
  // page, which most people never scrolled to. It waits for the personalised
  // summary to finish so it doesn't cover the result the moment it appears,
  // and it fires at most once per session so a retake isn't nagged.
  useEffect(() => {
    if (!result || summaryLoading || emailStatus === "sent") return;
    let prompted = false;
    try {
      prompted = sessionStorage.getItem("oralcheck:emailPrompted") === "1";
    } catch {}
    if (prompted) return;

    const timer = setTimeout(() => {
      try {
        sessionStorage.setItem("oralcheck:emailPrompted", "1");
      } catch {}
      setEmailModalOpen(true);
      sendGAEvent("event", "email_prompt_shown", { risk_tier: result.tier });
    }, 1200);
    return () => clearTimeout(timer);
  }, [result, summaryLoading, emailStatus]);

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
          locale,
        }),
      });
      if (!res.ok || !res.body) return;
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let text = "";
      // Drain the stream into a buffer and commit it once, rather than setting
      // state per chunk. Streaming still avoids the request timeout on a slow
      // generation, but the reader sees the skeleton resolve into finished
      // prose instead of watching it type itself out.
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        text += decoder.decode(value, { stream: true });
      }
      setClaudeSummary(text);
    } catch {
      // fall through — static summary shown as fallback
    } finally {
      setSummaryLoading(false);
    }
  }

  const handleShare = async () => {
    if (!result) return;
    const url = typeof window !== "undefined" ? window.location.origin : "";
    const text = t("shareText", { url });
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

  const handleEmailResult = async (e: React.FormEvent) => {
    e.preventDefault();
    if (emailStatus === "sending") return;
    setEmailStatus("sending");
    setEmailError("");
    let answers: Record<string, string> = {};
    try {
      answers = JSON.parse(sessionStorage.getItem("oralcheck:answers") || "{}");
    } catch {}
    try {
      const res = await fetch("/api/email-result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, answers, locale }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || t("emailGenericError"));
      }
      setEmailStatus("sent");
    } catch (err) {
      setEmailStatus("error");
      setEmailError(err instanceof Error ? err.message : t("emailGenericError"));
    }
  };

  // ── Loading / empty states ────────────────────────────────────────────────

  if (!loaded) {
    return (
      <div className="max-w-2xl mx-auto px-5 py-20 text-center text-ink-soft">
        {t("loading")}
      </div>
    );
  }

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto px-5 py-20 text-center">
        <h1 className="font-serif text-3xl text-ink mb-3">{t("noResultsTitle")}</h1>
        <p className="text-ink-soft mb-8">{t("noResultsDesc")}</p>
        <Link
          href="/screener"
          className="inline-block bg-accent hover:bg-accent-dark text-white font-semibold px-7 py-3.5 rounded-full transition-colors"
        >
          {t("startScreener")}
        </Link>
      </div>
    );
  }

  // ── Derive contextual learn links from top factors ────────────────────────

  type NextStep = { title: string; desc: string; linkLabel?: string };
  const nextSteps: NextStep[] = t.raw(`nextSteps.${result.tier}`);
  const hrefs = nextStepsHref[result.tier];

  type CategoryLearn = { tag: string; title: string };
  const categoryLearn: Partial<Record<Question["category"], CategoryLearn>> = t.raw("categoryLearn");

  const learnLinks = result.factors
    .map((f) => {
      const meta = categoryLearnMeta[f.category];
      const copy = categoryLearn[f.category];
      if (!meta || !copy) return undefined;
      return { href: meta.href, icon: meta.icon, tag: copy.tag, title: copy.title };
    })
    .filter((l): l is NonNullable<typeof l> => l !== undefined)
    .filter((l, i, arr) => arr.findIndex((x) => x.href === l.href) === i)
    .slice(0, 2);

  const primaryCTA: Record<RiskTier, string> = t.raw("primaryCTA");

  // factors arrive sorted by weight, so the first few are the ones worth explaining
  const PRIMARY_COUNT = 4;
  const primaryFactors = result.factors.slice(0, PRIMARY_COUNT);
  const minorFactors = result.factors.slice(PRIMARY_COUNT);

  // Rendered in two places (inline block and dialog) from one definition, so
  // the two can't drift apart. `stacked` is for the narrow dialog column.
  const renderEmailForm = (stacked: boolean) => (
    <>
      <form
        onSubmit={handleEmailResult}
        className={stacked ? "flex flex-col gap-2.5" : "flex flex-col sm:flex-row gap-3"}
      >
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder={t("emailPlaceholder")}
          aria-label={t("emailLabel")}
          className="flex-1 bg-warm px-5 py-3 rounded-xl border border-warm-dim focus:outline-none focus:ring-2 focus:ring-brand text-ink placeholder:text-ink-soft"
        />
        <button
          type="submit"
          disabled={emailStatus === "sending" || !email.trim()}
          className="bg-brand hover:bg-brand-dark disabled:opacity-60 text-white font-semibold px-6 py-3 rounded-xl transition-colors whitespace-nowrap"
        >
          {emailStatus === "sending" ? t("emailSending") : t("emailMe")}
        </button>
      </form>
      {emailStatus === "error" && (
        <p className="mt-2 text-sm text-accent">{emailError}</p>
      )}
    </>
  );

  // ── Main render ───────────────────────────────────────────────────────────

  return (
    <div className="max-w-5xl mx-auto px-5 py-10 sm:py-16">

      {/* Urgent symptom banner */}
      {result.hasUrgentSymptom && (
        <div className="mb-8 p-4 rounded-2xl bg-high/10 border border-high/30">
          <div className="flex gap-3 items-start">
            <div className="text-high shrink-0" aria-hidden><Icon name="signs" size={24} weight="fill" /></div>
            <div className="text-sm text-ink leading-relaxed">
              <span className="font-semibold">{t("urgentBannerBold")}</span>{" "}
              {t("urgentBannerRest")}
            </div>
          </div>
        </div>
      )}

      {/* Risk card */}
      <div className="bg-warm-dim rounded-3xl border border-warm-dim p-6 sm:p-10">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-8 items-center">
          <div className="md:col-span-2">
            <RiskGauge result={result} />
          </div>
          <div className="md:col-span-3 space-y-3">
            <h1 className="font-serif text-3xl sm:text-4xl text-ink leading-tight">
              {result.headline}
            </h1>

            {/* Shown on the reassuring tiers only, and only when no urgent
                symptom was reported.

                Dr. Yeshwant Rawal (Professor of Surgical Sciences and Director
                of Diagnostic Sciences at Marquette, President of the American
                Board of Oral & Maxillofacial Pathology) reviewed the
                methodology on 2026-08-24 and made the point this exists to
                answer: roughly a quarter of oral cancers occur in people with
                none of the conventional contributing factors. Consistent with
                the literature on never-smoker, never-drinker OSCC, which puts
                it at 25-30%.

                A score built only from risk factors therefore cannot reassure,
                and "Your current risk profile looks low" on its own invites
                exactly the wrong conclusion from someone who has a symptom. */}
            {(result.tier === "low" || result.tier === "moderate") &&
              !result.hasUrgentSymptom && (
                <div className="rounded-2xl border border-accent/30 bg-accent/5 px-5 py-4">
                  <p className="text-sm font-semibold text-accent mb-1">
                    {t("noFactorCaveatLabel")}
                  </p>
                  <p className="text-sm text-ink leading-relaxed">
                    {t("noFactorCaveatBody")}
                  </p>
                </div>
              )}

            {/* Summary with skeleton loading state */}
            {summaryLoading && !claudeSummary ? (
              <div className="space-y-2 pt-1">
                <div className="flex items-center gap-1.5 mb-3">
                  <span className="inline-block w-1.5 h-1.5 rounded-full bg-brand animate-pulse" />
                  <span className="text-xs text-ink-soft/70 font-medium">
                    {t("personalizing")}
                  </span>
                </div>
                <div className="h-3 bg-warm-dim rounded-full w-full animate-pulse" />
                <div className="h-3 bg-warm-dim rounded-full w-5/6 animate-pulse" />
                <div className="h-3 bg-warm-dim rounded-full w-4/6 animate-pulse" />
              </div>
            ) : (
              <p className="text-ink-soft leading-relaxed">
                {claudeSummary || result.summary}
              </p>
            )}

            {/* The scoring rationale lived only in the footer. On a health tool
                the "how was this calculated" answer belongs next to the number
                it explains, not three scrolls away. */}
            <Link
              href="/methods"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-brand hover:text-brand-dark transition-colors pt-1"
            >
              <Icon name="overview" size={15} />
              {t("howScored")}
            </Link>
          </div>
        </div>
      </div>

      {/* What's driving your risk.
          Only the factors that actually move the score get a full write-up.
          Listing all ten with a paragraph each read as padding and buried the
          ones that matter, so the tail collapses behind a toggle. */}
      {result.factors.length > 0 && (
        <div className="mt-10">
          <h2 className="font-serif text-2xl text-ink mb-4">{t("drivingHeading")}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {primaryFactors.map((f) => (
              <div
                key={f.questionId}
                className="bg-warm-dim rounded-2xl border border-warm-dim p-5"
              >
                <div className="flex items-start gap-4">
                  <div className="text-brand shrink-0" aria-hidden>
                    <Icon name={f.icon} size={26} />
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

          {minorFactors.length > 0 && (
            <div className="mt-3">
              <button
                onClick={() => setShowAllFactors((v) => !v)}
                aria-expanded={showAllFactors}
                className="w-full text-left bg-warm-dim/60 rounded-2xl border border-warm-dim px-5 py-3.5 hover:border-brand/40 transition-colors"
              >
                <span className="text-sm font-semibold text-ink">
                  {showAllFactors ? t("hideOthers") : t("alsoContributing")}
                </span>
                <span className="text-sm text-ink-soft">
                  {" "}
                  {minorFactors.map((f) => f.label).join(" · ")}
                </span>
              </button>
              {showAllFactors && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                  {minorFactors.map((f) => (
                    <div
                      key={f.questionId}
                      className="bg-warm-dim rounded-2xl border border-warm-dim p-5"
                    >
                      <div className="flex items-start gap-4">
                        <div className="text-brand shrink-0" aria-hidden><Icon name={f.icon} size={26} /></div>
                        <div className="flex-1">
                          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                            <div className="font-semibold text-ink">{f.label}</div>
                            <div className="text-sm text-ink-soft">{f.answerLabel}</div>
                          </div>
                          <p className="text-sm text-ink-soft mt-1.5 leading-relaxed">
                            {f.guidance}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Next steps */}
      <div className="mt-10">
        <h2 className="font-serif text-2xl text-ink mb-4">{t("nextStepsHeading")}</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {nextSteps.map((step, i) => (
            <div
              key={step.title}
              className="bg-warm-dim rounded-2xl border border-warm-dim p-5 flex gap-4 items-start"
            >
              <div className="flex-shrink-0 w-7 h-7 rounded-full bg-brand/10 text-brand text-xs font-bold flex items-center justify-center mt-0.5">
                {i + 1}
              </div>
              <div className="flex-1">
                <div className="font-semibold text-ink mb-1">{step.title}</div>
                <p className="text-sm text-ink-soft leading-relaxed">
                  {step.desc}
                </p>
                {step.linkLabel && hrefs[i] && (
                  <Link
                    href={hrefs[i]!}
                    className="inline-block mt-2 text-sm font-semibold text-brand hover:underline"
                  >
                    {step.linkLabel}
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
            {t("relatedReadingHeading")}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {learnLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="group bg-warm-dim rounded-2xl border border-warm-dim p-5 hover:border-brand/40 transition-all"
              >
                <div className="text-brand mb-2" aria-hidden>
                  <Icon name={link.icon} size={26} />
                </div>
                <span className="inline-block text-xs font-semibold uppercase tracking-wider text-brand bg-brand-soft px-2 py-0.5 rounded-full mb-2">
                  {link.tag}
                </span>
                <div className="font-serif text-lg text-ink group-hover:text-brand transition-colors leading-snug">
                  {link.title}
                </div>
                <div className="mt-2 text-xs font-semibold text-brand">
                  {t("read")}
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* CTAs */}
      <div className="mt-10 grid grid-cols-1 sm:grid-cols-2 gap-4">
        {/* The single most important number the tool does not currently
            measure: of the people who get a result, how many go looking for
            care? Everything else is upstream of this. Tagged with the tier so
            it can be read as a rate per tier, not just a total. */}
        <Link
          href="/find-care"
          onClick={() =>
            sendGAEvent("event", "find_care_click", {
              risk_tier: result.tier,
              risk_score: result.score,
              source: "results_primary_cta",
            })
          }
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-4 rounded-2xl transition-colors text-center"
        >
          {primaryCTA[result.tier]}
        </Link>
        <button
          onClick={handleShare}
          className="bg-warm-dim hover:bg-warm text-ink font-semibold px-6 py-4 rounded-2xl transition-colors border border-warm-dim text-center"
        >
          {copied ? <span className="inline-flex items-center justify-center gap-1.5"><Icon name="check" size={16} weight="bold" />{t("linkCopied")}</span> : t("shareCta")}
        </button>
      </div>

      {/* Email a copy. Stays on the page as well as in the dialog, so anyone
          who dismissed the prompt can still find it. */}
      <div className="mt-8 p-6 rounded-2xl bg-brand-soft border border-brand/15">
        {emailStatus === "sent" ? (
          <div className="text-center">
            <div className="font-serif text-xl text-ink mb-1">{t("emailSentTitle")}</div>
            <p className="text-sm text-ink-soft">{t("emailSentDesc")}</p>
          </div>
        ) : (
          <>
            <div className="font-serif text-xl text-ink mb-1">{t("emailKeepCopy")}</div>
            <p className="text-sm text-ink-soft mb-4 leading-relaxed">{t("emailBody")}</p>
            {renderEmailForm(false)}
          </>
        )}
      </div>

      <Modal
        open={emailModalOpen}
        onClose={() => setEmailModalOpen(false)}
        labelledBy="email-modal-title"
        closeLabel={t("emailDismiss")}
      >
        {emailStatus === "sent" ? (
          <div className="text-center py-2">
            <div className="w-11 h-11 rounded-full bg-brand-soft text-brand flex items-center justify-center mx-auto mb-3">
              <Icon name="check" size={22} weight="bold" />
            </div>
            <div id="email-modal-title" className="font-serif text-xl text-ink mb-1">
              {t("emailSentTitle")}
            </div>
            <p className="text-sm text-ink-soft">{t("emailSentDesc")}</p>
          </div>
        ) : (
          <>
            <div className="w-11 h-11 rounded-full bg-brand-soft text-brand flex items-center justify-center mb-3">
              <Icon name="email" size={22} />
            </div>
            <div id="email-modal-title" className="font-serif text-2xl text-ink mb-1.5 pr-6">
              {t("emailKeepCopy")}
            </div>
            <p className="text-sm text-ink-soft mb-4 leading-relaxed">{t("emailBody")}</p>
            {renderEmailForm(true)}
            <button
              onClick={() => setEmailModalOpen(false)}
              className="mt-3 w-full text-sm font-medium text-ink-soft hover:text-ink transition-colors py-1"
            >
              {t("emailDismiss")}
            </button>
          </>
        )}
      </Modal>

      <div className="mt-6 flex justify-center">
        <Link
          href="/screener"
          className="text-sm font-medium text-ink-soft hover:text-ink"
        >
          {t("retake")}
        </Link>
      </div>

      {/* Disclaimer stays visible; the citation list is long and only a few
          readers want it, so it collapses instead of padding every result. */}
      <div className="mt-12 p-5 rounded-2xl bg-warm-dim/50 text-xs text-ink-soft leading-relaxed">
        <p>
          <strong className="text-ink">{t("disclaimerLabel")}</strong> {t("disclaimerBody")}
        </p>
        <details className="mt-3 group">
          <summary className="cursor-pointer list-none font-semibold text-ink hover:text-brand transition-colors">
            {t("evidenceBasisLabel")}
            <span className="ml-1.5 inline-block text-brand group-open:rotate-45 transition-transform">+</span>
          </summary>
          <p className="mt-2 max-w-prose">
            {t.rich("evidenceBasisBody", { i: (chunks) => <em>{chunks}</em> })}
          </p>
        </details>
      </div>
    </div>
  );
}
