"use client";

import { useEffect, useId, useRef, useState } from "react";

interface Props {
  /** Server-rendered list items, newest first. */
  items: React.ReactNode[];
  /** How many show at first, and how many each click reveals. */
  step?: number;
  /** Visible button text, already localized. */
  buttonLabel: string;
  className?: string;
}

/**
 * Shows the first `step` items and a "Load more" button that reveals the next
 * `step` each time. Every item is rendered into the HTML from the start, with
 * the extras carrying the `hidden` attribute, so all links stay crawlable and
 * nothing is fetched on click. After a click, focus moves to the first newly
 * revealed link so keyboard and screen-reader users land on the new content.
 */
export default function LoadMoreList({ items, step = 5, buttonLabel, className }: Props) {
  const [visible, setVisible] = useState(step);
  const pendingFocus = useRef<number | null>(null);
  const itemRefs = useRef<(HTMLLIElement | null)[]>([]);
  const listId = useId();

  // Runs after the newly revealed items are in the DOM and visible.
  useEffect(() => {
    const index = pendingFocus.current;
    if (index === null) return;
    pendingFocus.current = null;
    itemRefs.current[index]?.querySelector<HTMLElement>("a, button")?.focus();
  }, [visible]);

  const hasMore = visible < items.length;

  return (
    <>
      <ul id={listId} className={className}>
        {items.map((item, i) => (
          <li
            key={i}
            ref={(el) => {
              itemRefs.current[i] = el;
            }}
            hidden={i >= visible}
          >
            {item}
          </li>
        ))}
      </ul>
      {hasMore && (
        <div className="mt-6 flex justify-center">
          <button
            type="button"
            aria-controls={listId}
            onClick={() => {
              pendingFocus.current = visible;
              setVisible((v) => Math.min(v + step, items.length));
            }}
            className="rounded-full border border-brand/40 px-6 py-2.5 text-sm font-semibold text-brand hover:bg-brand-soft focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand transition-colors"
          >
            {buttonLabel}
          </button>
        </div>
      )}
    </>
  );
}
