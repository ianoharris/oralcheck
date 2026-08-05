import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { localizedAlternates } from "@/lib/pageMetadata";

type Props = { children: React.ReactNode; params: Promise<{ locale: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { locale } = await params;
  const t = await getTranslations({ locale, namespace: "FindCareMeta" });
  return {
    title: t("title"),
    description: t("description"),
    alternates: localizedAlternates(locale, "/find-care"),
  };
}

export default function FindCareLayout({ children }: Props) {
  return children;
}
