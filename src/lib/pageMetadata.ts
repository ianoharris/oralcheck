import { routing } from "@/i18n/routing";

const SITE_URL = "https://oralcheck.org";

/** "/es/screener" for a prefixed locale, "/screener" for the default one. */
function localeUrl(locale: string, path: string) {
  return locale === routing.defaultLocale
    ? `${SITE_URL}${path}`
    : `${SITE_URL}/${locale}${path}`;
}

/**
 * Canonical + hreflang alternates for a given locale and unprefixed path
 * (e.g. "/screener", or "" for the homepage).
 *
 * Derived from routing.locales rather than listed by hand. The hand-written
 * version hardcoded English and Spanish, and the failure mode when a third
 * language arrived was quiet and expensive: every Portuguese page would have
 * carried a canonical pointing at its English equivalent, which tells search
 * engines the Portuguese page is a duplicate and should not be indexed. The
 * whole translation would have been invisible in search, with nothing visibly
 * broken on the site itself.
 */
export function localizedAlternates(locale: string, path: string) {
  const languages = Object.fromEntries(
    routing.locales.map((l) => [l, localeUrl(l, path)]),
  );
  return {
    canonical: localeUrl(locale, path),
    languages: {
      ...languages,
      // x-default is what a search engine serves when it has no better match
      // for the user's language, so it points at the default locale.
      "x-default": localeUrl(routing.defaultLocale, path),
    },
  };
}
