import { createTranslator } from "use-intl/core";
import enMessages from "../../messages/en.json";
import esMessages from "../../messages/es.json";
import { QUESTION_SKELETON, type Question } from "./questions";

export type Answers = Record<string, string>;

export type RiskTier = "low" | "moderate" | "elevated" | "high";

export type RiskFactor = {
  questionId: string;
  category: Question["category"];
  icon: string;
  label: string;
  answerLabel: string;
  weight: number;
  guidance: string;
};

export type RiskResult = {
  score: number;
  maxScore: number;
  percent: number;
  tier: RiskTier;
  tierLabel: string;
  tierColor: string;
  headline: string;
  summary: string;
  factors: RiskFactor[];
  hasUrgentSymptom: boolean;
};

const MESSAGES = { en: enMessages, es: esMessages } as const;

// riskEngine runs both in the browser (results page) and on the server
// (email-result API route), outside of any React tree, so it can't use the
// useTranslations()/getTranslations() hooks — createTranslator is next-intl's
// underlying, framework-agnostic primitive for exactly this case.
function getTranslator(locale: string) {
  const messages = locale === "es" ? MESSAGES.es : MESSAGES.en;
  return createTranslator({ locale, messages, namespace: "RiskEngine" });
}

function getQuestionsTranslator(locale: string) {
  const messages = locale === "es" ? MESSAGES.es : MESSAGES.en;
  return createTranslator({ locale, messages, namespace: "Questions" });
}

export function computeMaxScore(): number {
  return QUESTION_SKELETON.reduce((sum, q) => {
    const max = Math.max(...q.options.map((o) => o.weight));
    return sum + max;
  }, 0);
}

/**
 * SCORING METHODOLOGY
 *
 * Weights are derived from published odds ratios (ORs) using the formula:
 *   weight = round(ln(OR) × k)
 * where k = 4.47, anchored so that tobacco daily (OR 6.0) → weight 8.
 *
 * Key sources:
 *   Tobacco:   Gandini et al., Oral Oncology, 2008        (OR 2.5–6.0×)
 *   Alcohol:   Bagnardi et al., Annals of Oncology, 2015  (OR 2.0–3.0×)
 *   Betel:     IARC Monograph 85, 2004                    (OR 7–10×)
 *   HPV:       Gillison et al., JAMA, 2008                (OR ~15× oropharyngeal;
 *              conservative OR ~3–5× blended for oral+oropharyngeal)
 *   Age:       SEER incidence data, multivariable-adjusted ORs (~1.5–4× by decade)
 *   Symptoms:  Napier & Speight, J Oral Pathol Med, 2008  (leukoplakia 5–17%,
 *              erythroplakia 14–50% malignant transformation — used as clinical
 *              override flag rather than additive score)
 *
 * Interaction term:
 *   Tobacco + alcohol co-use produces multiplicative rather than additive risk
 *   (~15× combined vs. ~9× additive). The +3 interaction bonus reflects this
 *   excess beyond simple score addition (Bagnardi et al., 2015).
 *
 * Tier thresholds (max score ~53):
 *   Low ≤4 | Moderate 5–13 | Elevated 14–22 | High ≥23
 *
 * Limitations:
 *   Weights are evidence-informed but have not been validated against a clinical
 *   outcome dataset. This tool is a risk stratification instrument, not a
 *   validated diagnostic screener. Dental or medical evaluation is always required.
 */
