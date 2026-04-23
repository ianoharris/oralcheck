import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Your Risk Results | OralCheck",
  description: "Your personalized oral cancer risk assessment results.",
  robots: { index: false, follow: false },
};

export default function ResultsLayout({ children }: { children: React.ReactNode }) {
  return children;
}
