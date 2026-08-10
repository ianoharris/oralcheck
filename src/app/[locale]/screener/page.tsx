"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useTranslations } from "next-intl";
import { Link, useRouter } from "@/i18n/navigation";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { sendGAEvent } from "@next/third-parties/google";
import { useQuestions } from "@/lib/questions";
import ProgressBar from "@/components/ProgressBar";
import QuestionCard from "@/components/QuestionCard";

export default function ScreenerPage() {
  const t = useTranslations("ScreenerPage");
  const questions = useQuestions();
  const router = useRouter();
  const [index, setIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const dirRef = useRef(1); // 1 = forward, -1 = back
  const reduced = useReducedMotion();

  const q = questions[index];
  const isLast = index === questions.length - 1;
  const selected = answers[q.id];

  // Fire once when the screener loads — used to compute completion rate in GA4
  useEffect(() => {
    // Starting a screener arms the completion counter again, so a second run in
    // the same session is still counted exactly once.
    try {
      sessionStorage.removeItem("oralcheck:completionCounted");
    } catch {}
    sendGAEvent("event", "screener_started", {
      question_count: questions.length,
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleSelect = useCallback((optionId: string) => {
    setAnswers((a) => ({ ...a, [q.id]: optionId }));
  }, [q.id]);

  const handleNext = useCallback(() => {
    if (!selected) return;
    dirRef.current = 1;
    if (isLast) {
      try {
        sessionStorage.setItem("oralcheck:answers", JSON.stringify(answers));
      } catch {}
      router.push("/results");
    } else {
      setIndex((i) => i + 1);
    }
  }, [selected, isLast, answers, router]);

  const handleBack = () => {
    if (index === 0) return;
    dirRef.current = -1;
    setIndex((i) => i - 1);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;

      const num = parseInt(e.key, 10);
      if (!isNaN(num) && num >= 1 && num <= q.options.length) {
        handleSelect(q.options[num - 1].id);
        return;
      }
      if (e.key === "Enter") { handleNext(); return; }
      if (e.key === "Backspace" || e.key === "ArrowLeft") { handleBack(); }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [q.options, handleSelect, handleNext]);

  const slideX = reduced ? 0 : 36;

  return (
    <div className="max-w-2xl mx-auto px-5 py-10 sm:py-16">
      <h1 className="sr-only">{t("srHeading")}</h1>
      <div className="mb-10">
        <ProgressBar current={index + 1} total={questions.length} />
      </div>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={q.id}
          initial={reduced ? false : { opacity: 0, x: dirRef.current * slideX }}
          animate={{ opacity: 1, x: 0 }}
          exit={reduced ? {} : { opacity: 0, x: dirRef.current * -slideX }}
          transition={{ duration: 0.22, ease: [0.32, 0, 0.67, 0] }}
        >
          <QuestionCard
            question={q}
            selected={selected}
            onSelect={handleSelect}
          />
        </motion.div>
      </AnimatePresence>

      <div className="mt-10 flex items-center justify-between">
        {index > 0 ? (
          <button
            onClick={handleBack}
            className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-2 rounded-full transition-colors"
          >
            {t("back")}
          </button>
        ) : (
          <Link
            href="/"
            className="text-sm font-medium text-ink-soft hover:text-ink px-4 py-2 rounded-full"
          >
            {t("exit")}
          </Link>
        )}
        <motion.button
          onClick={handleNext}
          disabled={!selected}
          whileTap={selected && !reduced ? { scale: 0.97 } : {}}
          className="bg-brand hover:bg-brand-dark disabled:bg-warm-dim disabled:text-ink-soft disabled:cursor-not-allowed text-white font-semibold px-6 py-3 rounded-full transition-colors"
        >
          {isLast ? t("seeResults") : t("next")}
        </motion.button>
      </div>

      <p className="text-xs text-ink-soft text-center mt-10">
        {t("privacyNote")}
      </p>
    </div>
  );
}
