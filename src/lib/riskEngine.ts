import { questions, type Question } from "./questions";

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

const guidanceByCategory: Record<Question["category"], string> = {
  demographics:
    "Age is the strongest non-modifiable risk factor. After 40, screening at every dental visit is especially important — oral cancer caught at Stage I has an 84% five-year survival rate versus 38% at Stage IV.",
  tobacco:
    "Cessation reduces risk by approximately 50% within 5 years of quitting. Nicotine replacement therapy doubles long-term quit success rates. Ask your dentist or physician about free cessation programs — the Wisconsin Tobacco Quit Line is available at 1-800-QUIT-NOW.",
  alcohol:
    "Risk decreases with reduced consumption. For people using both tobacco and alcohol, tobacco cessation has the greatest individual impact. Even reducing drinking from daily to occasional lowers mucosal carcinogen exposure significantly.",
  hpv:
    "The HPV vaccine (Gardasil 9) is FDA-approved through age 45 and is highly effective against HPV-16, the strain most strongly linked to oropharyngeal cancer. Ask your clinician whether vaccination is appropriate for you.",
  sun:
    "Lower lip squamous cell carcinoma is highly preventable with consistent SPF lip balm use and wide-brim hat wearing. Unlike skin cancer, lip cancer often goes unnoticed — check your lips during any monthly oral self-exam.",
  symptoms:
    "Persistent red patches (erythroplakia), white patches (leukoplakia), non-healing ulcers, unexplained lumps, or difficulty swallowing lasting 2+ weeks are established clinical warning signs. These should not be observed for longer — they require professional evaluation this week, not at a future appointment.",
  family:
    "Tell your dentist about your family history. They may recommend more frequent oral cancer screenings or a referral to an oral medicine specialist. Genetic counseling is available through most academic medical centers.",
  diet:
    "Aim for 5+ servings of colorful fruits and vegetables daily. Evidence supports that diets high in vitamins A, C, and E reduce oral epithelial dysplasia. Processed meat intake has also been linked to elevated head and neck cancer risk in some cohort studies.",
  dental:
    "Book a dental visit as soon as possible. A visual oral cancer screening takes about 2 minutes and is performed as part of a routine examination. Over 60% of oral cancers are diagnosed at Stage III or IV — regular dental care changes this.",
  other:
    "Stopping betel/paan/gutka use lowers risk, though some changes to oral mucosa from prior use may persist. Ask your dentist to examine any areas of discoloration, thickening, or ulceration. Many communities have culturally specific cessation resources.",
};

const factorLabels: Record<string, string> = {
  age: "Age",
  tobacco: "Tobacco use",
  alcohol: "Alcohol use",
  hpv: "HPV exposure",
  sun: "Sun exposure",
  symptom: "Current symptoms",
  family: "Family history",
  diet: "Diet",
  dental: "Dental care",
  betel: "Betel / paan / gutka",
};

export function computeMaxScore(): number {
  return questions.reduce((sum, q) => {
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
export function computeRisk(answers: Answers): RiskResult {
  const factors: RiskFactor[] = [];
  let score = 0;
  let hasUrgentSymptom = false;

  for (const q of questions) {
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
        label: factorLabels[q.id] ?? q.id,
        answerLabel: option.label,
        weight: option.weight,
        guidance: guidanceByCategory[q.category],
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
      label: "Tobacco + alcohol interaction",
      answerLabel: "Both present",
      weight: interactionBonus,
      guidance:
        "When tobacco and alcohol are used together, they produce a multiplicative — not merely additive — increase in oral cancer risk. Combined regular use raises risk up to 15× above baseline, far exceeding the sum of either factor alone. Addressing both together is the most effective risk-reduction strategy (Bagnardi et al., Annals of Oncology, 2015).",
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
    tierLabel = "See a dentist soon";
    tierColor = "high";
    headline = "A symptom you mentioned deserves a close look.";
  } else if (score <= 4) {
    tier = "low";
    tierLabel = "Low risk";
    tierColor = "low";
    headline = "Your current risk profile looks low.";
  } else if (score <= 13) {
    tier = "moderate";
    tierLabel = "Moderate risk";
    tierColor = "mid";
    headline = "A few factors are worth paying attention to.";
  } else if (score <= 22) {
    tier = "elevated";
    tierLabel = "Elevated risk";
    tierColor = "mid";
    headline = "Several risk factors are stacking up.";
  } else {
    tier = "high";
    tierLabel = "See a dentist soon";
    tierColor = "high";
    headline = "Your risk profile is high enough that screening matters.";
  }

  const summary = buildSummary(tier, factors, hasUrgentSymptom);

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
  tier: RiskTier,
  factors: RiskFactor[],
  urgent: boolean,
): string {
  const top = factors.slice(0, 2).map((f) => f.label.toLowerCase());
  const topPhrase =
    top.length === 2
      ? `${top[0]} and ${top[1]}`
      : top.length === 1
        ? top[0]
        : "your responses";

  if (urgent) {
    return `A symptom you reported — combined with ${topPhrase} — warrants prompt professional evaluation. Oral cancer detected at Stage I has an 84% five-year survival rate versus 38% at Stage IV. That gap is why timing matters. Please book a dental or medical visit this week and mention your symptom specifically when you call.`;
  }

  switch (tier) {
    case "low":
      return `No major risk factors stand out in your profile right now. Maintain annual dental visits — a visual oral cancer screening takes about 2 minutes and is included in a routine examination. Familiarize yourself with the warning signs so you can act early if anything changes.`;
    case "moderate":
      return `Your ${topPhrase} elevate your risk modestly above baseline. These are factors you can act on. Mention your risk history to your dentist at your next visit and ask for an oral cancer screening. Early detection at Stage I carries an 84% five-year survival rate.`;
    case "elevated":
      return `Several factors — particularly ${topPhrase} — are stacking your risk. Consider booking a dental visit this month and asking specifically for an oral cancer screening. The 5-year survival rate is 84% when oral cancer is caught early, versus 38% when caught late. Don't wait for a symptom to appear.`;
    case "high":
      return `Your combination of risk factors — including ${topPhrase} — places you in a higher-risk group where proactive screening is strongly warranted. Please schedule a dental or medical visit soon. The difference between Stage I and Stage IV oral cancer survival is dramatic: 84% versus 38%. The exam takes 2 minutes and could be the most important appointment you make this year.`;
  }
}
