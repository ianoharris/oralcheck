import { useTranslations } from "next-intl";
import { Link } from "@/i18n/navigation";
import Icon from "@/components/Icon";

export default function NotFound() {
  const t = useTranslations("NotFound");
  return (
    <div className="max-w-2xl mx-auto px-5 py-20 sm:py-28 text-center">
      <div className="flex justify-center mb-6 text-brand" aria-hidden><Icon name="dental" size={56} /></div>
      <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-4">
        {t("title")}
      </h1>
      <p className="text-ink-soft text-lg leading-relaxed mb-10 max-w-md mx-auto">
        {t("body")}
      </p>
      <div className="flex flex-wrap justify-center gap-3">
        <Link
          href="/screener"
          className="bg-brand hover:bg-brand-dark text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {t("screener")}
        </Link>
        <Link
          href="/learn"
          className="bg-warm-dim hover:border-brand/40 text-ink font-semibold px-6 py-3 rounded-full transition-colors border border-ink/15"
        >
          {t("learn")}
        </Link>
        <Link
          href="/"
          className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-3"
        >
          {t("home")}
        </Link>
      </div>
    </div>
  );
}
