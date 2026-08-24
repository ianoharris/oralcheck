import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import HeroSectionPhoto from "@/components/HeroSectionPhoto";
import AnimatedStats from "@/components/AnimatedStats";
import FadeUp from "@/components/FadeUp";
import LogoMarquee from "@/components/LogoMarquee";
import InstagramFeed from "@/components/InstagramFeed";

type Props = { params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "Meta" });
  const path = locale === "en" ? "" : `/${locale}`;

  return {
    title: { absolute: t("siteTitle") },
    description: t("ogDescription"),
    alternates: { canonical: `https://oralcheck.org${path}` },
    openGraph: {
      title: t("siteTitle"),
      description: t("ogDescription"),
      url: `https://oralcheck.org${path}`,
      siteName: "OralCheck",
      type: "website",
    },
  };
}

export default async function Home({ params }: Props) {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "HomePage" });

  const features = [
    { title: t("feature1Title"), description: t("feature1Desc"), href: "/screener", cta: t("feature1Cta") },
    { title: t("feature2Title"), description: t("feature2Desc"), href: "/learn", cta: t("feature2Cta") },
    { title: t("feature3Title"), description: t("feature3Desc"), href: "/find-care", cta: t("feature3Cta") },
  ];

  return (
    <div>
      <h1 className="sr-only">{t("srHeading")}</h1>

      {/* Hero */}
      <HeroSectionPhoto />

      {/* Stats — count-up on scroll */}
      <AnimatedStats />

      {/* Features */}
      <section className="max-w-6xl mx-auto px-5 py-20">
        <FadeUp>
          <div className="mb-10">
            <h2 className="font-serif text-3xl sm:text-4xl text-ink">
              {t("sectionHeading")}
            </h2>
          </div>
        </FadeUp>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map(({ title, description, href, cta }, i) => (
            <FadeUp key={href} delay={i * 0.1}>
              <Link
                href={href}
                className="group flex flex-col h-full p-7 rounded-2xl bg-warm-dim border border-warm-dim hover:border-brand/40 hover:shadow-md transition-all duration-200"
              >
                <h3 className="font-serif text-2xl text-ink mb-3 group-hover:text-brand transition-colors">
                  {title}
                </h3>
                <p className="text-ink-soft text-sm leading-relaxed mb-5 flex-1">
                  {description}
                </p>
                <span className="text-sm font-semibold text-brand">
                  {cta} →
                </span>
              </Link>
            </FadeUp>
          ))}
        </div>
      </section>

      {/* Cited statistic.
          This was an unattributed line in the brand's own voice, which on a
          health page is the weakest thing it could be: a claim from nobody.
          It is now verbatim public data from the NCI SEER program, with the
          source named and linked so a clinician can check it in one click.
          Deliberately a citation rather than an endorsement, since nobody has
          endorsed this tool yet. */}
      <FadeUp>
        <section className="max-w-3xl mx-auto px-5 pb-16 text-center">
          <p className="font-serif text-2xl sm:text-3xl text-ink leading-snug">
            {t("quote")}
          </p>
          <p className="mt-5 text-sm text-ink-soft">
            {t("quoteSourcePrefix")}{" "}
            <a
              href="https://seer.cancer.gov/statfacts/html/oralcav.html"
              target="_blank"
              rel="noopener noreferrer"
              // No underline by request. The colour plus the weight carries the
              // affordance, and the hover shift confirms it is interactive.
              className="font-semibold text-brand no-underline hover:text-brand-dark transition-colors"
            >
              {t("quoteSourceName")}
            </a>
            , {t("quoteSourceDetail")}
          </p>
        </section>
      </FadeUp>

      {/* Share / print.
          Given here rather than buried in the footer because printed QR codes
          are the distribution channel that reaches the people this tool is
          actually for: the ones not seeing a dentist, who will never search
          for an oral cancer screener. */}
      <FadeUp>
        <section className="max-w-6xl mx-auto px-5 pb-20">
          <div className="rounded-3xl bg-brand-soft border border-brand/20 px-6 py-10 sm:px-12 sm:py-12 flex flex-col sm:flex-row sm:items-center gap-8">
            <div className="flex-1">
              <p className="text-xs font-semibold tracking-widest text-brand uppercase mb-2">
                {t("shareEyebrow")}
              </p>
              <h2 className="font-serif text-3xl sm:text-4xl text-ink mb-3 text-balance">
                {t("shareHeading")}
              </h2>
              <p className="text-ink-soft leading-relaxed max-w-xl">{t("shareBody")}</p>
            </div>
            <Link
              href="/qr"
              className="shrink-0 self-start sm:self-auto bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3.5 rounded-full transition-colors text-center"
            >
              {t("shareCta")}
            </Link>
          </div>
        </section>
      </FadeUp>

      {/* Logo marquee */}
      <LogoMarquee />

      {/* Instagram feed */}
      {process.env.NEXT_PUBLIC_BEHOLD_WIDGET_ID && (
        <section className="max-w-6xl mx-auto px-5 py-20">
          <FadeUp>
            <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4 mb-8">
              <div>
                <p className="text-xs font-semibold tracking-widest text-brand uppercase mb-2">
                  {t("followAlong")}
                </p>
                <h2 className="font-serif text-3xl sm:text-4xl text-ink">
                  @oralcheckdotorg
                </h2>
              </div>
              <a
                href="https://www.instagram.com/oralcheckdotorg"
                target="_blank"
                rel="noopener noreferrer"
                className="self-start sm:self-auto border border-brand text-brand hover:bg-brand hover:text-white font-semibold px-5 py-2.5 rounded-full text-sm transition-colors"
              >
                {t("followInstagram")}
              </a>
            </div>
          </FadeUp>
          <InstagramFeed widgetId={process.env.NEXT_PUBLIC_BEHOLD_WIDGET_ID} />
        </section>
      )}

      {/* Disclaimer and legal.
          On the page itself, not only in the footer. Someone who lands here,
          takes the screener and leaves may never scroll to a footer, and the
          limits of the tool are the one thing they should not miss. */}
      <section className="max-w-3xl mx-auto px-5 pb-16">
        <p className="text-xs text-ink-soft leading-relaxed text-center">
          {t("disclaimerLine")}{" "}
          <Link
            href="/terms"
            className="font-semibold text-brand no-underline hover:text-brand-dark transition-colors"
          >
            {t("disclaimerTermsLink")}
          </Link>
          {" · "}
          <Link
            href="/privacy"
            className="font-semibold text-brand no-underline hover:text-brand-dark transition-colors"
          >
            {t("disclaimerPrivacyLink")}
          </Link>
        </p>
      </section>
    </div>
  );
}
