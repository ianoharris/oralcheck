"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";

export default function LanguageSwitcher() {
  const locale = useLocale();
  const t = useTranslations("Nav");
  const pathname = usePathname();
  const router = useRouter();

  return (
    <div
      className="flex items-center gap-0.5 rounded-full border border-warm-dim p-0.5 text-xs font-semibold"
      role="group"
      aria-label={t("language")}
    >
      {routing.locales.map((l) => (
        <button
          key={l}
          onClick={() => router.replace(pathname, { locale: l })}
          aria-pressed={l === locale}
          className={`px-2 py-1 rounded-full uppercase transition-colors ${
            l === locale ? "bg-brand text-warm" : "text-ink-soft hover:text-ink hover:bg-warm-dim"
          }`}
        >
          {l}
        </button>
      ))}
    </div>
  );
}
