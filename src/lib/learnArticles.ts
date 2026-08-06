import { useTranslations } from "next-intl";
import type { IconName } from "@/components/Icon";

const HREFS_ICONS = [
  { key: "riskFactors", href: "/learn/risk-factors", icon: "riskFactors" },
  { key: "oralCancer", href: "/learn/oral-cancer", icon: "overview" },
  { key: "signs", href: "/learn/signs", icon: "signs" },
  { key: "selfExam", href: "/learn/self-exam", icon: "selfExam" },
  { key: "facts", href: "/learn/facts", icon: "facts" },
  { key: "hpv", href: "/learn/hpv", icon: "virus" },
  { key: "prevention", href: "/learn/prevention", icon: "prevention" },
  { key: "cankerVsCancer", href: "/learn/canker-sore-vs-oral-cancer", icon: "compare" },
] as const satisfies ReadonlyArray<{key:string;href:string;icon:IconName}>;

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
