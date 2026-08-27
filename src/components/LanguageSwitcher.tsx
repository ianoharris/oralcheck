"use client";

import { useLocale, useTranslations } from "next-intl";
import { usePathname, useRouter } from "@/i18n/navigation";
import { routing } from "@/i18n/routing";
import Icon from "@/components/Icon";
import { useEffect, useRef, useState } from "react";

/**
 * Language picker.
 *
 * A segmented slider works at two languages and stops working at three: the
 * pills either overflow the header on a phone or shrink to unreadable
 * two-letter stubs with no indication of what they mean. This renders whatever
 * is in `routing.locales`, so adding a language is a one-line change with no
 * layout consequences.
 *
 * Each language is named in its own language, which is the only labelling that
 * helps someone who cannot read the current one.
 */

const LANGUAGE_NAMES: Record<string, string> = {
  en: "English",
  es: "Español",
  pt: "Português",
};

export default function LanguageSwitcher() {
  const locale = useLocale();
  const t = useTranslations("Nav");
  const pathname = usePathname();
  const router = useRouter();

  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement>(null);

  // Close on an outside click or Escape. Without this the menu strands itself
  // open when someone taps elsewhere, which on a phone means it covers the nav.
  useEffect(() => {
    if (!open) return;
    function onPointerDown(e: PointerEvent) {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  function choose(l: string) {
    setOpen(false);
    router.replace(pathname, { locale: l as (typeof routing.locales)[number] });
  }

  return (
    <div ref={wrapRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-label={t("language")}
        className="flex items-center gap-1 rounded-full border border-warm-dim px-2.5 py-1 text-xs font-semibold uppercase text-ink-soft hover:text-ink hover:bg-warm-dim transition-colors"
      >
        {locale}
        <span
          aria-hidden
          className={`transition-transform ${open ? "rotate-180" : ""}`}
        >
          <Icon name="caretDown" size={12} weight="bold" />
        </span>
      </button>

      {open && (
        <ul
          role="listbox"
          aria-label={t("language")}
          className="absolute right-0 z-50 mt-1.5 min-w-[9rem] overflow-hidden rounded-2xl border border-warm-dim bg-warm shadow-lg"
        >
          {routing.locales.map((l) => (
            <li key={l} role="none">
              <button
                type="button"
                role="option"
                aria-selected={l === locale}
                onClick={() => choose(l)}
                className={`flex w-full items-center justify-between gap-3 px-3.5 py-2 text-left text-sm transition-colors ${
                  l === locale
                    ? "bg-brand-soft font-semibold text-brand"
                    : "text-ink hover:bg-warm-dim"
                }`}
              >
                <span>{LANGUAGE_NAMES[l] ?? l.toUpperCase()}</span>
                <span className="text-[0.65rem] font-semibold uppercase tracking-wider text-muted-foreground opacity-60">
                  {l}
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