export function computeRisk(answers: Answers, locale: string = "en"): RiskResult {
  const t = getTranslator(locale);
  const qt = getQuestionsTranslator(locale);

  const factors: RiskFactor[] = [];
  let score = 0;
  let hasUrgentSymptom = false;

  for (const q of QUESTION_SKELETON) {
    const answerId = answers[q.id];
    if (!answerId) continue;
    const option = q.options.find((o) => o.id === answerId);
    if (!option) continue;
    score += option.weight;

    if (q.id === "symptom" && (answerId === "yes" || answerId === "unsure")) {
      hasUrgentSymptom = true;
    }

    if (option.weight > 0) {
      factors.push({
        questionId: q.id,
        category: q.category,
        icon: q.icon,
        label: t(`factorLabels.${q.id}` as never) as string,
        answerLabel: qt(`${q.id}.options.${option.id}` as never) as string,
        weight: option.weight,
        guidance: t(`categoryGuidance.${q.category}` as never) as string,
      });
    }
  }

  // Tobacco + alcohol interaction term
  // When both are present at meaningful levels, the combined carcinogenic effect is
  // multiplicative rather than additive — up to 15× baseline risk vs. the sum-of-parts.
  // (Bagnardi et al., Annals of Oncology, 2015; IARC Monographs Vol. 100E)
  const tobaccoAnswer = answers["tobacco"];
  const alcoholAnswer = answers["alcohol"];
  const hasActiveTobacco = tobaccoAnswer === "daily" || tobaccoAnswer === "occasional";
  const hasActiveAlcohol = alcoholAnswer === "daily" || alcoholAnswer === "weekly";

  if (hasActiveTobacco && hasActiveAlcohol) {
    const interactionBonus = 3;
    score += interactionBonus;
    factors.push({
      questionId: "tobacco_alcohol_interaction",
      category: "tobacco",
      icon: "⚡",
      label: t("interaction.label"),
      answerLabel: t("interaction.answerLabel"),
      weight: interactionBonus,
      guidance: t("interaction.guidance"),
    });
  }

  factors.sort((a, b) => b.weight - a.weight);

  const maxScore = computeMaxScore();
  const percent = Math.round((score / maxScore) * 100);

  let tier: RiskTier;
  let tierLabel: string;
  let tierColor: string;
  let headline: string;

  // Tier thresholds calibrated to the log-odds weight scale (max score ~53):
  // Low ≤4 | Moderate 5–13 | Elevated 14–22 | High ≥23
  // These map proportionally to the old thresholds (≤4/5–10/11–17/≥18) scaled to the new max.
  // Example profiles: tobacco daily (8) = moderate; tobacco+alcohol+interaction (16) = elevated;
  // betel+tobacco+alcohol+interaction (25) = high.
  if (hasUrgentSymptom) {
    tier = "high";
    tierLabel = t("tier.seeADentist");
    tierColor = "high";
    headline = t("tier.urgentHeadline");
  } else if (score <= 4) {
    tier = "low";
    tierLabel = t("tier.low.label");
    tierColor = "low";
    headline = t("tier.low.headline");
  } else if (score <= 13) {
    tier = "moderate";
    tierLabel = t("tier.moderate.label");
    tierColor = "mid";
    headline = t("tier.moderate.headline");
  } else if (score <= 22) {
    tier = "elevated";
    tierLabel = t("tier.elevated.label");
    tierColor = "mid";
    headline = t("tier.elevated.headline");
  } else {
    tier = "high";
    tierLabel = t("tier.high.label");
    tierColor = "high";
    headline = t("tier.high.headline");
  }

  const summary = buildSummary(t, tier, factors, hasUrgentSymptom);

  return {
    score,
    maxScore,
    percent,
    tier,
    tierLabel,
    tierColor,
    headline,
    summary,
    factors,
    hasUrgentSymptom,
  };
}

function buildSummary(
  t: ReturnType<typeof getTranslator>,
  tier: RiskTier,
  factors: RiskFactor[],
  urgent: boolean,
): string {
  const top = factors.slice(0, 2).map((f) => f.label.toLowerCase());
  const and = t("and");
  const topPhrase =
    top.length === 2
      ? `${top[0]} ${and} ${top[1]}`
      : top.length === 1
        ? top[0]
        : t("summary.fallback");

  if (urgent) return t("summary.urgent", { topPhrase });

  switch (tier) {
    case "low":
      return t("summary.low");
    case "moderate":
      return t("summary.moderate", { topPhrase });
    case "elevated":
      return t("summary.elevated", { topPhrase });
    case "high":
      return t("summary.high", { topPhrase });
  }
}
