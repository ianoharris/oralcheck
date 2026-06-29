import Link from "next/link";
import type { Metadata } from "next";
import FadeUp from "@/components/FadeUp";
import AnimatedLearnCards from "@/components/AnimatedLearnCards";
import { getAllPublishedArticles } from "@/lib/articles";

export const metadata: Metadata = {
  title: "Learn About Oral Cancer",
  description:
    "Evidence-based guides on oral cancer signs, self-exams, HPV, and statistics. Written for regular people, not clinicians.",
  alternates: { canonical: "https://oralcheck.org/learn" },
};

export default function LearnPage() {
  const articles = getAllPublishedArticles();

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

      {articles.length > 0 && (
        <FadeUp>
          <div className="mt-16">
            <h2 className="font-serif text-2xl text-ink mb-6">More articles</h2>
            <div className="space-y-3">
              {articles.map((a) => (
                <Link
                  key={a.slug}
                  href={`/learn/${a.slug}`}
                  className="flex items-start gap-4 rounded-2xl border border-warm-dim bg-warm-dim p-5 hover:border-brand/40 hover:shadow-sm transition-all group"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-ink group-hover:text-brand transition-colors leading-snug">
                      {a.title}
                    </p>
                    {a.excerpt && (
                      <p className="text-sm text-ink-soft mt-1 line-clamp-2">{a.excerpt}</p>
                    )}
                  </div>
                  <span className="text-brand shrink-0 mt-0.5 text-sm font-semibold">→</span>
                </Link>
              ))}
            </div>
          </div>
        </FadeUp>
      )}
    </div>
  );
}
