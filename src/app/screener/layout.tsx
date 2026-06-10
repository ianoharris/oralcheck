import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Free Oral Cancer Screening — 2 Minutes, No Account | OralCheck",
  description:
    "Take OralCheck's free oral cancer risk screener. Answer 10 questions based on published risk factors from the ACS, NCI, and Oral Cancer Foundation. Private, no account required.",
  alternates: { canonical: "https://oralcheck.org/screener" },
};

export default function ScreenerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
