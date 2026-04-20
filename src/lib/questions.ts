export type AnswerOption = {
  id: string;
  label: string;
  description?: string;
  weight: number;
};

export type Question = {
  id: string;
  category:
    | "demographics"
    | "tobacco"
    | "alcohol"
    | "hpv"
    | "sun"
    | "symptoms"
    | "family"
    | "diet"
    | "dental"
    | "other";
  icon: string;
  title: string;
  subtitle?: string;
  options: AnswerOption[];
};

export const questions: Question[] = [
  {
    id: "age",
    category: "demographics",
    icon: "🎂",
    title: "What's your age range?",
    subtitle: "Oral cancer risk increases with age.",
    options: [
      { id: "under35", label: "Under 35", weight: 0 },
      { id: "35to54", label: "35 – 54", weight: 1 },
      { id: "55to64", label: "55 – 64", weight: 2 },
      { id: "65plus", label: "65 or older", weight: 3 },
    ],
  },
  {
    id: "tobacco",
    category: "tobacco",
    icon: "🚬",
    title: "Do you use tobacco?",
    subtitle:
      "This includes cigarettes, cigars, pipes, chewing tobacco, snuff, and vapes.",
    options: [
      { id: "daily", label: "Yes, daily", weight: 8 },
      { id: "occasional", label: "Yes, occasionally", weight: 5 },
      { id: "former", label: "Former user (quit)", weight: 2 },
      { id: "never", label: "Never", weight: 0 },
    ],
  },
  {
    id: "alcohol",
    category: "alcohol",
    icon: "🍷",
    title: "How often do you drink alcohol?",
    subtitle:
      "Alcohol and tobacco together multiply risk — the combined effect is larger than either alone.",
    options: [
      { id: "daily", label: "Daily or near-daily", weight: 4 },
      { id: "weekly", label: "A few times a week", weight: 2 },
      { id: "rarely", label: "Rarely", weight: 1 },
      { id: "never", label: "Never", weight: 0 },
    ],
  },
  {
    id: "hpv",
    category: "hpv",
    icon: "🧬",
    title: "HPV status",
    subtitle:
      "HPV is now the leading cause of oropharyngeal cancers. Vaccination lowers risk.",
    options: [
      { id: "vaccinated", label: "Vaccinated against HPV", weight: 0 },
      { id: "neither", label: "Not vaccinated, no known history", weight: 2 },
      { id: "history", label: "Have had an HPV-related condition", weight: 3 },
      { id: "unknown", label: "I'm not sure", weight: 1 },
    ],
  },
  {
    id: "sun",
    category: "sun",
    icon: "☀️",
    title: "Sun exposure on your lips",
    subtitle:
      "Prolonged sun exposure raises risk of lip cancer, especially on the lower lip.",
    options: [
      { id: "daily", label: "Daily, little protection", weight: 2 },
      { id: "regular", label: "Regular, sometimes protected", weight: 1 },
      { id: "minimal", label: "Minimal or well-protected", weight: 0 },
    ],
  },
  {
    id: "symptom",
    category: "symptoms",
    icon: "⚠️",
    title: "In the last month, have you had any of these for 2+ weeks?",
    subtitle:
      "Red or white patches, sores that don't heal, a lump or thickening, numbness, or trouble swallowing.",
    options: [
      { id: "yes", label: "Yes, one or more", weight: 6 },
      { id: "unsure", label: "Not sure / maybe", weight: 3 },
      { id: "no", label: "No", weight: 0 },
    ],
  },
  {
    id: "family",
    category: "family",
    icon: "👨‍👩‍👧",
    title: "Family history of head, neck, or oral cancer?",
    options: [
      { id: "yes", label: "Yes, a close relative", weight: 2 },
      { id: "distant", label: "Distant relative", weight: 1 },
      { id: "no", label: "No", weight: 0 },
      { id: "unsure", label: "Unsure", weight: 0 },
    ],
  },
  {
    id: "diet",
    category: "diet",
    icon: "🥗",
    title: "How often do you eat fruits and vegetables?",
    subtitle:
      "Diets low in fresh produce are associated with higher oral cancer risk.",
    options: [
      { id: "daily", label: "Daily", weight: 0 },
      { id: "weekly", label: "A few times a week", weight: 1 },
      { id: "rarely", label: "Rarely", weight: 2 },
    ],
  },
  {
    id: "dental",
    category: "dental",
    icon: "🦷",
    title: "When was your last dental visit?",
    subtitle: "Dentists are often the first to spot early oral cancer.",
    options: [
      { id: "recent", label: "Within the last year", weight: 0 },
      { id: "fewyears", label: "1 – 3 years ago", weight: 1 },
      { id: "longago", label: "More than 3 years ago", weight: 2 },
      { id: "never", label: "Never", weight: 3 },
    ],
  },
  {
    id: "betel",
    category: "other",
    icon: "🌿",
    title: "Have you ever chewed betel nut, paan, or gutka?",
    subtitle:
      "Common in some regions — a strong independent risk factor for oral cancer.",
    options: [
      { id: "current", label: "Yes, currently", weight: 5 },
      { id: "past", label: "In the past", weight: 2 },
      { id: "never", label: "Never", weight: 0 },
    ],
  },
];
