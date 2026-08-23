import { getTranslations } from "next-intl/server";
import { Link } from "@/i18n/navigation";
import Icon from "@/components/Icon";

export default async function Footer() {
  const t = await getTranslations("Footer");

  return (
    <footer className="border-t border-warm-dim bg-warm mt-24">
      <div className="max-w-6xl mx-auto px-5 py-10 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm">
        <div>
          <div className="font-serif text-xl text-brand mb-2">OralCheck</div>
          <p className="text-ink-soft leading-relaxed">{t("tagline")}</p>
        </div>
        <div>
          <div className="font-semibold text-ink mb-2">{t("exploreHeading")}</div>
          <ul className="space-y-1.5 text-ink-soft">
            <li><Link href="/screener" className="hover:text-brand">{t("riskScreener")}</Link></li>
            <li><Link href="/find-care" className="hover:text-brand">{t("findCare")}</Link></li>
            <li><Link href="/for-clinicians" className="hover:text-brand">{t("forClinicians")}</Link></li>
            <li><Link href="/about" className="hover:text-brand">{t("about")}</Link></li>
            <li><Link href="/methods" className="hover:text-brand">{t("scoringMethodology")}</Link></li>
            <li><Link href="/press" className="hover:text-brand">{t("press")}</Link></li>
            <li><Link href="/about#feedback" className="hover:text-brand">{t("sendFeedback")}</Link></li>
            <li><Link href="/qr" className="hover:text-brand">{t("printShare")}</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold text-ink mb-2">{t("learnHeading")}</div>
          <ul className="space-y-1.5 text-ink-soft">
            <li><Link href="/learn/oral-cancer" className="hover:text-brand">{t("whatIsOralCancer")}</Link></li>
            <li><Link href="/learn/signs" className="hover:text-brand">{t("warningSigns")}</Link></li>
            <li><Link href="/learn/self-exam" className="hover:text-brand">{t("selfExamGuide")}</Link></li>
            <li><Link href="/learn/hpv" className="hover:text-brand">{t("hpvOralCancer")}</Link></li>
            <li><Link href="/learn/prevention" className="hover:text-brand">{t("prevention")}</Link></li>
            <li><Link href="/learn/facts" className="hover:text-brand">{t("factsStats")}</Link></li>
            <li><Link href="/learn/canker-sore-vs-oral-cancer" className="hover:text-brand">{t("cankerSoreVsCancer")}</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-semibold text-ink mb-2">{t("disclaimerHeading")}</div>
          <p className="text-ink-soft leading-relaxed">{t("disclaimerBody")}</p>
          <p className="text-ink-soft leading-relaxed mt-2 text-xs">{t("disclaimerScoring")}</p>
        </div>
      </div>
      <div className="border-t border-warm-dim">
        <div className="max-w-6xl mx-auto px-5 py-4 text-xs text-ink-soft flex flex-col sm:flex-row justify-between gap-2">
          <span>{t("copyright", { year: new Date().getFullYear() })}</span>
          <div className="flex gap-4 items-center">
            <Link href="/methods" className="hover:text-brand transition-colors">{t("methods")}</Link>
            <Link href="/privacy" className="hover:text-brand transition-colors">{t("privacy")}</Link>
            <Link href="/terms" className="hover:text-brand transition-colors">{t("terms")}</Link>
            <a
              href="https://www.linkedin.com/company/oralcheckdotorg/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="OralCheck on LinkedIn"
              className="hover:text-brand transition-colors"
            >
              <Icon name="linkedin" size={16} weight="fill" />
            </a>
            <a
              href="https://www.instagram.com/oralcheckdotorg/"
              target="_blank"
              rel="noopener noreferrer"
              aria-label="OralCheck on Instagram"
              className="hover:text-brand transition-colors"
            >
              <Icon name="instagram" size={16} />
            </a>
          </div>
          <span>{t("notAffiliated")}</span>
        </div>
      </div>
    </footer>
  );
}
