const SITE_URL = "https://oralcheck.org";

/**
 * Canonical + hreflang alternates for a given locale and unprefixed path
 * (e.g. "/screener", or "" for the homepage). English stays unprefixed
 * (routing.localePrefix = "as-needed"); Spanish lives under /es.
 */
export function localizedAlternates(locale: string, path: string) {
  const enUrl = `${SITE_URL}${path}`;
  const esUrl = `${SITE_URL}/es${path}`;
  return {
    canonical: locale === "es" ? esUrl : enUrl,
    languages: {
      en: enUrl,
      es: esUrl,
      "x-default": enUrl,
    },
  };
}
