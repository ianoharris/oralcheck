import { defineRouting } from "next-intl/routing";

export const routing = defineRouting({
  locales: ["en", "es"],
  defaultLocale: "en",
  // English keeps its existing un-prefixed URLs (no SEO disruption to
  // already-indexed pages); Spanish lives under /es/*.
  localePrefix: "as-needed",
});

export type AppLocale = (typeof routing.locales)[number];
