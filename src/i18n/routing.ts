import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  // "pt" goes here the moment messages/pt.json is populated. See below.
  locales: ["en", "es"],
  defaultLocale: "en",
  // English keeps its existing un-prefixed URLs (no SEO disruption to
  // already-indexed pages); every other language is prefixed: /es/*, /pt/*.
  //
  // ENABLING PORTUGUESE is two steps and nothing else:
  //   1. add "pt" to the array above
  //   2. node scripts/i18n-sync.mjs --locale=pt
  // The translator brief for pt (Brazilian, not European) already exists in
  // LOCALE_BRIEF in scripts/i18n-sync.mjs, the switcher already renders any
  // number of locales, and sitemap/metadata already iterate routing.locales.
  // The only thing missing is API access to run the translation.
  localePrefix: "as-needed",
});

export type AppLocale = (typeof routing.locales)[number];
