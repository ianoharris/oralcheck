import type { Metadata } from "next";
import Image from "next/image";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { localizedAlternates } from "@/lib/pageMetadata";
import ContactForm from "@/components/ContactForm";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "AboutMeta" });
  return {
    title: { absolute: t("title") },
    description: t("description"),
    alternates: localizedAlternates(locale, "/about"),
  };
}

export default async function AboutPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "AboutPage" });

  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        {t("heading")}
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-10">
        {t("subheading")}
      </p>

      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">{t("whoBuiltHeading")}</h2>
        <div className="flex items-center gap-4 mb-6">
          <Image
            src="/ian-harris.jpg"
            alt="Ian Harris, founder of OralCheck"
            width={200}
            height={200}
            className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl object-cover object-[center_25%] border border-warm-dim shrink-0"
          />
          <div>
            <div className="font-serif text-xl text-ink">{t("founderName")}</div>
            <div className="text-sm text-ink-soft">{t("founderTitle")}</div>
          </div>
        </div>
        <p className="text-ink-soft leading-relaxed mb-3">{t("bio1")}</p>
        <p className="text-ink-soft leading-relaxed mb-3">{t("bio2")}</p>
        <p className="text-ink-soft leading-relaxed">{t("bio3")}</p>
      </section>

      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("howItWorksHeading")}</h2>
        <ul className="space-y-3 text-ink-soft leading-relaxed">
          <li>
            <strong className="text-ink">{t("point1Bold")}</strong> {t("point1Rest")}
          </li>
          <li>
            <strong className="text-ink">{t("point2Bold")}</strong> {t("point2Rest")}
          </li>
          <li>
            <strong className="text-ink">{t("point3Bold")}</strong> {t("point3Rest")}
          </li>
        </ul>
      </section>

      <section className="bg-accent/10 border border-accent/20 rounded-2xl p-6 sm:p-8 mb-10">
        <h2 className="font-serif text-2xl text-ink mb-3">{t("disclaimerHeading")}</h2>
        <p className="text-ink leading-relaxed">{t("disclaimerBody")}</p>
      </section>

      <div className="flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("startScreener")}
        </Link>
        <Link
          href="/find-care"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-warm-dim"
        >
          {t("findCare")}
        </Link>
      </div>

      <section id="feedback" className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mt-6">
        <h2 className="font-serif text-2xl text-ink mb-1">{t("getInTouchHeading")}</h2>
        <p className="text-ink-soft leading-relaxed mb-5 text-sm">{t("getInTouchBody")}</p>
        <ContactForm />
      </section>
    </div>
  );
}
