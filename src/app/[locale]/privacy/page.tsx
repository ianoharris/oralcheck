import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PrivacyMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/privacy"),
  };
}

type Section = { heading: string; body: string; linkLabel?: string };

export default async function PrivacyPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "PrivacyPage" });
  const shortVersion = t.raw("shortVersion") as string[];
  const sections = t.raw("sections") as Section[];
  const links: Record<string, string> = {
    "Google Analytics": "https://tools.google.com/dlpage/gaoptout",
  };

  return (
    <div className="max-w-4xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="text-sm text-brand hover:underline">
          {t("back")}
        </Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">{t("heading")}</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-10 max-w-2xl">{t("intro")}</p>

      {/* Summary callout */}
      <div className="bg-brand-soft border border-brand/20 rounded-2xl px-6 py-5 mb-14 max-w-2xl">
        <p className="text-sm font-semibold text-brand mb-3">{t("shortVersionLabel")}</p>
        <ul className="space-y-1.5 text-sm text-ink">
          {shortVersion.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="text-brand mt-0.5 flex-shrink-0">✓</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Sections */}
      <div className="max-w-2xl divide-y divide-warm-dim mb-14">
        {sections.map((s) => (
          <section key={s.heading} className="py-8 first:pt-0">
            <h2 className="font-serif text-xl text-ink mb-3">{s.heading}</h2>
            <p className="text-ink-soft text-sm leading-relaxed">{s.body}</p>
            {s.linkLabel && links[s.heading] && (
              <a
                href={links[s.heading]}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-block text-brand hover:underline text-sm mt-3"
              >
                {s.linkLabel}
              </a>
            )}
          </section>
        ))}

        <section className="py-8">
          <h2 className="font-serif text-xl text-ink mb-3">{t("contactHeading")}</h2>
          <p className="text-ink-soft text-sm leading-relaxed">
            {t("contactBody")}{" "}
            <a href="mailto:hello@oralcheck.org" className="text-brand hover:underline">
              hello@oralcheck.org
            </a>
          </p>
        </section>
      </div>

      {/* Disclaimer */}
      <div className="border-t border-warm-dim pt-8 max-w-2xl space-y-2">
        <p className="text-xs text-ink-soft leading-relaxed">
          <strong className="text-ink">{t("disclaimerLabel")}</strong> {t("disclaimerBody")}
        </p>
        <p className="text-xs text-ink-soft leading-relaxed">{t("scoringNote")}</p>
        <p className="text-xs text-ink-soft pt-2">{t("lastUpdated")}</p>
      </div>
    </div>
  );
}
