import { useTranslations } from "next-intl";

const HREFS_ICONS = [
  { key: "riskFactors", href: "/learn/risk-factors", icon: "⚡" },
  { key: "oralCancer", href: "/learn/oral-cancer", icon: "📖" },
  { key: "signs", href: "/learn/signs", icon: "⚠️" },
  { key: "selfExam", href: "/learn/self-exam", icon: "🔎" },
  { key: "facts", href: "/learn/facts", icon: "📊" },
  { key: "hpv", href: "/learn/hpv", icon: "🦠" },
  { key: "prevention", href: "/learn/prevention", icon: "🛡️" },
  { key: "cankerVsCancer", href: "/learn/canker-sore-vs-oral-cancer", icon: "🔬" },
] as const;

/** Client-component hook: returns the fully localized learn-index card list. */
export function useLearnArticles() {
  const t = useTranslations("LearnCards");
  return HREFS_ICONS.map(({ key, href, icon }) => ({
    href,
    icon,
    tag: t(`${key}.tag`),
    title: t(`${key}.title`),
    description: t(`${key}.description`),
  }));
}
