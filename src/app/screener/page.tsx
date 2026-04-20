"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { questions } from "@/lib/questions";
import ProgressBar from "@/components/ProgressBar";
import QuestionCard from "@/components/QuestionCard";

export default function ScreenerPage() {
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const q = questions[index];
  const isLast = index === questions.length - 1;
  const selected = answers[q.id];

  const handleSelect = (optionId: string) => {
    setAnswers((a) => ({ ...a, [q.id]: optionId }));
  };

  const handleNext = () => {
    if (!selected) return;
    if (isLast) {
      try {
        sessionStorage.setItem("oralcheck:answers", JSON.stringify(answers));
      } catch {}
      router.push("/results");
    } else {
      setIndex((i) => i + 1);
    }
  };

  const handleBack = () => {
    if (index === 0) return;
    setIndex((i) => i - 1);
  };

  return (
    <div className="max-w-2xl mx-auto px-5 py-10 sm:py-16">
      <div className="mb-10">
        <ProgressBar current={index + 1} total={questions.length} />
      </div>

      <QuestionCard
        question={q}
        selected={selected}
        onSelect={handleSelect}
      />

      <div className="mt-10 flex items-center justify-between">
        {index > 0 ? (
          <button
            onClick={handleBack}
            className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-2 rounded-full"
          >
            ← Back
          </button>
        ) : (
          <Link
            href="/"
            className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-2 rounded-full"
          >
            Exit
          </Link>
        )}
        <button
          onClick={handleNext}
          disabled={!selected}
          className="bg-brand hover:bg-brand-dark disabled:bg-warm-dim disabled:text-ink-soft disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {isLast ? "See my results →" : "Next →"}
        </button>
      </div>

      <p className="text-xs text-ink-soft text-center mt-10">
        Your answers stay on your device. Nothing is saved to a server.
      </p>
    </div>
  );
}
