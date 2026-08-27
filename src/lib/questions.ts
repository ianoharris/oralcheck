import { useTranslations } from "next-intl";
import type { IconName } from "@/components/Icon";

export type AnswerOption = {
  id: string;
  label: string;
  description?: string;
  weight: number;
};

export type Question = {
  id: string;
  // One category per question, not per theme. Results-page guidance is keyed
  // off the category, so two questions sharing one would show identical advice
  // under both — which is how "Sex at birth: Male" first shipped carrying the
  // age paragraph verbatim.
  category:
    | "demographics"
    | "sex"
    | "tobacco"
    | "alcohol"
    | "hpv"
    | "sun"
    | "symptoms"
    | "family"
    | "diet"
    | "dental"
    | "medical"
    | "other";
  icon: IconName;
  title: string;
  subtitle?: string;
  options: AnswerOption[];
};

// Locale-independent skeleton: ids, categories, icons, and scoring weights.
// Only title/subtitle/option labels are translated (see messages/*.json → Questions).
type QuestionSkeleton = {
  id: string;
  category: Question["category"];
  icon: IconName;
  options: { id: string; weight: number }[];
};

export const QUESTION_SKELETON: QuestionSkeleton[] = [
  {
    id: "age",
    category: "demographics",
    icon: "age",
    options: [
      { id: "under35", weight: 0 },
      { id: "35to54", weight: 2 },
      { id: "55to64", weight: 4 },
      { id: "65plus", weight: 6 },
    ],
  },
  {
    // Sex is asked as a separate demographic rather than folded into age
    // because the male excess is only partly explained by tobacco and alcohol,
    // both of which this instrument already scores. See /methods for why the
    // weight is derived from OR 2.0 rather than the raw 2.6x SEER rate ratio.
    id: "sex",
    category: "sex",
    icon: "sex",
    options: [
      { id: "male", weight: 3 },
      { id: "female", weight: 0 },
      // Population average: roughly half of respondents who decline are male,
      // so the expected excess is half of 3, rounded up to stay conservative.
      { id: "preferNotToSay", weight: 2 },
    ],
  },
  {
    id: "tobacco",
    category: "tobacco",
    icon: "tobacco",
    options: [
      { id: "daily", weight: 8 },
      { id: "occasional", weight: 5 },
      { id: "former", weight: 2 },
      { id: "never", weight: 0 },
    ],
  },
  {
    id: "alcohol",
    category: "alcohol",
    icon: "alcohol",
    options: [
      { id: "daily", weight: 5 },
      { id: "weekly", weight: 3 },
      { id: "rarely", weight: 1 },
      { id: "never", weight: 0 },
    ],
  },
  {
    id: "hpv",
    category: "hpv",
    icon: "hpv",
    options: [
      { id: "vaccinated", weight: 0 },
      { id: "neither", weight: 2 },
      { id: "history", weight: 5 },
      { id: "unknown", weight: 1 },
    ],
  },
  {
    id: "sun",
    category: "sun",
    icon: "sun",
    options: [
      { id: "daily", weight: 2 },
      { id: "regular", weight: 1 },
      { id: "minimal", weight: 0 },
    ],
  },
  {
    id: "symptom",
    category: "symptoms",
    icon: "symptom",
    options: [
      { id: "yes", weight: 6 },
      { id: "unsure", weight: 3 },
      { id: "no", weight: 0 },
    ],
  },
  {
    id: "family",
    category: "family",
    icon: "family",
    options: [
      { id: "yes", weight: 3 },
      { id: "distant", weight: 1 },
      { id: "no", weight: 0 },
      { id: "unsure", weight: 0 },
    ],
  },
  {
    // One combined question covering three distinct exposures that share a
    // mechanism (impaired immune surveillance of the oral mucosa). Kept
    // combined rather than split so the screener stays short, on the reasoning
    // that someone with any of the three warrants the same recommendation.
    id: "systemic",
    category: "medical",
    icon: "immune",
    options: [
      { id: "yes", weight: 5 },
      { id: "unsure", weight: 1 },
      { id: "no", weight: 0 },
    ],
  },
  {
    id: "diet",
    category: "diet",
    icon: "diet",
    options: [
      { id: "daily", weight: 0 },
      { id: "weekly", weight: 1 },
      { id: "rarely", weight: 3 },
    ],
  },
  {
    id: "dental",
    category: "dental",
    icon: "dental",
    options: [
      { id: "recent", weight: 0 },
      { id: "fewyears", weight: 1 },
      { id: "longago", weight: 2 },
      { id: "never", weight: 3 },
    ],
  },
  {
    id: "betel",
    category: "other",
    icon: "betel",
    options: [
      { id: "current", weight: 9 },
      { id: "past", weight: 4 },
      { id: "never", weight: 0 },
    ],
  },
];

/** Client-component hook: returns the fully localized question list. */
export function useQuestions(): Question[] {
  const t = useTranslations("Questions");
  return QUESTION_SKELETON.map((q) => ({
    id: q.id,
    category: q.category,
    icon: q.icon,
    title: t(`${q.id}.title`),
    subtitle: t(`${q.id}.subtitle`),
    options: q.options.map((o) => ({
      id: o.id,
      weight: o.weight,
      label: t(`${q.id}.options.${o.id}`),
    })),
  }));
}
