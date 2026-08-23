import type { Metadata } from "next";
import Icon from "@/components/Icon";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "TermsMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/terms"),
  };
}

type Section = { heading: string; body: string };

export default async function TermsPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "TermsPage" });
  const shortVersion = t.raw("shortVersion") as string[];
  const sections = t.raw("sections") as Section[];

  return (
    <div className="max-w-4xl mx-auto px-5 py-12 sm:py-20">
      <div className="mb-10">
        <Link href="/" className="text-sm text-brand hover:underline">
          {t("back")}
        </Link>
      </div>

      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">{t("heading")}</h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-10 max-w-2xl">{t("intro")}</p>

      {/* The medical disclaimer is the whole reason this page exists, so it
          leads rather than sitting in a numbered clause nobody reaches. */}
      <div className="bg-accent/5 border-2 border-accent/30 rounded-2xl px-6 py-5 mb-10 max-w-2xl">
        <p className="text-sm font-semibold text-accent mb-2">{t("medicalLabel")}</p>
        <p className="text-sm text-ink leading-relaxed">{t("medicalBody")}</p>
      </div>

      <div className="bg-brand-soft border border-brand/20 rounded-2xl px-6 py-5 mb-14 max-w-2xl">
        <p className="text-sm font-semibold text-brand mb-3">{t("shortVersionLabel")}</p>
        <ul className="space-y-1.5 text-sm text-ink">
          {shortVersion.map((item) => (
            <li key={item} className="flex items-start gap-2">
              <span className="text-brand mt-0.5 flex-shrink-0" aria-hidden>
                <Icon name="check" size={16} weight="bold" />
              </span>
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </div>

      <div className="space-y-10 max-w-2xl">
        {sections.map((s) => (
          <section key={s.heading}>
            <h2 className="font-serif text-2xl text-ink mb-3">{s.heading}</h2>
            <p className="text-ink-soft leading-relaxed">{s.body}</p>
          </section>
        ))}
      </div>

      <div className="mt-14 pt-8 border-t border-warm-dim max-w-2xl">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("contactHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-6">{t("contactBody")}</p>
        <p className="text-sm text-ink-soft">
          {t("privacyPointer")}{" "}
          <Link href="/privacy" className="text-brand hover:underline">
            {t("privacyLink")}
          </Link>
          .
        </p>
        <p className="text-xs text-ink-soft mt-6">{t("lastUpdated")}</p>
      </div>
    </div>
  );
}
