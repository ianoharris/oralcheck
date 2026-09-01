import { createTranslator } from "use-intl/core";
import enMessages from "../../messages/en.json";
import esMessages from "../../messages/es.json";
import ptMessages from "../../messages/pt.json";
import { QUESTION_SKELETON, type Question } from "./questions";
import type { IconName } from "@/components/Icon";

export type Answers = Record<string, string>;

export type RiskTier = "low" | "moderate" | "elevated" | "high";

export type RiskFactor = {
  questionId: string;
  category: Question["category"];
  icon: IconName;
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
  site: SiteAttribution;
};

const MESSAGES: Record<string, typeof enMessages> = {
  en: enMessages,
  es: esMessages as unknown as typeof enMessages,
  pt: ptMessages as unknown as typeof enMessages,
};

/**
 * Falls back to English for any locale we don't carry messages for, rather
 * than throwing. Keyed off the map so adding a language to routing.locales and
 * to MESSAGES is the whole change: the previous version tested `=== "es"`,
 * which silently served English factor labels and guidance on every Portuguese
 * results page while the rest of the site was fully translated.
 */
function messagesFor(locale: string) {
  return MESSAGES[locale] ?? MESSAGES.en;
}

// riskEngine runs both in the browser (results page) and on the server
// (email-result API route), outside of any React tree, so it can't use the
// useTranslations()/getTranslations() hooks — createTranslator is next-intl's
// underlying, framework-agnostic primitive for exactly this case.
function getTranslator(locale: string) {
  return createTranslator({ locale, messages: messagesFor(locale), namespace: "RiskEngine" });
}

function getQuestionsTranslator(locale: string) {
  return createTranslator({ locale, messages: messagesFor(locale), namespace: "Questions" });
}

/** Points added when tobacco and alcohol are both used at meaningful levels. */
const INTERACTION_BONUS = 3;

/**
 * Which of the two diseases each question actually speaks to.
 *
 * Oral cavity and oropharyngeal cancer are epidemiologically distinct: tobacco
 * and alcohol dominate the first, HPV-16 the second. The instrument has always
 * blended them into one score, which both reviewing clinicians raised
 * independently, and the blending has a concrete cost that is visible in the
 * weights themselves. The HPV weight is 5, derived from a deliberately
 * conservative blended OR, when the published OR for confirmed HPV-16 in
 * oropharyngeal cancer is around 15. A young non-smoker whose only real risk is
 * HPV therefore scores low-to-moderate off a total dominated by the tobacco and
 * alcohol questions they answered "never" to.
 *
 * The score is not split in two. Splitting would build the second score on a
 * single question, which is not a score, and the recommendation is identical
 * either way: go and have the exam. What was wrong was the *explanation*, so
 * that is what this fixes. See `attributeSite` below.
 */
const QUESTION_SITE: Record<string, "cavity" | "oropharynx" | "shared"> = {
  tobacco: "cavity",
  alcohol: "cavity",
  betel: "cavity",
  diet: "cavity",
  // Lower lip squamous cell carcinoma, which sits in the oral cavity group.
  sun: "cavity",
  hpv: "oropharynx",
  // These raise risk at both sites, or say nothing about which: they cannot
  // discriminate and are deliberately excluded from the lean.
  age: "shared",
  sex: "shared",
  family: "shared",
  systemic: "shared",
  symptom: "shared",
  dental: "shared",
  tobacco_alcohol_interaction: "cavity",
};

export type SiteAttribution = {
  cavity: number;
  oropharynx: number;
  shared: number;
  lean: "cavity" | "oropharynx" | "mixed" | "none";
};

/**
 * Which disease the person's own answers point at, by weight.
 *
 * A factor counts only if it discriminates: age and sex raise risk at both
 * sites, so counting them would drag every profile toward whichever site has
 * more questions rather than toward the one the person's exposures suggest.
 *
 * A site "leads" only at twice the other's weight. Below that the honest answer
 * is that the profile does not distinguish, and saying so beats manufacturing a
 * lean out of a one-point difference.
 */
export function attributeSite(factors: RiskFactor[]): SiteAttribution {
  let cavity = 0, oropharynx = 0, shared = 0;
  for (const f of factors) {
    const site = QUESTION_SITE[f.questionId] ?? "shared";
    if (site === "cavity") cavity += f.weight;
    else if (site === "oropharynx") oropharynx += f.weight;
    else shared += f.weight;
  }
  let lean: SiteAttribution["lean"] = "mixed";
  if (cavity === 0 && oropharynx === 0) lean = "none";
  else if (cavity >= oropharynx * 2) lean = "cavity";
  else if (oropharynx >= cavity * 2) lean = "oropharynx";
  return { cavity, oropharynx, shared, lean };
}

/**
 * Highest score a real answer set can produce. The tobacco+alcohol interaction
 * bonus is reachable (daily tobacco and daily alcohol are both max-weight
 * answers), so it has to be included here — otherwise a worst-case profile
 * scores above the stated max and reports over 100%.
 *
 * Computed rather than written down, so adding a question can't desynchronize
 * it. Currently 61 (58 option points + the 3-point interaction bonus).
 */
export function computeMaxScore(): number {
  const optionMax = QUESTION_SKELETON.reduce((sum, q) => {
    return sum + Math.max(...q.options.map((o) => o.weight));
  }, 0);
  return optionMax + INTERACTION_BONUS;
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
 *   Sex:       SEER incidence, male 17.5 vs female 6.6 per 100,000 (rate ratio
 *              ~2.6×). Deliberately weighted at OR 2.0 instead, because part of
 *              the male excess is tobacco and alcohol exposure this instrument
 *              already scores separately.
 *   Systemic:  Transplant / head-and-neck radiation / immunosuppression,
 *              blended ~3× (Engels et al., JAMA, 2011; Grulich et al., Lancet,
 *              2007). The least precisely derived weight in the instrument.
 *
 * Interaction term:
 *   Tobacco + alcohol co-use produces multiplicative rather than additive risk
 *   (~15× combined vs. ~9× additive). The +3 interaction bonus reflects this
 *   excess beyond simple score addition (Bagnardi et al., 2015).
 *
 * Tier thresholds (max score 61):
 *   Low ≤4 | Moderate 5–13 | Elevated 14–22 | High ≥23
 *
 *   These are anchored to reference profiles, not rescaled whenever the maximum
 *   changes. Adding the sex and systemic questions raised the maximum from 53 to
 *   61, and rescaling proportionally would have moved the High bar to 26 — which
 *   would have demoted a current betel + tobacco + alcohol user (25) from High to
 *   Elevated. A new question should not make an unchanged profile look safer, so
 *   the thresholds stayed where they are.
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
    score += INTERACTION_BONUS;
    factors.push({
      questionId: "tobacco_alcohol_interaction",
      category: "tobacco",
      icon: "interaction",
      label: t("interaction.label"),
      answerLabel: t("interaction.answerLabel"),
      weight: INTERACTION_BONUS,
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

  // Tier thresholds calibrated to the log-odds weight scale (max score 61):
  // Low ≤4 | Moderate 5–13 | Elevated 14–22 | High ≥23
  // Anchored to reference profiles rather than to the maximum — see the block
  // comment above for why they did not move when the maximum did.
  // Example profiles: tobacco daily (8) = moderate; tobacco+alcohol+interaction (16) = elevated;
  // betel+tobacco+alcohol+interaction (25) = high; male alone (3) = low.
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
    site: attributeSite(factors),
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
