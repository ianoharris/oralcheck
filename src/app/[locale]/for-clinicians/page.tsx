import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import { Suspense } from "react";
import { localizedAlternates } from "@/lib/pageMetadata";
import PrintableFlyer from "./PrintableFlyer";
import EmbedBlock from "./EmbedBlock";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "ForCliniciansMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/for-clinicians"),
  };
}

type WhyPoint = { icon: string; title: string; desc: string };
type Step = { title: string; desc: string };

export default async function ForCliniciansPage({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "ForCliniciansPage" });
  const whyPoints = t.raw("whyPoints") as WhyPoint[];
  const howToUse = t.raw("howToUse") as Step[];

  return (
    <div className="max-w-3xl mx-auto px-5 py-10 sm:py-16">
      {/* Hero */}
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        {t("heading")}
      </h1>
      <p className="text-lg text-ink-soft leading-relaxed mb-8">
        {t("subheading")}
      </p>

      {/* Flyer section — first thing they see */}
      <div className="mb-10">
        <h2 className="font-serif text-3xl text-ink mb-2">{t("flyerHeading")}</h2>
        <p className="text-ink-soft mb-6">{t("flyerSub")}</p>
        <Suspense fallback={<div className="h-32 bg-warm-dim rounded-2xl animate-pulse" />}>
          <PrintableFlyer />
        </Suspense>
      </div>

      {/* Why use it */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">{t("whyHeading")}</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {whyPoints.map((p) => (
            <div key={p.title} className="flex gap-3 items-start">
              <span className="text-xl leading-none mt-0.5">{p.icon}</span>
              <div>
                <div className="font-semibold text-ink text-sm">{p.title}</div>
                <div className="text-ink-soft text-sm leading-relaxed mt-0.5">{p.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* How to use */}
      <section className="bg-warm-dim rounded-2xl border border-warm-dim p-6 sm:p-8 mb-6">
        <h2 className="font-serif text-2xl text-ink mb-5">{t("howToUseHeading")}</h2>
        <div className="space-y-5">
          {howToUse.map((item, i) => (
            <div key={item.title} className="flex gap-4 items-start">
              <div className="w-8 h-8 rounded-full bg-brand text-white font-bold text-sm flex items-center justify-center flex-shrink-0">
                {i + 1}
              </div>
              <div>
                <div className="font-semibold text-ink">{item.title}</div>
                <div className="text-ink-soft text-sm leading-relaxed mt-0.5">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Disclaimer note */}
      <section className="bg-accent/10 border border-accent/20 rounded-2xl p-5 mb-10">
        <p className="text-sm text-ink leading-relaxed">
          <strong>{t("importantLabel")}</strong> {t("importantBody")}
        </p>
      </section>

      {/* Embed code */}
      <EmbedBlock />

      {/* Bottom links */}
      <div className="mt-12 pt-8 border-t border-warm-dim flex flex-wrap gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors text-sm"
        >
          {t("previewScreener")}
        </Link>
        <Link
          href="/about#feedback"
          className="bg-warm-dim hover:bg-warm-dim text-ink font-semibold px-6 py-3 rounded-full border border-warm-dim transition-colors text-sm"
        >
          {t("contactUs")}
        </Link>
      </div>
    </div>
  );
}
