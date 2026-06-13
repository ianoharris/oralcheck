import type { Metadata } from "next";
import FadeUp from "@/components/FadeUp";
import AnimatedLearnCards from "@/components/AnimatedLearnCards";

export const metadata: Metadata = {
  title: "Learn About Oral Cancer",
  description:
    "Evidence-based guides on oral cancer signs, self-exams, HPV, and statistics. Written for regular people, not clinicians.",
  alternates: { canonical: "https://oralcheck.org/learn" },
};

export default function LearnPage() {
  return (
    <div className="max-w-5xl mx-auto px-5 py-10 sm:py-16">
      <FadeUp>
        <div className="max-w-2xl mb-12">
          <h1 className="font-serif text-4xl sm:text-5xl text-ink mb-3">Learn</h1>
          <p className="text-ink-soft text-lg leading-relaxed">
            Short, evidence-based guides on oral cancer detection and prevention.
            Written for regular people, not clinicians.
          </p>
        </div>
      </FadeUp>

      <AnimatedLearnCards />
    </div>
  );
}
