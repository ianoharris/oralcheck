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
    "Age alone isn't something you can change, but regular screening becomes more important as you get older.",
  tobacco:
    "Quitting reduces risk steadily over time. Ask your dentist or physician about cessation programs — many are free.",
  alcohol:
    "Cutting back — even modestly — lowers risk. The effect compounds if you also use tobacco.",
  hpv:
    "The HPV vaccine is approved through age 45. Ask your clinician whether it's right for you.",
  sun:
    "Use SPF lip balm, wear a wide-brim hat, and avoid peak sun. Lip cancer is highly preventable.",
  symptoms:
    "Any sore, patch, lump, or numbness lasting more than 2 weeks should be seen by a dentist or doctor — soon, not someday.",
  family:
    "Tell your dentist. They may recommend more frequent oral cancer screenings.",
  diet:
    "Aim for a variety of colorful fruits and vegetables daily. Antioxidants support oral tissue health.",
  dental:
    "Book a dental visit. A routine cleaning includes an oral cancer screening that takes about 2 minutes.",
  other:
    "Stopping betel/paan/gutka use reduces risk. Ask your dentist for help — many communities have support resources.",
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

  factors.sort((a, b) => b.weight - a.weight);

  const maxScore = computeMaxScore();
  const percent = Math.round((score / maxScore) * 100);

  let tier: RiskTier;
  let tierLabel: string;
  let tierColor: string;
  let headline: string;

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
  } else if (score <= 10) {
    tier = "moderate";
    tierLabel = "Moderate risk";
    tierColor = "mid";
    headline = "A few factors are worth paying attention to.";
  } else if (score <= 17) {
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
    return `Based on what you described, a symptom you reported — combined with ${topPhrase} — is reason enough to get evaluated. Oral cancer caught early has an 84% five-year survival rate. Please book a dental or medical visit this week.`;
  }

  switch (tier) {
    case "low":
      return `Based on your answers, no major risk factors stand out right now. Keep up with annual dental visits — a quick oral cancer screening is part of a routine cleaning.`;
    case "moderate":
      return `Your ${topPhrase} put you at moderate risk. The good news is these are things you can act on. Talk to a dentist at your next visit about oral cancer screening.`;
    case "elevated":
      return `Several factors — particularly ${topPhrase} — raise your risk. Consider booking a dental visit this month and asking specifically for an oral cancer screening. It takes about 2 minutes.`;
    case "high":
      return `Your combination of factors — including ${topPhrase} — places you in a higher-risk group. Please schedule a dental or medical visit soon. Early-stage oral cancer has an 84% five-year survival rate.`;
  }
}
