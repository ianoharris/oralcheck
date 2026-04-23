import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Oral Cancer Risk Screener | OralCheck",
  description:
    "Answer 10 questions to understand your personal oral cancer risk factors. Free, private, and takes 2 minutes. No account needed.",
};

export default function ScreenerLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}
