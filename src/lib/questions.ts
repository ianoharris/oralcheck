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
    subtitle:
      "Oral cavity cancer incidence rises sharply after 40. Median age at diagnosis is 62 (SEER data). Risk roughly doubles per decade above 40.",
    options: [
      { id: "under35", label: "Under 35", weight: 0 },
      { id: "35to54", label: "35 – 54", weight: 2 },
      { id: "55to64", label: "55 – 64", weight: 4 },
      { id: "65plus", label: "65 or older", weight: 6 },
    ],
  },
  {
    id: "tobacco",
    category: "tobacco",
    icon: "🚬",
    title: "Do you use tobacco?",
    subtitle:
      "Tobacco is the single strongest risk factor for oral cavity cancer — an IARC Group 1 carcinogen. Daily smokers face 2–6× higher risk; smokeless tobacco users face 4–5× higher risk (Gandini et al., Oral Oncology, 2008).",
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
      "Alcohol is an IARC Group 1 carcinogen for oral cavity cancer. Heavy drinkers face 2–3× elevated risk. Combined with tobacco, the effect is multiplicative — up to 15× baseline risk (Bagnardi et al., Annals of Oncology, 2015).",
    options: [
      { id: "daily", label: "Daily or near-daily", weight: 5 },
      { id: "weekly", label: "A few times a week", weight: 3 },
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
      "HPV-16 is the primary driver of oropharyngeal cancer (tonsils, tongue base), with an odds ratio ~15× in infected individuals (Gillison et al., JAMA, 2008). It is less strongly linked to oral cavity cancer but remains a significant risk factor. Vaccination substantially lowers risk.",
    options: [
      { id: "vaccinated", label: "Vaccinated against HPV", weight: 0 },
      { id: "neither", label: "Not vaccinated, no known history", weight: 2 },
      { id: "history", label: "Have had an HPV-related condition", weight: 5 },
      { id: "unknown", label: "I'm not sure", weight: 1 },
    ],
  },
  {
    id: "sun",
    category: "sun",
    icon: "☀️",
    title: "Sun exposure on your lips",
    subtitle:
      "Chronic UV radiation is a direct cause of lower lip squamous cell carcinoma. Outdoor workers with unprotected lip exposure face significantly elevated risk. SPF lip balm and wide-brim hats are effective protective measures.",
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
      "Persistent red patches (erythroplakia: 14–50% malignant transformation rate), white patches (leukoplakia: 5–17% transformation rate), non-healing ulcers, unexplained lumps, or difficulty swallowing are established clinical warning signs requiring professional evaluation.",
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
    subtitle:
      "A first-degree family history of oral or head and neck cancer is associated with elevated risk, likely reflecting shared genetic susceptibility and environmental exposures.",
    options: [
      { id: "yes", label: "Yes, a close relative", weight: 3 },
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
      "Low fruit and vegetable intake is an independent risk factor for oral and oropharyngeal cancer. Diets rich in antioxidants — vitamins A, C, and E — are associated with reduced oral epithelial dysplasia.",
    options: [
      { id: "daily", label: "Daily", weight: 0 },
      { id: "weekly", label: "A few times a week", weight: 1 },
      { id: "rarely", label: "Rarely", weight: 3 },
    ],
  },
  {
    id: "dental",
    category: "dental",
    icon: "🦷",
    title: "When was your last dental visit?",
    subtitle:
      "Over 60% of oral cancers are not diagnosed until Stage III or IV — a gap driven largely by delayed presentation. Regular dental visits enable earlier detection; dentists are trained to identify mucosal changes patients cannot see.",
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
      "Betel quid with or without tobacco is an IARC Group 1 carcinogen for oral cavity cancer, with odds ratios of 7–10× independent of tobacco use. This includes areca nut, paan, and gutka (IARC Monograph 85).",
    options: [
      { id: "current", label: "Yes, currently", weight: 9 },
      { id: "past", label: "In the past", weight: 4 },
      { id: "never", label: "Never", weight: 0 },
    ],
  },
];
