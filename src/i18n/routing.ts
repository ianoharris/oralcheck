import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["en", "es", "pt"],
  defaultLocale: "en",
  // English keeps its existing un-prefixed URLs (no SEO disruption to
  // already-indexed pages); every other language is prefixed: /es/*, /pt/*.
  //
  // Adding a language is one line here plus `node scripts/i18n-sync.mjs`. The
  // switcher renders any number of locales and sitemap/metadata iterate this
  // array, so nothing else needs touching. Give the new locale a brief in
  // LOCALE_BRIEF in scripts/i18n-sync.mjs first, or the sync refuses to guess
  // at its register and regional variant.
  localePrefix: "as-needed",
});

export type AppLocale = (typeof routing.locales)[number];
