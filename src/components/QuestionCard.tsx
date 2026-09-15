"use client";

import type { Question } from "@/lib/questions";
import Icon from "@/components/Icon";

export default function QuestionCard({
  question,
  selected,
  onSelect,
}: {
  question: Question;
  selected?: string;
  onSelect: (optionId: string) => void;
}) {
  const headingId = `q-${question.id}-title`;
  const descId = question.subtitle ? `q-${question.id}-desc` : undefined;

  return (
    <div className="space-y-8">
      <div className="space-y-3">
        <div className="text-brand" aria-hidden="true">
          <Icon name={question.icon} size={40} />
        </div>
        <h2
          id={headingId}
          tabIndex={-1}
          className="text-3xl sm:text-4xl font-serif text-ink leading-tight text-balance focus:outline-none"
        >
          {question.title}
        </h2>
        {question.subtitle && (
          <p
            id={descId}
            className="text-ink-soft text-base sm:text-lg leading-relaxed max-w-xl"
          >
            {question.subtitle}
          </p>
        )}
      </div>

      {/*
        A set of mutually exclusive answers is a radio group, and it was being
        announced as a list of unrelated buttons: no group name, no position,
        and no indication of which one was chosen. Native inputs would be the
        first choice, but the whole visual treatment is the button surface, so
        the roles are applied to the buttons instead. Keyboard selection by
        number key is handled on the page.
      */}
      <div
        role="radiogroup"
        aria-labelledby={headingId}
        aria-describedby={descId}
        className="grid gap-3"
      >
        {question.options.map((opt) => {
          const isSelected = selected === opt.id;
          return (
            <button
              key={opt.id}
              type="button"
              role="radio"
              aria-checked={isSelected}
              onClick={() => onSelect(opt.id)}
              className={`text-left p-5 rounded-2xl border-2 touch-manipulation transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand ${
                isSelected
                  ? "border-brand bg-brand-soft"
                  : "border-warm-dim bg-warm-dim hover:border-brand/40"
              }`}
            >
              <div className="flex items-start gap-3">
                {/*
                  This ring used to be border-warm-dim sitting on a bg-warm-dim
                  button, which is the same colour: the control was invisible
                  until it was chosen, so an unanswered question looked like
                  four paragraphs rather than four options. It needs to read as
                  an empty control before anything is selected.
                */}
                <span
                  aria-hidden="true"
                  className={`mt-0.5 h-5 w-5 shrink-0 rounded-full border-2 flex items-center justify-center transition-colors ${
                    isSelected ? "border-brand" : "border-ink-soft/45"
                  }`}
                >
                  {isSelected && (
                    <span className="h-2 w-2 rounded-full bg-brand" />
                  )}
                </span>
                {/* min-w-0 so a long translated label wraps instead of
                    overflowing the card; es and pt both run longer than en. */}
                <div className="min-w-0">
                  <div className="font-semibold text-ink break-words">
                    {opt.label}
                  </div>
                  {opt.description && (
                    <div className="text-sm text-ink-soft mt-0.5 break-words">
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
