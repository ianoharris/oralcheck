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

      {/* Blockquote */}
      <FadeUp>
        <section className="max-w-3xl mx-auto px-5 pb-16 text-center">
          <blockquote className="font-serif text-2xl sm:text-3xl text-ink leading-snug">
            &ldquo;{t("quote")}&rdquo;
          </blockquote>
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
    </div>
  );
}
