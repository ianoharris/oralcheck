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
  { key: "patches", href: "/learn/white-and-red-patches", icon: "symptom" },
] as const satisfies ReadonlyArray<{key:string;href:string;icon:IconName}>;

/**
 * Guides left off the /learn index grid so it stays at six cards (two rows of
 * three on desktop). The pages, their routes, the sitemap, and the footer are
 * untouched; each of these is still linked from the footer and from other
 * learn pages, and their content is largely covered by a card that stays:
 *   - facts:      the "What Is Oral Cancer?" overview already carries the key statistics
 *   - hpv:        HPV-16 is one of the factors on the Risk Factors page
 *   - prevention: the six steps are the Risk Factors page read in reverse
 * To swap one back in, move its href out of this list and add another.
 */
export const LEARN_INDEX_HIDDEN_HREFS: ReadonlySet<string> = new Set([
  "/learn/facts",
  "/learn/hpv",
  "/learn/prevention",
]);

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
