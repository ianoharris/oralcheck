import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Oral Cancer Infographic | OralCheck",
  description:
    "Printable oral cancer awareness infographic. Risk factors, warning signs, key statistics, and the 2-week rule. Free to print and share.",
  alternates: { canonical: "https://oralcheck.org/infographic" },
};

export default function InfographicLayout({ children }: { children: React.ReactNode }) {
  return children;
}
