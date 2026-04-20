"use client";

import type { Question } from "@/lib/questions";

export default function QuestionCard({
  question,
  selected,
  onSelect,
}: {
  question: Question;
  selected?: string;
  onSelect: (optionId: string) => void;
}) {
  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <div className="text-4xl" aria-hidden>
          {question.icon}
        </div>
        <h2 className="text-3xl sm:text-4xl font-serif text-ink leading-tight">
          {question.title}
        </h2>
        {question.subtitle && (
          <p className="text-ink-soft text-base sm:text-lg leading-relaxed max-w-xl">
            {question.subtitle}
          </p>
        )}
      </div>

      <div className="grid gap-3">
        {question.options.map((opt) => {
          const isSelected = selected === opt.id;
          return (
            <button
              key={opt.id}
              onClick={() => onSelect(opt.id)}
              className={`text-left p-5 rounded-2xl border-2 transition-all ${
                isSelected
                  ? "border-brand bg-brand-soft"
                  : "border-warm-dim bg-white hover:border-brand/40"
              }`}
            >
              <div className="flex items-start gap-3">
                <span
                  className={`mt-0.5 h-5 w-5 shrink-0 rounded-full border-2 flex items-center justify-center ${
                    isSelected ? "border-brand" : "border-warm-dim"
                  }`}
                >
                  {isSelected && (
                    <span className="h-2 w-2 rounded-full bg-brand" />
                  )}
                </span>
                <div>
                  <div className="font-semibold text-ink">{opt.label}</div>
                  {opt.description && (
                    <div className="text-sm text-ink-soft mt-0.5">
                      {opt.description}
                    </div>
                  )}
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
